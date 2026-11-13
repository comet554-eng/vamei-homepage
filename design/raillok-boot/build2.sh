#!/usr/bin/env bash
# 款式提案 02「壳与芯」：生成 RAILLOK雪鞋款式提案02_壳与芯.pdf（2 页）+ 预览 png
# 依赖同 build.sh（python3 + pikepdf + shapely + Pillow、node + playwright、poppler-utils），先 npm i
set -euo pipefail
cd "$(dirname "$0")"
TP="../vamei-boot/src/Vamei双扣2026TP_复制.pdf"
LOGO="src/RAILLOK_LOGO规范.pdf"
OUT="RAILLOK雪鞋款式提案02_壳与芯"
mkdir -p build
python3 tools/pdf2svg.py "$TP" 1 build/tp.json
python3 tools/pdf2svg.py "$LOGO" 3 build/mono.json
python3 tools/pdf2svg.py "$LOGO" 4 build/word.json
python3 tools/ref.py build/tp.json build/ref.json
for cw in black-bone slate-bone sage-bone black-black; do
  python3 tools/boot2.py build/ref.json build/mono.json build/word.json $cw build/v2-$cw.svg --icon
  node tools/png.js build/v2-$cw.svg build/cw-$cw.png 1.4
done
cp build/v2-black-bone-icon.svg build/icon.svg
node tools/png.js build/v2-black-bone.svg build/hero.png 2.5
node tools/png.js build/v2-black-bone.svg build/hero-bg.png 4 '#E9E8E3'
python3 tools/crops.py build/hero-bg.png build
python3 tools/sheet2.py build/mono.json build/word.json build/sheet2.html
node tools/pdf.js build/sheet2.html "$OUT.pdf"
python3 - "$OUT.pdf" <<'PY'
import sys, pikepdf
pdf = pikepdf.open(sys.argv[1], allow_overwriting_input=True)
pdf.docinfo['/Title'] = 'RAILLOK 雪鞋款式提案 02 · 壳与芯'
pdf.save(sys.argv[1])
PY
pdftoppm -r 200 -png "$OUT.pdf" "$OUT"
echo "done: $OUT.pdf"
