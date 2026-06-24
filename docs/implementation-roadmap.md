---
type: roadmap
title: ETO 实现路线图（缝合方案）
description: 不写框架，只缝已有开源项目——ProtoLink + Nexus + Aegean + Gravity AI + agentmemory
tags: [eto, roadmap, stitching, ponytail]
timestamp: 2026-06-23
---

# ETO 实现路线图（缝合方案）

> **核心理念：** ETO 不写框架，它的"代码"是胶水——把 ProtoLink、Nexus、Aegean、Gravity AI、agentmemory 这些开源项目串起来。
>
> **Ponytail 原则：** 代码量越少越好，不重复造轮子。

---

## 技术栈分层

```
Pi CLI（入口 — 最后一步的执行器）
  |
  v
+-----------------------------------------+
|         A2A 通信层 (ProtoLink)           |
|  Agent Card · Registry · 发现 · 路由     |
+-----------------------------------------+
|         编排层 (Nexus)                   |
|  Goal -> Task DAG · 3 种路由模式          |
+-----------------------------------------+
|         共识层 (Aegean 投票)              |
|  提案 -> 广播 -> 独立推理 -> 超阈值通过    |
+-----------------------------------------+
|         选举层 (Gravity AI)              |
|  Raft 共识 · 声誉加权选举                 |
+-----------------------------------------+
|         记忆层 (agentmemory)             |
|  共享记忆 · 跨 Session 延续 · LRU 修剪   |
+-----------------------------------------+
|         安全层 (SkillSpector)            |
|  工具越界检测 · 权限控制                 |
+-----------------------------------------+
```

### 为什么每层选这个方案

| 层 | 选型 | 引用 | 为什么不自己写 |
|:--|:-----|:-----|:--------------|
| 通信 | **ProtoLink / A2A** | 24K⭐，Google/Linux 基金会 | 自写 Agent 间通信协议是巨大的工程 |
| 路由 | **Nexus** | 6.4K⭐，3 种路由内置 | 自写路由逻辑最后会越来越像 Nexus |
| 共识 | **Aegean Consensus** | 拜占庭容错 | 共识算法是计算机科学最难的部分之一 |
| 选举 | **Gravity AI (Raft)** | Raft 是工业标准 | 自写选举最后会越来越像 Raft |
| 记忆 | **agentmemory** | 已在用 | 零额外成本 |
| 安全 | **SkillSpector** | 7K⭐，NVIDIA | 安全规则引擎是另一个大工程 |

---

## 阶段总览

| 阶段 | 名称 | 核心交付 | 状态 |
|:-----|:------|:---------|:-----|
| **Phase 1** | A2A 通信层奠基 | ProtoLink HTTP Transport + Registry 验证 | **完成** |
| **Phase 2** | 编排与共识缝合 | Nexus + Aegean + Gravity AI 三件套 | 进行中 |
| **Phase 3** | 动态自组织 | 网状协作·弹性 Agent 池·自我修复 | 规划中 |
| **Phase 4** | 进化学习 | 集体回顾·策略调整·成本报告 | 规划中 |
| **Phase 5** | 理论引擎 | Active Inference · JEPA 集成 | 研究 |

---

## Phase 1：A2A 通信层奠基

> 已通过。详见 [phase-1-core-loop](phase-1-core-loop.md)。

| 里程碑 | 验收 | 状态 |
|:-------|:-----|:-----|
| ProtoLink 安装 | `pip install protolink` | 完成 |
| Agent invoke 功能 | `agent.invoke("hello")` 返回结果 | 完成 |
| HTTP Transport | Agent HTTP 启动 + Registry 注册 | 完成 |
| 跨 Agent 通信 | Agent A -> B A2A POST /tasks/ | 完成 |

---

## Phase 2：编排与共识缝合

> 核心任务。见 [phase-2-governance](phase-2-governance.md)。

```
第 1 步：pip install nexus -> 调通 route()
第 2 步：pip install gravity-ai -> 调通 elect()
第 3 步：pip install aegean-consensus -> 调通 vote()
第 4 步：接 agentmemory（已有）
第 5 步：全部串起来 -> end-to-end demo
```

**关键指标：** 每个 `pip install` 是一个检查点——验证能在 Windows 上正常使用再继续下一步。

---

## Phase 3：动态自组织

> 网状协作。见 [phase-3-routing](phase-3-routing.md)。

```
第 1 步：Registry 心跳 -> Agent 上下线自动感知
第 2 步：Router Adaptive 模式 -> embedding 匹配
第 3 步：Parallel + Pipeline -> 分叉执行
第 4 步：Gravity AI 接 agentmemory -> 历史感知选举
第 5 步：超时检测 + 自动重路由
第 6 步：知识蒸馏 + 集体回顾
```

---

## Phase 4：进化学习

> 系统从自己的执行历史中学习。见 [phase-4-evolution](phase-4-evolution.md)。

```
第 1 步：agentmemory -> 聚类失败模式
第 2 步：策略调整 -> 修改选举/路由权重
第 3 步：SkillSpector 规则去活
第 4 步：记忆修剪 -> 回顾报告
第 5 步：多渠道输出 + 成本报告
```

---

## Phase 5：理论引擎

> 认知科学集成。见 [phase-5-theory](phase-5-theory.md)。

```
第 1 步：agentmemory 加 prediction_error 字段
第 2 步：精度自动调整（连续成功/失败 -> 权重变化）
第 3 步：软先验推翻（规则可被证据推翻）
第 4 步：World Model rollout（潜空间模拟路由）
```

---

## 代码量预期

| 方法 | 代码量 | 维护成本 | 鲁棒性 |
|:-----|:------|:---------|:-------|
| 自写框架 | ~1569 行 | 高（全部自己修） | 低（一次没跑过） |
| **缝合方案** | **~90 行胶水代码** | 低（社区维护核心库） | 高（每个库各自有测试） |

---

## 决策记录

| 决策 | 选择 | 理由 |
|:-----|:------|:------|
| 通信协议 | A2A (ProtoLink) | 业界标准，不发明协议 |
| 编排引擎 | Nexus | 比自写路由健壮，3 种模式即用 |
| 共识协议 | Aegean Consensus | 拜占庭容错，工业级 |
| 选举算法 | Gravity AI (Raft) | 比 Jaccard 关键词匹配好得多 |
| 记忆层 | agentmemory | 已在用，零额外成本 |
| 安全层 | SkillSpector (NVIDIA) | 7K⭐，专业安全规则引擎 |
| Pi CLI 角色 | 最后一步的执行器 | 编排不依赖 Pi，Pi 只做具体工作 |
