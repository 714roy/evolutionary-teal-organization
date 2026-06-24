#!/usr/bin/env python3
"""共识协议边界测试 (Consensus Boundary Tests)

测试场景（隔离模式，mock Pi CLI）：
- 通过 (avg >= 0.6)
- 拒绝后 3 轮死锁
- CRITICAL concern 否决
- 智子规则 veto
"""
import sys, os, json

PIPELINES = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(PIPELINES)
sys.path.insert(0, PARENT)
if PIPELINES not in sys.path:
    sys.path.insert(0, PIPELINES)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PASS = 0
FAIL = 0


def ok(name: str, detail: str = ""):
    global PASS
    PASS += 1
    tag = "PASS"
    print(f"  {tag}  {name}" + (f"  ({detail})" if detail else ""))


def fail(name: str, detail: str):
    global FAIL
    FAIL += 1
    tag = "FAIL"
    print(f"  {tag}  {name}: {detail}")


def section(title: str):
    print()
    print(f"── {title} ──")


# ── 导入 ────────────────────────────────────────────────
section("0. 模块导入")

try:
    from pipelines.consensus import propose_action
    from pipelines.context import TealContext
    import pipelines.consensus as consensus_mod
    ok("导入")
except Exception as e:
    fail("导入", str(e))
    sys.exit(1)


# ── 测试数据 ────────────────────────────────────────────
AGENTS = {
    "researcher": {"specialty": "调研", "model": "mock", "tools": ["read"]},
    "coder": {"specialty": "编码", "model": "mock", "tools": ["read", "write"]},
}

BASE_PLAN = {
    "task": "测试任务",
    "analysis": "自动化测试",
    "steps": [
        {"id": 1, "description": "步骤1", "assigned_to": "coder",
         "expected_output": "完成", "tools_needed": ["read"]},
        {"id": 2, "description": "步骤2", "assigned_to": "researcher",
         "expected_output": "完成", "tools_needed": ["read"]},
    ],
    "estimated_difficulty": "easy",
    "fallback": "retry",
}


# ── Mock: 按 agent_id + round 返回固定分数 ────────────
class RoundRobinScorer:
    """评估 mock：每轮按 agent_id 返回固定分数"""

    def __init__(self, round_scores):
        """round_scores: [(coder_score, coder_concern, researcher_score, researcher_concern), ...]
        每回合一个 tuple"""
        self.round_scores = round_scores
        self.reset()

    def reset(self):
        self._call_count = 0
        self._rounds_run = 0

    def __call__(self, agent_id, agent_config, plan):
        round_idx = self._rounds_run
        scores = self.round_scores[min(round_idx, len(self.round_scores) - 1)]
        self._call_count += 1

        if agent_id == "coder":
            return (scores[0], scores[1])
        else:
            return (scores[2], scores[3])

    def mark_round_done(self):
        """在每轮评估结束后调用"""
        self._rounds_run += 1


def reflect_identity(proposer_id, agent_config, plan, feedbacks):
    """reflect mock：原样返回 plan（不改变评分可能性）"""
    return dict(plan)


class RoundTracker:
    """包裹 propose_action 并追踪轮次边界。

    propose_action 里每轮调用 N-1 次 evaluate_plan（proposer 不评自己）。
    N=2 agents → 每轮 1 次调用。
    """

    def __init__(self, scorer):
        self.scorer = scorer

    def evaluate(self, agent_id, agent_config, plan):
        return self.scorer(agent_id, agent_config, plan)

    def reflect(self, proposer_id, agent_config, plan, feedbacks):
        # 反射调用 = 本轮结束，下一轮开始
        self.scorer.mark_round_done()
        return dict(plan)


# ── 场景 1: 正常通过 ──────────────────────────────────
section("1. 正常通过")

try:
    # 2 agents, proposer=researcher → 只有 coder 评分
    # 每轮 1 次 evaluate，1 round → avg=0.8 通过
    scorer = RoundRobinScorer([(0.8, None, 0.0, None)])
    tracker = RoundTracker(scorer)
    consensus_mod.evaluate_plan = tracker.evaluate
    consensus_mod.reflect_plan = tracker.reflect

    ctx = TealContext(cleanup_stale=False)
    result = propose_action(
        proposer="researcher",
        agent_config=AGENTS["researcher"],
        plan=BASE_PLAN,
        agents=AGENTS,
        ctx=ctx,
        max_rounds=3,
    )

    if result["status"] == "approved":
        ok("通过", f"avg_score={result.get('avg_score')}, rounds={result.get('rounds')}")
    else:
        fail("通过", f"status={result['status']}, msg={result.get('message')}")
