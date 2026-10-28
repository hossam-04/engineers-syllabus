# Apply exact replacements inside diagram N of a volume; each old string must occur exactly once there.
# Usage (as a module): patch(path, n, [(old, new), ...])
import re, pathlib
def patch(path, n, pairs):
    p = pathlib.Path(path); doc = p.read_text(encoding="utf-8")
    spans = [m.span() for m in re.finditer(r'<svg\b.*?</svg>', doc, re.S)]
    a, b = spans[n - 1]; svg = doc[a:b]
    for old, new in pairs:
        c = svg.count(old)
        assert c == 1, f"{p.name} svg {n}: {c} matches for {old!r}"
        svg = svg.replace(old, new)
    p.write_text(doc[:a] + svg + doc[b:], encoding="utf-8")
def endpoint(x1, y1, x2, y2, new_x):
    """The point on the line through (x1,y1)-(x2,y2) at x = new_x, rounded."""
    return new_x, round(y1 + (y2 - y1) * (new_x - x1) / (x2 - x1), 1)
