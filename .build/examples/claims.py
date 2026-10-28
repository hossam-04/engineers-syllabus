# Evaluate each top-level expression whose comment states its result, and print both side by side.
# Usage: claims.py ID ...
import ast, json, subprocess, sys, tempfile, pathlib
B = {b["id"]: b for b in json.load(open(pathlib.Path(__file__).parent / "blocks.json"))}
for i in sys.argv[1:]:
    src = B[i]["text"]; lines = src.split("\n"); out = []
    for node in ast.parse(src).body:
        first = min([node.lineno] + [x.lineno for x in getattr(node, "decorator_list", [])])
        seg = "\n".join(lines[first - 1:node.end_lineno])
        if isinstance(node, ast.Expr) and not isinstance(node.value, ast.Constant) and \
           not (isinstance(node.value, ast.Call) and getattr(node.value.func, "id", None) == "print"):
            comment = lines[node.end_lineno - 1][node.end_col_offset:].strip()
            if comment.startswith("#"):
                seg = f"__v = ({ast.get_source_segment(src, node.value)})\nprint('  =>', repr(__v)[:200], '   ', {comment!r})"
        out.append(seg)
    d = pathlib.Path(tempfile.mkdtemp()); (d / "x.py").write_text("\n".join(out) + "\n")
    r = subprocess.run([sys.executable, "x.py"], cwd=d, capture_output=True, text=True, timeout=300)
    print("###", i, B[i]["cap"]); print(r.stdout.rstrip())
    if r.returncode: print(r.stderr[-400:])
