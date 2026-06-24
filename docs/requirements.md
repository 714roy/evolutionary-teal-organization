---
type: requirements
title: 进化型青色组织 · 需求文档（v1.0）
description: 基于青色三原则 + Pi+DW 技术栈的功能需求、非功能需求、用户故事与进化路径
tags: [requirements, teal-organization, pi, dynamic-workflows, three-body]
timestamp: 2026-06-21
resource: https://github.com/reoroy/evolutionary-teal-organization
---

# 进化型青色组织 · 需求文档

> 版本：v1.0
> 技术栈：Pi (pi-mono) Agent 运行时 + Dynamic Workflows 编排层

---

## 一、产品定位

进化型青色组织（ETO）是一个 **Multi-Agent 青色协作架构**，基于 Laloux 青色组织三原则设计。它不是又一个 AI Agent 产品——它是**关于如何让多个异构 Agent 以组织制度协作的架构设计**。

### 青色三原则

| 原则 | 含义 | 系统需求 |
|:-----|:------|:---------|
| **自主管理** | 没有固定主控，Agent 通过共识自组织 | 临时协调员选举 + 共识决策协议 |
| **完整性** | 所有 Agent 共享上下文，不孤立决策 | TealContext 共享记忆池 |
| **进化使命** | 系统从失败中学习，自适应调整 | 集体回顾循环 + 策略权重动态更新 |

### 技术栈分层

```
ETO 架构层 — 组织制度（共识/选举/回顾/治理）
─────────────────────────────────────
Dynamic Workflows — 多 Agent 编排引擎
─────────────────────────────────────
Pi (pi-mono) — Agent 运行时
```

### 使用场景

| 场景 | 路由逻辑 | 示例 |
|:----|:---------|:------|
| 快速查询 | 通政司判 direct → 单次 Pi 调用 | 查天气、查余额 |
| 调研报告 | 三体权重 → MODE=research | 行业竞争分析 |
| 方案设计 | 三体权重 → MODE=build | APP 设计、系统架构 |
| 争议分析 | 三体权重 → MODE=debate | 技术选型评估 |
| 综合任务 | 三体权重 → MODE=full | 创业方案、人生规划 |
| 持续监控 | 通政司判 loop=watch | 盯 repo 更新 |
| 定时任务 | 通政司判 loop=cron | 每日简报 |

---

## 二、功能需求

### 模块 A：入口与任务分析

#### FR-A1 入口 CLI
- **FR-A1.1** 接受自然语言任务描述（参数或 stdin）
- **FR-A1.2** 根据 ROUTE 分流：direct → 快速回答 / pipeline → 编排执行
- **FR-A1.3** 支持 `--mode` 参数手动指定 MODE 覆盖通政司判断

#### FR-A2 通政司（三镜分析）
- **FR-A2.1** 用三镜分析法判断任务本质：格物（产出形态）/ 析理（受众）/ 合验（定制化程度）
- **FR-A2.2** 输出 ROUTE=direct|pipeline 路由决策
- **FR-A2.3** 输出三体权重 `[☀️理体, 🌙实体, ⭐得体]` 作为后续决策输入
- **FR-A2.4** 输出置信度评分（0-1），用于权重学习

#### FR-A3 三体决策引力模型
- **FR-A3.1** 根据三体权重映射为 MODE：research | build | debate | full | direct
- **FR-A3.2** 支持恒纪元（稳定权重）和乱纪元（权重拉扯）两种模式
- **FR-A3.3** 乱纪元时自动增加 REWORK 轮次和审核深度
- **FR-A3.4** 通政司置信度随历史执行结果自动调整

---

### 模块 B：完整性基础设施

#### FR-B1 TealContext 共享记忆池
- **FR-B1.1** 提供全局记忆池（global_memory），存储 Agent 执行记录
- **FR-B1.2** 提供活跃提议池（active_proposals），跟踪当前流转的提议
- **FR-B1.3** 提供共识日志（consensus_log），完整记录决策链
- **FR-B1.4** Agent 执行前调用 `perceive()` 获取上下文
- **FR-B1.5** Agent 执行后调用 `record()` 记录结果
- **FR-B1.6** 记忆自动修剪（上限 1000 条，LRU 淘汰）
- **FR-B1.7** 跨会话持久化（JSON → SQLite 渐进迁移）

#### FR-B2 Fable-5 行为路由
- **FR-B2.1** 维护行为模式库索引（5 类：工程师/创作者/研究员/审计员/自动）
- **FR-B2.2** 根据通政司输出 + 三体权重动态拼接 Agent system prompt
- **FR-B2.3** 支持溯源标记（响应末尾注入路由决策信息）
- **FR-B2.4** 90% 走最优路由 + 10% 随机探索

