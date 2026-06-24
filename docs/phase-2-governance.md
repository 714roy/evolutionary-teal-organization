---
phase: 2
title: 动态编排与共识缝合
codename: "动态协调"
depends_on: phase-1
status: partial-done
---

# Phase 2：动态编排与共识缝合

> 在 A2A 通信层之上，实现 Coordinator 驱动的动态编排——任务拓扑由 LLM 实时决定，不是写死的 pipeline。

---

## 一、范围

### 做的

| # | 事项 | 说明 | 状态 |
|:-|:-----|:------|:-----|
| 1 | **Coordinator Agent** | 接收任务 → LLM 生成 Plan JSON，拓扑由模型实时决定 | ✅ 通过 |
| 2 | **Plan 执行引擎** | 读 Plan → 按步骤调度各 Agent，支持 depends_on 依赖注入 | ✅ 通过 |
| 3 | **Mock + Ollama 双模式** | 无依赖可测 Mock，真实模式用 qwen2.5-coder:7b | ✅ 通过 |
| 4 | **动态拓扑验证** | 简单任务 → direct（一步），复杂任务 → sequential（多步协作） | ✅ 通过 |
| 5 | **agentmemory 共享记忆** | 接上 A2A 上下文传递 | 📋 进行中 |
| 6 | **SkillSpector 技能安检** | Agent 执行前检查权限和工具边界 | 🟡 待做 |
| 7 | **MCP 工具接入** | Agent 通过 MCP 协议调用外部数据源/工具（文件、搜索、数据库等） | 🟡 待做 |
| 8 | **Skill 加载与运行** | Agent 按需加载 skill 来扩展能力（SkillSpector 安检后加载） | 🟡 待做 |

### 不做的

| 事项 | 理由 |
|:-----|:------|
| ❌ Nexus/Aegean/Gravity AI | 实际验证后发现这些仓库与描述不符或不适用（见下文） |

---

## 二、实际执行情况

### 缝合方案仓库验证（2026-06-23）

缝合方案中推荐的仓库，经逐一实际验证：

| 方案推荐 | 实际状态 | 结论 |
|:---------|:---------|:-----|
| **Nexus** (sontianye/nexus) | 4⭐，空壳项目，无 README、无代码 | ❌ 不可用 |
| **Aegean Consensus** (hetu-project) | 2⭐，实验性项目，release 未发布 | ❌ 不可用 |
| **Gravity AI** (dhiaayachi) | 4⭐，Go 语言，不是 Python | ❌ 无法集成 |
| **Open Multi-Agent** (6.4K⭐) | ✅ 真实的 TypeScript 项目，npm 可装 | ✅ 可选但需要 Node.js 桥接 |
| **ProtoLink** | ✅ v0.6.1 已验证可用 | ✅ 已验证 |

### 结论

缝合方案的仓库信息有部分不准确。实际可行的路径是：

> **Coordinator prompt → Plan JSON → 执行引擎调度**

这不需要任何额外依赖——就是 LLM 实时生成 Plan + 一个不到 50 行的执行器。ProtoLink 用于 Agent 注册发现和 A2A 通信，LLM 调用直走 API（绕过 ProtoLink 的 action validation）。

---

## 三、已通过的原型

### 测试文件

`~/.eto/a2a/tests/test_dynamic.py`

### 验收结果

| # | 测试 | 输入 | 结果 |
|:-|:-----|:------|:-----|
| T1 | 单步任务 | `"写斐波那契函数"` | ✅ Coordinator 生成 direct → coder 一步完成 |
| T2 | 多步协作 | `"调研 asyncio 并写 demo"` | ✅ researcher 调研 → coder 编码，两步协作 |
| T3 | Mock 模式 | 同上 | ✅ 静态回复，无依赖 |
| T4 | Ollama 模式 | 同上 | ✅ qwen2.5-coder:7b 实时推理 |

### 生成的 Plan 示例

