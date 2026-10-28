"""Spanner's commit wait, from the paper's rules: why waiting out the clock uncertainty makes
timestamps agree with real time, and what it costs."""
import random

EPS = 0.007          # TrueTime's uncertainty: every clock is within 7 ms of true time


class Node:
    def __init__(self, offset):
        self.offset = offset                       # how far this node's clock is from true time
    def clock(self, t):
        return t + self.offset
    def tt_now(self, t):                           # TrueTime: an interval sure to contain true time
        c = self.clock(t)
        return c - EPS, c + EPS


def commit(node, t, wait):
    """Commit at true time t. Returns (timestamp, true time the commit becomes visible)."""
    earliest, latest = node.tt_now(t)
    if not wait:
        return node.clock(t), t                    # stamp with the local clock, visible at once
    ts = latest                                    # a timestamp no earlier than true time
    while node.tt_now(t)[0] <= ts:                 # commit wait: until ts is surely in the past
        t += 0.0001
    return ts, t


def trial(rng, wait):
    a, b = Node(rng.uniform(-EPS, EPS)), Node(rng.uniform(-EPS, EPS))
    t1 = rng.uniform(0, 100)
    ts1, visible = commit(a, t1, wait)             # T1 on node a: revoke Bob's access to /payroll
    t2 = visible + rng.uniform(0, 0.005)           # T2 starts after T1 is visible, on node b
    ts2, done = commit(b, t2, wait)                # T2: upload salaries.csv to /payroll
    return ts2 <= ts1, visible - t1, (ts1, ts2)


for wait in (False, True):
    rng = random.Random(15)
    results = [trial(rng, wait) for _ in range(10_000)]
    bad = sum(r[0] for r in results)
    added = sum(r[1] for r in results) / len(results)
    label = "with commit wait   " if wait else "local clock stamps "
    print(f"{label}: {bad:5} of 10,000 causal pairs got timestamps"
          f" in the wrong order; commit latency added {added * 1000:.1f} ms")
    if bad:
        ts1, ts2 = next(r[2] for r in results if r[0])
        snap = (ts1 + ts2) / 2
        print(f"   e.g. revoke stamped {ts1:.4f}, upload stamped {ts2:.4f}: a snapshot read at {snap:.4f}"
              f"\n   sees salaries.csv in /payroll and Bob still allowed to read it")

print(f"\nthe wait is 2 x epsilon: {2 * EPS * 1000:.0f} ms at epsilon = {EPS * 1000:.0f} ms. "
      "Better clocks make every commit faster:")
for eps_ms in (7, 4, 1):
    print(f"  epsilon {eps_ms} ms -> commit wait {2 * eps_ms} ms")
