# vamei NUAGE 雪板详情页 · 设计规范

淘宝 / 天猫手机详情页，竖版长图。画布宽 **750 CSS px**，按 2 倍导出（1500px 宽）。
产品：VM88 进阶全能单板（硬度 5），配色 NUAGE（法语「云」），25/26 雪季。

## 概念：暮色云境

板面是一片傍晚的天：粉色云层、蓝紫色天幕、一轮满月；板底是粉到靛蓝的油画笔触。
整页像从黄昏滑进夜晚，最后在晨雾里收尾：

| 段落 | 情绪 | 底色 |
|---|---|---|
| 首屏 → 产品亮点 | 黄昏 | 粉紫渐变天空 |
| 科技 → 板型 → 细节 | 入夜 | 靛蓝 / 深夜蓝 |
| 板面展示 | 月光 | 深夜 + 满月 |
| 参数 / 尺码 / 保养 / 须知 / 品牌 | 晨雾 | 品牌米白 |

要像杂志、像高端户外品牌，不要像传统淘宝页：不用大色块按钮、不用描边圆角框堆叠、不用花哨渐变字、不用 emoji。
多留白，用细线（1px / 0.5px）和编号来组织信息。

## 颜色

```
--cream   #EFEDDF  品牌米白（主背景之一）
--paper   #F6F4EC  更亮的纸色
--grey    #BFBEBA  品牌暖灰
--ink     #16151C  正文黑
--ink-2   #4A4856  次要文字
--dusk    #E8A9B5  暮粉
--rose    #D9879A  强调色（价格、重点数字，少量用）
--lilac   #B8A9CF  淡紫
--haze    #8E8AB5  雾紫
--indigo  #2C2E57  靛蓝
--night   #15172E  深夜
--moon    #F3EFE4  月光白
```

## 字体

- 中文标题：Noto Serif SC 600 / 900，字距 0.04em
- 中文正文：Noto Sans SC 300 / 400，正文不小于 24px（750 宽画布）
- 法文 / 英文点缀：Cormorant Garamond Italic 300（例如 *Nuage*、*la nuit*）
- 编号、英文标签、数字：Inter 500 / 600，标签大写，字距 0.2em，18–20px
- 本地渲染时用 `src/fonts.css`（fontsource）

## 品牌元素

- logo：`assets/brand/vamei-*.svg`（stacked / horizontal / symbol / wordmark），`fill=currentColor`
- 招牌笔势：logo 里倒三角中的螺旋。可以把它抽成一条细螺旋线做装饰，克制使用
- 段落编号：`01 — 14` 用 Inter，配一条细线

## 素材目录

- `assets/src/`：原始素材（放大后的板面 / 板底、模特抠图、模特照裁切）
  - `nuage-top@4x.png` 板面正视图（584×2964，透明底，边缘有一点白边，用时内缩约 1.5%）
  - `nuage-base@4x.png` 板底正视图（576×2952）
  - `model-cutout.png` 模特 + 板抠图（1647×2800，透明）
  - `model-photo-crop.jpg` 模特实拍裁切（1061×2400，蓝天雪地，已裁掉度假村招牌）
- `assets/gen/`：生成的 3D 渲染和场景图
- `assets/svg/`：图示和图标
- `src/`：页面和生成器源码。`tools/render.mjs` 负责截图（会起本地服务器，页面需设置 `window.__READY = true`）

渲染：`node tools/render.mjs src/xxx.html out.png --w 750 --h 1000 --scale 2 [--transparent] [--query shot=hero]`
three.js 用 importmap 指向 `../node_modules/three/build/three.module.js` 和 `../node_modules/three/examples/jsm/`。
