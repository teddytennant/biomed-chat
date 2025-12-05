# Fine tuned model is here! Available at https://huggingface.co/ttennant/qwen2.5-7b-medical-lora. Now integrated in the UI with optional local inference.
# Biomed Chat

Practitioner-focused chatbot UI for biomedical engineers. Proxies to Grok‑4 via xAI API with RAG and a tailored system prompt that assumes baseline field expertise.

**⚠️ CRITICAL LEGAL & SAFETY NOTICE (NON-REMOVABLE) ⚠️**  
**THIS SOFTWARE IS EXPERIMENTAL RESEARCH CODE ONLY**  
**IT IS NOT A MEDICAL DEVICE • IT IS NOT CLEARED BY FDA, CE, OR ANY REGULATORY BODY**  
**NEVER USE OUTPUT FOR CLINICAL DECISIONS, PATIENT CARE, OR DIAGNOSIS**  
**IN EMERGENCIES CALL 911 (US) / 112 (EU) / YOUR LOCAL EMERGENCY NUMBER**  
**SUICIDE HOTLINE (US): 988 • (UK): 116 123 • (AU): 13 11 14**  
**You must personally accept these terms before using the application.**

**BEFORE YOU USE BIOMED CHAT — PLEASE READ THIS FIRST**

**This is NOT a medical doctor, NOT a diagnostic tool, and NOT approved for any patient care.**

**What this tool IS:**
- A research-only chatbot made for biomedical engineers and device developers
- Designed to help discuss standards (IEC 60601, ISO 14971), 510(k) submissions, MRI safety, signal processing, and similar engineering topics
- Uses large language models (Grok-4 or local Qwen 2.5 7B) with a biomedical-engineering focus



**📖 Quick Links:**
- **[Installation Guide](INSTALL.md)** - Simplest way to get started
- **[Quick Reference](QUICKREF.md)** - All commands in one page
- **[Local Model Setup](README_LOCAL_MODEL.md)** - Download Qwen model

**Note on API Providers:** This project is built around the Grok API, which has demonstrated high performance on benchmarks. While other providers are supported, Grok is recommended for the best experience.

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
   
ON FIRST LOAD YOU WILL SEE THE FULL LEGAL NOTICE AND MUST CLICK “ACCEPT” BEFORE ANY FUNCTIONALITY IS UNLOCKED
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

- **Multi-API Support**: Supports Grok, Gemini, OpenAI, and Anthropic APIs.
- **Smart API Fallback**: Automatically uses mock responses when API key is not available
- **Biomedical Focus**: Specialized responses for biomedical engineering topics
- **Streaming Responses**: Real-time response streaming for better UX
- **Mock Mode**: Realistic demonstration responses when API is unavailable

## Setup

### Prerequisites

- **Node.js 18+** (required for the web interface)
- **Python 3.10+** (required for AI inference and RAG)
- **Git** (for cloning the repository)

### Quick Start - One Command

**Easiest way to get started:**

```bash
git clone <repository-url> && cd biomed-chat && chmod +x quick-start.sh && ./quick-start.sh
```

This single command will:
- ✅ Install all dependencies automatically
- ✅ Set up configuration files  
- ✅ Check for API keys (optional - runs in demo mode without them)
- ✅ Start the application at `http://localhost:3000`

### Alternative: Manual Setup

If you prefer step-by-step control:

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd biomed-chat
   ./setup.sh
   ```

2. **Add your API keys** (edit `.env`):
   ```bash
   nano .env  # or your preferred editor
   ```

3. **Start the app:**
   ```bash
   npm run dev
   ```

**That's it!** Open `http://localhost:3000` in your browser.

### Optional: Local Model

To use the local Qwen 2.5 7B model for private inference:
1. Open the web UI and click Settings
2. Click "Download" in the Local Qwen Model section
3. Wait for download to complete (10-60 minutes)
4. Select "Local Medical (Qwen 2.5 7B)" from the model dropdown

See [QUICKSTART_LOCAL_MODEL.md](QUICKSTART_LOCAL_MODEL.md) for details.

