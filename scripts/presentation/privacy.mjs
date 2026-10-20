const APPROVED_ORIGIN = 'https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io';

export function validateOrigin(value) {
  const url = new URL(value);
  if (url.origin !== APPROVED_ORIGIN || url.username || url.password || url.search || url.hash || url.pathname !== '/') {
    throw new Error('Recording requires the approved public frontend origin only');
  }
  return url.origin;
}

export function redact(value) {
  return String(value)
    .replace(/-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----/gi, '[private material hidden]')
    .replace(/eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}/g, '[token hidden]')
    .replace(/\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b/gi, '[identifier hidden]')
    .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, '[account hidden]')
    .replace(/postgresql(?:\+psycopg)?:\/\/[^\s]+/gi, '[database URL hidden]')
    .replace(/\b[0-9a-f]{64}\b/gi, '[digest hidden]');
}

export const approvedOrigin = APPROVED_ORIGIN;
