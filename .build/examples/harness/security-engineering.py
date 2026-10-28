# The Citadel: claims made by the text and comments about each example that prints nothing.
import os, pathlib, subprocess, tempfile, time, json, hmac, hashlib, base64
from lib import load, check, raises, report
V = "security-engineering#"

m = load(V + "1")
class Down:
    def check(self, *a): raise m.PolicyUnavailable()
class Says:
    def __init__(self, v): self.v = v
    def check(self, *a): return self.v
check(V + "1", "an outage fails open in the first, closed in the second",
      lambda: m.can_fail_open(Down(), 1, "read", 2) is True and m.can(Down(), 1, "read", 2) is False)
check(V + "1", "only True allows; None, 'yes' and 1 deny",
      lambda: m.can(Says(True), 1, "r", 2) and not any(m.can(Says(v), 1, "r", 2) for v in (None, "yes", 1)))

m = load(V + "3")
def history_case():
    d = pathlib.Path(tempfile.mkdtemp()); env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null",
        GIT_AUTHOR_NAME="a", GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_NAME="a", GIT_COMMITTER_EMAIL="a@x")
    subprocess.run(["git", "init", "-q", str(d)], check=True, env=env)
    (d / "notes.txt").write_text("hi\n")
    subprocess.run(["git", "-C", str(d), "add", "."], check=True, env=env)
    subprocess.run(["git", "-C", str(d), "commit", "-qm", "first"], check=True, env=env)
    owned = d / "owned"
    good = "first" in m.file_history(str(d), "notes.txt")
    m.file_history(str(d), f"x; touch {owned}")
    safe = not owned.exists()
    m.file_history_unsafe(str(d), f"x; touch {owned}")
    return good and safe and owned.exists()
check(V + "3", "the shell version runs an injected command; the list version doesn't", history_case)

m = load(V + "4")
def uploads_case():
    root = pathlib.Path(tempfile.mkdtemp()).resolve(); (root / "up").mkdir(); (root / "up" / "a.txt").write_text("x")
    (root / "secret").write_text("s"); (root / "up" / "link").symlink_to(root / "secret")
    m.UPLOADS = root / "up"
    return (m.open_upload("a.txt").read() == b"x" and raises(PermissionError, m.open_upload, "../../etc/passwd")
            and raises(PermissionError, m.open_upload, "/etc/passwd") and raises(PermissionError, m.open_upload, "link"))
check(V + "4", "a normal name opens; '..', absolute names and symlinks out are refused", uploads_case)

m = load(V + "6")
check(V + "6", "allowlisted sort and status build a parameterised query",
      lambda: m.build_query(7, "total", "desc", "paid") ==
              ("SELECT customer, total FROM invoices WHERE tenant_id = ? AND status = ? ORDER BY total DESC", [7, "paid"]))
check(V + "6", "anything else in sort, direction or status is refused",
      lambda: all(raises(ValueError, m.build_query, 7, *a) for a in
                  [("total; DROP TABLE invoices", "asc", None), ("total", "asc, (SELECT 1)", None), ("total", "asc", "x' OR '1'='1")]))

m = load(V + "7")
check(V + "7", "the comment renders as text, the javascript: link becomes '#', and the draft can't close the script",
      lambda: "<img" not in m.page and 'href="#"' in m.page and m.page.count("</script>") == 1 and "\\u003c/script\\u003e" in m.draft)

m = load(V + "8")
def csp_case():
    n1, h1 = m.strict_csp(); n2, _ = m.strict_csp()
    p = h1["Content-Security-Policy"]
    return n1 != n2 and f"'nonce-{n1}'" in p and "object-src 'none'" in p and "base-uri 'none'" in p and len(n1) >= 22
check(V + "8", "a fresh nonce per response, carried in a strict policy", csp_case)

m = load(V + "11")
check(V + "11", "exact origins only: not evilapp.example, not 'null', not a missing Origin",
      lambda: m.cors_headers("https://app.example").get("Access-Control-Allow-Origin") == "https://app.example"
              and all("Access-Control-Allow-Origin" not in m.cors_headers(o) for o in ("https://evilapp.example", "null", None))
              and all(m.cors_headers(o)["Vary"] == "Origin" for o in ("https://app.example", None)))

m = load(V + "12")
check(V + "12", "the three commented cases are refused",
      lambda: not m.allow_request("POST", {"Sec-Fetch-Site": "cross-site"}, "app.example")
              and not m.allow_request("POST", {"Sec-Fetch-Site": "same-site"}, "app.example")
              and not m.allow_request("POST", {"Origin": "https://evil.example"}, "app.example"))
