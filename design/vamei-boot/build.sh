#!/usr/bin/env bash
# 由 TP 线稿生成白灰配色稿：Vamei双扣白灰.pdf + 预览 png
# 依赖：python3 + pikepdf、node + playwright（Chromium）、poppler-utils；先 npm i 装字体
set -euo pipefail
cd "$(dirname "$0")"
TP="src/Vamei双扣2026TP_复制.pdf"
OUT="Vamei双扣白灰"
mkdir -p build
python3 tools/walk.py "$TP" build/tp.json > /dev/null
python3 tools/spec.py build/tp.json build/spec.json
python3 tools/recolor.py "$TP" build/boot.pdf build/spec.json
node tools/panel.js build/panel.pdf
python3 tools/compose.py build/boot.pdf build/panel.pdf "$OUT.pdf" "$OUT"
pdftoppm -r 200 -png -singlefile "$OUT.pdf" "$OUT"
echo "done: $OUT.pdf $OUT.png"
