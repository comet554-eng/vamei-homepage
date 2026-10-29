"""把色卡栏叠到换好色的线稿上，写入标题。
usage: compose.py boot.pdf panel.pdf out.pdf title"""
import sys, pikepdf

boot_path, panel_path, out_path, title = sys.argv[1:5]
pdf = pikepdf.open(boot_path)
panel = pikepdf.open(panel_path)
page = pdf.pages[0]
page.add_overlay(panel.pages[0], pikepdf.Rectangle(*[float(v) for v in page.mediabox]))
pdf.docinfo['/Title'] = title
with pdf.open_metadata() as meta:
    meta['dc:title'] = title
pdf.save(out_path)
