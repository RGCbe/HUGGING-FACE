// Scenes for "The Emu War (1932)". Times come from timing.json via cue(section, "words").
(function () {
  const D = Doodle;
  const L = D.lib;
  const c = D.cue;
  const LEAD = 0.2; // a scene's board is in place this long before its first cue word

  const put = (x, y, s, nodes, o) => D.at(x, y, s, nodes, o);
  const draw = (at, dur, x, y, s, nodes, o) => D.draw(at, dur, put(x, y, s, nodes, o));
  const write = (at, x, y, str, o) => D.write(at, x, y, str, o);
  const scene = (t, build) => D.scene(Math.max(0, t - LEAD), build);

  const soldier = (o = {}) => L.person(Object.assign({ hat: 'slouch', torso: '#a8895a' }, o));
  const holdingGun = { arms: [[[-30, -120], [60, -80]], [[30, -120], [110, -85]]] };
  function soldierWithGun(at, x, y, s = 1) {
    draw(at, 1.0, x, y, s, soldier(holdingGun));
    draw(at + 0.9, 0.8, x + 190 * s, y - 75 * s, 0.7 * s, L.gun());
  }
  function calendar(at, x, y, month, day, year, s = 1) {
    draw(at, 0.7, x, y, s, L.calendar());
    write(at + 0.6, x, y - 60 * s, month, { size: 44 * s, color: '#ffffff', dur: 0.3 });
    write(at + 0.8, x, y + 40 * s, day, { size: 100 * s, dur: 0.3 });
    if (year) write(at + 1.0, x, y + 88 * s, year, { size: 36 * s, color: D.GREY, dur: 0.3 });
  }
  function herd(at, x, y, s, count, step = 0.3, gap = 150, dur = 0.6) {
    for (let i = 0; i < count; i++) {
      draw(at + i * step, dur, x + i * gap, y + (i % 2) * 30, s, L.emu(i % 3 === 2 ? 'eat' : 'stand'), { flip: i % 2 === 1 });
    }
  }

  // 1. Hook
  D.scene(0, () => {
    D.stamp(c(1, 'real history'), 1560, 190, 'TRUE STORY', { size: 56, rotate: 7 });
    write(c(1, 'nineteen thirty-two'), 330, 210, '1932', { size: 150, color: D.ORANGE });
    soldierWithGun(c(1, 'army'), 380, 760, 1.25);
    write(c(1, 'declared war'), 960, 600, 'VS', { size: 130, color: D.RED });
    draw(c(1, 'birds'), 1.1, 1430, 560, 0.95, L.emu());
    draw(c(1, 'machine guns'), 0.3, 780, 640, 0.9, L.flash());
    write(c(1, 'what happened'), 1250, 330, '?', { size: 200, color: D.RED, dur: 0.4 });
  });

  // 2. Greeting and what the video covers
  scene(D.sectionStart(2), () => {
    draw(c(2, 'Hello'), 0.6, 400, 250, 1, L.bubble(500, 190));
    write(c(2, 'Hello') + 0.4, 400, 272, 'Hello friends!', { size: 72 });
    write(c(2, "I'm Manoj"), 400, 470, "I'm Manoj", { size: 60, color: D.GREY });
    draw(c(2, 'In this video'), 0.8, 1180, 520, 1, L.notebook(820, 560));
    write(c(2, 'Emu War'), 1180, 380, 'THE EMU WAR', { size: 92, color: D.ORANGE });
    write(c(2, 'started'), 860, 500, '1. How it started', { size: 62, anchor: 'start' });
    write(c(2, 'what happened'), 860, 600, '2. What happened', { size: 62, anchor: 'start' });
    write(c(2, 'who won'), 860, 700, '3. Who won?', { size: 62, anchor: 'start' });
    D.stamp(c(2, 'Every word is true'), 1520, 800, '100% TRUE', { size: 58 });
    write(c(2, 'sources'), 400, 700, 'Sources in the\ndescription', { size: 54, color: D.BLUE });
    draw(c(2, 'description'), 0.4, 0, 0, 1, D.arrow(400, 790, 400, 880, { stroke: D.BLUE }));
  });

  // 3a. Soldiers become farmers
  scene(D.sectionStart(3), () => {
    write(c(3, 'After the First'), 960, 150, 'World War 1 ends', { size: 84 });
    draw(c(3, 'Australia gave land'), 1.0, 1520, 760, 1, [
      D.rect(-230, -90, 460, 120, { fill: '#7cb342', fillWeight: 2, hachureGap: 14 }),
      D.line(-170, -90, -170, -260, { strokeWidth: 6 }),
      D.rect(-260, -330, 180, 80, { fill: '#ffffff', fillStyle: 'solid' }),
    ]);
    write(c(3, 'land') + 0.8, 1350, 488, 'FREE LAND', { size: 46 });
    draw(c(3, 'old soldiers'), 1.0, 340, 760, 1.2, soldier());
    draw(c(3, 'now go and farm'), 0.5, 0, 0, 1, D.arrow(500, 600, 720, 600, { stroke: D.ORANGE }));
    draw(c(3, 'farm'), 1.0, 880, 760, 1.2, L.person({ hat: 'straw', torso: '#74c0fc', arms: [[[-30, -120], [-70, -60]], [[30, -120], [90, -110]]] }));
    draw(c(3, 'farm') + 0.9, 0.5, 990, 640, 1, [D.line(0, 120, 0, -170, { strokeWidth: 6 }), D.lines([[-30, -170], [-30, -220]], { strokeWidth: 4 }), D.lines([[0, -170], [0, -225]], { strokeWidth: 4 }), D.lines([[30, -170], [30, -220]], { strokeWidth: 4 }), D.line(-30, -170, 30, -170, { strokeWidth: 5 })]);
    write(c(3, 'Nice idea'), 960, 300, 'Nice idea, right?', { size: 64, color: D.GREEN });
  });

  // 3b. Western Australia, Campion, wheat
  scene(c(3, 'Western Australia'), () => {
    draw(c(3, 'Western Australia'), 1.0, 640, 480, 0.95, L.australia());
    draw(c(3, 'Western Australia') + 1.0, 0.7, 640, 480, 0.95, L.australia({ wa: true }).slice(2));
    write(c(3, 'Western Australia') + 1.2, 420, 470, 'Western\nAustralia', { size: 52 });
    const [px, py] = L.place(118.3, -31.1);
    draw(c(3, 'Campion'), 0.3, 640 + px * 0.95, 480 + py * 0.95, 1, D.dot(0, 0, 26, D.RED));
    write(c(3, 'Campion') + 0.2, 640 + px * 0.95, 480 + py * 0.95 + 70, 'Campion', { size: 50, color: D.RED });
    draw(c(3, 'growing wheat'), 1.2, 1230, 860, 1, L.wheatField(7, 75));
    write(c(3, 'growing wheat') + 0.6, 1460, 560, 'Wheat farms', { size: 64 });
    write(c(3, 'until'), 1460, 300, 'until 1932...', { size: 84, color: D.RED });
  });

  // 4a. 20,000 emus arrive
  scene(D.sectionStart(4), () => {
    write(c(4, 'twenty thousand'), 960, 190, '20,000 EMUS', { size: 130, color: D.ORANGE });
    herd(c(4, 'twenty thousand') + 0.1, 280, 660, 0.55, 8, 0.1, 190, 0.35);
  });

  // 4b. What an emu is
  scene(c(4, "If you've never seen"), () => {
    draw(c(4, "If you've never seen"), 1.3, 640, 560, 1.15, L.emu());
    write(c(4, 'huge bird'), 980, 230, 'HUGE bird', { size: 76 });
    draw(c(4, 'huge bird') + 0.4, 0.4, 0, 0, 1, D.arrow(930, 260, 800, 330));
    write(c(4, "can't fly"), 300, 300, "can't fly", { size: 66, color: D.RED });
    draw(c(4, "can't fly") + 0.4, 0.4, 560, 560, 0.5, L.cross());
    draw(c(4, 'But it can run'), 1.0, 1450, 640, 0.75, L.emu('run'));
    write(c(4, 'Very fast'), 1450, 860, 'VERY FAST!', { size: 76, color: D.ORANGE });
  });

  // 4c. Damage and rabbits
  scene(c(4, 'These emus ate'), () => {
    draw(c(4, 'ate the wheat'), 1.0, 360, 900, 1, L.wheatField(4, 70));
    draw(c(4, 'These emus ate'), 1.1, 520, 560, 0.9, L.emu('eat'), { flip: true });
    write(c(4, 'ruined the crops'), 450, 200, 'crops ruined', { size: 66, color: D.RED });
    draw(c(4, 'broke big holes'), 1.2, 1000, 840, 1, L.fence(6, 120, 2));
    write(c(4, 'holes in the fences'), 1300, 470, 'holes!', { size: 70, color: D.RED });
    draw(c(4, 'rabbits'), 0.8, 1300, 780, 1, L.rabbit());
    write(c(4, 'Double trouble'), 1300, 220, 'DOUBLE TROUBLE', { size: 92, color: D.RED });
  });

  // 5a. Farmers ask for machine guns; the minister says yes
  scene(D.sectionStart(5), () => {
    draw(c(5, 'farmers do'), 1.0, 380, 760, 1.2, L.person({ hat: 'straw', torso: '#74c0fc' }));
    write(c(5, 'former soldiers'), 380, 880, '(former soldiers!)', { size: 46, color: D.GREY });
    draw(c(5, 'went to the government'), 0.7, 720, 300, 1, L.bubble(620, 230));
    write(c(5, 'we need'), 720, 285, 'We need', { size: 64 });
    write(c(5, 'machine guns'), 720, 355, 'MACHINE GUNS!', { size: 70, color: D.RED });
    draw(c(5, 'Defence Minister'), 1.0, 1480, 760, 1.2, L.person({ hat: 'top', torso: D.INK, tie: true }));
    write(c(5, 'Sir George Pearce'), 1480, 300, 'Sir George Pearce', { size: 56 });
    write(c(5, 'Sir George Pearce') + 0.5, 1480, 360, 'Defence Minister', { size: 44, color: D.GREY, dur: 0.5 });
    D.stamp(c(5, 'said yes'), 1150, 560, 'YES!', { size: 80, color: D.GREEN });
  });

  // 5b. What the army sent
  scene(c(5, 'The army sent'), () => {
    write(c(5, 'The army sent'), 960, 120, 'The army sent:', { size: 72 });
    draw(c(5, 'Major Meredith'), 0.8, 500, 430, 0.75, L.person({ hat: 'cap', torso: '#a8895a' }));
    draw(c(5, 'Major Meredith') + 0.6, 0.3, 500, 430, 0.75, [D.at(0, -175, 1, [D.path('M -42 -26 Q 0 -70 42 -26 Z', { fill: '#5c7a3a' }), D.line(-45, -26, 60, -26, { strokeWidth: 5 })])]);
    write(c(5, 'Major Meredith') + 0.3, 500, 520, 'Major Meredith', { size: 56 });
    draw(c(5, 'two soldiers'), 0.6, 1360, 430, 0.7, soldier());
    draw(c(5, 'two soldiers') + 0.4, 0.6, 1520, 430, 0.7, soldier(), { flip: true });
    write(c(5, 'two soldiers') + 0.4, 1440, 520, '2 soldiers', { size: 56 });
    draw(c(5, 'two Lewis'), 0.8, 500, 740, 0.75, L.gun());
    write(c(5, 'two Lewis') + 0.6, 500, 870, '2 Lewis machine guns', { size: 52 });
    for (let i = 0; i < 6; i++) draw(c(5, 'two Lewis') + 1.0 + i * 0.06, 0.15, 1290 + i * 60, 740, 1, L.bullet());
    write(c(5, 'ten thousand bullets'), 1440, 870, '10,000 bullets', { size: 60, color: D.ORANGE, dur: 0.6 });
  });

  // 5c. The plan
  scene(c(5, 'The plan was simple'), () => {
    draw(c(5, 'The plan was simple'), 0.9, 1130, 460, 1, L.board(700, 420));
    write(c(5, 'The plan was simple') + 0.5, 1130, 330, 'THE PLAN', { size: 76, color: D.BLUE });
    write(c(5, 'Shoot the emus'), 840, 440, '1. Shoot the emus', { size: 60, anchor: 'start' });
    write(c(5, 'Problem solved'), 840, 540, '2. Problem solved', { size: 60, anchor: 'start' });
    draw(c(5, 'Problem solved') + 0.7, 0.3, 1400, 520, 1, L.check());
    draw(c(5, 'manager'), 1.0, 380, 770, 1.2, L.person({ torso: '#495057', tie: true, arms: [[[-30, -120], [-70, -60]], [[30, -120], [150, -190]]] }));
    write(c(5, 'Monday meeting'), 380, 330, 'Monday meeting', { size: 54, color: D.GREY });
    D.stamp(c(5, 'Perfect on paper'), 1130, 840, 'PERFECT ON PAPER', { size: 60, color: D.ORANGE, rotate: -5 });
  });

  // 6a. Round 1 starts; emus scatter out of range
  scene(D.sectionStart(6), () => {
    calendar(c(6, 'November second'), 230, 260, 'NOV', '2', '1932');
    write(c(6, 'The war begins'), 960, 150, 'ROUND 1', { size: 110, color: D.RED });
    soldierWithGun(c(6, 'soldiers spot'), 300, 780, 1.1);
    herd(c(6, 'spot the emus'), 1230, 640, 0.42, 3, 0.25, 150);
    draw(c(6, 'guns ready'), 0.7, 0, 0, 1, D.arc(560, 680, 1000, 760, -0.75, 0.75, { stroke: D.GREY, strokeWidth: 4 }));
    write(c(6, 'guns ready') + 0.5, 900, 320, 'gun range', { size: 48, color: D.GREY });
    [[1250, 520, 1450, 380], [1400, 600, 1720, 560], [1300, 760, 1600, 860]].forEach(([a, b, x, y], i) =>
      draw(c(6, 'split into small groups') + i * 0.2, 0.4, 0, 0, 1, D.arrow(a, b, x, y, { stroke: D.ORANGE })));
    write(c(6, 'run out of range'), 1540, 300, 'OUT OF RANGE!', { size: 66, color: D.ORANGE });
    write(c(6, 'not in the'), 960, 920, "(that wasn't in the plan)", { size: 46, color: D.GREY });
  });

  // 6b. The dam, twelve emus, the jam
  scene(c(6, 'Two days later'), () => {
    write(c(6, 'Two days later'), 260, 130, '2 days later...', { size: 56, color: D.GREY });
    draw(c(6, 'gathered near a dam'), 1.0, 1300, 700, 1, L.dam());
    herd(c(6, 'gathered near a dam') + 0.8, 1110, 560, 0.3, 4, 0.15, 120);
    write(c(6, 'more than a thousand'), 1300, 400, '1,000+ emus', { size: 74 });
    write(c(6, 'perfect chance'), 960, 200, 'PERFECT CHANCE!', { size: 84, color: D.ORANGE });
    soldierWithGun(c(6, 'The army was ready'), 260, 800, 1.05);
    draw(c(6, 'started shooting'), 0.3, 650, 670, 0.9, L.flash());
    write(c(6, 'twelve'), 620, 380, 'only 12', { size: 80, color: D.RED });
    D.pop(c(6, 'gun jammed'), put(560, 600, 0.9, L.burst(140)));
    write(c(6, 'gun jammed') + 0.15, 560, 625, 'JAMMED!', { size: 70, color: D.RED, dur: 0.4 });
    write(c(6, 'Bye bye'), 1600, 900, 'BYE BYE!', { size: 72, color: D.ORANGE });
    draw(c(6, 'Bye bye') + 0.2, 0.4, 0, 0, 1, D.arrow(1500, 820, 1800, 820, { stroke: D.ORANGE }));
  });

  // 7. Retreat; round one to the emus
  scene(D.sectionStart(7), () => {
    calendar(c(7, 'November eighth'), 230, 260, 'NOV', '8');
    for (let i = 0; i < 8; i++) draw(c(7, 'two thousand') + i * 0.06, 0.2, 700 + i * 55, 230, 0.9, L.bullet());
    write(c(7, 'two thousand') + 0.5, 900, 380, '2,500 bullets fired', { size: 62 });
    draw(c(7, 'Very poor'), 0.6, 300, 620, 1, L.face('sad', 150));
    write(c(7, 'Very poor'), 300, 790, 'Results: very poor', { size: 50, color: D.RED });
    draw(c(7, 'newspapers'), 0.9, 900, 620, 1.1, L.newspaper());
    write(c(7, 'newspapers') + 0.6, 900, 563, 'NEWS', { size: 56 });
    draw(c(7, 'making fun') , 0.5, 1000, 640, 1, L.face('laugh', 90));
    write(c(7, 'making fun') + 0.4, 1190, 470, 'HA HA!', { size: 66, color: D.RED, rotate: -10 });
    draw(c(7, 'pulled out'), 0.9, 1520, 640, 1, soldier(), { flip: true });
    draw(c(7, 'pulled out') + 0.6, 0.4, 0, 0, 1, D.arrow(1600, 760, 1800, 760));
    D.stamp(c(7, 'Round one'), 960, 900, 'ARMY 0  -  EMUS 1', { size: 64, color: D.RED, rotate: -3 });
  });

  // 8a. Round 2
  scene(D.sectionStart(8), () => {
    write(c(8, 'But the story'), 960, 150, 'But wait...', { size: 90 });
    draw(c(8, 'farmers asked again'), 1.0, 360, 780, 1.15, L.person({ hat: 'straw', torso: '#74c0fc' }));
    draw(c(8, 'farmers asked again') + 0.6, 0.5, 520, 380, 0.8, L.bubble(420, 170));
    write(c(8, 'farmers asked again') + 0.9, 520, 395, 'Again, please!', { size: 56 });
    calendar(c(8, 'November thirteenth'), 960, 470, 'NOV', '13');
    soldierWithGun(c(8, 'army came back'), 1340, 790, 1.05);
    D.stamp(c(8, 'Round two'), 960, 760, 'ROUND 2', { size: 80, color: D.RED });
    write(c(8, 'December tenth'), 960, 890, 'fighting until 10 December', { size: 50, color: D.GREY });
  });

  // 8b. The maths: ten bullets per emu
  scene(c(8, 'In his report'), () => {
    draw(c(8, 'In his report'), 0.8, 300, 520, 1, L.paper());
    write(c(8, 'In his report') + 0.6, 300, 395, 'REPORT', { size: 56, color: D.BLUE });
    write(c(8, 'nine hundred and eighty-six'), 900, 280, '986 emus', { size: 92 });
    write(c(8, 'nine thousand'), 900, 420, '9,860 bullets', { size: 92 });
    draw(c(8, 'Do the maths'), 0.4, 0, 0, 1, D.line(640, 470, 1160, 470, { strokeWidth: 6 }));
    write(c(8, 'Do the maths') + 0.3, 900, 570, '9,860 ÷ 986 = 10', { size: 76, color: D.BLUE });
    draw(c(8, 'ten bullets for every emu'), 1.0, 1560, 520, 0.6, L.emu());
    for (let i = 0; i < 10; i++) draw(c(8, 'Ten bullets', 1) + i * 0.06, 0.15, 700 + i * 50, 720, 0.8, L.bullet());
    D.stamp(c(8, 'For one bird'), 1300, 880, '10 BULLETS = 1 BIRD', { size: 62, color: D.RED, rotate: -4 });
  });

  // 9a. The tank quote
  scene(D.sectionStart(9), () => {
    draw(c(9, 'what Major Meredith said'), 0.8, 0, 0, 1, D.rect(130, 160, 1180, 450, { stroke: D.ORANGE, strokeWidth: 5 }));
    write(c(9, 'They can face'), 720, 270, 'They can face machine guns\nwith the invulnerability\nof tanks.', { size: 68, dur: 3.2 });
    write(c(9, 'In simple words'), 720, 560, '- Major Meredith, 1932', { size: 48, color: D.GREY });
    draw(c(9, 'these birds stood'), 1.0, 1480, 450, 0.62, L.emu());
    draw(c(9, 'like tanks'), 0.9, 1480, 600, 0.75, L.treads());
    write(c(9, 'comparing a bird'), 720, 800, 'A bird... like a TANK!', { size: 72, color: D.RED });
  });

  // 9b. Minister of the Emu War
  scene(c(9, 'In parliament'), () => {
    draw(c(9, 'In parliament'), 1.4, 640, 600, 1, L.parliament());
    draw(c(9, 'called the Defence Minister'), 1.0, 1420, 780, 1.15, L.person({ hat: 'top', torso: D.INK, tie: true }));
    draw(c(9, 'Minister of the Emu War'), 0.4, 1420, 660, 0.7, L.medal());
    write(c(9, 'Minister of the Emu War'), 1300, 260, 'MINISTER OF\nTHE EMU WAR', { size: 82, color: D.ORANGE });
  });

  // 10a. Who won
  scene(D.sectionStart(10), () => {
    write(c(10, 'Who won'), 960, 190, 'WHO WON?', { size: 130 });
    draw(c(10, 'And the answer is'), 1.0, 860, 640, 1.2, L.trophy());
    draw(c(10, 'And the answer is') + 0.5, 0.8, 1280, 620, 0.75, L.emu());
    D.stamp(c(10, 'the emus'), 960, 880, 'WINNER: THE EMUS', { size: 66, color: D.GREEN, rotate: -3 });
  });

  // 10b. Three more requests, three noes; bounties and fences instead
  scene(c(10, 'three more times'), () => {
    write(c(10, 'three more times'), 960, 130, 'Farmers asked for the army again:', { size: 62 });
    write(c(10, 'nineteen thirty-four'), 450, 330, '1934', { size: 100 });
    write(c(10, 'nineteen forty-three'), 960, 330, '1943', { size: 100 });
    write(c(10, 'nineteen forty-eight'), 1470, 330, '1948', { size: 100 });
    [450, 960, 1470].forEach((x, i) => D.stamp(c(10, 'said no') + i * 0.25, x, 450, 'NO', { size: 70 }));
    write(c(10, 'never came back'), 960, 590, 'The army never came back.', { size: 58, color: D.GREY });
    draw(c(10, 'bounty rewards'), 0.6, 960, 720, 1, L.coin());
    write(c(10, 'bounty rewards') + 0.4, 960, 745, '$', { size: 70, dur: 0.2 });
    write(c(10, 'bounty rewards') + 0.6, 960, 860, 'bounty rewards', { size: 52 });
    draw(c(10, 'strong fences'), 1.0, 220, 830, 0.9, L.fence(5, 110));
    write(c(10, 'strong fences') + 0.6, 440, 880, 'strong fences', { size: 52 });
    draw(c(10, 'Not machine guns'), 0.6, 1520, 740, 0.7, L.gun());
    draw(c(10, 'Not machine guns') + 0.5, 0.4, 1520, 740, 1.2, L.cross());
  });

  // 11. Comments
  scene(D.sectionStart(11), () => {
    draw(c(11, 'Do you know'), 0.9, 900, 430, 1, L.comment(780));
    write(c(11, 'funny true story'), 900, 420, 'Your funny true story?', { size: 72 });
    draw(c(11, 'Tell me'), 1.0, 1560, 600, 0.6, L.emu());
    write(c(11, 'comments'), 900, 700, 'Tell me in the comments', { size: 60, color: D.ORANGE });
    draw(c(11, 'comments') + 0.8, 0.4, 0, 0, 1, D.arrow(900, 760, 900, 880, { stroke: D.ORANGE }));
    write(c(11, 'It could be'), 330, 180, 'next video?', { size: 56, color: D.GREY });
  });

  // End card
  D.tail = 3.5;
  scene(window.TIMING.total + LEAD + 0.6, () => {
    const t = window.TIMING.total + 0.7;
    write(t, 960, 420, 'Thanks for watching!', { size: 110, color: D.ORANGE });
    draw(t + 0.8, 1.0, 960, 760, 0.7, L.emu());
  });
})();
