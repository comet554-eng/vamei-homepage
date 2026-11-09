# 单板新手课 · 制作工具

竖屏 1080×1920、30 fps、不配音（字幕按阅读速度）。同一集出 **2D 版**和 **3D 版**：字幕、实拍、时间轴完全一样，只有人物演示不同。

- `../newbie-EPxx/ep.py`：字幕（`SECTIONS`）、动作关键帧（`PERF`）、机位（`cam`）、实拍镜头表（`FOOT`）、逐帧计划（`plan()`）、配乐重拍和音效（`music_hits()`）
- `comp.py`：合成（实拍 / 3D 帧 / 2D 插画 + 字幕、标注、数据图）
- `draw2d.py`：2D 扁平插画（和 3D 用同一套骨架 `rig3d.skeleton`）
- `render3d.py`：Blender（`pip install bpy`）渲 3D 帧，人物与场景沿用 `rig3d_day.py`（《单板从0到刻滑》第6课起的白天画风）
- `covers_nb.py` + `cover3d.py`：封面（第2课起只出 竖版3x4、横版4x3；`ALL4=1` 恢复 4 张）；`finish.py` + `music_up.py`：配乐、音效、压制
- `foot.py`：按 `ep.FOOT` 从 Mixkit 原片裁竖条 jpg 序列，并把用到的那段存进素材目录

## 第2课起（只出 2D 版）

- 每集 `ep.py` 自己写 `overlay(c, t, 帧, 关节像素坐标, K)`：标注、图表都在这里；`K` 是 comp.py 本身，提供 `hook_title`、`end_card`、`sec_window`、`bars`（柱状图）、`edge_diagram`（推坡截面图）、`dim`、`stamp`、`weight_bar` 等
- `COVER = dict(title, sub, items, perf, p, cam, bg=(素材ID, 秒), set={})`：封面文字、人物姿势、背景帧
- `MARKS = True`：地上画雪印（人在动时看得出在滑）；`slope` 参数会画出倾斜的坡面，`trail` 画雪痕
- 一集的完整流程：

```bash
python3 newbie-lib/foot.py newbie-EP02 <Mixkit原片目录> foot02 素材/单板新手课第2课
python3 newbie-lib/comp.py newbie-EP02 2d raw02.mp4 --foot foot02
python3 newbie-lib/finish.py newbie-EP02 raw02.mp4 单板新手课第2课-单脚蹬行.mp4
CLIPS=<Mixkit原片目录> python3 newbie-lib/covers_nb.py newbie-EP02 2d auto 单板新手课第2课-单脚蹬行
```

## 流程（在 video/ 下）

```bash
# 1. 实拍片段：按 ep.FOOT 从 Mixkit 原片裁成竖条 jpg 序列，放 foot/<镜头名>/0001.jpg…（见 newbie-EP01 的素材清单）
# 2. 3D 帧（约 10 秒/帧，可分进程：PART=0/2、1/2）
python3 newbie-lib/render3d.py newbie-EP01 r3d
# 3. 合成 + 配乐
python3 newbie-lib/comp.py newbie-EP01 2d raw2d.mp4 && python3 newbie-lib/finish.py newbie-EP01 raw2d.mp4 成片-2D版.mp4
python3 newbie-lib/comp.py newbie-EP01 3d raw3d.mp4 && python3 newbie-lib/finish.py newbie-EP01 raw3d.mp4 成片-3D版.mp4
# 4. 封面
python3 newbie-lib/cover3d.py newbie-EP01 cover_rider3d.png
python3 newbie-lib/covers_nb.py newbie-EP01 2d cover_bg.jpg 前缀-2D版
python3 newbie-lib/covers_nb.py newbie-EP01 3d cover_bg.jpg 前缀-3D版 cover_rider3d.png
```

字体：Noto Sans SC / Noto Serif SC（Google Fonts，装到 `~/.fonts`）。

## 李财和配乐（2026-11-09 起，第1–15课）

- `licai.py` + `licai/`：主持人李财（三花猫，骑行系列的同一个角色）。逐帧动画从骑行系列的 `licai-seq/*.js` 转成 `licai/<动作>/<帧>.webp` + `seq.json`；`comp.py` 每帧自动按段落叠加（开头踩滑雪板滑进来、要领段点头指向、原理段思考 / 划重点、错误段摔跟头 / 捂脸 / 吓一跳、练习段叉腰 / 拍手、结尾挥手）。ep.py 可写 `LICAI = {段落: 动作名}` 换动作，`LICAI_ON = False` 关掉。封面也会放李财踩滑雪板。
- 配乐：ep.py 写 `TRACK = (Mixkit 音乐编号, 起点秒)`，`finish.py` 用 `music_up.py --bed` 把这首曲子当底、叠上段落音效；曲子放在 `MUSIC_DIR`（默认 `../素材/音乐/原曲/`，仓库里没放原曲，从 `https://assets.mixkit.co/music/<编号>/<编号>.mp3` 下载）。没写 `TRACK` 时还是本地合成的三种风格。
- `turns.py`：转弯轨迹 → 关键帧（横切、弯、换刃、起伏 `rise`、搓雪甩尾 `skid`、刻滑倾倒 `lean`、反脚 `switch`），第6课起的弯都用它。
- `epkit.py`：第6课起的通用结构（`std_plan`、`std_hits`、`std_overlay`），每集只写字幕、动作、要领标签和原理图。
- `comp.py` 里的图表：`bars`（柱状图）、`lines`（折线图）、`edge_diagram`（推坡截面）、`dim`（压暗背景）。
