// Renders index.html frame-by-frame with headless Chromium (Playwright).
// usage: node render.mjs <outDir> <fps> [start] [end] [onlyTimesCsv]
import { chromium } from 'playwright';
const [,, outDir='frames', fpsS='30', startS, endS, only] = process.argv;
const fps = +fpsS;
const browser = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('console', m => console.log('page:', m.text()));
page.on('pageerror', e => console.log('pageerror:', e.message));
await page.goto(process.env.PAGE_URL || 'http://localhost:8765/index.html');
await page.waitForFunction(() => window.READY === true, null, { timeout: 60000 });
const dur = await page.evaluate(() => window.DURATION);
const total = Math.round(dur * fps);
let frames;
if (only) frames = only.split(',').map(s => Math.round(+s * fps));
else { const a = +(startS ?? 0), b = +(endS ?? total); frames = []; for (let i = a; i < Math.min(b, total); i++) frames.push(i); }
for (const i of frames) {
  await page.evaluate(t => window.renderAt(t), i / fps);
  await page.screenshot({ path: `${outDir}/f${String(i).padStart(5,'0')}.jpg`, type: 'jpeg', quality: 93 });
  if (i % 60 === 0) console.log('frame', i);
}
await browser.close();
