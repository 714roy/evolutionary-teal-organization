---
type: design-spec
title: 进化型青色组织 · 架构功能说明
description: 青色组织 Multi-Agent 系统架构设计——TealContext 共享池、青色决策协议、临时协调员选举、集体回顾循环、安全守卫
tags: [teal-organization, architecture, consensus, self-management, evolution]
timestamp: 2026-06-20
resource: https://github.com/reoroy/evolutionary-teal-organization
---

# 进化型青色组织 · 架构功能说明

> 状态：设计文档（v0.28）
> 定位：青色组织架构 —— 自主管理 · 完整性 · 进化使命

---

## 一、核心理念

青色组织不是一种具体的技术方案——它是将 Laloux 的组织哲学翻译为 AI Agent 系统架构的一组设计原则。

| 青色原则 | 人类组织含义 | Agent 系统映射 |
|:---------|:------------|:---------------|
| **自主管理** | 没有固定层级，决策权在执行者手中 | 去中心化动态编排，Agent 通过共识协议自组织 |
| **完整性** | 每个人可以展现完整的自我 | 共享全局上下文（TealContext），Agent"看见"彼此 |
| **进化使命** | 组织有自己的生命和方向 | 集体回顾循环 + 动态目标校准 |

---

## 二、核心架构

### 2.1 TealContext — 共享工作记忆池

替代传统的中心化数据库和孤立 System Prompt。每个 Agent 执行前先将意图和上下文写入公共池。

```python
class TealContext:
    """青色共享池——实现'完整性'原则"""
    
    def __init__(self):
        self.global_memory = []        # 长周期向量记忆（包含成功/失败记录）
        self.active_proposals = []     # 当前流转中的提议
        self.consensus_log = []        # 完整决策审计日志（谁·何时·为啥）
    
    def perceive(self, agent_id):
        """Agent 感知全局上下文"""
        recent = self.global_memory[-10:]   # 近期记录
        active = self.active_proposals      # 正在流转的提议
        return {"recent": recent, "active": active}
    
    def record(self, entry):
        """写入全局记忆"""
        self.global_memory.append({
            **entry,
            "timestamp": now(),
        })
```

### 2.2 TealAgent — 基础 Agent

不预设角色，不分配固定工具集——Agent 根据上下文自主决定行为。

```python
class TealAgent:
    """青色 Agent——自主·完整·进化"""
    
    def __init__(self, agent_id: str, specialty: str, tools: list):
        self.id = agent_id
        self.specialty = specialty          # 专长领域（不是固定角色）
        self.tools = tools                  # 可用工具集
        self.local_knowledge = {}           # 个体经验
        self.busy_ratio = 0.0               # 当前负载
    
    def perceive(self, ctx: TealContext):
        """感知全局上下文"""
        return ctx.global_memory[-10:] + list(self.local_knowledge.items())
    
    def evaluate(self, proposal) -> tuple:
        """评估其他 Agent 的提议——返回 (评分, 担忧)"""
        score = self._calc_relevance(proposal)
        concern = self._detect_risk(proposal)
        return (score, concern)
    
    def reflect(self, feedbacks, original_plan):
        """根据同侪反馈调整计划"""
        # 分析反馈中最常被指出的问题
        # 自动调整，不需要管理员重写 Prompt
        return adjusted_plan
```

### 2.3 青色决策协议

核心流程：谁执行谁发起，广播取共识。

```python
def propose_action(proposer: TealAgent, plan, ctx: TealContext):
    """青色决策协议——替代上级指令"""
    
    # 第一步：广播给受影响方（同侪反馈）
    feedbacks = []
    affected = get_affected_agents(plan, ctx)   # 谁会被这个决策影响
    for peer in affected:
        score, concern = peer.evaluate(plan)
        feedbacks.append((peer.id, score, concern))
    
    # 第二步：共识过滤
    avg_score = sum(f[1] for f in feedbacks) / len(feedbacks)
    has_veto = any(f[2] == "CRITICAL" for f in feedbacks)  # 安全守卫触发点
    
    # 第三步：超时熔断（防止无休止等待）
    if timeout_reached(10_000):  # 10s
        plan = local_fallback(plan)   # 降级为本地默认执行
        return proposer.execute(plan)
    
    # 第四步：共识决策
    if avg_score > 0.6 and not has_veto:
        result = proposer.execute(plan)
        ctx.record({
            "type": "executed",
            "proposer": proposer.id,
            "plan": plan,
            "result": result,
            "feedbacks": feedbacks,
        })
        return result
    else:
        # 第五步：根据反馈调整
        adjusted = proposer.reflect(feedbacks, plan)
        ctx.record({
            "type": "adjusted",
            "proposer": proposer.id,
            "original": plan,
            "adjusted": adjusted,
            "feedbacks": feedbacks,
        })
        return propose_action(proposer, adjusted, ctx)  # 递归迭代
```

### 2.4 临时协调员选举

没有固定 PM。任务来临时动态推举。

```python
def elect_temporary_lead(agents: list, task_type: str):
    """动态推举临时协调员"""
    return max(
        agents,
        key=lambda a: match_score(a, task_type) * (1 - a.busy_ratio)
    )
```

主循环：

```
while mission_not_complete:
    current_lead = elect_temporary_lead(agent_pool, current_task)
    proposal = current_lead.draft_plan(ctx)
    propose_action(current_lead, proposal, ctx)
    # 任务完成 → lead 角色自动解散
```

### 2.5 集体回顾循环

每完成 N 轮任务，系统自动触发回顾。不需要管理员介入。

