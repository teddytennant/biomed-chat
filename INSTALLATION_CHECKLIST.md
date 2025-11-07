# Installation Verification Checklist

Use this checklist to verify your Qwen 2.5 7B Medical LoRA model installation is complete and working correctly.

## Pre-Installation Checks

- [ ] Python 3.10+ is installed (`python3 --version`)
- [ ] pip is installed (`pip3 --version`)
- [ ] Node.js 18+ is installed (`node --version`)
- [ ] At least 25 GB free disk space available
- [ ] Internet connection is stable

### For GPU Mode (Optional but Recommended)
- [ ] NVIDIA GPU with CUDA support
- [ ] CUDA toolkit installed (`nvidia-smi` works)
- [ ] At least 8 GB VRAM available
- [ ] PyTorch with CUDA installed (`python3 -c "import torch; print(torch.cuda.is_available())"` returns True)

### For CPU Mode
- [ ] At least 32 GB RAM available (16 GB minimum but slower)
- [ ] PyTorch installed (`python3 -c "import torch"` works)

## Installation Steps

### Option 1: Web UI Installation (Recommended)
- [ ] Application is running (`npm run dev`)
- [ ] Open http://localhost:3000
- [ ] Click Settings icon (⚙️) in top-right
- [ ] Scroll to "Local Qwen Model" section
- [ ] Current status shows (not "Checking status..." indefinitely)
- [ ] Click "Download" button
- [ ] Status changes to "Downloading..."
- [ ] Wait for completion (10-60 minutes)
- [ ] Status changes to "Ready"
- [ ] "Local Medical (Qwen 2.5 7B)" appears in model dropdown
- [ ] Model option is not grayed out

### Option 2: Command Line Installation
- [ ] Navigate to project directory (`cd biomed-chat`)
- [ ] Script is executable (`./install_qwen.sh --help` works)
- [ ] Check dependencies: `./install_qwen.sh --check-deps`
- [ ] All required dependencies shown with ✓
- [ ] Run installation: `./install_qwen.sh`
- [ ] Confirms GPU or CPU mode detected
- [ ] Shows download size estimate
- [ ] Accept confirmation prompt
- [ ] Installation completes without errors
- [ ] Success message displayed

## Post-Installation Verification

### File System Checks
- [ ] Sentinel file exists: `ls models/qwen2.5-7b-medical-lora/.ready`
- [ ] HuggingFace cache contains model:
  ```bash
  ls ~/.cache/huggingface/hub/ | grep -i qwen
  ```

### Status Checks
- [ ] Check with script: `./install_qwen.sh --check` shows "Model is installed and ready"
- [ ] Check with Python:
  ```bash
  python3 install_qwen_model.py --check
  ```
- [ ] API status endpoint works:
  ```bash
  curl http://localhost:8000/api/models/local/status
  # Should return: {"state": "ready", ...}
  ```

### Functional Tests

#### Test 1: Model Loads in Web UI
- [ ] Open application: http://localhost:3000
- [ ] Open Settings
- [ ] Status shows "Ready (GPU)" or "Ready (CPU)"
- [ ] Select "Local Medical (Qwen 2.5 7B)" from model dropdown
- [ ] Dropdown selection saves and persists

#### Test 2: Query Processing
- [ ] Type a simple query: "What is bioimpedance?"
- [ ] Click Send
- [ ] Response appears (may take 5-300 seconds depending on GPU/CPU)
- [ ] Response is relevant to biomedical topic
- [ ] No error messages appear

#### Test 3: Multiple Queries
- [ ] Send 2-3 different queries in succession
- [ ] Each query gets a response
- [ ] Response quality is consistent
- [ ] No memory errors or crashes

## GPU-Specific Checks (If Using GPU Mode)

- [ ] GPU is being used during inference:
  ```bash
  # In another terminal while query is processing:
  nvidia-smi
  # Should show Python process using GPU memory
  ```
- [ ] VRAM usage increases during query (use `nvidia-smi`)
- [ ] Response time is under 30 seconds
- [ ] Status shows "Ready (GPU)" not "Ready (CPU)"

## CPU-Specific Checks (If Using CPU Mode)

- [ ] Base model downloaded (~14 GB)
  ```bash
  ls ~/.cache/huggingface/hub/ | grep "Qwen2.5-7B-Instruct"
  ```
