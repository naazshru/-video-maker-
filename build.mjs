// One-command builder for all Ushvika product films.
//   node build.mjs                 -> render every film (CPU / software WebGL)
//   node build.mjs --gpu           -> use the graphics card (opens a Chromium window; much faster)
//   node build.mjs jelly twist     -> only these films
//   node build.mjs --fps 24        -> other frame rate (default 30)
//   node build.mjs --workers 16    -> parallel renderers (default: up to 4; raise it on big cloud machines)
// Output: out/<film>.mp4 (1920x1080, H.264 + AAC). Needs Node 18+, ffmpeg on PATH, and Playwright Chromium.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { chromium } from 'playwright';

const FILMS = {
  rose_tea:   { page: 'trailer/index.html', audio: 'trailer/music.wav' },
  rose_jelly: { page: 'jelly/index.html',   audio: 'jelly/final_audio.wav' },
  rose_badam: { page: 'badam/index.html',   audio: 'badam/final_audio.wav' },
  rose_twist: { page: 'twist/index.html',   audio: 'twist/final_audio.wav' },
};

const args = process.argv.slice(2);
const gpu = args.includes('--gpu');
const fpsIdx = args.indexOf('--fps');
const FPS = fpsIdx >= 0 ? +args[fpsIdx + 1] : 30;
const wIdx = args.indexOf('--workers');
const wanted = args.filter((a, i) => !a.startsWith('--') && args[i - 1] !== '--fps' && args[i - 1] !== '--workers')
  .map(a => FILMS[a] ? a : Object.keys(FILMS).find(k => k.endsWith(a))).filter(Boolean);
const films = wanted.length ? wanted : Object.keys(FILMS);
const WORKERS = wIdx >= 0 ? +args[wIdx + 1] : gpu ? 2 : Math.max(1, Math.min(4, os.cpus().length));
const ROOT = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
const OUT = path.join(ROOT, 'out');

// tiny static server for the repo
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.ttf': 'font/ttf', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, r));
const base = `http://localhost:${server.address().port}/`;

// one browser per worker: each gets its own GPU/WebGL process, so workers really run in parallel
const launch = () => chromium.launch(gpu
  ? { headless: false, args: ['--ignore-gpu-blocklist', '--enable-gpu-rasterization'] }
  : { args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const browsers = await Promise.all([...Array(WORKERS)].map(launch));

for (const name of films) {
  const film = FILMS[name];
  const frames = path.join(OUT, 'frames_' + name);
  fs.mkdirSync(frames, { recursive: true });
  const probe = await browsers[0].newPage({ viewport: { width: 1920, height: 1080 } });
  await probe.goto(base + film.page);
  await probe.waitForFunction(() => window.READY === true, null, { timeout: 120000 });
  const dur = await probe.evaluate(() => window.DURATION);
  await probe.close();
  const total = Math.round(dur * FPS);
  console.log(`\n${name}: ${dur}s, ${total} frames, ${WORKERS} workers, ${gpu ? 'GPU' : 'CPU'}`);
  let done = 0; const t0 = Date.now();
  await Promise.all([...Array(WORKERS).keys()].map(async w => {
    const page = await browsers[w].newPage({ viewport: { width: 1920, height: 1080 } });
    page.setDefaultTimeout(0);   // a busy machine can take a while per frame
    page.on('pageerror', e => console.log('pageerror:', e.message));
    await page.goto(base + film.page);
    await page.waitForFunction(() => window.READY === true, null, { timeout: 120000 });
    for (let i = w; i < total; i += WORKERS) {
      const file = path.join(frames, `f${String(i).padStart(5, '0')}.jpg`);
      if (!fs.existsSync(file)) {            // resumable: skips frames already rendered
        await page.evaluate(t => window.renderAt(t), i / FPS);
        await page.screenshot({ path: file, type: 'jpeg', quality: 93 });
      }
      if (++done % 30 === 0) process.stdout.write(`\r  ${done}/${total} frames  (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    }
    await page.close();
  }));
  const mp4 = path.join(OUT, name + '.mp4');
  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, 'f%05d.jpg'),
    '-i', path.join(ROOT, film.audio), '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-t', String(dur), '-movflags', '+faststart', mp4], { stdio: 'inherit' });
  console.log(r.status === 0 ? `\n  -> ${mp4}` : `\n  ffmpeg failed for ${name}`);
}
await Promise.all(browsers.map(b => b.close())); server.close();
