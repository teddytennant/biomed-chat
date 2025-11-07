#!/usr/bin/env python3
"""
Standalone installation script for Qwen 2.5 7B Medical LoRA model.
Downloads fine-tuned adapters from HuggingFace and optionally the base model for CPU inference.

This script can be run directly or imported by the API service.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configuration
MODEL_REPO_ID = "ttennant/qwen2.5-7b-medical-lora"
BASE_MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
MODELS_DIR = Path(__file__).parent / "models"
MODEL_DIR = MODELS_DIR / "qwen2.5-7b-medical-lora"
SENTINEL_FILE = MODEL_DIR / ".ready"


def check_cuda_available() -> bool:
    """Check if CUDA is available for GPU inference."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def check_pytorch_available() -> bool:
    """Check if PyTorch is installed."""
    try:
        import torch
        return True
    except ImportError:
        return False


def check_dependencies() -> Dict[str, bool]:
    """Check which dependencies are available."""
    deps = {
        'torch': False,
        'transformers': False,
        'peft': False,
        'unsloth': False,
        'bitsandbytes': False,
        'accelerate': False,
    }
    
    try:
        import torch
        deps['torch'] = True
    except ImportError:
        pass
    
    try:
        import transformers
        deps['transformers'] = True
    except ImportError:
        pass
    
    try:
        import peft
        deps['peft'] = True
    except ImportError:
        pass
    
    try:
        from unsloth import FastLanguageModel
        deps['unsloth'] = True
    except (ImportError, NotImplementedError):
        pass
    
    try:
        import bitsandbytes
        deps['bitsandbytes'] = True
    except ImportError:
        pass
    
    try:
        import accelerate
        deps['accelerate'] = True
    except ImportError:
        pass
    
    return deps


def download_adapter_weights_gpu() -> None:
    """Download and setup model for GPU inference using unsloth.
    
    Note: This downloads BOTH the base model and LoRA adapters, but uses
    4-bit quantization to reduce VRAM usage. The base model is cached by
    HuggingFace and shared across models. Total download may be larger on
    first run, but subsequent runs or other Qwen models will reuse the cache.
    """
    logger.info("=" * 60)
    logger.info("GPU MODE: Downloading model with LoRA adapters")
    logger.info("=" * 60)
    logger.info(f"Repository: {MODEL_REPO_ID}")
    logger.info(f"Base Model: {BASE_MODEL_ID} (auto-downloaded if not cached)")
    logger.info(f"Target directory: {MODEL_DIR}")
    logger.info("")
    
    try:
        from unsloth import FastLanguageModel
    except (ImportError, NotImplementedError) as e:
        raise RuntimeError(
            "GPU inference requires 'unsloth' package. "
            "Install it with: pip install unsloth"
        ) from e
    
    logger.info("Step 1/2: Downloading model files...")
    logger.info("Note: Downloads base model + LoRA adapters (~8-22 GB depending on cache)")
    logger.info("Base model is cached and shared with other Qwen models.")
    logger.info("This may take several minutes depending on your internet speed.")
    
    # FastLanguageModel.from_pretrained will download to HuggingFace cache
    # This includes both base model and adapters
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_REPO_ID,
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )
    
    logger.info("✓ Model files downloaded successfully")
    logger.info("")
    logger.info("Step 2/2: Preparing model for inference...")
    logger.info("Using 4-bit quantization to reduce VRAM usage (~3.5 GB vs ~14 GB)")
    
    # Clean up to free memory
    del model
    del tokenizer
    
    # Mark as ready
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    SENTINEL_FILE.write_text("ready")
    
    logger.info("✓ Model verified and ready for use")
    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ GPU SETUP COMPLETE")
    logger.info("=" * 60)
    logger.info("The model is now ready for inference with GPU acceleration.")


