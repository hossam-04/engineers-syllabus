# The Shipyard: claims made by the text and comments about each example that prints nothing.
import sqlite3, types, re, json, hashlib, base64, hmac, secrets, random
from datetime import datetime, timedelta, timezone
from lib import load, check, raises, report, BLOCKS
V = "shipping-products#"

class FakeDB:
    """sqlite behind the %s / %(name)s placeholders the examples use, rows as attributes."""
    def __init__(self, schema):
        self.c = sqlite3.connect(":memory:"); self.c.executescript(schema)
    def _sql(self, sql, params):
        if isinstance(params, dict):
            params = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in params.items()}
            return re.sub(r"%\((\w+)\)s", r":\1", sql), params
        return sql.replace("%s", "?"), tuple(v.isoformat() if isinstance(v, datetime) else v for v in params)
    def execute(self, sql, params=()):
        return self.c.execute(*self._sql(sql, params))
    def _row(self, cur, r):        # like a real driver, timestamps come back as datetimes
        return types.SimpleNamespace(**{d[0]: (datetime.fromisoformat(v) if d[0].endswith("_at") and isinstance(v, str) else v)
                                        for d, v in zip(cur.description, r)})
    def fetch_all(self, sql, params=()):
        cur = self.c.execute(*self._sql(sql, params)); return [self._row(cur, r) for r in cur.fetchall()]
    def fetch_one(self, sql, params=()):
        cur = self.c.execute(*self._sql(sql, params)); r = cur.fetchone(); return self._row(cur, r) if r else None

