// Thumbnail for "The Emu War (1932)": the winner's-podium picture (img/e18.png) with big words,
// rendered as a still at t = 3 (render.mjs --data passes {"img": DIR}).
(function () {
  const D = Doodle;

  D.scene(0, () => {
    D.image(0, 0.01, `${window.DATA.img}/e18.png`, 0, 0, D.W, D.H, { zoom: 0 });
    D.write(0.1, 960, 250, 'EMUS WON?!', { size: 260, color: D.ORANGE, outline: D.INK, outlineWidth: 18, dur: 0.3 });
    D.stamp(0.2, 330, 820, '1932', { size: 110, color: D.RED, rotate: -8 });
  });
  D.tail = 4;
})();
