/* Vercel Serverless Function: /api/chat */

import { createHmac } from 'crypto';
import { getMockResponse, createMockSSEStream } from '../mock-responses.js';

const AUTH_COOKIE_NAME = 'bc_auth';
const AUTH_COOKIE_SEED = 'biomed-chat';

function computeAuthCookieValue(password) {
  return createHmac('sha256', password).update(AUTH_COOKIE_SEED).digest('hex');
}

function parseCookies(req) {
  const header = req.headers['cookie'] || '';
  const pairs = header.split(';').map(s => s.trim()).filter(Boolean);
  const out = {};
  for (const p of pairs) {
    const idx = p.indexOf('=');
    if (idx > 0) out[p.slice(0, idx)] = decodeURIComponent(p.slice(idx + 1));
  }
  return out;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.statusCode = 405;
    res.setHeader('Allow', 'POST');
    return res.end('Method Not Allowed');
  }

  const SITE_PASSWORD = process.env.SITE_PASSWORD || process.env.BASIC_AUTH_PASS || '';
  if (SITE_PASSWORD) {
    const cookies = parseCookies(req);
    const expected = computeAuthCookieValue(SITE_PASSWORD);
    if (cookies[AUTH_COOKIE_NAME] !== expected) {
      res.statusCode = 401;
      return res.end('Unauthorized');
    }
  }

  let body = '';
  for await (const chunk of req) body += chunk;
  let messages;
  let model = '';
  try {
    const parsed = JSON.parse(body || '{}');
    messages = parsed.messages;
    model = (parsed.model || '').toString().trim();
    if (!Array.isArray(messages)) throw new Error('messages must be an array');
  } catch (e) {
    res.statusCode = 400;
    return res.end('Bad Request');
  }

  const XAI_API_KEY = process.env.XAI_API_KEY || '';

  const systemPrompt = `Role: Senior biomedical engineering copilot for practitioners.

Operating principles:
- Assume baseline practitioner knowledge: you can use standard terms (e.g., Poisson’s ratio, Nyquist sampling, impedance, HbA1c, ISO 13485) without lengthy definitions.
- Be concise and clinically/technically actionable. Favor bullet points, numbered steps, and brief justifications.
- Use equations and units when material, otherwise avoid math bloat.
- Note safety, regulatory, and validation considerations succinctly (e.g., IEC 60601, FDA 21 CFR 820, ISO 14971) when relevant.
- When uncertain, state assumptions and propose quick validation steps.
- Prefer pragmatic designs, references, and checks over theory recaps.
- If a result depends on parameters, provide defaults and ranges appropriate to typical biomedical contexts.
- Find and reference the work of industry experts and their papers to support your answers.

Response style:
- Start with a one‑sentence answer, then compact details.
- Use structured sections: Summary, Steps, Key Params, Risks/Checks, References (short, and include links).
- Keep code and math minimal, but correct and runnable when requested.
- Avoid overexplaining basics; this is for field practitioners.`

  const fullMessages = [{ role: 'system', content: systemPrompt }, ...messages];

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  // If no API key, use mock responses
  if (!XAI_API_KEY) {
    try {
      const userMessage = messages[messages.length - 1]?.content || '';
      const mockContent = getMockResponse(userMessage);
      const mockStream = createMockSSEStream(mockContent);
      
      for await (const chunk of mockStream.generate()) {
        res.write(chunk);
      }
      
      return res.end();
    } catch (err) {
      res.write(`event: error\n`);
      res.write(`data: ${JSON.stringify({ error: 'Mock response error' })}\n\n`);
      return res.end();
    }
  }

  // Use real API if key is available
  try {
    const upstream = await fetch('https://api.x.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${XAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: model || 'grok-4',
        messages: fullMessages,
        stream: true,
        temperature: 0.2,
        max_tokens: 1200,
      }),
    });

    if (!upstream.ok || !upstream.body) {
      // Fallback to mock response if API fails
      const userMessage = messages[messages.length - 1]?.content || '';
      const mockContent = getMockResponse(userMessage);
      const mockStream = createMockSSEStream(mockContent);
      
      for await (const chunk of mockStream.generate()) {
        res.write(chunk);
      }
      
      return res.end();
    }

    const reader = upstream.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      res.write(chunk);
    }

    res.end();
  } catch (err) {
    // Fallback to mock response on any error
    try {
      const userMessage = messages[messages.length - 1]?.content || '';
      const mockContent = getMockResponse(userMessage);
      const mockStream = createMockSSEStream(mockContent);
      
      for await (const chunk of mockStream.generate()) {
        res.write(chunk);
      }
      
      return res.end();
    } catch (fallbackErr) {
      res.write(`event: error\n`);
      res.write(`data: ${JSON.stringify({ error: err?.message || 'Unknown error' })}\n\n`);
      res.end();
    }
  }
} 