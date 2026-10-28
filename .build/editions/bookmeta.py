"""What both editions need to know about the books: which pages they're made from, in what
order, and the contents entry for each top-level section."""
import re, pathlib
from clean import Node


def books(WS):
    WS = pathlib.Path(WS)
    src = (WS / ".build/site-builder/build_site.py").read_text()
    vols = eval(re.search(r"^VOLS = (\[.*?^\])", src, re.S | re.M).group(1), {"dict": dict})
    yield dict(slug="syllabus", src="software-engineering-study-plan", name="Syllabus", stage="", subject="")
    yield from vols



def entry(n):
    """(label, kind, id) for one top-level node, or None when it gets no contents entry."""
    if n.tag == "header": return "Title page", "top", None
    if n.has("part"):
        num = n.first(lambda x: x.has("part-num")); h = n.first(lambda x: x.tag == "h2")
        return f"{num.text().strip()} · {h.text().strip()}", "part", n.attrs.get("id")
    if n.has("milestone"):
        m = n.first(lambda x: x.has("m-name")); k = m.first(lambda x: x.tag == "span")
        rest = m.text().strip()[len(k.text().strip()):].strip()
        return f"{k.text().strip()} · {rest}", "top", None
    if n.has("chapter"):
        num = n.first(lambda x: x.has("ch-num")); h = n.first(lambda x: x.tag == "h3")
        return f"{num.text().strip()} · {h.text().strip()}", "chapter", n.attrs.get("id")
    if n.has("stage"):
        num = n.first(lambda x: x.has("stage-num")); h = n.first(lambda x: x.tag == "h3")
        return f"{num.text().strip().title()} · {h.text().strip()}", "top", n.attrs.get("id")
    if n.tag == "footer": return None
    h = n.first(lambda x: x.tag in ("h2", "h3"))
    return (h.text().strip() if h else n.attrs.get("id", "Section")), "top", n.attrs.get("id")


def entries(nodes, name):
    out = []
    for i, n in enumerate(nodes):
        e = entry(n)
        if e: out.append((e[0], e[1], name + ("#" + e[2] if e[2] and i else "")))
    return out
