// Thumbnail for "The Emu War (1932)": one fully drawn board, rendered as a still at t = 3.
(function () {
  const D = Doodle;
  const L = D.lib;
  const put = (x, y, s, nodes, o) => D.at(x, y, s, nodes, o);
  const draw = (at, dur, x, y, s, nodes, o) => D.draw(at, dur, put(x, y, s, nodes, o));

  D.scene(0, () => {
    draw(0, 0.01, 0, 0, 1, D.rect(-20, -20, 1960, 1120, { fill: '#ffe066', fillStyle: 'solid', stroke: 'none' }));
    // the winner: a big proud emu with a trophy
    draw(0, 0.5, 1380, 640, 1.45, L.emu());
    draw(0, 0.5, 1730, 860, 0.9, L.trophy());
    // the loser: a soldier with a jammed gun
    draw(0, 0.5, 330, 830, 1.35, L.person({ hat: 'slouch', torso: '#a8895a', arms: [[[-30, -120], [60, -80]], [[30, -120], [110, -85]]] }));
    draw(0, 0.5, 580, 730, 0.95, L.gun());
    D.pop(0, put(640, 640, 0.75, L.burst(140)));
    D.write(0.1, 640, 662, 'JAMMED!', { size: 66, color: D.RED, dur: 0.2 });
    D.write(0.2, 960, 250, 'EMUS WON?!', { size: 250, color: D.ORANGE, outline: D.INK, outlineWidth: 16, dur: 0.3 });
  });
  D.tail = 4;
})();
