"""Mentoring as planning: what someone knows, what they're ready to learn next, and where their
knowledge is fragile because it rests on something they don't yet have."""
from graphlib import TopologicalSorter

# concept: the concepts it builds on
NEEDS = {
    "files and fsync": [],
    "pages and the buffer pool": ["files and fsync"],
    "B-trees": ["pages and the buffer pool"],
    "indexes": ["B-trees"],
    "query plans": ["indexes", "statistics"],
    "statistics": [],
    "transactions": [],
    "write-ahead log": ["files and fsync", "transactions"],
    "crash recovery": ["write-ahead log", "pages and the buffer pool"],
    "MVCC": ["transactions", "pages and the buffer pool"],
    "isolation anomalies": ["MVCC"],
    "replication": ["write-ahead log"],
}

# What a mentee says they know, after a conversation: what they've used, not what they can explain.
KNOWS = {"transactions", "indexes", "query plans", "replication"}

order = list(TopologicalSorter(NEEDS).static_order())

def ancestors(concept):
    seen, todo = set(), list(NEEDS[concept])
    while todo:
        c = todo.pop()
        if c not in seen:
            seen.add(c)
            todo.extend(NEEDS[c])
    return seen

print("fragile: known, but resting on something not yet known")
for c in [c for c in order if c in KNOWS]:
    gaps = sorted(ancestors(c) - KNOWS, key=order.index)
    if gaps:
        print(f"  {c:16} rests on: {', '.join(gaps)}")

ready = [c for c in order if c not in KNOWS and all(d in KNOWS for d in NEEDS[c])]
print("\nready to learn now (everything it needs is known):", ", ".join(ready))

goal = "crash recovery"
path = [c for c in order if (c in ancestors(goal) or c == goal) and c not in KNOWS]
print(f"\nto reach {goal!r}, in an order that never needs what hasn't been taught:")
for step, c in enumerate(path, 1):
    print(f"  {step}. {c}")
print(f"\nshortcut check: of {len(path)} steps, the first is {path[0]!r}: "
      f"ask them to explain it before teaching anything that rests on it")
