"""ETO CLI: Agent Profile Editor — 管理 profiles.json"""
import json, sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

PROFILES_PATH = Path(__file__).resolve().parent / "profiles.json"

def _load():
    if not PROFILES_PATH.exists():
        return []
    return json.loads(PROFILES_PATH.read_text("utf-8"))

def _save(profiles):
    PROFILES_PATH.write_text(json.dumps(profiles, ensure_ascii=False, indent=2), "utf-8")
    return {"status": "saved", "count": len(profiles)}

def list_all() -> list:
    return _load()

def get(name: str) -> dict | None:
    for p in _load():
        if p["name"] == name:
            return p
    return None

def update(name: str, **kwargs) -> dict:
    profiles = _load()
    for p in profiles:
        if p["name"] == name:
            p.update(kwargs)
            _save(profiles)
            return {"status": "updated", "profile": p}
    return {"status": "not_found", "name": name}

def delete(name: str) -> dict:
    profiles = _load()
    new = [p for p in profiles if p["name"] != name]
    if len(new) == len(profiles):
        return {"status": "not_found", "name": name}
    _save(new)
    return {"status": "deleted", "name": name}

def validate() -> dict:
    profiles = _load()
    errors = []
    for i, p in enumerate(profiles):
        if "name" not in p:
            errors.append(f"[{i}] missing 'name'")
        if "weights" not in p:
            errors.append(f"[{i}] missing 'weights'")
        if "maxSubtasks" not in p:
            errors.append(f"[{i}] missing 'maxSubtasks'")
    return {"valid": len(errors) == 0, "count": len(profiles), "errors": errors}

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if not args or args[0] in ("help", "--help", "-h"):
        print("Usage: profile_editor.py <command> [args]")
        print("Commands:")
        print("  list                    List all profiles")
        print("  get <name>             Get profile by name")
        print("  update <name> key=val  Update profile field")
        print("  delete <name>          Delete profile")
        print("  validate               Validate profiles.json")
        sys.exit(0)
    cmd = args[0]
    if cmd == "list":
        print(json.dumps(_load(), ensure_ascii=False, indent=2))
    elif cmd == "get" and len(args) >= 2:
        r = get(args[1])
        print(json.dumps(r, ensure_ascii=False, indent=2) if r else "not found")
    elif cmd == "update" and len(args) >= 3:
        kwargs = {}
        for kv in args[2:]:
            k, v = kv.split("=", 1)
            try: v = json.loads(v)
            except: pass
            kwargs[k] = v
        print(json.dumps(update(args[1], **kwargs), ensure_ascii=False))
    elif cmd == "delete" and len(args) >= 2:
        print(json.dumps(delete(args[1]), ensure_ascii=False))
    elif cmd == "validate":
        print(json.dumps(validate(), ensure_ascii=False))
    else:
        print("Unknown command. Use: help")
