import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { createHmac } from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env explicitly from CWD first, then fallback to server directory
dotenv.config({ path: path.join(process.cwd(), '.env') });
if (!process.env.XAI_API_KEY) {
  dotenv.config({ path: path.join(__dirname, '.env') });
}

const app = express();
app.use(cors());
app.use(express.json({ limit: '2mb' }));
app.use(express.urlencoded({ extended: false }));

// Enable password-only protection site-wide if a password is provided
const SITE_PASSWORD = process.env.SITE_PASSWORD || process.env.BASIC_AUTH_PASS || '';
const AUTH_COOKIE_NAME = 'bc_auth';
const AUTH_COOKIE_SEED = 'biomed-chat';

function computeAuthCookieValue() {
  return createHmac('sha256', SITE_PASSWORD).update(AUTH_COOKIE_SEED).digest('hex');
}

function parseCookies(req) {
  const header = req.headers['cookie'] || '';
  const pairs = header.split(';').map(s => s.trim()).filter(Boolean);
  const out = {};
  for (const p of pairs) {
    const idx = p.indexOf('=');
    if (idx > 0) {
      const k = p.slice(0, idx);
      const v = p.slice(idx + 1);
      out[k] = decodeURIComponent(v);
    }
  }
  return out;
}

function isHtmlRequest(req) {
  const accept = req.headers['accept'] || '';
  return req.method === 'GET' && accept.includes('text/html');
}

function requireSitePassword(req, res, next) {
  if (!SITE_PASSWORD) return next();

  const urlPath = req.path || req.url;
  if (urlPath.startsWith('/login') || urlPath === '/health') return next();

  const cookies = parseCookies(req);
  const expected = computeAuthCookieValue();
  if (cookies[AUTH_COOKIE_NAME] === expected) return next();

  if (isHtmlRequest(req)) {
    return res.redirect(302, '/login');
  }
  return res.status(401).json({ error: 'Unauthorized' });
}

if (SITE_PASSWORD) {
  console.log('[INFO] Password protection enabled for all routes');
} else {
  console.warn('[WARN] SITE_PASSWORD not set. Site is NOT password protected.');
}

