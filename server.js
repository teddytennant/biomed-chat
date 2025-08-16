import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { createHmac } from 'crypto';
import fetch from 'node-fetch'; // Using node-fetch to call the Python API

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env explicitly from CWD first, then fallback to server directory
dotenv.config({ path: path.join(process.cwd(), '.env') });
if (!process.env.SITE_PASSWORD) {
  dotenv.config({ path: path.join(__dirname, '.env') });
}

const app = express();
app.use(cors());
app.use(express.json({ limit: '2mb' }));
app.use(express.urlencoded({ extended: false }));

// --- Start: Auth Middleware (largely unchanged) ---
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
  // Allow access to API routes for the frontend to call
  if (urlPath.startsWith('/login') || urlPath === '/health' || urlPath.startsWith('/api')) return next();
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

app.post('/login', express.urlencoded({ extended: true }), (req, res) => {
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
// --- End: Auth Middleware ---

// Apply auth to all routes before they are handled
app.use(requireSitePassword);

// --- API Routes ---
const PYTHON_API_URL = `http://localhost:${process.env.PYTHON_API_PORT || 8000}/api/chat`;

app.post('/api/chat', async (req, res) => {
  console.log('[INFO] Received chat request. Relaying to Python RAG service...');

  req.on('close', () => {
    console.log('[INFO] Client disconnected, connection closed.');
    res.end();
  });

  try {
    const { messages } = req.body || {};
    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: 'messages must be a non-empty array' });
    }

    const userQuery = messages[messages.length - 1].content;

    const pythonServiceResponse = await fetch(PYTHON_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ query: userQuery }),
    });

    if (!pythonServiceResponse.ok) {
      const errorBody = await pythonServiceResponse.text();
      console.error('[ERROR] Python service returned an error:', pythonServiceResponse.status, errorBody);
      throw new Error(`Python service failed with status ${pythonServiceResponse.status}`);
    }

    const data = await pythonServiceResponse.json();
    const responseText = data.response;

    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const ssePayload = {
      choices: [{ delta: { content: responseText } }]
    };
    res.write(`data: ${JSON.stringify(ssePayload)}\n\n`);
    res.write(`data: [DONE]\n\n`);
    res.end();

    console.log('[INFO] Successfully relayed response from Python service.');

  } catch (err) {
    console.error('[ERROR] Failed to connect to Python RAG service:', err.message);
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    const errorPayload = {
        error: { message: 'The backend RAG service is currently unavailable. Please try again later.' }
    };
    res.write(`event: error\n`);
    res.write(`data: ${JSON.stringify(errorPayload)}\n\n`);
    res.end();
  }
});

app.get('/health', (_req, res) => {
  res.json({ ok: true });
});

// --- Serve React Frontend ---
if (process.env.NODE_ENV === 'production') {
  const clientBuildPath = path.join(__dirname, 'dist', 'client');
  app.use(express.static(clientBuildPath));

  // For any other GET request, serve the React app's index.html
  app.get('*', (req, res) => {
    res.sendFile(path.join(clientBuildPath, 'index.html'));
  });
}

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Biomed Chat (Node.js server) listening on http://localhost:${port}`);
  console.log(`Expecting Python RAG service to be running at ${PYTHON_API_URL}`);
  if (process.env.NODE_ENV === 'production') {
    console.log('Serving production build of the frontend.');
  } else {
    console.log('Frontend is served by the Vite dev server. Run `npm run dev:frontend`.');
  }
});

export default app;