def download_full_model_cpu() -> None:
    """Download base model + LoRA adapters for CPU inference."""
    logger.info("=" * 60)
    logger.info("CPU MODE: Downloading full model + adapters")
    logger.info("=" * 60)
    logger.info(f"Base model: {BASE_MODEL_ID}")
    logger.info(f"LoRA adapters: {MODEL_REPO_ID}")
    logger.info(f"Target directory: {MODEL_DIR}")
    logger.info("")
    logger.info("⚠️  WARNING: CPU inference requires ~22 GB total download:")
    logger.info("   - Base model: ~14 GB")
    logger.info("   - LoRA adapters: ~8 GB")
    logger.info("")
    
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        import torch
    except ImportError as e:
        raise RuntimeError(
            "CPU inference requires 'transformers', 'peft', and 'torch'. "
            "Install them with: pip install torch transformers peft"
        ) from e
    
    logger.info("Step 1/3: Downloading base model (~14 GB)...")
    logger.info("This will take a while. Please be patient...")
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, use_fast=False)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        device_map="cpu",
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    
    logger.info("✓ Base model downloaded successfully")
    logger.info("")
    logger.info("Step 2/3: Downloading LoRA adapters (~8 GB)...")
    
    peft_model = PeftModel.from_pretrained(base_model, MODEL_REPO_ID)
    
    logger.info("✓ LoRA adapters downloaded successfully")
    logger.info("")
    logger.info("Step 3/3: Merging adapters with base model...")
    logger.info("This may take a few minutes...")
    
    # Merge and clean up to save space
    merged_model = peft_model.merge_and_unload()
    
    logger.info("✓ Model merged successfully")
    logger.info("")
    
    # Clean up to free memory
    del merged_model
    del peft_model
    del base_model
    del tokenizer
    
    # Mark as ready
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    SENTINEL_FILE.write_text("ready")
    
    logger.info("=" * 60)
    logger.info("✓ CPU SETUP COMPLETE")
    logger.info("=" * 60)
    logger.info("The model is now ready for CPU inference.")
    logger.info("Note: CPU inference will be significantly slower than GPU.")


def install_model(force_cpu: bool = False) -> Dict[str, str]:
    """
    Install the Qwen 2.5 7B Medical LoRA model.
    
    Args:
        force_cpu: If True, use CPU mode even if GPU is available
        
    Returns:
        Dictionary with installation status information
    """
    # Check if already installed
    if SENTINEL_FILE.exists() and not force_cpu:
        logger.info("✓ Model already installed and ready")
        return {
            'status': 'success',
            'message': 'Model already installed',
            'device': 'cuda' if check_cuda_available() else 'cpu'
        }
    
    # Check dependencies
    deps = check_dependencies()
    
    if not deps['torch']:
        return {
            'status': 'error',
            'message': 'PyTorch is required. Install with: pip install torch',
            'device': None
        }
    
    # Determine installation mode
    has_cuda = check_cuda_available() and not force_cpu
    
    try:
        if has_cuda:
            if not deps['unsloth']:
                logger.warning("Unsloth not available. Falling back to CPU mode.")
                has_cuda = False
        
        if has_cuda:
            # GPU mode: download adapters only
            download_adapter_weights_gpu()
            device = 'cuda'
        else:
            # CPU mode: download full model + adapters
            if not (deps['transformers'] and deps['peft']):
                return {
                    'status': 'error',
                    'message': 'CPU mode requires transformers and peft. Install with: pip install transformers peft',
                    'device': None
                }
            download_full_model_cpu()
            device = 'cpu'
        
        return {
            'status': 'success',
            'message': f'Model installed successfully for {device.upper()} inference',
            'device': device
        }
        
    except Exception as e:
        logger.error(f"Installation failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e),
            'device': None
        }


def main():
    """Command-line interface for the installer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Install Qwen 2.5 7B Medical LoRA model from HuggingFace'
    )
    parser.add_argument(
        '--force-cpu',
        action='store_true',
        help='Force CPU mode even if GPU is available'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check installation status without installing'
    )
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check which dependencies are installed'
    )
    
    args = parser.parse_args()
    
    if args.check_deps:
        logger.info("Checking dependencies...")
        deps = check_dependencies()
        logger.info("")
        logger.info("Dependency Status:")
        logger.info("-" * 40)
        for dep, available in deps.items():
            status = "✓" if available else "✗"
            logger.info(f"  {status} {dep}")
        logger.info("")
        has_cuda = check_cuda_available()
        logger.info(f"  {'✓' if has_cuda else '✗'} CUDA GPU available")
        logger.info("")
        
        if has_cuda and deps['unsloth']:
            logger.info("→ GPU mode available (recommended)")
        elif deps['torch'] and deps['transformers'] and deps['peft']:
            logger.info("→ CPU mode available (slower)")
        else:
            logger.info("→ Missing required dependencies")
            logger.info("  Install with: pip install -r requirements.txt")
        
        return
    
    if args.check:
        if SENTINEL_FILE.exists():
            logger.info("✓ Model is installed and ready")
            device = "cuda" if check_cuda_available() else "cpu"
            logger.info(f"  Device: {device.upper()}")
        else:
            logger.info("✗ Model is not installed")
            logger.info("  Run without --check flag to install")
        return
    
    # Run installation
    logger.info("Starting Qwen 2.5 7B Medical LoRA installation...")
    logger.info("")
    
    result = install_model(force_cpu=args.force_cpu)
    
    if result['status'] == 'success':
        logger.info("")
        logger.info("🎉 Installation completed successfully!")
        sys.exit(0)
    else:
        logger.error("")
        logger.error(f"❌ Installation failed: {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
