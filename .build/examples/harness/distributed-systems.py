# The Fleet: claims made by the text and comments about each example that prints nothing.
import random, types, sqlite3, math
from lib import load, check, raises, report
V = "distributed-systems#"

class Timeout(Exception): pass
class ConnectionLost(Exception): pass
m = load(V + "2", Timeout=Timeout, ConnectionLost=ConnectionLost)
class Resp:
    def __init__(self, code): self.status_code = code
    def json(self): return {"code": self.status_code}
class Client:
    def __init__(self, result): self.result, self.keys = result, []
    def post(self, path, json, timeout, headers):
        self.keys.append(headers["Idempotency-Key"])
        if isinstance(self.result, Exception): raise self.result
        return Resp(self.result)
req = {"idempotency_key": "k-1", "amount": 100}
check(V + "2", "a timeout, a lost connection and a 5xx are UNKNOWN; 4xx FAILED; 2xx SUCCEEDED",
      lambda: [m.charge(Client(x), req, 1)[0].name for x in (Timeout(), ConnectionLost(), 503, 402, 201)]
              == ["UNKNOWN", "UNKNOWN", "UNKNOWN", "FAILED", "SUCCEEDED"])
check(V + "2", "every attempt carries the idempotency key", lambda: (lambda c: (m.charge(c, req, 1), c.keys == ["k-1"])[1])(Client(201)))

m = load(V + "3")
def lamport_case():
    a, b = m.LamportClock(), m.LamportClock()
    a.tick(); a.tick(); sent = a.tick()           # a: 3
    b.tick()                                      # b: 1, concurrent with a's events
    got = b.receive(sent)                         # b jumps past the sender
    return got == 4 and got > sent and b.tick() == 5
check(V + "3", "receiving jumps past the sender's stamp, so causes always get smaller numbers", lamport_case)

m = load(V + "4")
def vc_case():
    a = m.increment({}, "A"); b = m.increment(a, "B"); c = m.increment(a, "C")
    return (m.compare(a, b) == "before" and m.compare(b, a) == "after" and m.compare(b, c) == "concurrent"
            and m.compare(b, dict(b)) == "equal" and m.compare(m.merge(b, c), b) == "after" and a == {"A": 1})
check(V + "4", "before, after, equal and concurrent are told apart; merge dominates both sides", vc_case)

m = load(V + "6")
class Leader:
    pos = 0
    def execute_returning_log_position(self, sql, args): self.pos += 10; return self.pos
    def get_invoice(self, i): return "leader"
class Follower:
    def __init__(self, name, pos): self.name, self.pos = name, pos
    def replayed_position(self): return self.pos
    def get_invoice(self, i): return self.name
def reads_case():
    s, L = {}, Leader(); m.save_invoice(s, L, types.SimpleNamespace(id=1))
    behind, caught = Follower("behind", 5), Follower("caught-up", 10)
    return (m.load_invoice(s, [behind, caught], L, 1) == "caught-up" and m.load_invoice(s, [behind], L, 1) == "leader"
            and m.load_invoice({}, [behind], L, 1) == "behind")
check(V + "6", "reads go to a follower that has replayed our write, else the leader", reads_case)

m = load(V + "7")
def crdt_case():
    rng = random.Random(3); reps = {n: m.GCounter(n) for n in "ABC"}; true = 0
    for _ in range(300):
        r = rng.choice("ABC"); k = rng.randint(1, 5); reps[r].increment(k); true += k
        if rng.random() < .3:                     # gossip, with duplicates and any order
            x, y = rng.sample("ABC", 2); reps[x].merge(reps[y]); reps[x].merge(reps[y])
    for _ in range(2):
        for x in "ABC":
            for y in "ABC": reps[x].merge(reps[y])
    return all(r.value() == true for r in reps.values())
check(V + "7", "replicas that gossip with duplicates and reordering converge on the true total", crdt_case)

