/* 知识脉络图 · 知识包注册表
 * 术语见 docs/glossary.md，设计见 docs/rfc-001-knowledge-packs.md。
 *
 * 用法：
 *   <script src="data.js"></script><script src="detail.js"></script>   主体（自动包装成 core 包）
 *   <script src="atlas-core.js"></script>
 *   <script src="packs/climate.js"></script>                           Atlas.pack({...})
 *   const g = Atlas.build();          合并后的图谱：条目、关联、问题清单
 *   Atlas.applyLegacy();              把合并结果写回 window.ATLAS / ATLAS_DETAIL，供 3D 页面使用
 */
(function () {
  'use strict';

  // 条目类型：point / span 是抽象基类，其余都继承自它们；知识包可以再继承
  const BASE_KINDS = {
    point: { abstract: true, time: 'point' },
    span: { abstract: true, time: 'span' },
    milestone: { extends: 'point', name: '里程碑', color: null },
    work: { extends: 'point', name: '经典著作', color: '#fbbf24' },
    idea: { extends: 'point', name: '思想', color: '#7dd3fc' },
    person: { extends: 'span', name: '人物', color: '#c4b5fd' },
    debate: { extends: 'span', name: '辩论', color: '#f9a8d4', sides: true },
    link: { extends: 'span', name: '联动', color: '#e2e8f0' }
  };
  // 领域模板：决定领域视图有哪些泳道；模板之间可以继承
  const BASE_TEMPLATES = {
    discipline: { name: '学科', lanes: ['milestone', 'work', 'person', 'idea', 'debate'] }
  };

  const registered = [];
  const api = {};

  api.pack = def => { registered.push(def); return def; };

  // ---------- 主体：把 data.js / detail.js 包装成 core 包 ----------
  function legacyCore(A, DET) {
    const cats = A.cats.map(c => ({
      id: c.id, name: c.name, color: c.color,
      clusters: c.subs.map(s => ({ id: s.id || s.name, name: s.name, domains: s.domains.slice() }))
    }));
    const entries = [];
    A.nodes.forEach((n, i) => entries.push({ id: 'n' + i, k: 'milestone', d: [n.d], y: n.y, w: n.w, t: n.t, x: n.x, p: n.p, bk: n.bk, e: n.e }));
    Object.entries(DET || {}).forEach(([d, items]) => items.forEach(it => entries.push(Object.assign({}, it, { d: [d] }))));
    const links = A.links.map((l, i) => Object.assign({ id: 'l' + i }, l, { drv: l.k }));
    return {
      id: 'core', name: '主体', version: '2.0.0',
      categories: cats, domains: A.domains, entries, links,
      eras: A.eras, shocks: A.shocks, drivers: A.kinds, range: A.range,
      _legacy: { A, DET }
    };
  }

  // ---------- 继承解析 ----------
  function resolveChain(table, key, seen = []) {
    const def = table[key];
    if (!def) return null;
    if (seen.includes(key)) throw new Error('循环继承：' + seen.concat(key).join(' → '));
    const parent = def.extends ? resolveChain(table, def.extends, seen.concat(key)) : null;
    const out = Object.assign({}, parent || {}, def, { id: key, abstract: !!def.abstract });
    if (parent) out.chain = (parent.chain || [parent.id]).concat(key); else out.chain = [key];
    if (def.addLanes) out.lanes = (parent && parent.lanes || []).concat(def.addLanes);
    return out;
  }

  const normName = s => String(s).replace(/[\s《》“”"]/g, '');
  const lastPart = s => { const n = normName(s); const i = n.lastIndexOf('·'); return i < 0 ? n : n.slice(i + 1); };

  // ---------- 合并 ----------
  api.build = function () {
    const issues = [];
    const warn = (pack, msg) => issues.push({ level: 'warn', pack, msg });
    const err = (pack, msg) => issues.push({ level: 'error', pack, msg });

    const packs = [];
    if (window.ATLAS) packs.push(legacyCore(window.ATLAS, window.ATLAS_DETAIL));
    registered.forEach(p => { if (p.id === 'core') err(p.id, '包 id "core" 是保留名'); else packs.push(p); });
    const packIds = new Set(packs.map(p => p.id));
    packs.forEach(p => (p.requires || []).forEach(r => { if (!packIds.has(r)) err(p.id, `依赖的包 ${r} 没有加载`); }));

    const kindTable = Object.assign({}, BASE_KINDS), tplTable = Object.assign({}, BASE_TEMPLATES);
    packs.forEach(p => {
      Object.entries(p.kinds || {}).forEach(([k, v]) => { if (kindTable[k]) err(p.id, `条目类型 ${k} 已存在`); else kindTable[k] = Object.assign({ pack: p.id }, v); });
      Object.entries(p.templates || {}).forEach(([k, v]) => { if (tplTable[k]) err(p.id, `模板 ${k} 已存在`); else tplTable[k] = Object.assign({ pack: p.id }, v); });
    });
    const kinds = {}, templates = {};
    Object.keys(kindTable).forEach(k => { try { kinds[k] = resolveChain(kindTable, k); } catch (e) { err(kindTable[k].pack, e.message); } });
    Object.keys(tplTable).forEach(k => { try { templates[k] = resolveChain(tplTable, k); } catch (e) { err(tplTable[k].pack, e.message); } });

    // 大类 / 小类 / 领域
    const categories = [], catById = {}, clusterOf = {}, domains = {};
    const findCluster = ref => { for (const c of categories) for (const s of c.clusters) if (s.id === ref || s.name === ref) return { c, s }; return null; };
    packs.forEach(p => {
      (p.categories || []).forEach(c => {
        let cat = catById[c.id];
        if (!cat) { cat = { id: c.id, name: c.name, color: c.color, pack: p.id, clusters: [] }; catById[c.id] = cat; categories.push(cat); }
        (c.clusters || []).forEach(s => {
          const hit = findCluster(s.id);
          if (hit) s.domains.forEach(d => hit.s.domains.push(d));
          else cat.clusters.push({ id: s.id, name: s.name, pack: p.id, domains: s.domains.slice() });
        });
      });
      Object.entries(p.placement || {}).forEach(([d, where]) => {
        const hit = findCluster(where.cluster);
        if (!hit) return err(p.id, `领域 ${d} 要放进的小类 ${where.cluster} 不存在`);
        hit.s.domains.push(d);
      });
      Object.entries(p.domains || {}).forEach(([d, v]) => {
        if (domains[d]) return err(p.id, `领域 id ${d} 已被 ${domains[d].pack} 使用`);
        domains[d] = Object.assign({ id: d, pack: p.id, template: 'discipline' }, v);
        if (!templates[domains[d].template]) { warn(p.id, `领域 ${d} 的模板 ${domains[d].template} 不存在，改用 discipline`); domains[d].template = 'discipline'; }
      });
    });
    categories.forEach(c => c.clusters.forEach(s => {
      s.domains = s.domains.filter(d => { if (!domains[d]) { warn(c.pack, `小类 ${s.name} 里的领域 ${d} 没有定义`); return false; } return true; });
      s.domains.forEach(d => { clusterOf[d] = { category: c, cluster: s }; });
      if (s.domains.length > 3) warn(s.pack, `小类 ${s.name} 有 ${s.domains.length} 个领域，3D 视图每簇最多排 3 根光柱`);
    }));
    Object.keys(domains).forEach(d => { if (!clusterOf[d]) warn(domains[d].pack, `领域 ${d} 没有放进任何小类`); });

    // 条目
    const entries = new Map();
    const gidOf = (pack, id) => id.includes(':') ? id : pack + ':' + id;
    const add = (p, raw, extra) => {
      const gid = gidOf(p.id, raw.id);
      if (entries.has(gid)) return err(p.id, `条目 ${gid} 重复`);
      let k = raw.k;
      if (!kinds[k] || kinds[k].abstract) { warn(p.id, `条目 ${gid} 的类型 ${k} 不存在，按“思想”处理`); k = 'idea'; }
      // 没写归属时，归到本包的默认领域（只有一个领域的包就是那一个）
      const own = p.defaultDomain || (p.domains && Object.keys(p.domains).length === 1 ? Object.keys(p.domains)[0] : null);
      const d = [].concat(raw.d || own || []).filter(x => { if (!domains[x]) { warn(p.id, `条目 ${gid} 指向不存在的领域 ${x}`); return false; } return true; });
      entries.set(gid, Object.assign({}, raw, extra || {}, { gid, pack: p.id, k, d, rel: (raw.rel || []).map(r => gidOf(p.id, r)) }));
    };
    packs.forEach(p => {
      (p.entries || []).forEach(e => add(p, e));
      (p.links || []).forEach(l => {
        [l.a, l.b].forEach(x => { if (!domains[x]) warn(p.id, `联动 ${l.id} 指向不存在的领域 ${x}`); });
        add(p, Object.assign({}, l, { k: 'link', d: [l.a, l.b], y: l.y1, y2: l.y2 }));
      });
    });
    // 补丁：给别的包里的条目追加归属和关联
    packs.forEach(p => (p.patches || []).forEach(pt => {
      const e = entries.get(pt.target);
      if (!e) return warn(p.id, `补丁目标 ${pt.target} 不存在`);
      (pt.addDomains || []).forEach(d => { if (domains[d] && !e.d.includes(d)) e.d.push(d); });
      (pt.addRel || []).forEach(r => e.rel.push(gidOf(p.id, r)));
      (e.patchedBy = e.patchedBy || []).push(p.id);
    }));

    // 同名人物、同名著作合并成一份：保留第一份，其余的归属和关联并进来
    const alias = new Map();
    const byName = new Map();
    entries.forEach(e => {
      if (e.k !== 'person' && e.k !== 'work') return;
      const key = e.k + '|' + normName(e.t);
      const first = byName.get(key);
      if (!first) return byName.set(key, e);
      e.d.forEach(d => { if (!first.d.includes(d)) first.d.push(d); });
      first.rel.push(...e.rel);
      if ((e.x || '').length > (first.x || '').length) first.x = e.x;
      (first.merged = first.merged || []).push(e.gid);
      alias.set(e.gid, first.gid);
    });
    alias.forEach((_, gid) => entries.delete(gid));
    const canon = gid => alias.get(gid) || gid;

    // 名字索引：把里程碑、联动里的 p（人物）和 bk（书）字符串解析成条目
    const nameIdx = { person: new Map(), work: new Map() }, lastIdx = new Map();
    entries.forEach(e => {
      if (e.k === 'person') {
        [e.t].concat(e.aka || []).forEach(n => nameIdx.person.set(normName(n), e.gid));
        const lp = lastPart(e.t); lastIdx.set(lp, lastIdx.has(lp) && lastIdx.get(lp) !== e.gid ? null : e.gid);
      } else if (e.k === 'work') {
        [e.t].concat(e.aka || []).forEach(n => nameIdx.work.set(normName(n), e.gid));
      }
    });
    const stubs = new Map();
    const stub = (k, name, from) => {
      const gid = 'stub:' + k + ':' + normName(name);
      let s = stubs.get(gid);
      if (!s) { s = { gid, pack: 'stub', k, t: name, d: [], rel: [], stub: true }; stubs.set(gid, s); }
      from.d.forEach(d => { if (!s.d.includes(d)) s.d.push(d); });
      return gid;
    };
    const resolvePerson = n => nameIdx.person.get(normName(n)) || lastIdx.get(lastPart(n)) || null;

    const relations = [];
    const seenRel = new Set();
    const rel = (s, t, r) => {
      if (s === t) return;
      const key = s < t ? s + '|' + t : t + '|' + s;
      if (seenRel.has(key)) return;
      seenRel.add(key); relations.push({ s, t, r });
    };
    entries.forEach(e => {
      e.rel.forEach(r => {
        const t = canon(r);
        if (!entries.has(t)) { warn(e.pack, `条目 ${e.gid} 关联了不存在的 ${r}`); return; }
        rel(e.gid, t, 'rel');
      });
      (e.p || []).forEach(n => rel(e.gid, resolvePerson(n) || stub('person', n, e), 'person'));
      (e.bk || []).forEach(n => rel(e.gid, nameIdx.work.get(normName(n)) || stub('work', n, e), 'work'));
    });
    stubs.forEach((s, gid) => entries.set(gid, s));

    const core = packs[0] && packs[0].id === 'core' ? packs[0] : null;
    const graph = {
      packs, kinds, templates, categories, domains, clusterOf, entries, relations, issues, alias,
      range: core ? core.range : [1760, new Date().getFullYear()],
      eras: core ? core.eras : [], shocks: core ? core.shocks : [], drivers: core ? core.drivers : {}
    };
    graph.lanesOf = d => (templates[(domains[d] || {}).template] || templates.discipline).lanes;
    return graph;
  };

  // ---------- 写回旧格式，让 3D 页面不用改就能显示新包 ----------
  // 3D 页面目前只认识四种泳道：自定义类型退回到最近的内置祖先，时段型退回“人物”竖条
  const legacyKind = kd => {
    const hit = kd.chain.slice().reverse().find(k => ['work', 'person', 'idea', 'debate'].includes(k));
    return hit || (kd.chain.includes('span') ? 'person' : 'idea');
  };

  api.toLegacy = function (g) {
    const core = g.packs.find(p => p.id === 'core');
    const base = core ? core._legacy : { A: { range: g.range, kinds: g.drivers, eras: [], shocks: [], cats: [], domains: {}, nodes: [], links: [] }, DET: {} };
    const A = Object.assign({}, base.A, {
      cats: g.categories.map(c => ({ id: c.id, name: c.name, color: c.color, subs: c.clusters.map(s => ({ name: s.name, domains: s.domains.slice(0, 3) })) })),
      domains: Object.assign({}, base.A.domains),
      nodes: base.A.nodes.slice(), links: base.A.links.slice()
    });
    const DET = {};
    Object.entries(base.DET || {}).forEach(([d, items]) => { DET[d] = items.slice(); });
    Object.values(g.domains).forEach(d => { if (d.pack !== 'core') A.domains[d.id] = d; });
    const lid = gid => gid.replace(':', '-');
    g.entries.forEach(e => {
      if (e.pack === 'core' || e.stub || !e.d.length) return;
      if (e.k === 'milestone') A.nodes.push({ d: e.d[0], y: e.y, w: e.w, t: e.t, x: e.x, p: e.p, bk: e.bk, e: e.e });
      else if (e.k === 'link') A.links.push({ a: e.a, b: e.b, y1: e.y1, y2: e.y2, k: e.drv, w: e.w, t: e.t, bg: e.bg, what: e.what, out: e.out, p: e.p, bk: e.bk, e: e.e });
      else {
        const d = e.d[0];
        (DET[d] = DET[d] || []).push(Object.assign({}, e, {
          id: lid(e.gid), k: legacyKind(g.kinds[e.k]),
          rel: e.rel.filter(r => { const t = g.entries.get(r); return t && t.d.includes(d) && t.k !== 'milestone'; }).map(r => g.entries.get(r).pack === 'core' ? r.split(':')[1] : lid(r))
        }));
      }
    });
    return { A, DET };
  };

  api.applyLegacy = function () {
    const g = api.build();
    if (g.issues.length) console.warn('[atlas] 数据检查：\n' + g.issues.map(i => `${i.level} [${i.pack}] ${i.msg}`).join('\n'));
    const { A, DET } = api.toLegacy(g);
    window.ATLAS = A; window.ATLAS_DETAIL = DET;
    return g;
  };

  window.Atlas = api;
})();
