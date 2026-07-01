"""ETO Bootstrap __main__ — pi-bootstrap 入口"""
import sys, json
from pathlib import Path

# Add project root to path so eto.bootstrap is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eto.bootstrap import run

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    result = run(force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
