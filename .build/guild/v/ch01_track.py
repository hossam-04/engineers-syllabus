"""Choosing a track to go deep in: score the candidates, then ask how fragile the answer is."""

# A backend engineer on a payments team, scoring five candidate tracks from 1 to 5.
CRITERIA = {             # weight: how much this criterion matters to them
    "leverage": 3,       # how often their team's hard problems land here
    "curiosity": 3,      # would they read about it on a free weekend, for years?
    "adjacency": 2,      # how much of what they already know carries over
    "demand": 1,         # how many teams, anywhere, need a deep expert in it
}
TRACKS = {
    "databases":        {"leverage": 5, "curiosity": 3, "adjacency": 4, "demand": 4},
    "distributed":      {"leverage": 4, "curiosity": 4, "adjacency": 3, "demand": 4},
    "security":         {"leverage": 3, "curiosity": 5, "adjacency": 2, "demand": 5},
    "performance":      {"leverage": 3, "curiosity": 3, "adjacency": 3, "demand": 3},
    "ml-infrastructure": {"leverage": 1, "curiosity": 4, "adjacency": 1, "demand": 5},
}


def total(track, weights):
    return sum(weights[c] * TRACKS[track][c] for c in weights)


def ranking(weights):
    return sorted(TRACKS, key=lambda t: (-total(t, weights), t))


weights = dict(CRITERIA)
order = ranking(weights)
print("track               " + "".join(f"{c:>11}" for c in CRITERIA) + "      total")
for t in order:
    print(f"{t:20}" + "".join(f"{TRACKS[t][c]:>11}" for c in CRITERIA) + f"{total(t, weights):>11}")
winner, runner_up = order[0], order[1]
lead = total(winner, weights) - total(runner_up, weights)
print(f"\nwinner: {winner}, {lead} points ahead of {runner_up}")

# How far can each weight move, with the others held, before the winner changes?
print("\nweight range that keeps the same winner (tried from 0 to 6 in steps of 0.5):")
for c in CRITERIA:
    keep = [w / 2 for w in range(0, 13) if ranking({**weights, c: w / 2})[0] == winner]
    flips = sorted({ranking({**weights, c: w / 2})[0] for w in range(0, 13)} - {winner})
    note = "never flips" if not flips else "otherwise " + ", ".join(flips) + " wins"
    print(f"  {c:10} now {weights[c]}:  {min(keep):g} to {max(keep):g}   ({note})")

# What would have to be true for the runner-up to win? One score at a time.
def winner_if(track, criterion, score):
    saved, TRACKS[track][criterion] = TRACKS[track][criterion], score
    try:
        return ranking(weights)[0]
    finally:
        TRACKS[track][criterion] = saved


print(f"\nwhat would have to be true for {runner_up} to win, one score at a time:")
print(f"  {'criterion':10} {winner + ' falls to':>18} {runner_up + ' rises to':>20}")
for c in CRITERIA:
    now_w, now_r = TRACKS[winner][c], TRACKS[runner_up][c]
    fall = next((s for s in range(now_w - 1, 0, -1) if winner_if(winner, c, s) == runner_up), None)
    rise = next((s for s in range(now_r + 1, 6) if winner_if(runner_up, c, s) == runner_up), None)
    show = lambda now, s: f"{now} -> {s}" if s else "no score does it"
    print(f"  {c:10} {show(now_w, fall):>18} {show(now_r, rise):>20}")
