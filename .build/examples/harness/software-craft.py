# The Craft: claims made by the text about its self-contained examples.
import random, re, types, collections, dataclasses
from decimal import Decimal
from lib import load, check, raises, report, BLOCKS
V = "software-craft#"

Reminder = collections.namedtuple("Reminder", "to number days_overdue")
m = load(V + "11", Reminder=Reminder, render=lambda r: f"{r.number} is {r.days_overdue} days overdue")
from datetime import date
Inv = lambda n, due, paid=False: types.SimpleNamespace(customer_email=f"{n}@x", number=n, due_date=due, paid=paid)
def reminders_case():
    invs = [Inv("A", date(2026, 5, 1)), Inv("B", date(2026, 5, 20)), Inv("C", date(2026, 4, 1), paid=True), Inv("D", date(2026, 5, 11))]
    core = m.overdue_reminders(invs, date(2026, 5, 11))
    sent = []
    shell = types.SimpleNamespace(unpaid_invoices=lambda: invs)
    m.send_overdue_reminders(shell, types.SimpleNamespace(send=lambda to, body: sent.append((to, body))), types.SimpleNamespace(today=lambda: date(2026, 5, 11)))
    return core == [Reminder("A@x", "A", 10)] and sent == [("A@x", "A is 10 days overdue")]
check(V + "11", "the pure core picks unpaid, past-due invoices; the shell only gathers and sends", reminders_case)

class IllegalTransition(Exception): pass
m = load(V + "57", IllegalTransition=IllegalTransition)
def lifecycle_case():
    o = types.SimpleNamespace(status="pending")
    for a in ("pay", "ship", "deliver", "return"): m.transition(o, a)
    return o.status == "returned" and raises(IllegalTransition, m.transition, types.SimpleNamespace(status="pending"), "ship") \
           and raises(IllegalTransition, m.transition, types.SimpleNamespace(status="cancelled"), "pay")
check(V + "57", "legal actions move the order on; anything else raises", lifecycle_case)

# chapter 10: the TDD cycles, each one's tests against its own implementation, in order
pytest_stub = types.SimpleNamespace(mark=types.SimpleNamespace(parametrize=lambda *a: (lambda f: f)))   # pytest isn't installed
ns = {"re": re, "pytest": pytest_stub}
cycles = {}
for k in (80, 81, 82, 83):
    exec(BLOCKS[f"{V}{k}"]["text"], ns); cycles[k] = ns["parse_duration"]
check(V + "80", "cycle 1's naive version passes its test", lambda: cycles[80]("45m") == 2700)
check(V + "81", "cycle 2 passes both tests so far", lambda: cycles[81]("45m") == 2700 and cycles[81]("2h") == 7200)
check(V + "82", "cycle 3 passes all three", lambda: all(cycles[82](s) == n for s, n in (("45m", 2700), ("2h", 7200), ("1h30m", 5400))))
check(V + "83", "cycle 4 rejects every malformed input in the parametrize list and still passes the rest",
      lambda: all(raises(ValueError, cycles[83], b) for b in ["", "10", "5x", "1h 30m", "h"])
              and all(cycles[83](s) == n for s, n in (("45m", 2700), ("2h", 7200), ("1h30m", 5400))))
src = BLOCKS[V + "84"]["text"]; exec(src[:src.index("from hypothesis")], ns)
def property_case():
    fails = [s for s in range(0, 200_000) if raises(ValueError, ns["parse_duration"], ns["format_duration"](s))
             or (ns["format_duration"](s) and ns["parse_duration"](ns["format_duration"](s)) != s)]
    return fails == [0], f"failing inputs: {fails[:5]}"
check(V + "84", "the round-trip property fails at seconds=0, and only there", property_case)

m = load(V + "86")
def mutant_case():
    src = BLOCKS[V + "86"]["text"]
    mutant = {}; exec(src.replace(">= 5000", "> 5000"), mutant)
    survives = mutant["qualifies_for_free_shipping"](10_000) and not mutant["qualifies_for_free_shipping"](1_000)
    killed = mutant["qualifies_for_free_shipping"](5000) is False and m.qualifies_for_free_shipping(5000) is True
    m.test_large_order_ships_free(); m.test_small_order_pays_shipping()
    return survives and killed
check(V + "86", "the >= to > mutant passes both tests; assert ...(5000) kills it", mutant_case)