// Public login/logout endpoints
function renderLoginHtml(errorMessage = '') {
  const errorBlock = errorMessage
    ? `<div style="color:#b00020; margin-bottom: 12px;">${errorMessage}</div>`
    : '';
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Biomed Chat – Sign in</title>
<style>
  body { font-family: -apple-system, system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif; background: #0b0f19; color: #e6eaf2; display: grid; place-items: center; min-height: 100vh; margin: 0; }
  .card { background: #121826; border: 1px solid #222b45; padding: 28px; border-radius: 12px; width: 100%; max-width: 360px; box-shadow: 0 10px 30px rgba(0,0,0,0.35); }
  h1 { margin: 0 0 16px; font-size: 18px; font-weight: 600; }
  label { display: block; margin: 0 0 8px; font-size: 12px; color: #a0acc0; }
  input[type=password] { width: 100%; padding: 10px 12px; border-radius: 8px; border: 1px solid #2a3553; background: #0b1220; color: #e6eaf2; outline: none; }
  input[type=password]:focus { border-color: #4c8dff; box-shadow: 0 0 0 3px rgba(76, 141, 255, 0.2); }
  button { margin-top: 14px; width: 100%; padding: 10px 12px; border-radius: 8px; background: #2f6feb; color: white; border: none; cursor: pointer; font-weight: 600; }
  button:hover { background: #275bd4; }
  .footer { margin-top: 12px; font-size: 12px; color: #8b97ad; text-align: center; }
</style>
<body>
  <form class="card" method="post" action="/login">
    <h1>Enter password</h1>
    ${errorBlock}
    <label for="password">Password</label>
    <input id="password" name="password" type="password" autocomplete="current-password" autofocus required />
    <button type="submit">Continue</button>
    <div class="footer">Access is restricted</div>
  </form>
</body>
</html>`;
}

app.get('/login', (req, res) => {
  if (!SITE_PASSWORD) return res.redirect(302, '/');
  const cookies = parseCookies(req);
  const expected = computeAuthCookieValue();
  if (cookies[AUTH_COOKIE_NAME] === expected) return res.redirect(302, '/');
  res.status(200).send(renderLoginHtml());
});

app.post('/login', (req, res) => {
  if (!SITE_PASSWORD) return res.redirect(302, '/');
  const { password } = req.body || {};
  if (password === SITE_PASSWORD) {
    const expected = computeAuthCookieValue();
    const isProd = process.env.NODE_ENV === 'production';
    const cookie = `${AUTH_COOKIE_NAME}=${encodeURIComponent(expected)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${60 * 60 * 24 * 30}${isProd ? '; Secure' : ''}`;
    res.setHeader('Set-Cookie', cookie);
    return res.redirect(302, '/');
  }
  res.status(401).send(renderLoginHtml('Incorrect password'));
});

app.get('/logout', (req, res) => {
  const isProd = process.env.NODE_ENV === 'production';
  res.setHeader('Set-Cookie', `${AUTH_COOKIE_NAME}=; Path=/; HttpOnly; Max-Age=0; SameSite=Lax${isProd ? '; Secure' : ''}`);
  res.redirect(302, '/login');
});

// Apply auth before serving static assets and API routes
app.use(requireSitePassword);

app.use(express.static(path.join(__dirname, 'public')));

const XAI_API_KEY = process.env.XAI_API_KEY || '';
const XAI_MODEL = process.env.XAI_MODEL || 'grok-4';

if (!XAI_API_KEY) {
  console.warn('[WARN] XAI_API_KEY is not set. Ensure .env contains XAI_API_KEY=...');
} else {
  console.log('[INFO] XAI_API_KEY loaded');
}

const systemPrompt = `Role: Senior biomedical engineering copilot for practitioners.

Operating principles:
- Assume baseline practitioner knowledge: you can use standard terms (e.g., Poisson’s ratio, Nyquist sampling, impedance, HbA1c, ISO 13485) without lengthy definitions.
- Be concise and clinically/technically actionable. Favor bullet points, numbered steps, and brief justifications.
- Use equations and units when material, otherwise avoid math bloat.
- Note safety, regulatory, and validation considerations succinctly (e.g., IEC 60601, FDA 21 CFR 820, ISO 14971) when relevant.
- When uncertain, state assumptions and propose quick validation steps.
- Prefer pragmatic designs, references, and checks over theory recaps.
- If a result depends on parameters, provide defaults and ranges appropriate to typical biomedical contexts.

Response style:
- Start with a one‑sentence answer, then compact details.
- Use structured sections: Summary, Steps, Key Params, Risks/Checks, References (short).
- Keep code and math minimal, but correct and runnable when requested.
- Avoid overexplaining basics; this is for field practitioners.
`;

app.post('/api/chat', async (req, res) => {
  try {
    const { messages } = req.body || {};
    if (!Array.isArray(messages)) {
      return res.status(400).json({ error: 'messages must be an array' });
    }

    const fullMessages = [
      { role: 'system', content: systemPrompt },
      ...messages,
    ];

    // Stream via Server-Sent Events for responsive UI
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const response = await fetch('https://api.x.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${XAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: XAI_MODEL,
        messages: fullMessages,
        stream: true,
        temperature: 0.2,
        max_tokens: 1200,
      }),
    });

    if (!response.ok || !response.body) {
      const text = await response.text();
      res.write(`event: error\n`);
      res.write(`data: ${JSON.stringify({ error: text || 'Upstream error' })}\n\n`);
      return res.end();
    }

    const reader = response.body.getReader();
    const textDecoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = textDecoder.decode(value);
      // Forward upstream SSE as-is (already includes data: lines and separators)
      res.write(chunk);
    }

    return res.end();
  } catch (err) {
    res.write(`event: error\n`);
    res.write(`data: ${JSON.stringify({ error: err?.message || 'Unknown error' })}\n\n`);
    res.end();
  }
});

app.get('/health', (_req, res) => {
  res.json({ ok: true });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Biomed Chat listening on http://localhost:${port}`);
}); 