"""Arguing a trade-off both ways: three years of running our own event streaming cluster against a
managed service, with the uncertain inputs as ranges instead of single guesses. The question isn't
only which is cheaper, but which assumption decides it."""
import random
import statistics

ENGINEER_MONTH = 16_000            # loaded cost of one engineer for a month
rng = random.Random(42)


def sample():
    """One possible future: every uncertain input drawn from its range."""
    return {
        "growth": rng.uniform(1.0, 3.0),            # traffic multiplier per year
        "ops_fte": rng.uniform(0.15, 0.6),          # share of an engineer spent running it ourselves
        "incidents": rng.uniform(1, 6),             # serious incidents a year if we run it
        "incident_cost": rng.lognormvariate(9.9, 0.6),   # median about $20,000 each
    }


def three_years(f):
    traffic = [f["growth"] ** (m / 12) for m in range(36)]            # 1.0 = today's traffic
    own = (2 * ENGINEER_MONTH                                           # setting it up
           + sum(1_800 + 900 * t for t in traffic)                      # machines and storage
           + 36 * f["ops_fte"] * ENGINEER_MONTH                         # running it
           + 3 * f["incidents"] * f["incident_cost"])
    managed = (0.5 * ENGINEER_MONTH                                     # migrating to it
               + sum(2_600 + 2_400 * t for t in traffic)                # priced by throughput
               + 36 * 0.05 * ENGINEER_MONTH                             # a little of someone's time
               + 3 * 1 * f["incident_cost"])                            # the provider's outages hit us too
    return own, managed


futures = [sample() for _ in range(20_000)]
costs = [three_years(f) for f in futures]
pct = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))]
for i, name in enumerate(("run our own", "managed")):
    xs = [c[i] for c in costs]
    k = lambda p: f"${pct(xs, p) / 1e3:,.0f}k"
    print(f"{name:12} 3-year cost: median {k(.5)}  (80% between {k(.1)} "
          f"and {k(.9)})")
managed_wins = [c[1] < c[0] for c in costs]
print(f"managed is cheaper in {sum(managed_wins) / len(costs):.0%} of 20,000 simulated futures")

# Which assumption decides it? Split the futures on each input, and see how far the answer swings.
print("\nhow much each assumption moves the answer (share of futures where managed is cheaper):")
swings = []
for key in futures[0]:
    cut = statistics.median(f[key] for f in futures)
    low = [w for f, w in zip(futures, managed_wins) if f[key] <= cut]
    high = [w for f, w in zip(futures, managed_wins) if f[key] > cut]
    lo, hi = sum(low) / len(low), sum(high) / len(high)
    swings.append((abs(hi - lo), key, lo, hi))
for swing, key, lo, hi in sorted(swings, reverse=True):
    print(f"  {key:14} low half {lo:4.0%}  high half {hi:4.0%}   swing {swing * 100:3.0f} points")

# The two that matter most, as a table: what would have to be true for running our own to win?
print("\nwhich is cheaper, by traffic growth and time spent running it (other inputs at their medians):")
print(f"  {'':19}" + "".join(f"{f'{x} FTE':>10}" for x in (0.2, 0.3, 0.4, 0.5)))
for growth in (1.0, 1.5, 2.0, 2.5, 3.0):
    row = []
    for fte in (0.2, 0.3, 0.4, 0.5):
        future = {"growth": growth, "ops_fte": fte, "incidents": 3.5, "incident_cost": 20_000}
        own, managed = three_years(future)
        row.append("managed" if managed < own else "own")
    print(f"  {f'traffic x{growth:.1f}/year':19}" + "".join(f"{r:>10}" for r in row))
