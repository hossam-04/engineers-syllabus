# Code in languages other than Python: Go and C compiled and run, JavaScript run in Node, SQL
# against a throwaway PostgreSQL 18, the Lua script inside a real Redis, JSON and YAML parsed, and
# shell scripts syntax-checked. Starts and stops its own servers.
import json, os, pathlib, re, shutil, socket, subprocess, tempfile, time
from lib import check, report, BLOCKS
TMP = pathlib.Path(tempfile.mkdtemp(prefix="other-"))
def sh(cmd, cwd=None, inp=None, env=None, timeout=120):
    r = subprocess.run(cmd, cwd=cwd, input=inp, capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, r.stdout, r.stderr
def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

# ---- Go (Go 1.26)
def go_run(bid):
    d = TMP / bid.replace("#", "_"); d.mkdir(); (d / "main.go").write_text(BLOCKS[bid]["text"])
    sh(["go", "mod", "init", "example"], cwd=d)
    return sh(["go", "run", "."], cwd=d, env=dict(os.environ, GOFLAGS="-mod=mod", GOTOOLCHAIN="local"))
rc, out, err = go_run("security-engineering#24")
check("security-engineering#24", "HPKE: a 1,172-byte ciphertext opens; one flipped bit fails authentication",
      lambda: (rc == 0 and "sealed: 1172 bytes" in out and '"account 12345678, sort code 00-00-00"' in out
               and "after tampering: cipher: message authentication failed" in out, out.strip().replace("\n", " | ") or err[-200:]))
rc, out, err = go_run("security-engineering#26")
check("security-engineering#26", "envelope encryption: decrypts after rotation; another row and the retired key both fail",
      lambda: (rc == 0 and out.splitlines() == ['"bank account 12345678" <nil>', "in another row: cipher: message authentication failed",
                                                "with the old key: cipher: message authentication failed"], out.strip().replace("\n", " | ")))
rc, out, err = go_run("security-engineering#41")
check("security-engineering#41", "the Go version panics with index out of range [16] with length 16",
      lambda: rc != 0 and "panic: runtime error: index out of range [16] with length 16" in err)

# ---- C, with Apple clang: the default build, one without fortification, and AddressSanitizer
c = TMP / "record.c"; c.write_text(BLOCKS["security-engineering#39"]["text"])
def c_build(flags, name):
    rc, _, err = sh(["cc", *flags, "-o", str(TMP / name), str(c)]); return rc, err
c_build(["-O2"], "rec_default"); c_build(["-O0", "-U_FORTIFY_SOURCE", "-D_FORTIFY_SOURCE=0"], "rec_plain"); c_build(["-g", "-fsanitize=address"], "rec_asan")
r_def, r_plain, r_asan = (sh([str(TMP / n)]) for n in ("rec_default", "rec_plain", "rec_asan"))
check("security-engineering#39", "the default (fortified) build stops at the strcpy", lambda: (r_def[0] != 0, f"rc {r_def[0]} {r_def[2][-120:].strip()}"))
check("security-engineering#39", "without fortification it prints is_admin = 1852990836 ('tern')",
      lambda: (r_plain[1].strip() == "is_admin = 1852990836" and (1852990836).to_bytes(4, "little") == b"tern", r_plain[1].strip()))
check("security-engineering#39", "AddressSanitizer reports a heap-buffer-overflow, a WRITE of size 32 after a 20-byte region",
      lambda: "heap-buffer-overflow" in r_asan[2] and "WRITE of size 32" in r_asan[2] and "20-byte region" in r_asan[2])
u = TMP / "util.c"; u.write_text("#include <stdio.h>\n#include <string.h>\n#include <stdlib.h>\n"          # the types it uses live elsewhere
             "struct item { int id; }; struct session { char *token; }; void log_event(const char *, const char *);\n" + BLOCKS["security-engineering#42"]["text"])
check("security-engineering#42", "the exercise's util.c compiles (its bugs are the exercise)", lambda: sh(["cc", "-fsyntax-only", "-w", str(u)])[0] == 0)

# ---- JavaScript, in Node
def node(bid, module=False):
    f = TMP / (bid.replace("#", "_") + (".mjs" if module else ".js")); f.write_text(BLOCKS[bid]["text"]); return f
rc, out, _ = sh(["node", str(node("shipping-products#46"))])
check("shipping-products#46", "prints 1, 2, 3, 4: microtasks before a 0 ms timer", lambda: out.split() == ["1:", "script", "2:", "script", "end", "3:", "microtask", "4:", "timer", "task"])
rc, out, _ = sh(["node", str(node("shipping-products#49"))])
check("shipping-products#49", "the exercise's answer, A D G C E F B, is what Node prints", lambda: (out.split() == list("ADGCEFB"), " ".join(out.split())))
for bid, mod in (("shipping-products#19", False), ("shipping-products#45", False), ("shipping-products#66", True), ("security-engineering#9", False)):
    check(bid, "parses as JavaScript", lambda f=node(bid, mod): sh(["node", "--check", str(f)])[0] == 0)

# ---- JSON, and JSON lines
for bid, b in BLOCKS.items():
    if b["lang"] == "json":
        txt = b["text"]
        stream = bid == "production-reliability#24"      # log records, each wrapped over lines for the page
        def records(txt):
            dec, i, out = json.JSONDecoder(), 0, []
            while i < len(txt.strip()):
                while txt[i].isspace(): i += 1
                obj, i = dec.raw_decode(txt, i); out.append(obj)
            return out
        check(bid, "parses as JSON" + (" records" if stream else ""),
              lambda txt=txt, stream=stream: len(records(txt)) > 1 if stream else json.loads(txt) is not None)

# ---- YAML, with Ruby's Psych
for bid, b in BLOCKS.items():
    if b["lang"] == "yaml":
        f = TMP / (bid.replace("#", "_") + ".yaml"); f.write_text(b["text"])
        check(bid, "parses as YAML", lambda f=f: sh(["ruby", "-ryaml", "-e", "YAML.load_stream(File.read(ARGV[0]))", str(f)])[0] == 0)

# ---- shell: syntax only (terminal transcripts, which start with "$ ", are output, not scripts)
for bid, b in BLOCKS.items():
    if b["lang"] == "bash" and not b["text"].lstrip().startswith("$ "):
        check(bid, "parses as bash", lambda txt=b["text"]: sh(["bash", "-n"], inp=txt)[0] == 0)

# ---- Lua, inside a real Redis
rport = free_port(); rdir = TMP / "redis"; rdir.mkdir()
redis = subprocess.Popen(["redis-server", "--port", str(rport), "--dir", str(rdir), "--save", "", "--appendonly", "no"], stdout=subprocess.DEVNULL)
time.sleep(0.5)
lua = TMP / "token_bucket.lua"; lua.write_text(BLOCKS["distributed-systems#31"]["text"])
def bucket(key, rate, burst, cost=1):
    _, out, _ = sh(["redis-cli", "-p", str(rport), "--eval", str(lua), key, ",", str(rate), str(burst), str(cost)]); return [int(x) for x in out.split()]
def lua_case():
    first = [bucket("rl:a", 2, 3) for _ in range(4)]
    allowed = [x[0] for x in first]; wait = first[3][1]
    ttl = int(sh(["redis-cli", "-p", str(rport), "PTTL", "rl:a"])[1])
    time.sleep(0.6); again = bucket("rl:a", 2, 3)[0]
    other = bucket("rl:b", 2, 3)[0]
    return (allowed == [1, 1, 1, 0] and 0 < wait <= 500 and 0 < ttl <= 1500 and again == 1 and other == 1,
            f"allowed {allowed}, wait {wait} ms, ttl {ttl} ms, after 0.6 s {again}")
check("distributed-systems#31", "a burst of 3 passes, the 4th waits under 500 ms, refills at the rate, idle keys expire", lua_case)
redis.terminate(); redis.wait()

# ---- SQL, in a throwaway PostgreSQL 18 cluster
SOCK = pathlib.Path(tempfile.mkdtemp(prefix="pg", dir="/tmp"))     # macOS caps socket paths at ~104 bytes
pg = TMP / "pg"; pport = free_port()
sh(["initdb", "-D", str(pg), "-U", "postgres", "--auth=trust", "-E", "UTF8", "--no-locale"])
sh(["pg_ctl", "-D", str(pg), "-o", f"-p {pport} -k {SOCK} -c listen_addresses=''", "-w", "start", "-l", str(TMP / "pg.log")],
   env=dict(os.environ, LC_ALL="en_US.UTF-8"))      # on macOS the postmaster refuses to start without a valid LC_ALL
def psql(sql, user="postgres", db="postgres"):
    return sh(["psql", "-h", str(SOCK), "-p", str(pport), "-U", user, "-d", db, "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=0"], inp=sql)
try:
    psql("CREATE DATABASE t17; CREATE ROLE app_user LOGIN;")
    setup = BLOCKS["security-engineering#17"]["text"].split("-- For each request")[0]
    rc, out, err = psql(setup, db="t17")
    psql("BEGIN; SET LOCAL app.tenant_id='1'; INSERT INTO invoices (tenant_id, customer, total) VALUES (1,'Acme',1200),(1,'O''Brien',300); COMMIT;"
         "BEGIN; SET LOCAL app.tenant_id='2'; INSERT INTO invoices (tenant_id, customer, total) VALUES (2,'Globex',99000); COMMIT;", db="t17")
    request = BLOCKS["security-engineering#17"]["text"].split("-- For each request, inside its transaction:")[1]
    rc, out, err = psql(request, user="app_user", db="t17")
    check("security-engineering#17", "tenant 1 sees only its own rows, filter or no filter", lambda: (sorted(out.split()) == sorted(["Acme|1200", "O'Brien|300"]), out.strip()))
    check("security-engineering#17", 'inserting a tenant-2 row fails with the error shown',
          lambda: 'new row violates row-level security policy for table "invoices"' in err)
    rc, out, err = psql("SELECT count(*) FROM invoices;", user="app_user", db="t17")
    check("security-engineering#17", "with no tenant set, the query fails closed (SET LOCAL didn't leak into the next transaction)",
          lambda: "unrecognized configuration parameter" in err and not out.strip())
    # the table's owner, when it isn't a superuser (superusers skip policies, as the text says)
    psql("CREATE ROLE owner_role; ALTER TABLE invoices OWNER TO owner_role;", db="t17")
    rc, out, err = psql("SET ROLE owner_role; BEGIN; SET LOCAL app.tenant_id = '2'; SELECT customer FROM invoices; COMMIT;", db="t17")
    check("security-engineering#17", "FORCE applies to the table's owner too: it sees only the tenant set", lambda: (out.split() == ["Globex"], out.split()))

    psql("CREATE DATABASE s36;")
    rc, out, err = psql("CREATE ROLE app2 LOGIN; CREATE TABLE invoices (id serial, team_id uuid NOT NULL, number text); GRANT SELECT, INSERT ON invoices TO app2;"
                        "INSERT INTO invoices (team_id, number) VALUES ('5b1d0e1e-6f3a-4c2e-9d61-0f1b2c3d4e5f','INV-1'),('00000000-0000-0000-0000-000000000002','INV-2');", db="s36")
    rls = BLOCKS["shipping-products#36"]["text"].split("-- At the start")[0]
    psql(rls, db="s36")
    rc, out, err = psql("BEGIN; " + BLOCKS["shipping-products#36"]["text"].split("from the authenticated session:")[1] + " SELECT number FROM invoices; COMMIT;", user="app2", db="s36")
    check("shipping-products#36", "with the team set, a request sees that team's invoices only", lambda: (out.split() == ["INV-1"], out.split() + [err.strip()[:120]]))
    rc, out, err = psql("SELECT count(*) FROM invoices;", user="app2", db="s36")
    check("shipping-products#36", "a fresh connection with no team set sees nothing", lambda: (out.split() == ["0"], out.split() + [err.strip()[:120]]))
    rc, out, err = psql("BEGIN; " + BLOCKS["shipping-products#36"]["text"].split("from the authenticated session:")[1] + " COMMIT; SELECT count(*) FROM invoices;", user="app2", db="s36")
    REUSED_36 = (out.split(), err.strip()[:160])
    print("note: same connection, after a request's SET LOCAL ended:", REUSED_36)

    psql("CREATE DATABASE d10;"); psql("CREATE TABLE team_slugs (slug text PRIMARY KEY, team_id text NOT NULL);", db="d10")
    first = psql(BLOCKS["distributed-systems#10"]["text"], db="d10")[1].split()
    second = psql(BLOCKS["distributed-systems#10"]["text"].replace("team_42", "team_99"), db="d10")[1].split()
    check("distributed-systems#10", "the first claim gets a row back; the second gets none", lambda: first == ["team_42"] and second == [])

    psql("CREATE DATABASE s97;")
    psql("CREATE TABLE invoices (id serial PRIMARY KEY, team_id int, due_date date, total numeric(12,2));"
         "INSERT INTO invoices (team_id, due_date, total) SELECT g % 7, date '2026-01-01' + g % 300, (g % 1000) / 7.0 FROM generate_series(1, 12000) g;", db="s97")
    mig = BLOCKS["shipping-products#97"]["text"]
    steps = re.split(r"\n(?=-- \d\.)", mig)
    log = []
    for step in steps[:-1]:                     # 1 to 3; step 4 in the text's table changes code, not schema
        for _ in range(3 if step.startswith("-- 2.") else 1): log.append(psql(step, db="s97"))   # 12,000 rows: three batches
    rc, out, err = psql("SELECT count(*) FILTER (WHERE total_minor IS NULL), count(*) FILTER (WHERE total_minor <> round(total*100)) FROM invoices;"
                        "SELECT is_nullable FROM information_schema.columns WHERE table_name='invoices' AND column_name='total_minor';", db="s97")
    check("shipping-products#97", "expand, backfill in batches of 5,000, then NOT NULL, without errors; every row correct",
          lambda: (all(not e.strip() for _, _, e in log) and out.split() == ["0|0", "NO"], f"{out.split()} {[e.strip()[:120] for _, _, e in log if e.strip()]}"))
    rc, out, err = psql(steps[-1] + "SELECT count(*) FROM information_schema.columns WHERE table_name='invoices' AND column_name='total';", db="s97")
    check("shipping-products#97", "step 5 drops the old column", lambda: rc == 0 and out.split() == ["0"])
    rc, out, err = psql(BLOCKS["shipping-products#98"]["text"], db="s97")
    check("shipping-products#98", "the concurrent index builds, with a lock timeout set", lambda: rc == 0 and not err.strip())

    psql("CREATE DATABASE s100;")
    psql("CREATE TABLE users (id int PRIMARY KEY, created_at timestamptz); CREATE TABLE events (user_id int, name text, occurred_at timestamptz);"
         "INSERT INTO users VALUES (1,'2026-09-07 10:00'),(2,'2026-09-08 10:00'),(3,'2026-09-09'),(4,'2026-09-15');"
         "INSERT INTO events VALUES (1,'Invoice Sent','2026-09-09'),(2,'Invoice Sent','2026-09-20'),(4,'Invoice Sent','2026-09-16'),(4,'Invoice Sent','2026-09-17');", db="s100")
    rc, out, err = psql("SET TIME ZONE 'UTC';" + BLOCKS["shipping-products#100"]["text"], db="s100")
    check("shipping-products#100", "weekly cohorts: signups, activated within 7 days, and the percentage",
          lambda: ([l.split("|")[1:] for l in out.split("\n") if l] == [["3", "1", "33.3"], ["1", "1", "100.0"]], out.strip().replace("\n", " / ")))

    psql("CREATE DATABASE s11;")
    psql("CREATE TABLE invoices (id int PRIMARY KEY, team_id int, due_date date, notes text, version int DEFAULT 1, updated_at timestamptz);", db="s11")
    for bid in ("shipping-products#11", "shipping-products#12", "shipping-products#13"):
        q = BLOCKS[bid]["text"]; n = len(set(re.findall(r"\$\d", q)))
        rc, out, err = psql(f"PREPARE q AS {q.rstrip().rstrip(';')};" if n else q, db="s11")      # PostgreSQL infers the parameter types
        check(bid, "PostgreSQL accepts it", lambda rc=rc, err=err: (rc == 0 and not err.strip(), err.strip()[:160]))
finally:
    sh(["pg_ctl", "-D", str(pg), "-m", "fast", "stop"])
shutil.rmtree(TMP, ignore_errors=True); shutil.rmtree(SOCK, ignore_errors=True)
report()
