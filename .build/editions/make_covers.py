"""Cover images for the e-books: the book's name and the sixteen stages, its own highlighted.

    python3 make_covers.py WS OUTDIR [slug ...]     writes OUTDIR/<slug>.png (1600 x 2400)"""
import html, re, subprocess, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bookmeta import books

WS = pathlib.Path(sys.argv[1]).resolve(); OUT = pathlib.Path(sys.argv[2]).resolve(); ONLY = sys.argv[3:]
WORK = OUT.parent / ".covers"; OUT.mkdir(parents=True, exist_ok=True); WORK.mkdir(exist_ok=True)

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=IBM+Plex+Mono:wght@500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;1,8..60,400&display=swap">
<style>
html, body {{ margin: 0; width: 800px; height: 1200px; overflow: hidden; }}
body {{ background: #EFEFE9; color: #15181E; font-family: "Source Serif 4", Georgia, serif; position: relative; }}
.frame {{ position: absolute; inset: 56px 64px; display: flex; flex-direction: column; }}
.top {{ border-top: 6px solid #15181E; padding-top: 22px; font-family: "IBM Plex Mono", monospace; font-weight: 600;
  font-size: 19px; letter-spacing: .2em; text-transform: uppercase; color: #8A6A15; }}
.the {{ margin-top: 150px; font-family: Archivo, sans-serif; font-weight: 500; font-size: 52px; letter-spacing: -.02em; }}
.name {{ font-family: Archivo, sans-serif; font-weight: 800; font-size: {size}px; line-height: .9; letter-spacing: -.045em; margin-top: 4px; }}
.blurb {{ margin-top: 46px; font-size: 27px; line-height: 1.45; color: #3E444F; font-style: italic; max-width: 600px; }}
.stages {{ margin-top: auto; display: grid; grid-template-columns: repeat(16, 1fr); gap: 5px; }}
.stages span {{ height: 30px; border: 1.5px solid #B9B9AE; font-family: "IBM Plex Mono", monospace; font-size: 11px;
  display: flex; align-items: center; justify-content: center; color: #6A707B; }}
.stages span.on {{ background: #1B3CC0; border-color: #1B3CC0; color: #FFFFFF; font-weight: 600; }}
.foot {{ margin-top: 22px; display: flex; justify-content: space-between; font-family: "IBM Plex Mono", monospace;
  font-size: 16px; letter-spacing: .12em; text-transform: uppercase; color: #6A707B; }}
</style></head><body><div class="frame">
<div class="top">{top}</div>
<div class="the">The Engineer's</div>
<div class="name">{name}</div>
<div class="blurb">{blurb}</div>
<div class="stages">{stages}</div>
<div class="foot"><span>{foot_l}</span><span>{foot_r}</span></div>
</div></body></html>
"""

site = (WS / ".build/site-builder/build_site.py").read_text()
for b in books(WS):
    if ONLY and b["slug"] not in ONLY: continue
    if b["stage"]:
        top = f'Stage {b["stage"]} &middot; {b["subject"]}'
        blurb = b["blurb"]
        stages = "".join(f'<span class="{"on" if i == int(b["stage"]) else ""}">{i:02d}</span>' for i in range(16))
        foot_l, foot_r = "Companion volume", "The Engineer's Syllabus"
    else:
        top = "A self-directed curriculum"
        blurb = "Sixteen stages from your first line of code to the depth a team calls on when the system is on fire."
        stages = "".join(f'<span class="on">{i:02d}</span>' for i in range(16))
        foot_l, foot_r = "Sixteen stages", "Revised 2026"
    name = b["name"]
    size = 168 if len(name) <= 6 else 140 if len(name) <= 8 else 118
    page = PAGE.format(top=top, name=html.escape(name), blurb=blurb, stages=stages, foot_l=foot_l, foot_r=foot_r, size=size)
    src = WORK / f'{b["slug"]}.html'; src.write_text(page, encoding="utf-8")
    r = subprocess.run([str(HERE / "render"), "png", str(src), str(OUT / f'{b["slug"]}.png'), "800", "1200"], capture_output=True, text=True)
    print(b["slug"], r.stdout.strip() or r.stderr.strip()[-200:])
