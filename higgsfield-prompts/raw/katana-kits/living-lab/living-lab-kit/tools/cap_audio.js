// Render the synthesised score page (OfflineAudioContext) to WAV with Playwright Chromium.
// usage: node cap_audio.js "<score.html>?preset=arrival&bpm=120&dur=30&drop=2&vac=19.5&lift=20&end=28" out.wav
const path = require('path'), fs = require('fs');
const { chromium } = require(process.env.PW_MODULE || '/usr/local/lib/node_modules/playwright');
const [arg, out] = process.argv.slice(2); const [page, q] = arg.split('?');
(async () => {
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--allow-file-access-from-files'] });
  const p = await b.newPage(); let err = ''; p.on('pageerror', (e) => { err = String(e); });
  await p.goto('file://' + path.resolve(page) + (q ? '?' + q : ''));
  await p.waitForFunction('window.__done || window.__err', null, { timeout: 240000, polling: 300 }).catch(() => {});
  const st = await p.evaluate(() => (window.__err ? 'ERR ' + window.__err : window.__done ? 'done' : 'pending'));
  if (st !== 'done') { console.error('SCORE FAILED', st, err); process.exit(1); }
  const len = await p.evaluate(() => window.__wav.length), size = 1 << 20, parts = [];
  for (let i = 0; i * size < len; i++) parts.push(Buffer.from(await p.evaluate(([i, s]) => window.__chunk(i, s), [i, size]), 'base64'));
  fs.writeFileSync(out, Buffer.concat(parts)); console.log('wrote', out, len, 'bytes'); await b.close();
})().catch((e) => { console.error('SCORE FAILED', e.message); process.exit(1); });
