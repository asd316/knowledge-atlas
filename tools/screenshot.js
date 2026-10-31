const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const dir = path.join(__dirname, '../src/');
const V = path.join(__dirname, 'vendor/'); // three.min.js + OrbitControls.js（见 README）
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const [w, h, out, action] = [ +process.argv[2], +process.argv[3], process.argv[4], process.argv[5] ];
  const p = await b.newPage({ viewport: { width: w, height: h } });
  const errs = [];
  p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.text()); });
  p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  await p.route('**/*', r => {
    const u = r.request().url();
    if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(V + 'three.min.js'), contentType: 'text/javascript' });
    if (u.includes('d3.min.js')) return r.fulfill({ body: fs.readFileSync(V + 'd3.min.js'), contentType: 'text/javascript' });
    if (u.includes('OrbitControls')) return r.fulfill({ body: fs.readFileSync(V + 'OrbitControls.js'), contentType: 'text/javascript' });
    if (u.startsWith('http://x/')) {
      const f = path.join(dir, new URL(u).pathname);
      if (!fs.existsSync(f)) return r.abort();
      if (f.endsWith('.js')) return r.fulfill({ body: fs.readFileSync(f), contentType: 'text/javascript' });
      // 页面按 Artifact 片段编写，这里补上发布时的外壳
      const html = fs.readFileSync(f, 'utf8');
      if (/^<!doctype/i.test(html)) return r.fulfill({ body: html, contentType: 'text/html' });
      return r.fulfill({ body: '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>[hidden]{display:none!important}body{margin:0}</style></head><body>' + html + '</body></html>', contentType: 'text/html' });
    }
    return r.abort();
  });
  await p.goto('http://x/' + (process.env.PAGE || 'index.html'));
  await p.waitForTimeout(2500);
  if (action) await p.evaluate(action);
  await p.waitForTimeout(1500);
  await p.screenshot({ path: out });
  console.log(errs.filter(e => !e.includes('fonts')).join('\n') || 'no errors');
  await b.close();
})();
