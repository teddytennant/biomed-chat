#!/bin/bash
# Biomed Chat Setup Script
# This script streamlines the installation process for the biomed-chat application

set -e  # Exit on any error

echo "🚀 Biomed Chat Setup"
echo "===================="

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please upgrade to Node.js 18+."
    exit 1
fi
echo "✅ Node.js $(node -v) found"

# Check Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    echo "❌ Python version $PYTHON_VERSION is too old. Please upgrade to Python 3.10+."
    exit 1
fi
echo "✅ Python $PYTHON_VERSION found"

# Check pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

PIP_CMD="pip"
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
fi
echo "✅ pip found"

echo ""

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install
echo "✅ Node.js dependencies installed"

echo ""

# Install Python dependencies
echo "🐍 Installing Python dependencies..."

# Check if system has externally-managed Python
if $PIP_CMD install -r requirements.txt 2>&1 | grep -q "externally-managed-environment"; then
    echo "⚠️  Detected externally-managed Python environment"
    echo "   Installing with --break-system-packages flag..."
    $PIP_CMD install --break-system-packages -r requirements.txt
else
    $PIP_CMD install -r requirements.txt
fi

echo "✅ Python dependencies installed"

echo ""

# Check GPU availability
echo "🔍 Checking GPU availability..."
$PYTHON_CMD -c "
import sys
try:
    import torch
    if torch.cuda.is_available():
        print('✅ CUDA GPU detected - Local model will run on GPU')
        print(f'   GPU: {torch.cuda.get_device_name(0)}')
    else:
        print('⚠️  No CUDA GPU detected - Local model will run on CPU (slower)')
except ImportError:
    print('⚠️  PyTorch not available - Local model features disabled')
"

echo ""

# Create .env template if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# AI Provider Configuration
API_PROVIDER="grok"

# API Keys (uncomment and add your keys)
# GROK_API_KEY="your_grok_api_key_here"
# GEMINI_API_KEY="your_gemini_api_key_here"
# OPENAI_API_KEY="your_openai_api_key_here"
# ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Optional Settings
# PORT=3000
# SITE_PASSWORD="your_password_here"
EOF
    echo "✅ .env template created"
    echo "   ⚠️  Please edit .env and add your API keys for full functionality"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "For demo mode (no API keys needed):"
echo "  Comment out API keys in .env"
echo ""
echo "For local model support:"
echo "  Go to Settings → Local Qwen Model → Download"