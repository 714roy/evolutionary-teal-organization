"""嵌入路由层 (Phase 2 Layer 1)

用 Ollama embedding 模型（nomic-embed-text）做任务分类，
替代 7B LLM 的三镜分析调用。~50ms，零 VRAM 常驻。
"""

import json
import re
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"

# ── 路由原型句（每个 ROUTE 的代表性任务描述）──
_PROTOTYPES = {
    # gewu（格物）
    "gewu:code": [
        "写一个python脚本读取csv文件",
        "implement a flask rest api",
        "构建一个web应用",
        "refactor this code",
        "写一个hello world程序",
    ],
    "gewu:research": [
        "调研市场上最好的数据库",
        "research the latest ai models",
        "分析分布式系统架构",
        "比较两个技术方案的优劣",
        "搜索相关文献",
    ],
    "gewu:knowledge": [
        "什么是机器学习",
        "explain how tcp works",
        "今天天气怎么样",
        "what is the capital of france",
        "解释量子计算",
    ],
    "gewu:solution": [
        "解决这个生产问题",
        "我需要一个方案来处理高并发",
        "how to fix database connection pool",
        "设计系统架构",
        "处理这个bug",
    ],
    # ROUTE
    "route:direct": [
        "今天天气怎么样",
        "what is python",
        "hello world",
        "how to sort a list",
        "这段代码是什么意思",
    ],
    "route:plan": [
        "写一个flask api",
        "实现用户登录注册功能",
        "调研技术方案并写demo",
        "构建一个全栈项目",
        "写一个自动化测试脚本",
    ],
    "route:consensus": [
        "删除生产数据库",
        "deploy to production",
        "rm -rf /data",
        "支付订单退款",
        "迁移数据库到新服务器",
    ],
}

# ── 预计算原型的嵌入（缓存）──
_cache = {}


def _ollama_embed(texts: list) -> list:
    """调用 Ollama embedding API"""
    data = json.dumps({"model": EMBED_MODEL, "input": texts}).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("embeddings", [])
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return []


def _cosine_sim(a: list, b: list) -> float:
    """余弦相似度"""
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _embed_prototypes():
    """计算所有原型句的嵌入"""
    if _cache:
        return
    all_texts = []
    for key, phrases in _PROTOTYPES.items():
        all_texts.extend(phrases)
    embeddings = _ollama_embed(all_texts)
    if not embeddings:
        return
    idx = 0
    for key, phrases in _PROTOTYPES.items():
        for _ in phrases:
            _cache.setdefault(key, []).append(embeddings[idx])
            idx += 1


def classify(task: str, threshold: float = 0.35) -> dict:
    """嵌入层三镜分类

    返回: {
        "gewu": "code" | "research" | "knowledge" | "solution" | "unknown",
        "ROUTE": "direct" | "plan" | "consensus" | "unknown",
        "confidence": float,
        "explanation": str,
    }
    返回 "unknown" 表示嵌入匹配不可靠，应降级到 LLM。
    """
    task_embeddings = _ollama_embed([task])
    if not task_embeddings:
        return {"gewu": "unknown", "ROUTE": "unknown", "confidence": 0.0, "explanation": "embedding API unavailable, fallback to LLM"}

    task_vec = task_embeddings[0]
    _embed_prototypes()
    if not _cache:
        return {"gewu": "unknown", "ROUTE": "unknown", "confidence": 0.0, "explanation": "prototype embedding failed"}

    # 按 gewu 分组计算最大相似度
    gewu_scores = {}
    for key, vecs in _cache.items():
        cat = key.split(":", 1)[0]
        if cat == "gewu":
            scores = [_cosine_sim(task_vec, v) for v in vecs]
            max_score = max(scores) if scores else 0.0
            label = key.split(":", 1)[1] if ":" in key else key
            gewu_scores[label] = max_score

    # 按 route 分组
    route_scores = {}
    for key, vecs in _cache.items():
        cat = key.split(":", 1)[0]
        if cat == "route":
            scores = [_cosine_sim(task_vec, v) for v in vecs]
            max_score = max(scores) if scores else 0.0
            label = key.split(":", 1)[1] if ":" in key else key
            route_scores[label] = max_score

    best_gewu = max(gewu_scores, key=gewu_scores.get) if gewu_scores else "unknown"
    best_route = max(route_scores, key=route_scores.get) if route_scores else "unknown"
    best_score = max(gewu_scores.get(best_gewu, 0), route_scores.get(best_route, 0))

    return {
        "gewu": best_gewu if best_score >= threshold else "unknown",
        "ROUTE": best_route if best_score >= threshold else "unknown",
        "confidence": round(best_score, 4),
        "explanation": f"embedding match: gewu={best_gewu}({gewu_scores.get(best_gewu,0):.3f}) route={best_route}({route_scores.get(best_route,0):.3f})",
    }
