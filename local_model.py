"""Utilities for managing the local Qwen 2.5 7B Medical LoRA model.

This module encapsulates download, load, status tracking, and inference helpers
for the fine-tuned Qwen 2.5 7B model stored on Hugging Face. The goal is to
allow the rest of the application to treat the model as a managed resource that
can be downloaded on demand and queried once ready.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency for local inference
    torch = None

try:
    from unsloth import FastLanguageModel
except (ImportError, NotImplementedError):  # pragma: no cover - optional dependency for local inference
    FastLanguageModel = None

import config


BASE_DIR = Path(__file__).resolve().parent
MODEL_REPO_ID = "ttennant/qwen2.5-7b-medical-lora"
MAX_SEQ_LENGTH = 2048
MAX_NEW_TOKENS = 512
GENERATION_TEMPERATURE = 0.3
GENERATION_TOP_P = 0.9
SENTINEL_PATH = BASE_DIR / "models" / "qwen2.5-7b-medical-lora" / ".ready"


_status_lock = threading.Lock()
_generation_lock = threading.Lock()
_status: Dict[str, str | None] = {
    "state": "not_downloaded",
    "error": None,
    "detail": "Model not downloaded",
    "device": None,
}
_model = None
_tokenizer = None
_download_thread: threading.Thread | None = None


def _has_cuda() -> bool:
    return torch is not None and torch.cuda.is_available()


def _gpu_ready() -> bool:
    return _has_cuda() and FastLanguageModel is not None


def _torch_available() -> bool:
    return torch is not None


def _set_status(
    state: str,
    error: str | None = None,
    detail: str | None = None,
    device: str | None = None,
) -> None:
    with _status_lock:
        _status["state"] = state
        _status["error"] = error
        if detail is not None:
            _status["detail"] = detail
        if device is not None:
            _status["device"] = device


def get_status() -> Dict[str, str | None]:
    """Return the current status of the local model."""
    with _status_lock:
        return dict(_status)


def _mark_ready() -> None:
    SENTINEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SENTINEL_PATH.write_text("ready")


def _load_model() -> None:
    global _model, _tokenizer

    try:
        if _gpu_ready():
            _set_status(
                "downloading",
                detail="Downloading model files (~8-22 GB). Using 4-bit quantization for low VRAM usage...",
                device="cuda",
            )
            load_4bit = True
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=MODEL_REPO_ID,
                max_seq_length=MAX_SEQ_LENGTH,
                dtype=None,
                load_in_4bit=load_4bit,
            )

            FastLanguageModel.for_inference(model)

            with _status_lock:
                _model = model
                _tokenizer = tokenizer

            _set_status(
                "ready",
                detail="Ready. GPU acceleration active (4-bit quantized, ~3.5 GB VRAM).",
                device="cuda",
            )
            _mark_ready()
            return

        # CPU fallback path
        if not _torch_available():
            raise RuntimeError(
                "PyTorch is required for CPU inference but is not installed. "
                "Install with: pip install torch"
            )

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
            from peft import PeftModel  # type: ignore
        except ImportError as exc:  # pragma: no cover - surface informative error
            raise RuntimeError(
                "CPU inference requires 'transformers' and 'peft' packages. "
                "Install with: pip install transformers peft"
            ) from exc

        base_model_id = "Qwen/Qwen2.5-7B-Instruct"

        _set_status(
            "downloading",
            detail="Downloading base model (~14 GB) + adapters (~8 GB). This will take a while...",
            device="cpu",
        )

        tokenizer = AutoTokenizer.from_pretrained(base_model_id, use_fast=False)
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            device_map="cpu",
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
        )

        _set_status(
            "loading",
            detail="Applying LoRA adapters. Please wait...",
            device="cpu",
        )

        peft_model = PeftModel.from_pretrained(base_model, MODEL_REPO_ID)
        
        _set_status(
            "loading",
            detail="Merging adapters with base model. This may take a few minutes...",
            device="cpu",
        )
        
        merged_model = peft_model.merge_and_unload()
        merged_model.eval()

        with _status_lock:
            _model = merged_model
            _tokenizer = tokenizer

        _set_status(
            "ready",
            detail="Ready. Running on CPU (expect slower responses).",
            device="cpu",
        )
        _mark_ready()
    except Exception as exc:  # noqa: BLE001 - surface details to caller
        _set_status("error", str(exc), detail="Failed to prepare local model.")


def _start_background_load(state: str) -> None:
    global _download_thread

    with _status_lock:
        if _download_thread and _download_thread.is_alive():
            return
        _status["state"] = state
        _status["error"] = None
        if state in {"downloading", "loading"} and not _status.get("detail"):
            _status["detail"] = "Preparing local model..."
        _download_thread = threading.Thread(target=_load_model, daemon=True)
        _download_thread.start()


def _autoload_if_cache_present() -> None:
    if not SENTINEL_PATH.exists():
        return

    if not _torch_available():
        _set_status(
            "error",
            "Found cached weights but PyTorch is unavailable.",
            detail="Install PyTorch to reuse cached weights.",
        )
        return

    current_state = get_status().get("state")
    if current_state in {"ready", "downloading", "loading"}:
        return

    device = "cuda" if _gpu_ready() else "cpu"
    _set_status("loading", detail="Reloading cached weights...", device=device)
    _start_background_load("loading")


def start_download() -> Dict[str, str | None]:
    """Kick off a background download/load of the local model if needed."""
    with _status_lock:
        current_state = _status.get("state")

        if current_state == "ready":
            return dict(_status)
        if current_state in {"downloading", "loading"}:
            return dict(_status)

        if not _gpu_ready() and not _torch_available():
            _status["state"] = "error"
            _status["error"] = (
                "PyTorch is required to run the local model. Install the CPU or GPU "
                "build before retrying."
            )
            _status["detail"] = "Missing PyTorch runtime."
            return dict(_status)

    _start_background_load("downloading")
    return get_status()


def build_prompt(question: str, rag_context: str | None = None) -> str:
    """Construct the chat-style prompt expected by the fine-tuned model."""
    if rag_context:
        augmented_question = (
            f"{question}\n\nRetrieved Context:\n{rag_context.strip()}"
        )
    else:
        augmented_question = question

    return (
        "<|im_start|>system\n"
        f"{config.SYSTEM_PROMPT.strip()}<|im_end|>\n"
        "<|im_start|>user\n"
        f"{augmented_question}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def _extract_assistant_response(generated_text: str) -> str:
    if "<|im_start|>assistant" in generated_text:
        assistant_text = generated_text.split("<|im_start|>assistant")[-1]
    else:
        assistant_text = generated_text
    return assistant_text.replace("<|im_end|>", "").strip()


def generate_response(question: str, rag_context: str | None = None) -> str:
    """Generate a response from the local model. Raises if not ready."""
    status = get_status()
    if status.get("state") != "ready":
        raise RuntimeError("Local model is not ready")

    with _generation_lock:
        prompt = build_prompt(question, rag_context)

        if not _torch_available():
            raise RuntimeError("Local model dependencies are missing")

        inputs = _tokenizer([prompt], return_tensors="pt")
        device = get_status().get("device")
        if _has_cuda() and device == "cuda":
            inputs = {key: value.to("cuda") for key, value in inputs.items()}

        with torch.inference_mode():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=GENERATION_TEMPERATURE,
                do_sample=True,
                top_p=GENERATION_TOP_P,
                use_cache=True,
            )

        full_response = _tokenizer.decode(outputs[0], skip_special_tokens=True)
        return _extract_assistant_response(full_response)


_autoload_if_cache_present()