m = load(V + "8")
def ring_case():
    keys = [f"team-{i}" for i in range(20_000)]
    four = m.HashRing(["n1", "n2", "n3", "n4"]); before = {k: four.node_for(k) for k in keys}
    four.add("n5"); after = {k: four.node_for(k) for k in keys}
    moved = [k for k in keys if before[k] != after[k]]
    to_new = all(after[k] == "n5" for k in moved)
    h = m._hash
    mod_moved = sum(h(k) % 4 != h(k) % 5 for k in keys) / len(keys)
    frac = len(moved) / len(keys)
    return 0.13 <= frac <= 0.20 and to_new and 0.75 <= mod_moved <= 0.85, f"ring moved {frac:.1%}, modulo {mod_moved:.1%}"
check(V + "8", "about 16% of keys move, all to the new node, against about 80% with modulo", ring_case)

m = load(V + "14")
class State:
    def __init__(self, term, voted, last_term, last_index):
        self.current_term, self.voted_for, self.role = term, voted, "follower"
        self._lt, self._li, self.persisted = last_term, last_index, 0
    def last_log_term(self): return self._lt
    def last_log_index(self): return self._li
    def persist(self): self.persisted += 1
    def reset_election_timer(self): pass
class VoteReply:
    def __init__(self, term, granted): self.term, self.granted = term, granted
m.VoteReply = VoteReply
R = lambda term, cand, lt, li: types.SimpleNamespace(term=term, candidate_id=cand, last_log_term=lt, last_log_index=li)
def raft_case():
    s = State(5, None, 3, 10)
    stale = not m.handle_request_vote(s, R(4, "x", 9, 99)).granted
    behind = not m.handle_request_vote(State(5, None, 3, 10), R(5, "x", 3, 9)).granted
    later_term_shorter = m.handle_request_vote(State(5, None, 3, 10), R(5, "x", 4, 1)).granted
    s2 = State(5, None, 3, 10); first = m.handle_request_vote(s2, R(5, "a", 3, 10)).granted
    second = m.handle_request_vote(s2, R(5, "b", 3, 12)).granted
    again = m.handle_request_vote(s2, R(5, "a", 3, 10)).granted
    s3 = State(5, "a", 3, 10); newterm = m.handle_request_vote(s3, R(6, "b", 3, 10)).granted and s3.current_term == 6
    return stale and behind and later_term_shorter and first and not second and again and newterm and s2.persisted >= 1
check(V + "14", "one vote per term, only for an up-to-date log, persisted; a new term resets the vote", raft_case)

m = load(V + "16")
def fence_case():
    st = m.FencedStore(); st.write("f", "client 2", 34)
    return raises(m.StaleLeaseholder, st.write, "f", "client 1", 33) and st.data["f"] == "client 2"
check(V + "16", "the woken client's write with token 33 is refused after 34", fence_case)

m = load(V + "20")
class DB:
    def __init__(self): self.c = sqlite3.connect(":memory:"); self.c.executescript(
        "CREATE TABLE processed_messages(message_id TEXT PRIMARY KEY); CREATE TABLE upgrades(id INT, status TEXT, n INT DEFAULT 0);"
        "INSERT INTO upgrades VALUES (7, 'pending', 0);")
    def transaction(self): return self.c
    def execute(self, sql, args):
        sql = sql.replace("%s", "?").replace("SET status = 'paid'", "SET status = 'paid', n = n + 1")
        return self.c.execute(sql, args)
def consumer_case():
    db = DB(); msg = types.SimpleNamespace(id="m-1", upgrade_id=7)
    for _ in range(3): m.handle_payment_captured(db, msg)
    return db.c.execute("SELECT status, n FROM upgrades").fetchone() == ("paid", 1)
check(V + "20", "a message delivered three times is applied once", consumer_case)

class InvalidCommand(Exception): pass
m = load(V + "22", InvalidCommand=InvalidCommand)
class Conflict(Exception): pass
class Store:
    def __init__(self): self.ev = {}
    def events_for(self, i): return list(self.ev.get(i, []))
    def append(self, i, e, expected_version):
        if len(self.ev.get(i, [])) != expected_version: raise Conflict()
        self.ev.setdefault(i, []).append(e)
