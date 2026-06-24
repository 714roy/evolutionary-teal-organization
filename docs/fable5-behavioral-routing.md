---
type: design-spec
title: Fable-5 Behavioral Routing Module
description: 基于 513 个 Claude Code 系统提示词的动态行为路由——让异构 Agent 像 Claude Code 一样工作
tags: [fable-5, behavioral-routing, system-prompt, agent-behavior, orchestration]
timestamp: 2026-06-20
---

# 🪄 Fable-5 Behavioral Routing Module

> 不是让模型记住 Fable-5 提示词，而是在运行时动态注入最匹配的行为模式。

## 问题

异构 Agent（Claude / Qwen / DeepSeek / Reasonix）**不原生拥有 Claude Code 的行为能力**——不会自主调工具、不会分步思考、不知道什么时候该问用户。传统方案靠框架硬编码这些行为（Hermes Enforcer 的规则），但：

- 规则是静态的，无法适应不同任务场景
- Agent 没有「行为上下文」——它不知道现在该当工程师还是分析师
- 行为与执行逻辑耦合，改动成本高

## 方案：行为路由

把 513 个 Claude Code 系统提示词文件视为**行为模式库**，根据任务特征动态拼接注入：

```
                  ┌─ 通政司 · 三镜分析 ─┐
                  │ 格物/析理/合验        │
                  └──────────┬───────────┘
                             ↓
                  ┌─ 三体决策引力模型 ──┐
                  │ ☀️理体/🌙实体/⭐得体  │
                  └──────────┬───────────┘
                             ↓
                  ┌─ 🪄 Fable-5 行为路由 ──┐
                  │ 从 513 文件拼接身份     │
                  │ + 自主性 + 工具偏好      │
                  │ + 沟通方式 + 技能        │
                  └──────────┬───────────┘
                             ↓
                  ┌─ 注入目标 Agent ────┐
                  │ Agent 以 Fable-5    │
                  │ 行为模式执行任务      │
                  └────────────────────┘
                             ↓
                  ┌─ 智子治理层 ──────┐
                  │ 规则引擎/越界拦截    │
                  └────────────────────┘
```

## 行为模式库结构

513 个提示词文件按功能分为 **8 个行为维度**，路由模块按场景组合取用：

### 1. 身份声明（Identity）
| 文件 | 内容 | 场景 |
|:-----|:-----|:-----|
| `system-prompt-claude-fable-5-model-identity.md` | Fable-5 模型身份声明 | 所有场景默认加载 |

### 2. 行为框架（Harness）
| 文件 | 内容 | 注入时机 |
|:-----|:-----|:---------|
| `system-prompt-harness-instructions.md` | 核心行为规则——终端输出格式/权限模式/工具偏好/引用格式 | 始终注入 |
| `system-prompt-autonomy-instructions.md` | 自主性规则——何时主动行动/何时问用户 | 高自主性场景 |
| `system-prompt-communicating-with-user.md` | 用户沟通指令——如何呈现信息/何时追问 | 内容创作类任务 |

### 3. 工具描述（Tool Descriptions）
共 27 个文件，对应 Claude Code 的内置工具：

| 工具文件 | 功能 |
|:---------|:-----|
| `tool-description-bash.md` | Shell 命令执行 |
| `tool-description-write.md` | 文件写入 |
| `tool-description-edit.md` | 文件编辑 |
| `tool-description-search.md` | 代码搜索 |
| `tool-description-cron-create.md` | 定时任务创建 |
| ...（共 27 个） | |

**注入策略：** 根据任务检测到的工具需求，只注入相关工具描述，节省 token。

### 4. 行为技能（Skills）
| 文件 | 内容 | 触发条件 |
|:-----|:-----|:---------|
| `skill-debugging.md` | 调试方法论 | 任务含「bug/调试/修/报错」关键词 |
| `skill-code-review.md` | 代码审查流程 | 任务含「审查/审/review」关键词 |
| `skill-run-cli-tool-example.md` | CLI 工具使用范例 | 需要命令行操作时 |

### 5. 上下文提醒（System Reminders）
~40 个运行时注入的提醒块，**按会话阶段动态注入**：

| 阶段 | 注入什么 |
|:-----|:---------|
| 会话启动 | 上下文压缩提醒 |
| 工具调用前 | 工具选择偏好提醒 |
| 长对话 | 记忆/上下文边界提醒 |
| 错误恢复 | 重试策略提醒 |

