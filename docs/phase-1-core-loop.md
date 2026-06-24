---
phase: 1
title: A2A 通信层奠基
codename: "第一次握手"
status: done
---

# Phase 1：A2A 通信层奠基

> 实现最小可行 A2A 通信拓扑——不写通信协议，只缝 ProtoLink。

---

## 一、范围

### 做的

| # | 事项 | 说明 | 状态 |
|:-|:-----|:------|:-----|
| 1 | **ProtoLink 安装验证** | `pip install protolink`，确认 Agent/AgentCard 可用 | ✅ 完成 |
| 2 | **Agent 基础功能** | Agent 启动 + invoke() LLM 处理消息 | ✅ 完成 |
| 3 | **HTTP Transport** | Registry/Uvicorn 通过 HTTP 注册、发现、A2A 通信 | ✅ 完成 |
| 4 | **文件夹结构** | `~/.eto/a2a/` 按职责分目录 | ✅ 完成 |
| 5 | **跨 Agent 通信** | Agent A → Agent B 通过 A2A 标准协议 POST /tasks/ | ✅ 完成 |

### 不做的

| 事项 | 理由 |
|:-----|:------|
| ❌ 自写通信协议 | ProtoLink 已经实现了 A2A 标准 |
| ❌ 自写注册发现 | ProtoLink Registry 已经实现 |
| ❌ 任何"框架"代码 | Phase 1 的目标是证明通信能通，不是写框架 |
| ❌ 三镜/路由/共识 | 这些是 Phase 2 的范畴 |

---

## 二、技术栈

| 组件 | 选型 | 理由 |
|:-----|:------|:------|
| 通信协议 | **A2A Protocol** (Google 标准) | 24K⭐，Linux 基金会，Google+微软+AWS+SAP 联合维护 |
| Python 实现 | **ProtoLink v0.6.1** | `pip install protolink`，原生 A2A 实现 |
| Transport | **HTTP (Starlette/Uvicorn)** | Runtime transport v0.6.1 有序列化 bug，HTTP 更稳定 |
| 注册发现 | **ProtoLink Registry** | 内建 Agent 注册与发现，支持标签/角色过滤 |
| Agent Card | **A2A Agent Card 标准** | 每个 Agent 声明 skills/tags/role，通过 Registry 互相发现 |
| LLM | **Mock（测试）→ Ollama** | 通信层验证用 Mock，真实对话用本地模型 |
| 工作目录 | **`~/.eto/a2a/`** | 新架构独立目录，旧 pipelines/ 保留不动 |

---

## 三、架构

```
┌───────────── ProtoLink A2A 通信层 ─────────────┐
│                                                  │
│  Registry (HTTP :5550)                           │
│    ├── POST /agents/          ← Agent 注册       │
│    ├── GET  /agents/          ← Agent 发现       │
│    └── GET  /status           ← 健康检查         │
│                                                  │
│  Agent A (HTTP :A-port)       Agent B (HTTP :B-port)
│    ├── AgentCard                 ├── AgentCard    │
│    │   name: researcher          │   name: coder  │
│    │   skills: [search, analyze] │   skills: [code, review]
│    │   role: worker              │   role: worker │
│    ├── POST /tasks/   ←── A2A ──┤                │
│    └── POST /tasks/   ── A2A ──→┘                │
└──────────────────────────────────────────────────┘
        │
Pi CLI（作为"最后一步的执行器"，不是编排器）
```

### 数据流

```
Agent A 发现 Agent B:
  A → Registry: GET /agents/?tags=coding
  Registry → A: [AgentCard(coder)]

Agent A 发任务给 Agent B:
  A → B: POST /tasks/ {parts: [{type: "text", content: "..."}]}
  B → A: {parts: [{type: "text", content: "回复"}]}
```

### Agent Card 规范

```python
AgentCard(
    name="researcher",                  # 唯一标识
    description="调研分析 Agent",         # 可读描述
    url="http://127.0.0.1:PORT",        # HTTP 地址
    transport="http",
    skills=[
        AgentSkill(id="search", tags=["search", "research"]),
    ],
    role="worker",                       # gateway/interface/observer/orchestrator/worker
    tags=["research", "analysis"],       # 索引标签
)
```

---

## 四、验收结果

| # | 测试 | 结果 |
|:-|:-----|:-----|
| T1 | Agent 启动 + invoke() | ✅ Mock + Ollama 均通过 |
| T2 | Registry HTTP 启动 | ✅ Uvicorn 正常监听 |
| T3 | Agent HTTP 注册 | ✅ POST /agents/ 200 OK |
| T4 | Agent 互相发现 | ✅ GET /agents/ 返回两个 Agent |
| T5 | A2A 消息通信 | ✅ Agent A → B 发送任务，B 回复 |
| T6 | Mock → Ollama 切换 | ✅ --ollama 参数可用 |

---

## 五、搭建记录对照

| 缝合方案步骤 | 实现方式 | 状态 |
|:------------|:---------|:-----|
| 装 ProtoLink | `pip install protolink` | ✅ |
| 两个 Agent 通信 | HTTP transport + Registry | ✅ |
| A2A 发现 | discover_agents(filter_by) | ✅ |
| **验收：通信能通** | 三个 HTTP 服务器互调 POST | ✅ 确认 |

---

## 六、技术债务

| # | 事项 | 说明 | 优先级 |
|:-|:-----|:------|:-------|
| D1 | ProtoLink v0.6.1 runtime transport 序列化 bug | Agent.start() 不传递 register 参数到 _serve，handle_register 不反序列化 dict→AgentCard。已绕过（用 HTTP transport） | 🟡 观察 |
| D2 | 编码问题 | Windows GBK vs UTF-8，已设 PYTHONIOENCODING=utf-8 | ✅ 已修 |
