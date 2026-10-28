import ast, re

# 1. "Go to file": find the files whose paths contain the query's letters in order, best first.
FILES = ["README.md", "pyproject.toml", "src/shop/__init__.py", "src/shop/models/order.py",
         "src/shop/models/data_loader.py", "src/shop/views/menu.py", "src/shop/views/order_detail.py",
         "src/shop/utils/money.py", "tests/test_models.py", "tests/test_order_detail.py", "docs/deploy.md"]

def fuzzy(query, path):
    """The best score for finding the query's letters in order in the path, and where they are.
    A letter scores more at the start of a word, right after the previous match, or in the file name;
    letters skipped between matches cost a little."""
    q, p, n = query.lower(), path.lower(), len(path)
    name_start = path.rfind("/") + 1
    def value(j): return 1 + 8 * (j == 0 or p[j - 1] in "/_-.") + 2 * (j >= name_start)
    best = {}                                          # best[(i, j)]: score with q[i] matched at p[j]
    for i, ch in enumerate(q):
        for j in range(n):
            if p[j] != ch: continue
            if i == 0: best[(i, j)] = (value(j) - 0.1 * j, [j])
            else:
                options = [(s + value(j) + (8 if k == j - 1 else -0.2 * (j - k - 1)), at + [j])
                           for (pi, k), (s, at) in best.items() if pi == i - 1 and k < j]
                if options: best[(i, j)] = max(options)
    finals = [v for (i, _), v in best.items() if i == len(q) - 1]
    return max(finals) if finals else None

def marked(path, at): return "".join(f"[{c}]" if i in at else c for i, c in enumerate(path))

for query in ("mdl", "tmod", "odet", "ord"):
    ranked = sorted(((fuzzy(query, f), f) for f in FILES if fuzzy(query, f)), key=lambda t: -t[0][0])
    print(f"go to file '{query}':")
    for (score, at), f in ranked[:3]: print(f"   {score:5.1f}  {marked(f, at)}")

# 2. Search in files: every line that matches, with its file and line number, like rg or grep -rn
PROJECT = {"src/shop/models/order.py": "class Order:\n    total = 0\n",
           "src/shop/views/menu.py": "def show(menu):\n    # TODO: prices\n    return menu\n",
           "src/shop/utils/money.py": "def cents(x):\n    return round(x * 100)  # TODO: negative?\n"}
print("search for TODO in every file:")
for path, text in sorted(PROJECT.items()):
    for n, line in enumerate(text.splitlines(), 1):
        if re.search(r"TODO", line): print(f"   {path}:{n}: {line.strip()}")

# 3. Rename: text replacement versus a rename that knows what each name refers to
SOURCE = '''def total(items):
    return sum(items)

class Receipt:
    total = 0                              # a different thing with the same name

def report(carts):
    totals = [total(cart) for cart in carts]
    print("total:", total(totals))
'''

def rename_function(source, old, new):
    """Rename the module-level function `old`: its definition, and each use that refers to it."""
    tree = ast.parse(source); spots = []
    def visit(node, shadowed):
        if isinstance(node, ast.FunctionDef) and node.name == old and not shadowed:
            line = source.splitlines()[node.lineno - 1]
            spots.append((node.lineno, line.index(old, node.col_offset)))
        if isinstance(node, ast.Name) and node.id == old and not shadowed:
            spots.append((node.lineno, node.col_offset))
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):      # a name assigned inside is a new thing
            assigned = {t.id for n in ast.walk(node) for t in getattr(n, "targets", [])
                        if isinstance(t, ast.Name)}
            args = {a.arg for a in node.args.args} if isinstance(node, ast.FunctionDef) else set()
            shadowed = shadowed or old in assigned | args
            for child in node.body: visit(child, shadowed)
        else:
            for child in ast.iter_child_nodes(node): visit(child, shadowed)
    for child in tree.body: visit(child, False)
    lines = source.splitlines(keepends=True)
    for row, col in sorted(spots, reverse=True):
        lines[row - 1] = lines[row - 1][:col] + new + lines[row - 1][col + len(old):]
    return "".join(lines)

def changed(before, after):
    return [f"   line {n}: {b.strip()}  ->  {a.strip()}"
            for n, (b, a) in enumerate(zip(before.splitlines(), after.splitlines()), 1) if a != b]

for label, after in (("replace every 'total'", SOURCE.replace("total", "grand_total")),
                     ("replace whole words only, \\btotal\\b", re.sub(r"\btotal\b", "grand_total", SOURCE)),
                     ("rename the function, as an editor's Rename Symbol does",
                      rename_function(SOURCE, "total", "grand_total"))):
    print(f"{label}:"); print("\n".join(changed(SOURCE, after)))
    compile(after, "after.py", "exec")
