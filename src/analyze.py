"""三镜分析 (ETO-002) + ROUTE 分流 (ETO-005)

三层路由（Phase 2 两层架构实现）：
  Layer 0: 关键词启发式（纳秒级，覆盖高风险/典型任务）
  Layer 1: 嵌入分类器（~50ms，nomic-embed-text，替代原 7B LLM 路由调用）
  Layer 2: LLM 三镜分析（~5s，仅当嵌入置信度低时降级）
"""
import json, re, sys
from executor import call_pi_json, call_pi

# 三镜 prompt 化简为本地模型能跟上的格式
SYSTEM_PROMPT_SANJING = """分析用户任务，输出JSON分类结果。

三镜框架：
1. gewu（格物）: product=产品方案, solution=问题解决, research=调研, code=编码, knowledge=知识问答
2. xili（析理）: self=给自己, team=给团队, client=给客户, system=系统任务
3. heyan（合验）: standard=标准方案, custom=定制方案, innovative=创新方案

路由规则（ROUTE）:
- direct: 简单问答/单步查询 → 直接回答
- plan: 多步骤/编码/设计任务 → 需要计划
- consensus: 高风险操作/争议决策 → 需要同侪共识

只输出JSON，不要其他文字：
{"three_mirrors":{"gewu":"code","xili":"self","heyan":"standard"},"ROUTE":"plan","explanation":"简短说明"}"""


def _map_gewu_route(gewu: str, route: str, conf: float, layer: str = "keyword") -> str:
    """将 gewu + route 映射为完整三镜输出"""
    xili_map = {
        "code": "self", "research": "self",
        "knowledge": "self", "solution": "team",
    }
    heyan_map = {
        "code": "custom", "research": "standard",
        "knowledge": "standard", "solution": "standard",
    }
    return {
        "three_mirrors": {
            "gewu": gewu,
            "xili": xili_map.get(gewu, "self"),
            "heyan": heyan_map.get(gewu, "standard"),
        },
        "ROUTE": route if route in ("direct", "plan", "consensus") else "plan",
        "explanation": f"{layer} (gewu={gewu}, route={route}, conf={conf})",
        "weights": {"fact": 0.4, "logic": 0.3, "aesthetic": 0.3},
    }


def analyze(task: str) -> dict:
    """三镜分析入口 (ETO-002) — 三层路由"""
    task_s = task.strip()
    task_lower = task_s.lower()

    # ── Layer 0: 关键词启发式（纳秒级）──
    # 高风险操作 → 共识
    consensus_keywords_en = [
        "delete", "remove", "destroy", "drop", "erase",
        "deploy", "rollback", "migrate",
        "pay", "buy", "purchase", "charge", "price",
    ]
    consensus_keywords_cn = [
        "删除", "移除", "销毁", "部署", "生产", "回滚", "迁移",
        "支付", "购买", "扣费", "定价",
    ]
    import re as _re
    # 英文用 \b 边界，防止 "rm" 搜到 "transformer"
    if any(_re.search(r'\b' + _re.escape(kw) + r'\b', task_lower) for kw in consensus_keywords_en):
        return _map_gewu_route("solution", "consensus", 1.0)
    # 中文用直接子串匹配（多字符中文误触发概率极低）
    if any(kw in task_s for kw in consensus_keywords_cn):
        return _map_gewu_route("solution", "consensus", 1.0)
    # 短高风险命令（如 rm -rf）不适用单词边界
    short_risk = ["rm -rf", "rm -r", "rm -f", "rm -fr", "rm /", "rmdir /"]
    if any(kw in task_lower for kw in short_risk):
        return _map_gewu_route("solution", "consensus", 1.0)

    # ── Layer 1: LLM 语义路由（~500ms，主路由层）──
    # 7B 模型理解语义，正确区分"研究" vs "问答" vs "编码"
    try:
        from router import route as _llm_route
        _llm_result = _llm_route(task)
        if _llm_result and _llm_result["confidence"] >= 0.3:
            return _map_gewu_route(
                _llm_result["gewu"], _llm_result["ROUTE"], _llm_result["confidence"], layer="llm")
    except Exception:
        pass  # router 不可用 → 降级

    # ── Layer 2: 关键词快速兜底（仅当 LLM 路由失败时）──
    # 定义/解释类 → direct
    _def_kw = ["什么是", "是什么", "what is", "what are", "explain", "define"]
    if any(kw in task_lower for kw in _def_kw):
        return _map_gewu_route("knowledge", "direct", 0.95, layer="keyword")
    # 编码/调研/报告 → plan
    _plan_kw = ["写", "代码", "实现", "重构", "报告", "调研", "研究", "分析", "调查",
                "write", "code", "implement", "refactor", "create", "build"]
    if any(kw in task_s for kw in _plan_kw):
        gewu = "research" if any(kw in task_s for kw in ["报告", "调研", "研究"]) else "code"
        return _map_gewu_route(gewu, "plan", 0.85, layer="keyword")
    # 简短英文 / 中文问候 → direct
    if len(task_s.split()) <= 5 and len(task_s) < 40:
        return _map_gewu_route("knowledge", "direct", 0.8, layer="keyword")

    # ── Layer 4: 嵌入分类器（~50ms）──
    # 替代原 7B LLM 的三镜分析调用。embedding 模型常驻，零加载耗时
    try:
        from embedding import classify
        emb = classify(task)
        if emb["ROUTE"] != "unknown" and emb["confidence"] >= 0.35:
            return _map_gewu_route(emb["gewu"], emb["ROUTE"], emb["confidence"], layer="embedding")
    except Exception:
        pass  # embedding API 不可用 → 降级到 LLM

    # ── Layer 5: LLM 三镜分析（~5s，仅当嵌入置信度不足时到达）──
    prompt = f"任务：{task}\n\n分析并输出JSON分类。"
    result = call_pi_json(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT_SANJING,
        timeout=60,
        retry=1,
    )
    if isinstance(result, dict) and result.get("ROUTE") in ("direct", "plan", "consensus"):
        return result

    # ── 最终保底 ──
    return {
        "three_mirrors": {"gewu": "unknown", "xili": "unknown", "heyan": "unknown"},
        "ROUTE": "plan",
        "explanation": "all layers failed, default to plan",
        "weights": {"fact": 0.3, "logic": 0.4, "aesthetic": 0.3},
    }


def route(analysis: dict) -> str:
    """从三镜分析结果提取 ROUTE (ETO-005)"""
    r = analysis.get("ROUTE", "plan")
    return r if r in ("direct", "plan", "consensus") else "plan"