```json
// 简单任务 → direct（一步到位）
{
  "reasoning": "这是一个单步编码任务",
  "steps": [{"type": "direct", "agent": "coder", "task": "写斐波那契函数", "depends_on": []}]
}

// 复杂任务 → sequential（多步协作）
{
  "reasoning": "需要先调研再编码，两步协作",
  "steps": [
    {"type": "direct", "agent": "researcher", "task": "调研 asyncio", "depends_on": []},
    {"type": "direct", "agent": "coder", "task": "写 demo", "depends_on": [0]}
  ]
}
```

拓扑由 LLM 实时决定。不同的任务产生不同的拓扑。

---

## 四、当前架构

```
用户任务
  │
  ▼
Coordinator (LLM)
  │  生成 Plan JSON（拓扑由 LLM 实时决定）
  ▼
┌─ 执行引擎 ──────────────────────────────────┐
│  读 Plan → 按步骤调度                       │
│  ┌ direct: 一步到位                          │
│  ├ sequential: 多步协作（depends_on 链）      │
│  └ parallel: 独立子任务并行（待实现）          │
|  │                                              │
│  每步:                                       │
│  Registry 发现 Agent → 调 LLM → 存结果       │
│  支持 MCP 工具调用  ·  支持 Skill 按需加载    │
└──────────────────────────────────────────────┘
  │
  ▼
┌─ MCP / Skill 层（待实现）────────────────────┐
│  Agent 通过 MCP 协议调用外部工具               │
│  · 文件系统 · 搜索 · 数据库 · API             │
│  Agent 按需加载 skill 扩展能力                  │
│  · SkillSpector 安检 → 加载 → 运行             │
└──────────────────────────────────────────────┘
  │
  ▼
ProtoLink Registry (HTTP)
  ├── researcher (调研)
  ├── coder (编码)
  └── (可扩展更多 Agent)
```

---

## 五、(Phase 4 前置) 路由模型：轻量分拣 + 推理拆解两层

当前 Coordinator 直接用 LLM 做 Plan，但三镜分拣（分类任务类型）和 Plan 拆解（分解步骤）其实用不同计算量：

### 两层路由架构

```
用户任务
  │
  ▼
┌─ Layer 1：轻量路由（分类/分拣）─────────────┐
│  用 embedding + 规则/小模型做三镜分拣           │
│  分类：代码 / 文本 / 分析 / 调研 / 工具调用     │
│  判断：direct（一步） / plan（多步拆解）         │
│  产出：任务类型标签 + 路由模式决策              │
│                                                 │
│  候选模型：BGE-M3(568M) / TinyAgent-1.1B       │
│  特点：几MB嵌入匹配，瞬时完成，几乎零VRAM       │
└────────────────┬────────────────────────────────┘
                 │ 如果是 plan 模式
                 ▼
┌─ Layer 2：推理拆解（复杂任务分解）────────────┐
│  用推理模型做子任务分解                          │
│  输入：用户原始需求 + 三镜标签                   │
│  产出：Plan JSON（steps + agent + depends_on）  │
│                                                 │
│  候选模型：VibeThinker-3B ⭐（AIME 94.3）       │
│           Qwen3.5-9B（综合更强）                 │
│  特点：3B/500M 激活级推理，5090 上近乎免费      │
└─────────────────────────────────────────────────┘
```

### 对比：当前实现 vs 两层方案

| 维度 | 当前（单 LLM） | 两层方案 |
|:-----|:--------------|:---------|
| 简单任务 | LLM 也要加载，Plan 简单但推理成本不变 | embedding 匹配，<10ms 出 direct 决策 |
| 复杂任务 | LLM 拆解深度够 | VibeThinker-3B 数学级推理拆得更准 |
| 5090 多模型 | LLM 占着 VRAM | 轻量层几乎不占，VibeThinker 推理时才加载 |
| 可观测性 | LLM 黑盒输出 | 三镜标签可审计，路由决策可追溯 |
| 依赖 | 一个 LLM 做所有 | embedding 模型 + 推理模型，松耦合 |

### 适用场景判断

