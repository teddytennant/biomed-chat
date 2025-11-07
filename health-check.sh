#!/bin/bash
# Health Check Script for Biomed Chat
# Diagnoses common issues and provides solutions

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Biomed Chat - Health Check        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

ISSUES=0

# Check Node.js
echo -e "${YELLOW}Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✓${NC} Node.js installed: $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found"
    echo "   Install from: https://nodejs.org/"
    ISSUES=$((ISSUES+1))
fi

# Check Python
echo -e "${YELLOW}Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python installed: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python not found"
    echo "   Install from: https://www.python.org/"
    ISSUES=$((ISSUES+1))
fi

# Check pip
echo -e "${YELLOW}Checking pip...${NC}"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} pip installed: $PIP_VERSION"
else
    echo -e "${RED}✗${NC} pip not found"
    ISSUES=$((ISSUES+1))
fi

# Check node_modules
echo -e "${YELLOW}Checking Node.js dependencies...${NC}"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓${NC} node_modules exists"
else
    echo -e "${RED}✗${NC} node_modules not found"
    echo "   Run: npm install"
    ISSUES=$((ISSUES+1))
fi

# Check Python dependencies
echo -e "${YELLOW}Checking Python dependencies...${NC}"
MISSING_DEPS=()

# Check critical dependencies
python3 -c "import uvicorn" 2>/dev/null || MISSING_DEPS+=("uvicorn")
python3 -c "import fastapi" 2>/dev/null || MISSING_DEPS+=("fastapi")
python3 -c "import anthropic" 2>/dev/null || MISSING_DEPS+=("anthropic")
python3 -c "import openai" 2>/dev/null || MISSING_DEPS+=("openai")
python3 -c "import google.generativeai" 2>/dev/null || MISSING_DEPS+=("google-generativeai")
python3 -c "import torch" 2>/dev/null || MISSING_DEPS+=("torch")
python3 -c "import transformers" 2>/dev/null || MISSING_DEPS+=("transformers")

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All critical Python packages installed"
else
    echo -e "${RED}✗${NC} Missing Python packages: ${MISSING_DEPS[*]}"
    echo "   Run: pip3 install --break-system-packages -r requirements.txt"
    ISSUES=$((ISSUES+1))
fi

# Check .env file
echo -e "${YELLOW}Checking configuration...${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check for API keys
    if grep -qE "^(GROK|GEMINI|OPENAI|ANTHROPIC)_API_KEY=\".+\"" .env; then
        echo -e "${GREEN}✓${NC} API key configured"
    else
        echo -e "${YELLOW}⚠${NC}  No API keys found (will run in demo mode)"
        echo "   Edit .env to add API keys for full functionality"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
    echo "   Run: ./setup.sh"
    ISSUES=$((ISSUES+1))
fi

# Check disk space
echo -e "${YELLOW}Checking disk space...${NC}"
AVAILABLE=$(df -h ~ | tail -1 | awk '{print $4}')
echo -e "${GREEN}✓${NC} Available disk space: $AVAILABLE"
echo "   (Need ~22 GB for local model download)"

# Check ports
echo -e "${YELLOW}Checking ports...${NC}"
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠${NC}  Port 3000 is in use"
    echo "   Stop existing service or change PORT in .env"
else
    echo -e "${GREEN}✓${NC} Port 3000 available"
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠${NC}  Port 8000 is in use"
    echo "   Stop existing service or reconfigure"
else
    echo -e "${GREEN}✓${NC} Port 8000 available"
fi

# GPU check
echo -e "${YELLOW}Checking GPU...${NC}"
if python3 -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
    GPU_NAME=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
    echo -e "${GREEN}✓${NC} GPU detected: $GPU_NAME"
    echo "   Local model will use GPU acceleration"
else
    echo -e "${YELLOW}⚠${NC}  No GPU detected"
    echo "   Local model will run on CPU (slower but functional)"
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! System ready.${NC}"
    echo ""
    echo "To start the app:"
    echo "  npm run dev"
else
    echo -e "${RED}✗ Found $ISSUES issue(s) - see above for fixes${NC}"
    echo ""
    echo "Quick fix:"
    echo "  ./setup.sh"
fi
echo -e "${BLUE}═══════════════════════════════════════${NC}"
