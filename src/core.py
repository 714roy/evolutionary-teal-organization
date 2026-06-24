#!/usr/bin/env python3
# ETO Phase 1 - Teal Core Loop (ETO-001/048)

import sys, os, time, json, yaml, io

# 强制 UTF-8 (Windows GBK)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
elif hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from context import TealContext
from election import elect_temporary_lead
from consensus import propose_action
from executor import call_pi, call_pi_stream
from analyze import analyze, route
from zhizi import zhizi_report
from skill import load_all, match_skill, augment_prompt, required_tools

DATA_DIR = os.path.expanduser("~/.eto")


def load_agents(path=None):
    if path is None:
        path = os.path.join(DATA_DIR, "agents.yaml")
    if not os.path.exists(path):
        return {
            "researcher": {"specialty": "information research, data analysis", "model": "ollama/qwen2.5-coder:7b", "tools": ["read", "bash"], "max_concurrency": 3},
            "coder": {"specialty": "coding, refactoring, debugging, architecture", "model": "ollama/qwen2.5-coder:7b", "tools": ["read", "write", "bash", "edit"], "max_concurrency": 2},
            "auditor": {"specialty": "quality review, security check, audit", "model": "ollama/qwen2.5-coder:7b", "tools": ["read"], "max_concurrency": 5},
        }
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("agents", {})


def direct_execute(task):
    result = call_pi(prompt=task, timeout=30)
    return {"status": "done", "route": "direct", "output": result}


# ── 确定性任务分解模板 ──────────────────────────
# 按当选协调员分配 2-3 步，确保多步协作必定触发
# 步骤结构是结构问题，不是创意问题——Ponytail 原则
_TASK_TEMPLATES = {
    "coder": {
        "mode": "实现",
        "steps": [
            ("researcher", "调研需求", ["read", "bash"]),
            ("coder", "实现", ["read", "write", "bash", "edit"]),
            ("auditor", "审查质量", ["read"]),
        ],
    },
    "researcher": {
        "mode": "调研",
        "steps": [
            ("researcher", "收集信息", ["read", "bash"]),
            ("researcher", "深度分析", ["read"]),
            ("researcher", "整理报告", ["read", "write"]),
        ],
    },
    "auditor": {
        "mode": "审计",
        "steps": [
            ("researcher", "了解上下文", ["read"]),
            ("auditor", "执行审查", ["read"]),
            ("coder", "交叉验证", ["read"]),
        ],
    },
}


def draft_plan(lead_id, lead_config, task, ctx):
    """确定性任务分解（替代 LLM-based plan drafting）

    不再依赖 7B 模型输出 JSON Plan——它总是输出 1 步函数调用。
    改为按当选协调员类型生成 2-3 步模板，保证多步协作必定触发。
    """
    template = _TASK_TEMPLATES.get(lead_id, _TASK_TEMPLATES["coder"])
    steps = []
    for i, (agent, action, tools) in enumerate(template["steps"], 1):
        steps.append({
            "id": i,
            "description": f"{action}：{task}",
            "assigned_to": agent,
            "expected_output": f"{action} 完成",
            "tools_needed": tools,
        })

    return {
        "task": task,
        "analysis": f"自动分解为 {len(steps)} 步（{template['mode']}模式），协调员={lead_id}",
        "steps": steps,
        "estimated_difficulty": "medium",
        "fallback": "单步执行",
    }

def _run_step(step_no, step, plan, agents, ctx, skills, now, prev_outputs: list = None):
    """执行单步，注入上一步输出作为上下文"""
    a = step.get("assigned_to", list(agents.keys())[0])
    if a not in agents:
        from election import compute_match_score as _ms
        best_aid = max(agents.keys(), key=lambda x: _ms(agents[x].get("specialty",""), step.get("description","")))
        print(f"    ⚠ Agent '{a}' 不在池中，改用 '{best_aid}'")
        a = best_aid
    c = agents.get(a, list(agents.values())[0])
    desc = step.get("description") or "execute step"
    expected = step.get("expected_output") or ""

    # ── 构建 prompt：注入前几步的上下文 ──
    context = ""
    if prev_outputs:
        ctx_chunks = []
        for p in prev_outputs:
            p_out = (p.get("output") or "")[:300]
            if p_out:
                ctx_chunks.append(f"上一步（{p.get('assigned_to', '?')} - {p.get('description', '')[:30]}）：\n{p_out}")
        if ctx_chunks:
            context = "\n\n".join(ctx_chunks) + "\n\n"
    base = f"当前时间: {now}\n总体任务: {plan.get('task', '')}\n\n{context}当前步骤: {desc}\n预期产出: {expected}\n请执行。"
    matched = match_skill(skills, desc)
    if matched:
        prompt = augment_prompt(matched, base)
        tools = list(set(c.get("tools", ["read"])) | set(required_tools(matched)))
    else:
        prompt = base
        tools = c.get("tools", ["read"])

    # 研究/知识类步骤不传 read 工具
    if a == "researcher" and any(kw in desc.lower() for kw in ["收集", "信息", "知识", "调研", "search"]):
        tools = []

    model = c.get("model", "ollama/qwen2.5-coder:7b")
    action_name = desc.split("：")[0] if "：" in desc else desc[:25]
    print(f"\n  >> Step {step_no} ({a}): {action_name}")

    step_lines = []
    def _on_line(l_):
        step_lines.append(l_)
        stripped = l_.strip()
        is_tool_call = (
            stripped.startswith('{"name":') and '"arguments"' in stripped
        ) or (
            stripped.startswith("{'name':") and "'arguments'" in stripped
        )
        if is_tool_call:
            try:
                normalized = stripped.replace("'", '"')
                import json as _j
                obj = _j.loads(normalized)
                t_name = obj.get("name", "?")
                t_args = obj.get("arguments", {})
                arg_val = str(list(t_args.values())[0])[:60] if t_args else ""
                icon = {"read": "📖", "write": "✏️", "edit": "🔧",
                        "bash": "💻", "search": "🔍"}.get(t_name, "🛠")
                print(f"  {icon} {t_name}: {arg_val}", flush=True)
            except Exception:
                pass
            return
        if stripped.startswith("Warning:") or stripped.startswith("warning:"):
            return
        if stripped:
            print(f"  {stripped}", flush=True)

    out = call_pi_stream(
        prompt=prompt, tools=tools, model=model, timeout=120,
        stream_callback=_on_line,
    )
    print()
    ctx.record("execution", a, plan, "running", None)
    return {"step_id": step_no, "description": desc, "assigned_to": a, "output": (out or "")[:500]}


