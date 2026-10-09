// Frame-exact capture with Playwright Chromium (SwiftShader WebGL2). Node 20+, CommonJS.
// usage: node cap.js <page.html> <out_dir> <from_s> <to_s> [--png] [--stills 1.5,3.2]
const path = require('path'), fs = require('fs');
const PW = process.env.PW_MODULE || '/usr/local/lib/node_modules/playwright';
const { chromium } = require(PW);
const [page, out, from = '0', to = '', ...rest] = process.argv.slice(2);
const png = rest.includes('--png'); const si = rest.indexOf('--stills'); const stills = si >= 0 ? rest[si + 1].split(',').map(Number) : null;
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--force-color-profile=srgb'] });
  const kill = () => { try { b.close(); } catch (e) {} }; process.on('SIGTERM', kill); process.on('SIGINT', kill);
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; p.on('pageerror', (e) => errs.push(String(e))); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + path.resolve(page));
  await p.waitForFunction('window.__comp && window.__seek', null, { timeout: 60000 });
  const comp = await p.evaluate(() => window.__comp); await p.setViewportSize({ width: comp.width, height: comp.height });
  const shot = async (t, file) => { await p.evaluate(async (tt) => { await window.__seek(tt); await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))); }, t); await p.screenshot({ path: file, type: png ? 'png' : 'jpeg', quality: png ? undefined : 93 }); };
  if (stills) { for (const t of stills) await shot(t, `${out}/still_${t.toFixed(2)}.${png ? 'png' : 'jpg'}`); }
  else { const fps = comp.fps, n0 = Math.round(+from * fps), n1 = Math.round((to ? +to : comp.duration) * fps);
    for (let n = n0; n < n1; n++) { const f = `${out}/f_${String(n).padStart(5, '0')}.${png ? 'png' : 'jpg'}`; if (fs.existsSync(f)) continue; await shot(n / fps, f); } }
  if (errs.length) console.error('page errors:', errs.slice(0, 5).join(' | '));
  await b.close();
})().catch((e) => { console.error('CAPTURE FAILED', e.message); process.exit(1); });
