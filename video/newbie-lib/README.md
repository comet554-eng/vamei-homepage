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
