# The Watch: claims made by the text about each example that prints nothing.
import hashlib, io, json, logging, os, socket, statistics, subprocess, sys, tempfile, textwrap, threading, time
from lib import load, check, raises, report, BLOCKS
V = "production-reliability#"

def worker_case():
    script = BLOCKS[V + "2"]["text"] + textwrap.dedent("""
        import os, time
        done = []
        def process(job):
            if job == 1:
                os.kill(os.getpid(), signal.SIGTERM)     # the signal arrives mid-job
            time.sleep(0.3); done.append(job); print("finished", job, flush=True)
        for j in (1, 2, 3): jobs.put(j)
        try:
            run_worker(process)
        finally:
            print("left on queue", jobs.qsize(), flush=True)
        """)
    d = pathlib.Path(tempfile.mkdtemp()); (d / "w.py").write_text(script)
    r = subprocess.run([sys.executable, "w.py"], cwd=d, capture_output=True, text=True, timeout=30)
    return r.returncode == 0 and r.stdout.split("\n")[:2] == ["finished 1", "left on queue 2"], r.stdout.strip().replace("\n", " | ")
import pathlib
check(V + "2", "SIGTERM mid-job: that job finishes, no new one starts, the rest stay queued, exit 0", worker_case)

m = load(V + "4")
def where_case():
    hashing = m.where_did_the_time_go(lambda: [hashlib.sha256(b"x" * 1000).digest() for _ in range(300_000)])
    waiting = m.where_did_the_time_go(time.sleep, 0.5)
    return hashing[2] > 0.9 and waiting[2] < 0.05, f"hashing on-CPU {hashing[2]:.0%}, waiting {waiting[2]:.0%}"
check(V + "4", "hashing is ~all on-CPU; sleeping is ~0%", where_case)

def loadgen_case():
    # The text's toy: serves in 5 ms, but stalls for 200 ms once a second.
    srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(512); port = srv.getsockname()[1]
    gate = threading.Lock(); stop = threading.Event()
    def staller():
        while not stop.is_set():
            time.sleep(0.8)
            with gate: time.sleep(0.2)
    def serve():
        while not stop.is_set():
            try: c, _ = srv.accept()
            except OSError: return
            with c:
                c.recv(64)
                with gate: time.sleep(0.005)
                c.sendall(b"ok")
    for f in (staller, serve): threading.Thread(target=f, daemon=True).start()
    def one_request(p):
        with socket.create_connection(("127.0.0.1", p), timeout=5) as s:
            s.sendall(b"GET"); s.recv(8)
    m = load(V + "5", time=time, threading=threading, one_request=one_request)
    closed = m.closed_loop(port, 6); opened = m.open_loop(port, 6, 100)
    stop.set(); srv.close()
    q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))]
    slow = lambda xs: sum(x > 0.1 for x in xs) / len(xs)
    note = (f"closed median {statistics.median(closed)*1000:.1f} ms p99 {q(closed,.99)*1000:.0f} ms >100ms {slow(closed):.1%}; "
            f"open median {statistics.median(opened)*1000:.0f} ms p99 {q(opened,.99)*1000:.0f} ms >100ms {slow(opened):.0%}")
    return slow(closed) < 0.03 and slow(opened) > 0.2 and statistics.median(opened) > 4 * statistics.median(closed), note
check(V + "5", "closed loop reports ~1% slow; open loop at 100/s reports over a third slow, on the same stalling server", loadgen_case)

m = load(V + "11")
def config_case():
    env = {"DATABASE_URL": "", "PORT": "70000", "WORKERS": "0", "REQUEST_TIMEOUT_S": "-1", "NEW_PDF_RENDERER": "yes"}
    try: m.load(env); return False
    except m.ConfigError as e: got = f"ConfigError: {e}"
    want = BLOCKS[V + "12"]["text"].strip()
    good = m.load({"DATABASE_URL": "postgres://u:pw@db/app", "PORT": "8000", "NEW_PDF_RENDERER": "true"})
    return got == want and good.port == 8000 and good.new_pdf_renderer is True and good.redacted()["database_url"] == "***", got.replace("\n", " / ")
check(V + "11", "a bad environment produces exactly the error printed in the book, all problems at once", config_case)

m = load(V + "23")
def logging_case():
    buf = io.StringIO(); h = logging.StreamHandler(buf); h.setFormatter(m.JsonFormatter())
    lg = logging.getLogger("harness"); lg.handlers = [h]; lg.setLevel(logging.INFO); lg.propagate = False
    m.context.set({"trace_id": "t-1", "request_id": "r-9"})
    m.log(lg, logging.INFO, "invoice sent", invoice_id="inv_1", api_key="sk_live_x", card_last4="4242")
    try: 1 / 0
    except ZeroDivisionError: lg.exception("boom")
    a, b = [json.loads(l) for l in buf.getvalue().splitlines()]
    return (a["trace_id"] == "t-1" and a["invoice_id"] == "inv_1" and a["api_key"] == "***" and a["card_last4"] == "***"
            and a["level"] == "info" and a["ts"].endswith("Z") and b["error_type"] == "ZeroDivisionError" and "Traceback" in b["stack"])
check(V + "23", "context rides on every line, sensitive keys are redacted, errors carry type and stack", logging_case)
def sampling_case():
    ids = [hashlib.md5(str(i).encode()).hexdigest() for i in range(50_000)]
    kept = [m.keep(i, 0.1) for i in ids]
    return abs(sum(kept) / len(ids) - 0.1) < 0.01 and kept == [m.keep(i, 0.1) for i in ids], f"kept {sum(kept)/len(ids):.1%}"
check(V + "23", "sampling keeps about the rate, and the same traces every time", sampling_case)
report()