## 行为模式模板

根据 ETO 的三体权重 + 三镜分析结果，路由模块预定义以下行为模式：

### 🛠️ 工程师模式（Coding & Debugging）
```
身份: fable-5-identity
框架: harness + autonomy（高自主）
工具: bash + write + edit + search + glob
技能: debugging + code-review
通讯: 简洁直接，把进度写在 markdown 里
```

### 📝 内容创作模式（Writing & Planning）
```
身份: fable-5-identity
框架: harness + communicating-with-user
工具: write + edit + search（只读）
技能: （无特殊技能）
通讯: 详细呈现，保留多个方案供选择
```

### 🔍 研究模式（Research & Analysis）
```
身份: fable-5-identity
框架: harness + autonomy（中自主）
工具: bash + search + glob + cron-create
技能: （无特殊技能）
通讯: 结构化呈现，标注信息来源
```

### ⚖️ 审计模式（Review & Compliance）
```
身份: fable-5-identity
框架: harness（低自主）
工具: read + search + glob（只读工具集）
技能: code-review
通讯: 结构化问题清单，标注严重程度
```

### 🤖 自动模式（Batch & Cron）
```
身份: fable-5-identity
框架: harness + auto-mode + autonomous-loop-check
工具: 全部工具（全权限）
技能: （无特殊技能）
通讯: 无用户交互，结果归档
```

## 路由决策引擎

```typescript
interface Fable5Route {
  identity: string[];        // 身份声明文件
  framework: string[];       // 行为框架文件
  tools: string[];           // 工具描述文件
  skills: string[];          // 行为技能文件
  reminders: string[];       // 上下文提醒文件
}

function routeBehavior(
  taskType: string,          // 通政司三镜输出
  weights: ThreeBodyWeights, // 三体权重
  userPreferences: string[]  // 用户历史偏好
): Fable5Route {
  // 1. 根据 taskType 选择基础模式模板
  const base = getBaseTemplate(taskType);
  
  // 2. 根据三体权重微调
  // 实体(🌙)权重高 → 加更多工具描述
  // 理体(☀️)权重高 → 加更多技能
  // 得体(⭐)权重高 → 加更多沟通指令
  
  // 3. 根据用户偏好追加
  // 用户喜欢详细输出 → 加 communicating-with-user
  
  return { ...base, ...adjustments };
}
```

## 与 ETO 其他组件的关系

| 组件 | 关系 |
|:-----|:------|
| **通政司·三镜** | 输出任务类型 → 行为路由的基础模式选择 |
| **三体决策** | 输出权重 → 行为路由的精细化调整 |
| **智子** | 行为路由输出**不经过智子**——智子只拦越界，不干预行为选择 |
| **Agent 池** | 行为路由的输出注入到每个 Agent 的系统提示词 |
| **TealContext** | 行为路由的决策日志写入 TealContext，供集体回顾参考 |

## 与传统 Route 的对比

| 维度 | 传统路由（Hermes Enforcer） | Fable-5 行为路由 |
|:-----|:---------------------------|:-----------------|
| 路由依据 | 关键词匹配 12 个板块 | 三镜 + 三体权重 + 用户历史 |
| 输出 | 选 skill | 拼装行为提示词 |
| 覆盖 | 固定 rule（19 条） | 513 个组合单元 |
| 扩展性 | 加规则 | 加提示词文件即可 |
| 模型无关 | 部分（依赖 Hermes） | 完全（只改 system prompt） |
| 溯源 | — | 响应末位添加 `<!-- routed-from: fable5://xxx -->` |

## 溯源标记

每次行为路由决策在响应末尾注入不可见标记，用于调试和行为复盘：

```
<!-- 
  fable5-route: coding@v2.1.178
  ids: [identity, harness, autonomy, tool-bash, skill-debugging]
  weights: {☀️:0.6, 🌙:0.2, ⭐:0.2}
  timestamp: 2026-06-20T22:00:00+08:00
-->
```

## 数据来源

行为模式库由 [Piebald AI](https://github.com/Piebald-AI/claude-code-system-prompts) 从 Claude Code npm 包提取。
- 版本：v2.1.178（2026-06-15）
- 数量：528 个提示词文件（2026-06-23 实测）
- 路径：`~/Nutstore/工坊/参考/claude-code-system-prompts/system-prompts/`
- qmd 索引：516 docs / 1220 vectors，支持语义搜索
