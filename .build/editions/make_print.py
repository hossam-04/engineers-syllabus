"""Print pages for the PDF editions: each volume's own styles, its reading content without the
interactive parts, and overrides for A4 paper. `render pdf` then lays them out through WebKit.

    python3 make_print.py WS OUTDIR [slug ...]

writes OUTDIR/<slug>.html and OUTDIR/<slug>.toc.json, the contents entries with the text that
starts each one's first page. When OUTDIR/<slug>.pages.json holds their page numbers (found by
`render finish` in a first pass), the contents page shows them."""
import re, sys, json, html, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from clean import Node, reading_content, serialize, page_title
from bookmeta import books, entry

WS = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); ONLY = set(sys.argv[3:])
OUT.mkdir(parents=True, exist_ok=True)

PRINT_CSS = """
/* ===== print edition: A4, light, one column ===== */
:root, :root[data-theme] { --paper: #FFFFFF; }
html, body { background: #FFFFFF !important; }
body { font-size: 10.4pt; line-height: 1.5; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.book { max-width: none; margin: 0; padding: 0; }
.prose > * { max-width: none; }
.masthead { padding-top: 120pt; border-bottom-width: 1.5pt; break-after: page; }
.masthead h1 { font-size: 40pt; }
.standfirst { font-size: 13pt; max-width: none; }
.masthead-meta .v { font-size: 15pt; }
.part { margin: 0; padding-top: 200pt; border-top: none; border-bottom: none; break-before: page; break-after: page; }
.part h2 { font-size: 30pt; }
.part p { font-size: 11.5pt; max-width: none; }
.chapter, .book > section.prose, .book > section[id], .milestone, .book > footer { break-before: page; }
.part + .chapter, .milestone + .stage { break-before: auto; }
.chapter { margin-top: 0; }
.ch-head { margin-bottom: 18pt; }
.chapter h3 { font-size: 22pt; }
.thesis, .standfirst { font-size: 11.6pt; }
.chapter h4 { font-size: 13pt; margin: 20pt 0 6pt; }
h2.sec { margin-top: 0; }
h2, h3, h4, h5, .ex-head, figcaption .tag, .block-h { break-after: avoid; }
p, li { orphans: 3; widows: 3; }
pre { font-size: 7.4pt; line-height: 1.42; white-space: pre-wrap; overflow: visible; }
pre .ln { display: block; }
pre code { white-space: pre-wrap !important; word-break: break-word; }
p code, li code, td code { font-size: .86em; }
figure.diagram, .keyidea, tr, .ch-end > div, .exercise > p, .ex-head { break-inside: avoid; }
figure.diagram svg { max-height: 330pt; }
.keyidea p, .exercise > p, .solution p { font-size: 10.4pt; }
.traps li { font-size: 9.8pt; }
.table-wrap { overflow: visible; }
table { min-width: 0; font-size: 9pt; }
a { color: inherit; text-decoration: none; }
.book-solution > .book-solution-label { font-family: "IBM Plex Mono", monospace; font-size: 7.5pt; font-weight: 600;
  letter-spacing: .1em; text-transform: uppercase; color: var(--ok); margin: 0 0 6pt; }
.exercise { padding: 10pt 12pt; }
.colophon { font-size: 8.5pt; max-width: none; }
.stage { margin-top: 0; break-before: page; }
.stage-grid { grid-template-columns: minmax(0, 1fr); gap: 14pt; }
.diagram svg { max-width: 100%; }
.book-toc { break-before: page; break-after: page; font-family: Archivo, "Helvetica Neue", Arial, sans-serif; }
.book-toc h2 { font-size: 20pt; margin: 0 0 18pt; }
.book-toc ol { list-style: none; margin: 0; padding: 0; }
.book-toc li { display: flex; align-items: baseline; gap: 6pt; font-size: 10.5pt; padding: 3.2pt 0; }
.book-toc li.toc-part { font-weight: 700; margin-top: 9pt; }
.book-toc li.toc-chapter { padding-left: 14pt; }
.book-toc li .dots { flex: 1; border-bottom: 1px dotted var(--rule); transform: translateY(-3pt); }
.book-toc li .pg { font-family: "IBM Plex Mono", monospace; font-size: 9.5pt; min-width: 20pt; text-align: right; }
"""

TEMPLATE = """<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
{head}
<style>{css}</style>
</head>
<body>
<div class="book">
{body}
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
<script>
// highlightAll() would wait for the load event and then redo the blocks this script splits into
// lines, so highlight each block now, before splitting.
document.querySelectorAll("pre code").forEach(function (c) {{ try {{ hljs.highlightElement(c); }} catch (e) {{}} }});
// A long line wraps with a hanging indent, four characters past its own indentation, so a
// continuation never looks like a statement of its own. Highlight spans can run across lines,
// so each line reopens the spans still open from the line before.
document.querySelectorAll("pre").forEach(function (pre) {{
  var box = pre.querySelector("code") || pre, stack = [];
  box.innerHTML = box.innerHTML.replace(/\\n$/, "").split("\\n").map(function (line) {{
    var open = stack.join("");
    line.replace(/<([/]?)span([^>]*)>/g, function (m, close, attrs) {{ if (close) stack.pop(); else stack.push("<span" + attrs + ">"); return m; }});
    var text = line.replace(/<[^>]+>/g, ""), n = text.match(/^ */)[0].length + 4;
    return '<span class="ln" style="padding-left:' + n + 'ch;text-indent:-' + n + 'ch">' + open + (text ? line : " ") +
      new Array(stack.length + 1).join("</span>") + "</span>";
  }}).join("");
}});
</script>
</body>
</html>
"""

for b in books(WS):
    if ONLY and b["slug"] not in ONLY: continue
    page = (WS / (b["src"] + ".html")).read_text(encoding="utf-8")
    k = page.index('<div class="shell">')
    head = re.sub(r"<script\b.*?</script>", "", page[:k], flags=re.S)
    _, main = reading_content(page)
    tops = [n for n in main.kids if isinstance(n, Node)]
    toc = []
    for n in tops:
        e = entry(n)
        if not e or n.tag == "header": continue
        label, kind, _ = e
        # what the entry's first page starts with: the full label where the page prints it whole
        whole = kind in ("part", "chapter") or n.has("milestone")
        toc.append({"label": label, "kind": kind, "find": label.replace(" · ", " ") if whole else label.split(" · ", 1)[-1]})
    pages_file = OUT / (b["slug"] + ".pages.json")
    pages = json.loads(pages_file.read_text()) if pages_file.exists() else []
    rows = "".join(f'<li class="toc-{t["kind"]}"><span>{html.escape(t["label"])}</span><span class="dots"></span>'
                   f'<span class="pg">{pages[i] if i < len(pages) else "000"}</span></li>' for i, t in enumerate(toc))
    contents = f'<section class="book-toc"><h2>Contents</h2><ol>{rows}</ol></section>'
    body = [serialize(n) for n in tops]
    body.insert(1, contents)
    (OUT / (b["slug"] + ".html")).write_text(TEMPLATE.format(head=head, css=PRINT_CSS, body="\n".join(body)), encoding="utf-8")
    (OUT / (b["slug"] + ".toc.json")).write_text(json.dumps({"title": page_title(page), "entries": toc}, ensure_ascii=False, indent=1))
    print(b["slug"], page_title(page), len(toc), "entries", "with page numbers" if pages else "")
