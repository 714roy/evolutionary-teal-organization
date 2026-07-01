"""ETO Stitch: Metrics — 路由/Agent 统计"""
import io, json, os, sys, time
from collections import Counter, defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

MEMORY_DIR = Path.home() / ".eto" / "memory"
METRICS_FILE = MEMORY_DIR / "metrics.jsonl"

def _ensure():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def write(route: str, agent: str, success: bool, steps: int = 0, duration: float = 0.0) -> dict:
    _ensure()
    entry = {
        "route": route, "agent": agent, "success": success,
        "steps": steps, "duration": round(duration, 2),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

def load_all() -> list:
    if not METRICS_FILE.exists():
        return []
    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def summary() -> dict:
    records = load_all()
    if not records:
        return {"total": 0}
    route_dist = Counter(r.get("route", "?") for r in records)
    agent_success = defaultdict(lambda: {"ok": 0, "fail": 0})
    for r in records:
        a = r.get("agent", "?")
        if r.get("success"):
            agent_success[a]["ok"] += 1
        else:
            agent_success[a]["fail"] += 1
    total_ok = sum(1 for r in records if r.get("success"))
    return {
        "total": len(records),
        "success_rate": round(total_ok / len(records), 2),
        "route_distribution": dict(route_dist),
        "agent_success": {a: s for a, s in sorted(agent_success.items())},
    }

if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    fn = data.get("fn")
    args = data.get("args", [])
    func = globals().get(fn)
    if func:
        result = func(*args)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({"_error": True, "message": f"unknown fn: {fn}"}))
