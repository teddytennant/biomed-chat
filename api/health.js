export default function handler(req, res) {
  res.statusCode = 200;
  res.json({
    ok: true,
    node: process.version,
    hasXaiApiKey: Boolean(process.env.XAI_API_KEY),
    hasSitePassword: Boolean(process.env.SITE_PASSWORD || process.env.BASIC_AUTH_PASS),
    env: process.env.VERCEL_ENV || 'unknown'
  });
} 