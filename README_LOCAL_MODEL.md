# Qwen 2.5 7B Medical LoRA Model Installation Guide

This document explains how to install and use the fine-tuned Qwen 2.5 7B Medical LoRA model from HuggingFace in the Biomed Chat application.

## Overview

The local model provides privacy-preserving medical AI inference without sending data to external APIs. The model is fine-tuned specifically for biomedical and clinical applications.

**Model Repository**: `ttennant/qwen2.5-7b-medical-lora`  
**Base Model**: `Qwen/Qwen2.5-7B-Instruct`

## Installation Methods

### Method 1: Web UI (Recommended)

The easiest way to install the model is through the web interface:

1. Open the Biomed Chat application in your browser
2. Click the **Settings** icon (⚙️) in the top-right corner
3. Scroll to the **Local Qwen Model** section
4. Click the **Download** button
5. Wait for the download and installation to complete

The web UI will automatically:
- Detect if you have a CUDA GPU available
- Download the appropriate files (adapters only for GPU, full model for CPU)
- Show progress and status updates
- Enable the model once ready

### Method 2: Command Line

You can also install the model using the standalone script:

```bash
# Basic installation (auto-detects GPU)
python3 install_qwen_model.py

# Force CPU mode even if GPU is available
python3 install_qwen_model.py --force-cpu

# Check installation status
python3 install_qwen_model.py --check

# Check which dependencies are installed
python3 install_qwen_model.py --check-deps
```

## Installation Modes

### GPU Mode (Recommended)

**Requirements:**
- CUDA-compatible NVIDIA GPU
- CUDA toolkit installed
- PyTorch with CUDA support
- `unsloth` package for efficient inference

**Download Size:** ~8-22 GB (varies based on HuggingFace cache)
- Base Qwen 2.5 7B model: ~14 GB (cached and shared)
- LoRA adapters: ~8 GB

**Important:** While the total download includes both base model and adapters, the base model is cached by HuggingFace and shared across all Qwen-based models. If you already have Qwen models cached, only the adapters (~8 GB) will be downloaded.

**VRAM Usage:** ~3.5 GB (thanks to 4-bit quantization)

