#!/bin/bash
# Qwen 2.5 7B Medical LoRA Model Installation Wrapper
# This script provides a user-friendly interface to install the local model

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python is not installed. Please install Python 3.10+ first.${NC}"
    exit 1
fi

# Detect pip command
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo -e "${RED}❌ pip is not installed. Please install pip first.${NC}"
    exit 1
fi

# Function to print section headers
print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to print info messages
print_info() {
    echo -e "${GREEN}ℹ${NC}  $1"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗${NC}  $1"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓${NC}  $1"
}

# Parse command line arguments
FORCE_CPU=0
CHECK_ONLY=0
CHECK_DEPS=0
INSTALL_DEPS=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --force-cpu)
            FORCE_CPU=1
            shift
            ;;
        --check)
            CHECK_ONLY=1
            shift
            ;;
        --check-deps)
            CHECK_DEPS=1
            shift
            ;;
        --install-deps)
            INSTALL_DEPS=1
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force-cpu       Force CPU mode even if GPU is available"
            echo "  --check           Check if model is already installed"
            echo "  --check-deps      Check which dependencies are installed"
            echo "  --install-deps    Install required Python dependencies"
            echo "  -h, --help        Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main script
print_header "Qwen 2.5 7B Medical LoRA Model Installation"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_info "Using Python $PYTHON_VERSION"

# Check if install script exists
if [ ! -f "install_qwen_model.py" ]; then
    print_error "install_qwen_model.py not found in current directory"
    exit 1
fi

# Handle --install-deps flag
if [ $INSTALL_DEPS -eq 1 ]; then
    print_header "Installing Dependencies"
    
    print_info "Checking for GPU support..."
    
    HAS_GPU=0
    if $PYTHON_CMD -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
        HAS_GPU=1
        print_success "CUDA GPU detected"
    else
        print_warning "No CUDA GPU detected - will install CPU-only dependencies"
    fi
    
    if [ $HAS_GPU -eq 1 ]; then
        print_info "Installing GPU dependencies..."
        echo ""
        $PIP_CMD install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        $PIP_CMD install transformers peft accelerate bitsandbytes
        
        # Try to install unsloth (may not work on all systems)
        print_info "Attempting to install unsloth (may fail on some systems)..."
        if $PIP_CMD install unsloth 2>/dev/null; then
            print_success "Unsloth installed successfully"
        else
            print_warning "Could not install unsloth - will fall back to CPU mode"
        fi
    else
        print_info "Installing CPU dependencies..."
        echo ""
        $PIP_CMD install torch transformers peft
    fi
    
    print_success "Dependencies installed"
    echo ""
    exit 0
fi

# Handle --check-deps flag
if [ $CHECK_DEPS -eq 1 ]; then
    $PYTHON_CMD install_qwen_model.py --check-deps
    exit 0
fi

# Handle --check flag
if [ $CHECK_ONLY -eq 1 ]; then
    $PYTHON_CMD install_qwen_model.py --check
    exit 0
fi

# Check if dependencies are installed
print_info "Checking dependencies..."
DEP_CHECK=$($PYTHON_CMD -c "
import sys
try:
    import torch
    print('torch', end='')
except ImportError:
    sys.exit(1)
" 2>/dev/null)

if [ $? -ne 0 ]; then
    print_error "PyTorch is not installed"
    print_info "Install dependencies with: $0 --install-deps"
    print_info "Or manually: pip install torch transformers peft"
    exit 1
fi

print_success "Dependencies found"

# Check for GPU
print_info "Checking for GPU support..."
HAS_GPU=0
if $PYTHON_CMD -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
    HAS_GPU=1
    GPU_NAME=$($PYTHON_CMD -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
    print_success "CUDA GPU detected: $GPU_NAME"
else
    print_warning "No CUDA GPU detected"
fi

# Determine installation mode
if [ $FORCE_CPU -eq 1 ]; then
    print_warning "Forcing CPU mode (--force-cpu flag)"
    MODE="CPU"
elif [ $HAS_GPU -eq 1 ]; then
    MODE="GPU"
else
    MODE="CPU"
fi

print_header "Installation Mode: $MODE"

if [ "$MODE" = "GPU" ]; then
    print_info "Will download: ~8 GB (LoRA adapters only)"
    print_info "Inference: Fast (GPU accelerated)"
else
    print_warning "Will download: ~22 GB (full model + adapters)"
    print_warning "Inference: Slow (CPU only)"
fi

echo ""
echo -e "${YELLOW}This will download model files from HuggingFace.${NC}"
echo -e "${YELLOW}Depending on your internet speed, this may take 10-60 minutes.${NC}"
echo ""

# Prompt for confirmation
read -p "Continue with installation? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installation cancelled"
    exit 0
fi

# Run the installation
print_header "Starting Installation"

if [ $FORCE_CPU -eq 1 ]; then
    $PYTHON_CMD install_qwen_model.py --force-cpu
else
    $PYTHON_CMD install_qwen_model.py
fi

# Check exit code
if [ $? -eq 0 ]; then
    print_header "Installation Complete"
    print_success "Model is ready to use!"
    print_info "You can now use the local model in the Biomed Chat application"
    print_info "Select 'Local Medical (Qwen 2.5 7B)' from the model dropdown"
else
    print_header "Installation Failed"
    print_error "There was an error during installation"
    print_info "Check the error messages above for details"
    exit 1
fi