except Exception as e:
    import traceback
    fail("通过", f"{e}\n{traceback.format_exc()}")


# ── 场景 2: 3 轮死锁 ──────────────────────────────────
section("2. 3 轮死锁")

try:
    # 3 轮全是低分 → 每轮调整 → 第 3 轮后 deadlock
    low_scores = (0.3, "方案不完整", 0.4, "缺少细节")
    scorer = RoundRobinScorer([low_scores, low_scores, low_scores])
    tracker = RoundTracker(scorer)
    consensus_mod.evaluate_plan = tracker.evaluate
    consensus_mod.reflect_plan = tracker.reflect

    ctx = TealContext(cleanup_stale=False)
    result = propose_action(
        proposer="researcher",
        agent_config=AGENTS["researcher"],
        plan=BASE_PLAN,
        agents=AGENTS,
        ctx=ctx,
        max_rounds=3,
    )

    if result["status"] == "deadlock":
        ok("死锁", f"rounds={result.get('rounds')}, avg={result.get('avg_score')}")
    else:
        fail("死锁", f"expected deadlock, got {result['status']}")
except Exception as e:
    import traceback
    fail("死锁", f"{e}\n{traceback.format_exc()}")


# ── 场景 3: CRITICAL 否决 ────────────────────────────
section("3. CRITICAL 否决")

try:
    # 每轮 coder 评分高但带 CRITICAL → 永不通过
    # proposer=researcher → 只有 coder 评分
    # 第 1 轮: coder=0.8, CRITICAL → adjust
    # 第 2 轮: coder=0.8, CRITICAL → adjust
    # 第 3 轮: coder=0.8, CRITICAL → deadlock
    critical = (0.8, "CRITICAL: 方案会导致数据丢失", 0.0, None)
    scorer = RoundRobinScorer([critical, critical, critical])
    tracker = RoundTracker(scorer)
    consensus_mod.evaluate_plan = tracker.evaluate
    consensus_mod.reflect_plan = tracker.reflect

    ctx = TealContext(cleanup_stale=False)
    result = propose_action(
        proposer="researcher",
        agent_config=AGENTS["researcher"],
        plan=BASE_PLAN,
        agents=AGENTS,
        ctx=ctx,
        max_rounds=3,
    )

    # avg=0.8 >= 0.6 但含 CRITICAL → 永不通过 → 最终 deadlock
    if result["status"] == "deadlock":
        ok("CRITICAL 否决", f"rounds={result.get('rounds')}, avg={result.get('avg_score')}")
    else:
        fail("CRITICAL 否决", f"expected deadlock, got {result['status']}")
except Exception as e:
    import traceback
    fail("CRITICAL 否决", f"{e}\n{traceback.format_exc()}")


# ── 场景 4: 智子否决 ────────────────────────────────────
section("4. 智子否决")

try:
    veto_plan = {
        "task": "删除数据库",
        "analysis": "执行危险操作",
        "steps": [
            {"id": 1, "description": "rm -rf /data", "assigned_to": "coder",
             "expected_output": "删除完成", "tools_needed": ["bash"]},
        ],
    }

    ctx = TealContext(cleanup_stale=False)
    result = propose_action(
        proposer="coder",
        agent_config=AGENTS["coder"],
        plan=veto_plan,
        agents=AGENTS,
        ctx=ctx,
        max_rounds=3,
    )

    if result["status"] == "vetoed":
        ok("智子否决", f"msg={result.get('message')}")
    else:
        fail("智子否决", f"expected vetoed, got {result['status']}")
except Exception as e:
    import traceback
    fail("智子否决", f"{e}\n{traceback.format_exc()}")


# ── 汇总 ─────────────────────────────────────────────────
section("汇总")
total = PASS + FAIL
print(f"  {PASS}/{total} 通过" + ("" if FAIL == 0 else f"  {FAIL} 失败"))
sys.exit(0 if FAIL == 0 else 1)