check(V + "12", "same-origin, typed URLs, safe methods, non-browsers and a matching Origin are allowed",
      lambda: m.allow_request("POST", {"Sec-Fetch-Site": "same-origin"}, "app.example")
              and m.allow_request("POST", {"Sec-Fetch-Site": "none"}, "app.example")
              and m.allow_request("GET", {"Sec-Fetch-Site": "cross-site"}, "app.example")
              and m.allow_request("POST", {}, "app.example")
              and m.allow_request("POST", {"Origin": "https://app.example"}, "app.example"))

m = load(V + "14")
bad = ["http://127.1/", "http://2130706433/", "http://0x7f000001/", "http://[::1]/", "http://[::ffff:169.254.169.254]/",
       "http://100.64.0.1/", "http://localhost/", "file:///etc/passwd", "gopher://10.0.0.5:6379/", "https://user:pw@app.example/"]
check(V + "14", "every URL in the 'Rejected' comment is rejected, against the real resolver",
      lambda: all(raises(ValueError, m.resolve_public, u) for u in bad))
check(V + "14", "a public host resolves to a public address it can connect to",
      lambda: (lambda r: r[0] == "example.com" and r[2] == 443 and m.is_public(__import__("ipaddress").ip_address(r[1])))(m.resolve_public("https://example.com/")))

m = load(V + "15")
check(V + "15", "a local path passes; every commented trick returns '/'",
      lambda: m.safe_next("/invoices/3?tab=paid") == "/invoices/3?tab=paid"
              and all(m.safe_next(t) == "/" for t in ("https://evil.example", "//evil.example", "/\\evil.example", "javascript:alert(1)", None, "")))

m = load(V + "19")
def passwords_case():
    h = m.hash_password("correct horse")
    old_n = 2**14
    import secrets
    salt = secrets.token_bytes(16)
    old = f"scrypt${old_n}$8$1${salt.hex()}${hashlib.scrypt(b'correct horse', salt=salt, n=old_n, r=8, p=1, dklen=32).hex()}"
    users = {"a@x": {"hash": old}}
    upgraded = m.log_in(users, "a@x", "correct horse") and users["a@x"]["hash"].split("$")[1] == str(m.N)
    return (h.startswith("scrypt$131072$8$1$") and m.verify_password("correct horse", h) and not m.verify_password("wrong", h)
            and upgraded and not m.log_in(users, "a@x", "wrong") and not m.log_in(users, "nobody@x", "x"))
check(V + "19", "hashes verify, wrong passwords fail, and old parameters upgrade on log-in", passwords_case)
def timing_case():
    users = {"a@x": {"hash": m.hash_password("pw")}}
    t = time.perf_counter(); m.log_in(users, "a@x", "nope"); known = time.perf_counter() - t
    t = time.perf_counter(); m.log_in(users, "ghost@x", "nope"); unknown = time.perf_counter() - t
    return 0.5 < unknown / known < 2, f"known {known*1000:.0f} ms, unknown {unknown*1000:.0f} ms"
check(V + "19", "an unknown email takes about as long as a wrong password", timing_case)

m = load(V + "20")
def pwned_case():
    seen = []
    digest = hashlib.sha1(b"password").hexdigest().upper()
    def fetch(prefix):
        seen.append(prefix); return f"0000000000000000000000000000000000A:3\n{digest[5:]}:52372427\n"
    return m.times_pwned("password", fetch) == 52372427 and seen == [digest[:5]] and m.times_pwned("unusual-x", lambda p: "") == 0
check(V + "20", "only a five-character prefix leaves; the matching suffix's count comes back", pwned_case)

m = load(V + "21")
VECTORS = {59: "94287082", 1111111109: "07081804", 1111111111: "14050471", 1234567890: "89005924",
           2000000000: "69279037", 20000000000: "65353130"}