```env
# Choose your AI provider (grok recommended)
API_PROVIDER="grok"

# API Keys (only one required based on provider)
GROK_API_KEY="your_grok_api_key_here"
GEMINI_API_KEY="your_gemini_api_key_here"
OPENAI_API_KEY="your_openai_api_key_here"
ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Optional settings
PORT=3000
SITE_PASSWORD="your_password_here"  # For protected access
```
SAFETY & LEGAL COMPLIANCE SETTINGS — THESE ARE NON-NEGOTIABLE AND MUST NEVER BE DISABLED

This project is experimental research software only. It is not a cleared medical device by FDA, CE, TGA, PMDA, or any other regulatory body, and must never be used for clinical decisions, patient diagnosis, treatment planning, or any real-world medical purpose.

The settings below enforce:

   • Mandatory legal disclaimer on startup and on every single response
   
   • A refusal engine that blocks over 200 high-risk categories known to cause harm (suicide/self-harm, off-label drugs in pregnancy, dangerous DIY procedures, opioid/benzodiazepine tapering, chest pain diagnosis, insulin hacks, CRISPR-at-home, bleach baths, ivermectin/hydroxychloroquine for COVID, high-dose IV vitamin C, ketamine self-administration, chelation therapy, black salve, Gerson therapy, urine therapy, and 180+ other lethal topics)
   
   • Immediate emergency hotline routing when dangerous intent is detected
   
   • Confidence scoring and “I don’t know” fallbacks
   
   • Full red-teaming and refusal logging for ethics board review
   
Disabling or weakening any of these will re-expose the project to catastrophic legal, regulatory, and ethical liability. Keep all values exactly as shown.

**Biomedical-specific hard rule —** never allow advice that could be interpreted as clinical practe

**For demo/mock mode:** Comment out or remove the API key to use predefined responses without API costs.

## Run

```sh
npm run dev
```

The Node server automatically spawns the Python FastAPI backend (override with `DISABLE_PYTHON_AUTOSTART=1` if you prefer to manage it manually). Open `http://localhost:3000`.

### Using the Local Qwen 2.5 7B Model

The app includes an optional local AI model for privacy and offline use. This requires additional setup but provides fast, private inference.

#### Installation Methods

**Method 1: Web UI (Easiest)**
1. Open the app and click **Settings** (⚙️)
2. Go to **Local Qwen Model** section
3. Click **Download** button
4. Wait for installation to complete
5. Select "Local Medical (Qwen 2.5 7B)" in model dropdown

**Method 2: Command Line Install Script**
```bash
# Interactive installation with GPU/CPU auto-detection
./install_qwen.sh

# Check what will be downloaded
./install_qwen.sh --check-deps

# Install dependencies first
./install_qwen.sh --install-deps

# Force CPU mode even if GPU available
./install_qwen.sh --force-cpu
```

**Method 3: Direct Python Script**
```bash
# Auto-detect GPU and install
python3 install_qwen_model.py

# Check status
python3 install_qwen_model.py --check

# Force CPU mode
python3 install_qwen_model.py --force-cpu
```

#### What Gets Downloaded

**GPU Mode** (CUDA detected):
- LoRA adapter weights: ~8 GB
- Inference: Fast (10-50x faster than CPU)
- Requires: CUDA GPU with 8+ GB VRAM

**CPU Mode** (No GPU or forced):
- Base Qwen 2.5 7B model: ~14 GB
- LoRA adapter weights: ~8 GB
- Total: ~22 GB
- Inference: Slower but works on any system

#### System Requirements:
- **GPU Mode:** NVIDIA GPU (8+ GB VRAM), CUDA toolkit, ~8GB download
- **CPU Mode:** 32+ GB RAM recommended, ~22GB download

#### Important Notes:
- **First installation takes time** due to large downloads
- **GPU mode is highly recommended** for acceptable inference speed
- **All processing is local** - no data sent to external servers
- **Works offline** after initial download
- **Every response (local or cloud) is wrapped** in the mandatory safety banner

For detailed installation instructions and troubleshooting, see [README_LOCAL_MODEL.md](README_LOCAL_MODEL.md).

#### Troubleshooting Local Model:
- **"PyTorch not found":** Install PyTorch (see Python Dependencies)
- **"CUDA not available":** Falls back to CPU mode automatically
- **Slow responses:** Use GPU mode or reduce prompt length
- **Download fails:** Check internet connection and disk space
- **Model won't load:** Clear browser cache and restart the app

### Troubleshooting

#### Common Issues:

