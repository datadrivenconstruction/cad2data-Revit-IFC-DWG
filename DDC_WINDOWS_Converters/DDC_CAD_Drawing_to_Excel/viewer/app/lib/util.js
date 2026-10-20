// DDC Viewer — small own helpers: polygon measurement and an animation driver.
(function (g) {
  'use strict';
  const DDCV = g.DDCV = g.DDCV || {};

  // Points are {x, y, z} (THREE.Vector3 fits).
  const sub = (a, b) => [a.x - b.x, a.y - b.y, a.z - b.z];
  const len = (v) => Math.hypot(v[0], v[1], v[2]);
  DDCV.geom = {
    dist: (a, b) => len(sub(a, b)),
    // Area of a planar polygon in space: half the length of the summed fan cross products.
    area(pts) {
      if (pts.length < 3) return 0;
      const o = pts[0]; let sx = 0, sy = 0, sz = 0;
      for (let i = 1; i + 1 < pts.length; i++) {
        const u = sub(pts[i], o), w = sub(pts[i + 1], o);
        sx += u[1] * w[2] - u[2] * w[1]; sy += u[2] * w[0] - u[0] * w[2]; sz += u[0] * w[1] - u[1] * w[0];
      }
      return Math.hypot(sx, sy, sz) / 2;
    },
    perimeter(pts) {
      let s = 0;
      for (let i = 0; i < pts.length; i++) s += len(sub(pts[i], pts[(i + 1) % pts.length]));
      return pts.length > 1 ? s : 0;
    },
    centre(pts) {
      const n = pts.length || 1; let x = 0, y = 0, z = 0;
      for (const p of pts) { x += p.x; y += p.y; z += p.z; }
      return { x: x / n, y: y / n, z: z / n };
    },
  };

  // Animates numeric arrays from -> to over ms with smoothstep easing; start() returns a stop function.
  class Tween {
    constructor() { this.id = 0; }
    stop() { this.id++; }
    start(from, to, ms, apply) {
      const id = ++this.id, t0 = performance.now();
      const keys = Object.keys(to);
      const frame = (now) => {
        if (id !== this.id) return;
        const k = Math.min(1, (now - t0) / Math.max(ms, 1)), e = k * k * (3 - 2 * k);
        const state = {};
        for (const key of keys) state[key] = to[key].map((v, i) => from[key][i] + (v - from[key][i]) * e);
        apply(state);
        if (k < 1) requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
      return () => this.stop();
    }
  }
  DDCV.Tween = Tween;
})(typeof window !== 'undefined' ? window : globalThis);
