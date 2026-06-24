"""青色共识协议 (ETO-016/017)

完整循环: 提议 -> 广播 -> 评分(>0.6) -> 执行 / 递归调整(最多3轮)
同侪反馈调整: reflect -> 调整 -> 重提议
"""

import json
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from executor import call_pi, call_pi_json
from zhizi import zhizi_has_veto, zhizi_report
from context import TealContext


SYSTEM_PROMPT_EVALUATE = """你是同侪评审员。输出JSON评分。
{"score":0.8,"concern":"改进建议或null"}
评分标准：>=0.6通过，<0.6不通过。只输出JSON。
"""

SYSTEM_PROMPT_REFLECT = """你是协调员。根据反馈调整方案JSON。
只修改评分最低的步骤。输出完整Plan JSON。只输出JSON。
"""


def evaluate_plan(agent_id: str, agent_config: dict, plan: dict) -> tuple:
    """同侪评估 Plan (ETO-016)
    返回: (score, concern)
    """
    plan_json = json.dumps(plan, ensure_ascii=False, indent=2)
    prompt = f"请评估以下执行方案：\n\n{plan_json}"

    model = agent_config.get("model", "ollama/qwen2.5-coder:7b")
    tools = agent_config.get("tools", ["read"])
    specialty = agent_config.get("specialty", "")

    eval_prompt = f"{SYSTEM_PROMPT_EVALUATE}\n\n你的专长: {specialty}\n\n{prompt}"

    # ⚡ 评估只需文本输出，不传 tools → 使用 --no-tools 防止 Pi 执行工具调用
    result = call_pi_json(
        prompt=eval_prompt,
        tools=None,           # critical: 不传 tools 让 Pi 输出纯 JSON，而非执行工具
        model=model,
        timeout=60,           # 本地模型响应较慢，30s 不够
        retry=1,
    )

    if isinstance(result, dict):
        # 大小写不敏感的 key 匹配（Score/score, Notes/concern/reasoning）
        score_raw = (result.get("score") or result.get("Score") or result.get("SCORE")
                     or result.get("rating") or result.get("Rating"))
        if score_raw is not None:
            if isinstance(score_raw, str) and "/" in score_raw:
                parts = score_raw.split("/")
                try:
                    score = float(parts[0]) / float(parts[1])
                except (ValueError, ZeroDivisionError):
                    score = 0.5
            else:
                try:
                    score = float(score_raw)
                except (ValueError, TypeError):
                    score = 0.5
            # 归一化：模型有时输出 0-100 范围，统一到 0-1
            if score > 1.0:
                score = score / 100.0
            score = max(0.0, min(1.0, score))
            # 兼容多种字段名：concern / reasoning / Notes / feedback / comment
            concern = (result.get("concern") or result.get("reasoning")
                       or result.get("Notes") or result.get("notes")
                       or result.get("feedback") or result.get("comment")) or None
            return score, concern

    # 保底: 直接调 Pi 输出纯数字评分（不要 JSON 格式）
    try:
        from executor import call_pi as _call_pi
        fallback = _call_pi(
            prompt=f"只输出一个数字0到1之间的评分（如0.7），不要任何其他文字：\n\n请评估这个方案：\n\n{plan_json}",
            tools=None,
            model=model,
            timeout=30,
        )
        m = re.search(r"([0-9]+\.[0-9]+)", fallback)
        if m:
            score = max(0.0, min(1.0, float(m.group(1))))
            return score, "（数字评分，无文本意见）"
    except Exception:
        pass

    return None, "评估结果解析失败"


def reflect_plan(
    proposer_id: str,
    agent_config: dict,
    plan: dict,
    feedbacks: list,
) -> dict:
    """根据同侪反馈调整方案 (ETO-017)
    只调整评分最低的步骤
    """
    fb_text = "\n".join([
        f"- Agent {f[0]}: 评分 {f[1]}, 意见: {f[2] or '无'}"
        for f in feedbacks
    ])

    plan_json = json.dumps(plan, ensure_ascii=False, indent=2)
    prompt = (
        f"原始方案：\n{plan_json}\n\n"
        f"同侪反馈：\n{fb_text}\n\n"
        f"请根据反馈调整方案，输出调整后的完整 Plan JSON。"
    )

    model = agent_config.get("model", "ollama/qwen2.5-coder:7b")
    tools = agent_config.get("tools", ["read", "write"])

    result = call_pi_json(
        prompt=f"{SYSTEM_PROMPT_REFLECT}\n\n{prompt}",
        tools=tools,
        model=model,
        timeout=60,
        retry=1,
    )

    if isinstance(result, dict) and "steps" in result:
        return result

    # 保底：返回原 plan
    return plan


