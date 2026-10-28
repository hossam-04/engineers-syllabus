"""Estimating a project as a graph of uncertain tasks: what the plan's date really means, which
tasks decide the end date, and why parallel work finishes later than its parts suggest."""
import random

# task: (best case, most likely, worst case) in working days, and what it waits for
TASKS = {
    "design":    ((2, 3, 6), []),
    "migration": ((1, 2, 5), ["design"]),
    "api":       ((3, 5, 10), ["design"]),
    "ui":        ((4, 6, 12), ["api"]),
    "payments":  ((2, 4, 15), ["api"]),        # a third party's sandbox: usually fine, sometimes not
    "load test": ((1, 2, 4), ["ui", "payments", "migration"]),
    "launch":    ((1, 1, 3), ["load test"]),
}


def finish_times(duration):
    done = {}
    for task, (_, deps) in TASKS.items():          # listed in dependency order
        start = max((done[d] for d in deps), default=0)
        done[task] = start + duration[task]
    return done


def critical_path(duration, done):
    path, task = [], "launch"
    while task:
        path.append(task)
        deps = TASKS[task][1]
        task = max(deps, key=lambda d: done[d]) if deps else None
    return path[::-1]


likely = {t: est[1] for t, (est, _) in TASKS.items()}
plan = finish_times(likely)["launch"]
print(f"the plan, using every 'most likely' estimate: {plan} days "
      f"({' -> '.join(critical_path(likely, finish_times(likely)))})")

rng = random.Random(9)
runs, ends, critical = 20_000, [], {t: 0 for t in TASKS}
for _ in range(runs):
    d = {t: rng.triangular(lo, hi, mode) for t, ((lo, mode, hi), _) in TASKS.items()}
    done = finish_times(d)
    ends.append(done["launch"])
    for t in critical_path(d, done):
        critical[t] += 1
ends.sort()
p = lambda q: ends[int(q * (runs - 1))]
print(f"chance of finishing by day {plan}: {sum(e <= plan for e in ends) / runs:.0%}")
print(f"P50 {p(.5):.1f} days   P85 {p(.85):.1f} days   P95 {p(.95):.1f} days")

print("\nhow often each task is on the critical path:")
for t, n in sorted(critical.items(), key=lambda kv: -kv[1]):
    print(f"  {t:10} {n / runs:5.0%}")

# Merge bias: waiting for the later of two parallel tasks, each likely to take 6 days.
pairs = [max(rng.triangular(4, 12, 6), rng.triangular(4, 12, 6)) for _ in range(runs)]
single = sorted(rng.triangular(4, 12, 6) for _ in range(runs))
print(f"\none 6-day task: median {single[runs // 2]:.1f} days; "
      f"waiting for the later of two: median {sorted(pairs)[runs // 2]:.1f} days")

print("\nBrooks's law: pairs of people who must stay in sync")
for n in (3, 5, 8, 12):
    print(f"  {n:2} people: {n * (n - 1) // 2:3} channels")