# chapter 11: the refactoring, checked against the original on two thousand random orders
orig = load(V + "90", name="orig")
ref = load(V + "91", name="ref", dataclass=dataclasses.dataclass)
def refactor_case():
    rng = random.Random(11); differ = 0
    for _ in range(2000):
        items = [types.SimpleNamespace(name=rng.choice(["Pen", "Atlas", "Mug", "Lamp"]), quantity=rng.randint(1, 9),
                                       unit_price=round(rng.uniform(0.5, 120), 2), category=rng.choice(["books", "clearance", "home", "office"]))
                 for _ in range(rng.randint(0, 8))]
        order, cust = types.SimpleNamespace(items=items), types.SimpleNamespace(name=rng.choice(["Ana", "Lee"]))
        a, b = orig.receipt(order, cust).split("\n"), ref.receipt(order, cust).split("\n")
        if a == b: continue
        diff = [(x, y) for x, y in zip(a, b) if x != y]
        if len(a) != len(b) or len(diff) != 1 or not diff[0][0].startswith("Total: "): return False, f"unexpected difference {diff}"
        if abs(float(diff[0][0][7:]) - float(diff[0][1][7:])) > 0.0100001: return False, f"more than a cent: {diff}"
        differ += 1
    return 0.03 <= differ / 2000 <= 0.07, f"{differ} of 2,000 totals differ, each by one cent"
check(V + "91", "on 2,000 random orders only the total ever differs, by a cent, in about one in twenty (Python 3.12+ sum)", refactor_case)

class CurrencyMismatch(Exception): pass
m = load(V + "92", CurrencyMismatch=CurrencyMismatch)
check(V + "92", "dollars plus euros is an error; rounding is half-even, in one place; the factory takes strings",
      lambda: raises(CurrencyMismatch, lambda: m.Money.usd("1") + m.Money.of("1", "EUR"))
              and m.Money.usd("0.1") + m.Money.usd("0.2") == m.Money.usd("0.3")
              and m.Money.usd("0.125").amount == Decimal("0.12") and m.Money.usd("0.135").amount == Decimal("0.14")
              and m.Money.usd("19.99").times(3).cents == 5997 and m.Money.usd("10").times(0.15) == m.Money.usd("1.50"))
ns100 = {"Money": m.Money}
exec("def gift_wrap_fee" + BLOCKS[V + "100"]["text"].split("def gift_wrap_fee")[1], ns100)   # the new, pure part
check(V + "100", "the sprouted function is pure and testable on its own",
      lambda: ns100["gift_wrap_fee"]([types.SimpleNamespace(gift_wrap=g) for g in (True, False, True)]) == m.Money.usd("7.00"))

m = load(V + "131")
def retry_case():
    sleeps = []; m.time = types.SimpleNamespace(sleep=sleeps.append); m.random = random.Random(4)
    tries = []
    def flaky():
        tries.append(1)
        if len(tries) < 4: raise TimeoutError()
        return "ok"
    ok = m.call_with_retries(flaky) == "ok" and len(tries) == 4
    ceilings_ok = all(0 <= s <= c for s, c in zip(sleeps, [0.2, 0.4, 0.8]))
    sleeps.clear(); gives_up = raises(ConnectionError, m.call_with_retries, lambda: (_ for _ in ()).throw(ConnectionError()))
    other = raises(ValueError, m.call_with_retries, lambda: (_ for _ in ()).throw(ValueError()))
    capped = []; m.time = types.SimpleNamespace(sleep=capped.append)
    raises(TimeoutError, m.call_with_retries, lambda: (_ for _ in ()).throw(TimeoutError()), attempts=10, base=1, cap=5)
    return ok and ceilings_ok and gives_up and len(sleeps) == 3 and other and max(capped) <= 5 and len(capped) == 9
check(V + "131", "retries with full jitter under a capped exponential ceiling; gives up after the last; other errors pass straight through", retry_case)

slow, fast = load(V + "141", name="slow"), load(V + "142", name="fast")
def perf_case():
    rng = random.Random(2)
    cs = [types.SimpleNamespace(id=i) for i in range(2000)]; os_ = [types.SimpleNamespace(customer_id=rng.randrange(4000)) for _ in range(5000)]
    return [c.id for c in slow.customers_without_orders(cs, os_)] == [c.id for c in fast.customers_without_orders(cs, os_)]
check(V + "142", "the set version returns exactly what the list version did", perf_case)
check(V + "142", "the arithmetic: 10,000 x 100,000 is billions; 100,000 + 10,000 is about 110,000",
      lambda: 10_000 * 100_000 >= 1e9 and 100_000 + 10_000 == 110_000)
report()
