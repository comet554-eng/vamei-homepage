"""从 ep.py 生成配音文稿的一节（markdown）：python3 voscript.py EPDIR 课名
ep.VO_EXTRA = {section: "台词"} 会在该段开头补一句画面大字对应的台词。"""
import sys, os
EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, EP)
import ep

extra = getattr(ep, "VO_EXTRA", {})
out, prev = [], None
for name, (t0, t1, S) in ep.SEC.items():
    if out:
        out.append("")
    if name in extra:
        tt = t0 + 0.1
        out.append(f"- `{int(tt) // 60}:{int(tt) % 60:02d}` {extra[name]}（画面大字，不出字幕）")
    for s, a, b in S:
        raw = s
        if getattr(ep, "MUSIC", None):           # 激情版：高亮词标成重读，破折号和冒号处停顿
            import re
            raw = re.sub(r"\{[a-z]\|([^}]*)\}", r"**\1**", raw).replace("——", "——⏸").replace("：", "：⏸")
        txt = ep.plain(raw).replace("①", "第一，").replace("②", "第二，").replace("③", "第三，").replace("④", "第四，")
        out.append(f"- `{int(a) // 60}:{int(a) % 60:02d}` {txt}")
d = ep.DUR
print(f"## 第{ep.LESSON}课《{sys.argv[2]}》（{int(d) // 60}:{int(d) % 60:02d}）\n")
if getattr(ep, "MUSIC", None):
    print("> 激情版：**加粗**的字重读，⏸ 处停半拍；整体语速比平时快一点，句尾往上扬。\n")
print("\n".join(out))
