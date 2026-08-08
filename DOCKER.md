# Docker Installation Guide for Biomed Chat

This guide shows you how to run Biomed Chat using Docker, which works on **Windows, Mac, and Linux** without needing to install Node.js or Python manually.

## Prerequisites

- **Docker Desktop** installed ([Download here](https://www.docker.com/products/docker-desktop))
- **Git** for cloning the repository

## Quick Start (3 Steps)

### 1. Clone the Repository

**On Windows (PowerShell):**
```powershell
git clone https://github.com/YOUR_USERNAME/biomed-chat.git
cd biomed-chat
```

**On Mac/Linux (Terminal):**
```bash
git clone https://github.com/YOUR_USERNAME/biomed-chat.git
cd biomed-chat
```

### 2. Configure API Keys (Optional)

Create a `.env` file or edit the existing one:

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
notepad .env
```

**Mac/Linux:**
```bash
cp .env.example .env
nano .env
```

Add your API key:
```env
API_PROVIDER="grok"
GROK_API_KEY="your_actual_api_key_here"
```

**Note:** If you skip this step, the app runs in **demo mode** with mock responses.

### 3. Start the Application

Run this single command:

```bash
docker-compose up -d
```

That's it! Open your browser to: **http://localhost:3000**

## All Docker Commands

### Start the App
```bash
docker-compose up -d
```

### Stop the App
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Restart the App
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Stop and Remove Everything (Including Downloaded Models)
```bash
docker-compose down -v
```

## Alternative: Using Docker Without Docker Compose

If you prefer not to use docker-compose:

### Build the Image
```bash
docker build -t biomed-chat .
```

### Run the Container
```bash
docker run -d \
  --name biomed-chat \
  -p 3000:3000 \
  -p 8000:8000 \
  -e API_PROVIDER=grok \
  -e GROK_API_KEY=your_key_here \
  -v $(pwd)/.env:/app/.env:ro \
  biomed-chat
```

**On Windows PowerShell, replace `$(pwd)` with `${PWD}`**

## Troubleshooting

### Port Already in Use
If you see "port 3000 already allocated":

**Change the port mapping in docker-compose.yml:**
```yaml
ports:
  - "3001:3000"  # Use port 3001 instead
```

Then access at: http://localhost:3001

### Docker Not Starting
- Make sure Docker Desktop is running
- Check you have enough disk space (at least 5GB free)
- Try: `docker system prune -a` to clean up old images

### Can't Access the App
- Verify container is running: `docker ps`
- Check logs: `docker-compose logs`
- Try accessing: http://127.0.0.1:3000 instead of localhost

### API Keys Not Working
- Ensure `.env` file is in the same directory as docker-compose.yml
- Check that your API key is valid
- Restart the container after changing .env: `docker-compose restart`

## Using Local Models with Docker

The local Qwen model requires significant disk space (~22GB). To use it:

1. Increase Docker's disk space allocation in Docker Desktop settings
2. Download the model using the web UI after starting the container
3. Models are persisted in the `biomed-chat-models` Docker volume

## Windows-Specific Notes

### PowerShell Syntax
PowerShell doesn't support `&&` for chaining commands. Use `;` instead:
```powershell
git clone https://github.com/YOUR_USERNAME/biomed-chat.git ; cd biomed-chat ; docker-compose up -d
```

### Path Issues
If you see path-related errors, use `${PWD}` instead of `$(pwd)`:
```powershell
docker run -v ${PWD}/.env:/app/.env:ro biomed-chat
```

## Advantages of Docker

✅ **Works on all platforms** - Windows, Mac, Linux  
✅ **No manual dependency installation** - Node.js and Python included  
✅ **Consistent environment** - Same setup for everyone  
✅ **Easy cleanup** - Remove everything with one command  
✅ **Isolated** - Doesn't interfere with your system  

## Need Help?

- Check container status: `docker ps -a`
- View detailed logs: `docker-compose logs --tail=100`
- Restart fresh: `docker-compose down && docker-compose up -d --build`

For more information, see the main [README.md](README.md) or [INSTALL.md](INSTALL.md).
