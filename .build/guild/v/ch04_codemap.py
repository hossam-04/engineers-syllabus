"""Reading production code: map a real package before reading it, then trace what actually runs.
The package is the standard library's json, as shipped with this Python."""
import ast
import json
import pathlib
import sys

pkg = pathlib.Path(json.__file__).parent
print(f"json package, Python {sys.version_info.major}.{sys.version_info.minor}")

# 1. The map: files, sizes, what each defines, and who imports whom.
print("\nmodule        lines  defines")
imports = {}
for f in sorted(pkg.glob("*.py")):
    tree = ast.parse(f.read_text(encoding="utf-8"))
    names = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    public = [n for n in names if not n.startswith("_")]
    deps = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.level:             # from .decoder import ...
            deps.add((n.module or "").split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module == "json":  # from json import scanner
            deps.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom) and (n.module or "").startswith("json."):
            deps.add(n.module.split(".")[1])
    imports[f.stem] = sorted(deps - {"", f.stem})
    lines = len(f.read_text(encoding="utf-8").splitlines())
    print(f"{f.stem:12} {lines:6}  {', '.join(public) or '(only private helpers)'}")
print("\nimports within the package:")
for mod, deps in imports.items():
    if deps:
        print(f"  {mod} -> {', '.join(deps)}")
print("the public entry points (json.__all__):", ", ".join(json.__all__))


# 2. The trace: which of those functions actually run for one call, and in what order.
def trace(call):
    seen, depth = [], [0]
    def profiler(frame, event, arg):
        if pathlib.Path(frame.f_code.co_filename).parent != pkg:
            return
        if event == "call":
            module = pathlib.Path(frame.f_code.co_filename).stem
            seen.append("  " * depth[0] + f"{module}.{frame.f_code.co_qualname}")
            depth[0] += 1
        elif event == "return":
            depth[0] -= 1
    sys.setprofile(profiler)
    try:
        return call(), seen
    finally:
        sys.setprofile(None)

value = {"id": 7, "tags": ["a", "b"], "price": 9.5, "ok": None}
fast, calls = trace(lambda: json.dumps(value))
print(f"\njson.dumps(value): {len(calls)} Python-level calls")
for line in calls:
    print("  " + line)
print(f"  the encoding itself ran in C: encoder.c_make_encoder comes from module "
      f"{json.encoder.c_make_encoder.__module__!r}")

# Switch the C accelerator off, as CPython's own tests do, and the Python you were reading runs.
saved, json.encoder.c_make_encoder = json.encoder.c_make_encoder, None
try:
    slow, calls = trace(lambda: json.dumps(value))
finally:
    json.encoder.c_make_encoder = saved
names = sorted({c.strip() for c in calls})
print(f"\nthe same call with the accelerator off: {len(calls)} Python-level calls, "
      f"{len(names)} distinct functions; same output: {slow == fast}")
for line in calls[:8]:
    print("  " + line)
print(f"  ... and {len(calls) - 8} more")