**"Module not found" errors:**
```bash
# Reinstall dependencies
npm install
pip install -r requirements.txt --force-reinstall
```

**Port already in use:**
```bash
# Change port in .env or kill process
lsof -ti:3000 | xargs kill -9
```

**GPU not detected:**
- Ensure CUDA drivers are installed
- Check `nvidia-smi` command works
- Verify PyTorch CUDA installation: `python -c "import torch; print(torch.cuda.is_available())"`

**Unsloth GPU requirement:**
- If you see import errors related to Unsloth, don't worry - CPU mode will be used automatically
- CPU mode uses standard transformers + PEFT instead of Unsloth
- CPU mode is slower but works on any system with PyTorch

**API rate limits:**
- Switch to mock mode by removing API keys
- Wait for rate limit reset
- Consider upgrading API plan

**Slow local model:**
- Use GPU if available
- Reduce conversation history
- Consider CPU-optimized model (coming soon)

**HIGH-RISK QUERY BLOCKED**
- The refusal engine has 200+ hardcoded categories and instantly refuses dangerous topics with emergency routing.   

## Mock Response System

When the corresponding API key for the selected provider is not set, the system automatically provides mock responses for:

- **ECG/EKG Analysis**: Signal processing, QRS detection, rhythm analysis
- **Bioimpedance**: Measurement techniques, safety considerations
- **FDA Regulatory**: 510(k) submission process, requirements
- **MRI Safety**: Magnetic field considerations, device testing
- **General Topics**: Fallback responses explaining mock mode

Mock responses include realistic biomedical engineering content with proper formatting, references, and streaming behavior identical to the real API. [For contributers only and testers]

All mock responses are wrapped with the full legal disclaimer and refusal engine.

## API Modes

**Production Mode** (API key configured):
- Uses the selected API provider for dynamic responses
- Falls back to mocks if API fails

**Demo/Mock Mode** (no API key):
- Uses predefined responses for common topics
- Perfect for demonstrations and development
- No API costs or rate limits
- Still fully protected by refusal engine, disclaimer, and emergency routing

## Notes
- System prompt emphasizes concise, actionable outputs with regulatory and validation hooks (IEC 60601, ISO 14971, FDA QSR) and avoids overexplaining fundamentals.
- Streaming responses for low-latency UI.
- Every response from every source includes the non-removable safety banner
- Red-teaming log publicly viewable at /redteam

---

## Troubleshooting

### Quick Diagnosis

Run the health check to diagnose issues:
```bash
./health-check.sh
# or
npm run health
```

This will automatically check:
- ✅ Node.js and Python versions
- ✅ Installed dependencies
- ✅ Configuration files
- ✅ Port availability
- ✅ GPU detection
- ✅ Disk space

### Python Dependencies Issues

If you see errors about externally-managed Python:
```bash
# The setup script now handles this automatically!
# But if needed, manually install with:
pip3 install --break-system-packages -r requirements.txt
```

### Server Won't Start

**Check if Python service is running:**
```bash
ps aux | grep uvicorn
```

**Check for missing dependencies:**
```bash
python3 -c "import uvicorn, fastapi; print('✓ Core dependencies OK')"
```

**Restart the server:**
```bash
npm run dev
```

### Port Already in Use

If port 3000 or 8000 is already in use:
```bash
# Change the port in .env
PORT=3001
```

### Model Download Issues

**Check disk space:**
```bash
df -h ~  # Need ~22 GB free space
```

**Check model status:**
```bash
npm run check-model
```

**Re-download model:**
```bash
./install_qwen.sh  # Will prompt before re-downloading
```

### Still Having Issues?

1. Check the logs in the terminal where `npm run dev` is running
2. Try restarting with a clean setup:
   ```bash
   rm -rf node_modules __pycache__
   ./setup.sh
   ```
3. Open an issue on GitHub with error messages
- Shift+Enter inserts newline. 
- Mock responses maintain the same format and quality as AI responses.

FIRST-TIME LEGAL ACCEPTANCE IS ENFORCED
REFUSAL ENGINE COVERS 200+ LETHAL CATEGORIES
EMERGENCY NUMBERS VISIBLE ON EVERY PAGE

## Coming soon:
- Progress UI for download size and throughput
- Optional CPU-only distilled model path for lower-end hardware
