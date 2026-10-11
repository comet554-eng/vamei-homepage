# 你真的能忘掉一个人吗？

9:16 竖屏交互式视觉作品。单文件 `index.html`，无构建、无依赖（字体来自 Google Fonts，加载失败时回退系统宋体），声音由 WebAudio 实时合成。

- 打开 `index.html`：按住屏幕（或空格键）删除 TA，松手 TA 会回来一点。
- 打开 `index.html?demo`：自动演示全流程，适合录屏发抖音（录屏前先点一下画面以开启声音）。

叙事：删除进度不断被「那首歌 / 那阵香水 / 那场梦」打回 → 卡在 99.999% → 删除失败 → TA 的粒子重组成「我」→ 删除还是留着。

## 短视频版：《大脑没有删除键》

`video/` 下是专为抖音 / 小红书 / 视频号做的约 50 秒成片版本（1080×1920，30fps），情绪为主，穿插 3 个知识点（白熊效应、气味与记忆、习惯与程序性记忆）。

- 预览：浏览器打开 `video/film.html`，点击画面即可带声音播放。
- 导出：`node video/render.js [输出目录]`，生成 `video.mp4` 和封面 `cover.jpg`（需要 playwright 与 ffmpeg）。
- 画面和声音由同一条时间轴驱动，改 `film.html` 顶部的 `M`（关键节点）/ `PROG` / `TX` / `EV` 即可调整节奏与文案。

## 滑雪不难（教学系列）

- EP.01《为什么你一害怕就往后坐》：`video/ski-ep01.html`，约 2 分 26 秒，明亮的线条动画风格。
- 导出：`node video/render.js video/ski-ep01.html [输出目录]`。每集在页面里用 `FILM.encode` 指定码率，导出脚本自动采用。
- 画面是时间的纯函数，每个场景是 `S` 数组里的一个函数，场景起止时间在 `T`，字幕在 `TX`。
- 封面：`node video/covers.js video/ski-ep01.html video/滑雪不难EP01-封面`，一次生成竖版 9:16、3:4 和横版 16:9、4:3 四个尺寸。
- EP.02《摔倒也是一门技术》（单板）：`video/ski-ep02.html`，约 2 分 25 秒。
- EP.02 起各集共用 `video/snowkit.js`（字幕、雪景、配乐、转场、导出与封面接口），每集只写自己的场景、字幕、音效和封面排版，最后调用 `kitRun(...)`。
- EP.01 单板版：`video/ski-ep01-sb.html`，侧面视角（整块板沿坡、前脚在山下），结构与双板版一致。
- EP.02 双板版：`video/ski-ep02-ski.html`；双板侧面小人抽到了 `video/skirig.js`，正面小人在本页里。
- EP.03 单板《落叶飘，到底在练什么》：`video/ski-ep03-sb.html`；单板两种视角的小人抽到了 `video/sbrig.js`。
- EP.03 双板《八字刹车，为什么能停下》：`video/ski-ep03-ski.html`（俯视受力 + 正面迎面视角）。
- EP.04 单板《换刃：从落叶飘到第一个弯》：`video/ski-ep04-sb.html`。
- EP.04 双板《八字转弯：压哪边，往哪转》：`video/ski-ep04-ski.html`（讲左右脚用背面视角）；八字相关绘制抽到了 `video/skiwedge.js`。
- EP.05 单板《连续转弯：用转弯来控速》：`video/ski-ep05-sb.html`（俯视轨迹按"朝下 / 横过来"上色，速度为示意曲线）。
- EP.05 双板《从八字到平行：把八字收起来》：`video/ski-ep05-ski.html`（俯视双板 `skiPair()` 可分别设定两块板角度，演示内脚并过来）。
- EP.06 单板《搓雪还是刻滑：雪上的两种痕迹》：`video/ski-ep06-sb.html`（俯视痕迹 `skidTrack` / `carveTrack`、板的横截面、侧切示意）。
- EP.06 双板《点杖到底在点什么》：`video/ski-ep06-ski.html`（俯视平行双板带雪杖 `topPar()`、沿 S 形自动在新弯内侧点杖 `rideWithPlants()`、侧面杖尖瞄准 `plantPose()`）。
- EP.07 单板《腿为什么这么累：像弹簧一样起伏》：`video/ski-ep07-sb.html`（起伏地形 `terrain()` / `bumpState()`，吸收与伸直两种模式，头部高度轨迹对比）。
- EP.07 双板《搓雪还是刻滑：双板的两种痕迹》：`video/ski-ep07-ski.html`（俯视双板 `topSkis()`、两条"铁轨"痕迹 `railTrack()`、两块板横截面 `crossSkis()`）。
- EP.08 双板《腿为什么这么累：学会用腿吸收》：`video/ski-ep08-ski.html`（侧面双板小人走起伏地形，按头部高度自动选蹲起幅度）。
- EP.08 单板《雪道上，谁该让谁？》：`video/ski-ep08-sb.html`（俯视多人雪道、视线扇形 `cone()`、侧面坡顶遮挡视线）。
- EP.09 单板《雪况：硬雪、粉雪、烂雪怎么滑》：`video/ski-ep09-sb.html`（侧面雪面质感 `surface()`：灯芯绒 / 冰面 / 雪包，粉雪前景 `powderFront()`）。
