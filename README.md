# knowledge-atlas · 知识脉络图

一张可交互的 3D 跨领域知识地图，时间范围从 1760 年至今。它把设计、制造、电子信息、AI、货币、经济、心理、组织、地缘等领域的发展脉络放进同一个空间里，用来建立全局认识，作为继续学习的脚手架。

- **全局视图**：每个领域是一根光柱，柱上标出发展阶段和关键节点。领域之间用光弧相连，每条弧都说明“具体发生了什么，才促成两个领域联动”。
- **领域视图**：把一根光柱展开成五条泳道，分别是里程碑、经典著作、人物、思想、辩论。其他领域只显示为可以点击跳转的出口，不展开内容。
- **图谱视图**（`graph.html`）：类似 Obsidian 的平面网络。所有条目和关联都画出来，支持局部图谱、按年份播放生长，还会列出“最常被提到、还没写的”条目。
- **知识包**：新领域写成一个独立的文件（`src/packs/*.js`），声明放在哪个大类、继承哪个模板、连到哪些已有领域，就能自动接进上面三个视图。

**在线演示**：https://claude.ai/artifact/XFaAjVCBKLLL42HBHNUb9D
（托管在 claude.ai 上，可能和仓库里的最新代码有出入；以仓库代码为准，本地运行方法见下文。）

## 两篇文章：这套学习方法为什么有效

这个项目来自一套学习方法：**先理清脉络，定好关键词，看清它们之间的关联，然后自己去理解、补全其中一部分。** 下面两篇文章解释了它为什么有效：

1. [人是如何学习的：为什么“脉络 + 关键词”有效](docs/method/01-how-humans-learn.md)：结构为什么让人去理解，而报告让人去背；为什么只有真正消耗了脑力，才能形成深刻的认知。
2. [人与 AI 协作：为什么这种方式对 AI 也高效](docs/method/02-human-ai-collaboration.md)：AI 本质上擅长压缩；迁就报告格式反而会干扰学习；由人定边界和格式，让 AI 做填空式思考。

> **关于内容准确性**：图里的节点、联动和说明由 AI 按主流共识生成，没有逐条核实，也没有标注出处。请把它当作学习的脚手架和待验证的假设，而不是权威资料。发现错误欢迎提 issue。

![全局视图](docs/assets/global-view.png)

![图谱视图](docs/assets/graph-view.png)

## 目录

```
docs/
  method/           两篇方法文章：人如何学习、人与 AI 如何协作
  glossary.md       术语表（先读这个）
  rfc-001-knowledge-packs.md  知识包（插件）与图谱视图的设计
  requirements.md   原始需求、访谈记录、用户反馈、待办
  design.md         当前实现的设计说明和已知问题
  data-schema.md    数据结构
  assets/           线框图和截图
src/
  index.html        3D 页面，按 claude.ai Artifact 格式编写，没有 <html>/<head>/<body> 外壳
  graph.html        图谱视图，完整的 HTML 文档
  atlas-core.js     知识包注册表：继承解析、合并、校验
  data.js           主体：领域、里程碑、联动
  detail.js         主体：著作、人物、思想、辩论
  packs/climate.js  示例知识包：气候科学
tools/
  screenshot.js     本地截图检查，用 Playwright 驱动
  gen_wireframe.py  生成最初的 SVG 线框图
```

## 本地运行

`src/index.html` 是 Artifact 页面片段。在浏览器里直接打开也能运行，浏览器会自动补上外壳。

页面依赖 CDN 上的 Three.js r128、OrbitControls，以及图谱视图用的 d3 7.8.5。如果网络无法访问 CDN，先把这些文件下载到 `tools/vendor/`，`tools/screenshot.js` 会读取这里的本地副本：

```bash
cd tools && npm pack three@0.128.0 && tar xzf three-0.128.0.tgz && mkdir -p vendor && cp package/build/three.min.js package/examples/js/controls/OrbitControls.js vendor/ && rm -rf package three-0.128.0.tgz
```

```bash
cd tools && npm pack d3@7.8.5 && tar xzf d3-7.8.5.tgz && cp package/dist/d3.min.js vendor/ && rm -rf package d3-7.8.5.tgz
```

截图命令的参数依次是：宽、高、输出文件，以及可选的一段在页面里执行的 JS（只能操作 DOM，页面内部函数不是全局的）。

```bash
node tools/screenshot.js 1440 900 out.local.png
PAGE=graph.html node tools/screenshot.js 1440 900 graph.local.png
```

## 状态

- 全局视图：3 个大类、9 个小类、19 个领域，142 个节点、62 条连线。
- 领域细节：已完成 AI、经济学、货币学、心理学。其余 15 个领域待补。
- 知识包：主体，以及示例包“气候科学”。

更多计划见 [docs/requirements.md](docs/requirements.md#5-当前状态与待办)。
