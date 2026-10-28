"""A career that compounds starts with remembering what you did. A plain-text work log, kept a few
lines a week, turned into the summary a review, a promotion case or a CV needs."""
import re
from collections import defaultdict

LOG = """
2026-W02  Wrote the design doc for moving search to a dedicated index #design
2026-W02  Reviewed 14 pull requests, mostly for the new hire #mentoring
2026-W03  Led the search migration kickoff with platform and support #leadership
2026-W04  Fixed the nightly export that silently dropped rows #reliability impact: 3,200 rows a night
2026-W06  Search index live for 5% of traffic #design impact: p95 2.4 s -> 240 ms
2026-W07  Paired with Priya on her first on-call shift #mentoring
2026-W07  Wrote the postmortem for the 40-minute checkout outage #reliability
2026-W08  Search at 100% #design impact: support complaints 10 a week -> 1
2026-W09  Gave the internal talk on reading query plans #writing #mentoring
2026-W11  Published "What our search migration taught us" on our blog #writing impact: 4,100 readers
2026-W12  Added lag alerting to the change stream #reliability impact: caught 2 incidents before users did
2026-W13  Priya led her first incident review on her own #mentoring
"""

entries = []
for line in LOG.strip().splitlines():
    week, text = line.split(None, 1)
    impact = re.search(r"impact:\s*(.*)$", text)
    themes = re.findall(r"#(\w+)", text)
    what = re.sub(r"\s*(#\w+|impact:.*)", "", text).strip()
    entries.append((week, what, themes, impact.group(1) if impact else None))

def entries_word(n):
    return f"{n:2} entr{'ies' if n != 1 else 'y'}"


by_theme = defaultdict(list)
for e in entries:
    for t in e[2]:
        by_theme[t].append(e)
print("themes, by how often they appear:")
for theme, es in sorted(by_theme.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    measured = sum(1 for e in es if e[3])
    print(f"  {theme:11} {entries_word(len(es))}, {measured} with a measured result")

weeks = sorted({int(w[-2:]) for w, *_ in entries})
gaps = [f"W{w:02}" for w in range(weeks[0], weeks[-1] + 1) if w not in weeks]
print(f"\nweeks with nothing written down: {', '.join(gaps)} "
      f"({len(gaps)} of {weeks[-1] - weeks[0] + 1}; those are the ones you won't remember)")

print("\nthe paragraph for a review, written from the log, one sentence per theme:")
measured_first = lambda kv: (-sum(1 for e in kv[1] if e[3]), -len(kv[1]), kv[0])
for theme, es in sorted(by_theme.items(), key=measured_first):
    best = next((e for e in reversed(es) if e[3]), es[-1])
    result = f" ({best[3]})" if best[3] else ""
    print(f"  {theme.capitalize()}: {best[1]}{result}; {entries_word(len(es))} in all.")
