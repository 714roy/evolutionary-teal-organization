"""ETO Stitch: raft-lite 协调员选举"""
import json, sys

def elect(candidates: list) -> dict:
    if not candidates:
        return {"leader": "researcher"}
    candidates.sort(key=lambda x: x[1], reverse=True)
    return {"leader": candidates[0][0], "all": candidates}

if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    fn = globals().get(data["fn"])
    if fn:
        result = fn(*data.get("args", []))
        print(json.dumps(result, ensure_ascii=False))
