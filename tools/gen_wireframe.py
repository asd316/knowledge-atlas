import math, html

W, H = 1600, 940
S = 82
OX, OY = 370, 650
ZMAX = 520
Y0, Y1 = 1760, 2026
FONT = "'PingFang SC','Noto Sans CJK SC','Microsoft YaHei','WenQuanYi Zen Hei',sans-serif"

def P(u, v, z=0):
    return OX + u * S - v * 0.55 * S, OY + u * 0.12 * S + v * 0.32 * S - z

def Z(year):
    t = (year - Y0) / (Y1 - Y0)
    return ZMAX * t ** 1.7

CAT = {
    "tech": ("技术与生产", "#38bdf8"),
    "econ": ("经济与资本", "#fb923c"),
    "soc":  ("人与社会",   "#a78bfa"),
}
REL = {
    "tech":   ("技术推动", "#5eead4", ""),
    "cap":    ("资本推动", "#facc15", ""),
    "policy": ("战争 / 政策", "#f87171", ""),
    "idea":   ("思想影响", "#e5e7eb", "4 4"),
}

# 大类 -> 小类 -> 领域 ; 区域 u 起点
TREE = [
    ("tech", 0.0, [("信息技术", ["电子信息", "通信与互联网", "AI"]),
                   ("工业生产", ["制造业", "能源"]),
                   ("创造与设计", ["设计", "传媒与内容"])]),
    ("econ", 3.55, [("金融体系", ["货币学", "金融市场"]),
                    ("经济理论", ["经济学", "博弈与决策"]),
                    ("商业组织", ["现代商业架构", "企业战略"])]),
    ("soc", 7.1, [("个体", ["心理学", "认知科学"]),
                  ("组织", ["组织管理学", "劳动与社会"]),
                  ("国际秩序", ["地缘政治", "国际贸易"])]),
]

# 领域 -> 坐标
pos, dcat = {}, {}
clusters = []
for cat, u0, subs in TREE:
    for i, (sub, doms) in enumerate(subs):
        uc, vc = u0 + 0.55 + i * 1.1, 1.1
        clusters.append((cat, sub, uc, vc))
        n = len(doms)
        offs = {2: [(-0.28, -0.45), (0.28, 0.45)],
                3: [(-0.32, -0.55), (0.32, -0.1), (-0.05, 0.6)]}[n]
        for d, (du, dv) in zip(doms, offs):
            pos[d] = (uc + du, vc + dv)
            dcat[d] = cat

# 阶段（色段）与节点（示意）
STAGES = {
    "货币学": [(1760, 1821, "复本位"), (1821, 1914, "金本位"), (1914, 1944, "战间混乱"),
              (1944, 1971, "布雷顿森林"), (1971, 2008, "信用货币 · 浮动汇率"), (2008, 2026, "QE · 数字货币")],
}
DEFAULT_STAGE_YEARS = [1760, 1840, 1900, 1945, 1990, 2026]
NODES = {
    "制造业": [1769, 1913, 1950, 2001], "能源": [1769, 1882, 1973, 2015],
    "电子信息": [1947, 1958, 1971, 2022], "通信与互联网": [1876, 1969, 1995, 2007],
    "AI": [1956, 1986, 2012, 2022], "设计": [1919, 1984, 2007], "传媒与内容": [1920, 1950, 2004],
    "货币学": [1821, 1944, 1971, 2008], "金融市场": [1792, 1929, 1971, 2008],
    "经济学": [1776, 1867, 1936, 1979], "博弈与决策": [1944, 1950, 1994],
    "现代商业架构": [1856, 1920, 1970, 1995], "企业战略": [1962, 1980, 1990],
    "心理学": [1879, 1913, 1956, 1979], "认知科学": [1956, 1980, 2000],
    "组织管理学": [1911, 1933, 1954, 1990], "劳动与社会": [1848, 1886, 1935, 1980],
    "地缘政治": [1815, 1914, 1944, 1991, 2022], "国际贸易": [1846, 1947, 1995, 2001],
}
LABELED = {("货币学", 1944): "布雷顿森林", ("地缘政治", 1944): "二战终局",
           ("AI", 2012): "深度学习", ("制造业", 1913): "福特流水线", ("经济学", 1776): "《国富论》"}

