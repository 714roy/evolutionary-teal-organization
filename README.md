# ETO — Evolutionary Teal Organization

> Pi 是 Agent 引擎。ETO 不是另一个引擎——ETO 是让多个引擎协作的制度。

## 一句话

ETO 是青色组织原则翻译成 AI Agent 系统的**编排层**——跑在 Pi CLI 之上，做共识、路由、选举、安全和上下文传递。不写框架，只缝开源。

## 架构（5 组件，<1000 行）

```
                         ┌──────────────┐
                         │   智子守卫   │  ← 安全门禁 + 流程强制器
                         └──────┬───────┘
                                │
Agent A ──→ 三镜路由 ──→ 协调员选举 ──→ 同侪共识 ──→ Pi 执行
Agent B ──→ (按 Profile 匹配) (match×空闲率) (peer 评分)    │
Agent C ──→                                            TealContext
                                                       (共享上下文池)
                        ↓
               Agent Profile 注册表
               (specialty/style/ICP/skills/MCP_tools)
```

| 组件 | 做的事 | 不做什么 |
|:-----|:-------|:---------|
| **Agent Profile** | 每个 Agent 声明自己的能力全景（专长/风格/ICP/技能/MCP 工具），路由按 Profile 分配 | 不固定角色——Profile 是描述，不是标签 |
| **三镜路由** | 分析任务→匹配 Profile→分给最合适的 Agent | 不写 Agent 逻辑 |
| **协调员选举** | 按匹配度+空闲率选临时负责人 | 不建固定层级 |
| **同侪共识** | peer 评分→超阈值执行 | 不搞一言堂 |
| **智子守卫** | 安全检查 + **强制流程**：不只是 veto，还能 reroute 按预设流程走 | 不替 Agent 做决定 |
| **TealContext** | 共享上下文池，Agent 互相看见 | 不取代 Pi 的会话管理 |

**能力不丢失原则：** Agent 分配任务给另一个 Agent 时，接收方的全部能力（MCP、skill、工具）必须保留。不接受"subagent 降级"——ETO 里所有 Agent 都是平等完整节点。

**流程按需生成：** 任务流不是固定模板（研究员×3 步），而是由路由层根据任务特征动态决定拓扑结构。

**自动时间注入：** 每次执行前自动注入当前时间到 prompt。

**Pi 有的不碰：** TUI（pi-tui）、工具调用（--tools）、会话管理（JSONL）、提供商抽象（pi-ai）、Agent 运行时（pi 命令）——这些 ETO 一律不写，直接用。

## 当前状态（Extension 模式）

```
✅ 三镜路由（语义 + 关键词）
✅ 智子安检（veto 模式）
✅ before_agent_start 上下文注入 + 自动时间注入
🟡 Agent Profile 注册表（现在只有 specialty，缺 style/ICP/MCP）
🟡 共识工具（模拟随机数，缺真 peer 调用）
📋 Enforcer 模式（强制流程）
📋 流程按需生成（动态组装不固定）
📋 能力不丢失（跨 Agent 调用保留完整能力）
```

形态：`~/.pi/agent/extensions/eto.ts`（~200 行 TypeScript），在 Pi 生态内跑通所有核心流程。

## 路线图

```
Extension（现在）──验证设计──→ Fork 决策（1-2周）──→ 真多 Agent（长期）
                    ↑                  ↑                       ↑
              走通全部流程       触天花板就 Fork          Pi RPC / A2A
              代码 <1000 行     没触就继续 Extension     多独立 Agent 进程
```

### 决策标准

Fork 的前提——Extension **触及了 Pi 的能力天花板**：
- ❓ 无法修改 Pi 的 TUI 显示 ETO 特有信息？
- ❓ 无法修改 Pi 的会话存储格式？
- ❓ 需要 Pi 没有的内核钩子？

如果 YES → Fork，包名 `@reoroy/eto-cli`，保持 pi-ai + pi-tui。
如果 NO → 继续 Extension，接受 ETO 是 Pi 生态的一个扩展。

## 铁律（改代码前看）

