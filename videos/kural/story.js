// Scenes for a Super Kural Short, built from window.DATA (written by make.py from a story spec).
// Portrait layout: the scene space is 1080 x 1250, between the title and the captions.
//
// DATA: {n, next, kural: {line1, line2, translit, chapter_en, chapter_ta}, kid,
//        lines: [{section, board: [item, ...]}], intro_section, says_section, meaning_section,
//        lesson_section, outro_section, lesson_short, lesson_draw}
// Sections, in order: the hook (story line 1), the fixed intro, the rest of the story, the fixed
// "Thiruvalluvar says" line, the meaning, the lesson, the fixed goodbye.
// An item is one of
//   {draw: NAME, at: SLOT, mood?, arms?, color?, flip?, scale?, cue?}  a person or a thing
//   {text: "...", at: SLOT, color?, size?, cue?}                       handwritten words
//   {bubble: "...", at: SLOT, cue?}                                    a speech bubble over SLOT
//   {stamp: "...", at: SLOT, color?, cue?}
//   {arrow: [SLOT, SLOT], color?, cue?}
// cue is a word or phrase from that line's narration; the item starts when it is spoken.
(function () {
  const D = Doodle;
  const L = D.lib;
  const S = window.DATA;
  const LEAD = 0.2;
  const GROUND = 1000;

  const SLOTS = {
    left: [250, GROUND], center: [540, GROUND], right: [830, GROUND],
    'top-left': [250, 300], top: [540, 150], 'top-right': [830, 300],
    'middle-left': [250, 600], middle: [540, 560], 'middle-right': [830, 600],
    bottom: [540, 1170],
  };
  const COLORS = {
    red: D.RED, blue: D.BLUE, green: D.GREEN, orange: D.ORANGE, yellow: D.YELLOW, brown: D.BROWN,
    grey: D.GREY, pink: '#f06595', purple: '#9c36b5', black: D.INK,
  };
  const PEOPLE = {
    kid: (o) => L.kid(o), boy: (o) => L.kid(o), girl: (o) => L.kid(Object.assign({ girl: true }, o)),
    grandma: (o) => L.adult(Object.assign({ kind: 'grandma' }, o)),
    grandpa: (o) => L.adult(Object.assign({ kind: 'grandpa' }, o)),
    mom: (o) => L.adult(Object.assign({ kind: 'mom' }, o)), dad: (o) => L.adult(Object.assign({ kind: 'dad' }, o)),
    teacher: (o) => L.adult(Object.assign({ kind: 'teacher' }, o)),
    man: (o) => L.adult(Object.assign({ kind: 'man' }, o)), woman: (o) => L.adult(Object.assign({ kind: 'woman' }, o)),
    sage: () => L.sage(),
  };
  const SCALE = { kid: 1.8, boy: 1.8, girl: 1.8, sage: 1.2 };
  const BIG = ['tree', 'house', 'school', 'temple', 'shop', 'well', 'elephant', 'hill', 'river', 'boat', 'bicycle', 'cow'];
  const color = (c) => COLORS[c] || c;

  // Nodes measured once, so every drawing can stand on the ground or sit centred in its slot.
  function measure(nodes) {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    nodes.flat(Infinity).forEach((x) => g.appendChild(x.cloneNode(true)));
    D.svg.appendChild(g);
    const bb = g.getBBox();
    g.remove();
    return bb;
  }

  function figure(it) {
    const name = it.draw;
    const o = { mood: it.mood, arms: it.arms, color: color(it.color), shirt: color(it.color) };
    if (PEOPLE[name]) return { nodes: PEOPLE[name](o), scale: it.scale || SCALE[name] || 1.55, person: true };
    if (!L[name]) throw new Error(`unknown drawing "${name}"`);
    const arg = name === 'tree' ? { fruit: it.fruit, color: color(it.color) }
      : name === 'mango' ? { ripe: it.ripe !== false }
        : name === 'cloud' ? { rain: !!it.rain }
          : name === 'flower' ? { color: color(it.color) } : color(it.color);
    return { nodes: L[name](arg), scale: it.scale || (BIG.includes(name) ? 1.15 : 1), person: false };
  }

  function slot(name) {
    if (Array.isArray(name)) return name;
    if (!SLOTS[name]) throw new Error(`unknown place "${name}"`);
    return SLOTS[name];
  }

  function wrap(str, max) {
    const out = [];
    let cur = '';
    str.split(/\s+/).forEach((w) => {
      if (cur && (cur + ' ' + w).length > max) {
        out.push(cur);
        cur = w;
      } else cur = cur ? cur + ' ' + w : w;
    });
    if (cur) out.push(cur);
    return out.join('\n');
  }

  function place(it, at) {
    const [x, y] = slot(it.at || 'center');
    if (it.draw) {
      const f = figure(it);
      const bb = measure(f.nodes);
      const s = f.scale;
      const ground = y >= GROUND;
      const tx = x - (bb.x + bb.width / 2) * s * (it.flip ? -1 : 1);
      const ty = ground ? y - (bb.y + bb.height) * s : y - (bb.y + bb.height / 2) * s;
      D.draw(at, f.person ? 1.1 : 0.8, D.at(tx, ty, s, f.nodes, { flip: it.flip }));
    } else if (it.text) {
      const side = x !== 540;
      const size = it.size || (side ? 60 : 78);
      D.write(at, x, y, wrap(it.text, side ? 12 : 20), { size, color: color(it.color) || D.INK, maxWidth: side ? 440 : 1000 });
    } else if (it.bubble) {
      const bx = Math.min(840, Math.max(240, x));
      D.draw(at, 0.5, D.at(bx, 400, 1, L.bubble(440, 190, bx > 540 ? 'right' : 'left')));
      D.write(at + 0.4, bx, 400 - 10, wrap(it.bubble, 14), { size: 50, maxWidth: 380, lineHeight: 1.0 });
    } else if (it.stamp) {
      D.stamp(at, x, y, it.stamp, { size: 60, color: color(it.color) || D.RED, rotate: x > 540 ? 7 : -7 });
    } else if (it.arrow) {
      const [a, b] = it.arrow.map(slot);
      const y0 = (p) => (p[1] >= GROUND ? GROUND - 260 : p[1]);
      const dir = Math.sign(b[0] - a[0]) || 1;
      D.draw(at, 0.5, D.arrow(a[0] + dir * 110, y0(a), b[0] - dir * 110, y0(b), { stroke: color(it.color) || D.ORANGE }));
    } else {
      throw new Error(`item needs draw, text, bubble, stamp or arrow: ${JSON.stringify(it)}`);
    }
  }

  // Items with a cue start on that word; the others share out the time that is left. The first
  // board fills within its first two seconds, so the Short never opens on an empty page.
  function board(section, items, quick) {
    const sec = window.TIMING.sections[section - 1];
    const free = items.filter((it) => !it.cue);
    const step = Math.min(1.2, Math.max(0.5, (sec.duration - 0.6) / Math.max(1, free.length)));
    let k = 0;
    items.forEach((it, j) => {
      let at = it.cue ? D.cue(section, it.cue) : sec.offset + 0.1 + step * k++;
      if (quick) at = Math.min(at, sec.offset + 0.05 + 0.45 * j);
      place(it, at);
    });
  }
  const scene = (section, build) => D.scene(Math.max(0, D.sectionStart(section) - LEAD), build);

  // The hook, then the series intro, then the rest of the story: one board per line.
  D.scene(0, () => board(S.lines[0].section, S.lines[0].board, true));
  scene(S.intro_section, () => {
    const t0 = D.sectionStart(S.intro_section);
    place({ draw: S.kid || 'girl', at: 'left', mood: 'laugh', arms: 'wave' }, t0);
    place({ bubble: 'Hello friends!', at: 'left' }, t0 + 0.2);
    D.write(D.cue(S.intro_section, 'Super'), 700, 760, 'SUPER\nKURAL', { size: 120, color: D.ORANGE, dur: 0.8 });
    D.stamp(t0 + 0.9, 760, 1060, `KURAL ${S.n}`, { size: 64, rotate: -6 });
  });
  S.lines.slice(1).forEach((line) => scene(line.section, () => board(line.section, line.board)));

  // The kural itself: the couplet in Tamil on a palm leaf, with the poet.
  scene(S.says_section, () => {
    const t0 = D.sectionStart(S.says_section);
    D.write(t0, 540, 80, `Kural ${S.n}`, { size: 96, color: D.ORANGE, dur: 0.5 });
    D.write(t0 + 0.4, 540, 160, S.kural.chapter_en, { size: 48, color: D.GREY, maxWidth: 1000, dur: 0.5 });
    D.write(t0 + 0.7, 540, 228, S.kural.chapter_ta, { size: 46, color: D.GREY, font: 'Tamil', maxWidth: 1000, dur: 0.5 });
    D.draw(t0 + 0.3, 0.7, D.at(540, 470, 1, L.palmleaf(1000, 330)));
    const m = D.sectionStart(S.meaning_section);
    D.write(Math.max(t0 + 1.0, m - 1.6), 540, 452, S.kural.line1, { size: 66, font: 'Tamil', maxWidth: 900, dur: 1.5 });
    D.write(Math.max(t0 + 2.6, m), 540, 552, S.kural.line2, { size: 66, font: 'Tamil', maxWidth: 900, dur: 1.5 });
    D.write(m + 1.8, 540, 705, S.kural.translit.split(' / ').join('\n'), { size: 42, color: D.GREY, maxWidth: 1000, dur: 1.2 });
    place({ draw: 'sage', at: [230, 1220], scale: 1.15 }, t0 + 0.2);
    place({ draw: S.kid || 'girl', at: [850, 1220], mood: 'happy', flip: true, scale: 1.4 }, m + 0.8);
  });

  // Today's lesson and goodbye.
  scene(S.lesson_section, () => {
    const t0 = D.sectionStart(S.lesson_section);
    D.write(t0, 540, 80, "Today's lesson", { size: 80, color: D.ORANGE, dur: 0.5 });
    place({ draw: S.lesson_draw || 'star', at: [540, 290], scale: 1.4 }, t0 + 0.3);
    D.write(t0 + 0.8, 540, 500, wrap(S.lesson_short, 18), { size: 84, color: D.INK, maxWidth: 1000 });
    place({ draw: S.kid || 'girl', at: 'left', mood: 'laugh', arms: 'wave' }, t0 + 1.2);
    const bye = D.sectionStart(S.outro_section);
    D.write(bye, 760, 860, 'See you\ntomorrow!', { size: 68, color: D.BLUE });
    D.write(bye + 1.0, 760, 1040, `Next: Kural ${S.next}`, { size: 52, color: D.GREY });
  });

  D.tail = 1.2;
})();
