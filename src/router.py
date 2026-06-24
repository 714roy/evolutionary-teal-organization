"""语义路由分拣器（替代关键词启发式 Layer 0）

用 LLM 理解任务语义，直接输出 ROUTE + gewu。
不再依赖关键词子串匹配（fix: "rm" 匹配 "transformer" 类 bug）。

Ollama API 直调，无需 Pi CLI 开销。
"""

import json
import re
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5-coder:7b"

# 容错映射：模型可能的英文输出 → 标准值
GEWU_MAP = {
    "knowledge": "knowledge", "question": "knowledge", "definition": "knowledge",
    "code": "code", "coding": "code", "programming": "code",
    "implement": "code", "refactor": "code", "build": "code",
    "research": "research", "study": "research", "analysis": "research",
    "solution": "solution", "problem": "solution", "design": "solution",
}
ROUTE_MAP = {
    "direct": "direct", "simple": "direct",
    "plan": "plan", "multi_step": "plan",
    "consensus": "consensus", "highrisk": "consensus",
}

SYSTEM = (
    "Classify. Output a JSON object with gewu, ROUTE, confidence.\n"
    "gewu: knowledge | code | research | solution\n"
    "ROUTE: direct (simple Q&A only) | plan (anything multi-step) | consensus (high-risk)\n\n"
    "Rules:\n"
    "- direct: ONLY for simple questions, definitions, weather, facts. Single-sentence answer.\n"
    "- plan: ANY coding work (write/implement/refactor/build), research (research/analyze/investigate), report writing.\n"
    "- consensus: delete, deploy to production, pay, destroy, any destructive operation.\n\n"
    "Examples:\n"
    '{"gewu":"knowledge","ROUTE":"direct","confidence":0.95}  # "what is weather"\n'
    '{"gewu":"code","ROUTE":"plan","confidence":0.95}          # "write flask api"\n'
    '{"gewu":"research","ROUTE":"plan","confidence":0.85}      # "research AI safety"\n'
    '{"gewu":"solution","ROUTE":"consensus","confidence":0.95} # "delete database"'
)


def _extract_json(text: str) -> dict | None:
    """从模型输出提取 JSON（支持代码块、裸 JSON、截断 JSON）"""
    for m in re.finditer(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL):
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    return None


def route(task: str) -> dict | None:
    """调用 LLM 路由。返回 None → 降级到嵌入"""
    data = json.dumps({
        "model": MODEL, "system": SYSTEM, "prompt": task,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 256},
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate", data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read().decode("utf-8")).get("response", "").strip()
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None

    parsed = _extract_json(raw)
    if not parsed:
        return None

    gewu = GEWU_MAP.get(str(parsed.get("gewu", "")).lower())
    rval = ROUTE_MAP.get(str(parsed.get("ROUTE", "")).lower())
    conf = parsed.get("confidence", 0.5)
    if not isinstance(conf, (int, float)):
        conf = 0.5
    return {
        "gewu": gewu or "code",
        "ROUTE": rval or "plan",
        "confidence": min(max(conf, 0), 1),
    }