ARCS = [  # (年, 起, 止, 关系, 标签, 是否标注)
    (1776, "经济学", "制造业", "idea", "1776 分工理论", True),
    (1882, "能源", "制造业", "tech", "", False),
    (1913, "制造业", "组织管理学", "tech", "1913 流水线 → 科学管理", True),
    (1919, "设计", "制造业", "idea", "", False),
    (1944, "地缘政治", "货币学", "policy", "1944 布雷顿森林体系", True),
    (1956, "认知科学", "AI", "idea", "", False),
    (1969, "地缘政治", "通信与互联网", "policy", "1957→1969 冷战催生 ARPANET", True),
    (1971, "货币学", "金融市场", "policy", "", False),
    (1979, "心理学", "经济学", "idea", "1979 前景理论", True),
    (1970, "经济学", "企业战略", "idea", "", False),
    (1995, "通信与互联网", "现代商业架构", "cap", "1995 互联网商业化", True),
    (2001, "国际贸易", "制造业", "policy", "2001 中国入世", False),
    (2012, "电子信息", "AI", "tech", "", False),
    (2022, "地缘政治", "电子信息", "policy", "2022 芯片法案", True),
]
SEL = 4

o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
a('''<defs>
<radialGradient id="bg" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#101a33"/><stop offset="1" stop-color="#05070f"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glow2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>
<linearGradient id="fade" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity=".15"/></linearGradient>
</defs>''')
a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

# 地面网格
for k in range(0, 23):
    u = k * 0.5
    x1, y1 = P(u, -0.2); x2, y2 = P(u, 2.4)
    a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#1e2a4a" stroke-width="0.6"/>')
for k in range(0, 6):
    v = -0.2 + k * 0.52
    x1, y1 = P(-0.2, v); x2, y2 = P(10.9, v)
    a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#1e2a4a" stroke-width="0.6"/>')

# 大类地块
for cat, u0, subs in TREE:
    name, col = CAT[cat]
    pts = [P(u0, -0.1), P(u0 + 3.35, -0.1), P(u0 + 3.35, 2.3), P(u0, 2.3)]
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    a(f'<polygon points="{d}" fill="{col}" fill-opacity=".06" stroke="{col}" stroke-opacity=".55" stroke-width="1.2"/>')
    x, y = P(u0 + 0.1, 2.3)
    a(f'<text x="{x:.1f}" y="{y + 44:.1f}" fill="{col}" font-size="15" font-weight="700" letter-spacing="2">{name}</text>')
    a(f'<text x="{x:.1f}" y="{y + 60:.1f}" fill="{col}" fill-opacity=".6" font-size="10.5">大类</text>')

