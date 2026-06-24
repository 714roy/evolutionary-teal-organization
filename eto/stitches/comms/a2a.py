"""ETO Stitch: 多步任务执行层（Step 3 - 真实 LLM 执行 + 上下文传递）"""
import json, sys, urllib.request, urllib.error, time

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5-coder:7b"

def _call_llm(prompt: str, timeout: int = 60) -> str:
    """调 Ollama 生成回复"""
    data = json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1024},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate", data=data,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8")).get("response", "").strip()

def execute_plan(task: str, steps: list[str]) -> dict:
    """执行多步计划，每步注入上一步输出作为上下文"""
    outputs = []
    context = ""
    total = len(steps)

    for i, step in enumerate(steps, 1):
        prompt = f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n总体任务: {task}\n"
        if context:
            prompt += f"\n上一步结果:\n{context}\n\n"
        prompt += f"当前步骤({i}/{total}): {step}\n请执行并输出结果。"
        try:
            result = _call_llm(prompt)
        except Exception as e:
            result = f"<步骤执行失败: {e}>"
        outputs.append(result)
        context = result[:500]  # 向下文传递上一步摘要

    return {"outputs": outputs, "total": total}

if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    fn = globals().get(data["fn"])
    if fn:
        result = fn(*data.get("args", []))
        print(json.dumps(result, ensure_ascii=False))
