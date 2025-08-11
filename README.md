# Biomed Chat

Practitioner-focused chatbot UI for biomedical engineers. Proxies to Grok‑4 via xAI API with a tailored system prompt that assumes baseline field expertise.

## Features

- **Smart API Fallback**: Automatically uses mock responses when API key is not available
- **Biomedical Focus**: Specialized responses for biomedical engineering topics
- **Streaming Responses**: Real-time response streaming for better UX
- **Mock Mode**: Realistic demonstration responses when API is unavailable

## Setup

1. Node.js 18+ required
2. Install dependencies:

```sh
npm install
```

3. Configure `.env` file:

```env
# For full AI functionality:
XAI_API_KEY=your_xai_api_key_here

# For mock/demo mode, comment out the API key:
# XAI_API_KEY=your_xai_api_key_here

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

When `XAI_API_KEY` is not set, the system automatically provides mock responses for:

- **ECG/EKG Analysis**: Signal processing, QRS detection, rhythm analysis
- **Bioimpedance**: Measurement techniques, safety considerations
- **FDA Regulatory**: 510(k) submission process, requirements
- **MRI Safety**: Magnetic field considerations, device testing
- **General Topics**: Fallback responses explaining mock mode

Mock responses include realistic biomedical engineering content with proper formatting, references, and streaming behavior identical to the real API.

## API Modes

**Production Mode** (API key configured):
- Uses X.AI Grok-4 API for dynamic responses
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
