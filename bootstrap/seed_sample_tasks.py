"""种子示例任务 — 2 条演示数据（is_seed 标记，可清理）"""
import json
from pathlib import Path

SEED = [
    {
        "task": "写一个 Flask REST API",
        "result": "已创建 app.py, routes/users.py",
        "route": "plan",
        "agent": "coder",
        "is_seed": True,
    },
    {
        "task": "调研 Rust vs Go 在微服务中的性能表现",
        "result": "已完成调研报告",
        "route": "consensus",
        "agent": "researcher",
        "is_seed": True,
    },
]


def init(force: bool = False) -> dict:
    p = Path.home() / ".eto" / "memory" / "sample_tasks.json"
    if p.exists() and not force:
        return {"step": "tasks", "status": "skipped"}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(SEED, ensure_ascii=False, indent=2), "utf-8")
    return {"step": "tasks", "status": "ok", "count": len(SEED)}