# 小类圈
for cat, sub, uc, vc in clusters:
    col = CAT[cat][1]
    cx, cy = P(uc, vc)
    a(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="58" ry="24" fill="none" stroke="{col}" stroke-opacity=".45" stroke-dasharray="3 3"/>')
    a(f'<text x="{cx:.1f}" y="{cy + 40:.1f}" text-anchor="middle" fill="{col}" fill-opacity=".85" font-size="11">{sub}</text>')

# 时间标尺（左后方）
rx, ry = P(-0.35, -0.2)
a(f'<line x1="{rx:.1f}" y1="{ry:.1f}" x2="{rx:.1f}" y2="{ry - ZMAX:.1f}" stroke="#3b4a72" stroke-width="1"/>')
for yr in [1760, 1800, 1850, 1900, 1925, 1945, 1970, 1990, 2010, 2026]:
    z = Z(yr)
    a(f'<line x1="{rx - 5:.1f}" y1="{ry - z:.1f}" x2="{rx:.1f}" y2="{ry - z:.1f}" stroke="#5b6b95"/>')
    a(f'<text x="{rx - 9:.1f}" y="{ry - z + 4:.1f}" text-anchor="end" fill="#7d8bb3" font-size="10.5">{yr}</text>')
    # 年份平面辅助线（淡）
    if yr in (1900, 1945, 1990):
        x2, y2 = P(10.9, -0.2, z)
        a(f'<line x1="{rx:.1f}" y1="{ry - z:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#2a375c" stroke-dasharray="2 6" stroke-width=".8"/>')
a(f'<text x="{rx - 9:.1f}" y="{ry - ZMAX - 16:.1f}" text-anchor="end" fill="#7d8bb3" font-size="10">时间 ↑</text>')

# 光柱（由后往前画）
order = sorted(pos, key=lambda d: pos[d][0] * 0.12 + pos[d][1] * 0.32)
for d in order:
    u, v = pos[d]; col = CAT[dcat[d]][1]
    x, yb = P(u, v)
    sel = d in ("货币学", "地缘政治")
    a(f'<line x1="{x:.1f}" y1="{yb:.1f}" x2="{x:.1f}" y2="{yb - ZMAX:.1f}" stroke="{col}" stroke-width="{14 if sel else 9}" opacity="{.35 if sel else .18}" filter="url(#glow2)"/>')
    stages = STAGES.get(d) or [(a_, b_, "") for a_, b_ in zip(DEFAULT_STAGE_YEARS, DEFAULT_STAGE_YEARS[1:])]
    for i, (s0, s1, lab) in enumerate(stages):
        za, zb = Z(s0), Z(s1)
        op = (.95 if i % 2 else .6) if sel else (.75 if i % 2 else .4)
        a(f'<line x1="{x:.1f}" y1="{yb - za - 1:.1f}" x2="{x:.1f}" y2="{yb - zb + 1:.1f}" stroke="{col}" stroke-width="{4.5 if sel else 3}" opacity="{op}"/>')
        if lab and d == "货币学":
            ym = yb - (za + zb) / 2
            a(f'<text x="{x - 10:.1f}" y="{ym + 3.5:.1f}" text-anchor="end" fill="{col}" font-size="10">{lab}</text>')
    a(f'<ellipse cx="{x:.1f}" cy="{yb:.1f}" rx="7" ry="3" fill="{col}" opacity=".8" filter="url(#glow)"/>')
    for yr in NODES.get(d, []):
        z = Z(yr); key = (d, yr) in LABELED
        r = 4.2 if key else 2.6
        a(f'<circle cx="{x:.1f}" cy="{yb - z:.1f}" r="{r}" fill="#fff" stroke="{col}" stroke-width="1.5" filter="url(#glow)"/>')
        if key and d != "货币学":
            a(f'<text x="{x + 8:.1f}" y="{yb - z + 4:.1f}" fill="#dfe6ff" font-size="10">{LABELED[(d, yr)]}</text>')
    # 顶部领域名（交错）
    stag = 0 if order.index(d) % 2 == 0 else 15
    ty_ = yb - ZMAX - 10 - stag; tw_ = len(d) * 12 + 10
    a(f'<rect x="{x - tw_ / 2:.1f}" y="{ty_ - 13:.1f}" width="{tw_}" height="18" rx="4" fill="#0b1224" fill-opacity=".85" stroke="{col}" stroke-opacity=".5"/>')
    a(f'<text x="{x:.1f}" y="{ty_:.1f}" text-anchor="middle" fill="#e8edff" font-size="11.5" font-weight="600">{d}</text>')

# 连线弧
for i, (yr, s, t, rel, lab, show) in enumerate(ARCS):
    rname, rcol, dash = REL[rel]
    (u1, v1), (u2, v2) = pos[s], pos[t]
    x1, y1 = P(u1, v1, Z(yr)); x2, y2 = P(u2, v2, Z(yr))
    dist = math.hypot(x2 - x1, y2 - y1)
    cx, cy = (x1 + x2) / 2, min(y1, y2) - 30 - dist * 0.18
    w = 2.6 if i == SEL else 1.3
    op = 1 if i == SEL else .7
    da = f' stroke-dasharray="{dash}"' if dash else ""
    if i == SEL:
        a(f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{rcol}" stroke-width="8" opacity=".35" filter="url(#glow2)"/>')
    a(f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{rcol}" stroke-width="{w}" opacity="{op}"{da} filter="url(#glow)"/>')
    for (px, py) in ((x1, y1), (x2, y2)):
        a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="{rcol}"/>')
    if show:
        mx, my = (x1 + 2 * cx + x2) / 4, (y1 + 2 * cy + y2) / 4
        tw = len(lab) * 10.5 + 14
        bw = 1.6 if i == SEL else 0.8
        a(f'<rect x="{mx - tw / 2:.1f}" y="{my - 22:.1f}" width="{tw:.1f}" height="18" rx="9" fill="#0b1224" fill-opacity=".9" stroke="{rcol}" stroke-width="{bw}"/>')
        a(f'<text x="{mx:.1f}" y="{my - 9:.1f}" text-anchor="middle" fill="{rcol}" font-size="10.5">{html.escape(lab)}</text>')
        if i == SEL:
            selpt = (mx + tw / 2, my - 13)

# ===== 界面外壳 =====
# 顶栏
a('<rect x="0" y="0" width="1600" height="56" fill="#070b17" fill-opacity=".92"/><line x1="0" y1="56" x2="1600" y2="56" stroke="#1f2a48"/>')
a('<text x="24" y="35" fill="#f1f4ff" font-size="19" font-weight="700" letter-spacing="1">知识脉络图</text>')
a('<text x="138" y="35" fill="#7d8bb3" font-size="12">1760 — 今 · 3 大类 · 9 小类 · 20 领域</text>')
a('<rect x="430" y="14" width="300" height="28" rx="14" fill="#0e1630" stroke="#2a375c"/><text x="450" y="33" fill="#5d6a90" font-size="12">⌕  搜索节点、人物、书籍、事件…</text>')
bx = 770
for lab, on in [("3D 透视", True), ("俯视", False), ("时间正视", False)]:
    w = len(lab) * 12 + 22
    a(f'<rect x="{bx}" y="14" width="{w}" height="28" rx="6" fill="{"#1d4ed8" if on else "#0e1630"}" fill-opacity="{.55 if on else 1}" stroke="{"#60a5fa" if on else "#2a375c"}"/>')
    a(f'<text x="{bx + w / 2}" y="33" text-anchor="middle" fill="{"#fff" if on else "#9aa6c9"}" font-size="12">{lab}</text>')
    bx += w + 6
bx += 14
a(f'<text x="{bx}" y="33" fill="#7d8bb3" font-size="12">显示：</text>')
bx += 40
for lab, on in [("仅关键点", True), ("全部节点", False)]:
    w = len(lab) * 12 + 22
    a(f'<rect x="{bx}" y="14" width="{w}" height="28" rx="6" fill="{"#1d4ed8" if on else "#0e1630"}" fill-opacity="{.55 if on else 1}" stroke="{"#60a5fa" if on else "#2a375c"}"/>')
    a(f'<text x="{bx + w / 2}" y="33" text-anchor="middle" fill="{"#fff" if on else "#9aa6c9"}" font-size="12">{lab}</text>')
    bx += w + 6
# 关系图例
lx = 1240
a(f'<text x="{lx}" y="25" fill="#7d8bb3" font-size="10.5">连线类型</text>')
for k, (key, (nm, c, dash)) in enumerate(REL.items()):
    xx = lx + (k % 2) * 170; yy = 34 + (k // 2) * 0  # one row
for k, (key, (nm, c, dash)) in enumerate(REL.items()):
    xx = lx + k * 88; yy = 42
    da = f' stroke-dasharray="{dash}"' if dash else ""
    a(f'<line x1="{xx}" y1="{yy - 4}" x2="{xx + 20}" y2="{yy - 4}" stroke="{c}" stroke-width="2"{da}/><text x="{xx + 25}" y="{yy}" fill="#c5cde6" font-size="10.5">{nm}</text>')

# 左侧：层级树
a('<rect x="0" y="56" width="230" height="804" fill="#070b17" fill-opacity=".82"/><line x1="230" y1="56" x2="230" y2="860" stroke="#1f2a48"/>')
a('<text x="20" y="86" fill="#9aa6c9" font-size="11" letter-spacing="1">层级  大类 › 小类 › 领域</text>')
ty = 116
for cat, u0, subs in TREE:
    nm, col = CAT[cat]
    a(f'<rect x="20" y="{ty - 11}" width="12" height="12" rx="3" fill="{col}"/><text x="40" y="{ty}" fill="{col}" font-size="13.5" font-weight="700">▾ {nm}</text>')
    ty += 22
    for sub, doms in subs:
        a(f'<text x="36" y="{ty}" fill="#c5cde6" font-size="12">▾ {sub}</text>')
        ty += 19
        for d in doms:
            hl = d in ("货币学", "地缘政治")
            a(f'<rect x="54" y="{ty - 10}" width="10" height="10" rx="2" fill="{col if True else "none"}" fill-opacity=".85" stroke="{col}"/>')
            a(f'<text x="70" y="{ty}" fill="{"#ffffff" if hl else "#8f9bc0"}" font-size="11.5" {"font-weight=\"700\"" if hl else ""}>{d}</text>')
            ty += 17
        ty += 3
    ty += 8
a(f'<text x="20" y="{ty + 6}" fill="#4f5b80" font-size="10.5">勾选控制光柱显隐 · 后续可继续拆分</text>')

# 右侧：详情面板
PX = 1240
a(f'<rect x="{PX}" y="56" width="360" height="804" fill="#080d1c" fill-opacity=".95"/><line x1="{PX}" y1="56" x2="{PX}" y2="860" stroke="#1f2a48"/>')
rc = REL["policy"][1]
y = 90
a(f'<text x="{PX + 22}" y="{y}" fill="#7d8bb3" font-size="11" letter-spacing="1">已选中 · 跨领域连线</text>')
a(f'<text x="{PX + 338}" y="{y}" text-anchor="end" fill="#5d6a90" font-size="14">✕</text>')
y += 34
a(f'<text x="{PX + 22}" y="{y}" fill="#f5f7ff" font-size="21" font-weight="700">1944 · 布雷顿森林体系</text>')
y += 26
a(f'<rect x="{PX + 22}" y="{y - 14}" width="92" height="20" rx="10" fill="{rc}" fill-opacity=".15" stroke="{rc}"/><text x="{PX + 68}" y="{y}" text-anchor="middle" fill="{rc}" font-size="11">战争 / 政策推动</text>')
a(f'<text x="{PX + 124}" y="{y}" fill="#a78bfa" font-size="12">地缘政治</text><text x="{PX + 180}" y="{y}" fill="#7d8bb3" font-size="12">→</text><text x="{PX + 196}" y="{y}" fill="#fb923c" font-size="12">货币学</text>')
y += 20
a(f'<text x="{PX + 22}" y="{y}" fill="#5d6a90" font-size="10.5">波及：经济学 · 国际贸易 · 金融市场</text>')
y += 16
a(f'<line x1="{PX + 22}" y1="{y}" x2="{PX + 338}" y2="{y}" stroke="#1f2a48"/>')

def para(title, lines, y):
    a(f'<text x="{PX + 22}" y="{y}" fill="#9aa6c9" font-size="11" font-weight="700" letter-spacing="1">{title}</text>')
    y += 20
    for ln in lines:
        a(f'<text x="{PX + 22}" y="{y}" fill="#d6dcf0" font-size="12.5">{ln}</text>')
        y += 19
    return y + 8

y += 26
y = para("背景", ["二战尾声，美国握有全球约 2/3 黄金储备；", "各国都怕重演 1930 年代的竞争性贬值。"], y)
y = para("发生了什么", ["44 国在美国新罕布什尔州约定：美元挂钩", "黄金，其他货币挂钩美元；同时成立 IMF", "与世界银行。"], y)
y = para("后果", ["美元成为世界货币，支撑战后 25 年贸易", "扩张；但埋下“特里芬难题”，最终导致", "1971 年尼克松关闭黄金窗口。"], y)
a(f'<line x1="{PX + 22}" y1="{y - 4}" x2="{PX + 338}" y2="{y - 4}" stroke="#1f2a48"/>')
y += 20

def chips(title, items, y, col):
    a(f'<text x="{PX + 22}" y="{y}" fill="#9aa6c9" font-size="11" font-weight="700" letter-spacing="1">{title}</text>')
    y += 12
    x = PX + 22
    for it in items:
        w = len(it) * 11.5 + 18
        if x + w > PX + 340:
            x = PX + 22; y += 28
        a(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="22" rx="5" fill="{col}" fill-opacity=".1" stroke="{col}" stroke-opacity=".5"/><text x="{x + w / 2:.1f}" y="{y + 15}" text-anchor="middle" fill="#e2e8ff" font-size="11.5">{it}</text>')
        x += w + 6
    return y + 42

y = chips("关键人物", ["凯恩斯", "哈里·D·怀特", "罗伯特·特里芬"], y, "#a78bfa")
y = chips("关键书籍", ["《布雷顿森林货币战》", "《嚣张的特权》", "《就业、利息和货币通论》"], y, "#fb923c")
y = chips("关键事件", ["1931 英镑脱金", "1944 会议召开", "1960 特里芬难题", "1971 尼克松冲击"], y, "#38bdf8")
a(f'<line x1="{PX + 22}" y1="{y - 12}" x2="{PX + 338}" y2="{y - 12}" stroke="#1f2a48"/>')
y += 10
a(f'<text x="{PX + 22}" y="{y}" fill="#9aa6c9" font-size="11" font-weight="700" letter-spacing="1">因果链</text>')
y += 20
a(f'<text x="{PX + 22}" y="{y}" fill="#7d8bb3" font-size="11.5">← 上游</text><text x="{PX + 80}" y="{y}" fill="#d6dcf0" font-size="11.5">1914 一战 · 金本位崩溃</text>')
y += 20
a(f'<text x="{PX + 22}" y="{y}" fill="#7d8bb3" font-size="11.5">→ 下游</text><text x="{PX + 80}" y="{y}" fill="#d6dcf0" font-size="11.5">1971 美元脱钩 → 金融市场膨胀</text>')

# 选中连线 → 面板的引导线
if 'selpt' in dir():
    pass

# 底部时间轴
a('<rect x="0" y="860" width="1600" height="80" fill="#070b17"/><line x1="0" y1="860" x2="1600" y2="860" stroke="#1f2a48"/>')
TX0, TX1 = 260, 1560
def TX(yr):
    return TX0 + (TX1 - TX0) * ((yr - Y0) / (Y1 - Y0)) ** 1.7 if False else TX0 + (TX1 - TX0) * (Z(yr) / ZMAX)
ERAS = [(1760, 1840, "第一次工业革命"), (1840, 1914, "第二次工业革命"), (1914, 1945, "世界大战"),
        (1945, 1991, "冷战"), (1991, 2008, "全球化"), (2008, 2026, "数字 / AI")]
cols = ["#1a2440", "#1d2a4a"]
for k, (a0, a1, nm) in enumerate(ERAS):
    x0, x1 = TX(a0), TX(a1)
    a(f'<rect x="{x0:.1f}" y="876" width="{x1 - x0 - 2:.1f}" height="20" rx="3" fill="{cols[k % 2]}"/>')
    a(f'<text x="{(x0 + x1) / 2:.1f}" y="890" text-anchor="middle" fill="#9aa6c9" font-size="10.5">{nm}</text>')
for yr in [1760, 1840, 1914, 1945, 1991, 2008, 2026]:
    a(f'<text x="{TX(yr):.1f}" y="914" text-anchor="middle" fill="#5d6a90" font-size="10">{yr}</text>')
a(f'<text x="24" y="891" fill="#9aa6c9" font-size="11">时间轴（非线性）</text>')
a(f'<text x="24" y="912" fill="#4f5b80" font-size="10">拖动框选年份范围</text>')
hx0, hx1 = TX(1930), TX(1975)
a(f'<rect x="{hx0:.1f}" y="872" width="{hx1 - hx0:.1f}" height="28" rx="4" fill="#60a5fa" fill-opacity=".12" stroke="#60a5fa"/>')

# 操作提示
a('<text x="250" y="844" fill="#4f5b80" font-size="10.5">拖拽旋转 · 滚轮缩放（缩小只显示关键点，放大显示全部节点）· 点击节点 / 连线查看详情</text>')
a('<text x="1222" y="844" text-anchor="end" fill="#4f5b80" font-size="10.5">线框示意 · 内容为样例</text>')
a('</svg>')
open(__import__('os').path.join(__import__('os').path.dirname(__file__), '../docs/assets/wireframe.svg'), 'w').write("\n".join(o))
print("ok")