m = load(V + "8")
def pages_case():
    db = FakeDB("CREATE TABLE invoices(id TEXT, team_id TEXT, created_at TEXT);")
    base = datetime(2026, 9, 1, tzinfo=timezone.utc)
    for i in range(130):     # many invoices share a timestamp: the id breaks the tie
        db.execute("INSERT INTO invoices VALUES (?, ?, ?)", (f"inv_{i:03d}", "t1", (base + timedelta(minutes=i // 4)).isoformat()))
    db.execute("INSERT INTO invoices VALUES ('other', 't2', ?)", (base.isoformat(),))
    seen, cursor, pages = [], None, 0
    while True:
        page = m.list_invoices(db, "t1", cursor, limit=50); pages += 1
        seen += [r.id for r in page["data"]]
        if not page["has_more"]: break
        cursor = page["next_cursor"]
    expect = [f"inv_{i:03d}" for i in sorted(range(130), key=lambda i: (i // 4, f"inv_{i:03d}"), reverse=True)]
    clamp = len(m.list_invoices(db, "t1", None, limit=10_000)["data"]) == 100
    return seen == expect and pages == 3 and clamp and raises(Exception, m.decode_cursor, "not-a-cursor")
check(V + "8", "pages cover every row once, in order, with ties on time; the limit is capped; a bad cursor fails", pages_case)
check(V + "8", "the cursor round-trips and is opaque url-safe text",
      lambda: m.decode_cursor(m.encode_cursor(datetime(2026, 9, 1, 9, 12), "inv_8f3k2")) == (datetime(2026, 9, 1, 9, 12), "inv_8f3k2")
              and re.fullmatch(r"[A-Za-z0-9_-]+", m.encode_cursor(datetime(2026, 9, 1), "x")))

m = load(V + "9", UniqueViolation=sqlite3.IntegrityError, problem=lambda code, msg: {"type": code, "detail": msg})
def idem_case():
    db = FakeDB("CREATE TABLE idempotency_keys(key TEXT PRIMARY KEY, fingerprint TEXT, status TEXT, response_code INT, response_body TEXT);")
    runs = []
    h = lambda: (runs.append(1), (201, {"id": "pay_1"}))[1]
    first = m.with_idempotency(db, "k1", {"amount": 5, "to": "a"}, h)
    replay = m.with_idempotency(db, "k1", {"to": "a", "amount": 5}, h)        # same body, other key order
    reused = m.with_idempotency(db, "k1", {"amount": 6, "to": "a"}, h)
    db.execute("INSERT INTO idempotency_keys VALUES ('k2', ?, 'started', NULL, NULL)",
               (hashlib.sha256(json.dumps({"x": 1}, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),))
    busy = m.with_idempotency(db, "k2", {"x": 1}, h)
    return first == replay == (201, {"id": "pay_1"}) and len(runs) == 1 and reused[0] == 422 and busy[0] == 409
check(V + "9", "a retry replays the stored response; a reused key is 422; an unfinished one 409", idem_case)

m = load(V + "25")
class ResetDB:
    def __init__(self): self.rows = {}
    def execute(self, sql, p): self.rows[p[0]] = (p[1], p[2])
    def fetch_one(self, sql, p):
        r = self.rows.get(p[0])
        if r and r[1] > datetime.now(timezone.utc): del self.rows[p[0]]; return types.SimpleNamespace(user_id=r[0])
        return None
def reset_case():
    db = ResetDB(); t = m.create_reset_token(db, "u1")
    stored_plain = t in db.rows
    once = m.consume_reset_token(db, t) == "u1" and m.consume_reset_token(db, t) is None
    t2 = m.create_reset_token(db, "u2"); k = hashlib.sha256(t2.encode()).hexdigest()
    db.rows[k] = ("u2", datetime.now(timezone.utc) - timedelta(seconds=1))
    return not stored_plain and once and m.consume_reset_token(db, t2) is None and len(t) >= 43
check(V + "25", "only a hash is stored; a token works once, and not after it expires", reset_case)

m = load(V + "29", AUTHORIZE_URL="https://id.example/authorize", CLIENT_ID="app-1")
def pkce_case():
    real = m.secrets.token_urlsafe
    m.secrets = types.SimpleNamespace(token_urlsafe=lambda n: "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk", compare_digest=secrets.compare_digest)
    v, c = m.pkce_pair(); m.secrets = secrets
    v2, c2 = m.pkce_pair()
    return c == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM" and len(v2) == 86, f"challenge {c}"
check(V + "29", "PKCE matches the RFC 7636 test vector; a real verifier is 86 characters", pkce_case)
def authurl_case():
    from urllib.parse import urlsplit, parse_qs
    s = {}; q = {k: v[0] for k, v in parse_qs(urlsplit(m.authorization_url(s)).query).items()}
    return (q["state"] == s["oauth_state"] and q["nonce"] == s["oauth_nonce"] and q["code_challenge_method"] == "S256"
            and q["code_challenge"] == base64.urlsafe_b64encode(hashlib.sha256(s["pkce_verifier"].encode()).digest()).decode().rstrip("="))
check(V + "29", "the URL carries the state, nonce and challenge kept in the session", authurl_case)

class Forbidden(Exception): pass
ns = m.__dict__
ns.update(Forbidden=Forbidden, TOKEN_URL="https://id.example/token", CLIENT_SECRET="s", ISSUER="https://id.example")
exec(compile(BLOCKS[V + "30"]["text"], "<30>", "exec"), ns)        # the same file, continued
def callback_case():
    sent = {}
    class Http:
        def post(self, url, data, timeout): sent.update(data); return types.SimpleNamespace(json=lambda: {"id_token": "t"})
    ns["verify_id_token"] = lambda t, issuer, audience, nonce: (sent.update(nonce=nonce), {"iss": issuer, "sub": "s1", "email": "a@x"})[1]
    ns["find_or_link_user"] = lambda **k: k
    ns["start_new_session"] = lambda u: ("session", u["subject"])
    s = {"oauth_state": "S", "oauth_nonce": "N", "pkce_verifier": "V"}
    ok = ns["callback"](s, {"state": "S", "code": "c"}, Http()) == ("session", "s1")
    bad = raises(Forbidden, ns["callback"], {"oauth_state": "S"}, {"state": "T", "code": "c"}, Http())
    replay = raises(Forbidden, ns["callback"], {}, {"state": "", "code": "c"}, Http())
    return ok and sent["code_verifier"] == "V" and sent["nonce"] == "N" and bad and replay and "oauth_state" not in s
check(V + "30", "a state mismatch or missing state is refused; the verifier and nonce are used once", callback_case)

m = load(V + "35", Forbidden=Forbidden)
U = lambda role, team="t1": types.SimpleNamespace(role=role, team_id=team)
I = lambda status="draft", team="t1": types.SimpleNamespace(status=status, team_id=team)
check(V + "35", "the permission table, tenancy first, unknown roles get nothing, sent invoices admins only",
      lambda: m.can(U("viewer"), "invoice:read", I()) and not m.can(U("viewer"), "invoice:write", I())
              and m.can(U("member"), "invoice:write", I()) and not m.can(U("member"), "invoice:write", I("sent"))
              and m.can(U("admin"), "invoice:write", I("sent")) and not m.can(U("owner"), "invoice:read", I(team="t2"))
              and not m.can(U("superuser"), "invoice:read", I()) and not m.can(U("admin"), "billing:manage")
              and m.can(U("owner"), "billing:manage") and raises(Forbidden, m.authorize, U("viewer"), "invoice:delete", I()))

m = load(V + "79")
check(V + "79", "the real first bytes decide, whatever the declared type says",
      lambda: m.looks_like("image/png", b"\x89PNG\r\n\x1a\n...") and m.looks_like("application/pdf", b"%PDF-1.7")
              and not m.looks_like("image/png", b"%PDF-1.7") and not m.looks_like("image/svg+xml", b"<svg") and not m.looks_like("image/jpeg", b"MZ\x90"))

class InvalidSignature(Exception): pass
m = load(V + "83", InvalidSignature=InvalidSignature)
def webhook_case():
    secret = base64.b64decode("MfKQ9r8GKYqrTwjUPD8ILPZIo2LaLaSw")
    body = b'{"test": 2432232314}'
    h = {"webhook-id": "msg_p5jXN8AQM9LWM0D4loKWxJek", "webhook-timestamp": "1614265330",
         "webhook-signature": "v1,g0hM9SsE+OTPJTGt/tmIKtSyZlE3uFJELVlNIOLJ1OE="}
    m.time = types.SimpleNamespace(time=lambda: 1614265330 + 60)
    vector = m.verify_webhook(secret, h, body) is None
    rotated = m.verify_webhook(secret, dict(h, **{"webhook-signature": "v1,b2xk " + h["webhook-signature"]}), body) is None
    tampered = raises(InvalidSignature, m.verify_webhook, secret, h, body + b" ")
    other = raises(InvalidSignature, m.verify_webhook, b"other", h, body)
    m.time = types.SimpleNamespace(time=lambda: 1614265330 + 301)
    stale = raises(InvalidSignature, m.verify_webhook, secret, h, body)
    return vector and rotated and tampered and other and stale
check(V + "83", "the Standard Webhooks test vector verifies; rotation, tampering, wrong secret and replay are handled", webhook_case)

m = load(V + "89")
check(V + "89", "the commented conversions, plus three-digit and half-up cases",
      lambda: m.to_minor_units("19.99", "USD") == 1999 and m.to_minor_units("5000", "JPY") == 5000
              and m.to_minor_units("1.2345", "KWD") == 1235 and m.to_minor_units("0.005", "EUR") == 1 and m.to_minor_units("0.1", "USD") == 10)

m = load(V + "91")
def bucket_case():
    now = [0.0]; L = m.TokenBucketLimiter(rate_per_sec=2, burst=5, clock=lambda: now[0])
    burst = [L.allow("k")[0] for _ in range(5)]; denied, wait = L.allow("k")
    now[0] = wait; after = L.allow("k")[0]
    other = L.allow("k2")[0]
    now[0] = 1000; refill = sum(L.allow("k")[0] for _ in range(7))
    return all(burst) and not denied and abs(wait - 0.5) < 1e-9 and after and other and refill == 5
check(V + "91", "a burst of 5 passes, the 6th waits exactly 0.5 s, and refills cap at the burst", bucket_case)

class UnsafeUrl(Exception): pass
m = load(V + "93", UnsafeUrl=UnsafeUrl)
check(V + "93", "http, localhost, private and link-local addresses are refused; a public https host passes",
      lambda: all(raises(UnsafeUrl, m.assert_public_https_url, u) for u in
                  ("http://example.com/", "https://localhost/", "https://127.0.0.1/", "https://10.0.0.5/", "https://169.254.169.254/latest/", "https:///x"))
              and m.assert_public_https_url("https://example.com/hook") is None)

m = load(V + "104")
check(V + "104", "a missing required setting fails at start-up; email and payments default to safe",
      lambda: raises(KeyError, m.Config, {"PAYMENTS_SECRET_KEY": "x"})
              and (lambda c: c.email_sandbox and not c.payments_live and c.base_url == "http://localhost:8000")(m.Config({"DATABASE_URL": "d", "PAYMENTS_SECRET_KEY": "x"})))

src = BLOCKS[V + "96"]["text"]; src = src[:src.index("# Roll out")]
ns = {}; exec(src, ns); roll = ns["in_rollout"]
def rollout_case():
    ids = [f"team-{i}" for i in range(20_000)]
    five = {i for i in ids if roll("new_invoice_editor", i, 5)}; ten = {i for i in ids if roll("new_invoice_editor", i, 10)}
    other = {i for i in ids if roll("dark_mode", i, 5)}
    stable = all(roll("new_invoice_editor", i, 5) == (i in five) for i in list(ids)[:500])
    overlap = len(five & other) / len(five)
    return (abs(len(five) / 20_000 - .05) < .01 and five <= ten and stable and overlap < 0.12,
            f"{len(five)/200:.1f}% in at 5%, overlap with another flag {overlap:.1%}")
check(V + "96", "stable per subject, about 5% at 5, monotonic in percent, independent between flags", rollout_case)
report()