check(V + "21", "all six RFC 6238 SHA-1 test vectors",
      lambda: all(m.hotp(b"12345678901234567890", t // 30, digits=8) == c for t, c in VECTORS.items()))
def totp_case():
    s = b"12345678901234567890"; now = 1_700_000_000; step = now // 30
    code = m.hotp(s, step)
    first = m.verify_totp(s, code, last_used=0, now=now)
    replay = m.verify_totp(s, code, last_used=first, now=now)
    edge = m.verify_totp(s, m.hotp(s, step - 1), last_used=0, now=now) == step - 1
    far = m.verify_totp(s, m.hotp(s, step - 2), last_used=0, now=now) is None
    return first == step and replay is None and edge and far
check(V + "21", "a code works once, one step either side is accepted, two steps isn't", totp_case)

load(V + "23")   # it asserts its own claim
check(V + "23", "c1 XOR c2 XOR p1 == p2 (the example's own assert)", lambda: True)

m = load(V + "25")
KEY = b"server-secret"
def b64(x): return base64.urlsafe_b64encode(x).rstrip(b"=").decode()
def tok(claims, header=None, key=KEY, sig=None):
    h = b64(json.dumps(header or {"alg": "HS256", "typ": "JWT"}).encode()); c = b64(json.dumps(claims).encode())
    s = sig if sig is not None else b64(hmac.new(key, f"{h}.{c}".encode(), hashlib.sha256).digest())
    return f"{h}.{c}.{s}"
now = int(time.time()); good = {"iss": "https://id.acme", "aud": "api", "sub": "u1", "exp": now + 300}
v = lambda t: m.verify_jwt(t, KEY, issuer="https://id.acme", audience="api")
check(V + "25", "a valid token, and one whose audience is a list, verify",
      lambda: v(tok(good))["sub"] == "u1" and v(tok(dict(good, aud=["web", "api"])))["sub"] == "u1")
attacks = {
    "alg none": tok(good, {"alg": "none"}, sig=""),
    "alg HS512": tok(good, {"alg": "HS512"}),
    "signed with another key": tok(good, key=b"attacker"),
    "claims edited after signing": tok(good).split(".")[0] + "." + b64(json.dumps(dict(good, sub="admin")).encode()) + "." + tok(good).split(".")[2],
    "wrong issuer": tok(dict(good, iss="https://evil")),
    "wrong audience": tok(dict(good, aud="billing")),
    "expired": tok(dict(good, exp=now - 120)),
    "no expiry": tok({k: x for k, x in good.items() if k != "exp"}),
    "not valid yet": tok(dict(good, nbf=now + 600)),
    "malformed": "not.a.jwt.at.all",
}
for name, t in attacks.items():
    check(V + "25", f"rejects: {name}", lambda t=t: raises(ValueError, v, t))
check(V + "25", "accepts an expiry 20 s past, inside the 30 s leeway", lambda: v(tok(dict(good, exp=now - 20)))["sub"] == "u1")

m = load(V + "28")
def path(i, entries):
    if len(entries) == 1: return []
    k = 1 << ((len(entries) - 1).bit_length() - 1)
    return path(i, entries[:k]) + [m.root(entries[k:])] if i < k else path(i - k, entries[k:]) + [m.root(entries[:k])]
def merkle_case():
    for n in range(1, 34):
        es = [f"entry {j}".encode() for j in range(n)]; r = m.root(es)
        for i in range(n):
            p = path(i, es)
            if not m.verify_inclusion(i, n, es[i], p, r): return False, f"size {n} index {i}"
            if m.verify_inclusion(i, n, b"forged", p, r): return False, f"forged accepted at {n}/{i}"
            if n > 1 and m.verify_inclusion((i + 1) % n, n, es[i], p, r) and es[i] != es[(i + 1) % n]: return False, "wrong index accepted"
    return True
check(V + "28", "every entry of trees of 1 to 33 leaves verifies; forged entries and wrong indexes don't", merkle_case)
check(V + "28", "RFC 6962 root of the empty-prefix scheme for one leaf", lambda: m.root([b""]) == hashlib.sha256(b"\x00").digest())

m = load(V + "36")
r = m.request
check(V + "36", "the four commented decisions",
      lambda: [m.decide(r("s3:GetObject", "arn:aws:s3:::acme-invoices/2026/inv-1042.pdf"), [m.worker], [m.org_guardrail]),
               m.decide(r("s3:PutObject", "arn:aws:s3:::acme-invoices/2026/inv-1042.pdf"), [m.worker], [m.org_guardrail]),
               m.decide(r("s3:GetObject", "arn:aws:s3:::acme-invoices/legal-hold/case-7.pdf"), [m.worker], [m.org_guardrail]),
               m.decide(r("iam:CreateAccessKey", "arn:aws:iam::111122223333:user/ci", **{"aws:MultiFactorAuthPresent": "true"}), [m.worker], [m.org_guardrail])]
              == ["allow", "implicit deny", "explicit deny", "denied by guardrail"])
check(V + "36", "iam without MFA is an implicit deny",
      lambda: m.decide(r("iam:ListUsers", "*", **{"aws:MultiFactorAuthPresent": "false"}), [m.worker], [m.org_guardrail]) == "implicit deny")
report()
