# Fine tuned model is here! Available at https://huggingface.co/ttennant/qwen2.5-7b-medical-lora. Integration into UI coming soon.
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

## Coming soon:
- Fine tuned model for verifying outputs from Grok 4