---

### 模块 C：自主管理机制

#### FR-C1 临时协调员选举
- **FR-C1.1** 任务到达时从 Agent 池中动态选举协调员
- **FR-C1.2** 选举公式：`match_score(Agent, task) × (1 - busy_ratio)`
- **FR-C1.3** match_score 基于 Agent 专长 + 历史同类任务成功率
- **FR-C1.4** busy_ratio 反映当前负载（运行中任务 / 最大并发）
- **FR-C1.5** 任务完成 → 协调员角色自动解散

#### FR-C2 共识决策协议
- **FR-C2.1** 协调员发起提议，广播给受影响 Agent
- **FR-C2.2** 每个 Agent 返回 `(score, concern)` — 评分（0-1）+ 担忧（可选）
- **FR-C2.3** 共识过滤：平均评分 > 0.6 且无 CRITICAL 否决 → 执行
- **FR-C2.4** 评分不足或有否决 → 协调员根据反馈调整 → 重提议（最多 3 轮）
- **FR-C2.5** 超时熔断（10s 无响应）→ 降级为本地默认执行
- **FR-C2.6** 每轮决策写入 TealContext.consensus_log

#### FR-C3 死锁防护
- **FR-C3.1** 同一提议循环 3 轮 → 智子标记死锁 → 建议人工介入
- **FR-C3.2** 智子可在共识检查点发出 CRITICAL 否决
- **FR-C3.3** 否决原因写入审计日志

---

### 模块 D：治理与安全

#### FR-D1 智子规则引擎
- **FR-D1.1** 规则以 YAML 配置，支持热重载
- **FR-D1.2** 规则类型：pre_execution（执行前）/ post_execution（执行后）/ consensus（共识点）
- **FR-D1.3** 规则动作：veto（拦截）/ warn（警告）/ log（记录）
- **FR-D1.4** CLI 命令：`rule list/add/remove/test/toggle`

#### FR-D2 审计日志
- **FR-D2.1** 所有决策事件记录到 `~/.eto/audit/`
- **FR-D2.2** 支持按时间 / Agent / 事件类型筛选查询
- **FR-D2.3** 日志格式：JSON Lines，按日期分文件

#### FR-D3 权限与预算
- **FR-D3.1** 角色权限绑定（`permit --role=礼部 --allow=web_search`）
- **FR-D3.2** 任务级预算帽（`budget --cap=$0.05`）
- **FR-D3.3** 预算超额自动终止 pipeline

---

### 模块 E：进化与学习

#### FR-E1 集体回顾循环
- **FR-E1.1** 每 N 轮任务自动触发集体回顾
- **FR-E1.2** 高失败率（最近 5 轮失败 > 3）自动触发
- **FR-E1.3** 支持手动触发：`eto reflect`
- **FR-E1.4** 回顾分析：聚类失败记录 → 识别模式 → 调整策略权重
- **FR-E1.5** 输出回顾报告（发现 + 调整 + 建议）

#### FR-E2 Loop 系统
- **FR-E2.1** 通政司自动检测任务中的循环意图
- **FR-E2.2** 支持四种 Loop：Rework / Iteration / Watch / Cron
- **FR-E2.3** LoopContext 统一接口：type/round/maxRounds/artifacts
- **FR-E2.4** maxRounds = -1 表示无限循环

---

## 三、非功能需求

### NFR1：成本控制

| 模式 | 预估成本 | 说明 |
|:-----|:---------|:------|
| direct（快速直达） | ~$0.001-0.002 | 单次 Pi Agent 调用 |
| research（调研） | ~$0.005-0.01 | 调研 + 交叉验证 |
| build（构建） | ~$0.01-0.02 | 方案 + 编码 + 审查 |
| full（全流程） | ~$0.02-0.05 | 多 Agent 全链 |
| consensus（含共识迭代） | ~$0.03-0.08 | 多轮共识 + 调整 |
| loop（持续任务） | 按执行次数累加 | Watch/Cron 按次计费 |

### NFR2：响应时间

| 模式 | 目标 | 说明 |
|:-----|:------|:------|
| direct | < 30s | 单次 LLM 调用 |
| research | 1-3min | 调研 + 核验 + 输出 |
| build | 2-5min | 方案 + 编码 + 审查 |
| full | 3-10min | 全流程多 Agent |
| consensus 迭代 | +30s-1min/轮 | 每轮共识增加 |

### NFR3：可扩展性

- Agent 类型可通过 Pi 配置动态添加
- Pipeline 拓扑可通过三体权重动态生成（无需硬编码）
- 智子规则可通过 YAML 文件扩展
- Fable-5 行为模式可通过提示词文件扩展

