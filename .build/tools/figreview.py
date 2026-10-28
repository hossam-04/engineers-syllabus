# Build a review page of every flagged diagram in a volume, drawn with the volume's own styles,
# with each flagged label outlined in red and each flagged line overdrawn in orange.
# Usage: figreview.py VOLUME.html OUT.html [N,N,...]  (the listed diagrams are shown even when clean)
import html, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from svglint import check_svg
doc = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
head = doc[:doc.index('<div class="shell">')]
cards = []
also = {int(v) for v in sys.argv[3].split(',')} if len(sys.argv) > 3 else set()
for n, m in enumerate(re.finditer(r'<svg\b.*?</svg>', doc, re.S), 1):
    svg = m.group(0)
    labels, problems = check_svg(svg)
    if not problems and n not in also: continue
    marks = []
    for k, p in enumerate(problems, 1):
        for b in p["boxes"]:
            marks.append(f'<rect x="{b[0]:.1f}" y="{b[1]:.1f}" width="{b[2]-b[0]:.1f}" height="{b[3]-b[1]:.1f}" '
                         f'fill="none" stroke="#e5484d" stroke-width="1.2"></rect>')
        for l in p["lines"]:
            marks.append(f'<line x1="{l[0]}" y1="{l[1]}" x2="{l[2]}" y2="{l[3]}" stroke="#f76b15" stroke-width="2.5" '
                         f'stroke-opacity=".7"></line>')
    marked = svg.replace("</svg>", "".join(marks) + "</svg>")
    msgs = "".join(f"<li>{html.escape(p['msg'])}</li>" for p in problems)
    sec = doc.rfind('<section class="chapter', 0, m.start()); ch = re.search(r'id="(ch\d\d)"', doc[sec:sec + 200])
    cards.append(f'<div class="card" id="svg{n}"><h3 style="font:600 14px monospace">svg {n} &middot; '
                 f'{ch.group(1) if ch else "front"} &middot; {len(problems)} flag(s)</h3>'
                 f'<figure class="diagram">{marked}</figure><ol style="font:12px monospace">{msgs}</ol></div>')
page = ("<!doctype html><html><head><meta charset='utf-8'>" + head.replace("<title>", "<title>review: ") +
        "<style>.card{margin:28px 0;padding-bottom:18px;border-bottom:1px solid var(--rule)} body{padding:24px}"
        " figure.diagram svg{max-width:900px}</style></head><body>" + "".join(cards) + "</body></html>")
pathlib.Path(sys.argv[2]).write_text(page, encoding="utf-8")
print(sys.argv[1].split("/")[-1], len(cards), "flagged diagrams")
