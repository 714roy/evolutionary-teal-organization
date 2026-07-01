"""ETO Config 模板"""
import json

def make_config(default_provider: str) -> str:
    return json.dumps({
        "router": {
            "provider": default_provider,
            "models": {
                "deepseek": {"url": "https://api.deepseek.com/v1/chat/completions", "model": "deepseek-chat"},
                "ollama": {"url": "http://localhost:11434/api/chat", "model": "qwen2.5-coder:7b"}
            },
            "fallback": "keyword"
        }
    }, indent=2)