| 用户输入 | Layer 1 分类 | 走哪层 |
|:---------|:------------|:-------|
| "写个斐波那契函数" | 代码·简单 | ✅ 直接 direct，不走 Layer 2 |
| "帮我分析这份财报" | 分析·中等 | ✅ direct 或用 Layer 2 拆 question list |
| "调研 asyncio 并写 demo" | 调研+编码·复杂 | 🔄 Layer 2 拆为调研→编码两步 |
| "做一个全栈项目：用户系统+支付+通知" | 全栈·极复杂 | 🔄 Layer 2 拆出 DAG，3+ 个子任务 |

### 备注

- Phase 2 当前用单 LLM 做 Coordinator，这是正确的"Make it work"阶段选择
- 两层路由是 Phase 4 的优化项——等 Phase 3 的多 Agent 并行跑起来后，路由层才会成为瓶颈
- 届时 VibeThinker-3B 可在 5090 上常驻推理，与 OCR/Agent 等其他模型共存

---

## 六、(Phase 4 前置) 多模型共识：Fusion 类方案

### 背景

OpenRouter Fusion 是一种多模型共识架构——面板模型并行回答，judge 模型对比分析（共识/矛盾/盲区），然后合成最终答案。跟我们的 Consilium PID（三模型交叉验证纠错）互补：Fusion 做加法（多视角更全），Consilium 做减法（互检更准）。

### 开源实现

两个已拉取到本地参考目录：

| 项目 | 路径 | 特点 |
|:-----|:-----|:------|
| **openfusion** | `工坊/参考/openfusion/` | MIT，drop-in 代理，改 `model: "openfusion"` 即用，支持 debate 多轮策略 |
| **fusion-engine** | `工坊/参考/fusion-engine/` | Python 库，自定义 judge prompt（纯 markdown 模板），逐模型成本/延迟追踪，评测框架 |

### 如何融入 ETO

| ETO 环节 | 用什么 | 原因 |
|:---------|:-------|:------|
| **三体赋权**（实体=事实调研） | Fusion | 多模型并行搜+分析，给出全面全景 |
| **合验镜**（产出审查） | Consilium PID | 纠错，确保正确性 |
| **青色共识协议**（ETO-016 投票） | Fusion 的 vote/ranked 聚合器 | 多 Agent 对提议评分时，Fusion 的聚合策略可直接复用 |
| **复杂 Plan 拆解** | Fusion + VibeThinker | 多个小模型拆 Plan，judge 合成最优方案 |

### 备注

- 两个项目都已拉取，Phase 4 启动 Fusion 相关开发时可直接参考
- openfusion 的 debate 策略（模型互看答案后重新回答）值得关注——ETO 的青色共识协议（最 3 轮反馈调整）在逻辑上类似
- Fusion Engine 的评测框架可直接用于 ETO 的 consilium 评估

---

## 七、未完成的

| 事项 | 说明 |
|:-----|:------|
| parallel 模式 | 当前 only 实现了 direct/sequential |
| consensus 模式 | 需要 Aegean 或类似实现投票 |
| agentmemory 集成 | 结果写回记忆层，影响下次选举 |
| ProtoLink A2A handle_task | 当前 Agent 直调 LLM，不是通过 handle_task 通信 |
| Agent 独立 HTTP 服务 | 当前在同一个进程里，应独立部署 |
| election 选举 | Coordinator 当前固定为"我"，没有临时选举机制 |
| MCP 工具接入 | Agent 尚未能通过 MCP 协议调用外部工具（文件/搜索/数据库/API） |
| Skill 加载机制 | SkillSpector 安检 → 加载 → 运行的完整链路未实现 |
| Skill 模板库 | 缺乏标准化的 skill 定义格式和注册机制 |

---

## 六、关键设计决策

| 决策 | 选择 | 理由 |
|:-----|:------|:------|
| 动态编排方式 | Coordinator prompt → Plan JSON | 零依赖，最灵活 |
| LLM 调用方式 | 直接 API（不经过 ProtoLink action validation） | ProtoLink v0.6.1 只支持 structured action，不支持纯文本输出 |
| Plan 格式 | JSON（含 type/agent/task/depends_on） | 通用、可扩展 |
| 执行引擎 | < 50 行 Python，无框架 | Ponytail：够用就行 |
| Pi CLI 的角色 | "最后一步的执行器" | 编排不依赖 Pi，Pi 只做具体工作 |