**Installation:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install unsloth accelerate bitsandbytes
python3 install_qwen_model.py
```

**Benefits:**
- Much faster inference (10-50x speedup vs CPU)
- Lower VRAM usage with 4-bit quantization (3.5 GB vs 14 GB full precision)
- Efficient LoRA adapter application
- Base model cache shared with other Qwen models

### Why GPU Mode Uses Less VRAM Despite Downloading the Same Base Model

This is a common point of confusion! Here's what's happening:

**GPU Mode (with unsloth + 4-bit quantization):**
1. Downloads base model (~14 GB on disk)
2. Downloads LoRA adapters (~8 GB on disk)
3. **Loads base model in 4-bit format** → Only ~3.5 GB VRAM
4. Applies LoRA adapters dynamically
5. **Total VRAM usage: ~3.5-4 GB**

**CPU Mode (with transformers + peft):**
1. Downloads base model (~14 GB on disk)
2. Downloads LoRA adapters (~8 GB on disk)
3. **Loads base model in full precision (FP32)** → ~14 GB RAM
4. Merges adapters into base model
5. **Total RAM usage: ~16-20 GB**

The key difference is **quantization**: GPU mode uses 4-bit integers instead of 32-bit floats, reducing memory by ~75% while maintaining most of the model's accuracy.

### CPU Mode (Fallback)

**Requirements:**
- PyTorch (CPU version)
- `transformers` and `peft` packages

**Download Size:** ~22 GB (base model ~14 GB + adapters ~8 GB)

**Installation:**
```bash
pip install torch transformers peft
python3 install_qwen_model.py --force-cpu
```

**Note:** CPU inference will be significantly slower than GPU inference but doesn't require special hardware.

## Prerequisites

Before installing the model, ensure you have:

### Required Python Packages

```bash
pip install torch>=2.1.0
pip install transformers>=4.39.0
pip install peft>=0.10.0
```

### Optional (for GPU acceleration)

```bash
pip install unsloth>=2024.2.6
pip install accelerate>=0.27.0
pip install bitsandbytes>=0.43.0
```

### System Requirements

**For GPU Mode:**
- NVIDIA GPU with CUDA support (8 GB+ VRAM recommended)
- 16 GB+ system RAM
- 10 GB free disk space

**For CPU Mode:**
- 32 GB+ system RAM recommended
- 25 GB free disk space
- Fast CPU (inference will still be slow)

## Using the Model

Once installed, the model will be available in the web UI:

1. Open **Settings**
2. In the **Model** dropdown, select **Local Medical (Qwen 2.5 7B)**
3. Start chatting - your queries will be processed locally

The model will:
- Use RAG (Retrieval Augmented Generation) when available
- Provide medical and biomedical knowledge
- Run entirely on your local machine (no API calls)

## Troubleshooting

### Download Fails or Stalls

The model files are large and may take time to download. If the download fails:

1. Check your internet connection
2. Ensure you have enough disk space
3. Try running the installation script directly:
   ```bash
   python3 install_qwen_model.py
   ```
4. Check the logs for specific error messages

### Out of Memory Errors

**GPU:**
- The model uses 4-bit quantization to reduce memory usage
- Ensure your GPU has at least 8 GB VRAM
- Close other GPU-intensive applications

**CPU:**
- CPU mode requires substantial RAM (32 GB+ recommended)
- Close other memory-intensive applications
- Consider upgrading your RAM

### Model Not Appearing in Settings

1. Check the model status in Settings
2. Verify the installation completed successfully:
   ```bash
   python3 install_qwen_model.py --check
   ```
3. Restart the application:
   ```bash
   npm run dev
   ```

### Slow Inference

**If using CPU mode:**
- This is expected - CPU inference is much slower than GPU
- Consider using GPU mode if you have compatible hardware
- For faster responses, use the cloud API models instead

**If using GPU mode:**
- Ensure CUDA is properly installed and detected
- Check GPU utilization during inference
- Verify you're not running other GPU-intensive tasks

## Uninstalling

To remove the downloaded model files:

```bash
rm -rf models/qwen2.5-7b-medical-lora
rm -rf ~/.cache/huggingface/hub/models--ttennant--qwen2.5-7b-medical-lora
```

For CPU mode, also remove the base model cache:

```bash
rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct
```

## Technical Details

### Model Architecture

- **Base**: Qwen 2.5 7B Instruct (7 billion parameters)
- **Adapter**: LoRA (Low-Rank Adaptation) fine-tuned weights
- **Quantization**: 4-bit (GPU) or FP32 (CPU)
- **Context Length**: 2048 tokens
- **Fine-tuning**: Specialized for medical/biomedical queries

### Files Downloaded

**GPU Mode** (`~/.cache/huggingface/hub/models--ttennant--qwen2.5-7b-medical-lora/`):
- LoRA adapter weights
- Tokenizer configuration
- Model configuration

**CPU Mode** (additional files in `~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/`):
- Full base model weights (~14 GB)
- Model safetensors

### Privacy & Security

- **Local Processing**: All inference happens on your machine
- **No Data Sharing**: Queries are not sent to external servers
- **Offline Capable**: Once downloaded, works without internet
- **HIPAA Considerations**: Suitable for sensitive medical data (when properly deployed)

## Advanced Configuration

### Custom Installation Path

Edit `install_qwen_model.py` to change the installation directory:

```python
MODELS_DIR = Path("/path/to/your/models")
```

### Performance Tuning

Edit `local_model.py` to adjust generation parameters:

```python
MAX_NEW_TOKENS = 512  # Maximum response length
GENERATION_TEMPERATURE = 0.3  # Creativity (0.1-1.0)
GENERATION_TOP_P = 0.9  # Nucleus sampling threshold
```

### Integration with RAG

The local model automatically integrates with the RAG pipeline. To use RAG context:

1. Ensure your vector database is populated
2. The system will automatically retrieve relevant context
3. Context is passed to the model for enhanced responses

## Support

For issues or questions:

1. Check the logs: Application will show detailed error messages
2. Run diagnostics: `python3 install_qwen_model.py --check-deps`
3. Review the main README.md for general setup help
4. Check system requirements match your hardware

## Updates

To update the model to a newer version:

1. Remove the `.ready` sentinel file:
   ```bash
   rm models/qwen2.5-7b-medical-lora/.ready
   ```
2. Clear the HuggingFace cache (optional but recommended):
   ```bash
   rm -rf ~/.cache/huggingface/hub/models--ttennant--qwen2.5-7b-medical-lora
   ```
3. Re-run the installation through the Web UI or command line

---

**Note**: This model is for research and educational purposes. Always verify AI-generated medical information with qualified healthcare professionals.
