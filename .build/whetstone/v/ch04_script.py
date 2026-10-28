import os, pathlib, shutil, subprocess, tempfile

TIDY = r'''#!/usr/bin/env bash
# tidy: sort the files at the top of a folder into subfolders by type. Safe to run again.
set -euo pipefail

usage() { echo "usage: tidy [-n] FOLDER    -n: only show what would move"; }

dry_run=false
while getopts "nh" opt; do
  case "$opt" in
    n) dry_run=true ;;
    h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
[ "$#" -eq 1 ] || { usage >&2; exit 2; }
folder=${1%/}
[ -d "$folder" ] || { echo "tidy: no such folder: $folder" >&2; exit 1; }

# mkdir is atomic, so only one run can hold the lock; the trap removes it however the script ends
lock="$folder/.tidy.lock"
mkdir "$lock" 2> /dev/null || { echo "tidy: already running on $folder" >&2; exit 1; }
trap 'rmdir "$lock"' EXIT

category() {
  local ext
  ext=$(printf '%s' "${1##*.}" | tr '[:upper:]' '[:lower:]')
  case "$ext" in
    jpg|jpeg|png|gif|heic) echo images ;;
    pdf|doc|docx|txt|md|csv) echo documents ;;
    zip|tar|gz|dmg) echo archives ;;
    *) echo other ;;
  esac
}

free_name() {   # $2, or "$2 (1)", "$2 (2)"... whichever doesn't exist yet in folder $1
  local dir=$1 name=$2 base ext n=1 candidate=$2
  if [[ $name == ?*.* ]]; then base=${name%.*} ext=.${name##*.}; else base=$name ext=; fi
  while [ -e "$dir/$candidate" ]; do candidate="$base ($n)$ext"; n=$((n + 1)); done
  printf '%s\n' "$candidate"
}

count=0
for path in "$folder"/*; do
  [ -f "$path" ] || continue          # skip folders, and the unexpanded * of an empty folder
  name=${path##*/}
  dest=$(category "$name")
  target=$(free_name "$folder/$dest" "$name")
  if $dry_run; then
    echo "would move: $name -> $dest/$target"
  else
    mkdir -p "$folder/$dest"
    mv -n "$path" "$folder/$dest/$target"
    echo "moved: $name -> $dest/$target"
  fi
  count=$((count + 1))
done
[ "$count" -gt 0 ] || echo "nothing to tidy in $folder"
'''

def run(cmd, cwd, env):
    r = subprocess.run([shutil.which("bash"), "--norc", "--noprofile", "-c", cmd], cwd=cwd, env=env,
                       capture_output=True, text=True)
    print(f"$ {cmd}")
    for line in r.stdout.splitlines(): print(f"   {line}")
    for line in r.stderr.splitlines(): print(f"   (stderr) {line}")
    if r.returncode: print(f"   (exit status {r.returncode})")

def tree(folder):
    for p in sorted(folder.rglob("*")):
        if p.is_file(): print(f"   {p.relative_to(folder.parent)}")

with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp); (root / "bin").mkdir()
    script = root / "bin" / "tidy"; script.write_text(TIDY); script.chmod(0o755)
    downloads = root / "Downloads"
    for name in ["Holiday 2025.JPG", "invoice-0423.pdf", "report.pdf", "notes.txt", "photo.png",
                 "backup.tar.gz", "Makefile", "documents/report.pdf", "projects/plan.md"]:
        p = downloads / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(name)
    env = {"PATH": f"{root / 'bin'}:{os.environ['PATH']}", "HOME": "/home/learner", "LC_ALL": "C"}

    run("tidy", root, env)
    run("tidy -n Downloads", root, env)
    run("tidy Downloads/", root, env)
    print("After one run:"); tree(downloads)
    run("tidy Downloads", root, env)
    run("tidy Nowhere", root, env)
    run('mkdir Downloads/.tidy.lock; tidy Downloads || echo "refused, status $?"; '
        'rmdir Downloads/.tidy.lock', root, env)
    kept = (downloads / "documents/report.pdf").read_text() == "documents/report.pdf"
    print(f"no lock left behind: {not (downloads / '.tidy.lock').exists()}; "
          f"the report already in documents/ is untouched: {kept}")
