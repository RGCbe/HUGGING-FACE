// Thumbnail for "The Pig War (1859)": the pig between the cannons (img/p14.png) with big words,
// rendered as a still at t = 3 (render.mjs --data passes {"img": DIR}).
(function () {
  const D = Doodle;

  D.scene(0, () => {
    D.image(0, 0.01, `${window.DATA.img}/p14.png`, 0, 0, D.W, D.H, { zoom: 0 });
    D.write(0.1, 960, 250, 'WAR OVER A PIG?!', { size: 210, color: D.ORANGE, outline: D.INK, outlineWidth: 18, dur: 0.3 });
    D.stamp(0.2, 1400, 470, '1859', { size: 110, color: D.RED, rotate: -8 });
  });
  D.tail = 4;
})();
