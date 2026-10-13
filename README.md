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
- EP.09 双板《雪道上，谁该让谁？》：`video/ski-ep09-ski.html`（由单板 EP.08 改为双板俯视小人，盲区一段换成"走路贴边、回去捡东西先往上看"）。
- EP.10 双板《雪况：硬雪、粉雪、烂雪怎么滑》：`video/ski-ep10-ski.html`（由单板 EP.09 改为双板小人，粉雪一段改为正面"两脚平均用力"）。
- EP.10 单板《立刃：板立多高才咬得住》：`video/ski-ep10-sb.html`（顺着板看的横截面小人 + 角度弧 `angleArc()`、抓地条）。
- EP.11 单板《站姿怎么定：正脚、反脚和角度》：`video/ski-ep11-sb.html`（俯视大雪板 `bigBoard()`：固定器角度、站距、滑行方向；侧面固定器与鞋 `bindingSide()`）。
- EP.12 单板《魔毯、拖牵、缆车：单板怎么上下》：`video/ski-ep12-sb.html`（俯视单板可设后脚位置 `topSB()`、魔毯、拖牵侧面、缆车椅子 `chair()`）。
- EP.11 双板《立刃：板立多高才咬得住》：`video/ski-ep11-ski.html`（两块板横截面 `crossSkis()`，可分别设外脚、内脚角度）。
- EP.12 双板《雪鞋怎么穿才不疼》：`video/ski-ep12-ski.html`（雪鞋侧面剖面：外壳、内胆、扣子、魔术贴、脚和小腿）。
- EP.13 双板《魔毯、拖牵、缆车：双板怎么上下》：`video/ski-ep13-ski.html`（由单板 EP.12 改为双板，加上雪杖与腕带）。
- EP.14 双板《侧滑：陡坡下不去怎么办》：`video/ski-ep14-ski.html`。
- EP.15 双板《第一次上中级道：先看再滑》：`video/ski-ep15-ski.html`（俯视雪道地图、路线规划）。
- EP.13 单板《反脚也要会滑》：`video/ski-ep13-sb.html`（侧面镜像表现反着滑，L/R 两脚分色）。
- EP.14 单板《小跳：第一个 ollie》：`video/ski-ep14-sb.html`。
- EP.15 单板《第一次上中级道：先看再滑》：`video/ski-ep15-sb.html`。
- EP.16 单板《单板最常伤哪里：手腕和尾椎》：`video/ski-ep16-sb.html`（横截面小人往前、往后摔，护具部件）。
- EP.17 单板《平花入门：压板头、压板尾》：`video/ski-ep17-sb.html`（侧面压板 `placePress()`、板弯弧线）。
- EP.16 双板《双板最常伤哪里：膝盖》：`video/ski-ep16-ski.html`（杠杆特写、固定器脱离示意）。
- EP.17 双板《小回转：节奏快一点的连续转弯》：`video/ski-ep17-ski.html`（俯视上身朝下、板左右转，走廊路线）。

## 徒步不难（教学系列）

- 画面沿用 `video/snowkit.js` 的字幕、转场、配乐与导出框架，徒步专用画面在 `video/trailkit.js`：天空与日落 `hikeSky()`、太阳、云、飞鸟、远山、草地小路与花树 `hikeGround()`、背包小人 `drawHiker()`（步伐、坡度、累、挥手、头灯）、海拔剖面 `profile()`、路牌、时钟。
- EP.01《第一次徒步：选什么路线？》：`video/hike-ep01.html`，约 2 分 06 秒（距离、累计爬升、估时与日落时间轴、两条路线对比）。
- EP.02 起：`trailkit.js` 里加了系列模板（`bgWalk` 走路场景、`titleScene`、`listCards`、`mottoCard`、`endScene`、`hikeCover` 封面、`hikeSound` 声音）和物品图标 `ICO.*`、鞋 `shoe()`、T 恤 `tee()`、风雨 `windLines()` / `rainFall()`。
- EP.02《徒步鞋怎么选？》：`video/hike-ep02.html`（看路选鞋、鞋底抓地与软硬、高帮低帮、脚在鞋里的剖视 `footInShoe()`）。
- EP.03《徒步穿什么？》：`video/hike-ep03.html`（三层衣服的横截面圆环 `layers()`、洋葱式穿脱、海拔降温）。
- EP.04《一日徒步，背包里装什么？》：`video/hike-ep04.html`（饮水时间轴、物品宫格 `itemGrid()`、背包剖视 `packSection()`）。
- EP.05《登山杖：要不要买，怎么用？》：`video/hike-ep05.html`（示意小人 `fig()` 演示杖长与 90°、腕带特写、脚印与杖点交替）。
- EP.06《出发前，天气要看什么？》：`video/hike-ep06.html`（逐小时预报卡片、雷雨闪电、风口与林中路线、日落与预警）。
- EP.07《上坡怎么走才不喘？》：`video/hike-ep07.html`（台阶大步小步、说话测试、呼吸节奏、之字路与休息步）。
- EP.08《下坡怎么走，不伤膝盖？》：`video/hike-ep08.html`（刹车受力、冲击柱状图、弹簧缓冲 `spring()`、落脚点）。
- EP.09《路上怎么歇、怎么吃喝？》：`video/hike-ep09.html`（休息时间轴、补水与体力曲线 `curve()`、尿色示意）。
- EP.10《路标和轨迹怎么看？走岔了怎么办》：`video/hike-ep10.html`（俯视树林岔路 `forestBG()`、路标种类、手机轨迹偏离、原路退回）。

## 滑雪里的物理（科普系列）

- 制作规范见 `.claude/skills/ski-science/`（技能包、原始提示词、模板源码）。横屏 1920×1080，深色底、字幕 + 配乐，Python + cairo 程序化渲染。
- 《落在坡上，为什么不疼？》（单板跳台落地 · 等效下落高度）：源码 `video/ski-sci-EP02/`，叙事方案 `video/ski-sci-EP02-方案.md`。`jump.py` 是物理核心（桌面跳台、无阻力飞行、EFH、等 EFH 落地面），`scenes.py` 六个场景，`music.py` 配乐（落在坡上为铃声、砸到平地为闷响，时间由计算出的落地时刻决定）。`bash build.sh` 分块并行渲染并合成，`python3 covers.py 前缀` 出 4 张封面。
- 《雪板为什么能滑？》（压力融化 vs 摩擦生热）：源码 `video/ski-sci-EP01/`，叙事方案 `video/ski-sci-EP01-方案.md`。`art.py` 放所有物理数值（克拉珀龙方程、压强、摩擦功率、水膜上限）和画面元素（侧面滑雪小人、俯视雪板、熔点数轴放大、雪粒微观剖面 `Grains`、冰表面分子），`scenes.py` 六个场景。构建方式同上。
