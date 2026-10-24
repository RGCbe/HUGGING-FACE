// Scenes for "The Pig War (1859)". Times come from timing.json via cue(section, "words").
// Each board is an illustration (images.json, made with doodle/imagegen.py) painted in behind the
// pen, with handwritten words and small doodles on top, kept to the plain cream top third of the
// picture. render.mjs --data passes {"img": DIR}, the folder holding p01.png ... p23.png and end.png.
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
  scene(0, 'p01', () => {
    big(c(1, 'eighteen fifty-nine'), 300, 190, '1859', { size: 150, color: D.ORANGE });
    D.stamp(c(1, 'real history'), 1600, 170, 'TRUE STORY', { size: 56, rotate: 7 });
    big(c(1, 'one dead pig'), 960, 150, '1 PIG = WAR?', { size: 110, color: D.RED });
    write(c(1, 'But how'), 960, 260, 'But how?', { size: 70 });
  });

  // 2. Greeting and what the video covers
  scene(D.sectionStart(2), 'p02', () => {
    write(c(2, 'Hello'), 400, 140, 'Hello friends!', { size: 80 });
    write(c(2, "I'm Manoj"), 400, 230, "I'm Manoj", { size: 60, color: D.GREY });
    big(c(2, 'Pig War'), 1400, 140, 'THE PIG WAR', { size: 100, color: D.ORANGE });
    write(c(2, 'started'), 1280, 230, '1. How it started', { size: 56 });
    write(c(2, 'what happened'), 1280, 300, '2. What happened next', { size: 56 });
    write(c(2, 'who won'), 1280, 370, '3. Who won?', { size: 56 });
    D.stamp(c(2, 'Every word is true'), 400, 340, '100% TRUE', { size: 58 });
    write(c(2, 'sources'), 1280, 440, 'sources in the description', { size: 44, color: D.BLUE });
  });

  // 3. The border and the two channels
  scene(D.sectionStart(3), 'p03', () => {
    calendar(c(3, 'eighteen forty-six'), 190, 210, 'JUNE', '15', '1846');
    write(c(3, 'agreed on a border'), 960, 120, 'The border treaty', { size: 80 });
    write(c(3, 'middle of the channel'), 960, 215, 'line = middle of the channel', { size: 56, color: D.BLUE });
    big(c(3, 'two channels'), 1600, 170, '2 CHANNELS?!', { size: 90, color: D.RED });
    big(c(3, 'San Juan'), 960, 300, 'SAN JUAN', { size: 76, color: D.ORANGE });
  });

  // 4a. Both countries claim it
  scene(D.sectionStart(4), 'p04', () => {
    big(c(4, 'this island is ours'), 520, 170, 'MINE!', { size: 120, color: D.BLUE, rotate: -6 });
    big(c(4, 'this island is ours') + 0.6, 1400, 170, 'NO, MINE!', { size: 120, color: D.RED, rotate: 5 });
  });

  // 4b. The sheep farm and the settlers
  scene(c(4, "The British Hudson's"), 'p05', () => {
    write(c(4, "Hudson's Bay Company"), 480, 120, "Hudson's Bay Company", { size: 62 });
    write(c(4, 'sheep farm'), 480, 200, 'British sheep farm', { size: 56, color: D.GREEN });
    write(c(4, 'Charles Griffin'), 480, 275, 'boss: Charles Griffin', { size: 52, color: D.GREY });
    write(c(4, 'twenty-five'), 1450, 120, '~25 American settlers', { size: 62, color: D.BLUE });
    big(c(4, 'What could go wrong'), 1450, 230, 'What could go wrong?', { size: 76, color: D.ORANGE });
  });

  // 5a. June 15, 1859: the pig in the garden
  scene(D.sectionStart(5), 'p06', () => {
    calendar(c(5, 'June fifteenth'), 190, 210, 'JUNE', '15', '1859');
    write(c(5, 'Lyman Cutlar'), 960, 120, 'Lyman Cutlar, American farmer', { size: 62 });
    big(c(5, 'eating his potatoes'), 1080, 230, 'MY POTATOES!', { size: 90, color: D.RED });
  });

  // 5b. The shot; whose pig
  scene(c(5, 'Cutlar picks up'), 'p07', () => {
    D.pop(c(5, 'shoots the pig'), put(900, 170, 0.8, L.burst(140)));
    D.write(c(5, 'shoots the pig') + 0.15, 900, 190, 'BANG!', { size: 70, color: D.RED, dur: 0.4 });
    write(c(5, 'whose pig'), 520, 140, 'Whose pig was it?', { size: 70 });
    D.stamp(c(5, "Charles Griffin's"), 520, 260, "GRIFFIN'S!", { size: 70, color: D.RED });
  });

  // 5c. Thirteen years to the day
  scene(c(5, 'Fun fact'), 'p08', () => {
    write(c(5, 'exactly thirteen years'), 960, 110, 'June 15, 1846  ->  June 15, 1859', { size: 62 });
    write(c(5, 'exactly thirteen years') + 1.2, 960, 190, 'exactly 13 years later', { size: 56, color: D.GREY });
    D.punch(c(5, 'Happy anniversary'));
    big(c(5, 'Happy anniversary'), 960, 290, 'HAPPY ANNIVERSARY!', { size: 96, color: D.ORANGE });
  });

  // 6a. Ten dollars or a hundred
  scene(D.sectionStart(6), 'p09', () => {
    write(c(6, 'ten dollars'), 995, 110, 'Offer: $10', { size: 64, color: D.GREEN });
    big(c(6, 'one hundred dollars'), 995, 215, '$100!', { size: 100, color: D.RED });
    D.stamp(c(6, 'Cutlar refused'), 995, 320, 'REFUSED', { size: 56 });
    write(c(6, 'on his land'), 995, 415, '"It was on MY land!"', { size: 44 });
  });

  // 6b. Neighbours
  scene(c(6, 'Just like two'), 'p10', () => {
    write(c(6, 'two neighbours'), 400, 150, 'Two neighbours...', { size: 80 });
    D.punch(c(6, 'mango tree'));
    big(c(6, 'mango tree'), 1530, 150, '...one mango tree', { size: 84, color: D.ORANGE });
  });

  // 7a. Arrest threat; the settlers ask for help
  scene(D.sectionStart(7), 'p11', () => {
    big(c(7, 'arrest Cutlar'), 430, 105, 'ARREST HIM!', { size: 90, color: D.RED });
    write(c(7, 'asked their army'), 1560, 100, 'Army, help us!', { size: 72, color: D.BLUE });
  });

  // 7b. Captain Pickett lands
  scene(c(7, 'And the army sent'), 'p12', () => {
    write(c(7, 'Captain George Pickett'), 1250, 110, 'Captain George Pickett', { size: 66 });
    write(c(7, 'sixty-five soldiers'), 1250, 190, '+ about 65 soldiers', { size: 58, color: D.BLUE });
    calendar(c(7, 'July twenty-seventh'), 190, 210, 'JULY', '27', '1859');
    write(c(7, "We'll make"), 1250, 285, '"We\'ll make a Bunker Hill of it!"', { size: 56, color: D.RED });
  });

  // 7c. Bunker Hill, over a pig
  scene(c(7, 'Bunker Hill was'), 'p01', () => {
    write(c(7, 'famous battle'), 960, 110, 'Bunker Hill (1775): a famous battle', { size: 60 });
    write(c(7, 'famous battle') + 1.0, 960, 185, 'America vs Britain', { size: 56, color: D.GREY });
    D.punch(c(7, 'Over a pig'));
    big(c(7, 'Over a pig'), 960, 290, 'OVER A PIG?!', { size: 110, color: D.RED });
  });

  // 8a. The governor sends warships
  scene(D.sectionStart(8), 'p13', () => {
    write(c(8, 'James Douglas'), 1450, 110, 'Governor James Douglas', { size: 62 });
    write(c(8, 'not happy'), 1450, 190, 'NOT happy', { size: 64, color: D.RED });
    big(c(8, 'Then more warships'), 1450, 290, 'MORE WARSHIPS!', { size: 84, color: D.RED });
  });

  // 8b. The standoff, in numbers
  scene(c(8, 'Within a few weeks'), 'p14', () => {
    write(c(8, 'four hundred and sixty-one'), 1500, 100, 'USA: 461 soldiers', { size: 60, color: D.BLUE });
    write(c(8, 'fourteen cannons'), 1500, 170, '14 cannons', { size: 56, color: D.BLUE });
    write(c(8, 'five British warships'), 420, 100, 'Britain: 5 warships', { size: 60, color: D.RED });
    write(c(8, 'seventy guns'), 420, 170, '70 guns, 2,140 men', { size: 56, color: D.RED });
    D.punch(c(8, 'one pig'));
    big(c(8, 'one pig'), 960, 280, 'ALL FOR 1 PIG', { size: 100, color: D.ORANGE });
  });

  // 9. The admiral says no
  scene(D.sectionStart(9), 'p15', () => {
    write(c(9, 'wanted the American'), 1500, 120, 'Governor: "Get them out!"', { size: 56 });
    write(c(9, 'Robert Baynes'), 420, 110, 'Admiral Robert Baynes', { size: 60 });
    D.stamp(c(9, 'refused to attack'), 420, 210, 'NO ATTACK', { size: 60 });
    write(c(9, 'two great nations'), 1300, 200, 'No war "over a squabble about a pig"', { size: 48, color: D.GREY, dur: 2.4 });
    D.punch(c(9, 'Finally'));
    big(c(9, 'Finally'), 1300, 295, 'Finally, someone sensible!', { size: 76, color: D.GREEN });
  });

  // 10. General Scott and the deal
  scene(D.sectionStart(10), 'p16', () => {
    write(c(10, 'James Buchanan'), 520, 110, 'President James Buchanan sent...', { size: 52, color: D.GREY });
    write(c(10, 'Winfield Scott'), 520, 190, 'General Winfield Scott', { size: 66, color: D.BLUE });
    write(c(10, 'In October'), 1700, 110, 'October 1859', { size: 56, color: D.GREY });
    D.stamp(c(10, 'made a deal'), 1250, 150, 'THE DEAL', { size: 70, color: D.GREEN, rotate: -4 });
    write(c(10, 'no more than'), 1250, 270, 'small forces: max 100 men', { size: 56 });
  });

  // 11a. Two camps, twelve years
  scene(D.sectionStart(11), 'p17', () => {
    write(c(11, 'British camped'), 450, 110, 'British camp: north', { size: 60, color: D.RED });
    write(c(11, 'Americans camped'), 1470, 110, 'American camp: south', { size: 60, color: D.BLUE });
    big(c(11, 'twelve years'), 960, 230, '12 YEARS of waiting...', { size: 90, color: D.ORANGE });
  });

  // 11b. Friends, not enemies; the alcohol
  scene(c(11, "But here's the funny part"), 'p18', () => {
    write(c(11, 'visited each'), 330, 110, 'visits', { size: 64 });
    write(c(11, 'celebrated holidays'), 960, 110, 'holidays', { size: 64 });
    write(c(11, 'sports competitions'), 1590, 110, 'sports day!', { size: 64 });
    write(c(11, 'biggest danger'), 960, 200, 'Biggest danger to peace?', { size: 62 });
    D.punch(c(11, 'It was the alcohol'));
    big(c(11, 'It was the alcohol'), 960, 300, 'THE ALCOHOL!', { size: 100, color: D.RED });
  });

  // 12. The German emperor decides
  scene(D.sectionStart(12), 'p19', () => {
    write(c(12, 'Not America'), 330, 120, 'Not America', { size: 60 });
    draw(c(12, 'Not America') + 0.5, 0.3, 560, 110, 0.4, L.cross());
    write(c(12, 'Not Britain'), 330, 210, 'Not Britain', { size: 60 });
    draw(c(12, 'Not Britain') + 0.5, 0.3, 560, 200, 0.4, L.cross());
    write(c(12, 'eighteen seventy-one'), 330, 300, '1871', { size: 64, color: D.GREY });
    big(c(12, 'Kaiser Wilhelm'), 520, 400, 'KAISER WILHELM I', { size: 84, color: D.ORANGE });
    D.punch(c(12, 'started with a pig'));
    write(c(12, 'started with a pig'), 520, 490, 'Germany judges a pig fight', { size: 54, color: D.RED });
  });

  // 13a. Geneva and the ruling
  scene(D.sectionStart(13), 'p20', () => {
    write(c(13, 'three experts'), 480, 110, '3 experts in Geneva', { size: 64 });
    write(c(13, 'almost a year'), 480, 190, 'almost 1 year', { size: 54, color: D.GREY });
    calendar(c(13, 'October twenty-first'), 1760, 210, 'OCT', '21', '1872');
    D.stamp(c(13, 'belongs to America'), 1150, 160, 'ISLAND: AMERICA', { size: 66, color: D.BLUE, rotate: -4 });
  });

  // 13b. The British leave
  scene(c(13, 'A month later'), 'p21', () => {
    write(c(13, 'A month later'), 480, 120, 'November 1872', { size: 64, color: D.GREY });
    big(c(13, 'packed up and left'), 1400, 170, 'BYE BYE!', { size: 110, color: D.ORANGE });
  });

  // 14a. Who won, and the casualties
  scene(D.sectionStart(14), 'p17', () => {
    big(c(14, 'So who won'), 960, 120, 'WHO WON?', { size: 100 });
    write(c(14, 'America got the island'), 480, 230, 'America got the island', { size: 58, color: D.BLUE });
    draw(c(14, 'America got the island') + 1.0, 0.3, 820, 215, 0.6, L.check());
    write(c(14, 'not one soldier'), 1450, 210, '0 soldiers killed', { size: 58 });
    write(c(14, 'Not one sailor'), 1450, 280, '0 sailors killed', { size: 58 });
  });

  // 14b. The only casualty
  scene(c(14, 'The only one'), 'p22', () => {
    write(c(14, 'The only one'), 960, 110, 'The only casualty...', { size: 76 });
    D.punch(c(14, 'was the pig'));
    big(c(14, 'was the pig'), 960, 230, 'THE PIG', { size: 140, color: D.RED });
  });

  // 15. Comments
  scene(D.sectionStart(15), 'p23', () => {
    write(c(15, 'funny true story'), 960, 140, 'Your funny true story?', { size: 84 });
    big(c(15, 'comments'), 960, 250, 'Tell me in the comments', { size: 72, color: D.ORANGE });
    write(c(15, 'It could be'), 960, 340, 'It could be my next video!', { size: 52, color: D.GREY });
  });

  // End card (build.py adds 3 seconds after the voiceover)
  D.tail = 3;
  scene(window.TIMING.total + LEAD + 0.4, 'end', () => {
    big(window.TIMING.total + 0.5, 1300, 200, 'Thanks for watching!', { size: 104, color: D.ORANGE });
  });
})();
