# vamei NUAGE 雪板详情页

VM88 进阶全能单板（硬度 5）· NUAGE 云境配色 · 25/26 雪季，淘宝 / 天猫手机详情页。

- 设计规范：`DESIGN.md`
- 页面源码：`src/page.html` + `src/page.css` + `src/page.js`（750 CSS px 宽，共 15 屏）
- 素材：`assets/`（`src/` 原始素材，`gen/` 3D 渲染和场景图，`svg/` 图示和图标，`brand/` logo）
- 素材生成器：`src/board3d.html`（three.js 雪板渲染）、`src/scenes.html`（着色器天空 / 雪地）

## 导出

```bash
cd detail
npm install
node tools/export.mjs
```

输出到 `out/`：

| 路径 | 用途 |
|---|---|
| `out/taobao/*.jpg` | 淘宝手机详情切片，1242 宽，单张高度不超过 1546，按文件名顺序上传 |
| `out/sections/*.jpg` | 每屏一张，1500 宽（2 倍），可以给设计师或做主图 |
| `out/nuage-full.jpg` | 整页长图预览，750 宽 |

改文案直接改 `src/page.html`，再跑一次导出。
