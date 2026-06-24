---
type: reference-guide
title: ETO 开工前参考清单
description: 制作进化型青色组织（ETO）AI Agent 编排架构项目前需要的技术参考、参考项目与前置知识
tags: [eto, reference, multi-agent, orchestration, planning]
timestamp: 2026-06-19
---

# ETO 开工前参考清单

> **三省六部·礼部调研出品** | 2026-06-19 | MODE=reference-list | TYPE=document

---

## 一、AI Agent 编排框架

| 框架 | 链接 | 一句话说明 | 价值 |
|:-----|:-----|:-----------|:----:|
| **LangGraph** | [GitHub](https://github.com/langchain-ai/langgraph) | 基于图的状态管理构建 Agent 工作流，天然支持分支、循环、审核节点，最契合三省的流转与复核逻辑 | 🔴 |
| **AutoGen** | [GitHub](https://github.com/microsoft/autogen) | 微软多 Agent 对话框架，支持角色分工、对话流程控制，可模拟六部分工协作与消息回传 | 🔴 |
| **CrewAI** | [GitHub](https://github.com/joaomdmoura/crewAI) | 基于角色的多 Agent 编排，支持顺序/层级流程，适合快速搭建三省六部雏形 | 🟡 |
| **Semantic Kernel** | [GitHub](https://github.com/microsoft/semantic-kernel) | 企业级 AI 编排，内置规划器与链式调用，适合将审核链集成到现有业务系统 | 🟡 |
| **Dify** | [GitHub](https://github.com/langgenius/dify) | 可视化工作流编排，支持审批节点与人工介入，可用于门下省复核环节的原型验证 | 🟢 |
| **LangChain** | [GitHub](https://github.com/langchain-ai/langchain) | 基础 Agent 框架，工具调用、记忆、链式组合，可作为单步 Agent 单元底座 | 🟢 |

## 二、多 Agent 协作与路由模式

| 模式/协议 | 链接 | 一句话说明 | 价值 |
|:----------|:-----|:-----------|:----:|
| **集中式路由（中央调度器）** | — | 类似中书省角色，由中心调度器统一分派任务到六部，控制力强，适合审批流 | 🔴 |
| **事件驱动通信** | — | 通过事件总线解耦 Agent 间通信，六部可独立发布/订阅，适合并行执行 | 🔴 |
| **黑板模式** | — | 共享工作区，各 Agent 读写协作，适合多轮复核与迭代修订 | 🟡 |
| **A2A 协议** | [A2A 规范](https://google.github.io/a2a/) | Google 开放的 Agent 间通信协议，标准化消息与能力发现，三省六部通信首选标准 | 🔴 |
| **Oracle ADK** | [GitHub](https://github.com/oracle-samples/agent-development-kit) | 面向企业多 Agent 的协调框架，支持路由与策略注入 | 🟡 |

## 三、审核链与三省三审设计模式

| 模式 | 链接/参考 | 一句话说明 | 价值 |
|:-----|:----------|:-----------|:----:|
| **顺序审批** | — | 按固定顺序经过多级审核，映射门下省逐级复核（每级驳回即回退中书省） | 🔴 |
| **并行会签** | — | 多个审核节点同时审批，全部通过才放行，适合对尚书省执行结果做最终复核 | 🔴 |
| **驳回与修订** | — | 审核不通过时回退指定节点，支持多轮迭代 | 🔴 |
| **LangGraph Supervisor 示例** | [文档](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/) | 主管 Agent 监督子 Agent 输出，直接映射门下省对尚书省的复核模式 | 🔴 |
| **Temporal Workflow** | [GitHub](https://github.com/temporalio/temporal) | 持久化工作流引擎，原生支持状态持久化、超时、重试与人工中断 | 🟡 |
| **Camunda BPMN** | [官网](https://camunda.com/) | 成熟工作流引擎，审核链模式可参考其状态转移设计 | 🟢 |

## 四、现有参考项目（GitHub 开源）

| 项目 | 链接 | 一句话说明 | 价值 |
|:-----|:-----|:-----------|:----:|
| **MetaGPT** | [GitHub](https://github.com/geekan/MetaGPT) | 多角色元编程框架，模拟软件公司全面分工，可类比三省六部的角色与流程设计 | 🔴 |
| **CAMEL** | [GitHub](https://github.com/camel-ai/camel) | 角色扮演多 Agent 协作框架，支持任务协商与分工 | 🔴 |
| **TaskWeaver** | [GitHub](https://github.com/microsoft/TaskWeaver) | 代码优先的 Agent 框架，支持插件化执行单元 | 🟡 |
| **ChatDev** | [GitHub](https://github.com/OpenBMB/ChatDev) | 软件开发多 Agent 协作框架，含需求/编码/审查阶段 | 🟡 |
| **SWE-agent** | [GitHub](https://github.com/princeton-nlp/swe-agent) | 面向软件开发的多 Agent 系统，内建复查流程 | 🟢 |
| **langgraph-approval** | 搜索 `langgraph approval workflow` | LangGraph 审批工作流示例，代码级参考门下省节点实现 | 🔴 |

## 五、相关论文与博客

| 名称 | 链接 | 一句话说明 | 价值 |
|:-----|:-----|:-----------|:----:|
| **Anthropic Agent 模式指南** | [文档](https://docs.anthropic.com/en/docs/building-with-claude/agent-patterns) | Agent 路由、审核、工具调用模式详解，直接指导三省流程拆分 | 🔴 |
| **Practical Guide to Multi-Agent Orchestration** | [Anyscale 博客](https://www.anyscale.com/blog/practical-guide-to-multi-agent-orchestration) | 对比集中式/分布式/分层式编排的优缺点 | 🔴 |
| **Workflow Design Patterns for LLM Agents** | 搜索 `LLM agent workflow patterns` | 顺序、分支、循环、人工介入等模式汇总 | 🟡 |
| **Agent Workflow with Human-in-the-Loop** | 搜索 `LLM human-in-the-loop approval` | 人工审核节点在 Agent 工作流中的最佳实践 | 🟡 |
| **Saga 模式在 AI Agent中的应用** | 搜索 `saga pattern for LLM agents` | 分布式事务 Saga 可用于 Agent 状态回滚与错误恢复 | 🟡 |

## 六、预备知识点

| 知识 | 链接 | 一句话说明 | 价值 |
|:-----|:-----|:-----------|:----:|
| **A2A（Agent-to-Agent）** | [规范](https://github.com/google/A2A) | Google 开放 Agent 通信协议，三省六部通信首选标准 | 🔴 |
| **MCP（Model Context Protocol）** | [官网](https://modelcontextprotocol.io) | Anthropic 主导的模型-上下文协议，尚书省调用外部工具时使用 | 🔴 |
| **状态机设计（XState）** | [文档](https://stately.ai/docs/xstate) | 可视化状态机库，适合构建 Agent 状态转移（起草→审核→执行→复核） | 🔴 |
| **持久化与恢复** | Temporal / PostgreSQL 官方文档 | 工作流引擎持久化 + 数据库保存 Agent 状态，实现故障后精确恢复 | 🔴 |
| **错误恢复策略** | — | Circuit Breaker、指数退避、死信队列、人工介入 | 🟡 |
| **Agent 上下文管理** | — | 向量库/RAG/滑动窗口管理 Agent 记忆，确保多轮审核不丢失信息 | 🔴 |
| **工具调用权限控制** | — | 基于角色的权限模型，门下省可审核但不可执行外部写操作 | 🟡 |

---

**礼部建议：** 优先消化 🔴 高价值条目后快速启动原型验证。