def propose_action(
    proposer: str,
    agent_config: dict,
    plan: dict,
    agents: dict,
    ctx: TealContext,
    max_rounds: int = 3,
) -> dict:
    """青色决策协议 (ETO-016)
    完整共识循环：广播 -> 评分 -> 过滤 -> 执行 / 调整
    """
    # 0. 智子预检
    if zhizi_has_veto(plan):
        zhizi_checks = zhizi_report(plan)
        ctx.record("veto", "zhizi", plan, "vetoed", zhizi_checks)
        ctx.consensus_log_append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "type": "veto",
            "proposer": proposer,
            "plan_id": plan.get("task", "")[:30],
            "detail": {"checks": zhizi_checks},
        })
        return {
            "status": "vetoed",
            "message": "智子否决",
            "details": zhizi_checks,
        }

    # 创建提议
    proposal = {
        "id": f"prop_{int(time.time()*1000)}",
        "proposer": proposer,
        "plan": plan,
        "status": "voting",
        "feedbacks": [],
        "round": 1,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    proposal_id = ctx.propose(proposal)

    current_plan = dict(plan)

    for round_num in range(1, max_rounds + 1):
        print(f"\n  T- 共识轮次 {round_num}/{max_rounds}")
        feedbacks = []

        # 1. 并行广播给同侪评分（原串行 60-120s → 并行 ~30s）
        peers = [(aid, acfg) for aid, acfg in agents.items() if aid != proposer]
        with ThreadPoolExecutor(max_workers=len(peers)) as ex:
            futures = {ex.submit(evaluate_plan, aid, acfg, current_plan): aid for aid, acfg in peers}
            for future in as_completed(futures):
                aid = futures[future]
                try:
                    score, concern = future.result(timeout=90)
                except Exception as e:
                    score, concern = None, f"评估异常: {e}"
                feedbacks.append((aid, score, concern))
                if score is not None:
                    ctx.vote(proposal_id, aid, score, concern)
                concern_str = f" ({concern[:30]}...)" if concern else ""
                print(f"  | {aid} 评估完成 score={score}{concern_str}")

        # 2. 计算平均分
        scores = [f[1] for f in feedbacks if f[1] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0.6

        # 3. 检查是否通过
        has_critical = any(
            isinstance(f[2], str) and "CRITICAL" in f[2].upper()
            for f in feedbacks
        )

        print(f"  | 平均评分: {avg_score:.3f}  {'!! CRITICAL' if has_critical else 'V 无CRITICAL'}")
        print(f"  L 智子检查: {'V 通过' if not zhizi_has_veto(current_plan) else '!! 触发规则'}")

        if avg_score >= 0.6 and not has_critical and not zhizi_has_veto(current_plan):
            # 通过 V
            print(f"  V 共识通过！")
            ctx.complete_proposal(proposal_id, "done")
            ctx.record("execute", proposer, current_plan, "approved", feedbacks)

            return {
                "status": "approved",
                "rounds": round_num,
                "avg_score": round(avg_score, 3),
                "feedbacks": feedbacks,
                "plan": current_plan,
                "message": "共识通过，可以执行",
            }
        elif round_num < max_rounds:
            # 调整后重提议
            print(f"  -> 第 {round_num} 轮未通过，协调员调整中...")
            current_plan = reflect_plan(proposer, agent_config, current_plan, feedbacks)
            ctx.record("adjust", proposer, current_plan, "adjusted", feedbacks)
            ctx.consensus_log_append({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "type": "adjust",
                "proposer": proposer,
                "plan_id": proposal_id,
                "detail": {
                    "round": round_num,
                    "avg_score": round(avg_score, 3),
                    "feedbacks": feedbacks,
                },
            })
        else:
            # 超轮失败
            print(f"  ✗ 超 {max_rounds} 轮未达成共识")
            ctx.complete_proposal(proposal_id, "deadlock")
            ctx.record("timeout", proposer, current_plan, "deadlock", feedbacks)

            return {
                "status": "deadlock",
                "rounds": round_num,
                "avg_score": round(avg_score, 3),
                "feedbacks": feedbacks,
                "plan": current_plan,
                "message": f"超过 {max_rounds} 轮未达成共识，建议人工介入",
            }

    return {
        "status": "unknown",
        "message": "共识循环异常终止",
    }
