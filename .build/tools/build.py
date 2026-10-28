# Build a companion volume: concatenate NN_*.html parts, escape raw code, fill counts, check structure.
# Usage: build.py SRC_DIR OUT_FILE
import sys, re, html, pathlib
src = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
parts = sorted(p for p in src.glob("[0-9][0-9]_*.html"))
problems = []
CODE = re.compile(r'<pre><code class="language-([a-z0-9]+)">(.*?)</code></pre>', re.S)

def escape_code(text, name):
    def rep(m):
        lang, body = m.group(1), m.group(2).strip("\n")
        if re.search(r'&(lt|gt|amp|quot|nbsp|#\d+);', body):
            problems.append(f"{name}: HTML entity inside raw {lang} code (would double-escape)")
        return f'<pre><code class="language-{lang}">{html.escape(body, quote=False)}</code></pre>'
    return CODE.sub(rep, text)

def words(text):
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', text, flags=re.S)
    return len(re.sub(r'<[^>]+>', ' ', t).split())

chunks = []; total_ex = 0; total_code = 0
for p in parts:
    t = p.read_text(encoding="utf-8")
    ex = t.count('class="exercise"'); total_ex += ex
    n_code = len(CODE.findall(t)); total_code += n_code
    w = words(t); rt = max(1, round(w / 220))
    t = t.replace("{{RT}}", str(rt)).replace("{{EX}}", str(ex))
    t = escape_code(t, p.name)
    if "_ch" in p.name: print(f"{p.name:16} {w:6} words {rt:3} min {ex:2} exercises {n_code:2} code blocks")
    chunks.append(t)
doc = "\n".join(chunks)
figs = doc.count('<figure class="code')
doc = doc.replace("{{FIGTOTAL}}", str(figs)).replace("{{EXTOTAL}}", str(total_ex))

# ---- structural checks ----
body = re.sub(r'<(script|style)\b.*?</\1>', '', doc, flags=re.S)
for tag in ("section", "div", "details", "figure", "ul", "ol", "table", "svg", "pre", "main", "aside", "nav", "summary", "header", "footer"):
    o = len(re.findall(r'<' + tag + r'[\s>]', body)); c = body.count(f'</{tag}>')
    if o != c: problems.append(f"<{tag}> {o} opened / {c} closed")
nocode = re.sub(r'<pre\b.*?</pre>|<code\b.*?</code>', '', body, flags=re.S)
ids = re.findall(r'\sid="([^"]+)"', nocode); idset = set(ids)
dup = sorted({i for i in ids if ids.count(i) > 1})
if dup: problems.append(f"duplicate ids: {dup}")
for h in sorted(set(re.findall(r'href="#([^"]+)"', nocode))):
    if h not in idset: problems.append(f"broken anchor #{h}")
for r in sorted(set(re.findall(r'url\(#([^)]+)\)', nocode))):
    if r not in idset: problems.append(f"unresolved marker url(#{r})")
n_ex, n_sol = doc.count('class="exercise"'), doc.count('class="solution"')
if n_ex != n_sol: problems.append(f"exercises {n_ex} vs solutions {n_sol}")
for m in CODE.finditer(doc):
    if "<" in m.group(2): problems.append("unescaped < inside code")
left = re.findall(r'\{\{(RT|EX|FIGTOTAL|EXTOTAL)\}\}', doc)
if left: problems.append(f"unfilled placeholders: {set(left)}")
if re.search(r'__(EXAMPLE|SVG|CODE)', doc): problems.append("unexpanded template marker")
for m in re.finditer(r'<script>(.*?)</script>', doc, re.S):
    if re.search(r'\b(confirm|alert|prompt)\s*\(', re.sub(r'//[^\n]*', '', m.group(1))): problems.append("dialog call in script")

out.write_text(doc, encoding="utf-8")
print(f"code blocks escaped: {total_code}   worked examples: {figs}   exercises: {total_ex}")
print(f"total words: {words(doc)}   bytes: {len(doc.encode())}")
print("no structural problems found" if not problems else "PROBLEMS:\n  - " + "\n  - ".join(problems))
sys.exit(1 if problems else 0)
