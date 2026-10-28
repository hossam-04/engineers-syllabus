"""A first-pass reviewer for design documents: the questions a sceptical senior engineer asks
before arguing with the substance. It doesn't judge the design; it finds what's missing."""
import re
import textwrap

WEAK = """# Search improvements

## Background
Search is slow and users don't like it. We should make it much faster and more scalable.

## Proposal
We will move search to Elasticsearch, which is robust and should be easy to run.
This will significantly improve the experience and make search seamless.
"""

STRONG = """# Move product search to a dedicated index

We propose moving product search from Postgres full-text queries to a dedicated OpenSearch
index, fed from the existing change stream. Prototypes bring p95 latency from 2.4 s to 240 ms.

## Context
Search p95 is 2.4 s at today's 40 queries a second, and support logs about ten complaints a week.
The slow queries are prefix and typo-tolerant matches, which Postgres serves with sequential scans.

## Goals
- p95 search latency under 300 ms at 120 queries a second, three times today's peak.
- New and changed products searchable within 60 s of the write.

## Non-goals
- Personalised ranking. It is a separate project, and nothing here prevents it.
- Replacing Postgres as the source of truth for products.

## Proposal
A consumer reads product changes from the existing change stream and writes them to the index.
Search requests go to the index; product pages still read from Postgres.

## Alternatives considered
- Tune Postgres with trigram indexes: p95 fell to 900 ms in a test, short of the goal.
- A managed search service: meets the goal, but at $4,100 a month against $900 for self-hosting.
- Do nothing: complaints are growing about 8% a month with traffic.

## Risks
- The index falls behind the database. Mitigation: alert when lag exceeds 60 s; fall back to Postgres.
- Cost grows with the catalogue. Mitigation: a 30-day review of node sizes after launch.

## Rollout
Shadow traffic for a week and compare results, then 5%, 50% and 100% behind a flag,
with the flag as the rollback.

## Open questions
- Who owns the index on call: the search team or the platform team?
"""

REQUIRED = ["context", "goals", "non-goals", "proposal", "alternatives", "risks", "rollout"]
VAGUE = (r"\b(fast(er)?|slow|scalable|robust|easy|simple|significant(ly)?|seamless(ly)?"
         r"|better|improve[sd]?)\b")


def sections(doc):
    parts, current = {"_lead": []}, "_lead"
    for line in doc.splitlines():
        if line.startswith("## "):
            current = line[3:].strip().lower().split()[0]
            parts[current] = []
        elif not line.startswith("# "):
            parts[current].append(line)
    return {k: "\n".join(v).strip() for k, v in parts.items()}


def review(doc):
    s, notes = sections(doc), []
    missing = [r for r in REQUIRED if r not in s]
    if missing:
        notes.append("missing sections: " + ", ".join(missing))
    lead = s["_lead"] or s.get("background", "")
    if not re.search(r"\b(we propose|we recommend|this document proposes)\b", lead, re.I):
        notes.append("the first paragraph doesn't say what is being proposed")
    for goal in re.findall(r"^- (.*)$", s.get("goals", ""), re.M):
        if not re.search(r"\d", goal):
            notes.append(f"goal without a number: {goal!r}")
    prose = " ".join(line for line in doc.splitlines() if not line.startswith("#"))
    for sentence in re.split(r"(?<=[.!?])\s+", prose):
        words = dict.fromkeys(m.group(0).lower() for m in re.finditer(VAGUE, sentence, re.I))
        if words and not re.search(r"\d", sentence):
            quote = textwrap.shorten(sentence.strip(), 64, placeholder=" ...")
            notes.append(f"{', '.join(words)} with no number beside it: {quote!r}")
    alternatives = re.findall(r"^- ", s.get("alternatives", ""), re.M)
    if len(alternatives) < 2:
        notes.append(f"{len(alternatives)} alternatives considered; reviewers will ask about at least two, "
                     "and about doing nothing")
    for risk in re.findall(r"^- (.*)$", s.get("risks", ""), re.M):
        if "mitigation" not in risk.lower():
            notes.append(f"risk without a mitigation: {risk!r}")
    if "rollout" in s and not re.search(r"rollback|roll back|revert|flag", s["rollout"], re.I):
        notes.append("the rollout has no way back")
    if "open" not in s:
        notes.append("no open questions: either nothing is unsettled, or it isn't written down")
    return notes


for name, doc in [("weak draft", WEAK), ("revised draft", STRONG)]:
    notes = review(doc)
    print(f"{name}: {len(doc.split())} words, {len(notes)} review note{'s' * (len(notes) != 1)}")
    for n in notes:
        print("  - " + n)
    print()
