"""智子规则引擎 (ETO-034/036)

- pre_execution 类型规则检查
- 动作: veto / warn / log
- YAML 规则热重载
"""

import os
import re
import yaml
from pathlib import Path

RULES_DIR = Path.home() / ".eto" / "rules"


def _load_rules():
    """加载所有 YAML 规则"""
    rules = []
    if not RULES_DIR.exists():
        return rules
    for f in sorted(RULES_DIR.glob("*.yaml")):
        try:
            rule = yaml.safe_load(f.read_text(encoding="utf-8"))
            if rule and isinstance(rule, dict):
                rules.append(rule)
        except Exception as e:
            print(f"  [!] 规则文件 {f.name} 加载失败: {e}")
    # 按 priority 排序
    rules.sort(key=lambda r: r.get("priority", 50))
    return rules


def zhizi_check_plan(plan: dict) -> list:
    """检查 Plan 是否触发任何规则（基于步骤描述文字）"""
    results = []
    rules = _load_rules()

    # 只检查 plan 的 task + analysis + step descriptions
    check_text = str(plan.get("task", "")) + " " + str(plan.get("analysis", ""))
    for step in plan.get("steps", []):
        check_text += " " + step.get("description", "")
        check_text += " " + str(step.get("tools_needed", []))

    for rule in rules:
        if rule.get("type") != "pre_execution":
            continue
        pattern = rule.get("match", {}).get("pattern", "")
        if re.search(pattern, check_text, re.IGNORECASE):
            results.append({
                "rule": rule.get("name", "unknown"),
                "action": rule.get("action", "warn"),
                "message": rule.get("message", ""),
            })

    return results


def zhizi_pre_tool(agent_id: str, tool: str, args: str) -> dict:
    """Agent 调工具前检查。返回 {"allow": bool, "messages": [str]}"""
    rules = _load_rules()
    for rule in rules:
        if rule.get("type") != "pre_execution":
            continue
        match_tools = rule.get("match", {}).get("tool", [])
        if tool not in match_tools:
            continue
        pattern = rule.get("match", {}).get("pattern", "")
        if re.search(pattern, args, re.IGNORECASE):
            action = rule.get("action", "warn")
            msg = rule.get("message", f"规则 '{rule.get('name')}' 触发")
            return {
                "allow": action != "veto",
                "action": action,
                "message": msg,
            }
    return {"allow": True, "action": "log", "message": ""}


def zhizi_has_veto(plan: dict) -> bool:
    """快速检查是否有 veto（共识决策时调用）"""
    checks = zhizi_check_plan(plan)
    return any(c["action"] == "veto" for c in checks)


def zhizi_report(plan: dict) -> list:
    """返回完整的智子检查报告"""
    return zhizi_check_plan(plan)
