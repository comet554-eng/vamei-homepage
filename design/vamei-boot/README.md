# Vamei 双扣雪鞋 · 配色稿

- `src/Vamei双扣2026TP_复制.pdf`：白色线稿（TP），所有配色都从它出。
- `src/Vamei双扣黑灰.pdf`：黑灰配色（中间面 Quiet Shade，其它地方全黑）。
- `Vamei双扣白灰.pdf` / `.png`：白灰配色，由 `build.sh` 从 TP 线稿生成，矢量，可直接用 Illustrator 打开改。

## 白灰配色

| 部位 | 颜色 |
|---|---|
| 中间面（和黑灰版灰色的面完全一样） | PANTONE 18-4006 TPG Quiet Shade |
| 织带、内里领口、提拉环、大底 | 同上 |
| 圆标三角、后跟小标、鞋舌旁织网 | 灰 |
| 其它地方：鞋带区、侧片、鞋头、后跟、中底、BOA、鞋带 | PANTONE 11-4201 TPG Cloud Dancer（米白，不是死白） |
| 侧面 vamei 字标 | 米白 |

灰色和黑灰版中间面是同一个色号，两款可以共用一批料。

## 重新生成

```
npm i          # 装色卡栏用的字体
./build.sh
```

`tools/walk.py` 列出 TP 稿里每个色块的绘制序号和范围，`tools/spec.py` 按序号定颜色，
`tools/recolor.py` 改色并去掉右边的修改说明，`tools/panel.html` 是右侧色卡栏，`tools/compose.py` 叠在一起。
改颜色只需要改 `spec.py` 顶部的色值或部件表。