### NFR4：可观测性

- 智子审计日志可查询
- TealContext 状态可导出
- 集体回顾报告可查看
- 通政司置信度历史可追溯

---

## 四、技术架构

### 分层架构

```
┌─────────────────────────────────────────┐
│         入口 CLI (eto.sh / eto)          │
│    自然语言 → 通政司 → ROUTE 分流        │
├─────────────────────────────────────────┤
│         Dynamic Workflows 编排层         │
│  ┌──────────────────────────────────┐   │
│  │  JS 编排脚本 / subagent 调度     │   │
│  │  上下文传递 / 并行执行 / 结果校验 │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│     Pi Agent 运行时                     │
│  ┌──────────────────────────────────┐   │
│  │  通政司 Agent  │  执行 Agent     │   │
│  │  审计 Agent    │  审查 Agent     │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│         基础设施层                       │
│  TealContext  │ 智子规则  │ 审计日志   │
└─────────────────────────────────────────┘
```

### 数据流

```
用户 → 入口 CLI
        │
        ▼
   通政司 (Pi Agent) ──→ 三镜分析 + 三体权重
        │
   ┌────┴────┐
   │         │
direct    pipeline
   │         │
   ▼         ▼
Pi 直接回答  DW 编排脚本
              │
         ┌────┼────┬────┬────┐
         ▼    ▼    ▼    ▼    ▼
       Agent A  B  C  D (Pi configured sub-agents)
         │    │    │    │    │
         └────┴────┴────┴────┘
              │
              ▼
          智子审计 + TealContext 记录
              │
              ▼
          集体回顾 (周期性)
```

---

## 五、用户故事

### US1：快速查天气
> "查下今天天气"
> → 通政司判 ROUTE=direct
> → Pi Agent 直接回答 → 智子审计 → 归档

### US2：深度调研报告
> "写一份 2025 年 AI Agent 行业竞争分析"
> → 通政司判 ROUTE=pipeline, 三体权重 {☀️:0.6, 🌙:0.8, ⭐:0.3} → MODE=research
> → DW 编排：调研 Agent → 核验 Agent → 输出 Agent → 审计 Agent → 归档
> → 写入 TealContext

### US3：技术选型争议
> "React 还是 Vue 更适合我们的新项目？"
> → 通政司判 ROUTE=pipeline, 三体权重 {☀️:0.7, 🌙:0.5, ⭐:0.6} → MODE=debate
> → DW 编排：双方调研 → 对比分析 → 建议输出
> → 智子审计确保客观性

### US4：共识决策
> "这个 API 设计方案需要团队评审"
> → 临时协调员选举 → 发起提议
> → 广播给相关 Agent → 收集评分 → 共识过滤
> → 通过→执行 / 未通过→调整重提议
> → TealContext 记录完整决策链

### US5：持续监控
> "帮我盯着这个 GitHub repo，有新 issue 就分析"
> → 通政司判 loop=watch
> → DW 部署监控 Agent，事件触发时跑 Pipeline
> → 每次执行写入 TealContext

---

## 六、进化路径

### 🟤 阶段 S1-S3：Amber 基础设施

| 需求 | 对应阶段 | 说明 |
|:-----|:--------|:------|
| FR-A1, FR-A2 | S1 | 入口 CLI + 通政司原型 |
| FR-B1 | S2 | TealContext 共享记忆池 |
| FR-D1, FR-D2, FR-D3 | S3 | 智子规则引擎 + 审计 + 权限 |

### 🟠 阶段 S4-S5：Orange 动态路由

| 需求 | 对应阶段 | 说明 |
|:------|:--------|:------|
| FR-B2 | S4 | Fable-5 动态行为路由 |
| FR-A3, FR-A2.4 | S5 | 三体决策引力模型 + 置信度学习 |
| FR-E2 | S5 | Loop 系统（Rework/Iteration/Watch/Cron） |

### 🟢 阶段 S6：Green 共识驱动

| 需求 | 对应阶段 | 说明 |
|:------|:--------|:------|
| FR-C1 | S6 | 临时协调员选举 |
| FR-C2, FR-C3 | S6 | 共识决策协议 + 死锁防护 |

### 🦋 阶段 S7+：Teal 青色进化

| 需求 | 对应阶段 | 说明 |
|:------|:--------|:------|
| FR-E1 | S7 | 集体回顾循环 |
| — | S8+ | Active Inference / JEPA 集成 |
| — | S8+ | 自生成 Pipeline 拓扑 |

---

*本文档对应 design-spec v0.28，基于 Dynamic Workflows + Pi 技术栈。*
