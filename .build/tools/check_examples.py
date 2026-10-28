# Run each example in a volume's v/ folder twice, plainly and in a hostile environment, and check
# that both runs succeed and print the same thing. Usage: check_examples.py VOL_DIR [chNN_name.py ...]
import os, pathlib, subprocess, sys, tempfile, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); from hostile import hostile_env
V = pathlib.Path(sys.argv[1]).resolve() / "v"
bad = 0
for f in [V / a for a in sys.argv[2:]] or sorted(V.glob("ch*.py")):
    outs = []
    for mode in ("plain", "hostile"):
        root = pathlib.Path(tempfile.mkdtemp(prefix=f"chk-{mode}-"))
        env = dict(os.environ, PYTHONHASHSEED="1") if mode == "plain" else hostile_env(root)
        t = time.time()
        r = subprocess.run([sys.executable, str(f)], capture_output=True, text=True, cwd=root, env=env, timeout=600)
        outs.append((r.returncode, r.stdout, r.stderr, time.time() - t))
    same = outs[0][:2] == outs[1][:2] and outs[0][0] == 0
    bad += not same
    print(f"{f.name:20} {'same' if same else 'DIFFERENT'}  {outs[0][3]:.1f}s / {outs[1][3]:.1f}s")
    if not same:
        a, b = outs[0][1].splitlines(), outs[1][1].splitlines()
        for i in range(max(len(a), len(b))):
            x = a[i] if i < len(a) else None; y = b[i] if i < len(b) else None
            if x != y: print(f"   line {i + 1}\n     plain:   {x!r}\n     hostile: {y!r}"); break
        print("   stderr:", (outs[0][2] + outs[1][2])[-600:])
print("ALL SAME" if not bad else f"{bad} differ")
sys.exit(1 if bad else 0)
