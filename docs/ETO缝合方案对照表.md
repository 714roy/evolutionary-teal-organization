# ETO — 缝合方案对照表

> 目标：不写框架，只缝已有开源项目。Pi CLI + A2A + Nexus + Aegean + agentmemory = ETO  
> 总共胶水代码量预估：< 500 行

---

## 一、各层对照

### 通信层——Agent 怎么找到对方、怎么说话

| ETO 需求 | 开源方案 | 链接 | 集成方式 |
|:---------|:---------|:-----|:---------|
| Agent间通信协议 | **A2A Protocol v1.0** | [a2aproject/A2A](https://github.com/a2aproject/A2A) 24K⭐ | 标准协议，不写代码，直接遵守 |
| Python 实现 | **ProtoLink** | [nmaroulis/protolink](https://github.com/nmaroulis/protolink) | `pip install protolink`，每个Agent = 一个ProtoLink runtime |
| 能力发现 | A2A **Agent Card** | — | 每个Agent声明自己能干什么，其他Agent通过A2A发现 |

**预期胶水代码：** 每个 Agent 启动时注册到 A2A 网络，约 20 行

### 编排层——任务来了走哪条路

| ETO 需求 | 开源方案 | 链接 | 集成方式 |
|:---------|:---------|:-----|:---------|
| 任务→DAG分解 | **Maestro** 🏆 | [miciav/maestro](https://github.com/miciav/maestro) | YAML DAG + CLI/REST，多执行器（local/SSH/Docker） |
| 轻量DAG | **lythonic** | [walnutgeek/lythonic](https://github.com/walnutgeek/lythonic) | Python函数链式编排，`>>` 接线，SQLite追踪 |
| 本地DAG引擎+WebUI | **Dagu** | [dagucloud/dagu](https://github.com/dagucloud/dagu) | YAML DAG，Web UI，自带MCP Server，AI Agent友好 |

> ⚠ 旧方案 Nexus (`sontianye/nexus`) 已不可用，以上为2025-2026活跃替代。

**预期胶水代码：** 调 Maestro API 分解任务 -> 分给 Agent，约 50 行

### 共识/选举层——Agent 之间怎么达成一致

| ETO 需求 | 开源方案 | 链接 | 集成方式 |
|:---------|:---------|:-----|:---------|
| 多模型投票共识 | **VotingAI** 🏆 | [tejas-dharani/votingai](https://github.com/tejas-dharani/votingai) | 5种投票策略，加密验票，拜占庭容错，审计日志 |
| 轻量多LLM共识 | **LLM Council** | [gauravvij/llm_council](https://github.com/gauravvij/llm_council) | ~200行，并行查询多模型，投票/合成两种策略 |
| 结构化辩论+审计 | **Aragora** | [synaptent/aragora](https://github.com/synaptent/aragora) | Agent辩论→投票→决策收据，可审计溯源 |
| 协调员选举 | **raft-lite** 🏆 | [nikwl/raft-lite](https://github.com/nikwl/raft-lite) | 纯Python单文件Raft，Leader选举，网络层可换 |
| 协调员选举(备选) | **consensual** | [lycantropos/consensual](https://github.com/lycantropos/consensual) | 纯Python Raft，Leader选举+日志复制，PyPI可装 |

> ⚠ 旧方案 Aegean Consensus 和 Gravity AI 均不可用，以上为2025-2026活跃替代。

**预期胶水代码：** VotingAI 评分 + raft-lite 选举协调员，约 60 行

### 记忆层

| ETO 需求 | 开源方案 | 链接 | 集成方式 |
|:---------|:---------|:-----|:---------|
| 短期会话记忆 | **Pi JSONL 会话树** | Pi 内置 | 自动管理，ETO 不需要额外代码 |
| 长期语义记忆 | **@yylan/pi-memory** 🏆 | [npm](https://www.npmjs.com/package/@yylan/pi-memory) | `pi install npm:@yylan/pi-memory`，4层记忆+FTS5+向量 |
| 记忆+知识图谱 | **pi-mempalace** | [npm](https://www.npmjs.com/package/@sinamtz/pi-mempalace) | SurrealDB 3.0 HNSW，向量+图+时序 |
| 轻量语义记忆 | **pi-awareness-memory** | [npm](https://www.npmjs.com/package/pi-awareness-memory) | all-MiniLM嵌入，记忆衰减，Web仪表盘 |
| ~~agentmemory~~ | ❌ 已弃用 | — | 改为用 Pi 生态记忆扩展，更轻量更贴合 |
| 安全护栏 | **Hermes enforcer** | — | 已在用 |

---

## 二、建议的搭建顺序

```
Phase 1 (✅ 已完成):
第1步：[装 ProtoLink] 两个Agent通过HTTP A2A通信     ← ✅ ProtoLink v0.6.1 验证通过
     ↓
Phase 2 (🟡 进行中 — 旧方案已死，新替代就绪):
第2.1步：[接 Maestro] 输入任务，自动分解DAG步骤    ← pip install maestro
 或 [接 lythonic]  轻量Python函数链式编排          ← pip install lythonic
 或 [接 Dagu]      本地DAG引擎+WebUI               ← dagu init
     ↓
第3.1步：[接 VotingAI] 多Agent投票达成共识          ← pip install votingai
 或 [接 LLM Council] 轻量多模型并行评分              ← pip install llm-council
 或 [接 Aragora]    结构化辩论+审计溯源             ← pip install aragora
     ↓
第4.1步：[接 raft-lite] 纯Python Raft选举协调员     ← pip install raft-lite
 或 [接 consensual] 完整Raft实现(含日志复制)        ← pip install consensual
     ↓
第5步：[接 agentmemory] 共享记忆跨session持续       ← ✅ 已有的
     ↓
Phase 3-5 (📋 规划中):
第6步：动态自组织（弹性Agent池、自我修复）
第7步：进化学习（集体回顾、策略调整）
第8步：理论引擎（Active Inference、World Model）
```

---

## 三、怎么和编程 agent 描述需求

### 原则

| 别这么说 | 要这么说 |
|:---------|:---------|
| "帮我写一个多Agent编排框架" | "用 ProtoLink 让两个 Agent 通过 A2A 协议通信" |
| "实现一个共识协议" | "用 Aegean Consensus 库做多Agent投票" |
| "写个路由系统" | "用 Nexus 的 Adaptive 模式做任务路由" |

**核心就一句：告诉它用什么库、实现什么功能，而不是让它从头设计。**

### 标准模板

```
【目标】
在 Pi CLI 基础上，用 ProtoLink 实现两个 Agent 的 A2A 通信。

【已有环境】
- Pi CLI 已装 (v0.79.8)
- Python 3.11
- pip install protolink 可用

【具体要求】
1. Agent A 声明自己有 "web_search" 能力
2. Agent B 声明自己有 "code_write" 能力
3. 通过 A2A Agent Card 互相发现
4. A 搜到信息后通过 A2A Task 传给 B

【不要做的】
- 不要自己写通信协议
- 不要自己写 Agent 发现机制
- 不要造任何轮子

【验收标准】
跑一个 `etodemo "搜索XX API并写demo"` 能看到 A→B 的消息流转
```

### 针对不同编程 agent 的话术差异

**对 Claude Code：**
```
用 ProtoLink 的 A2A 实现。pip install protolink，按它的示例来。
不要自己写通信层。
```

**对 Codex CLI：**
```
先用 pip install protolink 装好，然后参考它的 README 示例。
目标：两个 Agent 能通过 A2A 发现对方并传任务。
```

**对 Cursor / Copilot：**
```
# 目标：用 ProtoLink 做 A2A 通信
# 约束：不造轮子，只用现成库
# 验收：跑通能看到 Agent A → Agent B 的消息
```

---

### 一句话原则总结

> **告诉编程 agent "用哪个库、做什么事"，而不是"写一个什么东西"。**
> 
> 好：`用 ProtoLink 的 A2A 实现两个 Agent 通信`
> 不好：`帮我写一个多 Agent 通信系统`
