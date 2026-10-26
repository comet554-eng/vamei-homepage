#!/usr/bin/env bash
# 提案 09：结构草图（铅笔草图风格）。双扣 ATOP 原厂旋钮，重点是分片层次、双扣分区走线、锁跟织带、内部加强件。
# 生成 RAILLOK雪鞋结构草图09.pdf（3 页）+ 预览 png
# 依赖：python3 + shapely + pikepdf、node + playwright、poppler-utils；先 npm i
set -euo pipefail
cd "$(dirname "$0")"
TP="../vamei-boot/src/Vamei双扣2026TP_复制.pdf"
LOGO="src/RAILLOK_LOGO规范.pdf"
OUT="RAILLOK雪鞋结构草图09"
mkdir -p build
python3 tools/pdf2svg.py "$TP" 1 build/tp.json
python3 tools/pdf2svg.py "$LOGO" 3 build/mono.json
python3 tools/pdf2svg.py "$LOGO" 4 build/word.json
python3 tools/sketch9.py build/tp.json build/mono.json build/word.json build
python3 tools/sheet9.py build build/word.json build/sheet9.html
node tools/pdf.js build/sheet9.html "$OUT.pdf"
python3 - "$OUT.pdf" <<'PY'
import sys, pikepdf
pdf = pikepdf.open(sys.argv[1], allow_overwriting_input=True)
pdf.docinfo['/Title'] = 'RAILLOK 雪鞋结构草图 09'
pdf.save(sys.argv[1])
PY
pdftoppm -r 200 -png "$OUT.pdf" "$OUT"
echo "done: $OUT.pdf"
