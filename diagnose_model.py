#!/usr/bin/env python3
"""Test script to check local model dependencies and diagnose download issues."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🔍 Checking local model dependencies...")
print("=" * 50)

# Check Python version
print(f"Python version: {sys.version}")

# Check PyTorch
try:
    import torch
    print(f"✅ PyTorch available: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   CUDA devices: {torch.cuda.device_count()}")
        print(f"   Current device: {torch.cuda.current_device()}")
        print(f"   Device name: {torch.cuda.get_device_name()}")
except ImportError as e:
    print(f"❌ PyTorch not available: {e}")

# Check Unsloth
try:
    from unsloth import FastLanguageModel
    print("✅ Unsloth available")
except ImportError as e:
    print(f"❌ Unsloth not available: {e}")

# Check transformers and peft (for CPU fallback)
try:
    import transformers
    print(f"✅ Transformers available: {transformers.__version__}")
except ImportError as e:
    print("❌ Transformers not available")

try:
    import peft
    print(f"✅ PEFT available: {peft.__version__}")
except ImportError as e:
    print("❌ PEFT not available")

print("\n" + "=" * 50)
print("Testing local model module...")

# Test local model
try:
    import local_model
    status = local_model.get_status()
    print(f"Initial status: {status}")

    # Test dependency checks
    print(f"Torch available: {local_model._torch_available()}")
    print(f"GPU ready: {local_model._gpu_ready()}")
    print(f"Has CUDA: {local_model._has_cuda()}")

    # Try to start download
    print("\nAttempting to start download...")
    result = local_model.start_download()
    print(f"Download start result: {result}")

except Exception as e:
    print(f"❌ Error testing local model: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Diagnosis complete.")