```python
def collective_reflection(ctx: TealContext, agents: list):
    """集体回顾——实现'进化使命'原则"""
    
    failures = [log for log in ctx.consensus_log if log.get('result') == 'fail']
    if not failures:
        return  # 没有失败，继续保持
    
    # 动态调整评价权重——Agent 自动学习
    for agent in agents:
        agent.local_knowledge['strategy_weight'] = update_weight(failures)
    
    # 清理过时记忆
    ctx.global_memory = trim_by_relevance(ctx.global_memory)
    
    # 广播调整结果
    broadcast(f"[回顾] 权重已更新，共 {len(failures)} 条失败记录纳入学习")
```

---

## 三、👑 安全守卫：智子

在去中心化系统中，需要一个只做否决不做干预的角色。

### 职责边界

```
✅ 只否决，不提议
✅ 只拦越界，不拦创新
✅ 检测共识死锁（提议循环 > 3 轮）
✅ 拦截越权工具调用
✅ 熔断超时提议（10s 无响应）
✅ 审计日志可查询

❌ 不参与日常决策
❌ 不指定谁当协调员
❌ 不改写其他 Agent 的 Prompt
❌ 不决定任务优先级
```

### 实现方式

安全守卫可以作为独立 CLI（`qsh`）运行：

```bash
qsh audit --since=1h          # 查看过去一小时的决策日志
qsh rule list                  # 列出否决规则
qsh rule add                   # 添加新规则
qsh veto <proposal-id>         # 手动否决（紧急情况）
```

安全守卫的逻辑嵌入在共识协议的 `has_veto` 检查点中——当一个提议触发守卫规则时，自动返回 `CRITICAL`，触发调整循环。

---

## 四、三体决策引力模型

每个任务受三个引力源影响，权重决定 Pipeline 拓扑：

| 体 | 含义 | 高权重时 |
|:---|:-----|:---------|
| ☀️ **太阳（理体）** | 逻辑 · 推理链 · 因果 | 审查加重，REWORK 增加 |
| 🌙 **太阴（实体）** | 事实 · 数据 · 可验证 | 调研 Agent 增多 |
| ⭐ **太白（得体）** | 品味 · 审美 · 文化 | 风格审查加入 |

详见 [定位文档 → 三体决策引力模型](positioning-and-strategy.md#-三体决策引力模型)。

---

## 五、进化路径

### 阶段① 🟤 琥珀色 — 三省六部（已验证）

固定 16 节点 pipeline，通政司→中书省→一审→五部→二审→刑部→早朝官。

- ✅ 全链跑通，REWORK 循环有效
- ✅ 20 条智子规则在生产环境运行
- ❌ 角色固定（礼部只能调研）
- ❌ Pipeline 拓扑固定（无法自适应）

路径：`~/Nutstore Files/工坊/项目/three-line-pipeline/`

### 阶段② 🟠 橙色 — 精英制

动态角色分配：通政司按历史表现推荐最佳 Agent 组合。

- 绩效数据驱动调度
- 快速通道（MODE=direct）
- 跨部门协作（MODE=squad）

### 阶段③ 🟢 绿色 — 共识制

Agent 有投票权。

- 三体权重由集体共识决定
- 智子从立法者转变为宪章法官
- 决策过程全透明

### 阶段④ 🦋 青色（终极目标）

Agent 完全自组织。

- Pipeline 拓扑动态生成（不由用户预设）
- Agent 自主决定下一个 call 谁
- 智子从宪章法官转变为顾问
- 系统像生命系统一样感知 → 适应 → 进化

---

## 六、已知缺陷（Pitfalls）

| # | 问题 | 状态 | 说明 |
|:-|:-----|:-----|:-----|
| P1 | 共识协议可能死锁 | ⏳ 待修复 | 提议循环超过 3 轮 → 智子介入或降级执行 |
| P2 | 安全守卫误判 | ⏳ 待解决 | 规则过于严格会扼杀创新，需持续调优 |
| P3 | TealContext 记忆膨胀 | ⏳ 待处理 | 需要 Relevance-based 修剪策略 |
| P4 | 超时熔断的默认值不合理 | ⏳ 待调优 | 10s 是保守值，需根据任务类型动态调整 |

---

## 七、与 Dynamic Workflows 的关系

ETO 的青色组织架构可以运行在不同的引擎上：

| 引擎 | 定位 | 现状 |
|:-----|:-----|:-----|
| **Dynamic Workflows** 🔥 | 首选实现引擎 | Claude Code JS 编排 + subagent |
| **Pi Extension** | 备选方案 | 已有设计文档（tlp-pi-fork-plan） |
| **AgentFlow** | 当前运行平台 | 三省六部已跑通 |
| **Shell CLI** | 最小可行版本 | `ETO` 命令已可用 |

> Dynamic Workflows 提供引擎（硬件），ETO 提供组织制度（软件）。
> DW = 人列计算机的 30 万士兵，ETO = 军阶/旗号/号令/奖惩。

---

## 八、成本预算

| 模式 | 成本 | 说明 |
|:-----|:-----|:------|
| **direct**（快速直达） | ~$0.001 | 单次 Reasonix 调用 |
| **research**（研究模式） | ~$0.003-0.005 | 调研 + 交叉验证 |
| **build**（构建模式） | ~$0.005-0.015 | 方案 + 编码 + 审查 |
| **full**（全流程） | ~$0.01-0.02 | 16 节点全链 |
| **青色共识**（含反馈迭代） | ~$0.02-0.05 | 多轮共识 + 调整 |

---

*ETO — Now, we are comrades. architecture > agent — Entropy · Trinity · Organic*
