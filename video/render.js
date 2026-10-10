// 将 film.html 逐帧导出为 1080×1920 / 30fps 的 MP4，并输出封面 cover.jpg
// 用法：node video/render.js [输出目录]    需要 playwright 与 ffmpeg
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const outDir = path.resolve(process.argv[2] || path.join(__dirname, 'out'));
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto('file://' + path.join(__dirname, 'film.html') + '?render');
  await page.waitForFunction(() => window.FILM && window.FILM.ready, null, { timeout: 60000 });
  console.log('fonts', await page.evaluate(() => FILM.fontStatus()));

  const wavPath = path.join(outDir, 'audio.wav');
  fs.writeFileSync(wavPath, Buffer.from(await page.evaluate(() => FILM.renderAudio()), 'base64'));
  console.log('audio done');

  const { frames, fps, coverFrame } = await page.evaluate(() => ({ frames: FILM.frames, fps: FILM.fps, coverFrame: FILM.coverFrame }));
  const mp4 = path.join(outDir, 'video.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-i', wavPath,
    // 胶片颗粒很吃码率：限制在短视频平台推荐的范围内
    '-c:v', 'libx264', '-preset', 'slow', '-b:v', '14M', '-maxrate', '18M', '-bufsize', '28M', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-r', String(fps),
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000',
    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', mp4], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => ff.on('close', code => code === 0 ? res() : rej(new Error('ffmpeg exit ' + code))));

  const t0 = Date.now();
  let cover = null;
  for (let i = 0; i < frames; i++) {
    const url = await page.evaluate(i => FILM.render(i), i);
    if (!ff.stdin.write(Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i === coverFrame) cover = true;
    if (i % 60 === 0) console.log(`frame ${i}/${frames}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await done;

  if (cover) {
    const url = await page.evaluate(() => FILM.cover());
    fs.writeFileSync(path.join(outDir, 'cover.jpg'), Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));
  }
  await browser.close();
  console.log('done →', mp4);
})().catch(e => { console.error(e); process.exit(1); });
