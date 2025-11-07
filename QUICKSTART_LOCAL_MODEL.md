# Quick Start: Local Model Installation

This is a quick reference for installing the Qwen 2.5 7B Medical LoRA model.

## TL;DR

### Web UI Installation (Easiest)
1. Open app → Click Settings (⚙️)
2. Scroll to "Local Qwen Model"
3. Click "Download"
4. Wait for completion
5. Select model from dropdown

### Command Line Installation
```bash
# One-command install
./install_qwen.sh

# OR with npm
npm run install-model
```

## What Gets Downloaded

| Mode | Download Size | Memory Usage | Speed | Requirements |
|------|---------------|--------------|-------|--------------|
| **GPU** | ~8-22 GB* | ~3.5 GB VRAM | Fast ⚡ | CUDA GPU (8+ GB VRAM) |
| **CPU** | ~22 GB | ~16-20 GB RAM | Slow 🐌 | 32+ GB RAM |

**\*GPU Download Note**: Downloads base model (~14 GB) + adapters (~8 GB), but base model is cached by HuggingFace. If you already have Qwen models, only adapters (~8 GB) download. The magic: 4-bit quantization reduces VRAM usage to ~3.5 GB!

## Quick Commands

```bash
# Install model (auto-detect GPU/CPU)
./install_qwen.sh

# Check if already installed
./install_qwen.sh --check

# Install dependencies
./install_qwen.sh --install-deps

# Force CPU mode
./install_qwen.sh --force-cpu

# OR use npm scripts
npm run install-model          # Auto-detect
npm run install-model-cpu      # Force CPU
npm run check-model            # Check status
npm run check-deps             # Check dependencies
```

## Troubleshooting

### Error: "PyTorch not installed"
```bash
# GPU mode
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CPU mode
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Error: "transformers not found"
```bash
pip install transformers peft
```

### Error: "unsloth not available"
Don't worry! The system automatically falls back to CPU mode.

### Download is slow or stuck
- Check internet connection
- Ensure sufficient disk space (25 GB minimum)
- Downloads resume automatically if interrupted

### Model installed but not showing in UI
```bash
# Restart the application
npm run dev
```

### Out of memory errors
- **GPU**: Close other GPU applications, ensure 8+ GB VRAM free
- **CPU**: Close memory-intensive apps, ensure 32+ GB RAM

## Time Estimates

| Connection | GPU Mode | CPU Mode |
|------------|----------|----------|
| Fast (100 Mbps+) | 10-15 min | 30-45 min |
| Medium (50 Mbps) | 20-30 min | 60-90 min |
| Slow (10 Mbps) | 60+ min | 180+ min |

## Privacy Benefits

✓ All processing on your machine  
✓ No data sent to external servers  
✓ Works offline after download  
✓ HIPAA-friendly for sensitive data  

## Performance Comparison

| Mode | Response Time | Cost | Privacy |
|------|---------------|------|---------|
| **Local GPU** | ~5-15 sec | Free ✓ | High ✓✓✓ |
| **Local CPU** | ~60-300 sec | Free ✓ | High ✓✓✓ |
| **Cloud APIs** | ~2-5 sec | Paid ✗ | Medium ✓ |

## Need More Help?

- **Detailed docs**: See [README_LOCAL_MODEL.md](README_LOCAL_MODEL.md)
- **Main docs**: See [README.md](README.md)
- **Check dependencies**: `./install_qwen.sh --check-deps`

---

**Remember**: First installation takes time due to large downloads. Be patient! ☕
