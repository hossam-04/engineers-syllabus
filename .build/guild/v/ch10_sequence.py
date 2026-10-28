"""Sequencing a project: the same work in three orders. Some tasks hide an unknown that, if it
turns out badly, forces a change of plan and throws away part of the work already done."""
import math
import random

# task: (days of work, chance its unknown turns out badly)
TASKS = {
    "data model":           (5, 0.05),
    "admin screens":        (8, 0.02),
    "reporting":            (6, 0.05),
    "email templates":      (3, 0.02),
    "bank API integration": (7, 0.35),    # does the bank's API support refunds at all?
    "fraud rules":          (6, 0.20),    # will the risk team accept rules instead of a model?
    "migration of old data": (5, 0.15),
    "load and failover test": (4, 0.10),
}
REWORK = 0.5          # share of the work already done that a change of plan throws away

NEEDS = {"migration of old data": ["data model"], "reporting": ["data model"],
         "load and failover test": [t for t in TASKS if t != "load and failover test"]}


def riskiest_first():
    """Of the tasks whose prerequisites are done, always take the most risk per day of work."""
    order = []
    while len(order) < len(TASKS):
        ready = [t for t in TASKS if t not in order and all(d in order for d in NEEDS.get(t, []))]
        order.append(max(ready, key=lambda t: (TASKS[t][1] / TASKS[t][0], t)))
    return order


ORDERS = {
    "comfortable first": ["data model", "email templates", "admin screens", "reporting",
                          "migration of old data", "fraud rules", "bank API integration",
                          "load and failover test"],
    "riskiest first": riskiest_first(),
}


def run(order, rng, spike=False):
    """Days wasted, and the day the first bad surprise surfaced (None if there was none)."""
    day, wasted, first = 0, 0.0, None
    if spike:                                     # two days of prototypes against the two riskiest unknowns
        day += 2
        for t in ("bank API integration", "fraud rules"):
            if rng.random() < TASKS[t][1]:
                first = first or day              # found before anything is built on it: nothing to redo
    for t in order:
        days, p = TASKS[t]
        day += days
        if not spike or t not in ("bank API integration", "fraud rules"):
            if rng.random() < p:
                first = first or day
                wasted += REWORK * (day - days)   # the plan changes; half the earlier work is redone
    return wasted, first


rng = random.Random(10)
print(f"{sum(d for d, _ in TASKS.values())} days of work; chance at least one unknown turns out badly: "
      f"{1 - math.prod(1 - p for _, p in TASKS.values()):.0%}\n")
print(f"{'order':40}{'days wasted':>12}{'first surprise':>16}")
plans = [(name, order, False) for name, order in ORDERS.items()]
plans.append(("riskiest first, after a 2-day spike", ORDERS["riskiest first"], True))
for name, order, spike in plans:
    results = [run(order, rng, spike) for _ in range(20_000)]
    wasted = sum(w for w, _ in results) / len(results)
    firsts = sorted(f for _, f in results if f is not None)
    print(f"{name:40}{wasted:>12.1f}{'day ' + str(firsts[len(firsts) // 2]):>16}")
print("\n(days wasted: the average over 20,000 runs; first surprise: the median day it surfaced)")
print("riskiest-first order:", " -> ".join(ORDERS["riskiest first"]))
