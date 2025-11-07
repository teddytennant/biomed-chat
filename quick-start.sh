#!/bin/bash
# Quick Start Script for Biomed Chat
# One command to install and run everything

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Biomed Chat - Quick Start Setup   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# Step 1: Run setup.sh
echo -e "${YELLOW}[1/3]${NC} Installing dependencies..."
./setup.sh

echo ""

# Step 2: Check if .env has any API key configured
echo -e "${YELLOW}[2/3]${NC} Checking API configuration..."
HAS_KEY=false
if [ -f .env ]; then
    if grep -qE "^(GROK|GEMINI|OPENAI|ANTHROPIC)_API_KEY=\".+\"" .env; then
        HAS_KEY=true
        echo -e "${GREEN}✓${NC} API key found in .env"
    fi
fi

if [ "$HAS_KEY" = false ]; then
    echo -e "${YELLOW}⚠${NC}  No API keys configured - running in demo mode"
    echo ""
    echo "To use AI features, edit .env and add an API key:"
    echo "  nano .env"
    echo ""
    echo "Press any key to continue with demo mode..."
    read -n 1 -s
fi

echo ""

# Step 3: Start the app
echo -e "${YELLOW}[3/3]${NC} Starting Biomed Chat..."
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🚀 Biomed Chat is starting...               ║${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║  Open: ${BLUE}http://localhost:3000${GREEN}              ║${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║  Press Ctrl+C to stop the server             ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""

npm run dev
