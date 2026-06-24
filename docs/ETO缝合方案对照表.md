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
| 任务→DAG分解 | **Nexus** (Python) | [sontianye/nexus](https://github.com/sontianye/nexus) | 3种模式：Graph/Router/Adaptive，对应ETO的三种路由 |
| 智能路由 | 同上，Adaptive模式 = embedding匹配 | — | 自动按能力匹配Agent，不用手动写路由逻辑 |
| 多Agent团队 | **Open Multi-Agent** | [open-multi-agent/core](https://github.com/open-multi-agent/open-multi-agent) 6.4K⭐ | Goal→Task DAG，并行执行独立任务 |

**预期胶水代码：** 给 Nexus 一个任务，拿回分解结果 -> 分给 Agent，约 40 行

### 共识/选举层——Agent 之间怎么达成一致

| ETO 需求 | 开源方案 | 链接 | 集成方式 |
|:---------|:---------|:-----|:---------|
| 拜占庭容错投票 | **Aegean Consensus** | [hetu-project/aegean-consensus](https://github.com/hetu-project/aegean-consensus) | 每个Agent独立回答→投票→超阈值通过 |
| 协调员选举 | **Gravity AI** (Raft) | [dhiaayachi/gravity-ai](https://github.com/dhiaayachi/gravity-ai) | Raft选举 + 声誉加权 |

**预期胶水代码：** 任务完成后调Aegean投票，约 30 行

### 记忆层

| ETO 需求 | 方案 | 备注 |
|:---------|:-----|:-----|
| Agent共享记忆 | **agentmemory** | 已在用，接 A2A 上下文传递 |
| 安全护栏 | **Hermes enforcer** | 已在用 |
| 技能安检 | **SkillSpector** | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) 7K⭐，可选 |

---

## 二、建议的搭建顺序

```
Phase 1 (✅ 已完成):
第1步：[装 ProtoLink] 两个Agent通过HTTP A2A通信     ← ✅ ProtoLink v0.6.1 HTTP transport 验证通过
     ↓
Phase 2 (🟡 进行中):
第2步：[接 Nexus] 输入一个任务，自动分解步骤       ← pip install nexus
     ↓
第3步：[接 Aegean] 多Agent投票达成共识             ← pip install aegean-consensus
     ↓
第4步：[接 Gravity AI] Raft选举协调员              ← pip install gravity-ai
     ↓
第5步：[接 agentmemory] 共享记忆跨session持续      ← 已有的，接上就行
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
