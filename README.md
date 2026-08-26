# Biomed Chat

A chat interface for biomedical engineering work: standards (IEC 60601, ISO 14971),
510(k) submissions, MRI safety, signal processing, and similar topics. It talks to
Grok, Gemini, OpenAI, or Anthropic, and can also run a local
[Qwen 2.5 7B medical LoRA](https://huggingface.co/ttennant/qwen2.5-7b-medical-lora)
for offline use.

## Read this before using it

This is experimental research code. It is not a medical device, it is not cleared
by the FDA, CE, TGA, or any other regulator, and it has no safety review of any
kind. Do not use it for diagnosis, treatment, dosing, or any other patient care
decision. It is a language model with a biomedical-engineering system prompt, and
it will state wrong things confidently.

If you are looking for medical help, close this and call a doctor. In an
emergency call 911 (US), 112 (EU), or your local emergency number. US suicide and
crisis line: 988. UK: 116 123. Australia: 13 11 14.

## Run it with Docker

You need [Docker Desktop](https://www.docker.com/products/docker-desktop)
installed and running.

```bash
git clone https://github.com/teddytennant/biomed-chat.git
cd biomed-chat
docker-compose up -d
```

Open http://localhost:3000. Stop it with `docker-compose down`.

It works with no API key at all, using canned responses. To use a real model, add
a key in Settings or in `.env`. See [DOCKER.md](DOCKER.md) for volumes, GPU
passthrough, and the rest.

## Run it without Docker

You need Node.js 18+ and Python 3.10+.

```bash
git clone https://github.com/teddytennant/biomed-chat.git
cd biomed-chat
./quick-start.sh
```

`quick-start.sh` installs Node and Python dependencies, writes a `.env` if there
isn't one, and starts the server on http://localhost:3000.

To do it by hand instead:

```bash
./setup.sh          # dependencies and .env
nano .env           # add an API key, optional
npm run dev
```

`npm run dev` starts the Node server, which also spawns the Python FastAPI
backend. Set `DISABLE_PYTHON_AUTOSTART=1` if you want to run that yourself.

## Configuration

Everything lives in `.env`:

```env
API_PROVIDER="grok"          # grok, gemini, openai, or anthropic

GROK_API_KEY="..."           # only the one matching API_PROVIDER is needed
GEMINI_API_KEY="..."
OPENAI_API_KEY="..."
ANTHROPIC_API_KEY="..."

PORT=3000
SITE_PASSWORD="..."          # optional; unset means the site is open
```

Leave the keys out and the app serves mock responses instead. Grok is the default
because it is what the system prompt was tuned against; the others work.

`.env.example` lists the rest, including the PubMed and Python service settings.

## Local model (optional)

The local Qwen 2.5 7B medical LoRA runs on your machine, so nothing leaves it.
It is a large download and it is slow without a GPU.

From the UI: Settings, then Local Qwen Model, then Download. Expect 10 to 60
minutes. When it finishes, pick "Local Medical (Qwen 2.5 7B)" in the model
dropdown.

From the command line:

```bash
./install_qwen.sh              # interactive, detects GPU or CPU
npm run install-model          # same thing, non-interactive
npm run install-model-cpu      # force CPU
npm run check-model            # is it installed?
```

With an NVIDIA GPU you need 8 GB of VRAM and CUDA, and the download is about
8 GB. On CPU it is about 22 GB on disk, wants 32 GB of RAM, and inference is
roughly one to two orders of magnitude slower.

[README_LOCAL_MODEL.md](README_LOCAL_MODEL.md) has the details;
[QUICKSTART_LOCAL_MODEL.md](QUICKSTART_LOCAL_MODEL.md) is the short version.

## Mock responses

With no API key configured, the app answers from `mock-responses.js` instead of
calling a provider. It covers ECG signal processing, bioimpedance, 510(k)
submissions, and MRI safety, plus a generic fallback, and it streams them the same
way a real response streams. It is there for development and demos, not for
answering real questions.

The same mocks are used as a fallback when a configured provider errors out.

## Troubleshooting

Start with the health check. It looks at Node, Python, and pip versions,
installed dependencies, disk space, ports 3000 and 8000, and whether a GPU is
visible to PyTorch.

```bash
./health-check.sh
```

**Docker: "docker-compose: command not found".** Docker Desktop isn't running, or
the terminal was open before you installed it. Restart the terminal.

**Port 3000 already in use.** Either free it or move:

```bash
lsof -ti:3000 | xargs kill -9
echo "PORT=3001" >> .env
```

Under Docker, edit the port mapping in `docker-compose.yml` instead.

**"Module not found".**

```bash
npm install
pip install -r requirements.txt --force-reinstall
```

**pip refuses to install, "externally-managed-environment".** `setup.sh` handles
this. By hand: `pip3 install --break-system-packages -r requirements.txt`.

**Python service won't start.** Check it is up with `ps aux | grep uvicorn`, then
`python3 -c "import uvicorn, fastapi"` to see whether the dependencies are
actually there.

**GPU not detected.** Check `nvidia-smi` works, then
`python -c "import torch; print(torch.cuda.is_available())"`. If Unsloth fails to
import, the code falls back to transformers plus PEFT on CPU; that is slower but
it works.

**Model download fails.** Check free space with `df -h ~` (you need about 22 GB),
then `npm run check-model`, then rerun `./install_qwen.sh`.

Still stuck: read the terminal output from `npm run dev`, try a clean install with
`rm -rf node_modules __pycache__ && ./setup.sh`, and open an issue with the error
and the health check output.

## Notes

- The system prompt pushes for short, actionable answers with regulatory hooks
  (IEC 60601, ISO 14971, FDA QSR).
- Shift+Enter inserts a newline in the chat box.
- Responses stream token by token from every backend, including the mocks.

## Still to do

- Progress UI showing download size and throughput
- A smaller distilled model for machines without a GPU
- More fine-tuning on specific biomedical subfields

## More docs

- [INSTALL.md](INSTALL.md), installation on one page
- [QUICKREF.md](QUICKREF.md), every command in one place
- [DOCKER.md](DOCKER.md), Docker in detail
- [README_LOCAL_MODEL.md](README_LOCAL_MODEL.md) and
  [QUICKSTART_LOCAL_MODEL.md](QUICKSTART_LOCAL_MODEL.md), the local model
- [README_RAG.md](README_RAG.md), the retrieval pipeline

## License

See [LICENSE](LICENSE).
