"""种子 Agent Profile，首次安装时写入 profiles.json"""
import json
from pathlib import Path

SEED = [
    {
        "name": "researcher",
        "label": "研究员",
        "specialty": "research",
        "description": "信息收集、深度分析、整理报告",
        "weights": {"knowledge": 0.9, "research": 0.95, "code": 0.2, "solution": 0.3},
        "maxSubtasks": 2,
    },
    {
        "name": "coder",
        "label": "编码员",
        "specialty": "code",
        "description": "编写代码、重构、调试",
        "weights": {"knowledge": 0.3, "research": 0.2, "code": 0.95, "solution": 0.5},
        "maxSubtasks": 3,
    },
    {
        "name": "auditor",
        "label": "审计员",
        "specialty": "solution",
        "description": "风险评估、共识审批、质量审查",
        "weights": {"knowledge": 0.5, "research": 0.4, "code": 0.4, "solution": 0.9},
        "maxSubtasks": 1,
    },
]


def init(path: str = None, force: bool = False) -> dict:
    p = Path(path) if path else Path.home() / ".pi" / "etoprofiles" / "profiles.json"
    if p.exists() and not force:
        return {"step": "profiles", "status": "skipped"}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(SEED, ensure_ascii=False, indent=2), "utf-8")
    return {"step": "profiles", "status": "ok", "count": len(SEED)}