1. **Pi 有的绝对不写**——TUI、工具调用、会话管理、提供商抽象、Agent 运行时
2. **ETO 只写编排层**——三镜路由、选举、共识、智子、上下文传递
3. **代码量 < 1000 行**——超过就说明在造轮子
4. **先问"Pi 有没有"**——有就直接 `import` / `--tools` / 调 `pi` 命令

## 历史教训

- ❌ 写了 3156 行 Python——其中 95% 是 Pi 已有的功能
- ✅ 删到 119 行 TypeScript Extension——才意识到 ETO 的正确形态
- **核心教训：ETO 做薄编排层跑在 Pi 之上，不是重写整个栈。**

---

## 想要达成的功能和特性（65 特性 × 8 维度）

完整清单：`docs/eto-feature-list.md`（含 ETO-001~066 编号、说明、优先级、来源追溯）

### 🚪 入口与路由（ETO-001~008）
| 特性 | 说人话 | 优先级 |
|:-----|:-------|:-------|
| 智子入口 | 统一 `eto <task>`，不走"聊到哪算哪" | P0 |
| 三镜分拣 + 三体赋权 | 格物镜→析理镜→合验镜，理体/实体/得体三路赋权 | P0 |
| 智能路由 | 单步直走 / 多步规划 / 多方共识 三种模式 | P0 |
| 置信度学习 + Loop 检测 | 每次路由打置信分，自动修正 + 识别循环模式 | P1 |

### 🦋 青色组织（ETO-009~021）
| 特性 | 说人话 | 优先级 |
|:-----|:-------|:-------|
| 自主管理 Agent 池 | Agent 是 peer 不是 worker，有 Profile（专长/风格/ICP/技能/MCP） | P0 |
| Agent Profile 注册表 | 每个 Agent 注册自己的完整能力画像，路由按 Profile 分派 | P0 |
| 能力不丢失原则 | A 派活给 B 时 B 保留全部能力（MCP/skill/工具），不降级 | P0 |
| 临时协调员选举 | `match_score(Agent, task) × (1 - busy_ratio)` 动态推举 | P0 |
| 青色共识协议 | 提议→广播→peer 评分(>0.6 通过)→执行，最多 3 轮反馈调整 | P0 |
| 流程按需生成 | 任务流不固定（不是研究员×3 的模板），路由层根据任务特征动态组装 | P0 |
| 超时降级 + 死锁防护 | 10s 无响应自动执行，同一提议循环 3 轮标记死锁 | P1 |
| 自动时间注入 | 每次执行前自动注入当前时间到 prompt | P1 |
| 探索奖励 + 进化使命 | 10% 概率随机选非最优路由，集体回顾持续自我调整 | P2 |

### 🧠 记忆与知识（ETO-022~033）
| 特性 | 说人话 | 优先级 |
|:-----|:-------|:-------|
| TealContext 共享池 | global_memory + active_proposals + consensus_log | P0 |
| 统一记忆 API | `perceive()/record()/query()` 三接口统一 | P0 |
| 三层记忆 | agentmemory(独享) + gbrain(共享) + AIMemory(工作台) | P1 |
| 知识蒸馏 + 记忆路由 | 对话→自动提炼 skill，自动判断新信息走哪层 | P1 |

### 👑 治理/智子（ETO-034~042）
| 特性 | 说人话 | 优先级 |
|:-----|:-------|:-------|
| 智子规则引擎 | YAML 配置，热重载，veto/warn/log 三种动作 | P0 |
| 否决不提议 | 只拦越界不拦创新 | P0 |
| **Enforcer 模式** | 不只是 block，还能强制 reroute 按预设流程走 | P0 |
| 审计日志 + 成本防火墙 | 所有调用可查，单次任务预算上限、token 告警、模型降级 | P1 |
| 流程强制器 | 对特定任务类型可预设执行路径，智子确保不走偏 | P1 |

### 🤝 Agent 协作（ETO-043~047）
| 特性 | 说人话 | 优先级 |
|:-----|:-------|:-------|
| Peer 注册发现 | Agent 动态加入/离开，查"谁在线" | P1 |
| 跨 Agent 桥接 | Hermes ↔ Claude Code ↔ Reasonix 传上下文 | P2 |
| 多 Agent 并行 + 调度 | 子任务分布式执行，按能力×负载×成本综合评分 | P1 |

