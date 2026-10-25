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
        txt = ep.plain(s).replace("①", "第一，").replace("②", "第二，").replace("③", "第三，").replace("④", "第四，")
        out.append(f"- `{int(a) // 60}:{int(a) % 60:02d}` {txt}")
d = ep.DUR
print(f"## 第{ep.LESSON}课《{sys.argv[2]}》（{int(d) // 60}:{int(d) % 60:02d}）\n")
print("\n".join(out))