def execute_plan(plan, agents, ctx):
    """顺序执行计划，每步注入前几步的输出作为上下文"""
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    skills = load_all()
    steps = plan.get("steps", [])
    results = []

    # 显示一次任务概要
    task = plan.get("task", "")
    print(f"\n  任务: {task}")
    print(f"  共 {len(steps)} 步, 协调员: {plan.get('analysis','').split('协调员=')[-1].rstrip(')') if '协调员=' in plan.get('analysis','') else '?'}")

    for step_no, step in enumerate(steps, 1):
        r = _run_step(step_no, step, plan, agents, ctx, skills, now, prev_outputs=results)
        if r:
            results.append(r)

    return {"status": "completed", "step_results": results}


def main():
    task = " ".join(sys.argv[1:])
    if not task or task in ("--help", "-h"):
        print("ETO - Teal Organization System (Phase 1)")
        print("Usage: eto <task>")
        sys.exit(0 if task else 1)

    sep = "-" * 50
    print("")
    print(sep)
    print("  ETO Teal Core Loop")
    print("  Task: " + task)
    print(sep)
    start = time.time()

    agents = load_agents()
    print("")
    print("  Agents: " + str(list(agents.keys())))
    ctx = TealContext()

    # Sanjing analysis
    print("")
    print("  Analyzing...", end="")
    analysis = analyze(task)
    rt = analysis.get("ROUTE", "plan")
    print(" ROUTE=" + rt)

    if rt == "direct":
        r = direct_execute(task)
        print("")
        print("  Done")
        print(r.get("output") or "")
    else:
        # Election
        print("")
        print("  Electing coordinator...")
        (lead_id, lead_config), scores = elect_temporary_lead(agents, task, ctx)
        print("    Coordinator: " + lead_id)
        for a, s in scores.items():
            t = " <- elected" if a == lead_id else ""
            print("    " + a + ": match=" + str(s['match']) + " busy=" + str(s['busy']) + " score=" + str(s['final']) + t)

        # Draft plan
        print("")
        print("  Drafting plan...")
        plan = draft_plan(lead_id, lead_config, task, ctx)
        steps = plan.get("steps", [])
        print("    Steps: " + str(len(steps)))
        for s in steps:
            sid = s.get('id') or s.get('step') or s.get('step_id') or str(steps.index(s)+1)
            desc = s.get('description') or s.get('action') or s.get('task') or str(s)[:40]
            who = s.get('assigned_to') or s.get('agent') or '?'
            print("      " + str(sid) + ". " + str(desc)[:40] + " -> " + str(who))

        # Zhizi check - veto blocks execution
        checks = zhizi_report(plan)
        has_veto = any(c['action'] == 'veto' for c in checks)
        if checks:
            print("")
            print("  Zhizi rules check:")
            for c in checks:
                print("    [" + c['action'] + "] " + c['message'])
        if has_veto:
            print("")
            print("  Action blocked by Zhizi veto!")
            ctx.record('veto', 'zhizi', plan, 'vetoed', checks)
            elapsed = time.time() - start
            print("")
            print(sep)
            print("  Time: " + f"{elapsed:.1f}" + "s")
            print(sep)
            print("")
            return

        # Consensus or direct execute
        if rt == "consensus" or len(steps) > 1:
            print("")
            print("  Consensus protocol...")
            cr = propose_action(proposer=lead_id, agent_config=lead_config, plan=plan, agents=agents, ctx=ctx)
            plan = cr.get("plan", plan)
            if cr["status"] == "approved":
                print("")
                print("  Executing...")
                er = execute_plan(plan, agents, ctx)
                print("")
                print("  ✓ 完成")
            else:
                print("")
                print("  Consensus failed: " + cr.get('message',''))
        else:
            print("")
            print("  Executing (single step)...")
            er = execute_plan(plan, agents, ctx)
            print("")
            print("  ✓ 完成")

    elapsed = time.time() - start
    print("")
    print(sep)
    print("  Time: " + f"{elapsed:.1f}" + "s")
    print(sep)
    print("")


if __name__ == "__main__":
    main()
