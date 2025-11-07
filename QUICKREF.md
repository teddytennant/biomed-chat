# Quick Reference - Biomed Chat

## Installation (One Command)

```bash
git clone <repository-url> && cd biomed-chat && chmod +x quick-start.sh && ./quick-start.sh
```

**That's it!** The app will open at `http://localhost:3000`

---

## Useful Commands

| Command | What it does |
|---------|-------------|
| `./quick-start.sh` | Install everything and start the app |
| `./setup.sh` | Install dependencies only (doesn't start) |
| `./health-check.sh` | Diagnose any issues |
| `npm run dev` | Start the app |
| `npm run health` | Same as `./health-check.sh` |

---

## Local Model Commands

| Command | What it does |
|---------|-------------|
| `./install_qwen.sh` | Download local Qwen model (interactive) |
| `npm run check-model` | Check if model is installed |
| `npm run install-model` | Download model (auto GPU/CPU) |
| `npm run install-model-cpu` | Force CPU-only model |

**Note:** You can also download the model from the web UI (Settings → Local Qwen Model → Download)

---

## Configuration

Edit `.env` file to configure:

```bash
nano .env
```

**Minimal config (demo mode - no API key needed):**
```env
API_PROVIDER="grok"
# Leave API keys commented out for demo mode
```

**Production config (requires API key):**
```env
API_PROVIDER="grok"
GROK_API_KEY="your_api_key_here"
```

**Optional settings:**
```env
PORT=3000
SITE_PASSWORD="your_password"
```

---

## API Providers

| Provider | Recommended | Notes |
|----------|-------------|-------|
| **Grok** | ✅ Yes | Best performance, trained on X.com data |
| Gemini | ⚠️ Good | Free tier available |
| OpenAI | ⚠️ Good | GPT-4 models |
| Anthropic | ⚠️ Good | Claude models |
| **Local (Qwen)** | ✅ Privacy | Offline, requires download |

---

## Common Issues & Solutions

### "Status unavailable" in web UI
```bash
# Check if Python service is running
ps aux | grep uvicorn

# Restart the app
npm run dev
```

### Missing Python dependencies
```bash
# Auto-handled by setup.sh, but if needed:
pip3 install --break-system-packages -r requirements.txt
```

### Port already in use
```bash
# Change port in .env
echo "PORT=3001" >> .env
```

### Model download stuck
```bash
# Check disk space (need 22 GB)
df -h ~

# Check model status
npm run check-model
```

### Something's broken - start fresh
```bash
rm -rf node_modules __pycache__
./setup.sh
```

---

## System Requirements

### Minimal (Cloud API only)
- Node.js 18+
- Python 3.10+
- 2 GB RAM
- 500 MB disk space

### Recommended (with local model - GPU)
- Node.js 18+
- Python 3.10+
- NVIDIA GPU with 6+ GB VRAM
- 16 GB RAM
- 30 GB disk space

### Alternative (with local model - CPU)
- Node.js 18+
- Python 3.10+
- 32 GB RAM (recommended)
- 30 GB disk space

---

## Getting Help

1. **Run health check:** `./health-check.sh`
2. **Check logs:** Look at terminal output from `npm run dev`
3. **Read docs:** See README.md and other documentation files
4. **Report issue:** Open GitHub issue with error messages

---

## Quick Tips

✅ **Use demo mode** to try without API keys
✅ **Run health check** if something doesn't work
✅ **GPU highly recommended** for local model
✅ **Grok API recommended** for best results
✅ **22 GB free disk space** needed for local model

---

*For detailed documentation, see [README.md](README.md) and [README_LOCAL_MODEL.md](README_LOCAL_MODEL.md)*
