#!/usr/bin/env bash
# RAILLOK 雪鞋款式提案：生成 RAILLOK雪鞋款式提案01.pdf（2 页）+ 每页预览 png
# 依赖：python3 + pikepdf + shapely、node + playwright（Chromium）、poppler-utils；先 npm i 装字体
set -euo pipefail
cd "$(dirname "$0")"
TP="../vamei-boot/src/Vamei双扣2026TP_复制.pdf"   # 复用大底、中底、内胆、提拉环、BOA 的形状
LOGO="src/RAILLOK_LOGO规范.pdf"
OUT="RAILLOK雪鞋款式提案01"
mkdir -p build
python3 tools/pdf2svg.py "$TP" 1 build/tp.json
python3 tools/pdf2svg.py "$LOGO" 3 build/mono.json    # 第 3 页：单独图形标
python3 tools/pdf2svg.py "$LOGO" 4 build/word.json    # 第 4 页：单独字标
python3 tools/boot.py build/tp.json build/mono.json build/word.json build/boot.svgfrag
python3 tools/sheet.py build/boot.svgfrag build/word.json build/sheet.html
node tools/pdf.js build/sheet.html "$OUT.pdf"
python3 - "$OUT.pdf" <<'PY'
import sys, pikepdf
pdf = pikepdf.open(sys.argv[1], allow_overwriting_input=True)
pdf.docinfo['/Title'] = 'RAILLOK 雪鞋款式提案 01'
pdf.save(sys.argv[1])
PY
pdftoppm -r 200 -png "$OUT.pdf" "$OUT"
echo "done: $OUT.pdf"
