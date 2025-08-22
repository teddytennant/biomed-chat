# Biomed Chat

🎨 **Modern, Professional UI/UX** | 🤖 **AI-Powered Biomedical Assistant** | 🔬 **Engineer-Focused Design**

A cutting-edge chatbot interface designed specifically for biomedical engineers. Features a stunning modern design with glass morphism effects, smooth animations, and an intuitive user experience. Proxies to Grok‑4 via xAI API with RAG and a tailored system prompt that assumes baseline field expertise.

**Note on API Providers:** This project is built around the Grok API, which has demonstrated high performance on benchmarks. While other providers are supported, Grok is recommended for the best experience.

## ✨ Modern UI/UX Features

### 🎨 **Visual Design**
- **Dynamic Animated Background**: Beautiful gradient background with floating orbs and smooth color transitions
- **Glass Morphism Effects**: Modern glass-like components with backdrop blur and transparency
- **Gradient Text Effects**: Eye-catching gradient text for branding and headings
- **Advanced Animations**: Smooth 60fps animations and micro-interactions throughout

### 🚀 **User Experience**
- **Intuitive Navigation**: Enhanced navbar with hover effects and active state indicators
- **Modern Chat Interface**: Glass morphism message bubbles with smooth slide-in animations
- **Enhanced Settings Page**: Professional settings interface with animated cards and modern controls
- **Responsive Design**: Optimized for all screen sizes with mobile-first approach
- **Accessibility**: High contrast support, reduced motion preferences, and keyboard navigation

### 💫 **Interactive Elements**
- **Hover Animations**: Subtle lift effects and color transitions on interactive elements
- **Loading States**: Beautiful loading indicators and typing animations
- **Visual Feedback**: Immediate response to user actions with smooth transitions
- **Modern Form Controls**: Custom-styled inputs, switches, and buttons with glass effects

## Features

- **Multi-API Support**: Supports Grok, Gemini, OpenAI, and Anthropic APIs.
- **Smart API Fallback**: Automatically uses mock responses when API key is not available
- **Biomedical Focus**: Specialized responses for biomedical engineering topics
- **Streaming Responses**: Real-time response streaming for better UX
- **Mock Mode**: Realistic demonstration responses when API is unavailable

## Setup

1. Node.js 18+ required
2. Install dependencies:

```sh
npm install
pip install -r requirements.txt
```

3. Configure `.env` file:

```env
# Set the API provider
API_PROVIDER="grok"  # "grok", "gemini", "openai", or "anthropic"

# For full AI functionality (only one is required based on the provider):
GROK_API_KEY="your_grok_api_key_here"
GEMINI_API_KEY="your_gemini_api_key_here"
OPENAI_API_KEY="your_openai_api_key_here"
ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# For mock/demo mode, comment out the API key:
# GROK_API_KEY="your_grok_api_key_here"

# Optional overrides:
# XAI_MODEL=grok-4
# PORT=3000
# SITE_PASSWORD=your_password_here
```

## Run

```sh
npm run dev
```

Open `http://localhost:3000`.

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

## 🚀 **Rust Performance Enhancements**

High-performance Rust implementations for biomedical signal processing and analysis:

### **Biomedical Signal Processing Library**
- **Real-time Signal Processing**: Moving average filtering, peak detection, and statistical analysis
- **ECG Analysis**: Heart rate calculation and rhythm analysis with high accuracy
- **Command Line Tools**: CLI interface for signal generation, processing, and analysis
- **Performance**: 10-100x faster than equivalent Python implementations

### **Key Features**
- **Memory Safety**: Rust's ownership system prevents memory-related bugs
- **Zero-Cost Abstractions**: High-level APIs with low-level performance
- **Concurrency**: Safe concurrent processing for real-time applications
- **Integration Ready**: Can be compiled to WebAssembly or used as Node.js addons

### **Usage**
```bash
cd rust
cargo build
./target/debug/biomed-chat-rust analyze 0.1 0.8 1.0 0.3  # ECG analysis
./target/debug/biomed-chat-rust generate 1.0 2.0 1000   # Signal generation
```

See [`rust/README.md`](rust/README.md) for detailed documentation.

## Coming soon:
- Fine tuned model for verifying outputs from Grok 4
- WebAssembly integration for browser-based signal processing
- Advanced ML models for biomedical pattern recognition
