# Structural checks on every page of the site, plus a syntax check of each inline script.
import re, sys, pathlib, subprocess
OUT = pathlib.Path(sys.argv[1]); CHK = pathlib.Path(sys.argv[2])
pages = sorted(p.name for p in OUT.glob("*.html")); bad = 0
# the flashcards page resolves #slug-NN itself, from the chapters listed in cards.js
import json
def js_data(name):
    f = OUT / name
    return json.loads(f.read_text(encoding="utf-8").split("=", 1)[1].rstrip().rstrip(";")) if f.exists() else None
CARDS = js_data("cards.js")
DECKS = {f'{v["slug"]}-{c[0]:02d}' for v in CARDS["vols"] for c in v["chapters"]} if CARDS else set()
for name in pages:
    doc = (OUT / name).read_text(encoding="utf-8"); probs = []
    body = re.sub(r'<(script|style)\b.*?</\1>', '', doc, flags=re.S)
    for tag in ("section", "div", "details", "figure", "ul", "ol", "table", "svg", "pre", "main", "aside", "nav", "summary", "header", "footer"):
        o = len(re.findall(r'<' + tag + r'[\s>]', body)); c = body.count(f'</{tag}>')
        if o != c: probs.append(f"<{tag}> {o}/{c}")
    nocode = re.sub(r'<pre\b.*?</pre>|<code\b.*?</code>', '', body, flags=re.S)
    ids = re.findall(r'\sid="([^"]+)"', nocode); idset = set(ids)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup: probs.append(f"duplicate ids {dup[:5]}")
    for h in sorted(set(re.findall(r'href="#([^"]+)"', nocode))):
        if h not in idset: probs.append(f"broken #{h}")
    for r in sorted(set(re.findall(r'url\(#([^)]+)\)', nocode))):
        if r not in idset: probs.append(f"marker #{r}")
    for h in sorted(set(re.findall(r'href="([a-z]+\.html)(?:#([^"]*))?"', nocode))):
        if h[0] not in pages: probs.append(f"missing page {h[0]}")
        elif h[0] == "review.html" and h[1] in DECKS: pass
        elif h[1]:
            other = (OUT / h[0]).read_text(encoding="utf-8")
            if f'id="{h[1]}"' not in other: probs.append(f"broken {h[0]}#{h[1]}")
    for k, js in enumerate(re.findall(r'<script>(.*?)</script>', doc, re.S)):
        f = CHK / f"chk_{name}.{k}.js"; f.write_text(js, encoding="utf-8")
        r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        if r.returncode: probs.append(f"script {k}: {r.stderr.strip()[:200]}")
        if re.search(r'\b(confirm|alert|prompt)\s*\(', re.sub(r'//[^\n]*', '', js)): probs.append("dialog call")
    if re.search(r'\{\{[A-Z]+\}\}', doc): probs.append("unfilled placeholder")
    bad += bool(probs)
    print(f"{name:15} {'OK' if not probs else 'PROBLEMS: ' + '; '.join(probs)}")
# every search result and every card must point at an anchor that exists
ID_CACHE = {}
def has_id(page, anchor):
    if page not in ID_CACHE:
        ID_CACHE[page] = set(re.findall(r'\sid="([^"]+)"', (OUT / page).read_text(encoding="utf-8"))) if (OUT / page).exists() else set()
    return anchor in ID_CACHE[page]
ROWS = js_data("search-index.js")
if ROWS is not None:
    gone = [f"{r[1]}#{r[2]}" for r in ROWS if not has_id(r[1], r[2])]
    empty = [f"{r[1]}#{r[2]}" for r in ROWS if not r[4] or not r[5]]
    print(f"search-index.js {len(ROWS)} entries", "OK" if not gone and not empty else f"PROBLEMS: missing {gone[:5]} empty {empty[:5]}")
    bad += bool(gone or empty)
if CARDS:
    pg = {v["slug"]: v["page"] for v in CARDS["vols"]}
    gone = [c[0] for c in CARDS["cards"] if not has_id(pg[c[1]], c[6])]
    empty = [c[0] for c in CARDS["cards"] if not c[4].strip() or not c[5].strip()]
    ids = [c[0] for c in CARDS["cards"]]; dup = sorted({i for i in ids if ids.count(i) > 1})
    print(f"cards.js        {len(ids)} cards", "OK" if not (gone or empty or dup) else f"PROBLEMS: missing {gone[:5]} empty {empty[:5]} dup {dup[:5]}")
    bad += bool(gone or empty or dup)
print("SITE OK" if not bad else f"{bad} page(s) with problems")