def events_case():
    s = Store(); s.ev["inv"] = [{"type": "InvoiceCreated", "total_minor": 10000}, {"type": "InvoiceSent"}]
    m.record_payment(s, "inv", 4000); part = m.load(s, "inv").status
    m.record_payment(s, "inv", 6000); paid = m.load(s, "inv")
    s.ev["d"] = [{"type": "InvoiceCreated", "total_minor": 5}]
    draft = raises(InvalidCommand, m.record_payment, s, "d", 5)
    orig = s.append; s.append = lambda i, e, expected_version: (s.ev[i].append({"type": "InvoiceSent"}), orig(i, e, expected_version))
    racing = raises(Conflict, m.record_payment, s, "inv", 1)
    return part == "partially_paid" and paid.status == "paid" and paid.version == 4 and draft and racing
check(V + "22", "state is the fold of its events; a stale expected_version is refused", events_case)

m = load(V + "24")
def windows_case():
    t = m.TumblingCounter(60, 30); out = []
    for e in [5, 20, 61, 70, 50, 95, 125, 40, 200]: out += t.add(e)
    return out == [(0, 3), (60, 3)] and t.late == [40] and dict(t.open) == {120: 1, 180: 1}
check(V + "24", "a straggler inside the lateness counts; one after its window closed is set aside", windows_case)

m = load(V + "25")
def breaker_case():
    now = [0.0]; b = m.CircuitBreaker(3, 30, clock=lambda: now[0])
    def boom(): raise IOError("down")
    for _ in range(3): raises(IOError, b.call, boom)
    fast = raises(m.CircuitOpen, b.call, lambda: "x")
    now[0] = 31; reprobe = raises(IOError, b.call, boom) and raises(m.CircuitOpen, b.call, lambda: "x")
    now[0] = 62; closed = b.call(lambda: "ok") == "ok" and b.opened_at is None and b.failures == 0
    return fast and reprobe and closed
check(V + "25", "trips after the threshold, fails fast while open, re-trips on a failed probe, closes on success", breaker_case)

m = load(V + "27")
def xfetch_case():
    probs = {}
    for gap in (1.0, 0.5, 0.2, 0.05):
        rng = random.Random(9); hits = 0; n = 40_000
        for _ in range(n):
            calls = []
            cache = {"k": ("old", 0.2, 100.0)}
            m.xfetch(cache, "k", lambda: calls.append(1) or "new", 60, now=lambda: 100.0 - gap, rand=rng.random)
            hits += bool(calls)
        probs[gap] = hits / n
    ok = probs[1.0] < 0.01 and abs(probs[0.5] - .08) < .01 and abs(probs[0.2] - .37) < .01 and abs(probs[0.05] - .78) < .01
    return ok, ", ".join(f"{g}s: {p:.1%}" for g, p in probs.items())
check(V + "27", "refresh probabilities: under 1% at 1 s, ~8% at 0.5 s, 37% at 0.2 s, 78% at 50 ms", xfetch_case)
check(V + "27", "a missing entry is computed and cached with its recompute time",
      lambda: (lambda c: m.xfetch(c, "k", lambda: 42, 60, now=lambda: 5.0) == 42 and c["k"][0] == 42 and c["k"][2] == 65.0)({}))

m = load(V + "30")
from decimal import Decimal
def model_case():
    o = m.Order("o1", "EUR"); o.add_line("a", 2, m.Money(Decimal("9.50"), "EUR")); o.add_line("b", 1, m.Money(Decimal("1"), "EUR"))
    usd = raises(ValueError, lambda: m.Money(Decimal(1), "EUR") + m.Money(Decimal(1), "USD"))
    o.place()
    return (o.total() == m.Money(Decimal("20.00"), "EUR") and usd and raises(ValueError, o.add_line, "c", 1, m.Money(Decimal(1), "EUR"))
            and o.events == [m.OrderPlaced("o1", m.Money(Decimal("20.00"), "EUR"))] and raises(ValueError, m.Order("x", "EUR").place))
check(V + "30", "adding to a placed order and adding euros to dollars fail inside the model", model_case)
report()
