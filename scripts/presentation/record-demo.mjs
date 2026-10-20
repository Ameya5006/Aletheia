/** Record only redacted viewport stills from the approved public deployment. */
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { validateOrigin, redact, approvedOrigin } from './privacy.mjs';

const require = createRequire(import.meta.url);
const { chromium } = require('../../frontend/node_modules/playwright');
const root = resolve(import.meta.dirname, '../..');
const media = resolve(root, 'docs/assets/demo');
const tokenPath = resolve(root, 'artifacts/azure-preflight/cloud-private/engineer.token');
const origin = validateOrigin(process.argv[2] ?? approvedOrigin);
const token = readFileSync(tokenPath, 'utf8').trim();
if (!token || token.includes('\n')) throw new Error('Expected one provisioned token in ignored private file');
mkdirSync(media, { recursive: true });
for (let attempt = 0; attempt < 3; attempt++) {
  try {
    const ready = await fetch(origin + '/api/health/ready', { signal: AbortSignal.timeout(45000) });
    if (ready.status === 200) break;
  } catch {
    // A scaled-to-zero API may need another bounded public readiness attempt.
  }
}

const browser = await chromium.launch({ headless: true, channel: 'msedge' });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
// Some managed desktops deny Chromium egress while Node can reach the same
// public host. Fulfil only this exact origin with live HTTPS responses.
await context.route('**/*', async route => {
  const request = route.request();
  const url = new URL(request.url());
  if (url.origin !== origin) return route.continue();
  const headers = { ...request.headers() };
  for (const name of ['host', 'content-length', 'accept-encoding', 'connection']) delete headers[name];
  const response = await fetch(request.url(), {
    method: request.method(),
    headers,
    body: ['GET', 'HEAD'].includes(request.method()) ? undefined : request.postDataBuffer(),
    signal: AbortSignal.timeout(30000),
  });
  const responseHeaders = Object.fromEntries(response.headers);
  for (const name of ['content-length', 'content-encoding', 'transfer-encoding', 'connection']) delete responseHeaders[name];
  await route.fulfill({ status: response.status, headers: responseHeaders, body: Buffer.from(await response.arrayBuffer()) });
});
const page = await context.newPage();
if (process.env.ALETHEIA_DEMO_DEBUG === '1') page.on('response', response => {
  const url = new URL(response.url());
  if (url.origin === origin && url.pathname.startsWith('/api/')) console.error('API status:', redact(url.pathname), response.status());
});
const frames = [];
const clean = async () => {
  await page.evaluate(() => {
    const scrub = (value) => String(value)
      .replace(/eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}/g, '[token hidden]')
      .replace(/\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b/gi, '[identifier hidden]')
      .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, '[account hidden]')
      .replace(/\b[0-9a-f]{64}\b/gi, '[digest hidden]');
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement?.closest('script,style')) continue;
      const next = scrub(node.textContent);
      if (next !== node.textContent) node.textContent = next;
    }
    for (const field of document.querySelectorAll('input')) {
      if (field.type === 'password') field.value = '';
      field.setAttribute('autocomplete', 'off');
    }
  });
};
async function shot(name, caption, seconds) {
  await clean();
  const bytes = await page.screenshot({ type: 'jpeg', quality: 78, animations: 'disabled' });
  const decoded = bytes.toString('latin1');
  if (redact(decoded) !== decoded) throw new Error('Image byte privacy check failed');
  writeFileSync(resolve(media, name + '.jpg'), bytes);
  frames.push({ name, caption, seconds, image: 'data:image/jpeg;base64,' + bytes.toString('base64') });
}
try {
  await page.goto(origin, { waitUntil: 'domcontentloaded' });
  await page.getByRole('heading', { name: 'Overview' }).waitFor();
  await shot('00-overview', 'Aletheia: public research workbench overview', 4);
  await page.goto(origin + '/local-session', { waitUntil: 'domcontentloaded' });
  await page.getByLabel('Provisioned access token').waitFor();
  await shot('01-identity', 'Provisioned identity: a short lived operator token', 5);
  await page.getByLabel('Provisioned access token').fill(token);
  let connectedStatus;
  for (let attempt = 0; attempt < 3; attempt++) {
    const response = page.waitForResponse(r => r.url().includes('/api/v1/analyses?limit=1'), { timeout: 30000 }).catch(() => null);
    await page.getByRole('button', { name: 'Connect provisioned identity' }).click();
    connectedStatus = (await response)?.status();
    if (connectedStatus === 200) break;
  }
  if (connectedStatus !== 200) throw new Error('Provisioned identity failed after bounded retries');
  await page.getByLabel('Admission type').waitFor();
  await shot('02-new-analysis', 'New Analysis: validated clinical input fields', 5);
  for (const [label, value] of Object.entries({
    'Admission type': '2', 'Admission source': '7',
    'Maximum glucose result': 'Norm', 'A1C result': '>7',
    'Diabetes medication prescribed': 'Yes',
  })) await page.getByLabel(label, { exact: true }).selectOption(value);
  for (const [label, value] of Object.entries({
    'Time in hospital': '5', 'Laboratory procedures': '45', Procedures: '2',
    'Distinct medications': '15', 'Outpatient visits in the preceding year': '1',
    'Emergency visits in the preceding year': '1',
    'Inpatient visits in the preceding year': '2', Diagnoses: '6',
  })) await page.getByLabel(label, { exact: true }).fill(value);
  await shot('03-inputs', 'Illustrative manually entered case values', 5);
  const createdResponse = page.waitForResponse(r => r.url().endsWith('/api/v1/analyses') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Run Analysis', exact: true }).click();
  const created = await createdResponse;
  if (created.status() !== 201) throw new Error('Prediction failed');
  const original = (await created.json()).data;
  if (!(original.probability >= 0 && original.probability <= 1)) throw new Error('Invalid probability');
  await page.getByRole('heading', { name: 'Prediction Result' }).waitFor();
  await page.getByRole('heading', { name: 'Prediction Result' }).evaluate(element => element.scrollIntoView({ block: 'start' }));
  await shot('04-result', 'Calibrated prediction and frozen model context', 7);
  await page.getByRole('heading', { name: 'Explanation evidence' }).evaluate(element => element.scrollIntoView({ block: 'start' }));
  await shot('04b-explanation', 'Noncausal contributions relative to a reference case', 6);
  await page.getByRole('button', { name: 'Save Analysis' }).click();
  await page.getByText('Saved', { exact: true }).waitFor();
  await shot('05-saved', 'Save persists the analysis and preserves its audit evidence', 5);
  await page.getByRole('link', { name: 'Analysis History', exact: true }).click();
  await page.getByRole('link', { name: 'Open analysis ' + original.prediction_id }).waitFor();
  await shot('06-history', 'Analysis History: reopen a saved result', 5);
  await page.locator('a[href="/analyses/' + original.prediction_id + '"]').click();
  await page.getByRole('button', { name: 'Load inputs into New Analysis' }).waitFor();
  await shot('07-reopened', 'The saved result remains available after navigation', 5);
  await page.getByRole('button', { name: 'Load inputs into New Analysis' }).click();
  await page.getByLabel('Inpatient visits in the preceding year').fill('4');
  const rerunResponse = page.waitForResponse(r => r.url().endsWith('/api/v1/analyses') && r.request().method() === 'POST');
  await page.getByRole('button', { name: 'Run Analysis', exact: true }).click();
  const rerun = (await (await rerunResponse).json()).data;
  if (rerun.prediction_id === original.prediction_id) throw new Error('Rerun reused original identifier');
  await page.getByRole('heading', { name: 'Prediction Result' }).evaluate(element => element.scrollIntoView({ block: 'start' }));
  await shot('08-rerun', 'Changing one input creates a new analysis', 6);
  const reopened = await fetch(origin + '/api/v1/analyses/' + original.prediction_id, { headers: { Authorization: 'Bearer ' + token } });
  if (reopened.status !== 200 || (await reopened.json()).data.probability !== original.probability) throw new Error('Saved result changed');
  await page.getByRole('link', { name: 'Analysis History', exact: true }).click();
  await page.locator('a[href="/analyses/' + original.prediction_id + '"]').click();
  await page.getByRole('heading', { name: 'Saved Analysis' }).waitFor();
  await shot('08b-original', 'The saved original still shows its unchanged probability', 5);
  await page.getByRole('link', { name: 'Audit Trail', exact: true }).click();
  await page.getByRole('heading', { name: 'Audit Trail' }).waitFor();
  await page.getByRole('heading', { name: 'Committed events' }).waitFor();
  await shot('09-audit', 'Audit Trail: recorded events with identifiers hidden', 6);
  await page.getByRole('link', { name: 'New Analysis', exact: true }).click();
  await page.getByLabel('Time in hospital').fill('5');
  await page.getByRole('button', { name: 'Reset Form' }).click();
  if ((await page.getByLabel('Time in hospital').inputValue()) !== '') throw new Error('Reset failed');
  await shot('10-reset', 'Reset clears unsent input and displayed result', 5);

  const composer = await context.newPage();
  await composer.goto('about:blank');
  const video = await composer.evaluate(async (slides) => {
    const canvas = document.createElement('canvas');
    canvas.width = 1440; canvas.height = 900;
    const draw = canvas.getContext('2d');
    const stream = canvas.captureStream(10);
    const type = MediaRecorder.isTypeSupported('video/webm;codecs=vp8') ? 'video/webm;codecs=vp8' : 'video/webm';
    const recorder = new MediaRecorder(stream, { mimeType: type, videoBitsPerSecond: 700000 });
    const chunks = [];
    recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
    const finished = new Promise(resolve => { recorder.onstop = resolve; });
    recorder.start();
    for (const slide of slides) {
      const img = new Image();
      img.src = slide.image;
      await img.decode();
      const until = performance.now() + slide.seconds * 1000;
      while (performance.now() < until) {
        draw.drawImage(img, 0, 0, canvas.width, canvas.height);
        draw.fillStyle = 'rgba(10, 20, 31, .88)';
        draw.fillRect(0, 846, 1440, 54);
        draw.fillStyle = '#fff';
        draw.font = 'bold 23px Arial';
        draw.fillText(slide.caption, 30, 880);
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
    recorder.stop();
    await finished;
    stream.getTracks().forEach(track => track.stop());
    return Array.from(new Uint8Array(await new Blob(chunks, { type }).arrayBuffer()));
  }, frames);
  writeFileSync(resolve(media, 'walkthrough.webm'), Buffer.from(video));
  writeFileSync(resolve(media, 'poster.jpg'), readFileSync(resolve(media, '04-result.jpg')));
  console.log(JSON.stringify({ screenshots: frames.length, seconds: frames.reduce((sum, frame) => sum + frame.seconds, 0), video_bytes: video.length, probability: original.probability, saved: true, reopened: true, original_immutable: true, reset: true }));
} finally {
  await browser.close();
}