- [ ] CPU usage spikes during inference (use `htop` or Task Manager)
- [ ] Status shows "Ready (CPU)"
- [ ] Response time is 60+ seconds (expected for CPU)
- [ ] Warning about slower performance was shown

## Troubleshooting Failed Checks

### Status Stuck on "Downloading..." or "Loading..."
```bash
# Check Python service logs
# Look for errors in the terminal where you ran `npm run dev`

# Restart and retry
# Kill the application and restart
npm run dev
```

### Status Shows "Error"
```bash
# Check error details in Settings modal
# Try manual installation to see detailed error:
python3 install_qwen_model.py

# Check dependencies:
./install_qwen.sh --check-deps
```

### Model Not Appearing in Dropdown
```bash
# Verify status is "ready":
curl http://localhost:8000/api/models/local/status

# If not ready, check for errors:
python3 -c "import local_model; print(local_model.get_status())"

# Restart application:
# Ctrl+C then npm run dev
```

### Slow or No Response to Queries
```bash
# Check if Python service is running:
curl http://localhost:8000/api/health

# Check logs for errors
# Terminal output should show query processing

# For CPU mode - this is expected! CPU inference is very slow
# Consider using GPU mode or cloud API models instead
```

### Out of Memory Errors
**GPU:**
```bash
# Check available VRAM:
nvidia-smi

# Close other GPU applications
# Reduce conversation history
# Consider CPU mode if insufficient VRAM
```

**CPU:**
```bash
# Check available RAM:
free -h  # Linux
# Activity Monitor on macOS
# Task Manager on Windows

# Close other applications
# Ensure 16+ GB RAM available
```

## Performance Benchmarks

After installation, your response times should be approximately:

| Hardware | Expected Time | Status |
|----------|---------------|--------|
| High-end GPU (RTX 4090) | 5-10 sec | ✅ Excellent |
| Mid-range GPU (RTX 3060) | 10-20 sec | ✅ Good |
| High-end CPU (i9) | 60-120 sec | ⚠️ Acceptable |
| Mid-range CPU (i5) | 120-300 sec | ⚠️ Slow |

If your times are significantly slower:
- [ ] Verify GPU is actually being used (check `nvidia-smi`)
- [ ] Check for background processes consuming resources
- [ ] Ensure model loaded correctly (no errors in logs)

## Final Verification

- [ ] ✅ Model status shows "Ready"
- [ ] ✅ Model appears in dropdown and can be selected
- [ ] ✅ Test query returns relevant medical response
- [ ] ✅ Response time is acceptable for your hardware
- [ ] ✅ No error messages or warnings
- [ ] ✅ Installation documented (note GPU vs CPU mode)

## Success Criteria

**Minimum Requirements Met:**
- [ ] Status shows "Ready (GPU)" or "Ready (CPU)"
- [ ] Can select model from dropdown
- [ ] Receives responses to queries (even if slow)

**Optimal Installation Achieved:**
- [ ] Status shows "Ready (GPU)" 
- [ ] Response time under 30 seconds
- [ ] Consistent performance across queries
- [ ] No errors or warnings

## Getting Help

If any checks fail:

1. **Review logs** - Check terminal output for detailed error messages
2. **Check documentation** - See README_LOCAL_MODEL.md for troubleshooting
3. **Verify dependencies** - Run `./install_qwen.sh --check-deps`
4. **Try clean install** - Delete `.ready` file and reinstall
5. **Check disk space** - Ensure 25+ GB available
6. **Restart system** - Some GPU drivers need restart after CUDA install

## Documentation References

- [Quick Start Guide](QUICKSTART_LOCAL_MODEL.md) - Fast setup instructions
- [Detailed Guide](README_LOCAL_MODEL.md) - Comprehensive documentation
- [Main README](README.md) - Project overview
- [Installation Summary](INSTALLATION_SYSTEM_SUMMARY.md) - Technical details

---

**Date Completed**: ___________  
**Mode Used**: ☐ GPU  ☐ CPU  
**Installation Time**: ___________ minutes  
**First Query Response Time**: ___________ seconds  
**Notes**: ___________________________________________

Save this checklist for future reference or troubleshooting!
