// Whiteboard doodle engine: scenes add timed items, renderAt(t) poses one frame.
//
// A video is a row of scenes on one long whiteboard. Each scene starts at a time; the camera pans
// to it just before. Inside a scene, items draw themselves stroke by stroke (rough.js sketches) or
// letter by letter (handwritten text), and a marker pen follows the line being drawn.
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const D = (window.Doodle = {});
  D.INK = '#1d1d1f';
  D.ORANGE = '#e8590c';
  D.RED = '#e03131';
  D.BLUE = '#1c7ed6';
  D.GREEN = '#2f9e44';
  D.YELLOW = '#f59f00';
  D.BROWN = '#8d5a2b';
  D.GREY = '#868e96';
  const PAN = 0.5; // seconds the camera takes to move to the next scene

  let svg, defs, camera, penG, rc;
  let scenes = [];
  let cur = null;
  let seed = 1;
  let uid = 0;

  function mk(tag, attrs = {}, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const ease = (q) => (q < 0.5 ? 2 * q * q : 1 - Math.pow(-2 * q + 2, 2) / 2);

  // stage: {width, height, scale, x, y, sceneW?, sceneH?} - the scene space (1920x1080 unless the
  // stage says otherwise) is drawn at scale, offset x/y.
  D.init = function (stage) {
    D.W = stage.sceneW || 1920;
    D.H = stage.sceneH || 1080;
    svg = mk('svg', { width: stage.width, height: stage.height, viewBox: `0 0 ${stage.width} ${stage.height}` });
    document.body.appendChild(svg);
    defs = mk('defs', {}, svg);
    mk('rect', { width: stage.width, height: stage.height, fill: '#ffffff' }, svg);
    const root = mk('g', { transform: `translate(${stage.x || 0},${stage.y || 0}) scale(${stage.scale || 1})` }, svg);
    camera = mk('g', {}, root);
    penG = mk('g', { opacity: 0 }, svg);
    buildPen(stage.penScale || 1);
    rc = rough.svg(svg);
    D.root = root;
    D.svg = svg;
  };

  function buildPen(s) {
    const g = mk('g', { transform: `scale(${s}) rotate(38)` }, penG);
    mk('path', { d: 'M0,0 L30,-11 L30,11 Z', fill: '#222' }, g);
    mk('rect', { x: 30, y: -17, width: 30, height: 34, rx: 4, fill: '#3a3a3a' }, g);
    mk('rect', { x: 58, y: -20, width: 150, height: 40, rx: 8, fill: '#f1f3f5', stroke: '#222', 'stroke-width': 4 }, g);
    mk('rect', { x: 95, y: -20, width: 30, height: 40, fill: D.ORANGE }, g);
    mk('rect', { x: 200, y: -22, width: 48, height: 44, rx: 12, fill: '#222' }, g);
  }

  // ---- scenes and timing --------------------------------------------------------------------

  D.scene = function (t0, build) {
    const g = mk('g', { transform: `translate(${scenes.length * D.W},0)` }, camera);
    cur = { t0, g, items: [] };
    scenes.push(cur);
    build();
    cur = null;
  };

  // Absolute time of the first word of `phrase` in voiceover section n (words from timing.json).
  D.cue = function (n, phrase, nth = 0) {
    const norm = (w) => w.toLowerCase().replace(/[^a-z0-9]/g, '');
    const words = window.TIMING.sections[n - 1].words;
    const want = phrase.split(/\s+/).map(norm).filter(Boolean);
    let seen = 0;
    for (let i = 0; i + want.length <= words.length; i++) {
      if (!want.every((w, k) => norm(words[i + k].w) === w)) continue;
      if (seen++ === nth) return words[i].t0;
    }
    throw new Error(`cue not found: section ${n} "${phrase}"`);
  };
  D.sectionStart = (n) => window.TIMING.sections[n - 1].offset;

  // ---- shapes: rough.js nodes, outlines first, hachure fills as separate nodes ----------------

  function ro(o = {}) {
    return Object.assign({ roughness: 1.2, bowing: 1, stroke: D.INK, strokeWidth: 5, seed: seed++ }, o);
  }
  function shape(fn, o) {
    o = o || {};
    if (!o.fill || o.fillStyle === 'solid') return [fn(ro(o))];
    const outline = fn(ro(Object.assign({}, o, { fill: undefined })));
    const fill = fn(ro(Object.assign({ hachureGap: 11, fillWeight: 3, hachureAngle: -41 }, o, { stroke: 'none' })));
    return [outline, fill];
  }
  D.line = (x1, y1, x2, y2, o) => shape((r) => rc.line(x1, y1, x2, y2, r), o);
  D.ellipse = (cx, cy, w, h, o) => shape((r) => rc.ellipse(cx, cy, w, h, r), o);
  D.circle = (cx, cy, d, o) => shape((r) => rc.circle(cx, cy, d, r), o);
  D.rect = (x, y, w, h, o) => shape((r) => rc.rectangle(x, y, w, h, r), o);
  D.poly = (pts, o) => shape((r) => rc.polygon(pts, r), o);
  D.curve = (pts, o) => shape((r) => rc.curve(pts, r), o);
  D.lines = (pts, o) => shape((r) => rc.linearPath(pts, r), o);
  D.path = (d, o) => shape((r) => rc.path(d, r), o);
  D.arc = (cx, cy, w, h, a0, a1, o) => shape((r) => rc.arc(cx, cy, w, h, a0, a1, false, r), o);
  D.dot = (cx, cy, d, color) => [mk('circle', { cx, cy, r: d / 2, fill: color || D.INK })];
  D.arrow = function (x1, y1, x2, y2, o = {}) {
    const a = Math.atan2(y2 - y1, x2 - x1);
    const h = o.head || 30;
    const p = (da) => [x2 - h * Math.cos(a + da), y2 - h * Math.sin(a + da)];
    return [D.line(x1, y1, x2, y2, o), D.lines([p(0.5), [x2, y2], p(-0.5)], o)];
  };
  // Group nodes and place them: translate to (x, y), scale s, rotate deg, mirror with flip.
  D.at = function (x, y, s, nodes, o = {}) {
    const g = mk('g', {
      transform: `translate(${x},${y}) rotate(${o.rotate || 0}) scale(${(o.flip ? -1 : 1) * s},${s})`,
    });
    nodes.flat(Infinity).forEach((n) => g.appendChild(n));
    return [g];
  };

  // ---- timed items ---------------------------------------------------------------------------

  // Draw nodes stroke by stroke from `at`, taking `dur` seconds; solid fills fade in afterwards.
  D.draw = function (at, dur, nodes) {
    const g = mk('g', {}, cur.g);
    nodes.flat(Infinity).forEach((n) => g.appendChild(n));
    const strokes = [];
    const fills = [];
    g.querySelectorAll('path, circle').forEach((p) => {
      const f = p.getAttribute('fill');
      if (p.tagName === 'circle' || (f && f !== 'none')) fills.push(p);
      else strokes.push(p);
    });
    const lens = strokes.map((p) => p.getTotalLength() + 1);
    lens.forEach((l, i) => strokes[i].setAttribute('stroke-dasharray', `${l} ${l}`));
    const total = lens.reduce((a, b) => a + b, 0);
    const it = { kind: 'draw', g, at, dur, strokes, lens, total, fills };
    cur.items.push(it);
    return it;
  };

  // Handwritten text revealed left to right. Lines split on "\n" are written one after another.
  // font: 'Hand' (Latin) or 'Tamil'; maxWidth shrinks the font until every line fits.
  D.write = function (at, x, y, str, o = {}) {
    let size = o.size || 64;
    const lines = str.split('\n');
    const font = o.font || 'Hand';
    if (o.maxWidth) {
      const probe = mk('text', { 'font-family': font, 'font-size': size }, cur.g);
      const widest = Math.max(...lines.map((l) => ((probe.textContent = l), probe.getBBox().width)));
      probe.remove();
      if (widest > o.maxWidth) size = Math.floor((size * o.maxWidth) / widest);
    }
    let t = at;
    const items = [];
    lines.forEach((line, i) => {
      const g = mk('g', o.rotate ? { transform: `rotate(${o.rotate},${x},${y})` } : {}, cur.g);
      const txt = mk('text', {
        x,
        y: y + i * size * (o.lineHeight || 1.12),
        'font-family': font,
        'font-size': size,
        fill: o.color || D.INK,
        'text-anchor': o.anchor || 'middle',
      }, g);
      txt.textContent = line;
      if (o.outline) {
        // thick outline behind the fill, for thumbnails
        txt.setAttribute('stroke', o.outline);
        txt.setAttribute('stroke-width', o.outlineWidth || 12);
        txt.setAttribute('stroke-linejoin', 'round');
        txt.setAttribute('paint-order', 'stroke');
      }
      const bb = txt.getBBox();
      const id = `clip${uid++}`;
      const cp = mk('clipPath', { id }, defs);
      const rect = mk('rect', { x: bb.x - 8, y: bb.y - 12, width: 0, height: bb.height + 24 }, cp);
      g.setAttribute('clip-path', `url(#${id})`);
      const dur = o.dur ? o.dur / lines.length : clamp(line.length * 0.05, 0.3, 1.4);
      const it = { kind: 'write', g, at: t, dur, rect, bb, txt };
      cur.items.push(it);
      items.push(it);
      t += dur + 0.05;
    });
    return items;
  };

  // A picture (an illustration file) painted in row by row behind the pen, then slowly zooming in.
  // o: rows (4), zoom (0.04: how much it grows over zoomDur), zoomDur (8 s).
  D.loading = [];
  D.image = function (at, dur, href, x, y, w, h, o = {}) {
    const rows = o.rows || 4;
    const id = `clip${uid++}`;
    const cp = mk('clipPath', { id }, defs);
    const bands = [];
    for (let i = 0; i < rows; i++) bands.push(mk('rect', { x, y: y + (i * h) / rows - 1, width: 0, height: h / rows + 2 }, cp));
    const g = mk('g', { 'clip-path': `url(#${id})` }, cur.g);
    const inner = mk('g', {}, g);
    mk('image', { href, x, y, width: w, height: h, preserveAspectRatio: 'xMidYMid slice' }, inner);
    D.loading.push(new Promise((done) => {
      const im = new Image();
      im.onload = im.onerror = done;
      im.src = href;
    }));
    const it = { kind: 'image', g, inner, at, dur, x, y, w, h, rows, bands, zoom: o.zoom ?? 0.04, zoomDur: o.zoomDur || 8 };
    cur.items.push(it);
    return it;
  };
  // Resolves once every picture has loaded (render.mjs waits for it before the first frame).
  D.ready = () => Promise.all(D.loading);

  // Appear with a small bounce (stamps, bursts).
  D.pop = function (at, nodes, o = {}) {
    const outer = mk('g', {}, cur.g);
    const g = mk('g', {}, outer);
    nodes.flat(Infinity).forEach((n) => g.appendChild(n));
    const bb = g.getBBox();
    const it = { kind: 'pop', g: outer, inner: g, at, dur: o.dur || 0.3, cx: bb.x + bb.width / 2, cy: bb.y + bb.height / 2 };
    cur.items.push(it);
    return it;
  };

  // A stamp: rotated rough box with bold text, popped in.
  D.stamp = function (at, x, y, str, o = {}) {
    const size = o.size || 60;
    const color = o.color || D.RED;
    const txt = mk('text', { x, y: y + size * 0.35, 'font-family': 'Hand', 'font-size': size, fill: color, 'text-anchor': 'middle' });
    txt.textContent = str;
    // measure in place, then build the box around it
    cur.g.appendChild(txt);
    const bb = txt.getBBox();
    txt.remove();
    const box = D.rect(bb.x - 22, bb.y - 10, bb.width + 44, bb.height + 20, { stroke: color, strokeWidth: 7, roughness: 1.6 });
    const g = mk('g', { transform: `rotate(${o.rotate ?? -8},${x},${y})` });
    [box, txt].flat(Infinity).forEach((n) => g.appendChild(n));
    return D.pop(at, [g]);
  };

  // ---- rendering -----------------------------------------------------------------------------

  function pose(it, t) {
    const q = clamp((t - it.at) / it.dur);
    if (it.kind === 'draw') {
      const vis = ease(q) * it.total;
      let acc = 0;
      it.strokes.forEach((p, i) => {
        const l = it.lens[i];
        const shown = clamp(vis - acc, 0, l);
        p.setAttribute('stroke-dashoffset', `${l - shown}`);
        acc += l;
      });
      const f = clamp((t - it.at - it.dur) / 0.25);
      it.fills.forEach((p) => p.setAttribute('opacity', `${f}`));
    } else if (it.kind === 'write') {
      it.rect.setAttribute('width', `${(it.bb.width + 16) * q}`);
    } else if (it.kind === 'image') {
      // rows are painted one after another, alternating direction
      const p = q * it.rows;
      it.bands.forEach((b, i) => {
        const f = clamp(p - i);
        b.setAttribute('width', `${it.w * f}`);
        b.setAttribute('x', `${i % 2 === 0 ? it.x : it.x + it.w * (1 - f)}`);
      });
      const s = 1 + it.zoom * clamp((t - it.at) / it.zoomDur);
      const cx = it.x + it.w / 2;
      const cy = it.y + it.h / 2;
      it.inner.setAttribute('transform', `translate(${cx},${cy}) scale(${s}) translate(${-cx},${-cy})`);
    } else if (it.kind === 'pop') {
      const s = q <= 0 ? 0 : 1 + 0.35 * Math.sin(Math.PI * q) * (1 - q);
      it.g.setAttribute('opacity', q <= 0 ? '0' : '1');
      it.inner.setAttribute('transform', `translate(${it.cx},${it.cy}) scale(${q <= 0 ? 0.01 : s}) translate(${-it.cx},${-it.cy})`);
    }
  }

  function tip(it, t) {
    const q = clamp((t - it.at) / it.dur);
    if (it.kind === 'draw') {
      let vis = ease(q) * it.total;
      for (let i = 0; i < it.strokes.length; i++) {
        if (vis <= it.lens[i] || i === it.strokes.length - 1) {
          const p = it.strokes[i];
          const pt = p.getPointAtLength(Math.min(vis, it.lens[i] - 1));
          return new DOMPoint(pt.x, pt.y).matrixTransform(p.getCTM());
        }
        vis -= it.lens[i];
      }
    } else if (it.kind === 'write') {
      const x = it.bb.x + it.bb.width * q;
      const y = it.bb.y + it.bb.height * 0.72;
      return new DOMPoint(x, y).matrixTransform(it.txt.getCTM());
    } else if (it.kind === 'image') {
      const p = Math.min(q * it.rows, it.rows - 1e-6);
      const i = Math.floor(p);
      const f = p - i;
      const x = i % 2 === 0 ? it.x + it.w * f : it.x + it.w * (1 - f);
      return new DOMPoint(x, it.y + ((i + 0.5) * it.h) / it.rows).matrixTransform(it.g.getCTM());
    }
    return null;
  }

  // Every item must finish before the camera leaves its scene: squeeze any that would run over,
  // and warn about any that start too late to be seen properly (those need moving in the scene).
  let finalized = false;
  function finalize() {
    finalized = true;
    scenes.forEach((s, i) => {
      const leave = i + 1 < scenes.length ? scenes[i + 1].t0 - PAN - 0.08 : Infinity;
      s.items.forEach((it) => {
        // solid fills fade in for 0.25 s after a drawing's strokes, and must be done before the pan
        const fade = it.kind === 'draw' && it.fills.length ? 0.25 : 0;
        if (it.at > leave - 0.3 - fade) {
          console.warn(`scene ${i + 1}: item at ${it.at.toFixed(2)}s starts too close to the pan at ${leave.toFixed(2)}s`);
          it.at = leave - 0.3 - fade;
        }
        if (it.at + it.dur + fade > leave) it.dur = Math.max(0.2, leave - fade - it.at);
      });
    });
  }

  D.renderAt = function (t) {
    if (!finalized) finalize();
    let k = 0;
    for (let i = 0; i < scenes.length; i++) if (scenes[i].t0 <= t) k = i;
    let cam = k;
    let panning = false;
    if (k + 1 < scenes.length && t > scenes[k + 1].t0 - PAN) {
      cam = k + ease(clamp((t - (scenes[k + 1].t0 - PAN)) / PAN));
      panning = true;
    }
    camera.setAttribute('transform', `translate(${-cam * D.W},0)`);
    let active = null;
    scenes.forEach((s, i) => {
      const near = i === k || i === k + 1;
      s.g.setAttribute('display', near ? 'inline' : 'none');
      if (!near) return;
      s.items.forEach((it) => {
        pose(it, t);
        if (it.kind !== 'pop' && t >= it.at && t < it.at + it.dur && (!active || it.at >= active.at)) active = it;
      });
    });
    const pt = !panning && active ? tip(active, t) : null;
    if (pt) {
      penG.setAttribute('opacity', '1');
      penG.setAttribute('transform', `translate(${pt.x},${pt.y})`);
    } else {
      penG.setAttribute('opacity', '0');
    }
  };

  // The moment each scene is complete, just before the camera leaves it (for review stills).
  D.sceneEnds = () =>
    scenes.map((s, i) => (i + 1 < scenes.length ? scenes[i + 1].t0 - PAN - 0.05 : D.duration() - 0.05));

  D.tail = 0; // extra seconds after the voiceover ends (an end card)
  D.duration = () => window.TIMING.total + D.tail;
})();
