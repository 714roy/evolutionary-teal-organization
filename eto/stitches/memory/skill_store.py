"""ETO Stitch: Skill Memory — JSONL 持久化"""
import io, json, os, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

MEMORY_DIR = Path.home() / ".eto" / "memory"
SKILLS_FILE = MEMORY_DIR / "skills.jsonl"

def _ensure():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def append(name: str, context: str, reward: float = 0.5, source: str = "") -> dict:
    _ensure()
    entry = {
        "skill_name": name, "context": context, "reward": reward,
        "source": source, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    with open(SKILLS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

def load(min_reward: float = 0.0) -> list:
    if not SKILLS_FILE.exists():
        return []
    with open(SKILLS_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()
                and json.loads(line).get("reward", 0) >= min_reward]

def scan(query: str = "") -> list:
    all_skills = load()
    if not query:
        return all_skills
    q = query.lower()
    return [s for s in all_skills if q in s.get("context", "").lower()
            or q in s.get("skill_name", "").lower()]

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
