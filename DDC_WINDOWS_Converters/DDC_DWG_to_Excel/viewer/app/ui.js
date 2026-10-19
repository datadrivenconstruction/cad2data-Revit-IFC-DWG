// DDC Viewer — application controller (DOM, tree, search, properties, tools, shortcuts).
(function (g) {
  'use strict';
  const DDCV = g.DDCV, THREE = g.THREE, I = DDCV.i18n, t = (k) => I.t(k);
  const S = DDCV.STATE;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s === null || s === undefined ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const PALETTE = ['#1f77d0', '#e8710a', '#2ca05a', '#d6383a', '#8a5cd1', '#8c564b', '#e377c2', '#7f8c8d', '#bcbd22', '#17becf',
                   '#5a8fd6', '#f2a541', '#62c370', '#ef6f6c', '#a68bd8', '#b07b6a', '#f19fd6', '#aab7b8', '#d4d45a', '#5fd3e0'];
  const ICON = {
    fit: '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
    ortho: '<path d="M4 7l8-4 8 4v10l-8 4-8-4Z M4 7l8 4 8-4 M12 11v10"/>',
    walk: '<circle cx="13" cy="4.5" r="1.8"/><path d="m9 21 2.5-6.5L14 17v4M8.5 11.5 11 8l3 1 2 3.5M11.5 14.5 11 8"/>',
    measure: '<path d="M3 17 17 3l4 4L7 21Z M7 13l2 2M10 10l2 2M13 7l2 2"/>',
    area: '<path d="M4 6l7-3 9 5-3 12-11-2Z"/><path d="M8 10h6v5H8Z" stroke-dasharray="2 2"/>',
    section: '<path d="M3 12h18M12 3l7 4v10l-7 4-7-4V7Z" />',
    box: '<path d="M4 7l8-4 8 4v10l-8 4-8-4Z" stroke-dasharray="3 2"/><path d="M4 7l8 4 8-4M12 11v10"/>',
    hide: '<path d="M3 3l18 18M10.6 6.1A9.8 9.8 0 0 1 12 6c5 0 9 6 9 6a17 17 0 0 1-3 3.6M6.4 7.5A17 17 0 0 0 3 12s4 6 9 6a9 9 0 0 0 4-.9"/>',
    isolate: '<circle cx="12" cy="12" r="3.5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>',
    ghost: '<path d="M6 20V10a6 6 0 0 1 12 0v10l-2-1.5-2 1.5-2-1.5-2 1.5-2-1.5Z"/><circle cx="10" cy="10" r=".8"/><circle cx="14" cy="10" r=".8"/>',
    show: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    edges: '<path d="M4 7l8-4 8 4v10l-8 4-8-4Z"/>',
    tree: '<path d="M4 6h16M4 12h10M4 18h16"/>', info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
  };
  const svg = (k) => '<svg viewBox="0 0 24 24">' + ICON[k] + '</svg>';

  const app = {
    doc: null, view: null, selected: [], vis: null, colourKey: '', section: null, box: null, base: '', files: null,
    propsCache: new Map(), loadingChunks: new Map(), treeTab: null,
  };
  g.DDCV.app = app;

  // ------------------------------------------------------------------ setup
  function init() {
    let theme = null;
    try { theme = localStorage.getItem('ddcv.theme'); } catch (e) { /* ignore */ }
    const params = new URLSearchParams(location.search);
    if (params.get('theme')) theme = params.get('theme');
    if (params.get('lang')) I.set(params.get('lang'));
    app.engine = new DDCV.Engine($('viewport'), $('overlay'), {
      onClick: onClick, onDblClick: onDblClick, onCamera: () => app.cube && app.cube.render(), onRender: () => app.cube && app.cube.render(),
    });
    app.cube = new DDCV.ViewCube($('viewcube'), app.engine);
    setTheme(theme === 'dark' || (theme === null && g.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches));
    applyI18n();
    bindChrome();
    renderSamples();
    const pkg = params.get('pkg');
    if (pkg) loadScriptPackage(pkg, params);
  }

  function setTheme(dark) {
    app.dark = dark;
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    try { localStorage.setItem('ddcv.theme', dark ? 'dark' : 'light'); } catch (e) { /* ignore */ }
    app.engine.setTheme(dark);
    if (app.engine.edgesGroup) app.engine._syncEdges();
    app.cube.refresh(dark);
  }

  function applyI18n() {
    document.documentElement.lang = I.lang;
    for (const el of document.querySelectorAll('[data-i18n]')) el.textContent = t(el.dataset.i18n);
    for (const el of document.querySelectorAll('[data-i18n-title]')) el.title = t(el.dataset.i18nTitle);
    for (const el of document.querySelectorAll('[data-i18n-placeholder]')) el.placeholder = t(el.dataset.i18nPlaceholder);
    $('btnLang').textContent = I.lang.toUpperCase();
    if (app.cube) app.cube.refresh(app.dark);
    if (app.doc) { buildToolbar(); renderTreeTabs(); renderTree(); renderProps(); renderBadge(); renderSheetTabs(); renderLegend(); }
  }

  function toast(msg) {
    const el = $('toast'); el.textContent = msg; el.hidden = false;
    clearTimeout(app._toast); app._toast = setTimeout(() => { el.hidden = true; }, 1600);
  }

  function copy(text) {
    const done = () => toast(t('copied'));
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, () => fallback());
    else fallback();
    function fallback() { const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); done(); } catch (e) { /* ignore */ } ta.remove(); }
  }

  function bindChrome() {
    $('btnOpen').onclick = $('btnOpen2').onclick = () => $('fileInput').click();
    $('fileInput').onchange = (e) => openFiles([...e.target.files]);
    $('btnTheme').onclick = () => setTheme(!app.dark);
    $('btnLang').onclick = () => { I.set(I.lang === 'ru' ? 'en' : 'ru'); applyI18n(); };
    $('btnHelp').onclick = showHelp;
    $('btnShot').onclick = screenshot;
    $('btnCopyAll').onclick = () => { const id = app.selected[0]; if (id !== undefined) getProps(id).then((p) => copy(JSON.stringify(entityExport(id, p), null, 2))); };
    $('modalClose').onclick = () => { $('modal').hidden = true; };
    $('modal').onclick = (e) => { if (e.target === $('modal')) $('modal').hidden = true; };
    $('coverageBadge').onclick = showCoverage;
    for (const b of document.querySelectorAll('[data-collapse]')) b.onclick = () => {
      const side = b.dataset.collapse === 'leftPanel' ? 'left' : 'right';
      $('app').classList.toggle(side + '-collapsed'); $('app').classList.remove('show-' + side);
    };
    let timer = null;
    $('search').oninput = () => { clearTimeout(timer); timer = setTimeout(renderTree, 180); };
    const stage = $('stage');
    stage.addEventListener('dragover', (e) => { e.preventDefault(); });
    stage.addEventListener('drop', async (e) => {
      e.preventDefault();
      const items = [...(e.dataTransfer.items || [])];
      const files = [];
      const walk = (entry, path) => new Promise((res) => {
        if (entry.isFile) entry.file((f) => { f.relPath = path + f.name; files.push(f); res(); }, () => res());
        else if (entry.isDirectory) { const r = entry.createReader(); const all = []; const read = () => r.readEntries(async (ents) => { if (!ents.length) { for (const en of all) await walk(en, path + entry.name + '/'); res(); } else { all.push(...ents); read(); } }, () => res()); read(); }
        else res();
      });
      const entries = items.map((i) => i.webkitGetAsEntry && i.webkitGetAsEntry()).filter(Boolean);
      if (entries.length) { for (const en of entries) await walk(en, ''); openFiles(files); }
      else openFiles([...e.dataTransfer.files]);
    });
    document.addEventListener('keydown', onKey);
  }

  // ------------------------------------------------------------------ loading
  function renderSamples() {
    const list = $('sampleList'); const samples = g.DDCV_SAMPLES || [];
    list.innerHTML = samples.length ? '' : '<div class="empty">' + esc(t('no_samples')) + '</div>';
    for (const s of samples) {
      const el = document.createElement('div'); el.className = 'sample';
      el.innerHTML = '<span class="fmt ' + esc(s.format) + '">' + esc(s.format) + '</span><span>' + esc(s.title) + '</span><span class="meta">' + esc(s.meta || '') + '</span>';
      el.onclick = () => { history.replaceState(null, '', '?pkg=' + encodeURIComponent(s.path)); loadScriptPackage(s.path, new URLSearchParams()); };
      list.appendChild(el);
    }
  }
  g.addEventListener('load', renderSamples);

  function progress(frac, text) {
    $('progress').hidden = frac === null;
    if (frac !== null) { $('progressBar').style.width = Math.round(frac * 100) + '%'; $('progressText').textContent = text || ''; }
  }

  function loadScriptPackage(path, params) {
    progress(0.02, t('loading'));
    app.base = path.replace(/[^/]*$/, ''); app.files = null;
    const before = (g.DDCV_PACKAGES || []).length;
    const s = document.createElement('script'); s.src = path;
    s.onload = () => {
      const pk = (g.DDCV_PACKAGES || [])[before] || (g.DDCV_PACKAGES || []).slice(-1)[0];
      g.DDCV_PACKAGES = [];
      if (!pk) { progress(null); toast('No package in ' + path); return; }
      DDCV.pkg.unbox(pk).then((doc) => openDoc(doc, params), (e) => { progress(null); toast(String(e.message || e)); });
    };
    s.onerror = () => { progress(null); toast('Cannot load ' + path); };
    document.body.appendChild(s);
  }

  async function openFiles(files) {
    if (!files.length) return;
    const pkgFile = files.find((f) => /(^|\/)package\.js(on)?$/i.test(f.relPath || f.name)) || files.find((f) => /\.js(on)?$/i.test(f.name));
    if (!pkgFile) return;
    progress(0.02, t('loading'));
    const prefix = (pkgFile.relPath || pkgFile.name).replace(/[^/]*$/, '');
    app.files = new Map(files.map((f) => [(f.relPath || f.name).slice(prefix.length), f]));
    app.base = null;
    const text = await pkgFile.text();
    try {
      const raw = /\.js$/i.test(pkgFile.name) ? DDCV.pkg.containerFromScript(text) : JSON.parse(text);
      openDoc(await DDCV.pkg.unbox(raw), new URLSearchParams());
    } catch (e) { progress(null); toast(String(e.message || e)); }
  }

  async function openDoc(raw, params) {
    let doc;
    try { doc = DDCV.pkg.decode(raw); } catch (e) { progress(null); toast(String(e.message || e)); return; }
    app.doc = doc; app.selected = []; app.propsCache.clear(); app.colourKey = ''; app.section = null; app.box = null;
    app.engine.units = doc.units && doc.units.length ? doc.units.length : '';
    app.engine.setSection([]); app.engine._viewCache = new Map(); app.engine._grids = new Map();
    $('welcome').hidden = true;
    $('docTitle').innerHTML = esc(doc.title) + '<small>' + esc(doc.format) + (doc.source && doc.source.generation ? ' · ' + esc(doc.source.generation) : '') + (doc.source && doc.source.ifc_schema ? ' · ' + esc(doc.source.ifc_schema) : '') + '</small>';
    document.title = doc.title + ' — DDC Viewer';
    const visible = doc.views.filter((v) => !v.hidden_in_list);
    let view = visible.find((v) => v.id === params.get('view')) || visible.find((v) => v.kind === '3d') || visible.find((v) => v.space === 'model') || visible[0];
    app.treeTab = doc.tree && doc.tree.spatial ? 'spatial' : (doc.layers.length ? 'layers' : 'types');
    await showView(view);
    renderBadge(); renderTreeTabs(); renderTree(); renderProps(); renderSheetTabs(); renderFilters();
    // URL-driven state (used by headless verification and by converters' "Open in viewer")
    if (params.get('colour')) setColourBy(params.get('colour'));
    if (params.get('select')) {
      const key = params.get('select').toLowerCase();
      const e = doc.entities.find((x) => (x.handle && x.handle.toLowerCase() === key) || (x.guid && x.guid.toLowerCase() === key) || String(x.id) === key)
        || doc.entities.find((x) => x.type && x.type.toLowerCase() === key && (x.has_geometry || doc.format === 'DWG'));
      if (e) { select([e.id]); if (params.get('zoom') === '1') app.engine.zoomToEntities([e.id]); if (params.get('iso') === '1') isolate(); }
    }
    if (params.get('section')) { const [ax, f] = params.get('section').split(':'); openSection(ax || 'z', parseFloat(f || '0.5')); }
    if (params.get('box') === '1') openBox(0.15);
    if (params.get('ortho') === '1') toggleOrtho();
    if (params.get('preset')) app.engine.viewPreset(params.get('preset').split(',').map(Number));
    if (params.get('measure') === 'demo') demoMeasure();
    if (params.get('coverage') === '1') showCoverage();
    if (params.get('panel') === 'right') $('app').classList.add('show-right');
    const eng = app.engine;
    document.body.dataset.debug = JSON.stringify({ mode: eng.mode, geoms: eng.geoms.length, lines: eng.lines2d.length, texts: eng.texts.length,
      bbox: eng.bbox && [eng.bbox.min.toArray(), eng.bbox.max.toArray()], radius: eng.radius, target: eng.target.toArray(),
      tris: eng.geoms.reduce((a, g2) => a + g2.geom.index.count / 3, 0) });
    document.body.dataset.ready = '1';
  }

  async function showView(view) {
    app.view = view;
    progress(0.05, t('building'));
    const cb = (f) => progress(0.05 + 0.9 * f, t('building'));
    if (view.kind === '3d') await app.engine.build3d(app.doc, view, cb);
    else await app.engine.build2d(app.doc, view, cb);
    app.vis = new Uint8Array(app.doc.entities.length).fill(S.NORMAL);
    $('viewcube').hidden = view.kind !== '3d';
    const empty = view.kind === '2d' ? !(view.batches || []).length && !(view.texts || []).length && !(view.viewports || []).length
                                     : !(view.meshes || []).length;
    hint(empty ? t(view.kind === '2d' ? 'empty_view' : 'geometry_missing') : '');
    progress(null);
    buildToolbar(); updateStatus(); renderSheetTabs();
    if (app.colourKey) setColourBy(app.colourKey);
    if (app.selected.length) applyStates();
  }

  // ------------------------------------------------------------------ properties (inline or lazily loaded chunks)
  function getProps(id) {
    const e = app.doc.entities[id];
    if (!e) return Promise.resolve({});
    if (e.props) return Promise.resolve(e.props);
    const info = app.doc.properties || {};
    if (info.mode !== 'chunks') return Promise.resolve({});
    const ci = Math.floor(id / info.chunk_size);
    const name = info.files[ci];
    if (!name) return Promise.resolve({});
    if (app.loadingChunks.has(name)) return app.loadingChunks.get(name).then(() => app.doc.entities[id].props || {});
    const p = new Promise((resolve) => {
      const accept = (box) => {
        DDCV.pkg.unbox(box).then((chunk) => {
          if (chunk && chunk.start !== undefined) chunk.props.forEach((pr, k) => { const en = app.doc.entities[chunk.start + k]; if (en) en.props = pr; });
          resolve();
        }, () => resolve());
      };
      if (app.files) {
        const f = app.files.get(name + '.js');
        if (!f) return resolve();
        f.text().then((txt) => { try { accept(DDCV.pkg.containerFromScript(txt)); } catch (err) { resolve(); } });
      } else {
        const s = document.createElement('script'); s.src = app.base + name + '.js';
        s.onload = () => { const list = g.DDCV_PROPS || []; const chunk = list.find((c) => c.start === ci * info.chunk_size && c.package === app.doc.source.sha256); g.DDCV_PROPS = list.filter((c) => c !== chunk); accept(chunk); s.remove(); };
        s.onerror = () => resolve();
        document.body.appendChild(s);
      }
    });
    app.loadingChunks.set(name, p);
    return p.then(() => app.doc.entities[id].props || {});
  }

  function entityExport(id, props) {
    const e = app.doc.entities[id];
    const out = {}; for (const k in e) if (k !== 'props' && k[0] !== '_') out[k] = e[k];
    out.properties = props; return out;
  }

  // ------------------------------------------------------------------ selection and visibility
  function applyStates() {
    const m = new Map(); const sel = new Set(app.selected);
    const st = app.engine.state;
    for (let i = 0; i < app.vis.length; i++) {
      const want = sel.has(i) && app.vis[i] !== S.HIDDEN ? S.SELECTED : app.vis[i];
      if (st[i] !== want) m.set(i, want);
    }
    app.engine.setStates(m);
  }

  function select(ids, additive) {
    if (additive) { const s = new Set(app.selected); for (const id of ids) s.has(id) ? s.delete(id) : s.add(id); app.selected = [...s]; }
    else app.selected = ids.slice();
    applyStates(); renderProps(); markTreeSelection(); updateStatus();
  }

  function onClick(x, y, ev) {
    const eng = app.engine;
    if (app.tool === 'distance' || app.tool === 'area') {
      const r = eng.mode === '2d' ? eng._pick2d(x, y, true) : eng.pick(x, y);
      if (!r.point) return;
      if (!eng.draft) eng.draft = { kind: app.tool, points: [], live: true };
      eng.draft.points.push(r.point.clone());
      if (app.tool === 'distance' && eng.draft.points.length === 2) { eng.draft.live = false; eng.measures.push(eng.draft); eng.draft = null; }
      eng.dirty = true; return;
    }
    const r = eng.pick(x, y);
    if (r.id === null || r.id === undefined) { if (!ev.shiftKey && !ev.ctrlKey) select([]); return; }
    select([r.id], ev.shiftKey || ev.ctrlKey);
  }

  function onDblClick(x, y) {
    if (app.tool === 'area' && app.engine.draft) { finishArea(); return; }
    if (app.selected.length) app.engine.zoomToEntities(app.selected);
  }

  function finishArea() {
    const eng = app.engine;
    if (eng.draft && eng.draft.points.length >= 3) { eng.draft.live = false; eng.measures.push(eng.draft); }
    eng.draft = null; eng.dirty = true;
  }

  g.addEventListener('pointermove', (e) => {
    const eng = app.engine; if (!eng || !app.tool || !eng.mouse) return;
    if (e.target !== eng.renderer.domElement) return;
    if (eng.mode === '2d') { const r = eng._pick2d(eng.mouse.x, eng.mouse.y, true); eng.livePoint = r.point; eng.snapMark = r.snapped ? r.point : null; }
    else { eng.livePoint = null; }
    eng.dirty = true;
  });

  function hideSel() { for (const id of app.selected) app.vis[id] = S.HIDDEN; app.selected = []; applyStates(); renderProps(); }
  function ghostSel() { for (const id of app.selected) app.vis[id] = S.GHOST; app.selected = []; applyStates(); renderProps(); }
  function isolate(ids) {
    ids = ids || app.selected; if (!ids.length) return;
    const keep = new Set(ids);
    const other = app.engine.mode === '3d' ? S.GHOST : S.HIDDEN;
    for (let i = 0; i < app.vis.length; i++) app.vis[i] = keep.has(i) ? S.NORMAL : other;
    applyStates(); app.engine.zoomToEntities(ids);
  }
  function showAll() { app.vis.fill(S.NORMAL); applyStates(); renderFilters(); }

  // ------------------------------------------------------------------ colour by
  function colourKeys() {
    const d = app.doc; const keys = [['', t('colour_none')], ['type', 'Type / Тип'], ['coverage', t('coverage')]];
    if (d.format === 'DWG') keys.push(['layer', t('tab_layers')]); else keys.push(['storey', t('storey')], ['material', 'Material / Материал']);
    for (const k of DDCV.pkg.propKeys(d, 40)) keys.push([k, k.replace('::', ' › ')]);
    return keys;
  }

  async function setColourBy(key) {
    app.colourKey = key;
    const d = app.doc;
    if (!key) { app.engine.applyColourBy(null); app.engine.textColourBy = null; app.legend = null; renderLegend(); return; }
    const needsProps = key.indexOf('::') > 0 && d.properties && d.properties.mode === 'chunks';
    if (needsProps) { progress(0.1, t('loading')); for (let i = 0; i < d.properties.files.length; i++) { await getProps(i * d.properties.chunk_size); progress((i + 1) / d.properties.files.length, t('loading')); } progress(null); }
    const vals = new Map();
    for (const e of d.entities) { const v = DDCV.pkg.propValue(e, key); const s = v && typeof v === 'object' ? JSON.stringify(v.value !== undefined ? v.value : v) : v; e._cv = s === undefined || s === null || s === '' ? '—' : String(s); vals.set(e._cv, (vals.get(e._cv) || 0) + 1); }
    const sorted = [...vals.entries()].sort((a, b) => b[1] - a[1]);
    const map = new Map(); sorted.forEach(([v], i) => map.set(v, i < PALETTE.length ? PALETTE[i] : '#9aa7b5'));
    if (map.has('—')) map.set('—', '#b8c2cc');
    const rgb = new Map([...map.entries()].map(([k, h]) => [k, [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]]));
    const fn = (id) => { const e = d.entities[id]; return e ? rgb.get(e._cv) : null; };
    app.engine.applyColourBy(fn); app.engine.textColourBy = fn;
    app.legend = { key, items: sorted.slice(0, 24).map(([v, n]) => [v, n, map.get(v)]), more: Math.max(0, sorted.length - 24) };
    renderLegend();
  }

  function renderLegend() {
    const el = $('legend');
    if (!app.legend) { el.hidden = true; return; }
    el.hidden = false;
    el.innerHTML = '<h4>' + esc(t('legend')) + ': ' + esc(app.legend.key.replace('::', ' › ')) + '</h4>' +
      app.legend.items.map(([v, n, c]) => '<div data-v="' + esc(v) + '" style="cursor:pointer"><i style="background:' + c + '"></i>' + esc(String(v).slice(0, 48)) + ' <span style="color:var(--muted)">' + n + '</span></div>').join('') +
      (app.legend.more ? '<div style="color:var(--muted)">+' + app.legend.more + '</div>' : '');
    for (const row of el.querySelectorAll('[data-v]')) row.onclick = () => { const v = row.dataset.v; isolate(app.doc.entities.filter((e) => e._cv === v).map((e) => e.id)); };
    if (app.engine.mode === '2d' && !$('sheetTabs').hidden) el.style.top = '52px'; else el.style.top = '12px';
  }

  // ------------------------------------------------------------------ toolbar and tools
  function buildToolbar() {
    const tb = $('toolbar'); const is3d = app.engine.mode === '3d';
    const items = [
      ['mobile-tree', 'tree', 'model_tree', () => $('app').classList.toggle('show-left'), 'mobile-only'],
      ['fit', 'fit', 'fit', () => app.engine.fit(true)],
    ];
    if (is3d) items.push(['ortho', 'ortho', 'ortho', toggleOrtho], ['walk', 'walk', 'walk', toggleWalk]);
    items.push('|', ['distance', 'measure', 'measure', () => setTool('distance')], ['area', 'area', 'area', () => setTool('area')]);
    if (is3d) items.push(['section', 'section', 'section', () => (app.section ? closeSection() : openSection('z', 0.5))], ['box', 'box', 'section_box', () => (app.box ? closeBox() : openBox(0))]);
    items.push('|', ['hide', 'hide', 'hide', hideSel], ['isolate', 'isolate', 'isolate', () => isolate()], ['ghost', 'ghost', 'ghost', ghostSel], ['show', 'show', 'show_all', showAll]);
    if (is3d && app.engine.edgesAvailable) items.push(['edges', 'edges', 'edges', () => { app.engine.setEdges(!app.engine.edgesOn); markToolbar(); }]);
    items.push('|');
    tb.innerHTML = '';
    for (const it of items) {
      if (it === '|') { const s = document.createElement('span'); s.className = 'sep'; tb.appendChild(s); continue; }
      const b = document.createElement('button'); b.className = 'icon-btn ' + (it[4] || ''); b.dataset.tool = it[0]; b.title = t(it[2]); b.innerHTML = svg(it[1]); b.onclick = it[3];
      tb.appendChild(b);
    }
    const sel = document.createElement('select'); sel.title = t('colour_by');
    for (const [k, label] of colourKeys()) { const o = document.createElement('option'); o.value = k; o.textContent = k ? label : '🎨 ' + label; sel.appendChild(o); }
    sel.value = app.colourKey; sel.onchange = () => setColourBy(sel.value);
    tb.appendChild(sel);
    const info = document.createElement('button'); info.className = 'icon-btn mobile-only'; info.innerHTML = svg('info'); info.title = t('properties'); info.onclick = () => $('app').classList.toggle('show-right');
    tb.appendChild(info);
    markToolbar();
  }

  function markToolbar() {
    for (const b of $('toolbar').querySelectorAll('[data-tool]')) {
      const k = b.dataset.tool;
      b.classList.toggle('active', (k === app.tool) || (k === 'ortho' && app.engine.projection === 'orthographic') || (k === 'walk' && !!app.engine.walk) ||
        (k === 'section' && !!app.section) || (k === 'box' && !!app.box) || (k === 'edges' && app.engine.edgesOn));
    }
  }

  function hint(text) { const h = $('hint'); h.hidden = !text; h.textContent = text || ''; }

  function setTool(tool) {
    const eng = app.engine;
    if (app.tool === tool) tool = null;
    app.tool = tool; eng.draft = null; eng.livePoint = null; eng.snapMark = null;
    hint(tool === 'distance' ? t('measure_hint') : tool === 'area' ? t('area_hint') : '');
    if (!tool) eng.measures = [];
    eng.renderer.domElement.style.cursor = tool ? 'crosshair' : '';
    eng.dirty = true; markToolbar();
  }

  function toggleOrtho() { const e = app.engine; if (e.walk) toggleWalk(); e.setProjection(e.projection === 'perspective' ? 'orthographic' : 'perspective'); markToolbar(); }
  function toggleWalk() { const e = app.engine; const on = !e.walk; e.setWalk(on); hint(on ? t('walk_hint') : ''); markToolbar(); }

  function sectionPlanes() {
    const planes = [];
    const bb = app.engine.bbox;
    if (app.section) {
      const ax = { x: 0, y: 1, z: 2 }[app.section.axis]; const n = new THREE.Vector3(); n.setComponent(ax, app.section.flip ? 1 : -1);
      const pos = bb.min.getComponent(ax) + (bb.max.getComponent(ax) - bb.min.getComponent(ax)) * app.section.f;
      planes.push(new THREE.Plane(n, app.section.flip ? -pos : pos));
    }
    if (app.box) {
      for (let a = 0; a < 3; a++) {
        const lo = bb.min.getComponent(a), hi = bb.max.getComponent(a), span = hi - lo;
        const n1 = new THREE.Vector3(); n1.setComponent(a, 1); planes.push(new THREE.Plane(n1, -(lo + span * app.box.min[a])));
        const n2 = new THREE.Vector3(); n2.setComponent(a, -1); planes.push(new THREE.Plane(n2, lo + span * app.box.max[a]));
      }
    }
    app.engine.setSection(planes);
  }

  function openSection(axis, f) { app.section = { axis: axis.toLowerCase(), f: isFinite(f) ? f : 0.5, flip: false }; sectionPlanes(); renderToolPanel(); markToolbar(); }
  function closeSection() { app.section = null; sectionPlanes(); renderToolPanel(); markToolbar(); }
  function openBox(m) { app.box = { min: [m, m, m], max: [1 - m, 1 - m, 1 - m] }; sectionPlanes(); renderToolPanel(); markToolbar(); }
  function closeBox() { app.box = null; sectionPlanes(); renderToolPanel(); markToolbar(); }

  function renderToolPanel() {
    const el = $('toolPanel');
    if (!app.section && !app.box) { el.hidden = true; return; }
    el.hidden = false; let h = '';
    if (app.section) {
      h += '<h4>' + esc(t('section')) + '</h4><label>' + esc(t('axis')) + '<span class="row">' + ['x', 'y', 'z'].map((a) => '<button class="pill' + (a === app.section.axis ? ' on' : '') + '" data-ax="' + a + '" style="' + (a === app.section.axis ? 'background:var(--blue);color:#fff' : '') + '">' + a.toUpperCase() + '</button>').join('') +
        '<button class="pill" id="secFlip">⇄ ' + esc(t('reverse')) + '</button></span></label><label>' + esc(t('offset')) + '<input type="range" id="secF" min="0" max="1" step="0.001" value="' + app.section.f + '"></label>';
    }
    if (app.box) {
      h += '<h4 style="margin-top:8px">' + esc(t('section_box')) + '</h4>';
      for (let a = 0; a < 3; a++) h += '<label>' + 'XYZ'[a] + ' min<input type="range" data-bmin="' + a + '" min="0" max="1" step="0.001" value="' + app.box.min[a] + '"></label><label>' + 'XYZ'[a] + ' max<input type="range" data-bmax="' + a + '" min="0" max="1" step="0.001" value="' + app.box.max[a] + '"></label>';
      h += '<div class="row"><button class="pill" id="boxSel">⌖ ' + esc(t('selected')) + '</button></div>';
    }
    el.innerHTML = h;
    for (const b of el.querySelectorAll('[data-ax]')) b.onclick = () => { app.section.axis = b.dataset.ax; sectionPlanes(); renderToolPanel(); };
    if ($('secFlip')) $('secFlip').onclick = () => { app.section.flip = !app.section.flip; sectionPlanes(); };
    if ($('secF')) $('secF').oninput = (e) => { app.section.f = parseFloat(e.target.value); sectionPlanes(); };
    for (const r of el.querySelectorAll('[data-bmin]')) r.oninput = () => { app.box.min[+r.dataset.bmin] = Math.min(parseFloat(r.value), app.box.max[+r.dataset.bmin] - 0.001); sectionPlanes(); };
    for (const r of el.querySelectorAll('[data-bmax]')) r.oninput = () => { app.box.max[+r.dataset.bmax] = Math.max(parseFloat(r.value), app.box.min[+r.dataset.bmax] + 0.001); sectionPlanes(); };
    if ($('boxSel')) $('boxSel').onclick = () => {
      const b = app.engine.entitiesBox(app.selected); if (b.isEmpty()) return; const bb = app.engine.bbox;
      for (let a = 0; a < 3; a++) { const lo = bb.min.getComponent(a), span = (bb.max.getComponent(a) - lo) || 1; app.box.min[a] = Math.max(0, (b.min.getComponent(a) - lo) / span - 0.01); app.box.max[a] = Math.min(1, (b.max.getComponent(a) - lo) / span + 0.01); }
      sectionPlanes(); renderToolPanel();
    };
  }

  function demoMeasure() {
    // deterministic measurement for verification: diagonal of the model extent
    const eng = app.engine; const bb = eng.bbox;
    const a = bb.min.clone(), b = bb.max.clone();
    if (eng.mode === '2d') { a.z = 0; b.z = 0; }
    eng.measures.push({ kind: 'distance', points: [a.clone().lerp(b, 0.2), a.clone().lerp(b, 0.8)], live: false });
    const c = bb.getCenter(new THREE.Vector3()), s = bb.getSize(new THREE.Vector3()).multiplyScalar(0.18);
    const z = eng.mode === '2d' ? 0 : bb.min.z;
    eng.measures.push({ kind: 'area', points: [new THREE.Vector3(c.x - s.x, c.y - s.y, z), new THREE.Vector3(c.x + s.x, c.y - s.y, z), new THREE.Vector3(c.x + s.x, c.y + s.y, z), new THREE.Vector3(c.x - s.x, c.y + s.y, z)], live: false });
    eng.dirty = true;
  }

  // ------------------------------------------------------------------ sheets (DWG layouts)
  function renderSheetTabs() {
    const el = $('sheetTabs'); const d = app.doc;
    const views = d ? d.views.filter((v) => !v.hidden_in_list && v.kind === '2d') : [];
    if (views.length < 2) { el.hidden = true; return; }
    el.hidden = false;
    el.innerHTML = views.map((v) => '<button data-v="' + esc(v.id) + '" class="' + (app.view && v.id === app.view.id ? 'on' : '') + '">' + (v.space === 'paper' ? '▭ ' : '◇ ') + esc(v.space === 'model' ? t('model_space') : v.name) + '</button>').join('');
    for (const b of el.querySelectorAll('button')) b.onclick = () => { const v = d.views.find((x) => x.id === b.dataset.v); if (v && v !== app.view) showView(v).then(() => { renderTree(); renderLegend(); }); };
  }

  // ------------------------------------------------------------------ tree
  function renderTreeTabs() {
    const d = app.doc; const tabs = [];
    if (d.tree && d.tree.spatial) tabs.push(['spatial', t('tab_spatial')]);
    if (d.layers.length) tabs.push(['layers', t('tab_layers')]);
    tabs.push(['types', t('tab_types')]);
    const el = $('treeTabs');
    el.innerHTML = tabs.map(([k, l]) => '<button data-k="' + k + '" class="' + (k === app.treeTab ? 'on' : '') + '">' + esc(l) + '</button>').join('');
    for (const b of el.querySelectorAll('button')) b.onclick = () => { app.treeTab = b.dataset.k; renderTreeTabs(); renderTree(); };
  }

  function renderFilters() {
    const d = app.doc; const el = $('filters'); if (!d) return;
    const counts = new Map(); for (const e of d.entities) counts.set(e.coverage, (counts.get(e.coverage) || 0) + 1);
    el.innerHTML = [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([k, n]) => '<span class="chip" data-c="' + esc(k) + '">' + esc(k) + ' · ' + n.toLocaleString() + '</span>').join('');
    for (const c of el.querySelectorAll('.chip')) c.onclick = () => {
      const on = !c.classList.contains('on');
      for (const x of el.querySelectorAll('.chip')) x.classList.remove('on');
      if (!on) { showAll(); return; }
      c.classList.add('on'); isolate(d.entities.filter((e) => e.coverage === c.dataset.c).map((e) => e.id));
    };
  }

  function nodeHtml(label, opts) {
    return '<div class="node' + (opts.cls ? ' ' + opts.cls : '') + '"' + (opts.id !== undefined ? ' data-id="' + opts.id + '"' : '') + (opts.key ? ' data-key="' + esc(opts.key) + '"' : '') + '>' +
      '<span class="tw">' + (opts.tw || '') + '</span>' + (opts.sw ? '<span class="sw" style="background:' + opts.sw + '"></span>' : '') +
      '<span class="nm" title="' + esc(label) + '">' + esc(label) + '</span>' + (opts.ct !== undefined ? '<span class="ct">' + opts.ct + '</span>' : '') +
      (opts.eye ? '<span class="eye" data-eye="' + esc(opts.eye) + '">' + svg(opts.off ? 'hide' : 'show') + '</span>' : '') + '</div>';
  }

  function renderTree() {
    const d = app.doc; const el = $('tree'); if (!d) return;
    const q = $('search').value.trim().toLowerCase();
    if (q) {
      const hits = [];
      for (const e of d.entities) { if (DDCV.pkg.searchText(e).includes(q)) { hits.push(e); if (hits.length >= 1000) break; } }
      el.innerHTML = '<div class="empty" style="padding:6px;text-align:left">' + esc(t('results')) + ': ' + hits.length + (hits.length >= 1000 ? '+' : '') + (hits.length ? ' · <a href="#" id="isoHits">' + esc(t('isolate')) + '</a>' : '') + '</div>' +
        hits.slice(0, 500).map((e) => nodeHtml(label(e), { id: e.id, ct: e.type })).join('');
      bindNodes(el);
      if ($('isoHits')) $('isoHits').onclick = (ev) => { ev.preventDefault(); isolate(hits.map((h) => h.id)); };
      return;
    }
    if (app.treeTab === 'layers') {
      // drawn primitives per layer in the current sheet (entities inside blocks keep their own layer)
      const counts = new Map(); for (const o of app.engine.lines2d) { const nm = (d.layers[o.userData.layer] || {}).name; counts.set(nm, (counts.get(nm) || 0) + o.userData.ents.length); }
      el.innerHTML = '<div class="row" style="display:flex;gap:6px;padding:2px 6px 6px"><button class="pill" id="lOn">' + esc(t('layers_all_on')) + '</button><button class="pill" id="lOff">' + esc(t('layers_all_off')) + '</button></div>' +
        d.layers.map((l, i) => nodeHtml(l.name + (l.hidden ? ' ◌' : ''), { key: 'L' + i, sw: l.colour || '#999', ct: (counts.get(l.name) || 0).toLocaleString(), eye: String(i), off: l._off, cls: l._off ? 'off' : '' })).join('');
      for (const eye of el.querySelectorAll('[data-eye]')) eye.onclick = (ev) => { ev.stopPropagation(); const i = +eye.dataset.eye; app.engine.setLayerVisible(i, !!d.layers[i]._off); renderTree(); };
      for (const n of el.querySelectorAll('[data-key]')) n.onclick = () => { const l = d.layers[+n.dataset.key.slice(1)]; select(d.entities.filter((e) => e.layer === l.name).map((e) => e.id)); };
      $('lOn').onclick = () => { d.layers.forEach((l, i) => app.engine.setLayerVisible(i, true)); renderTree(); };
      $('lOff').onclick = () => { d.layers.forEach((l, i) => app.engine.setLayerVisible(i, false)); renderTree(); };
      return;
    }
    if (app.treeTab === 'spatial' && d.tree && d.tree.spatial) {
      el.innerHTML = '';
      const add = (node, parent, depth) => {
        const wrap = document.createElement('div');
        const kids = node.children || []; const elems = node.elements || [];
        const total = kids.length + elems.length;
        wrap.innerHTML = nodeHtml(node.name + '  ', { id: node.entity, tw: total ? (depth < 4 ? '▾' : '▸') : '', ct: node.type.replace(/^Ifc/, '') + (elems.length ? ' · ' + elems.length : '') });
        const box = document.createElement('div'); box.className = 'children'; box.hidden = depth >= 4;
        wrap.appendChild(box); parent.appendChild(wrap);
        let filled = false;
        const fill = () => {
          if (filled) return; filled = true;
          for (const c of kids) add(c, box, depth + 1);
          // group contained elements by class
          const by = new Map(); for (const id of elems) { const e = d.entities[id]; const k = e.type; if (!by.has(k)) by.set(k, []); by.get(k).push(id); }
          for (const [k, ids] of [...by.entries()].sort()) {
            const gw = document.createElement('div');
            gw.innerHTML = nodeHtml(k.replace(/^Ifc/, ''), { tw: '▸', ct: ids.length, key: 'G' });
            const gb = document.createElement('div'); gb.className = 'children'; gb.hidden = true; gw.appendChild(gb); box.appendChild(gw);
            const head = gw.firstChild;
            head.onclick = (ev) => { if (ev.target.classList.contains('tw')) { gb.hidden = !gb.hidden; head.querySelector('.tw').textContent = gb.hidden ? '▸' : '▾'; if (!gb.childNodes.length) { gb.innerHTML = ids.slice(0, 2000).map((id) => nodeHtml(label(d.entities[id]), { id })).join(''); bindNodes(gb); } } else select(ids); };
          }
        };
        if (!box.hidden) fill();
        const head = wrap.firstChild;
        head.onclick = (ev) => {
          if (ev.target.classList.contains('tw') && total) { box.hidden = !box.hidden; head.querySelector('.tw').textContent = box.hidden ? '▸' : '▾'; fill(); return; }
          const ids = collect(node); select(ids.length ? ids : [node.entity]);
        };
      };
      const collect = (node) => { const out = [...(node.elements || [])]; for (const c of node.children || []) out.push(c.entity, ...collect(c)); return out; };
      for (const r of d.tree.spatial) add(r, el, 0);
      markTreeSelection();
      return;
    }
    // by category (entity type)
    const by = new Map(); for (const e of d.entities) { if (!by.has(e.type)) by.set(e.type, []); by.get(e.type).push(e.id); }
    el.innerHTML = '';
    for (const [k, ids] of [...by.entries()].sort((a, b) => b[1].length - a[1].length)) {
      const gw = document.createElement('div');
      gw.innerHTML = nodeHtml(String(k).replace(/^Ifc/, ''), { tw: '▸', ct: ids.length.toLocaleString(), key: 'T' });
      const gb = document.createElement('div'); gb.className = 'children'; gb.hidden = true; gw.appendChild(gb); el.appendChild(gw);
      const head = gw.firstChild;
      head.onclick = (ev) => {
        if (ev.target.classList.contains('tw')) {
          gb.hidden = !gb.hidden; head.querySelector('.tw').textContent = gb.hidden ? '▸' : '▾';
          if (!gb.childNodes.length) { gb.innerHTML = ids.slice(0, 1500).map((id) => nodeHtml(label(d.entities[id]), { id })).join('') + (ids.length > 1500 ? '<div class="empty">+' + (ids.length - 1500) + '</div>' : ''); bindNodes(gb); }
        } else select(ids);
      };
    }
  }

  function label(e) { return e.name || (e.handle ? e.type + ' ' + e.handle : e.type + ' #' + e.id); }

  function bindNodes(root) {
    for (const n of root.querySelectorAll('.node[data-id]')) {
      if (n._bound) continue; n._bound = true;
      n.onclick = (ev) => { if (n.parentNode.parentNode && n.closest('[data-key]') === n) return; select([+n.dataset.id], ev.shiftKey || ev.ctrlKey); };
      n.ondblclick = () => app.engine.zoomToEntities([+n.dataset.id]);
    }
    markTreeSelection();
  }

  function markTreeSelection() {
    const sel = new Set(app.selected);
    for (const n of $('tree').querySelectorAll('.node[data-id]')) n.classList.toggle('sel', sel.has(+n.dataset.id));
  }

  // ------------------------------------------------------------------ properties panel
  function fmtValue(v) {
    if (v === null || v === undefined) return ['—', '', false];
    if (typeof v === 'object' && !Array.isArray(v) && 'value' in v) return [fmtNum(v.value), v.unit || '', false];
    if (typeof v === 'number') return [fmtNum(v), '', false];
    if (typeof v === 'boolean') return [v ? '✓ true' : '✗ false', '', false];
    if (Array.isArray(v) || typeof v === 'object') return [JSON.stringify(v), '', true];
    const s = String(v);
    return [s, '', /^[0-9a-f]{32,}$/i.test(s) || /^[\[{]/.test(s)];
  }
  function fmtNum(n) { if (typeof n !== 'number') return String(n); if (Number.isInteger(n)) return n.toLocaleString(I.lang === 'ru' ? 'ru-RU' : 'en-US'); return (Math.abs(n) >= 1e-3 && Math.abs(n) < 1e9 ? +n.toPrecision(10) : n).toLocaleString(I.lang === 'ru' ? 'ru-RU' : 'en-US', { maximumFractionDigits: 6 }); }

  function renderProps() {
    const el = $('props'); const d = app.doc;
    if (!d) { el.innerHTML = ''; return; }
    if (!app.selected.length) {
      const c = d.coverage || {};
      el.innerHTML = '<div class="prop-head"><div class="t">' + esc(d.title) + '</div><div class="s">' + esc(d.format) + ' · ' + d.entities.length.toLocaleString() + ' ' + esc(t('elements')) + '</div></div>' +
        group(t('source'), Object.assign({}, d.source, { units: (d.units && d.units.length) || t('unresolved') }), true) + group(t('producer'), d.producer || {}, false) +
        '<div class="empty">' + esc(t('nothing_selected')) + '</div>';
      bindCopy(el); return;
    }
    if (app.selected.length > 1) {
      const by = new Map(); for (const id of app.selected) { const e = d.entities[id]; by.set(e.type, (by.get(e.type) || 0) + 1); }
      el.innerHTML = '<div class="prop-head"><div class="t">' + esc(t('selected')) + ': ' + app.selected.length.toLocaleString() + '</div></div>' + group(t('tab_types'), Object.fromEntries([...by.entries()].sort((a, b) => b[1] - a[1]).slice(0, 60)), true);
      bindCopy(el); return;
    }
    const id = app.selected[0]; const e = d.entities[id];
    el.innerHTML = '<div class="prop-head"><div class="t">' + esc(label(e)) + '</div><div class="empty">' + esc(t('loading')) + '</div></div>';
    getProps(id).then((props) => {
      if (app.selected[0] !== id) return;
      let h = '<div class="prop-head"><div class="t">' + esc(label(e)) + '</div><div class="s"><span class="cov ' + esc(e.coverage) + '">' + esc(e.coverage) + '</span>' + esc(e.type || '') +
        (e.handle ? ' · <span style="font-family:Consolas,monospace">#' + esc(e.handle) + '</span>' : '') + (e.layer ? ' · ' + esc(e.layer) : '') + (e.storey ? ' · ' + esc(e.storey) : '') + '</div></div>';
      const summary = {}; for (const k of ['guid', 'handle', 'type', 'layer', 'storey', 'material', 'coverage', 'via']) if (e[k] !== undefined && e[k] !== null) summary[k] = e[k];
      h += group('Element / Элемент', summary, true);
      const names = Object.keys(props || {});
      names.forEach((g2, i) => { h += group(g2, props[g2], i < 3 || /Attributes|Coverage|Identity|Qto/i.test(g2)); });
      el.innerHTML = h; bindCopy(el);
    });
  }

  function group(name, obj, open) {
    const keys = Object.keys(obj || {});
    let rows = '';
    for (const k of keys) {
      const [v, u, mono] = fmtValue(obj[k]);
      rows += '<div class="k">' + esc(k) + '</div><div class="v' + (mono ? ' mono' : '') + '">' + esc(v.length > 600 ? v.slice(0, 600) + '…' : v) + (u ? '<span class="u">' + esc(u) + '</span>' : '') + '</div><button title="' + esc(t('copy')) + '" data-copy="' + esc(v + (u ? ' ' + u : '')) + '">⧉</button>';
    }
    return '<details class="grp"' + (open ? ' open' : '') + '><summary>' + esc(name) + '<span class="n">' + keys.length + '</span></summary><div class="kv">' + rows + '</div></details>';
  }
  function bindCopy(el) { for (const b of el.querySelectorAll('[data-copy]')) b.onclick = () => copy(b.dataset.copy); }

  // ------------------------------------------------------------------ coverage
  function coverageSummary() {
    const d = app.doc; const c = d.coverage || {};
    if (d.format === 'DWG') {
      const counts = c.counts || {}; const total = c.records || Object.values(counts).reduce((a, b) => a + b, 0);
      const dec = counts.DECODED || 0;
      return { pct: total ? dec / total : 0, total, decoded: dec, refused: (counts.REFUSED || 0), other: total - dec - (counts.REFUSED || 0), unit: 'records' };
    }
    const counts = c.counts || {}; const withRep = (counts.DECODED || 0) + (counts.PARTIAL || 0) + (counts.REFUSED || 0);
    return { pct: withRep ? (counts.DECODED || 0) / withRep : 0, total: withRep, decoded: counts.DECODED || 0, refused: counts.REFUSED || 0, other: counts.PARTIAL || 0, unit: 'elements with geometry' };
  }

  function ring(p, colour) {
    const r = 9, C = 2 * Math.PI * r;
    return '<svg class="ring" viewBox="0 0 24 24"><circle cx="12" cy="12" r="' + r + '" stroke="var(--line)" stroke-width="3.2"/><circle cx="12" cy="12" r="' + r + '" stroke="' + colour + '" stroke-width="3.2" stroke-dasharray="' + (C * p).toFixed(2) + ' ' + C.toFixed(2) + '" transform="rotate(-90 12 12)" stroke-linecap="round"/></svg>';
  }

  function renderBadge() {
    const b = $('coverageBadge'); const s = coverageSummary();
    const cls = s.pct >= 0.995 ? 'ok' : s.pct >= 0.9 ? 'warn' : 'bad';
    const colour = cls === 'ok' ? 'var(--ok)' : cls === 'warn' ? 'var(--warn)' : 'var(--bad)';
    b.className = 'badge ' + cls; b.hidden = false;
    const pct = (Math.floor(s.pct * 1000) / 10).toFixed(1);
    b.innerHTML = ring(s.pct, colour) + '<span><b>' + pct + ' %</b> <span class="txt">' + esc(t('decoded')) + (s.refused ? ' · ' + s.refused.toLocaleString() + ' ' + esc(t('refused')) : '') + (s.other ? ' · ' + s.other.toLocaleString() + ' ' + esc(t(app.doc.format === 'DWG' ? 'not_decoded' : 'partial')) : '') + '</span></span>';
    b.title = t('coverage_title');
  }

  function showCoverage() {
    const d = app.doc; if (!d) return; const c = d.coverage || {}; const s = coverageSummary();
    const total = Object.values(c.counts || {}).reduce((a, b) => a + b, 0) || 1;
    const colour = { DECODED: 'var(--ok)', COMPLETE: 'var(--ok)', PARTIAL: 'var(--warn)', REFUSED: 'var(--bad)', UNIMPLEMENTED: 'var(--bad)' };
    let h = '<h2>' + esc(t('coverage_title')) + '</h2><div style="color:var(--muted)">' + esc(d.format) + ' · ' + esc(d.title) + ' · ' + esc(t('coverage_state')) + ': <b>' + esc(c.state) + '</b>' + (c.can_convert === false ? ' · can_convert=false' : '') + '</div>';
    h += '<h3>' + esc(t('counts')) + '</h3><div class="bars">' + Object.entries(c.counts || {}).sort((a, b) => b[1] - a[1]).map(([k, n]) => '<div><span>' + esc(k) + '</span><span class="b"><i style="width:' + (100 * n / total).toFixed(2) + '%;background:' + (colour[k] || 'var(--muted)') + '"></i></span><span style="text-align:right">' + n.toLocaleString() + '</span></div>').join('') + '</div>';
    const table = (title, obj) => { const e = Object.entries(obj || {}); if (!e.length) return ''; return '<h3>' + esc(title) + '</h3><table class="t">' + e.sort((a, b) => (typeof b[1] === 'number' ? b[1] : 0) - (typeof a[1] === 'number' ? a[1] : 0)).slice(0, 80).map(([k, v]) => '<tr><td>' + esc(k) + '</td><td>' + esc(typeof v === 'number' ? v.toLocaleString() : JSON.stringify(v)) + '</td></tr>').join('') + '</table>'; };
    h += table(t('undrawn'), c.undrawn) + table(t('not_in_model'), c.not_in_model) + table('Refused items', c.refused_items);
    if (c.truncated) h += '<p style="color:var(--bad)">' + esc(t('truncated')) + ': ' + esc(c.truncated) + '</p>';
    if (c.approximations) h += '<h3>' + esc(t('approximations')) + '</h3><ul>' + c.approximations.map((a) => '<li>' + esc(a) + '</li>').join('') + '</ul>';
    const misc = {}; for (const k of ['placement', 'world_fallback_reason', 'drawn_primitives', 'records', 'elements', 'elements_with_geometry', 'triangles']) if (c[k] !== undefined && c[k] !== null) misc[k] = c[k];
    h += table('Summary', misc) + table('Scene counts', c.scene_counts) + table('Viewer counts', c.viewer_counts);
    if (c.rvt_source) h += '<h3>RVT</h3><p>' + esc(c.rvt_source.note) + '</p>' + table('RVT converter report', c.rvt_source.report);
    $('modalBody').innerHTML = h; $('modal').hidden = false;
  }

  function showHelp() {
    const keys = [['F', t('fit')], ['O', t('ortho')], ['P', t('walk')], ['M', t('measure')], ['A', t('area')], ['C', t('section')], ['B', t('section_box')],
      ['H', t('hide')], ['I', t('isolate')], ['G', t('ghost')], ['U', t('show_all')], ['E', t('edges')], ['T', t('theme')], ['L', t('lang')], ['Shift+S', t('screenshot')],
      ['/', t('search')], ['1–6', 'View presets / Виды'], ['Esc', t('close')], ['Dbl-click', t('fit')], ['Shift+click', t('selected') + ' +']];
    $('modalBody').innerHTML = '<h2>' + esc(t('hk_title')) + '</h2><table class="t">' + keys.map(([k, v]) => '<tr><td><kbd>' + esc(k) + '</kbd></td><td style="text-align:left">' + esc(v.replace(/\s*\(.*\)$/, '')) + '</td></tr>').join('') + '</table>';
    $('modal').hidden = false;
  }

  function onKey(e) {
    if (e.target && /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) { if (e.key === 'Escape') e.target.blur(); return; }
    if (app.engine.walk && /^(KeyW|KeyA|KeyS|KeyD|KeyQ|KeyE|Arrow|Page|Shift)/.test(e.code) && e.key !== 'Escape') return;
    const k = e.key;
    if (k === 'Escape') { if (!$('modal').hidden) { $('modal').hidden = true; return; } if (app.engine.walk) { toggleWalk(); return; } if (app.tool) { setTool(null); return; } select([]); return; }
    if (k === '?') { showHelp(); return; }
    if (k === '/') { e.preventDefault(); $('search').focus(); return; }
    if (!app.doc) return;
    if (k === 'S' && e.shiftKey) { screenshot(); return; }
    if (k === 'Enter' && app.tool === 'area') { finishArea(); return; }
    const is3d = app.engine.mode === '3d';
    const map = { f: () => app.engine.fit(true), o: () => is3d && toggleOrtho(), p: () => is3d && toggleWalk(), m: () => setTool('distance'), a: () => setTool('area'),
      c: () => is3d && (app.section ? closeSection() : openSection('z', 0.5)), b: () => is3d && (app.box ? closeBox() : openBox(0)), h: hideSel, i: () => isolate(), g: ghostSel, u: showAll,
      e: () => { if (is3d) { app.engine.setEdges(!app.engine.edgesOn); markToolbar(); } }, t: () => setTheme(!app.dark), l: () => { I.set(I.lang === 'ru' ? 'en' : 'ru'); applyI18n(); } };
    const presets = { 1: [0, 0, 1], 2: [0, -1, 0], 3: [1, 0, 0], 4: [0, 1, 0], 5: [-1, 0, 0], 6: [1, -1, 1] };
    if (map[k.toLowerCase()] && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); map[k.toLowerCase()](); }
    else if (presets[k] && is3d) app.engine.viewPreset(presets[k]);
  }

  function screenshot() {
    const url = app.engine.screenshot();
    const a = document.createElement('a'); a.href = url; a.download = (app.doc ? app.doc.title.replace(/[^\w.-]+/g, '_') : 'ddc-viewer') + '.png'; a.click();
  }

  function updateStatus() {
    const d = app.doc; if (!d) return;
    const parts = [d.entities.length.toLocaleString() + ' ' + t('elements')];
    const c = d.coverage || {};
    if (c.triangles) parts.push(c.triangles.toLocaleString() + ' △');
    if (d.units) parts.push(t('units') + ': ' + (d.units.length || t('unresolved')));
    if (app.selected.length) parts.push(t('selected') + ': ' + app.selected.length);
    $('status').textContent = parts.join(' · ');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})(window);
