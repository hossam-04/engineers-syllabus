# Every <pre><code> block in every volume, with where it sits (example figure, prose, exercise or
# solution), its language and its text. Writes blocks.json.
import re, json, html, pathlib
WS = pathlib.Path(__file__).resolve().parents[2]
VOLS = json.load(open(pathlib.Path(__file__).parent / "examples.json"))
VOLS = list(dict.fromkeys(e["vol"] for e in VOLS))
out = []
for v in VOLS:
    d = (WS / f"{v}-handbook.html").read_text(encoding="utf-8")
    figs = [(m.start(), m.end()) for m in re.finditer(r'<figure class="code".*?</figure>', d, re.S)]
    for k, m in enumerate(re.finditer(r'<pre( class="out")?><code class="language-([a-z]+)">(.*?)</code></pre>', d, re.S), 1):
        if m.group(1): continue
        p = m.start(); fig = next((i for i, (a, b) in enumerate(figs, 1) if a <= p < b), None)
        before = d[:p]
        sol = before.rfind('<div class="sol-body">') > before.rfind('</details>')
        ex = before.rfind('<div class="exercise"') > max(before.rfind('<div class="exercises">') - 1, 0) and \
             before.rfind('<div class="exercise"') > before.rfind('<div class="ch-end">')
        exercises_open = before.rfind('<div class="exercises">') > before.rfind('<div class="ch-end">')
        kind = "figure" if fig else ("solution" if sol else ("exercise" if exercises_open else "prose"))
        sec = before.rfind('<section'); ch = re.search(r'id="([a-z0-9]+)"', d[sec:sec + 200]).group(1)
        cap = ""
        if fig:
            a, b = figs[fig - 1]; f = d[a:b]
            c = re.search(r'<span class="file">(.*?)</span>', f, re.S) or re.search(r'<figcaption>(.*?)</figcaption>', f, re.S)
            cap = html.unescape(re.sub(r'<[^>]+>', '', c.group(1))) if c else ""
        out.append({"vol": v, "id": f"{v}#{k}", "ch": ch, "kind": kind, "fig": fig, "lang": m.group(2), "cap": cap,
                    "text": html.unescape(re.sub(r'<[^>]+>', '', m.group(3))), "pos": p})
json.dump(out, open(pathlib.Path(__file__).parent / "blocks.json", "w"), indent=1)
import collections
print(len(out), collections.Counter(b["kind"] for b in out))
