"""A prose checker for writing in public: the mechanical habits that make technical writing hard to
read, measured on the opening of a blog post before and after editing."""
import re
import statistics

BEFORE = """In this post I want to talk a little bit about something that I think is quite important,
which is the way that database migrations are handled by many teams. It is important to note that
mistakes were made by us in the past, and it could perhaps be argued that some of them were really
avoidable. Basically, the migration was run during the day and the table was locked by it for
eleven minutes, which was obviously not ideal for our users."""

AFTER = """A migration locked our orders table for eleven minutes on a Tuesday afternoon. Nobody could
check out. The fix took one line, and the lesson took longer: on a large table, adding a column with
a default rewrote every row while holding the lock. Here is what we changed, and the three rules we
now follow for every migration."""

HEDGES = (r"\b(i think|perhaps|maybe|might|could|somewhat|quite|very|really|just|basically"
          r"|obviously|a little bit)\b")
OPENERS = r"\b(in this post|it is important to note|i want to talk|needless to say|at the end of the day)\b"
PASSIVE = r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?(\w+ed|made|run|done|held|taken|written)\b"


def syllables(word):
    groups = re.findall(r"[aeiouy]+", word.lower())
    n = len(groups) - (word.lower().endswith("e") and len(groups) > 1)
    return max(1, n)


def check(text):
    text = " ".join(text.split())
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s]
    words = re.findall(r"[A-Za-z']+", text)
    lengths = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences]
    flesch = 206.835 - 1.015 * len(words) / len(sentences) - 84.6 * sum(map(syllables, words)) / len(words)
    return {
        "sentences": len(sentences),
        "words per sentence": round(statistics.mean(lengths), 1),
        "longest sentence": max(lengths),
        "reading ease": round(flesch),
        "hedges": [m.group(0) for m in re.finditer(HEDGES, text, re.I)],
        "throat-clearing": [m.group(0) for m in re.finditer(OPENERS, text, re.I)],
        "passive": [m.group(0) for m in re.finditer(PASSIVE, text, re.I)],
        "first sentence": sentences[0],
    }


before, after = check(BEFORE), check(AFTER)
print(f"{'':22}{'before':>10}{'after':>10}")
for key in ("sentences", "words per sentence", "longest sentence", "reading ease"):
    print(f"{key:22}{before[key]:>10}{after[key]:>10}")
for key in ("hedges", "throat-clearing", "passive"):
    print(f"{key:22}{len(before[key]):>10}{len(after[key]):>10}")
print("\nflagged in the first draft:")
for key in ("throat-clearing", "hedges", "passive"):
    print(f"  {key}: " + "; ".join(before[key]))
print("\nwhat each version's first sentence promises the reader:")
print("  before:", before["first sentence"][:88] + " ...")
print("  after: ", after["first sentence"])
