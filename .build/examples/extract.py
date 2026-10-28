# Pull every code figure out of a volume: its caption, each code block with its language, and the
# recorded output if the figure shows one. Writes examples.json next to this script.
import re, json, html, pathlib, sys
WS = pathlib.Path(__file__).resolve().parents[2]
VOLS = ["tools", "programming", "algorithms", "mathematics", "architecture", "operating-systems", "networking",
        "compilers", "databases", "software-craft", "shipping-products", "distributed-systems",
        "production-reliability", "security-engineering", "ai-engineering"]
out = []
for v in VOLS:
    d = (WS / f"{v}-handbook.html").read_text(encoding="utf-8")
    meta = re.search(r'<span class="k">Code examples</span><span class="v">(.*?)</span>', d).group(1)
    for k, m in enumerate(re.finditer(r'<figure class="code".*?</figure>', d, re.S), 1):
        fig = m.group(0)
        sec = d.rfind('<section', 0, m.start()); ch = re.search(r'id="([a-z0-9]+)"', d[sec:sec + 200]).group(1)
        tag = re.sub(r'<[^>]+>', '', re.search(r'<span class="tag">(.*?)</span>', fig, re.S).group(1)) if '<span class="tag">' in fig else ""
        cap = html.unescape(re.sub(r'<[^>]+>', '', (re.search(r'<span class="file">(.*?)</span>', fig, re.S) or re.search(r'<figcaption>(.*?)</figcaption>', fig, re.S)).group(1)))
        blocks = []
        for pm in re.finditer(r'(<div class="out-h">(.*?)</div>\s*)?<pre( class="out")?><code class="language-([a-z]+)">(.*?)</code></pre>', fig, re.S):
            blocks.append({"out": bool(pm.group(3)), "outh": pm.group(2) or "", "lang": pm.group(4),
                           "text": html.unescape(re.sub(r'<[^>]+>', '', pm.group(5)))})
        out.append({"vol": v, "n": k, "ch": ch, "tag": tag, "cap": cap, "meta": meta, "blocks": blocks,
                    "start": m.start(), "end": m.end()})
(pathlib.Path(__file__).parent / "examples.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(len(out), "figures")
