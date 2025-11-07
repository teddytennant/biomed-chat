# Biomed Chat - Installation Guide (Simplified)

This is the **ultra-simple** installation guide. Everything you need to know on one page.

---

## The Absolute Easiest Way

### Copy and paste this ONE command:

```bash
git clone https://github.com/YOUR_USERNAME/biomed-chat.git && cd biomed-chat && chmod +x quick-start.sh && ./quick-start.sh
```

**That's it!** The app will:
1. Install everything automatically
2. Handle any Python environment issues
3. Create configuration files
4. Start the server

Open **http://localhost:3000** when it says "ready"

---

## If Something Goes Wrong

### Run the health check:

```bash
./health-check.sh
```

It will tell you exactly what's wrong and how to fix it.

---

## Common Questions

### Q: Do I need an API key?
**A:** No! The app works in demo mode without any API keys.

To use real AI:
1. Get a free API key from [Grok](https://x.ai/) or [Gemini](https://ai.google.dev/)
2. Edit `.env` and add your key
3. Restart the app

### Q: How do I install the local model?
**A:** After the app is running:
1. Click **Settings** (⚙️ icon)
2. Click **Download** in "Local Qwen Model" section
3. Wait (10-60 minutes depending on your internet)
4. Select "Local Medical (Qwen 2.5 7B)" from the model dropdown

OR from command line:
```bash
./install_qwen.sh
```

### Q: Does it need a GPU?
**A:** 
- **For cloud APIs:** No GPU needed
- **For local model:** GPU recommended but works on CPU (slower)

### Q: How much disk space do I need?
**A:** 
- **Without local model:** ~500 MB
- **With local model:** ~22 GB

---

## Requirements

You need these installed first:
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Python 3.10+** - [Download here](https://www.python.org/)

The quick-start script checks these automatically.

---

## Troubleshooting

### "Command not found"
Make the script executable:
```bash
chmod +x quick-start.sh
./quick-start.sh
```

### "Port already in use"
Something is using port 3000. Either:
- Stop the other service
- Or change port in `.env`: `PORT=3001`

### "Python externally-managed"
Don't worry! The setup script handles this automatically.

### Still broken?
1. Run the health check: `./health-check.sh`
2. Follow its suggestions
3. If still stuck, see [QUICKREF.md](QUICKREF.md) for detailed troubleshooting

---

## Manual Installation (If Preferred)

If you want more control:

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/biomed-chat.git
cd biomed-chat

# 2. Install dependencies
./setup.sh

# 3. (Optional) Edit configuration
nano .env

# 4. Start
npm run dev
```

---

## What Gets Installed

### Node.js packages:
- express (web server)
- dotenv (config)
- cors (API access)
- @xenova/transformers (local ML)

### Python packages:
- fastapi (API framework)
- uvicorn (Python server)
- torch (machine learning)
- transformers (AI models)
- anthropic, openai, google-generativeai (AI APIs)
- sentence-transformers, faiss-cpu (RAG)

All installed automatically by the scripts.

---

## Next Steps After Installation

1. **Try it out** - Open http://localhost:3000
2. **Ask a question** - Type any biomedical engineering question
3. **Change model** - Try different AI models from the dropdown
4. **Explore settings** - Click ⚙️ to configure
5. **Add API key** - For unlimited real AI responses (optional)
6. **Download local model** - For private/offline inference (optional)

---

## Pro Tips

✅ **Start simple** - Use demo mode first to learn the interface
✅ **Add API key later** - Only when you need real AI responses
✅ **GPU optional** - Cloud APIs work great without GPU
✅ **Local model optional** - Only needed for privacy/offline use
✅ **Run health check** - If anything seems broken

---

## Getting Help

**Quick diagnosis:**
```bash
./health-check.sh
```

**All commands:**
[QUICKREF.md](QUICKREF.md)

**Full documentation:**
[README.md](README.md)

**Report issues:**
GitHub Issues (include output from health check)

---

## That's All!

Seriously, that's everything you need. The setup is designed to "just work" with sensible defaults.

**Remember:** Run `./quick-start.sh` and you're done in 3-5 minutes! ✨
