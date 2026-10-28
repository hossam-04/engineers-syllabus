# Print the elements of diagram N in a volume, one per line, optionally only those matching a pattern.
# Usage: svgsrc.py VOLUME.html N [regex]
import re, sys
doc = open(sys.argv[1], encoding="utf-8").read()
svg = re.findall(r'<svg\b.*?</svg>', doc, re.S)[int(sys.argv[2]) - 1]
pat = re.compile(sys.argv[3]) if len(sys.argv) > 3 else None
for el in re.findall(r'<(?:text|line|rect|path|circle|polyline|polygon)\b[^>]*>(?:[^<]*</text>)?', svg):
    if not pat or pat.search(el): print(el)
