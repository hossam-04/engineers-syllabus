import random
from dataclasses import dataclass

# A small model of memory, of the kind spaced-repetition programs are built on. Its constants are
# chosen to show the shape of the effect; the experiments described in the chapter are the evidence.
#   - Each fact has a stability S: the number of days until your chance of recalling it falls to 90%.
#     t days after you last saw it, the chance is 1 / (1 + t / (9 * S)). A new fact has S = 1.
#   - Recalling it makes S larger, by more the nearer you were to forgetting: S * (1 + 15 * (1 - chance)).
#     A review of something you can recall easily adds almost nothing.
#   - Failing to recall it sets S back to 1: you look up the answer and start again.
def chance(days, stability): return 1 / (1 + days / (9 * stability))

@dataclass
class Fact:
    S: float = 1.0
    seen: float = 0.0
    reviews: int = 0
    box: int = 1

    def review(self, day, rng):
        p = chance(day - self.seen, self.S)
        recalled = rng.random() < p
        self.S = self.S * (1 + 15 * (1 - p)) if recalled else 1.0
        self.seen, self.reviews = day, self.reviews + 1
        return recalled

def cram(fact, rng):                                  # four more passes through the cards, that evening
    for k in range(1, 5): fact.review(k / 48, rng)

def fixed(fact, rng):                                 # the same five days for every fact
    for day in (1, 3, 7, 14, 28): fact.review(day, rng)

def leitner(fact, rng):
    """Leitner boxes: a fact in box k comes back 2**(k-1) days later; recalling it moves it up a box,
    forgetting it sends it back to box 1. Hard facts are seen often, easy ones rarely."""
    day = 1
    while day <= 30:
        fact.box = min(fact.box + 1, 5) if fact.review(day, rng) else 1
        day += 2 ** (fact.box - 1)

def at_ninety(fact, rng):
    """What modern schedulers do: bring each fact back just as its predicted recall falls to 90%."""
    day = fact.seen + fact.S
    while day <= 30:
        fact.review(day, rng); day = fact.seen + fact.S

print("200 facts learned on day 0, then reviewed only during the first 30 days")
print(f"   {'plan':38}{'reviews per fact':>17}{'recall, day 60':>16}{'recall, day 90':>16}")
for label, plan in (("no review", None), ("cram: 4 more passes on day 0", cram),
                    ("fixed: days 1, 3, 7, 14 and 28", fixed), ("Leitner boxes", leitner),
                    ("each fact when recall reaches 90%", at_ninety)):
    rng = random.Random(16); facts = [Fact() for _ in range(200)]
    for f in facts:
        if plan: plan(f, rng)
    reviews = sum(f.reviews for f in facts) / len(facts)
    later = [sum(chance(day - f.seen, f.S) for f in facts) / len(facts) for day in (60, 90)]
    print(f"   {label:38}{reviews:>17.1f}{later[0]:>16.0%}{later[1]:>16.0%}")

print("one fact under the 90% rule: the gaps between reviews grow as it becomes stable")
f, rng = Fact(), random.Random(3); days = []
while f.seen + f.S <= 365:
    f.review(f.seen + f.S, rng); days.append(round(f.seen))
print("   reviewed on days " + ", ".join(map(str, days)) + f"; by then it would last {f.S:.0f} days")
