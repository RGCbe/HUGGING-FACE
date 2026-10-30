// Scenes for "The Emu War (1932)". Times come from timing.json via cue(section, "words").
// Each board is an illustration (images.json, made with doodle/imagegen.py) painted in behind the
// pen, with handwritten words and small doodles on top. render.mjs --data passes {"img": DIR}, the
// folder holding e01.png ... e21.png (01-emu-war/img).
(function () {
  const D = Doodle;
  const L = D.lib;
  const c = D.cue;
  const LEAD = 0.2; // a scene's board is in place this long before its first cue word
  const CREAM = '#fff8e7';

  const put = (x, y, s, nodes, o) => D.at(x, y, s, nodes, o);
  const draw = (at, dur, x, y, s, nodes, o) => D.draw(at, dur, put(x, y, s, nodes, o));
  // handwriting with a cream halo, so it reads over any picture
  const write = (at, x, y, str, o = {}) => D.write(at, x, y, str, Object.assign({ outline: CREAM, outlineWidth: 16 }, o));
  const big = (at, x, y, str, o = {}) => write(at, x, y, str, Object.assign({ outline: D.INK, outlineWidth: 14 }, o));
  // the board is cream paper before the picture is painted over it
  function picture(at, name, dur = 1.1) {
    D.draw(at, 0.01, D.rect(-20, -20, D.W + 40, D.H + 40, { fill: CREAM, fillStyle: 'solid', stroke: 'none' }));
    D.image(at, dur, `${window.DATA.img}/${name}.png`, 0, 0, D.W, D.H, { zoom: 0.04, zoomDur: 12 });
  }
  const scene = (t, name, build) => D.scene(Math.max(0, t - LEAD), () => {
    picture(Math.max(0, t - LEAD), name, t < 1 ? 0.6 : 1.1);
    build();
  });

  function calendar(at, x, y, month, day, year, s = 0.8) {
    draw(at, 0.7, x, y, s, L.calendar());
    D.write(at + 0.6, x, y - 60 * s, month, { size: 44 * s, color: '#ffffff', dur: 0.3 });
    D.write(at + 0.8, x, y + 40 * s, day, { size: 100 * s, dur: 0.3 });
    if (year) D.write(at + 1.0, x, y + 88 * s, year, { size: 36 * s, color: D.GREY, dur: 0.3 });
  }

  // 1. Hook
  scene(0, 'e01', () => {
    big(c(1, 'nineteen thirty-two'), 300, 190, '1932', { size: 150, color: D.ORANGE });
    D.stamp(c(1, 'real history'), 1600, 170, 'TRUE STORY', { size: 56, rotate: 7 });
    big(c(1, 'what happened'), 960, 210, '?', { size: 200, color: D.RED, dur: 0.4 });
  });

  // 2. Greeting and what the video covers
  scene(D.sectionStart(2), 'e02', () => {
    write(c(2, 'Hello'), 400, 140, 'Hello friends!', { size: 80 });
    write(c(2, "I'm Manoj"), 400, 230, "I'm Manoj", { size: 60, color: D.GREY });
    big(c(2, 'Emu War'), 1400, 140, 'THE EMU WAR', { size: 100, color: D.ORANGE });
    write(c(2, 'started'), 1400, 230, '1. How it started', { size: 56 });
    write(c(2, 'what happened'), 1400, 300, '2. What happened', { size: 56 });
    write(c(2, 'who won'), 1400, 370, '3. Who won?', { size: 56 });
    D.stamp(c(2, 'Every word is true'), 400, 340, '100% TRUE', { size: 58 });
    write(c(2, 'sources'), 1400, 455, 'sources in the description', { size: 44, color: D.BLUE });
  });

  // 3a. Soldiers become farmers
  scene(D.sectionStart(3), 'e03', () => {
    write(c(3, 'After the First'), 960, 130, 'World War 1 ends', { size: 84 });
    big(c(3, 'land'), 1520, 250, 'FREE LAND', { size: 80, color: D.GREEN });
    write(c(3, 'Nice idea'), 500, 250, 'Nice idea, right?', { size: 64, color: D.GREEN });
  });

  // 3b. Western Australia, Campion, wheat
  scene(c(3, 'Western Australia'), 'e04', () => {
    write(c(3, 'Western Australia'), 420, 140, 'Western Australia', { size: 76 });
    write(c(3, 'Campion'), 420, 230, 'Campion', { size: 64, color: D.RED });
    write(c(3, 'growing wheat'), 1480, 140, 'Wheat farms', { size: 76 });
    big(c(3, 'until'), 1480, 245, 'until 1932...', { size: 84, color: D.RED });
  });

  // 4a. 20,000 emus arrive
  scene(D.sectionStart(4), 'e05', () => {
    big(c(4, 'twenty thousand'), 960, 190, '20,000 EMUS', { size: 150, color: D.ORANGE });
  });

  // 4b. What an emu is
  scene(c(4, "If you've never seen"), 'e06', () => {
    write(c(4, 'huge bird'), 880, 140, 'HUGE bird', { size: 84 });
    write(c(4, "can't fly"), 880, 240, "can't fly", { size: 70, color: D.RED });
    draw(c(4, "can't fly") + 0.4, 0.4, 1080, 220, 0.4, L.cross());
    big(c(4, 'Very fast'), 1450, 180, 'VERY FAST!', { size: 100, color: D.ORANGE });
  });

  // 4c. Damage and rabbits
  scene(c(4, 'These emus ate'), 'e07', () => {
    write(c(4, 'ruined the crops'), 380, 140, 'crops ruined', { size: 72, color: D.RED });
    write(c(4, 'holes in the fences'), 960, 140, 'holes!', { size: 76, color: D.RED });
    big(c(4, 'Double trouble'), 1480, 160, 'DOUBLE TROUBLE', { size: 96, color: D.RED });
  });

  // 5a. Farmers ask for machine guns; the minister says yes
  scene(D.sectionStart(5), 'e08', () => {
    write(c(5, 'we need'), 450, 130, 'We need', { size: 66 });
    big(c(5, 'machine guns'), 450, 230, 'MACHINE GUNS!', { size: 84, color: D.RED });
    write(c(5, 'Sir George Pearce'), 1050, 130, 'Sir George Pearce', { size: 66 });
    write(c(5, 'Sir George Pearce') + 0.5, 1050, 200, 'Defence Minister', { size: 48, color: D.GREY, dur: 0.5 });
    D.stamp(c(5, 'said yes'), 1050, 310, 'YES!', { size: 80, color: D.GREEN });
  });

  // 5b. What the army sent
  scene(c(5, 'The army sent'), 'e09', () => {
    write(c(5, 'The army sent'), 960, 110, 'The army sent:', { size: 72 });
    write(c(5, 'Major Meredith'), 380, 210, 'Major Meredith', { size: 60 });
    write(c(5, 'two soldiers'), 960, 210, '2 soldiers', { size: 60 });
    write(c(5, 'two Lewis'), 1540, 210, '2 Lewis machine guns', { size: 56 });
    for (let i = 0; i < 6; i++) draw(c(5, 'two Lewis') + 1.0 + i * 0.06, 0.15, 790 + i * 60, 300, 1, L.bullet());
    big(c(5, 'two Lewis') + 1.3, 960, 400, '10,000 bullets', { size: 84, color: D.ORANGE, dur: 0.6 });
  });

  // 5c. The plan
  scene(c(5, 'The plan was simple'), 'e10', () => {
    D.write(c(5, 'The plan was simple'), 1250, 290, 'THE PLAN', { size: 84, color: D.BLUE });
    D.write(c(5, 'Shoot the emus'), 1250, 390, '1. Shoot the emus', { size: 62 });
    D.write(c(5, 'Problem solved'), 1250, 470, '2. Problem solved', { size: 62 });
    draw(c(5, 'Problem solved') + 0.7, 0.3, 1520, 450, 1, L.check());
    write(c(5, 'Monday meeting'), 330, 150, 'Monday meeting', { size: 58, color: D.GREY });
    D.stamp(c(5, 'Perfect on paper'), 1250, 120, 'PERFECT ON PAPER', { size: 56, color: D.ORANGE, rotate: -4 });
  });

  // 6a. Round 1 starts; emus scatter out of range
  scene(D.sectionStart(6), 'e11', () => {
    calendar(c(6, 'November second'), 190, 210, 'NOV', '2', '1932');
    big(c(6, 'The war begins'), 960, 150, 'ROUND 1', { size: 120, color: D.RED });
    write(c(6, 'not in the'), 960, 260, "(that wasn't in the plan)", { size: 52, color: D.GREY });
    big(c(6, 'run out of range'), 1560, 200, 'OUT OF RANGE!', { size: 80, color: D.ORANGE });
  });

  // 6b. The dam, twelve emus, the jam
  scene(c(6, 'Two days later'), 'e12', () => {
    write(c(6, 'Two days later'), 300, 110, '2 days later...', { size: 56, color: D.GREY });
    write(c(6, 'more than a thousand'), 1500, 140, '1,000+ emus', { size: 80 });
    big(c(6, 'perfect chance'), 960, 140, 'PERFECT CHANCE!', { size: 84, color: D.ORANGE });
    write(c(6, 'twelve'), 960, 250, 'only 12', { size: 84, color: D.RED });
    D.pop(c(6, 'gun jammed'), put(860, 470, 0.7, L.burst(140)));
    D.write(c(6, 'gun jammed') + 0.15, 860, 490, 'JAMMED!', { size: 58, color: D.RED, dur: 0.4 });
    big(c(6, 'Bye bye'), 1500, 260, 'BYE BYE!', { size: 80, color: D.ORANGE });
  });

  // 7. Retreat; round one to the emus
  scene(D.sectionStart(7), 'e13', () => {
    calendar(c(7, 'November eighth'), 190, 210, 'NOV', '8');
    write(c(7, 'two thousand'), 960, 130, '2,500 bullets fired', { size: 70 });
    write(c(7, 'Very poor'), 960, 220, 'Results: very poor', { size: 60, color: D.RED });
    write(c(7, 'making fun'), 560, 300, 'HA HA!', { size: 70, color: D.RED, rotate: -10 });
    D.stamp(c(7, 'Round one'), 1500, 230, 'ARMY 0 - EMUS 1', { size: 64, color: D.RED, rotate: -3 });
  });

  // 8a. Round 2
  scene(D.sectionStart(8), 'e14', () => {
    write(c(8, 'But the story'), 960, 120, 'But wait...', { size: 90 });
    write(c(8, 'farmers asked again'), 400, 230, 'Again, please!', { size: 64 });
    calendar(c(8, 'November thirteenth'), 1730, 210, 'NOV', '13');
    D.stamp(c(8, 'Round two'), 960, 215, 'ROUND 2', { size: 76, color: D.RED });
    write(c(8, 'December tenth'), 960, 300, 'fighting until 10 December', { size: 48, color: D.GREY });
  });

  // 8b. The maths: ten bullets per emu
  scene(c(8, 'In his report'), 'e15', () => {
    write(c(8, 'nine hundred and eighty-six'), 420, 130, '986 emus', { size: 92 });
    write(c(8, 'nine thousand'), 420, 240, '9,860 bullets', { size: 92 });
    big(c(8, 'Do the maths'), 1400, 140, '9,860 ÷ 986 = 10', { size: 84, color: D.BLUE });
    D.stamp(c(8, 'For one bird'), 1400, 280, '10 BULLETS = 1 BIRD', { size: 62, color: D.RED, rotate: -4 });
  });

  // 9a. The tank quote
  scene(D.sectionStart(9), 'e16', () => {
    write(c(9, 'They can face'), 1500, 100, '"They can face machine guns with\nthe invulnerability of tanks."', { size: 54, dur: 3.2 });
    write(c(9, 'In simple words'), 1500, 230, '- Major Meredith, 1932', { size: 42, color: D.GREY });
    big(c(9, 'comparing a bird'), 60, 140, 'A bird...\nlike a TANK!', { size: 72, color: D.RED, anchor: 'start' });
  });

  // 9b. Minister of the Emu War
  scene(c(9, 'In parliament'), 'e17', () => {
    write(c(9, 'In parliament'), 330, 130, 'In parliament...', { size: 64, color: D.GREY });
    big(c(9, 'Minister of the Emu War'), 1180, 140, 'MINISTER OF THE EMU WAR', { size: 92, color: D.ORANGE });
  });

  // 10a. Who won
  scene(D.sectionStart(10), 'e18', () => {
    big(c(10, 'Who won'), 320, 200, 'WHO WON?', { size: 110 });
    D.punch(c(10, 'the emus'));
    D.stamp(c(10, 'the emus'), 1550, 300, 'WINNER: THE EMUS', { size: 62, color: D.GREEN, rotate: -3 });
  });

  // 10b. Three more requests, three noes; bounties and fences instead
  scene(c(10, 'three more times'), 'e19', () => {
    write(c(10, 'three more times'), 960, 90, 'The farmers asked for the army again:', { size: 50 });
    write(c(10, 'nineteen thirty-four'), 450, 180, '1934', { size: 80 });
    write(c(10, 'nineteen forty-three'), 960, 180, '1943', { size: 80 });
    write(c(10, 'nineteen forty-eight'), 1470, 180, '1948', { size: 80 });
    [450, 960, 1470].forEach((x, i) => D.stamp(c(10, 'said no') + i * 0.25, x, 255, 'NO', { size: 54 }));
    write(c(10, 'bounty rewards'), 175, 420, 'bounty\nrewards', { size: 48, color: D.GREEN });
    write(c(10, 'strong fences'), 1760, 330, 'strong\nfences', { size: 48, color: D.GREEN });
  });

  // 11. Comments
  scene(D.sectionStart(11), 'e20', () => {
    write(c(11, 'funny true story'), 960, 140, 'Your funny true story?', { size: 84 });
    big(c(11, 'comments'), 960, 250, 'Tell me in the comments', { size: 72, color: D.ORANGE });
    write(c(11, 'It could be'), 960, 340, 'It could be my next video!', { size: 52, color: D.GREY });
  });

  // End card
  D.tail = 3.5;
  scene(window.TIMING.total + LEAD + 0.6, 'e21', () => {
    big(window.TIMING.total + 0.7, 1300, 200, 'Thanks for watching!', { size: 104, color: D.ORANGE });
  });
})();
