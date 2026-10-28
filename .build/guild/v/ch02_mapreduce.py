"""Reading the MapReduce paper by building its core: map, shuffle, reduce, a combiner,
re-execution after a failure, and backup tasks for stragglers."""
import random
import re
from collections import defaultdict

DOCS = [  # eight "input splits", one per map task
    "the log is the database the rest is cache",
    "a cache is a log you are allowed to forget",
    "the database keeps the log and the log keeps the truth",
    "replicas apply the log in order and agree",
    "the truth is in the log not in the cache",
    "forget the cache and replay the log",
    "order is the hard part of the log",
    "agree on the order and the rest follows",
]


def map_fn(doc):                      # user code: emit (word, 1) for every word
    for word in re.findall(r"[a-z]+", doc):
        yield word, 1


def reduce_fn(word, counts):          # user code: add up one word's counts
    return sum(counts)


def run_job(docs, reducers=3, combiner=False, fail_task=None):
    """One MapReduce job. Each map task writes one partition per reducer, as the paper's do."""
    partitions = [defaultdict(list) for _ in range(reducers)]
    pairs_sent = 0
    for task, doc in enumerate(docs):
        attempts = 2 if task == fail_task else 1      # the master re-runs a task whose worker died
        for attempt in range(attempts):
            local = [defaultdict(list) for _ in range(reducers)]
            for word, n in map_fn(doc):
                local[sum(map(ord, word)) % reducers][word].append(n)     # partition by hash of the key
            if task == fail_task and attempt == 0:
                continue          # the worker died: its local output is lost, nothing was sent
            for r, part in enumerate(local):
                for word, ns in part.items():
                    if combiner:
                        ns = [reduce_fn(word, ns)]        # pre-aggregate on the map side
                    partitions[r][word].extend(ns)
                    pairs_sent += len(ns)
    result = {}
    for part in partitions:                                # each reducer sees its keys in sorted order
        for word in sorted(part):
            result[word] = reduce_fn(word, part[word])
    return result, pairs_sent


plain, sent_plain = run_job(DOCS)
combined, sent_combined = run_job(DOCS, combiner=True)
rerun, _ = run_job(DOCS, fail_task=3)
top = sorted(plain.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
print("top words:", ", ".join(f"{w} {n}" for w, n in top))
print(f"pairs shuffled to reducers: {sent_plain} without a combiner, {sent_combined} with one "
      f"({1 - sent_combined / sent_plain:.0%} less)")
print("same answer with the combiner:", combined == plain)
print("same answer after map task 3's worker died and the task was re-run:", rerun == plain)

# Stragglers: the job finishes when its slowest task does. The paper's fix is a backup copy of
# each task still running near the end; whichever copy finishes first wins.
rng = random.Random(7)
def job_time(tasks=200, machines=50, backups=False):
    times = []
    for _ in range(tasks):
        t = rng.uniform(1.0, 1.4)
        if rng.random() < 0.03:                  # a few machines are slow: a bad disk, a noisy neighbour
            t *= rng.uniform(5, 10)
        if backups and t > 2.0:                  # still running at the end: a backup copy starts there,
            t = min(t, 2.0 + rng.uniform(1.0, 1.4))   # and it usually lands on a healthy machine
        times.append(t)
    waves = [times[i:i + machines] for i in range(0, tasks, machines)]
    return sum(max(w) for w in waves)            # each wave of tasks waits for its slowest member
runs = 1000
without = sorted(job_time() for _ in range(runs))
with_b = sorted(job_time(backups=True) for _ in range(runs))
med = lambda xs: xs[len(xs) // 2]
print(f"\n200 tasks on 50 machines, 3% of tasks on a slow machine, {runs} simulated jobs:")
print(f"  median job time without backup tasks: {med(without):5.1f}")
print(f"  median job time with backup tasks:    {med(with_b):5.1f}  "
      f"({1 - med(with_b) / med(without):.0%} faster)")
