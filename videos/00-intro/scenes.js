// Scenes for the Tea Break with Manoj channel intro. Each board is an AI illustration (images.json,
// made with doodle/imagegen.py) painted in behind the pen, with handwritten words on top, cued to
// the voiceover. render.mjs --data passes {"img": DIR}, the folder holding s1.png ... s7.png.
(function () {
  const D = Doodle;
  const L = D.lib;
  const c = D.cue;
  const LEAD = 0.2; // a scene's board is in place this long before its first cue word
  const CREAM = '#fff8e7';

  const scene = (t, build) => D.scene(Math.max(0, t - LEAD), build);
  // the board is cream paper (like the pictures) before the picture is painted over it
  const picture = (at, name, dur = 1.1) => {
    D.draw(at, 0.01, D.rect(-20, -20, D.W + 40, D.H + 40, { fill: CREAM, fillStyle: 'solid', stroke: 'none' }));
    D.image(at, dur, `${window.DATA.img}/${name}.png`, 0, 0, D.W, D.H, { zoom: 0.05 });
  };
  // handwriting with a cream halo, so it reads over any picture
  const say = (at, x, y, str, o = {}) => D.write(at, x, y, str, Object.assign({ outline: CREAM, outlineWidth: 16 }, o));

  // 1. Hook: Ever wished history was this much fun?
  D.scene(0, () => {
    picture(0, 's1', 0.6);
    say(c(1, 'history'), 330, 170, 'History...', { size: 110 });
    say(c(1, 'this much'), 1600, 175, 'FUN?!', { size: 150, color: D.ORANGE, outline: D.INK, outlineWidth: 14 });
  });

  // 2. Hello friends, I'm Manoj, and welcome to Tea Break with Manoj.
  scene(D.sectionStart(2), () => {
    picture(D.sectionStart(2) - LEAD, 's2');
    say(c(2, 'Hello'), 960, 160, 'Hello friends!', { size: 96 });
    say(c(2, 'welcome'), 960, 320, 'Tea Break with Manoj', { size: 150, color: D.ORANGE, outline: D.INK, outlineWidth: 14 });
  });

  // 3. For busy people: a short tea break, a short funny story.
  scene(D.sectionStart(3), () => {
    picture(D.sectionStart(3) - LEAD, 's3');
    say(c(3, 'busy people'), 1460, 160, 'For busy people', { size: 96 });
    say(c(3, 'short tea break'), 1460, 270, 'a short tea break...', { size: 72 });
    say(c(3, 'funny story'), 1460, 370, '+ a funny true story', { size: 72, color: D.ORANGE });
  });

  // 4. True, simple English, no long lectures.
  scene(D.sectionStart(4), () => {
    picture(D.sectionStart(4) - LEAD, 's4');
    D.stamp(c(4, 'true'), 330, 170, '100% TRUE', { size: 64, color: D.GREEN });
    say(c(4, 'simple English'), 960, 175, 'simple English', { size: 88 });
    D.draw(c(4, 'No long lectures'), 0.5, D.at(960, 470, 2.6, L.cross(D.RED)));
    say(c(4, 'good part'), 1580, 175, 'just the good part!', { size: 76, color: D.GREEN });
  });

  // 5. Sources in the description.
  scene(D.sectionStart(5), () => {
    picture(D.sectionStart(5) - LEAD, 's5');
    say(c(5, 'sources'), 300, 300, 'Sources', { size: 120 });
    say(c(5, 'description'), 320, 420, 'in the description', { size: 66, color: D.BLUE });
    D.draw(c(5, 'description') + 0.5, 0.4, D.arrow(320, 470, 320, 650, { stroke: D.BLUE }));
    D.stamp(c(5, 'check every word'), 1600, 190, 'CHECK IT!', { size: 66, color: D.GREEN });
  });

  // 6. Saturday: a new story. Monday and Wednesday: Shorts.
  scene(D.sectionStart(6), () => {
    picture(D.sectionStart(6) - LEAD, 's6');
    say(c(6, 'Saturday'), 420, 300, 'SATURDAY', { size: 110, color: D.ORANGE, outline: D.INK, outlineWidth: 12 });
    say(c(6, 'new story'), 420, 400, 'a new story', { size: 72 });
    say(c(6, 'Monday'), 1500, 300, 'MON + WED', { size: 110, color: D.ORANGE, outline: D.INK, outlineWidth: 12 });
    say(c(6, 'short ones'), 1500, 400, 'Shorts', { size: 72 });
  });

  // 7. Grab your tea, subscribe, see you next tea break.
  scene(D.sectionStart(7), () => {
    picture(D.sectionStart(7) - LEAD, 's7');
    say(c(7, 'grab your tea'), 480, 160, 'Grab your tea', { size: 96 });
    D.stamp(c(7, 'subscribe'), 1450, 190, 'SUBSCRIBE', { size: 96, color: D.RED, rotate: -5 });
    say(c(7, 'next tea break'), 1450, 360, 'See you next tea break!', { size: 76, color: D.ORANGE });
  });

  D.tail = 2.5;
})();
