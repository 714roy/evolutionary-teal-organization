"""ETO Bootstrap Bundle — 新手一键初始化"""
import json, os, sys
from pathlib import Path

HOME = Path.home()
ETO_DIR = HOME / ".eto"
ETO_MEM_DIR = ETO_DIR / "memory"
ETO_PROFILES_DIR = HOME / ".pi" / "etoprofiles"

def run(force=False):
    steps = []
    ETO_MEM_DIR.mkdir(parents=True, exist_ok=True)
    ETO_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    steps.append({"step": "prepare_dir", "status": "ok"})

    from eto.bootstrap.seed_profiles import init as seed_profiles
    r = seed_profiles(str(ETO_PROFILES_DIR / "profiles.json"), force)
    steps.append(r)

    from eto.bootstrap.seed_sample_skills import init as seed_skills
    r = seed_skills(force)
    steps.append(r)

    config_path = HOME / ".pi" / "eto-config.json"
    if force or not config_path.exists():
        from eto.bootstrap.config_template import make_config
        provider = "deepseek" if os.environ.get("DEEPSEEK_API_KEY") else "ollama"
        config_path.write_text(make_config(provider), "utf-8")
        steps.append({"step": "config", "status": "created", "provider": provider})
    else:
        steps.append({"step": "config", "status": "skipped"})

    return {"status": "bootstrap_complete", "steps": steps}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    result = run(force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
