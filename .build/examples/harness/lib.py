# Shared helpers for the per-volume harnesses: load an example's code from the volume itself (via
# blocks.json, rebuilt by extract_blocks.py), and record each claim checked.
import json, pathlib, sys, types, traceback
HERE = pathlib.Path(__file__).resolve().parent
BLOCKS = {b["id"]: b for b in json.load(open(HERE.parent / "blocks.json"))}
RESULTS = []

def load(block_id, name="example", **inject):
    """Run one code block as a module and return it; `inject` pre-defines names it expects."""
    mod = types.ModuleType(name); mod.__dict__.update(inject)
    sys.modules[name] = mod
    exec(compile(BLOCKS[block_id]["text"], f"<{block_id}>", "exec"), mod.__dict__)
    return mod

def check(block_id, claim, fn):
    """fn() must return True. Exceptions count as failures."""
    try:
        ok, note = fn(), ""
        if isinstance(ok, tuple): ok, note = ok
    except Exception as e:
        ok, note = False, f"{type(e).__name__}: {e}"
    RESULTS.append((block_id, claim, bool(ok), note))

def raises(exc, fn, *a, **k):
    try: fn(*a, **k)
    except exc: return True
    return False

def report():
    bad = [r for r in RESULTS if not r[2]]
    for b, c, ok, note in RESULTS:
        print(f"{'ok  ' if ok else 'FAIL'} {b:28} {c}" + (f"   [{note}]" if note else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} claims hold, over {len({r[0] for r in RESULTS})} examples")
    sys.exit(1 if bad else 0)
