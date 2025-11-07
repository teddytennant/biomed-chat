# Fine tuned model is here! Available at https://huggingface.co/ttennant/qwen2.5-7b-medical-lora. Now integrated in the UI with optional local inference.
# Biomed Chat

Practitioner-focused chatbot UI for biomedical engineers. Proxies to Grok‑4 via xAI API with RAG and a tailored system prompt that assumes baseline field expertise.

**Note on API Providers:** This project is built around the Grok API, which has demonstrated high performance on benchmarks. While other providers are supported, Grok is recommended for the best experience.

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
- **CUDA-capable GPU** (recommended for fast local model inference; CPU fallback available)
- **Git** (for cloning the repository)

**💡 Pro tip:** Use the automated `./setup.sh` script for the easiest installation experience.

### Quick Start (Recommended)

1. **Clone and run the automated setup:**
   ```bash
   git clone <repository-url>
   cd biomed-chat
   ./setup.sh
   ```

   The setup script will:
   - Check all prerequisites
   - Install Node.js and Python dependencies
   - Detect GPU availability
   - Create a `.env` template
   - Provide next steps

2. **Configure environment** (if not done automatically):
   ```bash
   # Edit .env with your API keys
   nano .env  # or your preferred editor
   ```

3. **Start the application:**
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

### Manual Setup (Alternative)

If you prefer manual installation or the automated script fails:

### Detailed Installation

#### Node.js Dependencies (Required)
```bash
npm install
```
This installs the web server and UI dependencies.

#### Python Dependencies

**Core Dependencies (Required):**
```bash
pip install -r requirements.txt
```

**GPU Support (Recommended for Local Model):**
If you have a CUDA-compatible GPU, the requirements.txt will automatically install GPU-optimized versions on Linux. For other platforms:

- **macOS/Windows:** Install PyTorch first, then the other dependencies:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121  # For CUDA 12.1
  pip install accelerate bitsandbytes unsloth
  ```

**CPU-Only Mode:**
If you don't have a GPU or prefer CPU-only operation:
```bash
# Install CPU versions (skip GPU packages)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers peft accelerate
```

#### Optional Biomedical Tools
For advanced biomedical analysis features:
```bash
pip install biopython rdkit SimpleITK pydicom scipy pandas matplotlib plotly
```

### Configuration

Create a `.env` file in the project root:

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

## Mock Response System

When the corresponding API key for the selected provider is not set, the system automatically provides mock responses for:

- **ECG/EKG Analysis**: Signal processing, QRS detection, rhythm analysis
- **Bioimpedance**: Measurement techniques, safety considerations
- **FDA Regulatory**: 510(k) submission process, requirements
- **MRI Safety**: Magnetic field considerations, device testing
- **General Topics**: Fallback responses explaining mock mode

Mock responses include realistic biomedical engineering content with proper formatting, references, and streaming behavior identical to the real API.

## API Modes

**Production Mode** (API key configured):
- Uses the selected API provider for dynamic responses
- Falls back to mocks if API fails

**Demo/Mock Mode** (no API key):
- Uses predefined responses for common topics
- Perfect for demonstrations and development
- No API costs or rate limits

## Notes
- System prompt emphasizes concise, actionable outputs with regulatory and validation hooks (IEC 60601, ISO 14971, FDA QSR) and avoids overexplaining fundamentals.
- Streaming responses for low-latency UI.
- Shift+Enter inserts newline. 
- Mock responses maintain the same format and quality as AI responses.

## Coming soon:
- Progress UI for download size and throughput
- Optional CPU-only distilled model path for lower-end hardware
