/** Check the sanitized WebM opens in Chromium and capture one ignored review frame. */
import { createRequire } from 'node:module';
import { readFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('../../frontend/node_modules/playwright');
const root = resolve(import.meta.dirname, '../..');
const video = readFileSync(resolve(root, 'docs/assets/demo/walkthrough.webm'));
const out = resolve(root, 'artifacts/presentation-20261020');
mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ headless: true, channel: 'msedge' });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('about:blank');
  const metadata = await page.evaluate(async source => {
    const player = document.createElement('video');
    player.src = 'data:video/webm;base64,' + source;
    player.muted = true;
    player.style.width = '1440px';
    player.style.height = '900px';
    document.body.style.margin = '0';
    document.body.appendChild(player);
    await new Promise((resolve, reject) => {
      player.onloadedmetadata = resolve;
      player.onerror = () => reject(new Error('Video could not be decoded'));
    });
    await player.play();
    await new Promise(resolve => setTimeout(resolve, 1600));
    return { width: player.videoWidth, height: player.videoHeight, current_time: player.currentTime };
  }, video.toString('base64'));
  if (metadata.width !== 1440 || metadata.height !== 900 || metadata.current_time < 1) {
    throw new Error('Unexpected demo video dimensions or playback');
  }
  await page.screenshot({ path: resolve(out, 'video-playback-review.png') });
  console.log(JSON.stringify({ playable: true, ...metadata, bytes: video.length }));
} finally {
  await browser.close();
}
