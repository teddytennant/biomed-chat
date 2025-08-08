/* Vercel Serverless Function: /api/login */

import { createHmac } from 'crypto';

const AUTH_COOKIE_NAME = 'bc_auth';
const AUTH_COOKIE_SEED = 'biomed-chat';

function computeAuthCookieValue(password) {
  return createHmac('sha256', password).update(AUTH_COOKIE_SEED).digest('hex');
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.statusCode = 405;
    res.setHeader('Allow', 'POST');
    return res.end('Method Not Allowed');
  }

  const SITE_PASSWORD = process.env.SITE_PASSWORD || process.env.BASIC_AUTH_PASS || '';
  if (!SITE_PASSWORD) {
    // If not configured, allow through to avoid lockout
    res.statusCode = 204;
    return res.end();
  }

  let body = '';
  for await (const chunk of req) body += chunk;
  const parsed = new URLSearchParams(body);
  const providedPassword = parsed.get('password') || '';

  if (providedPassword === SITE_PASSWORD) {
    const expected = computeAuthCookieValue(SITE_PASSWORD);
    const isProd = process.env.NODE_ENV === 'production';
    const cookie = `${AUTH_COOKIE_NAME}=${encodeURIComponent(expected)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${60 * 60 * 24 * 30}${isProd ? '; Secure' : ''}`;
    res.setHeader('Set-Cookie', cookie);
    res.statusCode = 204;
    return res.end();
  }

  res.statusCode = 401;
  res.end('Unauthorized');
} 