"""Shared by the EPUB and PDF editions: read a volume page, drop everything interactive, and
keep the reading content as a small tree that can be written back as HTML or as XHTML."""
import re, html
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
RAW = {"script", "style"}
# html.parser lowercases names; SVG needs its camelCase back.
SVG_TAGS = {t.lower(): t for t in ("clipPath", "linearGradient", "radialGradient", "textPath", "foreignObject")}
SVG_ATTRS = {a.lower(): a for a in ("viewBox", "preserveAspectRatio", "refX", "refY", "markerWidth", "markerHeight",
                                    "markerUnits", "patternUnits", "gradientUnits", "gradientTransform", "textLength",
                                    "lengthAdjust", "startOffset", "stdDeviation", "spreadMethod", "patternTransform")}


class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.kids, self.parent = tag, dict(attrs or {}), [], parent

    def cls(self): return (self.attrs.get("class") or "").split()
    def has(self, c): return c in self.cls()

    def walk(self):
        yield self
        for k in self.kids:
            if isinstance(k, Node): yield from k.walk()

    def find(self, pred): return [n for n in self.walk() if pred(n)]
    def first(self, pred): return next((n for n in self.walk() if pred(n)), None)

    def remove(self):
        self.parent.kids.remove(self)

    def text(self):
        return "".join(k if isinstance(k, str) else k.text() for k in self.kids)


class Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root"); self.cur = self.root; self.svg = 0

    def _open(self, tag, attrs):
        if tag == "svg": self.svg += 1
        if self.svg:
            tag = SVG_TAGS.get(tag, tag)
            attrs = [(SVG_ATTRS.get(k, k), v) for k, v in attrs]
        n = Node(tag, attrs, self.cur); self.cur.kids.append(n)
        return n

    def handle_starttag(self, tag, attrs):
        n = self._open(tag, attrs)
        if tag not in VOID: self.cur = n

    def handle_startendtag(self, tag, attrs):
        self._open(tag, attrs)
        if tag == "svg": self.svg -= 1

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag.lower() != tag: n = n.parent
        if n is self.root: return                       # stray end tag
        if tag == "svg": self.svg -= 1
        self.cur = n.parent

    def handle_data(self, d):
        if d: self.cur.kids.append(d)


def parse(s):
    b = Builder(); b.feed(s); b.close(); return b.root


def serialize(n, xhtml=False):
    if isinstance(n, str): return html.escape(n, quote=False)
    if n.tag == "#root": return "".join(serialize(k, xhtml) for k in n.kids)
    if xhtml and n.tag == "math" and "xmlns" not in n.attrs:        # XHTML needs MathML's namespace spelled out
        n.attrs = {"xmlns": "http://www.w3.org/1998/Math/MathML", **n.attrs}
    a = "".join(f' {k}="{html.escape(k if v is None else v, quote=True)}"' if (xhtml or v is not None) else f" {k}"
                for k, v in n.attrs.items())
    if n.tag in RAW:
        return f"<{n.tag}{a}>" + "".join(k for k in n.kids if isinstance(k, str)) + f"</{n.tag}>"
    if n.tag in VOID: return f"<{n.tag}{a}/>" if xhtml else f"<{n.tag}{a}>"
    inner = "".join(serialize(k, xhtml) for k in n.kids)
    if xhtml and not inner and in_svg(n): return f"<{n.tag}{a}/>"
    return f"<{n.tag}{a}>{inner}</{n.tag}>"


def in_svg(n):
    while n is not None:
        if n.tag == "svg": return True
        n = n.parent
    return False


def el(tag, attrs=None, kids=()):
    n = Node(tag, attrs)
    for k in kids:
        if isinstance(k, Node): k.parent = n
        n.kids.append(k)
    return n


SCREEN_ONLY = re.compile(r"\s*(?:Your (?:chapter|stage) marks are stored in this browser only\. Nothing is sent anywhere\."
                         r"|Tick a chapter as read in its heading and the contents will track your progress\."
                         r"|The marks are kept in this browser only\.)")


def reading_content(page):
    """The page's <main>, without the bits that only make sense on screen."""
    root = parse(page)
    main = root.first(lambda n: n.tag == "main")
    assert main is not None
    drop = lambda n: (n.tag in ("script", "style", "button", "input", "nav")
                      or (n.tag == "label" and n.has("done-toggle"))
                      or n.has("rail") or n.has("resume-bar"))
    for n in main.find(drop):
        if n.parent is not None and n in n.parent.kids: n.remove()
    # Solutions are folded on screen; in a book they're printed, under a plain label.
    for d in main.find(lambda n: n.tag == "details"):
        summ = d.first(lambda n: n.tag == "summary")
        label = summ.text().strip() if summ else "Solution"
        if summ: summ.remove()
        label = "Solution" if label.lower().startswith("show") else label
        d.tag = "div"; d.attrs = {"class": " ".join(c for c in d.cls() + ["book-solution"]) }
        p = el("p", {"class": "book-solution-label"}, [label]); p.parent = d
        d.kids.insert(0, p)
    # Sentences about the on-screen Read marks don't apply to a book.
    for p in main.find(lambda n: n.tag == "p"):
        p.kids = [SCREEN_ONLY.sub("", k) if isinstance(k, str) else k for k in p.kids]
        if not any(isinstance(k, Node) for k in p.kids) and not "".join(p.kids).strip(): p.remove()
    # "{N} min read" makes no sense on paper.
    for m in main.find(lambda n: n.has("ch-meta")):
        for s in [k for k in m.kids if isinstance(k, Node) and "min read" in k.text()]: m.kids.remove(s)
    return root, main


def hang_code_lines(main, unit="ch", step=1.0):
    """Give every line of a plain code block its own block with a hanging indent, so a line the
    reader wraps continues four characters past its own indentation."""
    for pre in main.find(lambda n: n.tag == "pre"):
        box = pre.first(lambda n: n.tag == "code") or pre
        if any(isinstance(k, Node) for k in box.kids): continue          # marked-up code stays as it is
        lines = "".join(box.kids).rstrip("\n").split("\n")
        box.kids = []
        for line in lines:
            n = len(line) - len(line.lstrip(" ")) + 4
            w = f"{n * step:g}{unit}"
            span = el("span", {"class": "ln", "style": f"display: block; padding-left: {w}; text-indent: -{w}"}, [line or " "])
            span.parent = box; box.kids.append(span)


def page_title(page):
    m = re.search(r"<title>(.*?)</title>", page, re.S)
    return html.unescape(m.group(1).strip()) if m else ""


def page_css(page):
    return "\n".join(re.findall(r"<style>(.*?)</style>", page, re.S))


def light_tokens(css):
    m = re.search(r":root\s*\{(.*?)\}", css, re.S)
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1))) if m else {}


def resolve_vars(text, tokens):
    for _ in range(4):                                     # tokens may refer to tokens
        text = re.sub(r"var\((--[\w-]+)(?:\s*,\s*([^)]+))?\)",
                      lambda m: tokens.get(m.group(1), m.group(2) or "currentColor").strip(), text)
    return text
