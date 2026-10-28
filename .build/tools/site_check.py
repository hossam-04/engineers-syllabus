# Structural checks on every page of the site, plus a syntax check of each inline script.
import re, sys, pathlib, subprocess
OUT = pathlib.Path(sys.argv[1]); CHK = pathlib.Path(sys.argv[2])
pages = sorted(p.name for p in OUT.glob("*.html")); bad = 0
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
print("SITE OK" if not bad else f"{bad} page(s) with problems")
