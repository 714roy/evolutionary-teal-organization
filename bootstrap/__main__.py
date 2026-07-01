"""__main__ entry — python3 -m bootstrap 支持"""
import argparse
import json
import sys
from pathlib import Path

# Ensure current dir is on path for package resolution
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bootstrap import run as bootstrap_run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETO Bootstrap Bundle")
    parser.add_argument("--force", action="store_true", help="Force overwrite")
    args = parser.parse_args()
    result = bootstrap_run(force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
