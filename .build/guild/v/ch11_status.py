"""A status update written from the project's own data: the colour comes from the forecast, not
from mood, and each audience gets the bottom line first."""
import random

TODAY, COMMITTED = 12, 30              # working days since kickoff; the date we promised
REMAINING = {                          # task: (best, most likely, worst) days left
    "refunds in the bank API": (3, 5, 12),
    "fraud rules sign-off": (1, 2, 6),
    "admin screens": (4, 5, 8),
    "load and failover test": (2, 3, 5),
}
DONE = ["data model", "migration of old data", "email templates"]
BLOCKERS = [("bank API: refunds endpoint returns 501 in sandbox", "the bank's integration team",
             "ticket open 6 days")]
DECISIONS = [("ship without partial refunds if the bank can't support them by day 20",
              "product lead", "day 18")]

def forecast(remaining, start=TODAY, seed=11):
    rng = random.Random(seed)
    return sorted(start + sum(rng.triangular(lo, hi, mode) for lo, mode, hi in remaining.values())
                  for _ in range(10_000))


ends = forecast(REMAINING)
p50, p85 = ends[len(ends) // 2], ends[int(len(ends) * 0.85)]
stuck = forecast(REMAINING, start=TODAY + 5)          # if the blocker holds the work up another week
stuck_p50 = stuck[len(stuck) // 2]
on_time = sum(e <= COMMITTED for e in ends) / len(ends)
colour = "GREEN" if p85 <= COMMITTED else ("AMBER" if p50 <= COMMITTED else "RED")

print("=== the status update nobody reads ===")
print("This week we continued working on the bank integration and made good progress on the admin")
print("screens. We had several meetings with the bank. Next week we will keep going.\n")

print("=== for the leadership summary: two lines ===")
print(f"{colour}: {on_time:.0%} likely to ship by day {COMMITTED} as committed "
      f"(median forecast day {p50:.1f}).")
what, who, when = DECISIONS[0]
print(f"Need: a decision from the {who} by {when} on whether to {what}.\n")

print("=== for partner teams: what we need from you ===")
for what, who, age in BLOCKERS:
    print(f"- {who}: {what} ({age}). If it holds us up another week, "
          f"the median forecast moves from day {p50:.1f} to day {stuck_p50:.1f}.")
print()

print("=== for the team: the detail ===")
print(f"done: {', '.join(DONE)}")
for task, (lo, mode, hi) in REMAINING.items():
    print(f"open: {task:26} {mode} days likely, {lo} to {hi}")
widest = max(REMAINING, key=lambda t: REMAINING[t][2] - REMAINING[t][0])
print(f"forecast: P50 day {p50:.1f}, P85 day {p85:.1f}; committed day {COMMITTED}. "
      f"The widest range is {widest}, so it's the task to finish first.")
