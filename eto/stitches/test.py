"""Verify all stitcher layers work via stdin pipe (no CLI args)"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
cases = [
    (ROOT / "comms/a2a.py",       {"fn": "execute_plan",    "args": ["task", ["a","b"]]}),
    (ROOT / "consensus/vote.py",  {"fn": "peer_review",     "args": ["plan", ["x","y"]]}),
    (ROOT / "election/raft_lead.py", {"fn": "elect",        "args": [[["r",0.9],["c",0.5]]]}),
]

all_ok = True
for path, payload in cases:
    inp = json.dumps(payload)
    r = subprocess.run([sys.executable, str(path)], input=inp, capture_output=True, text=True, encoding="utf-8", timeout=10)
    ok = r.returncode == 0 and r.stdout.strip()
    print(f"{'✅' if ok else '❌'} {path.name:20s} → {r.stdout.strip()[:60] if ok else r.stderr.strip()[:60]}")
    all_ok = all_ok and ok

sys.exit(0 if all_ok else 1)
