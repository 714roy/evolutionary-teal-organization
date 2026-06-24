# Deli_AutoResearch ↔ ETO 对照分析

> 生成日期：2026-06-23
> 来源：[Deli_AutoResearch SKILL.md](reference/Deli_AutoResearch_SKILL.md)
> 背景：DeepSeek 研究员 Deli Chen 开源的自主研究框架，已验证完成 4 篇论文（最高 8.6/10 自评）和 285B RL 实验。

---

## 一、同一条河的两条支流

Deli AutoResearch 和 ETO 解决的是同一个问题——**AI Agent 长时间运行的可靠性**——但从相反的方向切入。

| 维度 | Deli AutoResearch | ETO |
|:-----|:------------------|:----|
| 出发点 | 一个 Agent 自己跑久了会崩 | 多个 Agent 协作怎么不出乱子 |
| 组织模型 | **自上而下**：Orchestrator → Worker | **自下而上**：分布式共识 → 临时协调 |
| 失败检测 | Watchdog + stale_count + 时间戳 | 智子规则 + 共识边界 |
| 韧性机制 | 结构性转向（Pivoting） | 共识死锁回退 |
| 上下文策略 | 每次开新会话，状态通过文件注入 | TealContext 共享记忆池 |
| 调度 | 4 种子 Agent 模式 | 3 种路由（consensus/direct/plan） |

---

## 二、ETO 可以直接吸收的 5 个机制

### 1. Callback = report-alive（L0 优先级）

**Deli 的做法：** 每个回调的第一动作是更新自己的 `last_seen`，而不是先干活。如果检测到上次心跳超时，立即重启并记录。

**ETO 现状：** `executor.py` 执行完 Pi CLI 调用就结束了，没有 `report back` 回调。如果 Agent 挂了，上游完全不知道。

**改动量：** ~30 行 —— 在 `core.py` 的每个阶段末尾加一个 `TealContext.report_alive()`，写入时间戳 + 阶段名。

### 2. Stall detection + 结构性转向

**Deli 的做法：**
- `stale_count`：每轮 0 个新发现 → +1
- ≥2 → 改变结构性约束（不是调参数）
- ≥4 → 报给人
- 方向多样性强制：新方向必须和所有历史方向不同

**ETO 现状：** `consensus.py` 有 3 轮死锁回退，但只覆盖共识阶段。执行阶段没有 stall 检测，Pi CLI 卡住了就死等。

**改动量：** ~50 行 —— 在 `executor.py` 加一个 stall 计数器 + 超时切换策略而不是死等。

### 3. 三层心跳（3-Layer Watchdog）

**Deli 的做法：**
- L0：shell 守护（不依赖任何 session）
- L1：cron 定时检查（小时级）
- L2：业务循环自身（每个回调更新 last_seen）

**ETO 现状：** 零层。没有 Watchdog。

**改动量：** 需要决定 L0/L1 的宿主（Windows? Linux?），这是一个 P2 增强，不阻塞 Phase 1 核心循环。

### 4. 方向多样性强制（Direction Diversity）

**Deli 的做法：** 写 `directions_tried.json`，每次新方向要与所有历史方向不同。卡住时注入扰动（对立假设、跨领域类比）。

**ETO 应用：** ETO 的三镜分析在 `analyze.py` 中产生方向，但没有记录「试过的方向」。可以复用 `TealContext` 来存。

**改动量：** ~40 行 —— 在 `analyze.py` 中加 `directions_tried` 持久化 + 多样性检查。

### 5. 四种子 Agent 模式 → ETO 路由模式补全

| Deli 模式 | ETO 对应 | 状态 |
|:----------|:---------|:-----|
| Goal-driven | plan 路由 | ✅ 已有 |
| Experiment run | direct 路由（部分） | ✅ 已有 |
| Verification | consensus 路由 | ✅ 已有 |
| **Parallel exploration** | — | ❌ **ETO 缺的** |

**Parallel exploration** —— 同时启动多个 Agent 做交叉探索（调查、反驳、跨领域类比）—— 是 ETO 路由覆盖域的明确缺口。

---

## 三、根本性的架构差异：要修吗？

| 议题 | Deli 选择 | ETO 选择 | ETO 是否需要改？ |
|:-----|:---------|:---------|:----------------|
| **新会话 vs 上下文积累** | 每次开新会话（fresh session） | 一次 session 跑完 | ⚠️ 短期不用改。ETO 的用户查询是单次 ≤5 分钟的任务，不是 Deli 的 72 小时连续跑。但如果 ETO 的任务变长，需要借鉴。 |
| **Orchestrator 中心化 vs 分布式共识** | 一个 Orchestrator 监控所有 | 没有中心大脑 | ❌ 不改。这是 ETO 的核心设计主张。 |
| **零交互 vs 用户可介入** | 绝对不打扰用户 | 用户可介入（`clarify` 工具） | ❌ 不改。ETO 场景不同，用户介入是功能不是 bug。 |

---

## 四、建议行动顺序

```
P1 ─ 加 callback report-alive（~30 行，已有 TealContext 接）
P1 ─ 加 stall detection + 超时切换（~50 行，executor.py）
P2 ─ Parallel exploration 模式（路由扩展）
P2 ─ direction_tried 记录（analyze.py + TealContext）
P3 ─ 三层 Watchdog（取决于需要多长的自治运行）
```

---

## 五、相关文件

- Deli AutoResearch 完整协议：`reference/Deli_AutoResearch_SKILL.md`
- Deli 的框架页面：https://victorchen96.github.io/auto_research/framework.html
- 当前 ETO Phase 1 状态：`docs/handover-2026-06-23b.md`
- 路由设计：`docs/phase-1-core-loop.md`