### 🏗️ Pi 架构（ETO-048~052）
| 特性 | 说人话 | 优先级 |
|:-----|:-------|:-------|
| CLI 命令体系 | `eto 智子 / eto 做 / eto 问 / eto 提议` 等 | P0 |
| Pi Extension | ETO 是 Pi 的一个扩展，不是独立框架 | P1 |
| MCP 兼容层 + 模块化 | 对接任何 MCP 工具，各模块可单独升级 | P2 |

### 📡 平台与渠道（ETO-053~055）
| 特性 | 说人话 | 优先级 |
|:-----|:-------|:-------|
| 多渠道输出 | QQ/微信/Telegram 统一路由 | P2 |
| 定时任务编排 + 推送路由 | cron 统一管理，低频重要→微信，高频提醒→QQ | P1 |

### 🔄 进化与反馈（ETO-056~066）
| 特性 | 说人话 | 优先级 |
|:-----|:-------|:-------|
| 集体回顾 | 定期分析失败模式，更新策略权重、清理记忆 | P0 |
| 自动学习 | 踩坑→记教训→重复 3 次升永久规则 | P1 |
| 四种 Loop | Rework(打回重做) / Iteration(逐步逼近) / Watch(外部触发) / Cron | P1 |
| 远期 | Active Inference（自由能最小化）+ World Model（潜空间模拟） | ⭐ |

### 开发纪律
ETO-D01~D05：TDD-AI / Millstone(审) / Planwright(先想) / Trammel(知道怎么拼) / Compound Agent(全流程+回滚)——全部已装 ✅

---

## 功能缝合对照表

> **原则：不写框架，只缝已有开源。ETO 的胶水代码预估 < 500 行。**

完整方案：`docs/ETO缝合方案对照表.md`（含备选方案、搭建顺序、编程 Agent 话术）

| 层 | ETO 需求 | 缝合方案 | 怎么缝 | 胶水代码 |
|:---|:---------|:---------|:-------|:---------|
| 📡 通信 | Agent 间发现与通信 | **A2A Protocol v1.0** + **ProtoLink** | 每个 Agent 启动时注册到 A2A 网络 | ~20 行 |
| 🧩 编排 | 任务→DAG 分解 | **Maestro** (YAML DAG + CLI/REST) | 调 Maestro API 分解任务→分给 Agent | ~50 行 |
| 🗳️ 共识 | 多 Agent 投票 | **VotingAI** (5 种策略，拜占庭容错) | 多模型并行评分→加权合成 | ~30 行 |
| 👑 选举 | 协调员选举 | **raft-lite** (纯 Python 单文件 Raft) | 匹配度 × 空闲率动态推举 | ~30 行 |
| 🧠 短期记忆 | 会话上下文 | **Pi JSONL 会话树** | Pi 内置，ETO 不碰 | 0 行 |
| 🧠 长期记忆 | 跨会话持久化 | **@yylan/pi-memory** (4 层+FTS5+向量) | `pi install npm:@yylan/pi-memory` | ~20 行 |
| 🔒 安全 | 护栏 | **Hermes enforcer** | 已在用 | 0 行 |

### 已弃用的旧方案
| 层 | 旧方案 | 原因 | 替代 |
|:---|:-------|:-----|:-----|
| 记忆 | agentmemory | 改为 Pi 生态扩展，更轻量 | @yylan/pi-memory |
| 编排 | Nexus | 已不可用（2025 后） | Maestro / lythonic / Dagu |
| 共识 | Aegean \| Gravity AI | 均不可用 | VotingAI / LLM Council / Aragora |

### 搭建顺序
```
Phase 1 ✅  → Phase 2 🟡  → Phase 3-5 📋
ProtoLink      Maestro         动态自组织
A2A 通信       VotingAI        进化学习
               raft-lite       理论引擎
               pi-memory        (Active Inference)
```
