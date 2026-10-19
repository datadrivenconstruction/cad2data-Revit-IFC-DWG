# Third-party notices — DDC Viewer

DDC Viewer ships exactly one third-party component. Everything else (viewer
code, exporters, package format) is own code written for this repository; no
OpenConstructionERP code is reused (see PROVENANCE.json).

## three.js 0.185.1 (MIT)

- Files: `vendor/three.classic.js` (generated wrapper) from the unmodified
  `vendor/three-0.185.1-src/three.core.min.js` and `three.module.min.js`
  (npm package `three@0.185.1`). SHA-256 of inputs and output: `vendor/three.classic.json`.
- Generator: `tools/vendor_three.py` (stdlib) — only wraps the two ES modules in
  function scopes so the viewer works from `file://`; no code is changed.
- Loaded locally; no CDN or network access at runtime.

```
The MIT License

Copyright © 2010-2026 three.js authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
