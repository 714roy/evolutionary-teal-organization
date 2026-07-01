"""种子经验数据 — 5 条典型 Skill Entry"""
import json
from pathlib import Path

SEED = [
    {
        "skill_name": "dependency-circuit-breaker",
        "context": "外部调用必须加熔断，避免级联失败",
        "reward": 0.95,
        "source": "bootstrap",
    },
    {
        "skill_name": "empty-state-handling",
        "context": "空列表状态需有友好提示，不直接渲染空白",
        "reward": 0.85,
        "source": "bootstrap",
    },
    {
        "skill_name": "config-first-pattern",
        "context": "配置项必须从文件读取而非硬编码",
        "reward": 0.80,
        "source": "bootstrap",
    },
    {
        "skill_name": "keyword-fallback-safe",
        "context": "LLM 路由不可用时，关键词匹配必须有兜底默认值",
        "reward": 0.75,
        "source": "bootstrap",
    },
    {
        "skill_name": "graceful-degradation",
        "context": "任何外部依赖失败都应回退到安全模式，不能 crash",
        "reward": 0.90,
        "source": "bootstrap",
    },
]


def init(force: bool = False) -> dict:
    p = Path.home() / ".eto" / "memory" / "skills.jsonl"
    if p.exists() and not force:
        return {"step": "skills", "status": "skipped"}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "\n".join(json.dumps(s, ensure_ascii=False) for s in SEED) + "\n",
        "utf-8",
    )
    return {"step": "skills", "status": "ok", "count": len(SEED)}
