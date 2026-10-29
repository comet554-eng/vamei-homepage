// 内联 SVG（让 currentColor 和页面字体生效）、按 3D 渲染给出的锚点画板芯分层引线，全部就绪后设置 __READY 供截图
(async () => {
  const inline = [...document.querySelectorAll('[data-svg]')].map(async el => {
    try {
      const r = await fetch(el.dataset.svg);
      if (r.ok) el.innerHTML = await r.text();
      else el.classList.add('missing');
    } catch { el.classList.add('missing'); }
  });

  const imgs = [...document.images].map(im => im.complete ? Promise.resolve() :
    new Promise(res => { im.onload = im.onerror = res; }));

  await Promise.all([...inline, ...imgs]);
  await document.fonts.ready;
  await drawLayerLines();
  window.__READY = true;
})();

async function drawLayerLines() {
  const wrap = document.querySelector('.layers-wrap');
  if (!wrap) return;
  let anchors;
  try { anchors = await (await fetch('../assets/gen/layers-exploded.json')).json(); } catch { return; }
  const img = wrap.querySelector('.layers-img');
  const svg = wrap.querySelector('.layers-lines');
  const k = img.clientWidth / (img.naturalWidth || 1500);
  const box = wrap.getBoundingClientRect();
  const ib = img.getBoundingClientRect();
  svg.setAttribute('viewBox', `0 0 ${box.width} ${box.height}`);
  svg.setAttribute('width', box.width);
  svg.setAttribute('height', box.height);
  const labels = [...wrap.querySelectorAll('.layers-labels li')];
  const list = Array.isArray(anchors) ? anchors : anchors.layers || [];
  const midX = ib.left - box.left + ib.width / 2;
  // 锚点在图左半边的标签放左栏，右半边放右栏；同一栏内按锚点高度排开，避免重叠
  const items = labels.map((li, i) => {
    const a = list.find(x => String(x.id) === li.dataset.id) || list[i];
    if (!a) return null;
    const ax = ib.left - box.left + a.x * k, ay = ib.top - box.top + a.y * k;
    return { li, ax, ay, right: ax > midX };
  }).filter(Boolean);
  const GAP = 66, COL = 196, EDGE = 22;
  for (const right of [false, true]) {
    let last = -Infinity;
    items.filter(it => it.right === right).sort((p, q) => p.ay - q.ay).forEach(it => {
      it.ly = Math.max(it.ay, last + GAP); last = it.ly;
      it.li.classList.toggle('r', right);
      it.li.style.top = `${it.ly - 14}px`;
      it.li.style.left = right ? `${box.width - EDGE - COL}px` : `${EDGE}px`;
    });
  }
  for (const it of items) {
    const lx = it.right ? box.width - EDGE - COL - 12 : EDGE + COL + 12;
    const elbow = it.right ? Math.max(it.ax + 24, lx - 40) : Math.min(it.ax - 24, lx + 40);
    svg.insertAdjacentHTML('beforeend',
      `<polyline points="${it.ax},${it.ay} ${elbow},${it.ly} ${lx},${it.ly}" />` +
      `<circle cx="${it.ax}" cy="${it.ay}" r="4" />`);
  }
}
