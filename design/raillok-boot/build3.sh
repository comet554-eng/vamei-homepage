#!/usr/bin/env bash
# 提案 03「一线」：同色一体，光照渲染。生成 RAILLOK雪鞋款式提案03_一线.pdf（2 页）+ 预览 png
# 依赖：python3 + numpy + scipy + shapely + Pillow + pikepdf、node + playwright、poppler-utils；先 npm i
set -euo pipefail
cd "$(dirname "$0")"
TP="../vamei-boot/src/Vamei双扣2026TP_复制.pdf"
LOGO="src/RAILLOK_LOGO规范.pdf"
OUT="RAILLOK雪鞋款式提案03_一线"
mkdir -p build
python3 tools/pdf2svg.py "$TP" 1 build/tp.json
python3 tools/pdf2svg.py "$LOGO" 3 build/mono.json
python3 tools/pdf2svg.py "$LOGO" 4 build/word.json
python3 tools/ref.py build/tp.json build/ref.json
python3 tools/render3.py build/ref.json build/mono.json build/word.json black build/hero3.png 6
for cw in black slate sage bone; do
  python3 tools/render3.py build/ref.json build/mono.json build/word.json $cw build/cw3-$cw.png 2.4
done
python3 tools/crops3.py build/hero3.png build
python3 tools/sheet3.py build/mono.json build/word.json build/sheet3.html
node tools/pdf.js build/sheet3.html "$OUT.pdf"
python3 - "$OUT.pdf" <<'PY'
import sys, pikepdf
pdf = pikepdf.open(sys.argv[1], allow_overwriting_input=True)
pdf.docinfo['/Title'] = 'RAILLOK 雪鞋款式提案 03 · 一线'
pdf.save(sys.argv[1])
PY
pdftoppm -r 200 -png "$OUT.pdf" "$OUT"
echo "done: $OUT.pdf"
