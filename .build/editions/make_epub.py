"""EPUB 3 editions of the syllabus and its sixteen volumes, built with the standard library only.

    python3 make_epub.py WS OUTDIR [slug ...]

Each book is split into one XHTML file per front section, chapter and appendix. Diagram styles are
written onto the SVG elements, with the light theme's colours, because many readers ignore CSS
variables and classes inside SVG."""
import re, sys, uuid, zipfile, pathlib, datetime, html
import xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from clean import Node, el, reading_content, serialize, page_title, page_css, light_tokens, resolve_vars, hang_code_lines
from bookmeta import books, entries

HERE = pathlib.Path(__file__).parent
WS = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); ONLY = set(sys.argv[3:])
OUT.mkdir(parents=True, exist_ok=True)


# ---------- diagram styles, resolved onto the elements ----------
def css_rules(css, tokens):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)
    rules = []
    for i, (sel, body) in enumerate(re.findall(r"([^{}]+)\{([^{}]*)\}", css)):
        for one in sel.split(","):
            one = one.strip()
            if "dg-" not in one or ":" in one: continue
            parts = one.split()
            comp = [(re.match(r"^[a-zA-Z]*", p).group(0), re.findall(r"\.([\w-]+)", p)) for p in parts]
            spec = (sum(len(c) for _, c in comp), sum(1 for t, _ in comp if t), i)
            rules.append((spec, comp, resolve_vars(body.strip().rstrip(";"), tokens)))
    return sorted(rules, key=lambda r: r[0])


def matches(n, comp):
    def ok(node, c):
        tag, classes = c
        return isinstance(node, Node) and (not tag or node.tag == tag) and all(node.has(x) for x in classes)
    if not ok(n, comp[-1]): return False
    p = n.parent
    for c in reversed(comp[:-1]):
        while p is not None and not ok(p, c): p = p.parent
        if p is None: return False
        p = p.parent
    return True


def bake_svg(svg, rules, tokens):
    for n in svg.walk():
        decl = [body for _, comp, body in rules if matches(n, comp)]
        for k, v in list(n.attrs.items()):
            if v and "var(" in v: n.attrs[k] = resolve_vars(v, tokens)
        if decl:
            own = n.attrs.get("style")
            n.attrs["style"] = "; ".join(decl + ([resolve_vars(own, tokens)] if own else []))
        if n.tag != "svg": n.attrs.pop("class", None)


# ---------- splitting into files ----------
def units(main):
    """Lists of top-level nodes, one per XHTML file. A part divider or milestone stays with
    what follows it; the colophon stays with the last section."""
    out, cur, glue = [], [], False
    for k in main.kids:
        if not isinstance(k, Node): continue
        starts = (k.attrs.get("id") or k.has("part") or k.has("milestone")) and k.tag != "footer"
        if starts and cur and not glue: out.append(cur); cur = []
        cur.append(k); glue = k.has("part") or k.has("milestone")
    if cur: out.append(cur)
    return out


XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><meta charset="utf-8"/><title>{title}</title><link rel="stylesheet" type="text/css" href="../style.css"/></head>
<body{bodycls}>
{body}
</body>
</html>
"""


def make_book(b):
    page = (WS / (b["src"] + ".html")).read_text(encoding="utf-8")
    title = page_title(page)
    css = page_css(page); tokens = light_tokens(css); rules = css_rules(css, tokens)
    _, main = reading_content(page)
    for svg in main.find(lambda n: n.tag == "svg"): bake_svg(svg, rules, tokens)
    hang_code_lines(main, unit="em", step=0.6)   # some readers lack the ch unit; monospace is about 0.6em wide
    groups = units(main)
    names = [f"p{i + 1:03d}.xhtml" for i in range(len(groups))]
    where = {}
    for name, g in zip(names, groups):
        for top in g:
            for n in top.walk():
                if n.attrs.get("id"): where[n.attrs["id"]] = name
    files, toc, has_svg = [], [], []
    for name, g in zip(names, groups):
        for top in g:
            for a in top.find(lambda n: n.tag == "a" and (n.attrs.get("href") or "").startswith("#")):
                target = a.attrs["href"][1:]
                if target in where: a.attrs["href"] = (where[target] if where[target] != name else "") + "#" + target
                else: a.attrs.pop("href")
            for a in top.find(lambda n: n.tag == "a" and (n.attrs.get("href") or "").startswith("http")):
                a.attrs.pop("target", None); a.attrs.pop("rel", None)
        body = "\n".join(serialize(t, xhtml=True) for t in g)
        here = entries(g, name)
        doc = XHTML.format(title=html.escape(here[0][0] if here else title), body=body,
                           bodycls=' class="title-page"' if g[0].tag == "header" else "")
        ET.fromstring(doc.split("\n", 2)[2])                # fail loudly on anything not well formed
        files.append((name, doc)); has_svg.append(" ".join(k for k, t in (("svg", "<svg"), ("mathml", "<math")) if t in body))
        toc.extend(here)
    write_epub(b, title, files, has_svg, toc)
    return title, len(files)


def nav_xhtml(title, toc):
    items, open_part = [], False
    for label, kind, href in toc:
        li = f'<li><a href="text/{href}">{html.escape(label)}</a>'
        if kind == "part":
            if open_part: items.append("</ol></li>")
            items.append(li + "<ol>"); open_part = True
        elif kind == "chapter" and open_part: items.append(li + "</li>")
        else:
            if open_part: items.append("</ol></li>"); open_part = False
            items.append(li + "</li>")
    if open_part: items.append("</ol></li>")
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">\n'
            f'<head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
            f'<body><nav epub:type="toc" id="toc"><h1>Contents</h1><ol>{"".join(items)}</ol></nav>\n'
            f'<nav epub:type="landmarks" hidden="hidden"><ol><li><a epub:type="bodymatter" href="text/{toc[min(1, len(toc) - 1)][2]}">Start</a></li>'
            f'<li><a epub:type="toc" href="nav.xhtml">Contents</a></li></ol></nav></body></html>\n')


def ncx(title, uid, toc):
    pts = "".join(f'<navPoint id="n{i}" playOrder="{i}"><navLabel><text>{html.escape(l)}</text></navLabel><content src="text/{n}"/></navPoint>'
                  for i, (l, _, n) in enumerate(toc, 1))
    return ('<?xml version="1.0" encoding="utf-8"?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
            f'<head><meta name="dtb:uid" content="{uid}"/></head><docTitle><text>{html.escape(title)}</text></docTitle>'
            f'<navMap>{pts}</navMap></ncx>\n')


def write_epub(b, title, files, has_svg, toc):
    uid = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "engineers-syllabus/" + b["slug"]))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cover = OUT.parent / "covers" / (b["slug"] + ".png")
    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
                '<item id="css" href="style.css" media-type="text/css"/>']
    spine = []
    if cover.exists():
        manifest.append('<item id="cover-img" href="cover.png" media-type="image/png" properties="cover-image"/>')
        manifest.append('<item id="cover" href="text/cover.xhtml" media-type="application/xhtml+xml"/>')
        spine.append('<itemref idref="cover" linear="yes"/>')
    for (name, _), svg in zip(files, has_svg):
        i = name[:-6]
        manifest.append(f'<item id="{i}" href="text/{name}" media-type="application/xhtml+xml"{f' properties="{svg}"' if svg else ""}/>')
        spine.append(f'<itemref idref="{i}"/>')
    desc = f"Companion volume to stage {b['stage']} of The Engineer's Syllabus." if b["stage"] else "A self-directed curriculum in sixteen stages."
    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="en">\n'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
           f'<dc:identifier id="uid">{uid}</dc:identifier><dc:title>{html.escape(title)}</dc:title>'
           '<dc:creator>The Engineer\'s Syllabus</dc:creator><dc:language>en</dc:language>'
           f'<dc:description>{html.escape(desc)}</dc:description><dc:date>2026-10-23</dc:date>'
           f'<meta property="dcterms:modified">{now}</meta>'
           + ('<meta name="cover" content="cover-img"/>' if cover.exists() else "") +
           f'</metadata>\n<manifest>{"".join(manifest)}</manifest>\n<spine toc="ncx">{"".join(spine)}</spine>\n</package>\n')
    path = OUT / (title.replace("The Engineer's ", "").replace(" ", "-") + ".epub")
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zi = lambda n, d: z.writestr(n, d, compress_type=zipfile.ZIP_DEFLATED)
        zi("META-INF/container.xml", '<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
           '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>\n')
        zi("OEBPS/content.opf", opf)
        zi("OEBPS/nav.xhtml", nav_xhtml(title, toc))
        zi("OEBPS/toc.ncx", ncx(title, uid, toc))
        zi("OEBPS/style.css", (HERE / "book.css").read_text())
        if cover.exists():
            z.write(cover, "OEBPS/cover.png", compress_type=zipfile.ZIP_STORED)
            zi("OEBPS/text/cover.xhtml", XHTML.format(title="Cover", bodycls=' class="cover"',
               body=f'<div class="cover-img"><img src="../cover.png" alt="{html.escape(title)}"/></div>'))
        for name, doc in files: zi("OEBPS/text/" + name, doc)
    return path


for b in books(WS):
    if ONLY and b["slug"] not in ONLY: continue
    t, n = make_book(b)
    print(f"{t:36} {n:3} files")
