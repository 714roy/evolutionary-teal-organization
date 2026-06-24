"""Skill 加载系统 (Phase 2, ETO-037/038)

Skill = Agent 的扩展能力包。YAML 格式，定义：
- 触发的任务模式（pattern）
- 注入的 system prompt 片段
- 需要的工具
- 智子安检级别

加载流程：skill 目录扫描 → 安检 → 注册 → 注入到 Agent prompt
"""

import os
import re
import yaml
from pathlib import Path

SKILLS_DIR = Path.home() / ".eto" / "skills"


def _load_skill(file_path: Path) -> dict | None:
    """加载单个 skill YAML 文件"""
    try:
        data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        if not data or not isinstance(data, dict):
            return None
        name = data.get("name", file_path.stem)
        return {"name": name, "file": file_path.name, **data}
    except Exception as e:
        print(f"  [!] Skill {file_path.name} 加载失败: {e}")
        return None


def load_all() -> list[dict]:
    """加载所有 skill"""
    if not SKILLS_DIR.exists():
        return []
    skills = []
    for f in sorted(SKILLS_DIR.glob("*.yaml")):
        skill = _load_skill(f)
        if skill:
            skills.append(skill)
    return skills


def match_skill(skills: list[dict], task: str) -> list[dict]:
    """按任务描述匹配 skill（pattern 正则或关键词匹配）"""
    task_lower = task.lower()
    matched = []
    for s in skills:
        patterns = s.get("match", {}).get("pattern", [])
        if isinstance(patterns, str):
            patterns = [patterns]
        for p in patterns:
            try:
                if re.search(p, task_lower):
                    matched.append(s)
                    break
            except re.error:
                pass
    return matched


def augment_prompt(skills: list[dict], base_prompt: str) -> str:
    """将匹配到的 skill system prompt 注入到 base_prompt"""
    extra = []
    for s in skills:
        sp = s.get("system_prompt", "")
        if sp:
            extra.append(f"[Skill: {s['name']}]\n{sp}")
    if extra:
        return base_prompt + "\n\n" + "\n\n".join(extra)
    return base_prompt


def required_tools(skills: list[dict]) -> list[str]:
    """汇总所有匹配 skill 需要的工具"""
    tools = set()
    for s in skills:
        for t in s.get("tools", []):
            tools.add(t)
    return sorted(tools)
