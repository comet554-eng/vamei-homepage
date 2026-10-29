#!/usr/bin/env bash
# 提案 07「一笔」：双扣（ATOP 原厂旋钮，不印 logo），一笔护条 + 回声分片 + 柔和阴影。
# 生成 RAILLOK雪鞋款式提案07_一笔.pdf（3 页）+ 预览 png
# 依赖：python3 + numpy + scipy + shapely + pikepdf、node + playwright、poppler-utils；先 npm i
set -euo pipefail
cd "$(dirname "$0")"
TP="../vamei-boot/src/Vamei双扣2026TP_复制.pdf"
LOGO="src/RAILLOK_LOGO规范.pdf"
OUT="RAILLOK雪鞋款式提案07_一笔"
mkdir -p build
python3 tools/pdf2svg.py "$TP" 1 build/tp.json
python3 tools/pdf2svg.py "$LOGO" 3 build/mono.json
python3 tools/pdf2svg.py "$LOGO" 4 build/word.json
python3 tools/rail7.py build/tp.json build/mono.json build/word.json build
python3 tools/sheet7.py build build/word.json build/sheet7.html
node tools/pdf.js build/sheet7.html "$OUT.pdf"
python3 - "$OUT.pdf" <<'PY'
import sys, pikepdf
pdf = pikepdf.open(sys.argv[1], allow_overwriting_input=True)
pdf.docinfo['/Title'] = 'RAILLOK 雪鞋款式提案 07 · 一笔'
pdf.save(sys.argv[1])
PY
pdftoppm -r 200 -png "$OUT.pdf" "$OUT"
echo "done: $OUT.pdf"
