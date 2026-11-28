// People and things for children's stories, in the same style as doodles.js.
// People stand with their feet at y = 60 and are about 200 (kids) or 280 (adults) tall at scale 1;
// things are centred on (0, 0) and about 200 wide. Place them with D.at(x, y, s, nodes).
(function () {
  const D = window.Doodle;
  const L = D.lib;
  const SKIN = '#f3c99b';
  const HAIR = '#2b2b2b';

  // Eyes and a mouth for a head centred at (cx, cy) of diameter d.
  // mood: happy | sad | angry | surprised | laugh | calm | worried
  L.features = function (cx, cy, d, mood = 'happy') {
    const n = [D.dot(cx - d * 0.18, cy - d * 0.06, d * 0.1), D.dot(cx + d * 0.18, cy - d * 0.06, d * 0.1)];
    const my = cy + d * 0.2;
    const w = d * 0.36;
    if (mood === 'sad' || mood === 'worried') n.push(D.arc(cx, my + d * 0.1, w, d * 0.22, Math.PI + 0.35, 2 * Math.PI - 0.35, { strokeWidth: 3 }));
    else if (mood === 'angry') n.push(D.line(cx - w / 2, my + 4, cx + w / 2, my + 4, { strokeWidth: 3 }));
    else if (mood === 'surprised') n.push(D.circle(cx, my + 4, d * 0.16, { strokeWidth: 3 }));
    else if (mood === 'laugh') n.push(D.path(`M ${cx - w / 2} ${my - 2} Q ${cx} ${my + d * 0.32} ${cx + w / 2} ${my - 2} Z`, { fill: D.RED, fillStyle: 'solid', strokeWidth: 3 }));
    else if (mood === 'calm') n.push(D.arc(cx, my - 2, w * 0.8, d * 0.14, 0.3, Math.PI - 0.3, { strokeWidth: 3 }));
    else n.push(D.arc(cx, my - 4, w, d * 0.26, 0.25, Math.PI - 0.25, { strokeWidth: 3 }));
    if (mood === 'angry') {
      n.push(D.line(cx - d * 0.3, cy - d * 0.26, cx - d * 0.08, cy - d * 0.16, { strokeWidth: 4 }));
      n.push(D.line(cx + d * 0.3, cy - d * 0.26, cx + d * 0.08, cy - d * 0.16, { strokeWidth: 4 }));
    }
    if (mood === 'worried') {
      n.push(D.line(cx - d * 0.3, cy - d * 0.17, cx - d * 0.08, cy - d * 0.25, { strokeWidth: 3 }));
      n.push(D.line(cx + d * 0.3, cy - d * 0.17, cx + d * 0.08, cy - d * 0.25, { strokeWidth: 3 }));
    }
    return n;
  };

  // Arm poses, as [shoulder, hand] pairs relative to the shoulders at (+-sx, sy).
  function arms(pose, sx, sy, len) {
    const p = {
      down: [[-sx - len * 0.35, sy + len * 0.9], [sx + len * 0.35, sy + len * 0.9]],
      up: [[-sx - len * 0.5, sy - len * 0.85], [sx + len * 0.5, sy - len * 0.85]],
      wave: [[-sx - len * 0.35, sy + len * 0.9], [sx + len * 0.55, sy - len * 0.8]],
      point: [[-sx - len * 0.35, sy + len * 0.9], [sx + len, sy - len * 0.1]],
      give: [[-sx + len * 0.2, sy + len * 0.6], [sx + len * 0.95, sy + len * 0.15]],
      hips: [[-sx - len * 0.5, sy + len * 0.45], [sx + len * 0.5, sy + len * 0.45]],
      pray: [[-6, sy + len * 0.15], [6, sy + len * 0.15]],
    }[pose || 'down'];
    return [D.line(-sx, sy, p[0][0], p[0][1], { strokeWidth: 6 }), D.line(sx, sy, p[1][0], p[1][1], { strokeWidth: 6 })];
  }

  // A child. o: {girl, shirt, mood, arms: down|up|wave|point|give|hips|pray}
  L.kid = function (o = {}) {
    const n = [];
    const shirt = o.shirt || (o.girl ? '#f783ac' : '#74c0fc');
    n.push(...arms(o.arms, 24, -95, 62));
    if (o.girl) n.push(D.poly([[-24, -105], [24, -105], [44, -20], [-44, -20]], { fill: shirt, fillWeight: 2.5, hachureGap: 9 }));
    else n.push(D.rect(-28, -105, 56, 70, { fill: shirt, fillWeight: 2.5, hachureGap: 9 }), D.rect(-28, -40, 56, 22, { fill: '#495057', fillWeight: 2 }));
    n.push(D.lines([[-13, -20], [-20, 55]], { strokeWidth: 6 }), D.lines([[13, -20], [20, 55]], { strokeWidth: 6 }));
    n.push(D.circle(0, -150, 86, { fill: SKIN, fillStyle: 'solid' }));
    if (o.girl) {
      n.push(D.path('M -43 -152 Q -40 -200 0 -197 Q 40 -200 43 -152 Q 20 -178 -43 -152 Z', { fill: HAIR, fillStyle: 'solid' }));
      n.push(D.circle(-50, -132, 26, { fill: HAIR, fillStyle: 'solid' }), D.circle(50, -132, 26, { fill: HAIR, fillStyle: 'solid' }));
    } else {
      n.push(D.path('M -42 -158 Q -38 -198 0 -196 Q 38 -198 42 -158 Q 10 -176 -42 -158 Z', { fill: HAIR, fillStyle: 'solid' }));
    }
    n.push(...L.features(0, -146, 86, o.mood));
    return n;
  };

  // A grown-up. kind: grandma | grandpa | mom | dad | teacher | man | woman
  // o: {kind, mood, arms, color}
  L.adult = function (o = {}) {
    const kind = o.kind || 'man';
    const n = [];
    const woman = ['grandma', 'mom', 'teacher', 'woman'].includes(kind);
    const old = kind === 'grandma' || kind === 'grandpa';
    const color = o.color || { grandma: '#9c36b5', grandpa: '#ffffff', mom: '#e64980', dad: '#1c7ed6', teacher: '#2f9e44', man: '#f08c00', woman: '#f76707' }[kind];
    n.push(...arms(o.arms, 30, -150, 80));
    if (woman) {
      n.push(D.poly([[-30, -165], [30, -165], [52, 55], [-52, 55]], { fill: color, fillWeight: 2.5, hachureGap: 10 }));
      n.push(D.line(-30, -160, 40, -40, { stroke: D.YELLOW, strokeWidth: 6 }));
    } else {
      n.push(D.rect(-32, -165, 64, 110, { fill: color, fillWeight: 2.5, hachureGap: 10 }));
      if (kind === 'grandpa') n.push(D.rect(-34, -55, 68, 110, { strokeWidth: 5 }));
      else n.push(D.lines([[-15, -55], [-24, 58]], { strokeWidth: 7 }), D.lines([[15, -55], [24, 58]], { strokeWidth: 7 }));
    }
    const hair = old ? '#adb5bd' : HAIR;
    n.push(D.circle(0, -205, 80, { fill: SKIN, fillStyle: 'solid' }));
    if (woman) {
      n.push(D.path('M -40 -205 Q -40 -250 0 -248 Q 40 -250 40 -205 Q 10 -232 -40 -205 Z', { fill: hair, fillStyle: 'solid' }));
      if (kind === 'grandma') n.push(D.circle(0, -258, 34, { fill: hair, fillStyle: 'solid' }));
      else n.push(D.path('M 34 -222 Q 56 -170 40 -120 L 28 -150 Z', { fill: hair, fillStyle: 'solid' }));
      n.push(D.dot(0, -228, 8, D.RED));
    } else if (kind === 'grandpa') {
      n.push(D.path('M -40 -196 Q -46 -226 -28 -236', { stroke: hair, strokeWidth: 8 }), D.path('M 40 -196 Q 46 -226 28 -236', { stroke: hair, strokeWidth: 8 }));
    } else {
      n.push(D.path('M -40 -210 Q -36 -250 0 -248 Q 36 -250 40 -210 Q 10 -228 -40 -210 Z', { fill: hair, fillStyle: 'solid' }));
    }
    n.push(...L.features(0, -200, 80, o.mood));
    if (kind === 'grandpa' || kind === 'dad') n.push(D.path('M -20 -184 Q 0 -194 20 -184', { stroke: hair, strokeWidth: 6 }));
    if (old || kind === 'teacher') n.push(D.circle(-15, -206, 26, { strokeWidth: 3 }), D.circle(15, -206, 26, { strokeWidth: 3 }), D.line(-2, -206, 2, -206, { strokeWidth: 3 }));
    if (kind === 'grandpa') n.push(D.line(-95, -60, -110, 60, { stroke: D.BROWN, strokeWidth: 7 }));
    return n;
  };

  // A wise old poet sitting cross-legged, writing on a palm leaf (for the kural board).
  L.sage = () => [
    D.ellipse(0, 20, 220, 70, { fill: '#ffffff', fillStyle: 'solid' }),
    D.poly([[-45, -120], [45, -120], [70, 10], [-70, 10]], { fill: '#fff4e6', fillStyle: 'solid' }),
    D.circle(0, -165, 78, { fill: SKIN, fillStyle: 'solid' }),
    D.circle(0, -218, 34, { fill: '#e9ecef', fillStyle: 'solid' }),
    D.poly([[-30, -150], [30, -150], [16, -70], [0, -55], [-16, -70]], { fill: '#e9ecef', fillStyle: 'solid' }),
    D.arc(-16, -172, 16, 8, 0.2, Math.PI - 0.2, { strokeWidth: 3 }), D.arc(16, -172, 16, 8, 0.2, Math.PI - 0.2, { strokeWidth: 3 }),
    D.rect(-10, -60, 120, 26, { fill: '#e9c46a', fillWeight: 2, hachureGap: 6 }),
    D.line(30, -95, 60, -60, { strokeWidth: 4 }),
    D.line(-40, -100, -5, -55, { strokeWidth: 6 }), D.line(40, -100, 30, -70, { strokeWidth: 6 }),
  ];

  // ---- nature ----
  L.tree = (o = {}) => {
    const n = [D.rect(-22, -40, 44, 140, { fill: D.BROWN, fillWeight: 2.5, hachureGap: 8 })];
    n.push(D.path('M -110 -40 Q -150 -110 -90 -150 Q -80 -230 0 -220 Q 80 -235 95 -150 Q 155 -110 110 -40 Z', { fill: o.color || D.GREEN, fillWeight: 2.5, hachureGap: 13 }));
    (o.fruit ? [[-60, -100], [10, -160], [60, -80], [-10, -70]] : []).forEach(([x, y]) => n.push(D.circle(x, y, 34, { fill: o.fruit === 'green' ? '#8ce99a' : D.YELLOW, fillStyle: 'solid' })));
    return n;
  };
  L.mango = (o = {}) => [
    D.path('M 0 -70 Q 70 -60 60 20 Q 45 80 -10 75 Q -65 60 -55 0 Q -45 -60 0 -70 Z', { fill: o.ripe === false ? '#8ce99a' : '#ffa94d', fillWeight: 2.5, hachureGap: 9 }),
    D.line(0, -70, 8, -95, { stroke: D.BROWN, strokeWidth: 5 }),
    D.ellipse(28, -98, 44, 18, { fill: D.GREEN, fillStyle: 'solid' }),
  ];
  L.flower = (o = {}) => {
    const n = [D.line(0, 0, 0, 120, { stroke: D.GREEN, strokeWidth: 6 })];
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      n.push(D.circle(Math.cos(a) * 34, Math.sin(a) * 34, 44, { fill: o.color || '#f06595', fillStyle: 'solid' }));
    }
    n.push(D.circle(0, 0, 36, { fill: D.YELLOW, fillStyle: 'solid' }));
    return n;
  };
  L.lotus = () => [
    D.path('M 0 -90 Q 40 -40 0 30 Q -40 -40 0 -90 Z', { fill: '#faa2c1', fillStyle: 'solid' }),
    D.path('M -20 25 Q -100 -10 -95 -60 Q -40 -40 -10 20 Z', { fill: '#fcc2d7', fillStyle: 'solid' }),
    D.path('M 20 25 Q 100 -10 95 -60 Q 40 -40 10 20 Z', { fill: '#fcc2d7', fillStyle: 'solid' }),
    D.ellipse(0, 40, 220, 40, { fill: D.GREEN, fillWeight: 2, hachureGap: 10 }),
  ];
  L.sun = () => {
    const n = [D.circle(0, 0, 110, { fill: D.YELLOW, fillStyle: 'solid', stroke: D.ORANGE })];
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * Math.PI * 2;
      n.push(D.line(Math.cos(a) * 72, Math.sin(a) * 72, Math.cos(a) * 110, Math.sin(a) * 110, { stroke: D.ORANGE, strokeWidth: 5 }));
    }
    return n;
  };
  L.moon = () => [D.path('M 20 -80 Q -70 -60 -60 10 Q -40 80 40 70 Q -20 40 -15 -10 Q -10 -60 20 -80 Z', { fill: D.YELLOW, fillStyle: 'solid' })];
  L.star = (c) => [D.poly([[0, -60], [16, -18], [60, -18], [24, 8], [38, 52], [0, 26], [-38, 52], [-24, 8], [-60, -18], [-16, -18]], { fill: c || D.YELLOW, fillStyle: 'solid', stroke: D.ORANGE })];
  L.cloud = (o = {}) => {
    const n = [D.path('M -110 30 Q -140 -20 -80 -35 Q -60 -90 0 -70 Q 50 -105 85 -45 Q 140 -40 115 30 Z', { fill: '#ffffff', fillStyle: 'solid', stroke: o.rain ? D.GREY : D.INK })];
    if (o.rain) [[-70, 60], [-20, 80], [30, 60], [80, 85]].forEach(([x, y]) => n.push(D.line(x, y, x - 12, y + 40, { stroke: D.BLUE, strokeWidth: 5 })));
    return n;
  };
  L.river = () => [0, 40, 80].map((y) => D.curve([[-200, y], [-120, y - 20], [-40, y], [40, y - 20], [120, y], [200, y - 20]], { stroke: D.BLUE, strokeWidth: 6 }));
  L.hill = () => [D.path('M -220 60 Q -120 -120 0 -40 Q 90 -150 220 60 Z', { fill: '#69db7c', fillWeight: 2, hachureGap: 14 })];

  // ---- animals ----
  L.bird = (c) => [
    D.ellipse(0, 0, 110, 70, { fill: c || '#4dabf7', fillStyle: 'solid' }),
    D.circle(52, -30, 50, { fill: c || '#4dabf7', fillStyle: 'solid' }),
    D.poly([[74, -34], [104, -26], [74, -20]], { fill: D.YELLOW, fillStyle: 'solid' }),
    D.dot(58, -36, 9),
    D.path('M -20 -10 Q 0 -60 30 -10', { strokeWidth: 4 }),
    D.line(-10, 34, -14, 62, { strokeWidth: 4 }), D.line(14, 34, 18, 62, { strokeWidth: 4 }),
  ];
  L.dog = () => [
    D.ellipse(0, 0, 170, 90, { fill: '#e9c46a', fillWeight: 2, hachureGap: 10 }),
    D.circle(90, -50, 80, { fill: '#e9c46a', fillStyle: 'solid' }),
    D.ellipse(70, -70, 26, 56, { fill: D.BROWN, fillStyle: 'solid' }),
    D.dot(104, -56, 10), D.dot(128, -44, 12),
    D.line(-50, 40, -55, 95, { strokeWidth: 6 }), D.line(-20, 40, -20, 95, { strokeWidth: 6 }),
    D.line(30, 40, 30, 95, { strokeWidth: 6 }), D.line(55, 40, 60, 95, { strokeWidth: 6 }),
    D.curve([[-85, -10], [-115, -40], [-120, -70]], { strokeWidth: 6 }),
  ];
  L.cat = () => [
    D.ellipse(0, 10, 130, 90, { fill: D.GREY, fillWeight: 2, hachureGap: 9 }),
    D.circle(0, -60, 76, { fill: '#ced4da', fillStyle: 'solid' }),
    D.poly([[-34, -86], [-28, -128], [-8, -96]], { fill: '#ced4da', fillStyle: 'solid' }),
    D.poly([[34, -86], [28, -128], [8, -96]], { fill: '#ced4da', fillStyle: 'solid' }),
    D.dot(-14, -64, 9), D.dot(14, -64, 9),
    D.line(-40, -50, -70, -54, { strokeWidth: 2 }), D.line(40, -50, 70, -54, { strokeWidth: 2 }),
    D.curve([[60, 30], [100, 10], [95, -40]], { strokeWidth: 6 }),
  ];
  L.cow = () => [
    D.rect(-120, -60, 220, 110, { fill: '#ffffff', fillStyle: 'solid' }),
    D.ellipse(-50, -20, 60, 40, { fill: D.INK, fillStyle: 'solid' }), D.ellipse(40, 10, 50, 34, { fill: D.INK, fillStyle: 'solid' }),
    D.rect(100, -110, 80, 90, { fill: '#ffffff', fillStyle: 'solid' }),
    D.line(110, -110, 95, -140, { strokeWidth: 5 }), D.line(170, -110, 185, -140, { strokeWidth: 5 }),
    D.dot(125, -80, 10), D.dot(155, -80, 10), D.ellipse(140, -35, 60, 26, { fill: '#ffc9c9', fillStyle: 'solid' }),
    D.line(-100, 50, -100, 120, { strokeWidth: 7 }), D.line(-60, 50, -60, 120, { strokeWidth: 7 }),
    D.line(40, 50, 40, 120, { strokeWidth: 7 }), D.line(80, 50, 80, 120, { strokeWidth: 7 }),
    D.curve([[-120, -50], [-150, 0], [-140, 50]], { strokeWidth: 4 }),
  ];
  L.fish = (c) => [
    D.ellipse(0, 0, 150, 80, { fill: c || D.ORANGE, fillStyle: 'solid' }),
    D.poly([[-70, 0], [-120, -40], [-120, 40]], { fill: c || D.ORANGE, fillStyle: 'solid' }),
    D.dot(40, -10, 10),
  ];
  L.elephant = () => [
    D.ellipse(0, 0, 260, 170, { fill: '#adb5bd', fillWeight: 2, hachureGap: 12 }),
    D.circle(130, -50, 120, { fill: '#adb5bd', fillStyle: 'solid' }),
    D.ellipse(95, -45, 70, 100, { fill: '#ced4da', fillStyle: 'solid' }),
    D.curve([[180, -30], [205, 40], [185, 110], [205, 125]], { strokeWidth: 16, stroke: '#868e96' }),
    D.dot(150, -70, 12),
    ...[-90, -40, 40, 90].map((x) => D.rect(x - 18, 60, 36, 70, { fill: '#adb5bd', fillStyle: 'solid' })),
  ];
  L.peacock = () => {
    const n = [];
    for (let i = 0; i < 7; i++) {
      const a = Math.PI + (i / 6) * Math.PI;
      n.push(D.ellipse(Math.cos(a) * 110, Math.sin(a) * 110, 60, 90, { fill: '#38d9a9', fillStyle: 'solid' }));
      n.push(D.circle(Math.cos(a) * 125, Math.sin(a) * 125, 24, { fill: D.BLUE, fillStyle: 'solid' }));
    }
    n.push(D.ellipse(0, 0, 70, 120, { fill: '#1c7ed6', fillStyle: 'solid' }), D.circle(0, -80, 46, { fill: '#1c7ed6', fillStyle: 'solid' }), D.dot(10, -84, 8));
    return n;
  };

  // ---- places ----
  L.house = (c) => [
    D.rect(-120, -80, 240, 170, { fill: c || '#ffd8a8', fillWeight: 2, hachureGap: 12 }),
    D.poly([[-150, -80], [0, -190], [150, -80]], { fill: D.RED, fillWeight: 2.5, hachureGap: 10 }),
    D.rect(-30, 0, 60, 90, { fill: D.BROWN, fillStyle: 'solid' }),
    D.rect(55, -50, 45, 45, { fill: '#a5d8ff', fillStyle: 'solid' }),
  ];
  L.school = () => [
    D.rect(-200, -110, 400, 210, { fill: '#ffe066', fillWeight: 2, hachureGap: 12 }),
    D.poly([[-220, -110], [0, -190], [220, -110]], { fill: D.ORANGE, fillWeight: 2, hachureGap: 10 }),
    D.rect(-35, 10, 70, 90, { fill: D.BROWN, fillStyle: 'solid' }),
    ...[-150, -90, 90, 150].map((x) => D.rect(x - 22, -70, 44, 44, { fill: '#a5d8ff', fillStyle: 'solid' })),
    D.line(0, -190, 0, -270, { strokeWidth: 5 }), D.poly([[0, -270], [60, -252], [0, -234]], { fill: D.GREEN, fillStyle: 'solid' }),
  ];
  L.temple = () => [
    D.rect(-150, 0, 300, 110, { fill: '#ffd8a8', fillWeight: 2, hachureGap: 12 }),
    D.poly([[-120, 0], [120, 0], [95, -70], [-95, -70]], { fill: '#ffc078', fillStyle: 'solid' }),
    D.poly([[-95, -70], [95, -70], [70, -140], [-70, -140]], { fill: '#ffa94d', fillStyle: 'solid' }),
    D.poly([[-70, -140], [70, -140], [45, -200], [-45, -200]], { fill: '#ff922b', fillStyle: 'solid' }),
    D.ellipse(0, -215, 110, 36, { fill: D.YELLOW, fillStyle: 'solid' }),
    D.path('M -30 110 L -30 50 Q 0 20 30 50 L 30 110', { strokeWidth: 5 }),
  ];
  L.shop = () => [
    D.rect(-150, -60, 300, 160, { fill: '#e7f5ff', fillStyle: 'solid' }),
    D.path('M -170 -60 L -150 -130 L 150 -130 L 170 -60 Z', { fill: D.RED, fillWeight: 2, hachureGap: 12 }),
    D.rect(-130, 20, 260, 30, { fill: D.BROWN, fillStyle: 'solid' }),
    ...[-80, 0, 80].map((x) => D.circle(x, 0, 40, { fill: [D.ORANGE, D.YELLOW, '#8ce99a'][(x + 80) / 80], fillStyle: 'solid' })),
  ];
  L.well = () => [
    D.ellipse(0, -10, 220, 50, { fill: '#a5d8ff', fillStyle: 'solid' }),
    D.path('M -110 -10 L -110 80 Q 0 120 110 80 L 110 -10', { fill: '#ced4da', fillWeight: 2, hachureGap: 10 }),
    D.line(-90, -10, -90, -150, { strokeWidth: 7 }), D.line(90, -10, 90, -150, { strokeWidth: 7 }),
    D.line(-100, -150, 100, -150, { strokeWidth: 7 }), D.line(0, -150, 0, -60, { strokeWidth: 3 }),
    D.rect(-20, -60, 40, 40, { fill: D.BROWN, fillStyle: 'solid' }),
  ];

  // ---- things ----
  L.book = (c) => [
    D.path('M 0 -60 Q -60 -85 -130 -60 L -130 60 Q -60 35 0 60 Z', { fill: '#ffffff', fillStyle: 'solid' }),
    D.path('M 0 -60 Q 60 -85 130 -60 L 130 60 Q 60 35 0 60 Z', { fill: '#ffffff', fillStyle: 'solid' }),
    D.line(0, -60, 0, 60, { strokeWidth: 4 }),
    ...[-30, -5, 20].map((y) => D.line(-105, y - 10, -25, y, { stroke: c || D.GREY, strokeWidth: 3 })),
    ...[-30, -5, 20].map((y) => D.line(25, y, 105, y - 10, { stroke: c || D.GREY, strokeWidth: 3 })),
  ];
  L.palmleaf = (w = 900, h = 300) => [
    D.path(`M ${-w / 2} 0 Q ${-w / 2} ${-h / 2} ${-w / 2 + 60} ${-h / 2} L ${w / 2 - 60} ${-h / 2} Q ${w / 2} ${-h / 2} ${w / 2} 0 Q ${w / 2} ${h / 2} ${w / 2 - 60} ${h / 2} L ${-w / 2 + 60} ${h / 2} Q ${-w / 2} ${h / 2} ${-w / 2} 0 Z`,
      { fill: '#fff3bf', fillStyle: 'solid', stroke: '#c49a2c', strokeWidth: 6 }),
    D.circle(-w / 2 + 40, 0, 18, { strokeWidth: 3, stroke: '#c49a2c' }),
  ];
  L.lamp = () => [
    D.path('M -90 0 Q -80 60 0 60 Q 80 60 90 0 Z', { fill: '#e8590c', fillWeight: 2.5, hachureGap: 8 }),
    D.path('M 70 0 Q 110 -6 120 -20', { strokeWidth: 5 }),
    D.path('M 118 -24 Q 100 -70 120 -110 Q 145 -70 122 -24 Z', { fill: D.YELLOW, fillStyle: 'solid', stroke: D.ORANGE }),
  ];
  L.ball = (c) => [D.circle(0, 0, 110, { fill: c || D.RED, fillWeight: 2.5, hachureGap: 10 }), D.arc(0, 0, 110, 50, 0, Math.PI, { strokeWidth: 4 }), D.line(0, -55, 0, 55, { strokeWidth: 4 })];
  L.kite = (c) => [
    D.poly([[0, -100], [70, 0], [0, 110], [-70, 0]], { fill: c || D.BLUE, fillWeight: 2.5, hachureGap: 10 }),
    D.line(0, -100, 0, 110, { strokeWidth: 3 }), D.line(-70, 0, 70, 0, { strokeWidth: 3 }),
    D.curve([[0, 110], [20, 150], [-15, 190], [10, 230]], { strokeWidth: 3 }),
  ];
  L.bag = (c) => [
    D.rect(-80, -70, 160, 170, { fill: c || D.BLUE, fillWeight: 2.5, hachureGap: 9 }),
    D.path('M -40 -70 Q -40 -120 0 -120 Q 40 -120 40 -70', { strokeWidth: 6 }),
    D.rect(-55, 10, 110, 55, { strokeWidth: 4 }),
  ];
  L.pencil = () => [
    D.rect(-120, -16, 200, 32, { fill: D.YELLOW, fillStyle: 'solid' }),
    D.poly([[80, -16], [125, 0], [80, 16]], { fill: SKIN, fillStyle: 'solid' }),
    D.rect(-140, -16, 22, 32, { fill: '#ffa8a8', fillStyle: 'solid' }),
  ];
  L.plate = () => [
    D.ellipse(0, 0, 260, 90, { fill: '#ffffff', fillStyle: 'solid' }),
    D.ellipse(0, -8, 150, 44, { fill: '#fff9db', fillStyle: 'solid' }),
    D.ellipse(-40, -16, 50, 22, { fill: D.ORANGE, fillStyle: 'solid' }), D.ellipse(40, -14, 50, 22, { fill: D.GREEN, fillStyle: 'solid' }),
  ];
  L.leaf = () => [D.path('M -150 20 Q -60 -70 150 -20 Q 60 70 -150 20 Z', { fill: '#51cf66', fillWeight: 2, hachureGap: 12 }), D.line(-150, 20, 150, -20, { strokeWidth: 3 })];
  L.pot = () => [
    D.path('M -30 -90 L 30 -90 L 25 -60 Q 100 -40 90 20 Q 80 90 0 90 Q -80 90 -90 20 Q -100 -40 -25 -60 Z', { fill: '#e8590c', fillWeight: 2.5, hachureGap: 9 }),
    D.ellipse(0, -90, 80, 20, { fill: '#a5d8ff', fillStyle: 'solid' }),
  ];
  L.gift = () => [
    D.rect(-90, -50, 180, 140, { fill: '#f783ac', fillWeight: 2.5, hachureGap: 10 }),
    D.rect(-100, -80, 200, 40, { fill: '#f783ac', fillStyle: 'solid' }),
    D.rect(-14, -80, 28, 170, { fill: D.YELLOW, fillStyle: 'solid' }),
    D.ellipse(-30, -100, 60, 36, { stroke: D.ORANGE, strokeWidth: 5 }), D.ellipse(30, -100, 60, 36, { stroke: D.ORANGE, strokeWidth: 5 }),
  ];
  L.heart = (c) => [D.path('M 0 70 Q -110 0 -90 -55 Q -60 -100 0 -50 Q 60 -100 90 -55 Q 110 0 0 70 Z', { fill: c || D.RED, fillStyle: 'solid' })];
  L.clock = () => [D.circle(0, 0, 200, { fill: '#ffffff', fillStyle: 'solid' }), D.line(0, 0, 0, -70, { strokeWidth: 6 }), D.line(0, 0, 50, 20, { strokeWidth: 6 }), D.dot(0, 0, 14)];
  L.phone = () => [D.rect(-55, -100, 110, 200, { fill: '#343a40', fillStyle: 'solid' }), D.rect(-45, -85, 90, 160, { fill: '#a5d8ff', fillStyle: 'solid' })];
  L.bicycle = () => [
    D.circle(-90, 40, 120), D.circle(90, 40, 120),
    D.lines([[-90, 40], [-20, -50], [60, -50], [90, 40]], { stroke: D.RED, strokeWidth: 6 }),
    D.lines([[-20, -50], [0, 40], [60, -50]], { stroke: D.RED, strokeWidth: 6 }),
    D.line(-35, -70, 0, -70, { strokeWidth: 7 }), D.line(60, -50, 50, -90, { strokeWidth: 5 }), D.line(35, -95, 70, -90, { strokeWidth: 6 }),
  ];
  L.boat = () => [
    D.path('M -150 0 L 150 0 L 100 60 L -100 60 Z', { fill: D.BROWN, fillWeight: 2.5, hachureGap: 9 }),
    D.line(0, 0, 0, -180, { strokeWidth: 6 }), D.poly([[8, -170], [110, -20], [8, -20]], { fill: '#ffffff', fillStyle: 'solid' }),
  ];
  L.bench = () => [
    D.rect(-150, -30, 300, 28, { fill: D.BROWN, fillStyle: 'solid' }),
    D.line(-120, -2, -120, 60, { strokeWidth: 8 }), D.line(120, -2, 120, 60, { strokeWidth: 8 }),
  ];
  L.money = () => [
    D.rect(-120, -60, 240, 120, { fill: '#b2f2bb', fillWeight: 2, hachureGap: 12 }),
    D.circle(0, 0, 70, { strokeWidth: 4 }),
  ];
  L.bulb = () => [
    D.path('M -30 40 Q -80 -10 -60 -60 Q -30 -110 0 -110 Q 30 -110 60 -60 Q 80 -10 30 40 Z', { fill: D.YELLOW, fillStyle: 'solid' }),
    D.rect(-30, 40, 60, 40, { fill: D.GREY, fillStyle: 'solid' }),
    ...[-1, 0, 1].map((k) => D.line(k * 100, -150 + Math.abs(k) * 40, k * 125, -185 + Math.abs(k) * 40, { stroke: D.ORANGE, strokeWidth: 5 })),
  ];
})();
