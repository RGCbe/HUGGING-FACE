// Doodle library: characters and props built from engine primitives.
// Every function returns nodes in local coordinates around (0, 0); place them with D.at(x, y, s, nodes).
(function () {
  const D = window.Doodle;
  const L = (D.lib = {});

  // A cartoon emu facing right. pose: 'stand' | 'eat' (head down to the ground) | 'run'.
  L.emu = function (pose = 'stand', o = {}) {
    const n = [];
    n.push(D.ellipse(0, 0, 230, 150, { fill: o.fill || D.BROWN, fillWeight: 2.5, hachureGap: 14 }));
    n.push(D.curve([[-110, -10], [-150, -30], [-135, 15], [-105, 35]])); // tail feathers
    [[-40, -20], [0, 10], [40, -25], [-10, -45], [55, 15]].forEach(([x, y]) =>
      n.push(D.curve([[x, y], [x + 18, y + 12], [x + 34, y + 4]], { strokeWidth: 3 })));
    let head;
    if (pose === 'eat') {
      n.push(D.curve([[80, -30], [150, -20], [175, 60], [165, 120]], { strokeWidth: 9 }));
      head = [160, 140];
      n.push(D.circle(head[0], head[1], 44));
      n.push(D.poly([[175, 150], [200, 175], [168, 162]]));
      n.push(D.dot(150, 132, 12));
    } else {
      n.push(D.curve([[75, -40], [105, -110], [100, -180], [118, -225]], { strokeWidth: 9 }));
      head = [125, -232];
      n.push(D.circle(head[0], head[1], 48));
      n.push(D.poly([[146, -240], [188, -230], [146, -222]]));
      n.push(D.circle(130, -242, 20, { strokeWidth: 3 }));
      n.push(D.dot(134, -242, 9));
    }
    const legs = pose === 'run'
      ? [[[-20, 60], [-75, 130], [-130, 170]], [[25, 60], [70, 140], [60, 225]]]
      : [[[-25, 60], [-38, 150], [-20, 228]], [[30, 60], [44, 150], [62, 228]]];
    legs.forEach(([a, b, c]) => {
      n.push(D.lines([a, b, c], { strokeWidth: 6 }));
      n.push(D.lines([[c[0] - 26, c[1] + 6], c, [c[0] + 30, c[1] + 4]], { strokeWidth: 5 }));
      n.push(D.line(c[0], c[1], c[0] + 8, c[1] + 18, { strokeWidth: 5 }));
    });
    if (pose === 'run') {
      [[-260, -40], [-290, 10], [-250, 60]].forEach(([x, y]) => n.push(D.line(x, y, x + 90, y, { strokeWidth: 4 })));
    }
    return n;
  };

  // Australian slouch hat on a head centred at (0, 0) of diameter ~70.
  L.slouchHat = (color) => [
    D.ellipse(0, -28, 140, 26, { fill: color || '#a07a45', fillWeight: 2 }),
    D.path('M -38 -32 Q -36 -78 0 -80 Q 36 -78 38 -32', { fill: color || '#a07a45', fillWeight: 2 }),
    D.line(-70, -30, -52, -70, { strokeWidth: 5 }),
  ];

  // Stick person. hat: 'slouch' | 'straw' | 'top' | 'cap' | null. torso colour optional.
  L.person = function (o = {}) {
    const n = [];
    n.push(D.circle(0, -175, 70));
    n.push(D.dot(-12, -180, 9), D.dot(14, -180, 9));
    n.push(D.arc(0, -168, 34, 22, 0.2, Math.PI - 0.2, { strokeWidth: 3 }));
    if (o.torso) n.push(D.rect(-32, -138, 64, 105, { fill: o.torso, fillWeight: 2.5, hachureGap: 9 }));
    else n.push(D.line(0, -140, 0, -30));
    if (o.tie) n.push(D.poly([[0, -136], [9, -120], [0, -78], [-9, -120]], { fill: D.RED, fillStyle: 'solid' }));
    const arms = o.arms || [[[-30, -120], [-75, -70]], [[30, -120], [80, -80]]];
    arms.forEach(([a, b]) => n.push(D.line(a[0], a[1], b[0], b[1], { strokeWidth: 6 })));
    n.push(D.lines([[-15, -33], [-38, 60]], { strokeWidth: 6 }), D.lines([[15, -33], [38, 60]], { strokeWidth: 6 }));
    if (o.hat === 'slouch') n.push(D.at(0, -175, 1, L.slouchHat()));
    if (o.hat === 'straw') n.push(D.at(0, -175, 1, [
      D.ellipse(0, -26, 150, 30, { fill: D.YELLOW, fillWeight: 2 }),
      D.rect(-36, -62, 72, 34, { fill: D.YELLOW, fillWeight: 2 }),
    ]));
    if (o.hat === 'top') n.push(D.at(0, -175, 1, [
      D.ellipse(0, -30, 110, 18),
      D.rect(-32, -110, 64, 78, { fill: D.INK, fillWeight: 3, hachureGap: 6 }),
    ]));
    if (o.hat === 'helmet') n.push(D.at(0, -175, 1, [D.path('M -48 -18 Q -40 -70 0 -70 Q 40 -70 48 -18 Z', { fill: '#5c7a3a' })]));
    return n;
  };

  // Lewis machine gun pointing right, about 360 wide.
  L.gun = () => [
    D.rect(-120, -24, 260, 48, { fill: '#495057', fillWeight: 2.5, hachureGap: 8 }),
    D.rect(140, -10, 70, 20),
    D.ellipse(-20, -40, 120, 30, { fill: '#343a40', fillWeight: 2.5, hachureGap: 7 }),
    D.poly([[-120, -20], [-190, -10], [-200, 40], [-150, 40], [-120, 20]], { fill: D.BROWN, fillWeight: 2 }),
    D.lines([[110, 22], [80, 110]], { strokeWidth: 5 }),
    D.lines([[120, 22], [150, 110]], { strokeWidth: 5 }),
    D.line(-60, 24, -60, 55, { strokeWidth: 5 }),
  ];

  // Little bang/flash at a gun muzzle.
  L.flash = () => [D.poly([[0, 0], [40, -30], [30, -5], [80, -10], [35, 10], [60, 40], [20, 18], [5, 45]], { stroke: D.ORANGE, fill: D.YELLOW, fillStyle: 'solid' })];

  L.wheat = (h = 170) => {
    const n = [D.curve([[0, 0], [6, -h * 0.5], [0, -h]], { stroke: D.YELLOW, strokeWidth: 5 })];
    for (let i = 0; i < 5; i++) {
      const y = -h + 10 + i * 18;
      n.push(D.ellipse(-12, y, 22, 12, { stroke: D.YELLOW, strokeWidth: 4 }));
      n.push(D.ellipse(12, y + 8, 22, 12, { stroke: D.YELLOW, strokeWidth: 4 }));
    }
    return n;
  };
  L.wheatField = (count = 6, gap = 60) => {
    const n = [];
    for (let i = 0; i < count; i++) n.push(D.at(i * gap, (i % 2) * 12, 1, L.wheat(150 + (i % 3) * 20)));
    return n;
  };

  // Fence of posts and rails; hole = index of a broken section (or -1).
  L.fence = (posts = 6, gap = 110, hole = -1) => {
    const n = [];
    for (let i = 0; i < posts; i++) n.push(D.rect(i * gap - 9, -150, 18, 150, { fill: D.BROWN, fillWeight: 2 }));
    for (let i = 0; i < posts - 1; i++) {
      const x0 = i * gap + 9;
      const x1 = (i + 1) * gap - 9;
      if (i === hole) {
        n.push(D.lines([[x0, -110], [x0 + 25, -95], [x0 + 15, -80]], { strokeWidth: 4 }));
        n.push(D.lines([[x1, -55], [x1 - 22, -40], [x1 - 10, -30]], { strokeWidth: 4 }));
      } else {
        n.push(D.line(x0, -110, x1, -110, { strokeWidth: 6 }), D.line(x0, -50, x1, -50, { strokeWidth: 6 }));
      }
    }
    return n;
  };

  L.rabbit = () => [
    D.ellipse(0, 0, 90, 60, { fill: D.GREY, fillWeight: 2 }),
    D.circle(48, -30, 46),
    D.ellipse(40, -78, 16, 54),
    D.ellipse(60, -76, 16, 54),
    D.dot(58, -34, 7),
    D.circle(-46, -6, 18),
  ];

  // Outline of Australia (rough lon/lat points, equirectangular), Western Australia border and
  // an optional marked place. Width about 760.
  const AUS = [[142.5, -10.7], [141.6, -13.0], [141.6, -15.6], [140.8, -17.4], [139.4, -17.4], [137.6, -16.2],
    [135.6, -14.9], [136.8, -12.4], [135.0, -12.0], [132.6, -11.4], [130.8, -12.4], [129.5, -14.9],
    [128.1, -15.0], [126.6, -13.9], [124.8, -15.2], [123.4, -16.6], [122.2, -17.9], [120.0, -19.7],
    [117.0, -20.6], [114.2, -21.8], [113.6, -24.2], [114.1, -26.6], [114.6, -28.7], [115.7, -31.9],
    [115.1, -34.3], [117.9, -35.1], [121.9, -33.9], [124.0, -32.9], [126.2, -32.3], [129.0, -31.7],
    [131.2, -31.5], [133.6, -32.1], [135.5, -34.6], [136.6, -33.6], [137.8, -32.6], [138.1, -34.4],
    [138.5, -35.6], [139.7, -37.1], [140.9, -38.1], [143.5, -38.8], [144.9, -37.9], [146.3, -39.1],
    [148.1, -37.8], [149.9, -37.5], [150.2, -35.7], [151.2, -33.9], [152.5, -32.1], [153.6, -28.6],
    [153.1, -25.2], [151.3, -23.8], [149.2, -21.1], [146.8, -19.3], [145.8, -17.0], [145.3, -15.0],
    [143.6, -14.0], [143.0, -11.5]];
  const proj = ([lon, lat]) => [(lon - 133.5) * 17.4, (lat + 25.5) * -19.2];
  L.australia = (o = {}) => {
    const n = [D.poly(AUS.map(proj), { strokeWidth: 6, roughness: 0.8 })];
    n.push(D.poly([[144.6, -40.7], [148.3, -40.9], [148.0, -43.2], [146.8, -43.6], [145.2, -42.2]].map(proj),
      { strokeWidth: 5, roughness: 0.8 }));
    if (o.wa) {
      n.push(D.poly([[129.0, -14.9], [128.1, -15.0], [126.6, -13.9], [124.8, -15.2], [123.4, -16.6], [122.2, -17.9],
        [120.0, -19.7], [117.0, -20.6], [114.2, -21.8], [113.6, -24.2], [114.1, -26.6], [114.6, -28.7], [115.7, -31.9],
        [115.1, -34.3], [117.9, -35.1], [121.9, -33.9], [124.0, -32.9], [126.2, -32.3], [129.0, -31.7]].map(proj),
      { stroke: 'none', fill: D.ORANGE, fillWeight: 2.5, hachureGap: 12 }));
      n.push(D.line(...proj([129.0, -14.9]), ...proj([129.0, -31.7]), { strokeWidth: 5 }));
    }
    return n;
  };
  L.place = (lon, lat) => proj([lon, lat]);

  L.calendar = (accent) => [
    D.rect(-110, -100, 220, 200, { fill: '#ffffff', fillStyle: 'solid' }),
    D.rect(-110, -100, 220, 55, { fill: accent || D.RED, fillStyle: 'solid' }),
    D.circle(-55, -100, 22), D.circle(55, -100, 22),
  ];

  L.board = (w = 520, h = 340) => [
    D.rect(-w / 2, -h / 2, w, h, { strokeWidth: 6 }),
    D.lines([[-w / 3, h / 2], [-w / 2.4, h / 2 + 110]], { strokeWidth: 6 }),
    D.lines([[w / 3, h / 2], [w / 2.4, h / 2 + 110]], { strokeWidth: 6 }),
  ];

  L.newspaper = () => {
    const n = [D.rect(-170, -120, 340, 240, { fill: '#ffffff', fillStyle: 'solid' })];
    n.push(D.rect(-150, -100, 300, 60, { strokeWidth: 4 }));
    for (let i = 0; i < 4; i++) n.push(D.line(-150, -20 + i * 32, i % 2 ? 40 : 150, -20 + i * 32, { strokeWidth: 3 }));
    n.push(D.rect(60, -24, 90, 110, { strokeWidth: 3 }));
    return n;
  };

  L.face = (mood = 'happy', d = 120) => {
    const n = [D.circle(0, 0, d, { fill: D.YELLOW, fillWeight: 2 }), D.dot(-d * 0.18, -d * 0.12, d * 0.09), D.dot(d * 0.18, -d * 0.12, d * 0.09)];
    if (mood === 'sad') n.push(D.arc(0, d * 0.3, d * 0.45, d * 0.3, Math.PI + 0.3, 2 * Math.PI - 0.3, { strokeWidth: 4 }));
    else if (mood === 'laugh') n.push(D.path(`M ${-d * 0.25} ${d * 0.08} Q 0 ${d * 0.45} ${d * 0.25} ${d * 0.08} Z`, { fill: D.RED, fillStyle: 'solid' }));
    else n.push(D.arc(0, d * 0.05, d * 0.45, d * 0.35, 0.3, Math.PI - 0.3, { strokeWidth: 4 }));
    return n;
  };

  L.dam = () => [
    D.ellipse(0, 0, 520, 150, { stroke: D.BLUE, fill: D.BLUE, fillWeight: 2, hachureGap: 16, hachureAngle: 0 }),
    D.rect(-280, -10, 40, 60, { fill: D.BROWN, fillWeight: 2 }),
    D.curve([[-120, -10], [-100, -18], [-80, -10]], { stroke: D.BLUE, strokeWidth: 3 }),
    D.curve([[60, 20], [80, 12], [100, 20]], { stroke: D.BLUE, strokeWidth: 3 }),
  ];

  L.treads = () => [
    D.rect(-170, 0, 340, 90, { fill: D.GREY, fillWeight: 2.5, hachureGap: 9 }),
    D.circle(-120, 45, 60), D.circle(-40, 45, 60), D.circle(40, 45, 60), D.circle(120, 45, 60),
  ];

  L.parliament = () => {
    const n = [D.poly([[-260, -150], [0, -260], [260, -150]], { fill: D.GREY, fillWeight: 2 })];
    n.push(D.rect(-260, -150, 520, 30));
    for (let i = 0; i < 6; i++) n.push(D.rect(-225 + i * 85, -120, 30, 190));
    n.push(D.rect(-280, 70, 560, 30), D.rect(-300, 100, 600, 30));
    n.push(D.line(0, -260, 0, -350, { strokeWidth: 5 }), D.rect(0, -350, 70, 44, { fill: D.BLUE, fillWeight: 2 }));
    return n;
  };

  L.trophy = () => [
    D.path('M -90 -150 L 90 -150 Q 90 -20 0 0 Q -90 -20 -90 -150 Z', { fill: D.YELLOW, fillWeight: 3, hachureGap: 9 }),
    D.arc(-95, -100, 70, 80, Math.PI / 2, 3 * Math.PI / 2, { strokeWidth: 6 }),
    D.arc(95, -100, 70, 80, -Math.PI / 2, Math.PI / 2, { strokeWidth: 6 }),
    D.rect(-18, 0, 36, 60),
    D.rect(-80, 60, 160, 40, { fill: D.BROWN, fillWeight: 2 }),
  ];

  L.coin = () => [D.circle(0, 0, 90, { fill: D.YELLOW, fillWeight: 2.5 }), D.circle(0, 0, 66, { strokeWidth: 3 })];

  L.bubble = (w = 420, h = 170, tail = 'left') => {
    const tx = tail === 'left' ? -w * 0.25 : w * 0.25;
    return [
      D.ellipse(0, 0, w, h, { fill: '#ffffff', fillStyle: 'solid' }),
      D.lines([[tx - 20, h * 0.42], [tx - (tail === 'left' ? 70 : -70), h * 0.9], [tx + 30, h * 0.4]]),
    ];
  };

  L.comment = (w = 600) => [
    D.rect(-w / 2, -130, w, 230, { strokeWidth: 6 }),
    D.lines([[-w / 3, 100], [-w / 3 - 40, 170], [-w / 3 + 60, 100]], { strokeWidth: 6 }),
  ];

  L.check = (c) => [D.lines([[-30, 0], [-8, 26], [36, -30]], { stroke: c || D.GREEN, strokeWidth: 9 })];
  L.cross = (c, s = 60) => [D.line(-s, -s, s, s, { stroke: c || D.RED, strokeWidth: 10 }), D.line(s, -s, -s, s, { stroke: c || D.RED, strokeWidth: 10 })];
  L.burst = (r = 150, c) => {
    const pts = [];
    for (let i = 0; i < 18; i++) {
      const a = (i / 18) * Math.PI * 2;
      const rr = i % 2 ? r * 0.62 : r;
      pts.push([Math.cos(a) * rr * 1.45, Math.sin(a) * rr]);
    }
    return [D.poly(pts, { stroke: c || D.RED, strokeWidth: 6, fill: D.YELLOW, fillWeight: 2, hachureGap: 12 })];
  };
  L.bullet = () => [D.path('M -14 30 L -14 -10 Q 0 -45 14 -10 L 14 30 Z', { fill: D.YELLOW, fillWeight: 2, hachureGap: 6 })];
  L.paper = (w = 300, h = 380) => {
    const n = [D.rect(-w / 2, -h / 2, w, h, { fill: '#ffffff', fillStyle: 'solid' })];
    for (let i = 0; i < 5; i++) n.push(D.line(-w / 2 + 30, -h / 2 + 120 + i * 45, w / 2 - 30 - (i % 2) * 60, -h / 2 + 120 + i * 45, { strokeWidth: 3 }));
    return n;
  };
  L.notebook = (w = 760, h = 520) => {
    const n = [D.rect(-w / 2, -h / 2, w, h, { strokeWidth: 6 })];
    for (let i = 0; i < 7; i++) n.push(D.circle(-w / 2 + 70 + i * ((w - 140) / 6), -h / 2, 30, { strokeWidth: 4 }));
    return n;
  };
  L.medal = () => [D.lines([[-30, -90], [0, -20], [30, -90]], { stroke: D.BLUE, strokeWidth: 8 }), D.circle(0, 0, 60, { fill: D.YELLOW, fillWeight: 2 })];
})();
