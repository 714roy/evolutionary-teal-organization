"""临时协调员选举 (ETO-011/012)

选举公式: match_score × (1 - busy_ratio)
- match_score: Jaccard 关键词重叠 + keyword dispatch + term frequency
- busy_ratio: 未完成任务数 / max_concurrency
"""

import re
import math

# ── Agent 关键词映射 ──────────────────────────────
#   任务中的动词/名词 → 匹配哪个 agent 的专长
_KEYWORD_MAP = {
    "coder": {
        "write", "code", "implement", "build", "create", "refactor", "debug",
        "fix", "patch", "commit", "compile", "deploy", "test",
        "function", "class", "script", "program", "app", "api", "cli",
        "写", "编码", "代码", "编程", "实现", "构建", "创建", "修改",
        "重构", "调试", "开发", "部署", "提交",
    },
    "researcher": {
        "research", "investigate", "analyze", "find", "search", "study",
        "report", "survey", "compare", "explain", "summarize",
        "文献", "调研", "研究", "分析", "对比", "报告", "总结", "搜索",
        "评估", "调查", "信息",
    },
    "auditor": {
        "review", "audit", "inspect", "verify", "check", "validate",
        "security", "quality", "compliance", "safe",
        "delete", "remove", "drop", "destroy", "production", "prod",
        "diagnose", "failover", "rollback",
        "审查", "审计", "检查", "验证", "安全", "合规", "质量", "审核",
        "校验", "评审", "删除", "移除", "销毁", "生产", "部署",
    },
}


def _keyword_hits(agent_id: str, task: str) -> int:
    """关键词命中数：任务中出现了多少该 agent 的关键词"""
    task_lower = task.lower()
    keywords = _KEYWORD_MAP.get(agent_id, set())
    return sum(1 for kw in keywords if kw in task_lower)


def _tokenize(text: str) -> set:
    """分词：英文单词 + 英文 bigram + 中文双字词组"""
    text = text.lower()
    tokens = set()
    # 英文/数字单词
    for w in re.findall(r"[a-zA-Z0-9_]+", text):
        if len(w) >= 2:
            tokens.add(w)
    # 英文双词组（帮助 "data analysis" 匹配 "analysis"）
    words = re.findall(r"[a-zA-Z]+", text)
    for i in range(len(words) - 1):
        if len(words[i]) >= 2 and len(words[i + 1]) >= 2:
            tokens.add(f"{words[i]} {words[i+1]}")
    # 中文双字词组
    chars = re.findall(r"[一-鿿]", text)
    for i in range(len(chars) - 1):
        tokens.add(chars[i] + chars[i + 1])
    return tokens


def compute_match_score(specialty: str, task: str) -> float:
    """Jaccard 关键词重叠（原始函数，保留兼容性）"""
    spec_tokens = _tokenize(specialty)
    task_tokens = _tokenize(task)
    if not spec_tokens or not task_tokens:
        return 0.0
    inter = spec_tokens & task_tokens
    union = spec_tokens | task_tokens
    return len(inter) / len(union) if union else 0.0


def compute_agent_match(agent_id: str, specialty: str, task: str, agents: dict) -> float:
    """综合评分：Jaccard (30%) + keyword dispatch (45%) + TF (25%)

    三层互补：
    - Jaccard: 专长和任务字面重叠
    - keyword dispatch: 任务关键词分类命中（"write" → coder 即使 Jaccard=0）
    - TF: 专长描述词在任务中的覆盖率
    """
    base = compute_match_score(specialty, task)

    # dispatch 层
    hits = _keyword_hits(agent_id, task)
    all_hits = [_keyword_hits(aid, task) for aid in agents]
    max_hits = max(all_hits) if all_hits else 0
    kw_norm = hits / max_hits if max_hits > 0 else 0.0

    # TF 层
    task_lower = task.lower()
    spec_lower = specialty.lower()
    task_words = set(re.findall(r"[a-zA-Z0-9_]+", task_lower))
    spec_words = set(re.findall(r"[a-zA-Z0-9_]+", spec_lower))
    # 中文 char overlap
    task_chars = set(re.findall(r"[一-鿿]", task_lower))
    spec_chars = set(re.findall(r"[一-鿿]", spec_lower))
    total_words = task_words | task_chars
    overlap_words = (task_words & spec_words) | (task_chars & spec_chars)
    tf = len(overlap_words) / len(total_words) if total_words else 0.0

    return round(0.30 * base + 0.45 * kw_norm + 0.25 * tf, 3)


def compute_busy_ratio(agent_id: str, agents: dict, ctx) -> float:
    """Agent 当前负载 = 未完成任务数 / max_concurrency

    参数 agents 由调用方传入（与主循环共享同一份 agent 池），
    不再旁路读取 agents.yaml，避免双状态源不一致（审计发现 #1）。
    """
    ctx_data = ctx.data if hasattr(ctx, 'data') else {}
    active = ctx_data.get("active_proposals", [])

    busy_count = 0
    for prop in active:
        if prop.get("proposer") == agent_id:
            busy_count += 1
        plan = prop.get("plan", {})
        for step in plan.get("steps", []):
            if step.get("assigned_to") == agent_id:
                busy_count += 1

    config = agents.get(agent_id, {})
    max_conc = config.get("max_concurrency", 3)

    ratio = busy_count / max_conc
    return min(ratio, 1.0)


def elect_temporary_lead(agents: dict, task: str, ctx):
    """按综合评分 × (1 - busy_ratio) 选举临时协调员"""
    best = None
    best_score = -1.0
    scores = {}

    for agent_id, config in agents.items():
        specialty = config.get("specialty", "")
        match = compute_agent_match(agent_id, specialty, task, agents)
        busy = compute_busy_ratio(agent_id, agents, ctx)
        score = match * (1.0 - busy)
        scores[agent_id] = {"match": round(match, 3), "busy": round(busy, 3), "final": round(score, 3)}

        if score > best_score:
            best_score = score
            best = (agent_id, config)

    # 全零保底
    if best_score <= 0 and agents:
        best = (list(agents.keys())[0], list(agents.values())[0])

    return best, scores
