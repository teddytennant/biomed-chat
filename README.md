# Biomed Chat

Practitioner-focused chatbot UI for biomedical engineers. Proxies to Grok‑4 via xAI API with a tailored system prompt that assumes baseline field expertise.

## Setup

1. Node.js 18+ required
2. Install dependencies:

```sh
npm install
```

3. Create an `.env` in project root:

```
XAI_API_KEY=your_xai_api_key_here
# Optional overrides
# XAI_MODEL=grok-4
# PORT=3000
```

## Run

```sh
npm run dev
```

Open `http://localhost:3000`.

## Notes
- System prompt emphasizes concise, actionable outputs with regulatory and validation hooks (IEC 60601, ISO 14971, FDA QSR) and avoids overexplaining fundamentals.
- Streaming responses for low-latency UI.
- Shift+Enter inserts newline. 