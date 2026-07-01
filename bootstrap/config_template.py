"""eto-config.json 模板"""
import json


def make_config(default_provider: str) -> str:
    """生成 eto-config.json 内容。

    Args:
        default_provider: "deepseek" | "ollama" | "skip"
    Returns:
        JSON string，包含 models/fallback 字段
    """
    return json.dumps(
        {
            "router": {
                "provider": default_provider,
                "models": {
                    "deepseek": {
                        "url": "https://api.deepseek.com/v1/chat/completions",
                        "model": "deepseek-chat",
                    },
                    "ollama": {
                        "url": "http://localhost:11434/api/chat",
                        "model": "qwen2.5-coder:7b",
                    },
                },
                "fallback": "keyword",
            }
        },
        indent=2,
    )
