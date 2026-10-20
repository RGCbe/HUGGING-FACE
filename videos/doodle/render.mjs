// Render a doodle video's frames with headless Chromium and pipe them into ffmpeg.
//
//   node render.mjs --scenes SCENES.js --timing TIMING.json --out OUT.mp4
//        [--layout landscape|vertical] [--fps 30] [--from SEC] [--to SEC] [--stills t1,t2,...]
//
// --stills writes PNG frames at the given times next to OUT instead of a video (for checking).
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, all) => (a.startsWith('--') ? [...acc, [a.slice(2), all[i + 1]]] : acc), []),
);
const here = path.dirname(fileURLToPath(import.meta.url));
const fps = Number(args.fps || 30);
const layouts = {
  landscape: { width: 1920, height: 1080, scale: 1, x: 0, y: 0, penScale: 1 },
  // The 1920x1080 scene space shrinks into the middle of a 1080x1920 frame; captions and a
  // title go above and below it.
  vertical: { width: 1080, height: 1920, scale: 0.5625, x: 0, y: 660, penScale: 0.7 },
};
const stage = layouts[args.layout || 'landscape'];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: stage.width, height: stage.height } });
page.on('pageerror', (e) => console.error('page error:', e.message));
page.on('console', (m) => m.type() === 'warning' && console.log('warning:', m.text()));
await page.goto('file://' + path.join(here, 'engine.html'));
await page.evaluate(() => document.fonts.load("64px 'Hand'"));
await page.evaluate(([timing, st]) => {
  window.TIMING = timing;
  window.Doodle.init(st);
}, [JSON.parse(readFileSync(args.timing, 'utf8')), stage]);
await page.addScriptTag({ path: path.resolve(args.scenes) });
const total = await page.evaluate(() => window.Doodle.duration());

if (args.stills) {
  const times = args.stills === 'auto'
    ? await page.evaluate(() => window.Doodle.sceneEnds())
    : args.stills.split(',').map(Number);
  for (const t of times) {
    await page.evaluate((tt) => window.Doodle.renderAt(tt), t);
    const file = args.out.replace(/\.mp4$/, '') + `_${t.toFixed(2)}.png`;
    await page.screenshot({ path: file });
    console.log('still', file);
  }
  await browser.close();
  process.exit(0);
}

const from = Number(args.from || 0);
const to = Math.min(Number(args.to || total), total);
const frames = Math.round((to - from) * fps);
const ff = spawn('ffmpeg', ['-nostdin', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps),
  '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', args.out],
{ stdio: ['pipe', 'inherit', 'inherit'] });
const started = Date.now();
for (let i = 0; i < frames; i++) {
  await page.evaluate((tt) => window.Doodle.renderAt(tt), from + i / fps);
  const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  if (i % (fps * 10) === 0) console.log(`frame ${i}/${frames}  ${((Date.now() - started) / 1000).toFixed(0)}s`);
}
ff.stdin.end();
await new Promise((r) => ff.on('close', r));
await browser.close();
console.log(`wrote ${args.out}: ${frames} frames in ${((Date.now() - started) / 1000).toFixed(0)}s`);
