"""Measuring delivery: the four DORA metrics computed from a real Git history with deploy tags and
an incident log, for three weeks of weekly releases and three weeks of releasing every day."""
import os, pathlib, statistics, subprocess, tempfile

BASE = {"PATH": os.environ["PATH"], "HOME": "/home/team", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "Dev", "GIT_AUTHOR_EMAIL": "dev@example.org",
        "GIT_COMMITTER_NAME": "Dev", "GIT_COMMITTER_EMAIL": "dev@example.org"}
START = 1780876800                      # a Monday, 00:00 UTC
HOUR, DAY = 3600, 86400

def git(*args, cwd, when=None):
    env = dict(BASE)
    if when:
        env.update(GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True)
    return r.stdout.strip()

with tempfile.TemporaryDirectory() as tmp:
    repo = pathlib.Path(tmp)
    git("init", "-q", "-b", "main", cwd=repo)
    deploys, n = [], 0
    for day in range(42):
        week, weekday = divmod(day, 7)
        if weekday >= 5:
            continue                                        # nobody works at the weekend
        for hour in (10, 14, 16):                           # three merged changes a day
            n += 1
            (repo / "app.txt").write_text(f"change {n}\n")
            git("add", "app.txt", cwd=repo)
            git("commit", "-q", "-m", f"Change {n}", cwd=repo, when=START + day * DAY + hour * HOUR)
        weekly = week < 3 and weekday == 4                  # weeks 1-3: one big release on Friday
        daily = week >= 3                                   # weeks 4-6: release every afternoon
        if weekly or daily:
            when = START + day * DAY + 17 * HOUR
            git("tag", f"deploy-{len(deploys) + 1}", cwd=repo)
            deploys.append((f"deploy-{len(deploys) + 1}", when, "weekly" if weekly else "daily"))

    # incidents: (the deploy that caused it, hours until service was restored)
    INCIDENTS = {"deploy-2": 6.0, "deploy-3": 3.5, "deploy-9": 0.5, "deploy-15": 0.75}

    print(f"{len(deploys)} deploys from {n} commits; incidents after {', '.join(INCIDENTS)}\n")
    print(f"{'':24}{'weekly releases':>18}{'daily releases':>18}")
    rows = {"weekly": {}, "daily": {}}
    previous = None
    for tag, when, kind in deploys:
        span = f"{previous}..{tag}" if previous else tag
        commit_times = [int(t) for t in git("log", "--format=%ct", span, cwd=repo).split()]
        r = rows[kind]
        r.setdefault("deploys", 0); r["deploys"] += 1
        r.setdefault("lead", []).extend((when - t) / HOUR for t in commit_times)
        r.setdefault("batch", []).append(len(commit_times))
        r.setdefault("failed", 0); r["failed"] += tag in INCIDENTS
        if tag in INCIDENTS:
            r.setdefault("restore", []).append(INCIDENTS[tag])
        previous = tag
    metrics = [
        ("deploys a week", lambda r: f"{r['deploys'] / 3:.1f}"),
        ("changes per deploy", lambda r: f"{statistics.mean(r['batch']):.0f}"),
        ("lead time, median", lambda r: f"{statistics.median(r['lead']):.1f} h"),
        ("change failure rate", lambda r: f"{r['failed'] / r['deploys']:.0%}"),
        ("time to restore, median", lambda r: f"{statistics.median(r['restore']):.1f} h"),
    ]
    for name, f in metrics:
        print(f"{name:24}{f(rows['weekly']):>18}{f(rows['daily']):>18}")
