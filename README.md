# Biomed Chat

Practitioner-focused chatbot UI for biomedical engineers with specialized AI responses for biomedical engineering topics. Supports multiple AI providers (Grok, Gemini, OpenAI, Anthropic) and includes an optional local medical model.

**🎉 Fine-tuned medical model available!** [Qwen 2.5 7B Medical LoRA](https://huggingface.co/ttennant/qwen2.5-7b-medical-lora) - now integrated with optional local inference.

## 📖 Quick Links

- **[Installation Guide](INSTALL.md)** - Simplest way to get started
- **[Quick Reference](QUICKREF.md)** - All commands in one page
- **[Local Model Guide](README_LOCAL_MODEL.md)** - Detailed local model setup
- **[Local Model Quick Start](QUICKSTART_LOCAL_MODEL.md)** - Fast local model install

## 🚀 Quick Start with Docker (Easiest Way)

**No coding required!** Use Docker to run Biomed Chat on any computer (Windows, Mac, or Linux).

### What You Need
- **Computer** (Windows, Mac, or Linux)
- **Docker Desktop** installed ([Download here](https://www.docker.com/products/docker-desktop))
- **Web browser** (Chrome, Firefox, Safari, or Edge)

### Step-by-Step Instructions

1. **Download the project:**
   - If you have the files, skip to step 2
   - If not, download or clone the biomed-chat folder to your computer

2. **Open Terminal/Command Prompt:**
   - **Windows:** Press `Win + R`, type `cmd`, press Enter
   - **Mac:** Press `Cmd + Space`, type "Terminal", press Enter
   - **Linux:** Press `Ctrl + Alt + T`

3. **Navigate to the biomedical-chat folder:**
   ```bash
   cd Downloads/biomed-chat
   ```
   *(Or wherever you saved the folder. If you're unsure, ask someone or use the file explorer to find the exact path)*

4. **Start the application (assumes that docker is already installed on your system, if not please install):**
   ```bash
   docker-compose up -d
   ```
   *This command downloads everything needed and starts the app in the background*

5. **Open your web browser and go to:**
   ```
   http://localhost:3000
   ```
   *Or try: http://127.0.0.1:3000*

That's it! Biomed Chat will open in your browser.

### First Time Setup (Optional)
- **Try the demo mode first** - it works without any setup!
- **For full features:** Click the ⚙️ Settings icon and add an API key (see below)

### What If Something Goes Wrong?

**"command not found" or "docker-compose not found":**
- Make sure Docker Desktop is installed and running
- Try restarting your terminal

**"Port already in use" or "address already in use":**
- Close other web applications or change the port by editing docker-compose.yml:
  ```yaml
  ports:
    - "3001:3000"  # Use port 3001 instead
  ```

**"Permission denied" or "access denied":**
- On Mac/Linux: Try `sudo docker-compose up -d`
- Contact IT support if issues persist

**Application won't load:**
- Wait 1-2 minutes for first startup (downloads models)
- Check Docker Desktop - make sure containers are running
- Try refreshing the browser page

**Need to stop the app:**
```bash
docker-compose down
```

**Need more help?**
- Check the [Docker Guide](DOCKER.md) for detailed instructions
- Most issues are solved by restarting Docker Desktop

### Benefits of Docker
✅ **Works on any computer** - same setup everywhere  
✅ **No installation headaches** - everything included  
✅ **Safe and isolated** - doesn't interfere with your system  
✅ **Easy cleanup** - delete when done  

## Features

- **Multi-API Support**: Grok (recommended), Gemini, OpenAI, and Anthropic
- **Optional Local Model**: Privacy-focused offline inference with Qwen 2.5 7B Medical LoRA
- **Smart API Fallback**: Automatically uses mock responses when API unavailable
- **Biomedical Focus**: Tailored system prompt for biomedical engineering professionals
- **Streaming Responses**: Real-time response streaming for better user experience
- **Demo Mode**: Full functionality without API keys using realistic mock responses

## Quick Start

### Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.10+** - [Download](https://www.python.org/)
- **Git** - For cloning the repository

### One-Command Installation

The fastest way to get started:

```bash
git clone <repository-url> && cd biomed-chat && chmod +x quick-start.sh && ./quick-start.sh
```

This command will:
- ✅ Install all dependencies automatically
- ✅ Set up configuration files  
- ✅ Check for API keys (optional - works in demo mode without them)
- ✅ Start the application at `http://localhost:3000`

### Manual Installation

For step-by-step control:

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd biomed-chat
   ./setup.sh
   ```

2. **Configure API keys** (optional - edit `.env`):
   ```bash
   nano .env  # or your preferred editor
   ```

3. **Start the application:**
   ```bash
   npm run dev
   ```

Open `http://localhost:3000` in your browser. The app works in demo mode without API keys!

## Configuration

### API Provider Setup

Edit `.env` to configure your preferred AI provider:

```env
# Choose your AI provider (grok recommended)
API_PROVIDER="grok"

# API Keys - only one required based on provider
GROK_API_KEY="your_grok_api_key_here"
GEMINI_API_KEY="your_gemini_api_key_here"
OPENAI_API_KEY="your_openai_api_key_here"
ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Optional settings
PORT=3000
SITE_PASSWORD="your_password_here"  # For protected access
```

**Demo Mode**: Comment out or remove API keys to use predefined responses without API costs.

**Recommended Provider**: Grok offers best performance for biomedical engineering topics. Other providers are fully supported.

### Running the Application

```bash
npm run dev
```

The Node server automatically spawns the Python FastAPI backend. To manage the Python service manually, set `DISABLE_PYTHON_AUTOSTART=1` in your environment.

## Local Model Setup (Optional)

The application includes an optional local Qwen 2.5 7B Medical LoRA model for privacy-focused, offline inference.

### Installation Methods

**Method 1: Web UI (Recommended)**
1. Open the app and click **Settings** (⚙️)
2. Navigate to **Local Qwen Model** section
3. Click **Download** button
4. Wait for installation (10-60 minutes depending on connection)
5. Select "Local Medical (Qwen 2.5 7B)" from model dropdown

**Method 2: Command Line**
```bash
# Interactive installation with GPU/CPU auto-detection
./install_qwen.sh

# Or use npm scripts
npm run install-model          # Auto-detect GPU/CPU
npm run install-model-cpu      # Force CPU mode
npm run check-model            # Check installation status
```

### System Requirements

**GPU Mode** (Recommended):
- NVIDIA GPU with 8+ GB VRAM
- CUDA toolkit installed
- ~8 GB download
- Fast inference (10-50x faster than CPU)

**CPU Mode**:
- 32+ GB RAM recommended
- ~22 GB download (base model + adapters)
- Slower inference but works on any system

### Key Benefits

- ✓ All processing on your local machine
- ✓ No data sent to external servers
- ✓ Works completely offline after download
- ✓ HIPAA-friendly for sensitive data
- ✓ No API costs

For detailed instructions and troubleshooting, see [README_LOCAL_MODEL.md](README_LOCAL_MODEL.md) or [QUICKSTART_LOCAL_MODEL.md](QUICKSTART_LOCAL_MODEL.md).

## Mock Response System

When an API key is not configured, the system automatically provides realistic mock responses for common biomedical engineering topics:

- **ECG/EKG Analysis**: Signal processing, QRS detection, rhythm analysis
- **Bioimpedance**: Measurement techniques, safety considerations
- **FDA Regulatory**: 510(k) submission process, requirements
- **MRI Safety**: Magnetic field considerations, device testing
- **General Topics**: Fallback responses explaining mock mode

Mock responses include proper formatting, references, and streaming behavior identical to real API responses.

### API Modes

**Production Mode** (API key configured):
- Uses selected API provider for dynamic responses
- Falls back to mocks if API fails

**Demo Mode** (no API key):
- Uses predefined responses for common topics
- Perfect for demonstrations and development
- No API costs or rate limits

## Troubleshooting

### Quick Diagnosis

Run the automated health check to diagnose common issues:

```bash
./health-check.sh
# or
npm run health
```

This automatically checks:
- ✅ Node.js and Python versions
- ✅ Installed dependencies
- ✅ Configuration files
- ✅ Port availability
- ✅ GPU detection
- ✅ Disk space

### Common Issues

**"Module not found" errors:**
```bash
# Reinstall dependencies
npm install
pip install -r requirements.txt --force-reinstall
```

**Port already in use:**
```bash
# Change port in .env or kill the process
lsof -ti:3000 | xargs kill -9
# Or change port in .env:
echo "PORT=3001" >> .env
```

**Python service not starting:**
```bash
# Check if service is running
ps aux | grep uvicorn

# Check dependencies
python3 -c "import uvicorn, fastapi; print('✓ Core dependencies OK')"

# Restart the server
npm run dev
```

**GPU not detected:**
- Ensure CUDA drivers are installed
- Check `nvidia-smi` command works
- Verify PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`

**Python externally-managed environment:**
```bash
# The setup script handles this automatically
# Manual install if needed:
pip3 install --break-system-packages -r requirements.txt
```

**Model download issues:**
```bash
# Check disk space (need ~22 GB)
df -h ~

# Check model status
npm run check-model

# Re-download if needed
./install_qwen.sh
```

**API rate limits:**
- Switch to demo mode by removing API keys
- Wait for rate limit reset
- Consider upgrading API plan

**Slow local model inference:**
- Use GPU mode if available (10-50x faster)
- Reduce conversation history length
- Ensure no other GPU-intensive applications are running

**Unsloth import errors:**
- Don't worry - system automatically falls back to CPU mode
- CPU mode uses standard transformers + PEFT
- Slower but fully functional

**Still having issues?**
1. Check terminal logs from `npm run dev`
2. Try a clean setup:
   ```bash
   rm -rf node_modules __pycache__
   ./setup.sh
   ```
3. Open a GitHub issue with error messages and health check output

## Technical Notes

- System prompt emphasizes concise, actionable outputs with regulatory and validation hooks (IEC 60601, ISO 14971, FDA QSR)
- Streaming responses provide low-latency user interface
- Mock responses maintain identical format and quality to API responses
- Shift+Enter inserts newline in chat interface

## Roadmap

- Progress UI for model download size and throughput
- CPU-optimized distilled model for lower-end hardware
- Additional fine-tuning for specialized biomedical subfields

---

## License

See [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: Check [Quick Links](#-quick-links) for detailed guides
- **Issues**: Open a GitHub issue with error messages and health check output
- **Health Check**: Run `./health-check.sh` for automated diagnostics
