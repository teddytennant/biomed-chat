/* Vercel Serverless Function: /api/logout */

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.statusCode = 405;
    res.setHeader('Allow', 'GET');
    return res.end('Method Not Allowed');
  }
  const isProd = process.env.NODE_ENV === 'production';
  res.setHeader('Set-Cookie', `bc_auth=; Path=/; HttpOnly; Max-Age=0; SameSite=Lax${isProd ? '; Secure' : ''}`);
  res.statusCode = 204;
  res.end();
} 