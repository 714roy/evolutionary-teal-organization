---
type: bundle
title: Evolutionary-Teal Organization (ETO)
description: 多 Agent 青色组织架构——自主管理·完整性·进化使命
tags: [multi-agent, teal-organization, orchestration, a2a, stitching]
timestamp: 2026-06-23
---

# Evolutionary-Teal Organization (ETO)

> Multi-Agent 青色组织架构设计 —— 不写框架，只缝已有开源项目。

## 项目定位

ETO 不是"写一个多 Agent 编排框架"，而是**把已有的开源项目粘起来**，形成青色组织架构。

| 层 | 开源方案 | 替换了什么 |
|:--|:---------|:----------|
| 通信 | **ProtoLink** (A2A 协议) | 自写通信层 |
| 路由 | **Nexus** (3 种路由模式) | 自写 analyze.py |
| 共识 | **Aegean Consensus** (拜占庭投票) | 自写 consensus.py |
| 选举 | **Gravity AI** (Raft + 声誉加权) | 自写 election.py |
| 记忆 | **agentmemory** (已在用) | 自写 context.py |
| 安全 | **SkillSpector** (NVIDIA, 7K⭐) | 自写 zhizi.py |

胶水代码目标：< 500 行。

## 当前状态

- **Phase 1：A2A 通信层** ✅ 已完成——ProtoLink HTTP transport + Registry 验证通过
- **Phase 2：编排+共识缝合** ⏳ 进行中——下一步
- **Phase 3-5：** 规划中

## Contents

- [README](README.md) — 项目概览
- [缝合方案对照表](ETO缝合方案对照表.md) — 各层开源项目对照
- [docs/design-spec](docs/design-spec.md) — 架构设计概念
- [docs/positioning-and-strategy](docs/positioning-and-strategy.md) — 竞品分析与战略蓝图
- [docs/alternative-paradigms-to-eto](docs/alternative-paradigms-to-eto.md) — 替代范式映射
- [docs/implementation-roadmap](docs/implementation-roadmap.md) — 实现路线图
- [docs/eto-feature-list](docs/eto-feature-list.md) — 特性清单（58 特性）
- [docs/requirements](docs/requirements.md) — 需求文档
- [docs/eto-ecosystem-tools](docs/eto-ecosystem-tools.md) — 生态工具

### Phase 文档

- [docs/phase-1-core-loop](docs/phase-1-core-loop.md) — ✅ **Phase 1：A2A 通信层奠基**（已通过）
- [docs/phase-2-governance](docs/phase-2-governance.md) — 🟡 **Phase 2：编排与共识缝合**（规划中）
- [docs/phase-3-routing](docs/phase-3-routing.md) — 🟡 **Phase 3：动态自组织**（规划中）
- [docs/phase-4-evolution](docs/phase-4-evolution.md) — 🟠 **Phase 4：进化学习**（规划中）
- [docs/phase-5-theory](docs/phase-5-theory.md) — ⭐ **Phase 5：理论引擎**（研究阶段）

### 历史参考

- [docs/缝合方案对照表](ETO缝合方案对照表.md) — 各层开源项目详细对照
- [docs/handover-2026-06-22](docs/handover-2026-06-22.md) — 项目交接文档（历史状态）
- [docs/handover-git-diff-2026-06-22](docs/handover-git-diff-2026-06-22.patch) — 交接时 git diff

---

## 🛠️ 开发纪律（Reasonix Skills）

| Skill | 一句话 | 调用方式 |
|:------|:-------|:---------|
| **TDD-AI** | 没测试不写代码 | `/tdd-ai` |
| **Millstone** | 写完必须有人审 | `/millstone` |
| **Planwright** | 先想清楚再动手 | `/planwright` |
| **Trammel** | 知道代码怎么拼在一起 | `/trammel` |
| **Compound Agent** | 以上全部 + 失败记忆 + 自动回滚 | `/compound-agent` |
