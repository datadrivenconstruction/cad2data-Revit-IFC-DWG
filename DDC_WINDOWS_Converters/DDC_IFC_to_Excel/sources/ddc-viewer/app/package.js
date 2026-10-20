// DDC Viewer — package decoding and validation (ddc-viewer-package/1).
(function (g) {
  'use strict';
  const DDCV = g.DDCV = g.DDCV || {};
  const SUPPORTED = 'ddc-viewer-package/1';
  const TYPES = { f32: Float32Array, u32: Uint32Array, u16: Uint16Array, f64: Float64Array, u8: Uint8Array };

  // Errors carry a code that the UI maps to a short, translated message; the raw text goes to "details".
  function PkgError(code, detail) { const e = new Error(detail || code); e.code = code; return e; }

  function b64ToBytes(text) {
    if (typeof text !== 'string') throw PkgError('corrupt', 'Buffer data missing');
    let bin;
    try { bin = atob(text); } catch (e) { throw PkgError('corrupt', 'Invalid base64 data: ' + e.message); }
    const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  function decode(doc) {
    if (!doc || typeof doc !== 'object' || Array.isArray(doc)) throw PkgError('not_pkg', 'Not a package object');
    if (doc.schema === undefined) throw PkgError('not_pkg', 'No "schema" field');
    if (doc.schema !== SUPPORTED) throw PkgError('schema', 'Unsupported schema: ' + doc.schema + ' (expected ' + SUPPORTED + ')');
    for (const k of ['buffers', 'entities', 'views', 'layers', 'materials']) {
      if (doc[k] !== undefined && doc[k] !== null && !Array.isArray(doc[k])) throw PkgError('corrupt', 'Field "' + k + '" is not a list');
    }
    const buffers = [];
    for (const b of doc.buffers || []) {
      const T = TYPES[b.dtype];
      if (!b || !T) throw PkgError('corrupt', 'Unknown buffer dtype ' + (b && b.dtype));
      const bytes = b64ToBytes(b.data);
      if (bytes.byteLength !== b.count * T.BYTES_PER_ELEMENT) throw PkgError('corrupt', 'Buffer ' + b.id + ' size mismatch');
      buffers[b.id] = new T(bytes.buffer, bytes.byteOffset, b.count);
      b.data = null; // free the base64 text
    }
    doc.buf = (id) => {
      if (id === undefined || id === null) return null;
      const v = buffers[id];
      if (!v) throw PkgError('corrupt', 'Missing buffer ' + id);
      return v;
    };
    doc.entities = doc.entities || [];
    doc.views = doc.views || [];
    doc.layers = doc.layers || [];
    doc.materials = doc.materials || [];
    return doc;
  }

  // Search text per entity (lower case), built lazily.
  function searchText(e) {
    if (e._s !== undefined) return e._s;
    const parts = [e.name, e.type, e.handle, e.guid, e.layer, e.storey, e.coverage];
    const props = e.props || {};
    for (const grp in props) for (const k in props[grp]) {
      const v = props[grp][k];
      if (v !== null && v !== undefined && typeof v !== 'object') parts.push(k + '=' + v);
    }
    e._s = parts.filter((p) => p !== undefined && p !== null).join(' ').toLowerCase();
    return e._s;
  }

  // Flat property lookup: "Group.Key" or plain field.
  function propValue(e, key) {
    if (key === 'type' || key === 'layer' || key === 'coverage' || key === 'storey' || key === 'name' || key === 'material') return e[key];
    const dot = key.indexOf('::');
    if (dot > 0) {
      const grp = (e.props || {})[key.slice(0, dot)];
      return grp ? grp[key.slice(dot + 2)] : undefined;
    }
    return undefined;
  }

  function propKeys(doc, limit) {
    const counts = new Map();
    const n = Math.min(doc.entities.length, 20000);
    const step = Math.max(1, Math.floor(doc.entities.length / n));
    for (let i = 0; i < doc.entities.length; i += step) {
      const props = doc.entities[i].props || {};
      for (const grp in props) for (const k in props[grp]) {
        const v = props[grp][k];
        if (v === null || typeof v === 'object') continue;
        const key = grp + '::' + k;
        counts.set(key, (counts.get(key) || 0) + 1);
      }
    }
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit || 200).map((x) => x[0]);
  }

  // ddc-viewer-container/1: {encoding: 'gzip+base64' | 'json', data}.  Plain package documents pass through.
  async function unbox(box) {
    if (!box || box.schema !== 'ddc-viewer-container/1') return box;
    if (box.encoding === 'json') return box.data;
    if (box.encoding !== 'gzip+base64') throw PkgError('schema', 'Unknown container encoding ' + box.encoding);
    if (typeof DecompressionStream === 'undefined') throw new Error('This browser cannot inflate gzip (DecompressionStream). Re-export the package with --no-compress.');
    const bytes = b64ToBytes(box.data); box.data = null;
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    let text;
    try { text = await new Response(stream).text(); } catch (e) { throw PkgError('corrupt', 'gzip: ' + e.message); }
    return parseJson(text);
  }
  function parseJson(text) {
    if (!text || !String(text).trim()) throw PkgError('empty', 'Empty input');
    try { return JSON.parse(text); } catch (e) { throw PkgError('corrupt', 'JSON: ' + e.message); }
  }
  function containerFromScript(text) {
    if (!text || !String(text).trim()) throw PkgError('empty', 'Empty file');
    const a = text.indexOf('push('), b = text.lastIndexOf(');');
    if (a < 0) throw PkgError('not_pkg', 'No DDCV_PACKAGES.push(...) in script');
    if (b <= a) throw PkgError('corrupt', 'Script is truncated');
    return parseJson(text.slice(a + 5, b));
  }

  DDCV.pkg = { unbox, containerFromScript, parseJson, PkgError, decode, searchText, propValue, propKeys, SUPPORTED };
})(typeof window !== 'undefined' ? window : globalThis);
