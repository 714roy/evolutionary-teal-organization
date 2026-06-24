"""ETO API Server — OpenAI-compatible /v1/chat/completions
CodeWhale (DeepSeek TUI) 调这个 API，我们的 ETO 核心循环处理请求
"""
import sys, os, json, threading, time
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import main as core_main

app = Flask(__name__)


def extract(buf):
    skip = ["ROUTE=", "Coordinator:", "Steps:", "Time:", "Agents:", "Analyzing",
            "Electing", "score=", "consensus", "approved", "failed", "Action",
            "vote", "Executing", "Drafting", "Step ", "Core Loop", "Task:",
            "--------", "========", "| ", "T- ", "L ", "Done"]
    c = [l.strip() for l in buf if l.strip() and len(l.strip()) > 5 and not any(k in l for k in skip)]
    return "\n".join(c[-10:]) if c else "(no output)"

def run_eto(task):
    """运行 ETO 核心循环，返回结果"""
    buf = []
    old_out, old_argv = sys.stdout, sys.argv
    class Cap:
        def __init__(self, b):
            self.b = b
        def write(self, t):
            if t is not None:
                self.b.append(t)
        def flush(self):
            pass
    sys.stdout = Cap(buf)
    sys.argv = ["eto", task]
    try:
        core_main()
    except SystemExit:
        pass
    except Exception as e:
        buf.append(str(e))
    finally:
        sys.stdout, sys.argv = old_out, old_argv
    return extract(buf)


@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    
    # 提取最后一条用户消息
    task = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            task = msg.get("content", "")
            break
    
    if not task:
        return jsonify({"error": "no user message"}), 400
    
    # 运行 ETO 核心循环
    answer = run_eto(task)
    
    # OpenAI 格式返回
    return jsonify({
        "id": "chatcmpl-eto-" + str(int(time.time())),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "eto-core-loop",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": answer,
            },
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": len(task),
            "completion_tokens": len(answer),
            "total_tokens": len(task) + len(answer),
        }
    })


@app.route("/v1/models", methods=["GET"])
def models():
    return jsonify({
        "object": "list",
        "data": [{
            "id": "eto-core-loop",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "eto",
        }]
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("ETO_API_PORT", 11435))
    print(f"ETO API Server running on http://localhost:{port}")
    print("Configure CodeWhale with:")
    print(f"  provider = \"openai\"")
    print(f"  CODEWHALE_BASE_URL=http://localhost:{port}")
    print(f"  CODEWHALE_MODEL=eto-core-loop")
    app.run(host="127.0.0.1", port=port, debug=False)
