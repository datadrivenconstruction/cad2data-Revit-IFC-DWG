// DDC Viewer — view cube.
// Own tiny three.js scene; mirrors the main camera; click a face / edge / corner to fly there.
(function (g) {
  'use strict';
  const DDCV = g.DDCV, THREE = g.THREE;

  function faceTexture(label, dark) {
    const c = document.createElement('canvas'); c.width = c.height = 128;
    const x = c.getContext('2d');
    x.fillStyle = dark ? '#1a3451' : '#f4f8fd'; x.fillRect(0, 0, 128, 128);
    x.strokeStyle = dark ? '#3d5a7c' : '#b9cbe0'; x.lineWidth = 6; x.strokeRect(3, 3, 122, 122);
    x.fillStyle = dark ? '#e9f1fc' : '#162d48';
    x.font = '700 ' + (label.length > 6 ? 19 : 23) + 'px "Segoe UI", Arial, sans-serif';
    x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(label, 64, 66);
    const t = new THREE.CanvasTexture(c); t.anisotropy = 4; t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }

  class ViewCube {
    constructor(el, engine) {
      this.el = el; this.engine = engine;
      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      this.renderer.setPixelRatio(Math.min(2, g.devicePixelRatio || 1));
      el.appendChild(this.renderer.domElement);
      this.scene = new THREE.Scene();
      this.camera = new THREE.OrthographicCamera(-1.6, 1.6, 1.6, -1.6, 0.1, 20);
      this.camera.up.set(0, 0, 1);
      this.mats = [];
      // BoxGeometry face order: +x, -x, +y, -y, +z, -z
      this.order = ['right', 'left', 'back', 'front', 'top', 'bottom'];
      this.cube = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.8, 1.8), []);
      this.scene.add(this.cube);
      const edges = new THREE.LineSegments(new THREE.EdgesGeometry(this.cube.geometry), new THREE.LineBasicMaterial({ color: 0x6b86a6 }));
      this.scene.add(edges);
      this.hover = null;
      this.refresh(false);
      const ray = new THREE.Raycaster();
      const at = (e) => {
        const r = this.renderer.domElement.getBoundingClientRect();
        ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), this.camera);
        const hit = ray.intersectObject(this.cube)[0];
        if (!hit) return null;
        // snap the local hit point to face / edge / corner
        const p = hit.point.clone().divideScalar(0.9);
        const s = (v) => (Math.abs(v) > 0.55 ? Math.sign(v) : 0);
        return [s(p.x), s(p.y), s(p.z)];
      };
      this.renderer.domElement.addEventListener('click', (e) => { const n = at(e); if (n) engine.viewPreset(n); });
      this.renderer.domElement.addEventListener('pointermove', (e) => { this.renderer.domElement.style.cursor = at(e) ? 'pointer' : 'default'; });
      new ResizeObserver(() => this.resize()).observe(el);
      this.resize();
    }

    refresh(dark) {
      this.dark = dark;
      for (const m of this.mats) { m.map.dispose(); m.dispose(); }
      this.mats = this.order.map((preset) => {
        return new THREE.MeshBasicMaterial({ map: faceTexture(DDCV.i18n.t('cube_' + preset), dark) });
      });
      this.cube.material = this.mats;
      this.render();
    }

    resize() {
      const w = this.el.clientWidth || 100;
      this.renderer.setSize(w, w, false);
      this.renderer.domElement.style.width = w + 'px'; this.renderer.domElement.style.height = w + 'px';
      this.render();
    }

    render() {
      const cam = this.engine.walk ? this.engine.persp : this.engine.camera;
      const dir = new THREE.Vector3(); cam.getWorldDirection(dir);
      this.camera.position.copy(dir).multiplyScalar(-6);
      this.camera.up.copy(cam.up);
      this.camera.quaternion.copy(cam.quaternion);
      this.renderer.render(this.scene, this.camera);
    }
  }
  DDCV.ViewCube = ViewCube;
})(window);
