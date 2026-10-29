#!/usr/bin/env bash
# 提案 04「轨与锁」：照 Vamei TP 的画法出矢量款式图。生成 RAILLOK雪鞋款式提案04_轨与锁.pdf（3 页）+ 预览 png
# 依赖：python3 + numpy + scipy + shapely + pikepdf、node + playwright、poppler-utils；先 npm i
set -euo pipefail
cd "$(dirname "$0")"
TP="../vamei-boot/src/Vamei双扣2026TP_复制.pdf"
LOGO="src/RAILLOK_LOGO规范.pdf"
OUT="RAILLOK雪鞋款式提案04_轨与锁"
mkdir -p build
python3 tools/pdf2svg.py "$TP" 1 build/tp.json
python3 tools/pdf2svg.py "$LOGO" 3 build/mono.json
python3 tools/pdf2svg.py "$LOGO" 4 build/word.json
for cw in tp slate bone sage black; do
  python3 tools/tp4.py build/tp.json build/mono.json build/word.json $cw build/t4-$cw.svg
done
python3 tools/sheet4.py build build/word.json build/sheet4.html
node tools/pdf.js build/sheet4.html "$OUT.pdf"
python3 - "$OUT.pdf" <<'PY'
import sys, pikepdf
pdf = pikepdf.open(sys.argv[1], allow_overwriting_input=True)
pdf.docinfo['/Title'] = 'RAILLOK 雪鞋款式提案 04 · 轨与锁'
pdf.save(sys.argv[1])
PY
pdftoppm -r 200 -png "$OUT.pdf" "$OUT"
echo "done: $OUT.pdf"
