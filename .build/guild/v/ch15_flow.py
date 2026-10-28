"""Finishing things: a team of four with the same arrivals, run two ways. One starts every request
as it comes in; the other limits work in progress. Little's law ties the numbers together."""
import random

PEOPLE, DAYS, WARMUP = 4, 2000, 200
SWITCH = 0.04          # each item juggled beyond one per person costs this share of their time


def simulate(wip_limit, seed=15):
    rng = random.Random(seed)
    waiting, active, finished = [], [], []        # items: [arrived, started, work left]
    in_progress_days = 0
    for day in range(DAYS):
        for _ in range(sum(rng.random() < 0.25 for _ in range(3))):     # 0.75 new requests a day
            waiting.append([day, None, rng.uniform(2, 6)])              # 2 to 6 days of focused work
        while waiting and (wip_limit is None or len(active) < wip_limit):
            item = waiting.pop(0)
            item[1] = day
            active.append(item)
        if active:
            per_person = max(1, len(active) / PEOPLE)
            efficiency = 1 / (1 + SWITCH * (per_person - 1))            # context switching
            share = PEOPLE * efficiency / len(active) if len(active) > PEOPLE else efficiency
            for item in active:
                item[2] -= share
        done = [i for i in active if i[2] <= 0]
        active = [i for i in active if i[2] > 0]
        finished += [(i[0], i[1], day) for i in done if i[0] >= WARMUP]
        if day >= WARMUP:
            in_progress_days += len(active) + len(done)
    span = DAYS - WARMUP
    throughput = len(finished) / span
    wip = in_progress_days / span
    cycle = sum(end - start + 1 for _, start, end in finished) / len(finished)
    lead = sum(end - arrived + 1 for arrived, _, end in finished) / len(finished)
    return throughput, wip, cycle, lead


print(f"{'':28}{'start everything':>18}{'limit WIP to 4':>18}")
a, b = simulate(None), simulate(PEOPLE)
for i, name in enumerate(["finished per day", "average in progress", "cycle time (start->done)",
                          "lead time (asked->done)"]):
    unit = "" if i < 2 else " days"
    print(f"{name:28}{a[i]:>13.2f}{unit:5}{b[i]:>13.2f}{unit:5}")
print("\nLittle's law, in progress = finished per day x cycle time:")
for name, (tp, wip, cycle, _) in [("start everything", a), ("limit WIP to 4", b)]:
    print(f"  {name:18} {wip:6.2f} vs {tp:.2f} x {cycle:5.2f} = {tp * cycle:6.2f}")
