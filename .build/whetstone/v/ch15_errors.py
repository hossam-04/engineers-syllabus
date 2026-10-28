import random, traceback

def average_prices(text):
    """The average price in each category of a menu, from lines like '[drinks]' and 'tea 2.50'."""
    result, category, prices = {}, None, []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        if line.startswith("["):
            if category is not None:
                result[category] = average(prices)
            category, prices = line.strip("[]"), []
        else:
            name, price = line.rsplit(" ", 1)
            prices.append(float(price))
    if category is not None and prices:
        result[category] = average(prices)
    return result

def average(numbers): return round(sum(numbers) / len(numbers), 2)

def make_menu():
    """A menu of about a hundred lines; one category, part-way down, has nothing in it yet."""
    rng = random.Random(15); lines = ["# The Corner Cafe menu"]
    for category in ["breakfast", "soups", "salads", "mains", "specials", "sides", "cakes",
                     "ice cream", "tea", "coffee", "juice", "wine"]:
        lines += ["", f"[{category}]"]
        if category == "specials": lines.append("# coming soon"); continue
        lines += [f"{category} item {i} {rng.randint(150, 1800) / 100:.2f}" for i in range(1, 8)]
    return lines + ["# prices include service"]

menu = make_menu()
print(f"1. The program fails on the real menu, {len(menu)} lines long")
try:
    average_prices("\n".join(menu))
except Exception as error:
    frames = traceback.extract_tb(error.__traceback__)
    print(f"   the last line of the traceback says what went wrong: {type(error).__name__}: {error}")
    print("   the lines above it say where; from the bottom up, the innermost call first:")
    for f in reversed(frames):
        name = f.name if f.name.startswith("<") else f.name + "()"
        print(f"      line {f.lineno:2} in {name:16} {f.line}")

def fails(lines):
    try: average_prices("\n".join(lines)); return False
    except ZeroDivisionError: return True

def shrink(lines, fails):
    """Delta debugging (Zeller, 2002): keep dropping chunks of the input while it still fails."""
    n, tests, sizes = 2, 0, [len(lines)]
    while len(lines) >= 2:
        size = -(-len(lines) // n)
        chunks = [lines[i:i + size] for i in range(0, len(lines), size)]
        for i in range(len(chunks)):
            rest = [line for j, c in enumerate(chunks) if j != i for line in c]
            tests += 1
            if fails(rest):
                lines, n = rest, max(n - 1, 2); sizes.append(len(lines)); break
        else:
            if n >= len(lines): break
            n = min(2 * n, len(lines))
    return lines, tests, sizes

print("2. Shrinking the input automatically, keeping only what's needed to fail")
small, tests, sizes = shrink(menu, fails)
print(f"   {tests} test runs; the failing input went from {' -> '.join(map(str, sizes))} lines:")
for line in small: print(f"      {line}")
print(f"   with the first line alone it works: {not fails(small[:1])}; "
      f"with the second alone: {not fails(small[1:])}")

print("3. The bug report this makes possible")
print(f"""   average_prices() raises ZeroDivisionError when a category has no items and another follows.
   To reproduce:  average_prices("{small[0]}\\n{small[1]}")
   Expected:      {{}} or {{'{small[0].strip('[]')}': None}}, not a crash
   Actually:      ZeroDivisionError: division by zero, in average(), called from line 11
   Tried:         the same with an empty category at the end of the menu works""")
