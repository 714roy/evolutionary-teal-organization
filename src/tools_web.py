"""Web 搜索工具 (Phase 2)

通过 DuckDuckGo 做零配置网页搜索和内容抓取。
不需要 API key。返回标题+摘要+链接。
"""

import json
import re
import urllib.parse
import urllib.request
import urllib.error

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ETO/1.0"


def search(query: str, max_results: int = 5) -> list:
    """DuckDuckGo 搜索

    返回 [{"title": str, "snippet": str, "url": str}, ...]
    """
    params = urllib.parse.urlencode({"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"})
    url = f"https://api.duckduckgo.com/?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        return [{"title": "[搜索失败]", "snippet": str(e), "url": ""}]

    results = []
    # RelatedTopics 是 DDG 的结构化结果
    topics = data.get("RelatedTopics", [])
    for topic in topics:
        if "Topics" in topic:
            for sub in topic["Topics"]:
                results.append({
                    "title": sub.get("Text", "").split(" - ")[0] or sub.get("FirstURL", ""),
                    "snippet": sub.get("Text", ""),
                    "url": sub.get("FirstURL", ""),
                })
        else:
            results.append({
                "title": topic.get("Text", "").split(" - ")[0] or topic.get("FirstURL", ""),
                "snippet": topic.get("Text", ""),
                "url": topic.get("FirstURL", ""),
            })
        if len(results) >= max_results:
            break

    # 保底：如果 DDG API 没返回结果，用 HTML 版兜底
    if not results:
        results = _search_html(query, max_results)

    return results if results else [{"title": "无结果", "snippet": f"'{query}' 未找到相关结果", "url": ""}]


def _search_html(query: str, max_results: int = 5) -> list:
    """DDG HTML 搜索兜底"""
    params = urllib.parse.urlencode({"q": query})
    url = f"https://html.duckduckgo.com/html/?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError):
        return []

    results = []
    # 简单提取结果块
    for match in re.finditer(
        r'class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</(?:a|div)>',
        html, re.DOTALL,
    ):
        url = match.group(1)
        title = re.sub(r"<[^>]+>", "", match.group(2)).strip()
        snippet = re.sub(r"<[^>]+>", "", match.group(3)).strip()
        results.append({"title": title, "snippet": snippet, "url": url})
        if len(results) >= max_results:
            break
    return results


def fetch_page(url: str, max_chars: int = 3000) -> str:
    """抓取网页内容（纯文本）"""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text" not in content_type and "html" not in content_type:
                return f"[跳过: 非文本内容 ({content_type})]"
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError) as e:
        return f"[抓取失败: {e}]"

    # 去 HTML 标签
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]
