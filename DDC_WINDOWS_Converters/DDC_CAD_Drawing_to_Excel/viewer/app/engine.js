// DDC Viewer — rendering engine (three.js r185, own controls, GPU picking, 2D/3D views).
(function (g) {
  'use strict';
  const DDCV = g.DDCV = g.DDCV || {};
  const THREE = g.THREE;
  const HIDDEN = 0, NORMAL = 1, GHOST = 2, SELECTED = 3;
  const NONE = 0xFFFFFFFF;
  const nextFrame = () => new Promise((r) => requestAnimationFrame(() => r()));

  // ---------------------------------------------------------------- 3D material
  const VERT = `
    attribute vec4 aColor; attribute vec3 aPick; attribute float aState;
    varying vec4 vColor; varying vec3 vPick; varying float vState; varying vec3 vWorld; varying vec3 vView;
    #include <clipping_planes_pars_vertex>
    void main() {
      vColor = aColor; vPick = aPick; vState = aState;
      #include <begin_vertex>
      #include <project_vertex>
      #include <clipping_planes_vertex>
      vWorld = (modelMatrix * vec4(position, 1.0)).xyz; vView = -mvPosition.xyz;
    }`;
  const FRAG = `
    uniform int uMode; uniform vec3 uSel; uniform float uGhost;
    varying vec4 vColor; varying vec3 vPick; varying float vState; varying vec3 vWorld; varying vec3 vView;
    #include <clipping_planes_pars_fragment>
    void main() {
      #include <clipping_planes_fragment>
      float s = floor(vState + 0.5);
      if (s < 0.5) discard;
      bool ghost = s > 1.5 && s < 2.5;
      if (uMode == 1) { if (!ghost) discard; } else if (ghost) discard;
      if (uMode == 2) { gl_FragColor = vec4(vPick, 1.0); return; }
      if (uMode == 3) {
        float v = floor(clamp(gl_FragCoord.z, 0.0, 1.0) * 16777215.0);
        float r = floor(v / 65536.0); float g = floor((v - r * 65536.0) / 256.0); float b = v - r * 65536.0 - g * 256.0;
        gl_FragColor = vec4(r / 255.0, g / 255.0, b / 255.0, 1.0); return;
      }
      vec3 n = normalize(cross(dFdx(vWorld), dFdy(vWorld)));
      if (dot(n, cameraPosition - vWorld) < 0.0) n = -n;
      vec3 base = s > 2.5 ? uSel : vColor.rgb;
      float key = max(dot(n, normalize(vec3(0.42, -0.62, 0.66))), 0.0);
      float fill = max(dot(n, normalize(vec3(-0.6, 0.5, 0.25))), 0.0);
      float shade = 0.34 + 0.52 * key + 0.16 * fill + 0.10 * (0.5 + 0.5 * n.z);
      vec3 c = base * shade;
      float a = uMode == 1 ? uGhost : vColor.a;
      if (s > 2.5) a = max(a, 0.85);
      gl_FragColor = vec4(c, a);
      #include <colorspace_fragment>
    }`;

  function makeMeshMaterial(mode, transparent) {
    const m = new THREE.ShaderMaterial({
      vertexShader: VERT, fragmentShader: FRAG,
      uniforms: { uMode: { value: mode }, uSel: { value: new THREE.Color('#ff8a1f') }, uGhost: { value: 0.09 } },
      clipping: true, side: THREE.DoubleSide,
      transparent: mode === 1 || transparent, depthWrite: !(mode === 1 || transparent),
    });
    if (mode === 0 && !transparent) { m.polygonOffset = true; m.polygonOffsetFactor = 1; m.polygonOffsetUnits = 1; }
    return m;
  }

  function hexToRgb(hex) {
    const v = parseInt(String(hex || '#999999').slice(1, 7), 16);
    return [(v >> 16) & 255, (v >> 8) & 255, v & 255];
  }

  // ---------------------------------------------------------------- engine
  class Engine {
    constructor(container, overlay, hooks) {
      this.container = container; this.overlay = overlay; this.hooks = hooks || {};
      this.ctx2d = overlay.getContext('2d');
      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: false });
      this.renderer.setPixelRatio(Math.min(2, g.devicePixelRatio || 1));
      this.renderer.localClippingEnabled = true;
      container.appendChild(this.renderer.domElement);
      this.scene = new THREE.Scene();
      this.persp = new THREE.PerspectiveCamera(45, 1, 0.01, 1e7);
      this.ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, -1e7, 1e7);
      for (const c of [this.persp, this.ortho]) c.up.set(0, 0, 1);
      this.camera = this.persp;
      this.target = new THREE.Vector3();
      this.radius = 10; this.theta = -Math.PI / 4; this.phi = Math.PI / 3; // azimuth around Z, polar from +Z
      this.mode = '3d'; this.projection = 'perspective';
      this.root = new THREE.Group(); this.scene.add(this.root);
      this.pickTarget = new THREE.WebGLRenderTarget(1, 1);
      this.pickBuf = new Uint8Array(4);
      this.tween = new DDCV.Tween();
      this.dirty = true; this.walk = null; this.tool = null; this.measures = []; this.draft = null;
      this.entityRanges = new Map(); // 3D: id -> [[geomIndex,start,count]]
      this.geoms = []; this.lines2d = []; this.texts = []; this.state = null;
      this.sectionPlanes = []; this.sectionBox = null;
      this.theme = { bg: '#f4f7fb', ink: [22, 45, 72], paper: '#ffffff' };
      this._bindInput();
      this._resize();
      new ResizeObserver(() => this._resize()).observe(container);
      const loop = () => {
        requestAnimationFrame(loop);
        const now = performance.now();
        if (this.walk) this._walkTick((now - (this._last || now)) / 1000);
        this._last = now;
        if (this.dirty) { this.dirty = false; this.render(); }
      };
      requestAnimationFrame(loop);
    }

    // ------------------------------------------------------------ setup
    setTheme(dark) {
      this.dark = dark;
      this.theme = dark ? { bg: '#0f1d2e', ink: [233, 241, 252], paper: '#13263c', grid: '#1d3550' }
                        : { bg: '#eef3f9', ink: [22, 45, 72], paper: '#ffffff', grid: '#dde7f2' };
      this.scene.background = new THREE.Color(this.theme.bg);
      if (this.paperMesh) this.paperMesh.material.color.set(this.theme.paper);
      if (this.doc && this.mode === '2d') this._recolour2d();
      this.dirty = true;
    }

    _resize() {
      const w = Math.max(1, this.container.clientWidth), h = Math.max(1, this.container.clientHeight);
      this.renderer.setSize(w, h, false);
      this.renderer.domElement.style.width = w + 'px'; this.renderer.domElement.style.height = h + 'px';
      const pr = this.renderer.getPixelRatio();
      this.overlay.width = Math.round(w * pr); this.overlay.height = Math.round(h * pr);
      this.overlay.style.width = w + 'px'; this.overlay.style.height = h + 'px';
      this.w = w; this.h = h;
      this._applyCamera();
    }

    clear() {
      this.tween.stop();
      this.root.traverse((o) => { if (o.geometry) o.geometry.dispose(); });
      this.scene.remove(this.root); this.root = new THREE.Group(); this.scene.add(this.root);
      this.entityRanges.clear(); this.geoms = []; this.lines2d = []; this.texts = []; this.fills2d = [];
      this.measures = []; this.draft = null; this.paperMesh = null; this.grid = null; this.selected = new Set();
      this.viewportRefs = []; this.edges = null; this.fitBox = null;
      this.dirty = true;
    }

    // ------------------------------------------------------------ 3D build
    async build3d(doc, view, progress) {
      this.clear(); this.doc = doc; this.view = view; this.mode = '3d';
      const origin = view.origin || [0, 0, 0];
      this.origin = origin;
      const mats = doc.materials;
      const n = doc.entities.length;
      this.state = new Uint8Array(n).fill(NORMAL);
      this.baseColour = new Map();
      let done = 0; let t0 = performance.now();
      const total = view.meshes.reduce((s, m) => s + doc.buf(m.ranges).length / 4, 0) || 1;
      for (const mesh of view.meshes) {
        const pos = doc.buf(mesh.positions), idx = doc.buf(mesh.indices), ranges = doc.buf(mesh.ranges);
        // split ranges by transparency so transparent elements are drawn after opaque ones
        for (const transparent of [false, true]) {
          let vcount = 0, icount = 0; const sel = [];
          for (let r = 0; r < ranges.length; r += 4) {
            const m = mats[ranges[r + 3]] || {};
            const tr = (m.opacity !== undefined && m.opacity < 0.99);
            if (tr !== transparent) continue;
            sel.push(r); vcount += ranges[r + 2];
          }
          if (!sel.length) continue;
          // index ranges are encoded per element as triangles referencing its own vertex span
          const P = new Float32Array(vcount * 3), C = new Uint8Array(vcount * 4), K = new Uint8Array(vcount * 3), S = new Uint8Array(vcount).fill(NORMAL);
          const Iparts = []; let vbase = 0;
          const geomIndex = this.geoms.length;
          for (const r of sel) {
            const id = ranges[r], v0 = ranges[r + 1], vc = ranges[r + 2], m = mats[ranges[r + 3]] || {};
            P.set(pos.subarray(v0 * 3, (v0 + vc) * 3), vbase * 3);
            const rgb = hexToRgb(m.colour); const a = Math.round(255 * (m.opacity === undefined ? 1 : m.opacity));
            const pid = id + 1;
            for (let v = 0; v < vc; v++) {
              const o = (vbase + v) * 4; C[o] = rgb[0]; C[o + 1] = rgb[1]; C[o + 2] = rgb[2]; C[o + 3] = a;
              const k = (vbase + v) * 3; K[k] = pid & 255; K[k + 1] = (pid >> 8) & 255; K[k + 2] = (pid >> 16) & 255;
            }
            let list = this.entityRanges.get(id); if (!list) this.entityRanges.set(id, list = []);
            list.push([geomIndex, vbase, vc]);
            Iparts.push([v0, vc, vbase]);
            vbase += vc; done++;
            if (performance.now() - t0 > 40) { progress && progress(done / total); await nextFrame(); t0 = performance.now(); }
          }
          // remap indices: element vertex span [v0, v0+vc) -> [vbase, vbase+vc)
          const I = this._remapIndices(idx, Iparts, new Uint32Array(idx.length)).slice();
          const geom = new THREE.BufferGeometry();
          geom.setAttribute('position', new THREE.BufferAttribute(P, 3));
          geom.setAttribute('aColor', new THREE.BufferAttribute(C, 4, true));
          geom.setAttribute('aPick', new THREE.BufferAttribute(K, 3, true));
          geom.setAttribute('aState', new THREE.BufferAttribute(S, 1, false));
          geom.setIndex(new THREE.BufferAttribute(I, 1));
          geom.computeBoundingBox(); geom.computeBoundingSphere();
          const solid = new THREE.Mesh(geom, makeMeshMaterial(0, transparent));
          const ghost = new THREE.Mesh(geom, makeMeshMaterial(1, true)); ghost.renderOrder = 2;
          if (transparent) solid.renderOrder = 1;
          solid.userData.pickable = true;
          this.root.add(solid); this.root.add(ghost);
          this.geoms.push({ geom, solid, ghost, baseColour: C.slice() });
        }
      }
      this._buildEdges();
      this.bbox = new THREE.Box3().setFromObject(this.root);
      if (this.bbox.isEmpty()) this.bbox.set(new THREE.Vector3(-1, -1, -1), new THREE.Vector3(1, 1, 1));
      this.setProjection('perspective', true);
      this.fit(false);
      this.dirty = true;
    }

    _countIndices(idx, parts, nverts) {
      // indices of an element lie in its vertex span; build per-span triangle lists once
      if (!this._spanTri || this._spanTriSrc !== idx) {
        // owner span of each index triple via vertex -> span start lookup
        this._spanTriSrc = idx;
      }
      return idx.length; // upper bound, trimmed in _remapIndices
    }

    _remapIndices(idx, parts, out) {
      // vertex -> new index map for the selected spans
      let maxV = 0; for (const [v0, vc] of parts) maxV = Math.max(maxV, v0 + vc);
      const map = new Int32Array(maxV).fill(-1);
      for (const [v0, vc, nb] of parts) for (let v = 0; v < vc; v++) map[v0 + v] = nb + v;
      let k = 0;
      for (let i = 0; i + 2 < idx.length; i += 3) {
        const a = idx[i], b = idx[i + 1], c = idx[i + 2];
        if (a >= maxV || b >= maxV || c >= maxV) continue;
        const ma = map[a], mb = map[b], mc = map[c];
        if (ma < 0 || mb < 0 || mc < 0) continue;
        out[k++] = ma; out[k++] = mb; out[k++] = mc;
      }
      // shrink view (BufferAttribute uses array.length as count)
      const trimmed = out.subarray(0, k);
      out.__trimmed = trimmed;
      return trimmed;
    }

    _buildEdges() {
      let tris = 0; for (const g2 of this.geoms) tris += g2.geom.index.count / 3;
      this.edgesAvailable = tris > 0 && tris < 2500000;
      this.edgesGroup = new THREE.Group(); this.root.add(this.edgesGroup);
      this.edgesOn = this.edgesAvailable;
      if (!this.edgesAvailable) return;
      for (const g2 of this.geoms) {
        // geometry index was trimmed: rebuild an attribute from the trimmed view if needed
        const e = new THREE.EdgesGeometry(g2.geom, 30);
        const l = new THREE.LineSegments(e, new THREE.LineBasicMaterial({ color: 0x1b2b3d, transparent: true, opacity: 0.35 }));
        l.renderOrder = 0; this.edgesGroup.add(l);
      }
    }

    setEdges(on) { this.edgesOn = on && this.edgesAvailable; this._syncEdges(); }
    _syncEdges() {
      if (!this.edgesGroup) return;
      const anyHidden = this.state && this.state.some((s) => s !== NORMAL && s !== SELECTED);
      this.edgesGroup.visible = !!this.edgesOn && !anyHidden;
      for (const l of this.edgesGroup.children) l.material.color.set(this.dark ? 0x9fb6cf : 0x1b2b3d);
      this.dirty = true;
    }

    // ------------------------------------------------------------ 2D build
    async build2d(doc, view, progress) {
      this.clear(); this.doc = doc; this.view = view; this.mode = '2d';
      const n = doc.entities.length;
      this.state = new Uint8Array(n).fill(NORMAL);
      this.layerGroups = new Map();
      const group = await this._viewGroup(doc, view, progress, true);
      this.root.add(group);
      // viewports: model view by reference (shared geometry), clipped to the viewport rectangle
      for (const vp of view.viewports || []) {
        const src = doc.views.find((v) => v.id === vp.view);
        if (!src) continue;
        const inner = await this._viewGroup(doc, src, null, false);
        const m = vp.matrix; const M = new THREE.Matrix4().set(m[0], m[2], 0, m[4], m[1], m[3], 0, m[5], 0, 0, 1, 0, 0, 0, 0, 1);
        inner.matrixAutoUpdate = false; inner.matrix.copy(M);
        const [x0, y0, x1, y1] = vp.rect;
        const planes = [new THREE.Plane(new THREE.Vector3(1, 0, 0), -x0), new THREE.Plane(new THREE.Vector3(-1, 0, 0), x1),
                        new THREE.Plane(new THREE.Vector3(0, 1, 0), -y0), new THREE.Plane(new THREE.Vector3(0, -1, 0), y1)];
        inner.traverse((o) => { if (o.material) { o.material = o.material.clone(); o.material.clippingPlanes = planes; } });
        this.root.add(inner);
        this.viewportRefs.push({ vp, src, inverse: M.clone().invert(), group: inner });
      }
      const e = view.extent || { min: [-1, -1], max: [1, 1] };
      if (view.space === 'paper') {
        const o = view.origin || [0, 0];
        const w = e.max[0] - e.min[0], h = e.max[1] - e.min[1], pad = Math.max(w, h) * 0.03;
        const geo = new THREE.PlaneGeometry(w + 2 * pad, h + 2 * pad);
        this.paperMesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: this.theme.paper }));
        this.paperMesh.position.set((e.min[0] + e.max[0]) / 2 - o[0], (e.min[1] + e.max[1]) / 2 - o[1], -1e-3);
        this.paperMesh.renderOrder = -1;
        this.root.add(this.paperMesh);
      }
      const o = view.origin || [0, 0];
      this.bbox = new THREE.Box3(new THREE.Vector3(e.min[0] - o[0], e.min[1] - o[1], 0), new THREE.Vector3(e.max[0] - o[0], e.max[1] - o[1], 0));
      if (this.bbox.isEmpty()) this.bbox.set(new THREE.Vector3(-1, -1, 0), new THREE.Vector3(1, 1, 0));
      this.origin = [o[0], o[1], 0];
      this.theta = -Math.PI / 2; this.phi = 1e-4;
      this.setProjection('orthographic', true);
      const fe = view.fit_extent;
      this.fitBox = fe ? new THREE.Box3(new THREE.Vector3(fe.min[0] - o[0], fe.min[1] - o[1], 0), new THREE.Vector3(fe.max[0] - o[0], fe.max[1] - o[1], 0)) : null;
      this.fit(false, this.fitBox);
      this._recolour2d();
    }

    async _viewGroup(doc, view, progress, primary) {
      this._viewCache = this._viewCache || new Map();
      const cached = this._viewCache.get(view.id);
      if (cached && cached.doc === doc) {
        const g2 = new THREE.Group();
        for (const child of cached.group.children) { const c = child.clone(); c.material = child.material; g2.add(c); }
        return g2;
      }
      const group = new THREE.Group();
      const batches = view.batches || [];
      let t0 = performance.now(); let i = 0;
      const ink = this.theme.ink;
      for (const b of batches) {
        i++;
        const layer = doc.layers[b.layer] || {};
        const ents = doc.buf(b.entities);
        if (b.type === 'lines') {
          const p2 = doc.buf(b.positions); const nv = p2.length / 2;
          const P = new Float32Array(nv * 3);
          for (let v = 0; v < nv; v++) { P[v * 3] = p2[v * 2]; P[v * 3 + 1] = p2[v * 2 + 1]; }
          const C = new Uint8Array(nv * 4);
          const geo = new THREE.BufferGeometry();
          geo.setAttribute('position', new THREE.BufferAttribute(P, 3));
          geo.setAttribute('color', new THREE.BufferAttribute(C, 4, true));
          let mat;
          if (b.dash && b.dash.length >= 2 && Math.abs(b.dash[0]) > 0) {
            mat = new THREE.LineDashedMaterial({ vertexColors: true, transparent: true, dashSize: Math.abs(b.dash[0]), gapSize: Math.abs(b.dash[1]) || Math.abs(b.dash[0]) });
          } else mat = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true });
          const obj = new THREE.LineSegments(geo, mat);
          if (mat.isLineDashedMaterial) obj.computeLineDistances();
          obj.userData = { batch: b, layer: b.layer, ents, kind: 'lines', base: hexToRgb(b.colour), view };
          obj.frustumCulled = false;
          group.add(obj);
          if (primary || true) this.lines2d.push(obj);
        } else if (b.type === 'fills') {
          const p2 = doc.buf(b.positions), rings = doc.buf(b.rings), polys = doc.buf(b.polygons);
          const P = []; const triEnt = []; let triCount = 0;
          const ringEnd = (r) => (r + 1 < rings.length ? rings[r + 1] : p2.length / 2);
          for (let k = 0; k < polys.length; k++) {
            const r0 = polys[k], r1 = k + 1 < polys.length ? polys[k + 1] : rings.length;
            const toV = (r) => { const out = []; for (let v = rings[r]; v < ringEnd(r); v++) out.push(new THREE.Vector2(p2[v * 2], p2[v * 2 + 1])); return out; };
            const outer = toV(r0); const holes = [];
            for (let r = r0 + 1; r < r1; r++) holes.push(toV(r));
            let faces;
            try { faces = THREE.ShapeUtils.triangulateShape(outer, holes); } catch (e) { faces = []; }
            const all = outer.concat(...holes);
            for (const f of faces) { for (const vi of f) P.push(all[vi].x, all[vi].y, 0); triEnt.push(ents[k]); triCount++; }
            if (performance.now() - t0 > 40) { progress && progress(i / batches.length); await nextFrame(); t0 = performance.now(); }
          }
          if (!triCount) continue;
          const geo = new THREE.BufferGeometry();
          geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(P), 3));
          geo.setAttribute('color', new THREE.BufferAttribute(new Uint8Array(triCount * 12), 4, true));
          const op = b.opacity === null || b.opacity === undefined ? 1 : b.opacity;
          const mat = new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, opacity: 1, depthWrite: false, side: THREE.DoubleSide });
          const obj = new THREE.Mesh(geo, mat); obj.renderOrder = -0.5; obj.frustumCulled = false;
          obj.userData = { batch: b, layer: b.layer, ents: Uint32Array.from(triEnt), kind: 'fills', base: hexToRgb(b.colour), alpha: op, view };
          group.add(obj); this.lines2d.push(obj);
          // keep polygons for picking
          (this.fills2d = this.fills2d || []).push({ view, p2, rings, polys, ents });
        }
        if (performance.now() - t0 > 40) { progress && progress(i / batches.length); await nextFrame(); t0 = performance.now(); }
      }
      // texts are drawn on the overlay canvas
      for (const t of view.texts || []) this.texts.push({ t, view, M: null });
      this._viewCache.set(view.id, { doc, group });
      group.userData.view = view;
      return group;
    }

    _recolour2d() {
      if (!this.doc) return;
      const ink = this.theme.ink, dark = this.dark;
      const layers = this.doc.layers;
      for (const obj of this.lines2d) {
        const u = obj.userData; const C = obj.geometry.attributes.color.array;
        const per = u.kind === 'lines' ? 2 : 3;
        let rgb = u.colourBy ? null : this._themeColour(u.base);
        const alpha0 = Math.round(255 * (u.alpha === undefined ? 1 : u.alpha));
        const layerHidden = layers[u.layer] && layers[u.layer]._off;
        obj.visible = !layerHidden;
        for (let s = 0; s < u.ents.length; s++) {
          const id = u.ents[s];
          const st = id === NONE ? NORMAL : this.state[id];
          let c = rgb;
          if (u.colourBy) c = u.colourBy(id) || this._themeColour(u.base);
          let a = alpha0;
          if (st === HIDDEN) a = 0; else if (st === GHOST) a = Math.round(alpha0 * 0.12);
          if (st === SELECTED) c = [255, 138, 31];
          for (let k = 0; k < per; k++) { const o = (s * per + k) * 4; C[o] = c[0]; C[o + 1] = c[1]; C[o + 2] = c[2]; C[o + 3] = a; }
        }
        obj.geometry.attributes.color.needsUpdate = true;
      }
      this.dirty = true;
    }

    _themeColour(rgb) {
      const lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2];
      if (this.dark) {
        if (lum < 40) return this.theme.ink;
        return rgb;
      }
      if (lum > 235) return this.theme.ink;
      if (rgb[0] === 0 && rgb[1] === 0 && rgb[2] === 0) return this.theme.ink;
      // light theme: darken very light colours (yellow, cyan) for contrast on white
      if (lum > 190) return [Math.round(rgb[0] * 0.72), Math.round(rgb[1] * 0.72), Math.round(rgb[2] * 0.72)];
      return rgb;
    }

    setLayerVisible(index, on) {
      const l = this.doc.layers[index]; if (!l) return;
      l._off = !on;
      for (const obj of this.lines2d) if (obj.userData.layer === index) obj.visible = on;
      this.dirty = true;
    }

    // ------------------------------------------------------------ camera
    setProjection(kind, silent) {
      this.projection = kind;
      this.camera = kind === 'orthographic' ? this.ortho : this.persp;
      this._applyCamera();
      if (!silent && this.hooks.onCamera) this.hooks.onCamera();
    }

    _viewHeight() { return 2 * this.radius * Math.tan(THREE.MathUtils.degToRad(this.persp.fov / 2)); }

    _applyCamera() {
      const aspect = (this.w || 1) / (this.h || 1);
      const dir = new THREE.Vector3(Math.sin(this.phi) * Math.cos(this.theta), Math.sin(this.phi) * Math.sin(this.theta), Math.cos(this.phi));
      const size = this.bbox ? this.bbox.getSize(new THREE.Vector3()).length() : 10;
      if (!this.walk) {
        this.persp.position.copy(this.target).addScaledVector(dir, this.radius);
        this.persp.near = Math.max(this.radius / 2000, size / 1e6); this.persp.far = this.radius * 20 + size * 4;
        this.persp.up.set(0, 0, 1);
        if (this.phi < 1e-3) this.persp.up.set(-Math.cos(this.theta), -Math.sin(this.theta), 0);
        this.persp.lookAt(this.target);
      }
      this.persp.aspect = aspect; this.persp.updateProjectionMatrix();
      const hh = this._viewHeight() / 2;
      this.ortho.left = -hh * aspect; this.ortho.right = hh * aspect; this.ortho.top = hh; this.ortho.bottom = -hh;
      const back = Math.max(this.radius, size * 2);
      this.ortho.position.copy(this.target).addScaledVector(dir, back);
      this.ortho.near = -size * 4; this.ortho.far = back + size * 8;
      this.ortho.up.set(0, 0, 1);
      if (this.phi < 1e-3) this.ortho.up.set(-Math.cos(this.theta), -Math.sin(this.theta), 0);
      this.ortho.lookAt(this.target);
      this.ortho.updateProjectionMatrix();
      this.dirty = true;
      if (this.hooks.onCamera) this.hooks.onCamera();
    }

    cameraState() { return { target: this.target.toArray(), radius: this.radius, theta: this.theta, phi: this.phi }; }

    fit(animate, box) {
      box = box || this.fitBox || this.bbox; if (!box) return;
      const c = box.getCenter(new THREE.Vector3()); const s = box.getSize(new THREE.Vector3());
      const aspect = (this.w || 1) / (this.h || 1);
      let r;
      if (this.mode === '2d') {
        r = Math.max(s.y, s.x / aspect) * 1.08 / (2 * Math.tan(THREE.MathUtils.degToRad(this.persp.fov / 2)));
      } else {
        const rad = Math.max(s.length() / 2, 1e-6);
        const v = THREE.MathUtils.degToRad(this.persp.fov / 2), hz = Math.atan(Math.tan(v) * aspect);
        r = rad / Math.sin(Math.min(v, hz)) * 0.9;
      }
      this.animateTo(c, Math.max(r, 1e-6), this.theta, this.phi, animate);
    }

    animateTo(target, radius, theta, phi, animate) {
      if (!animate) { this.target.copy(target); this.radius = radius; this.theta = theta; this.phi = phi; this._applyCamera(); return; }
      const from = { orbit: [this.theta, this.phi, this.radius], target: this.target.toArray() };
      let dTheta = theta - this.theta; while (dTheta > Math.PI) dTheta -= 2 * Math.PI; while (dTheta < -Math.PI) dTheta += 2 * Math.PI;
      const to = { orbit: [this.theta + dTheta, phi, radius], target: target.toArray() };
      this.tween.start(from, to, 450, (st) => {
        [this.theta, this.phi, this.radius] = st.orbit;
        this.target.fromArray(st.target); this._applyCamera();
      });
    }

    viewPreset(normal) {
      const [x, y, z] = normal; const len = Math.hypot(x, y, z) || 1;
      const phi = Math.acos(Math.max(-1, Math.min(1, z / len)));
      const theta = (Math.abs(x) < 1e-9 && Math.abs(y) < 1e-9) ? this.theta : Math.atan2(y, x);
      this.animateTo(this.target.clone(), this.radius, theta, Math.max(1e-4, Math.min(Math.PI - 1e-4, phi)), true);
    }

    zoomToEntities(ids) {
      const box = this.entitiesBox(ids);
      const total = this.bbox ? this.bbox.getSize(new THREE.Vector3()).length() : 1;
      if (box && !box.isEmpty()) this.fit(true, box.expandByScalar(Math.max(box.getSize(new THREE.Vector3()).length() * 0.6, total * 1e-4, 1e-3)));
    }

    entitiesBox(ids) {
      const box = new THREE.Box3(); const v = new THREE.Vector3();
      if (this.mode === '3d') {
        for (const id of ids) for (const [gi, st, ct] of this.entityRanges.get(id) || []) {
          const P = this.geoms[gi].geom.attributes.position.array;
          for (let k = st; k < st + ct; k++) box.expandByPoint(v.set(P[k * 3], P[k * 3 + 1], P[k * 3 + 2]));
        }
      } else {
        const set = new Set(ids);
        for (const obj of this.lines2d) {
          if (obj.userData.view !== this.view) continue;
          const u = obj.userData; const P = obj.geometry.attributes.position.array; const per = u.kind === 'lines' ? 2 : 3;
          for (let s = 0; s < u.ents.length; s++) if (set.has(u.ents[s])) for (let k = 0; k < per; k++) box.expandByPoint(v.fromArray(P, (s * per + k) * 3));
        }
        for (const tx of this.texts) if (tx.view === this.view && set.has(tx.t[0])) {
          const t = tx.t, h = Math.hypot(t[7], t[8]), w = Math.max(1, ...t[10].map((x) => x.length)) * 0.62 * Math.hypot(t[5], t[6]);
          box.expandByPoint(v.set(t[3] - w, t[4] - h * 2, 0)); box.expandByPoint(v.set(t[3] + w, t[4] + h * (t[10].length * 1.7 + 1), 0));
        }
      }
      return box;
    }

    // ------------------------------------------------------------ state
    setStates(changes) {
      // changes: Map id -> state
      if (this.mode === '3d') {
        const touched = new Set();
        for (const [id, s] of changes) {
          this.state[id] = s;
          for (const [gi, st, ct] of this.entityRanges.get(id) || []) { this.geoms[gi].geom.attributes.aState.array.fill(s, st, st + ct); touched.add(gi); }
        }
        for (const gi of touched) this.geoms[gi].geom.attributes.aState.needsUpdate = true;
        this._syncEdges();
      } else {
        for (const [id, s] of changes) this.state[id] = s;
        this._recolour2d();
      }
      this.dirty = true;
    }

    resetStates(base) {
      this.state.fill(base === undefined ? NORMAL : base);
      if (this.mode === '3d') { for (const g2 of this.geoms) { g2.geom.attributes.aState.array.fill(this.state[0] === undefined ? NORMAL : base === undefined ? NORMAL : base); g2.geom.attributes.aState.needsUpdate = true; } this._syncEdges(); }
      else this._recolour2d();
      this.dirty = true;
    }

    applyColourBy(fn) {
      // fn(id) -> [r,g,b] | null ; null fn restores
      if (this.mode === '3d') {
        for (const g2 of this.geoms) {
          const C = g2.geom.attributes.aColor.array; const K = g2.geom.attributes.aPick.array;
          C.set(g2.baseColour);
          if (fn) for (let v = 0; v < C.length / 4; v++) {
            const id = (K[v * 3] | (K[v * 3 + 1] << 8) | (K[v * 3 + 2] << 16)) - 1;
            const c = fn(id); if (c) { C[v * 4] = c[0]; C[v * 4 + 1] = c[1]; C[v * 4 + 2] = c[2]; }
          }
          g2.geom.attributes.aColor.needsUpdate = true;
        }
      } else {
        for (const obj of this.lines2d) obj.userData.colourBy = fn || null;
        this._recolour2d();
      }
      this.dirty = true;
    }

    // ------------------------------------------------------------ section
    setSection(planes) {
      this.renderer.clippingPlanes = planes || [];
      this.dirty = true;
    }

    // ------------------------------------------------------------ picking
    pick(x, y) {
      // returns {id, point(Vector3 world-local) | null}
      if (this.mode === '2d') return this._pick2d(x, y);
      if (!this.geoms.length) return { id: null, point: null };
      const cam = this.camera; const pr = this.renderer.getPixelRatio();
      const W = this.w * pr, H = this.h * pr;
      const px = Math.floor(x * pr), py = Math.floor(y * pr);
      const read = (mode) => {
        cam.setViewOffset(W, H, px, py, 1, 1);
        for (const g2 of this.geoms) { g2.solid.material.uniforms.uMode.value = mode; g2.ghost.visible = false; }
        const edgesVis = this.edgesGroup ? this.edgesGroup.visible : false; if (this.edgesGroup) this.edgesGroup.visible = false;
        const bg = this.scene.background; this.scene.background = null;
        this.renderer.setRenderTarget(this.pickTarget); this.renderer.setClearColor(0x000000, 0); this.renderer.clear();
        this.renderer.render(this.scene, cam);
        this.renderer.readRenderTargetPixels(this.pickTarget, 0, 0, 1, 1, this.pickBuf);
        this.renderer.setRenderTarget(null); this.scene.background = bg;
        for (const g2 of this.geoms) { g2.solid.material.uniforms.uMode.value = 0; g2.ghost.visible = true; }
        if (this.edgesGroup) this.edgesGroup.visible = edgesVis;
        cam.clearViewOffset();
        return this.pickBuf;
      };
      const b = read(2);
      const pid = b[0] | (b[1] << 8) | (b[2] << 16);
      let point = null;
      if (pid) {
        const d = read(3);
        const depth = (d[0] * 65536 + d[1] * 256 + d[2]) / 16777215;
        const ndc = new THREE.Vector3((x / this.w) * 2 - 1, -(y / this.h) * 2 + 1, depth * 2 - 1);
        point = ndc.unproject(cam);
      }
      this.dirty = true;
      return { id: pid ? pid - 1 : null, point };
    }

    screenToPlane(x, y) {
      const ndc = new THREE.Vector3((x / this.w) * 2 - 1, -(y / this.h) * 2 + 1, 0.5);
      const ray = new THREE.Raycaster(); ray.setFromCamera(new THREE.Vector2(ndc.x, ndc.y), this.camera);
      const p = new THREE.Vector3();
      return ray.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0, 0, 1), 0), p) ? p : null;
    }

    worldPerPixel() { return this._viewHeight() / (this.h || 1); }

    _index2d(view) {
      this._grids = this._grids || new Map();
      let G = this._grids.get(view.id); if (G) return G;
      const e = view.extent; const o = view.origin || [0, 0];
      const minx = (e ? e.min[0] : -1) - o[0], miny = (e ? e.min[1] : -1) - o[1];
      const maxx = (e ? e.max[0] : 1) - o[0], maxy = (e ? e.max[1] : 1) - o[1];
      const N = 192; const cw = Math.max((maxx - minx) / N, 1e-9), ch = Math.max((maxy - miny) / N, 1e-9);
      const cells = new Map(); const big = [];
      const segs = [];
      for (const b of view.batches || []) {
        if (b.type !== 'lines') continue;
        const p2 = this.doc.buf(b.positions), ents = this.doc.buf(b.entities);
        for (let s = 0; s < ents.length; s++) segs.push(p2, s, ents[s], b.layer);
      }
      for (let k = 0; k < segs.length; k += 4) {
        const p2 = segs[k], s = segs[k + 1];
        const ax = p2[s * 4], ay = p2[s * 4 + 1], bx = p2[s * 4 + 2], by = p2[s * 4 + 3];
        const i0 = Math.floor((Math.min(ax, bx) - minx) / cw), i1 = Math.floor((Math.max(ax, bx) - minx) / cw);
        const j0 = Math.floor((Math.min(ay, by) - miny) / ch), j1 = Math.floor((Math.max(ay, by) - miny) / ch);
        if ((i1 - i0 + 1) * (j1 - j0 + 1) > 256) { big.push(k); continue; }
        for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) { const key = i * 100003 + j; let c = cells.get(key); if (!c) cells.set(key, c = []); c.push(k); }
      }
      G = { minx, miny, cw, ch, cells, big, segs };
      this._grids.set(view.id, G);
      return G;
    }

    _nearest2d(view, x, y, tol, wantSnap) {
      const G = this._index2d(view);
      const layers = this.doc.layers;
      let best = null, bestD = tol;
      let snap = null, snapD = tol;
      const test = (k) => {
        const p2 = G.segs[k], s = G.segs[k + 1], id = G.segs[k + 2], layer = G.segs[k + 3];
        if ((layers[layer] && layers[layer]._off) || (id !== NONE && this.state[id] === HIDDEN)) return;
        const ax = p2[s * 4], ay = p2[s * 4 + 1], bx = p2[s * 4 + 2], by = p2[s * 4 + 3];
        const dx = bx - ax, dy = by - ay; const L = dx * dx + dy * dy;
        let t = L > 0 ? ((x - ax) * dx + (y - ay) * dy) / L : 0; t = Math.max(0, Math.min(1, t));
        const d = Math.hypot(ax + dx * t - x, ay + dy * t - y);
        if (d < bestD && id !== NONE) { bestD = d; best = id; }
        if (wantSnap) for (const [qx, qy] of [[ax, ay], [bx, by]]) { const dq = Math.hypot(qx - x, qy - y); if (dq < snapD) { snapD = dq; snap = [qx, qy]; } }
      };
      const ci = Math.floor((x - G.minx) / G.cw), cj = Math.floor((y - G.miny) / G.ch);
      const ri = Math.ceil(tol / G.cw), rj = Math.ceil(tol / G.ch);
      const seen = new Set();
      for (let i = ci - ri; i <= ci + ri; i++) for (let j = cj - rj; j <= cj + rj; j++) {
        const c = G.cells.get(i * 100003 + j); if (!c) continue;
        for (const k of c) if (!seen.has(k)) { seen.add(k); test(k); }
      }
      for (const k of G.big) test(k);
      return { id: best, snap };
    }

    _pickFill(view, x, y) {
      for (const f of this.fills2d || []) {
        if (f.view !== view) continue;
        const { p2, rings, polys, ents } = f;
        for (let k = polys.length - 1; k >= 0; k--) {
          const id = ents[k]; if (id === NONE || this.state[id] === HIDDEN) continue;
          const r0 = polys[k], r1 = k + 1 < polys.length ? polys[k + 1] : rings.length;
          let inside = false;
          for (let r = r0; r < r1; r++) {
            const a = rings[r], b = r + 1 < rings.length ? rings[r + 1] : p2.length / 2;
            for (let i = a, j = b - 1; i < b; j = i++) {
              const xi = p2[i * 2], yi = p2[i * 2 + 1], xj = p2[j * 2], yj = p2[j * 2 + 1];
              if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
            }
          }
          if (inside) return id;
        }
      }
      return null;
    }

    _pick2d(x, y, wantSnap) {
      const p = this.screenToPlane(x, y); if (!p) return { id: null, point: null };
      const tol = this.worldPerPixel() * 6;
      let r = this._nearest2d(this.view, p.x, p.y, tol, wantSnap);
      let id = r.id, snap = r.snap ? new THREE.Vector3(r.snap[0], r.snap[1], 0) : null;
      if (id === null) {
        for (const ref of this.viewportRefs || []) {
          const [x0, y0, x1, y1] = ref.vp.rect;
          if (p.x < x0 || p.x > x1 || p.y < y0 || p.y > y1) continue;
          const q = p.clone().applyMatrix4(ref.inverse);
          const scale = Math.hypot(ref.vp.matrix[0], ref.vp.matrix[1]) || 1;
          const rr = this._nearest2d(ref.src, q.x, q.y, tol / scale, false);
          if (rr.id !== null) { id = rr.id; break; }
        }
      }
      if (id === null) id = this._pickFill(this.view, p.x, p.y);
      if (id === null) {
        // texts: point inside the estimated box
        for (const tx of this.texts) {
          if (tx.view !== this.view) continue;
          const t = tx.t; const h = Math.hypot(t[7], t[8]); const w = Math.max(...t[10].map((s) => s.length)) * 0.62 * Math.hypot(t[5], t[6]);
          if (Math.abs(p.x - t[3]) < w + h && Math.abs(p.y - t[4]) < h * (t[10].length * 1.7 + 1)) { id = t[0]; break; }
        }
      }
      return { id: id === NONE ? null : id, point: snap || p, snapped: !!snap };
    }

    // ------------------------------------------------------------ input
    _bindInput() {
      const el = this.renderer.domElement; el.tabIndex = 0;
      let drag = null;
      el.addEventListener('contextmenu', (e) => e.preventDefault());
      el.addEventListener('pointerdown', (e) => {
        el.focus(); this.tween.stop();
        drag = { x: e.clientX, y: e.clientY, b: e.button, moved: false, shift: e.shiftKey };
        el.setPointerCapture(e.pointerId);
      });
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        this.mouse = { x: e.clientX - r.left, y: e.clientY - r.top };
        if (this.tool && !drag) { this.dirty = true; }
        if (!drag) return;
        const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
        if (!drag.moved && Math.hypot(dx, dy) < 3) return;
        drag.moved = true; drag.x = e.clientX; drag.y = e.clientY;
        if (this.walk) { this.walk.yaw -= dx * 0.004; this.walk.pitch = Math.max(-1.5, Math.min(1.5, this.walk.pitch - dy * 0.004)); this._walkApply(); return; }
        const pan = this.mode === '2d' ? (drag.b === 0 || drag.b === 1 || drag.b === 2) : (drag.b === 2 || drag.b === 1 || drag.shift);
        if (pan) this._pan(dx, dy);
        else { this.theta -= dx * 0.008; this.phi = Math.max(1e-4, Math.min(Math.PI - 1e-4, this.phi - dy * 0.008)); this._applyCamera(); }
      });
      el.addEventListener('pointerup', (e) => {
        const d = drag; drag = null;
        if (d && !d.moved && d.b === 0) {
          const r = el.getBoundingClientRect();
          if (this.hooks.onClick) this.hooks.onClick(e.clientX - r.left, e.clientY - r.top, e);
        }
      });
      el.addEventListener('dblclick', (e) => { if (this.hooks.onDblClick) { const r = el.getBoundingClientRect(); this.hooks.onDblClick(e.clientX - r.left, e.clientY - r.top, e); } });
      el.addEventListener('wheel', (e) => {
        e.preventDefault(); this.tween.stop();
        const r = el.getBoundingClientRect();
        const f = Math.pow(1.0015, e.deltaY * (e.deltaMode === 1 ? 30 : 1));
        if (this.walk) { this.walk.speed *= f > 1 ? 0.85 : 1.18; return; }
        this._zoomAt(e.clientX - r.left, e.clientY - r.top, f);
      }, { passive: false });
      // touch: pinch zoom handled by pointer events with two pointers
      const touches = new Map();
      el.addEventListener('pointerdown', (e) => { if (e.pointerType === 'touch') touches.set(e.pointerId, [e.clientX, e.clientY]); });
      el.addEventListener('pointermove', (e) => {
        if (e.pointerType !== 'touch' || !touches.has(e.pointerId) || touches.size !== 2) return;
        const [a, b] = [...touches.values()]; const d0 = Math.hypot(a[0] - b[0], a[1] - b[1]);
        touches.set(e.pointerId, [e.clientX, e.clientY]);
        const [c, d] = [...touches.values()]; const d1 = Math.hypot(c[0] - d[0], c[1] - d[1]);
        if (d0 > 0 && d1 > 0) { const r = el.getBoundingClientRect(); this._zoomAt((c[0] + d[0]) / 2 - r.left, (c[1] + d[1]) / 2 - r.top, d0 / d1); }
      });
      const drop = (e) => touches.delete(e.pointerId);
      el.addEventListener('pointerup', drop); el.addEventListener('pointercancel', drop);
    }

    _pan(dx, dy) {
      const wpp = this.worldPerPixel();
      const cam = this.camera; cam.updateMatrixWorld();
      const right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0);
      const up = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 1);
      this.target.addScaledVector(right, -dx * wpp).addScaledVector(up, dy * wpp);
      this._applyCamera();
    }

    _zoomAt(x, y, f) {
      const ndc = new THREE.Vector2((x / this.w) * 2 - 1, -(y / this.h) * 2 + 1);
      const ray = new THREE.Raycaster(); ray.setFromCamera(ndc, this.camera);
      const dir = new THREE.Vector3(); this.camera.getWorldDirection(dir);
      const p = new THREE.Vector3();
      if (ray.ray.intersectPlane(new THREE.Plane().setFromNormalAndCoplanarPoint(dir, this.target), p)) {
        this.target.lerp(p, 1 - f);
      }
      const size = this.bbox ? this.bbox.getSize(new THREE.Vector3()).length() : 10;
      this.radius = Math.max(size * 1e-6, Math.min(size * 50, this.radius * f));
      this._applyCamera();
    }

    // ------------------------------------------------------------ walk (WalkMode.ts mapping)
    setWalk(on) {
      if (on && this.mode !== '3d') return false;
      if (on) {
        this.setProjection('perspective');
        const size = this.bbox.getSize(new THREE.Vector3());
        const pos = this.persp.position.clone();
        const dir = new THREE.Vector3(); this.persp.getWorldDirection(dir);
        this.walk = { pos, yaw: Math.atan2(dir.y, dir.x), pitch: Math.asin(Math.max(-1, Math.min(1, dir.z))) * 0.3, speed: Math.max(size.length() / 25, 0.5), keys: new Set() };
        this._walkKeys = (e, down) => {
          if (e.target && /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
          if (down) this.walk && this.walk.keys.add(e.code); else this.walk && this.walk.keys.delete(e.code);
          if (e.key === 'Shift') this.walk && (this.walk.sprint = down);
        };
        this._kd = (e) => this._walkKeys(e, true); this._ku = (e) => this._walkKeys(e, false);
        g.addEventListener('keydown', this._kd); g.addEventListener('keyup', this._ku);
        this._walkApply();
      } else if (this.walk) {
        g.removeEventListener('keydown', this._kd); g.removeEventListener('keyup', this._ku);
        const dir = new THREE.Vector3(); this.persp.getWorldDirection(dir);
        this.target.copy(this.persp.position).addScaledVector(dir, Math.max(this.radius * 0.3, 1));
        const off = this.persp.position.clone().sub(this.target);
        this.radius = off.length(); this.phi = Math.acos(Math.max(-1, Math.min(1, off.z / this.radius))); this.theta = Math.atan2(off.y, off.x);
        this.walk = null; this._applyCamera();
      }
      return true;
    }

    _walkApply() {
      const w = this.walk; const c = this.persp;
      c.position.copy(w.pos); c.up.set(0, 0, 1);
      const look = new THREE.Vector3(Math.cos(w.yaw) * Math.cos(w.pitch), Math.sin(w.yaw) * Math.cos(w.pitch), Math.sin(w.pitch));
      c.lookAt(w.pos.clone().add(look));
      c.near = Math.max(0.01, w.speed / 500); c.far = this.bbox.getSize(new THREE.Vector3()).length() * 10 + 1000; c.updateProjectionMatrix();
      this.dirty = true;
      if (this.hooks.onCamera) this.hooks.onCamera();
    }

    _walkTick(dt) {
      const w = this.walk; if (!w || !w.keys.size) return;
      const K = { forward: ['KeyW', 'ArrowUp'], back: ['KeyS', 'ArrowDown'], left: ['KeyA', 'ArrowLeft'], right: ['KeyD', 'ArrowRight'],
                  up: ['KeyE', 'PageUp'], down: ['KeyQ', 'PageDown'] };
      const has = (a) => a.some((k) => w.keys.has(k));
      const v = w.speed * dt * (w.sprint ? 3 : 1);
      const fwd = new THREE.Vector3(Math.cos(w.yaw), Math.sin(w.yaw), 0); const right = new THREE.Vector3(Math.sin(w.yaw), -Math.cos(w.yaw), 0);
      if (has(K.forward)) w.pos.addScaledVector(fwd, v);
      if (has(K.back)) w.pos.addScaledVector(fwd, -v);
      if (has(K.right)) w.pos.addScaledVector(right, v);
      if (has(K.left)) w.pos.addScaledVector(right, -v);
      if (has(K.up)) w.pos.z += v;
      if (has(K.down)) w.pos.z -= v;
      this._walkApply();
    }

    // ------------------------------------------------------------ render
    render() {
      this.renderer.setClearColor(this.scene.background || new THREE.Color(this.theme.bg), 1);
      this.renderer.render(this.scene, this.walk ? this.persp : this.camera);
      this._drawOverlay();
      if (this.hooks.onRender) this.hooks.onRender();
    }

    project(v) {
      const p = v.clone().project(this.walk ? this.persp : this.camera);
      return { x: (p.x + 1) / 2 * this.w, y: (1 - p.y) / 2 * this.h, behind: p.z > 1 };
    }

    _drawOverlay() {
      const ctx = this.ctx2d; const pr = this.renderer.getPixelRatio();
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, this.overlay.width, this.overlay.height);
      ctx.setTransform(pr, 0, 0, pr, 0, 0);
      if (this.mode === '2d') this._drawTexts(ctx);
      this._drawMeasures(ctx);
    }

    _drawTexts(ctx) {
      const cam = this.camera; const wpp = this.worldPerPixel();
      const half = { x: this.w * wpp / 2, y: this.h * wpp / 2 };
      const cx = this.target.x, cy = this.target.y;
      // camera may be rotated in 2D (twist); in plan mode up is +Y
      const layers = this.doc.layers; let drawn = 0;
      ctx.textBaseline = 'alphabetic';
      const font = '"Segoe UI", Arial, sans-serif';
      const groups = [{ texts: this.texts.filter((t) => t.view === this.view), M: null }];
      for (const ref of this.viewportRefs || []) groups.push({ texts: this.texts.filter((t) => t.view === ref.src), M: ref.vp.matrix, rect: ref.vp.rect });
      for (const grp of groups) {
        ctx.save();
        if (grp.rect) {
          const a = this.project(new THREE.Vector3(grp.rect[0], grp.rect[1], 0)), b = this.project(new THREE.Vector3(grp.rect[2], grp.rect[3], 0));
          ctx.beginPath(); ctx.rect(Math.min(a.x, b.x), Math.min(a.y, b.y), Math.abs(b.x - a.x), Math.abs(b.y - a.y)); ctx.clip();
        }
        for (const tx of grp.texts) {
          if (drawn > 6000) break;
          const t = tx.t; const id = t[0];
          if (layers[t[1]] && layers[t[1]]._off) continue;
          const st = id === NONE ? NORMAL : this.state[id]; if (st === HIDDEN) continue;
          let ax = t[3], ay = t[4], dx = t[5], dy = t[6], ux = t[7], uy = t[8];
          if (grp.M) { const m = grp.M; const X = m[0] * ax + m[2] * ay + m[4], Y = m[1] * ax + m[3] * ay + m[5]; ax = X; ay = Y;
            const d2 = [m[0] * dx + m[2] * dy, m[1] * dx + m[3] * dy], u2 = [m[0] * ux + m[2] * uy, m[1] * ux + m[3] * uy]; dx = d2[0]; dy = d2[1]; ux = u2[0]; uy = u2[1]; }
          const hpx = Math.hypot(ux, uy) / wpp; if (hpx < 2.2) continue;
          if (Math.abs(ax - cx) > half.x + Math.hypot(ux, uy) * 60 || Math.abs(ay - cy) > half.y + Math.hypot(ux, uy) * 60) continue;
          const s = this.project(new THREE.Vector3(ax, ay, 0));
          // text space: x along direction (one text height per 1 unit * width factor), y against up
          const hx = Math.hypot(dx, dy) / wpp, ang = Math.atan2(dy, dx);
          let c = this._themeColour(hexToRgb(t[2]));
          if (this.textColourBy) c = this.textColourBy(id) || c;
          if (st === SELECTED) c = [255, 138, 31];
          ctx.fillStyle = 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + (st === GHOST ? 0.12 : 1) + ')';
          ctx.save(); ctx.translate(s.x, s.y); ctx.rotate(-ang);
          const fx = hx / hpx; // width factor
          const upAng = Math.atan2(uy, ux) - ang; // skew from 90deg
          const skew = Math.cos(upAng) / Math.max(1e-6, Math.sin(upAng));
          ctx.transform(fx, 0, -skew, 1, 0, 0);
          ctx.font = (hpx / 0.716).toFixed(2) + 'px ' + font;
          ctx.textAlign = ['left', 'center', 'right'][t[9]] || 'left';
          const rows = t[11]; const len = t[12];
          for (let i = 0; i < t[10].length; i++) {
            const line = t[10][i]; if (!line) continue;
            const y = rows[i] * hpx;
            if (len && t[10].length === 1) {
              const target = len / wpp / fx; const m = ctx.measureText(line).width || 1;
              ctx.save(); ctx.scale(target / m, 1); ctx.fillText(line, 0, y / 1); ctx.restore();
            } else ctx.fillText(line, 0, y);
          }
          ctx.restore();
          drawn++;
        }
        ctx.restore();
      }
    }

    _fmt(v, area) {
      const u = this.units || ''; const a = Math.abs(v);
      const s = a >= 1000 ? v.toFixed(0) : a >= 10 ? v.toFixed(2) : v.toFixed(3);
      return s + (u ? ' ' + u + (area ? '²' : '') : '');
    }

    _drawMeasures(ctx) {
      const all = this.measures.concat(this.draft ? [this.draft] : []);
      if (!all.length && !this.hover) return;
      ctx.lineWidth = 2; ctx.font = '600 12px "Segoe UI", sans-serif';
      for (const m of all) {
        const pts = m.points.map((p) => this.project(p));
        if (m.live && this.livePoint) pts.push(this.project(this.livePoint));
        if (pts.some((p) => p.behind)) continue;
        ctx.strokeStyle = '#ff8a1f'; ctx.fillStyle = 'rgba(255,138,31,0.14)';
        ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y)));
        if (m.kind === 'area' && pts.length > 2) { ctx.closePath(); ctx.fill(); }
        ctx.stroke();
        for (const p of pts) { ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI * 2); ctx.fillStyle = '#ff8a1f'; ctx.fill(); }
        let label = null, at = null;
        const P = m.points.concat(m.live && this.livePoint ? [this.livePoint] : []);
        if (m.kind === 'distance' && P.length >= 2) {
          label = this._fmt(DDCV.geom.dist(P[0], P[1]));
          const d = P[1].clone().sub(P[0]);
          if (this.mode === '3d') label += '   Δx ' + this._fmt(d.x) + ' Δy ' + this._fmt(d.y) + ' Δz ' + this._fmt(d.z);
          at = { x: (pts[0].x + pts[1].x) / 2, y: (pts[0].y + pts[1].y) / 2 };
        } else if (m.kind === 'area' && P.length >= 3) {
          label = DDCV.i18n.t('area_v') + ' ' + this._fmt(DDCV.geom.area(P), true) + ' · ' + DDCV.i18n.t('perimeter') + ' ' + this._fmt(DDCV.geom.perimeter(P));
          const c = DDCV.geom.centre(P); at = this.project(new THREE.Vector3(c.x, c.y, c.z));
        }
        if (label) {
          const w = ctx.measureText(label).width + 14;
          ctx.fillStyle = this.dark ? 'rgba(19,38,60,.94)' : 'rgba(255,255,255,.95)'; ctx.strokeStyle = '#ff8a1f'; ctx.lineWidth = 1;
          ctx.beginPath(); ctx.roundRect(at.x - w / 2, at.y - 24, w, 20, 6); ctx.fill(); ctx.stroke();
          ctx.fillStyle = this.dark ? '#e9f1fc' : '#162d48'; ctx.textAlign = 'center'; ctx.fillText(label, at.x, at.y - 10);
          ctx.lineWidth = 2;
        }
      }
      if (this.snapMark) { const p = this.project(this.snapMark); ctx.strokeStyle = '#2bb673'; ctx.lineWidth = 2; ctx.strokeRect(p.x - 6, p.y - 6, 12, 12); }
    }

    screenshot() {
      this.render();
      const c = document.createElement('canvas'); c.width = this.renderer.domElement.width; c.height = this.renderer.domElement.height;
      const x = c.getContext('2d'); x.drawImage(this.renderer.domElement, 0, 0); x.drawImage(this.overlay, 0, 0);
      return c.toDataURL('image/png');
    }
  }

  DDCV.Engine = Engine;
  DDCV.STATE = { HIDDEN, NORMAL, GHOST, SELECTED, NONE };
})(typeof window !== 'undefined' ? window : globalThis);
