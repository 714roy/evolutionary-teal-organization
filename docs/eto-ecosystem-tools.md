---
title: ETO 生态工具与前沿技术映射
description: 编程工具 + 前沿 AI 开源项目，按 ETO 特性分类
---

# 🛠️ ETO 生态工具与前沿技术

---

## 一、可直接安装的编程工具（Developer Tools）

### 已安装（可直接用）

| 工具 | 用途 | 工具数 | 安装方式 |
|:-----|:------|:-------|:---------|
| **server-filesystem** | 文件系统读写 | 14 | `npx @modelcontextprotocol/server-filesystem` ✅ |
| **server-github** | GitHub API | 26 | `npx @modelcontextprotocol/server-github` ✅ |
| **chrome-devtools-mcp** | Chrome 调试 | 29 | `npx chrome-devtools-mcp` ✅ |
| **playwright-mcp** | 浏览器自动化 | 23 | `npx @playwright/mcp` ✅ |
| **superpower-mcp** | 多开发技能网关 | — | Reasonix skill `/superpower-mcp` ✅ |

### 多 Agent 编排

| 工具 | ⭐ | 说明 | 对应 ETO 特性 | 安装 |
|:-----|:---|:------|:-------------|:------|
| **OpenAI Swarm** | 21.6k | 轻量多 Agent 编排，handoff 模式匹配 ETO 的 peer 模型 | ETO-004/005 路由, ETO-009 peer自治 | `pip install openai-swarm` |
| **microsoft/agent-framework** | 11.5k | 生产级 Agent 编排 SDK，Python+.NET | ETO-010 Agent池, ETO-045 并行 | `pip install microsoft-agent-framework` |
| **kyegomez/swarms** | 6.9k | 企业级多 Agent 协作文档，内置共识模式 | ETO-016 共识协议, ETO-011 选举 | `pip install swarms` |
| **CrewAI** | 30k | 角色化 Agent 团队框架（注意：角色固定，适合 Phase 1 快速原型） | ETO-015 Plan起草, ETO-010 Agent池 | `pip install crewai` |

### 🏆 本地参考：Hermes Agent 团队模式

你每天在用的 Hermes 本身就是多智能体架构的最佳参考。它把任务处理分为五大层级：

| 层级 | 核心命令 | 特点 |
|:----|:---------|:------|
| 1️⃣ 任务排队 | `/q` | 当前线程串行，零开销处理后续任务 |
| 2️⃣ 后台任务 | `/background` | 独立线程跑耗时任务，不阻塞前台 |
| 3️⃣ 批量子代理 | `delegate_task` | 最多 5 个并发子代理，父代理同步等结果 |
| 4️⃣ 系统级并行 | `hermes sw` | Tmux + Git Worktree 实现 OS 级隔离 |
| 5️⃣ 监控管理 | `agents` / `tasks` | 实时树状图、成本追踪、一键暂停/强杀 |

**核心设计：上下文防火墙**

每个子代理在独立"隔音室"中启动，**完全空白的状态，不带历史包袱**。好处：
- 防止记忆污染和任务蔓延
- 消除 Token 冗余浪费
- 降低 AI 幻觉概率

**子代理只能返回结构化报告，不能修改全局状态**——确保安全。

**与 ETO 的对应关系：**

| Hermes | ETO |
|:-------|:----|
| 上下文防火墙 | ETO-043 Peer注册发现 + 隔离执行 |
| delegate_task 并行 | ETO-045 多 Agent 并行 |
| 子代理只返回报告 | 智子规则：不越界（ETO-035） |
| agents 监控面板 | ETO-037 智子审计日志 |
| `/q` 排队 | 通政司路由（ETO-004/005） |
| `/background` | Cron Loop / Watch Loop（ETO-062/063） |

**ETO 的 Phase 1 可以先把 Hermes 的五层级对齐到自己身上——不是重新造轮子，是先搞清楚自己现在能做什么、还缺什么。**

### 记忆与知识

| 工具 | ⭐ | 说明 | 对应 ETO 特性 | 安装 |
|:-----|:---|:------|:-------------|:------|
| **Mem0** | 25k | 自改进 Agent 记忆层，自动存/取偏好和事实 | ETO-022~028 TealContext 系列 | `pip install mem0ai` |
| **Letta** (MemGPT) | 13k | 虚拟上下文管理，层级记忆+持久化 | ETO-024 三层记忆, ETO-027 会话延续 | `pip install letta` |
| **Zep** | 3k | 长期记忆服务，图结构实体提取 | ETO-032 知识图谱, ETO-031 记忆修剪 | `pip install zep-python` |
| **simple-memory-mcp** | 1 | 极简 MCP 记忆服务器，JSON文件持久化 | ETO-032 轻量级知识图谱替代 | `npx @anthropic/create-mcp-server` |

### MCP 服务器（ETO-050 MCP 兼容层）

| 工具 | ⭐ | 说明 | 安装 |
|:-----|:---|:------|:------|
| **modelcontextprotocol/servers** | 25k | 官方 MCP 服务器合集（文件系统/GitHub/Git/PostgreSQL等） | `npx @modelcontextprotocol/server-*` |
| **ollama-mcp-bridge** | 975 | 本地 Ollama 模型 ↔ MCP 工具桥接 | `npm install -g ollama-mcp-bridge` |
| **playwright-mcp** | 5.6k | 浏览器自动化 MCP → ETO 的 TDD 测试能力 | `npx @executeautomation/mcp-playwright` |
| **5ire** | 5.2k | 跨平台 MCP 客户端桌面应用，含本地知识库 | `brew install --cask 5ire` |

### 开发纪律配套

| 工具 | 说明 | 对应 Skill | 安装 |
|:-----|:------|:-----------|:------|
| **metaswarm** (dsifry) | 18个Agent+13个Skill，内置TDD+质量门禁 | ETO-D01~D05 全栈 | `git clone https://github.com/dsifry/metaswarm` |
| **tree-sitter** | 代码结构解析为 AST → Agent 可分析 | ETO-D04 Trammel 结构意识 | `pip install tree-sitter` |
| **pydeps** | Python 依赖关系可视化 | ETO-D04 影响范围分析 | `pip install pydeps` |

---

## 二、前沿 AI 开源项目（Research Projects）

### Active Inference（ETO-065）

| 项目 | ⭐ | 说明 | 落地方式 |
|:-----|:---|:------|:---------|
| **pymdp** (infer-actively) | 707 | **最成熟的 Active Inference Python 库**——MDP 上的变分自由能最小化 | ETO 的集体回顾循环可以直接调用 pymdp 做预测误差分析和策略更新 |
| **contrastive-aif** | 15 | NeurIPS'21 — World Model + Active Inference 结合 | Phase 5 做 ETO-065+ETO-066 联调时参考 |
| **DesignAInf/DAU** | 2 | 多 Agent Active Inference 原型 | ETO-011+016 多 Agent 共识的实验参考 |

**推荐路径：** Phase 4 先给 TealContext 加 prediction_error 字段插桩 → Phase 5 引入 pymdp 做真正的自由能计算。

### World Model / JEPA（ETO-066）

| 项目 | ⭐ | 说明 | 落地方式 |
|:-----|:---|:------|:---------|
| **Sub-JEPA** (intcomp) | 49 | **最新 JEPA 变种** ——子空间高斯正则化世界模型 | ETO-066 潜空间 rollout 的参考实现 |
| **JEPA-Image-World-Model** | 12 | JEPA 在 Minecraft 上的世界模型 | 演示 JEPA 如何不通过重建损失做潜空间预测 |
| **jepas** (yunusskeete) | 10 | 多 JEPA 变种的教学实现（I-JEPA/V-JEPA 等） | 理解 JEPA 家族差异的代码库 |

**推荐路径：** ETO-066 先不做完整 JEPA，先做轻量版——用 embedding + 线性回归取代 128 维潜空间 rollout，验证概念后再引入 Sub-JEPA。

### 记忆系统对比（ETO-022~028 技术选型）

```
                    Mem0 (25k★)          Letta (13k★)         Zep (3k★)
持久化               ✅                    ✅                    ✅
知识图谱             entity extraction      ❌                    ✅ 实体图
离线可用             库模式✅               ✅                    ❌ 需服务
API 复杂度           中                     高                    中
推荐阶段             Phase 2 替代 JSON      Phase 3 试点           Phase 3 备选
```

### Agent 通信协议

| 协议 | 发起方 | 说明 | ETO 对应 |
|:-----|:-------|:------|:---------|
| **A2A** (Agent-to-Agent) | Google | Agent 间发现+通信的开放协议 | ETO-043 Peer注册发现 |
| **MCP** (Model Context Protocol) | Anthropic | Agent ↔ 工具的标准化接口 | ETO-050 MCP 兼容层 |
| **FIPA-ACL** (via SPADE) | IEEE 标准 | 成熟的 Agent 通信语言标准 | ETO-016 共识协议的语义基础 |

**结论：** MCP 已装（Reasonix 原生支持），A2A 关注（等更成熟），FIPA-ACL 作为理论参考。

---

## 三、推荐安装清单

### 立即装（帮助 Phase 1 开发）

```bash
# Agent 编排
pip install openai-swarm        # 轻量编排，匹配 ETO peer 模型

# MCP 工具
npx @modelcontextprotocol/server-filesystem    # 文件系统 MCP
npm install -g ollama-mcp-bridge                # 本地模型 MCP 桥

# 开发纪律配套
pip install pydeps tree-sitter    # 代码分析
```

### Phase 2 装（记忆系统）

```bash
pip install mem0ai               # 替代 JSON 文件做 TealContext 持久化
pip install zep-python           # 知识图谱备选
```

### Phase 5 装（理论引擎）

```bash
pip install pymdp                # Active Inference
git clone https://github.com/intcomp/Sub-JEPA   # World Model 参考
```

---

## 📦 四、编程 MCP Server 全集（按用途分类）

这些是 ETO 开发中可直接对接的 MCP 工具，覆盖编码全流程。

### 代码与版本控制

| 工具 | 说明 | 安装 |
|:-----|:------|:------|
| **@modelcontextprotocol/server-github** | GitHub API — PR/Issue/Repo 管理 | `npx @modelcontextprotocol/server-github` |
| **@modelcontextprotocol/server-git** | Git 操作 — commit/log/diff/branch | `npx @modelcontextprotocol/server-git` |
| **@modelcontextprotocol/server-filesystem** | 文件系统读写访问 | `npx @modelcontextprotocol/server-filesystem` |

### 编程辅助

| 工具 | 说明 | 安装 |
|:-----|:------|:------|
| **@firmancli/mcp (Superpower)** | 多开发技能合一：Figma/Elementor/Framer + 编码 | `npm install -g @firmancli/mcp` |
| **chrome-devtools-mcp** | Chrome DevTools 调试 — 控制台/元素/网络 | `npx chrome-devtools-mcp` |
| **@playwright/mcp** | 浏览器自动化 — 测试/E2E/截图 | `npx @playwright/mcp` |
| **@storybook/mcp** | 组件文档 + 测试生成 | `npx @storybook/mcp` |
| **@orval/mcp** | API 客户端代码生成 (OpenAPI→TypeScript) | `npx @orval/mcp` |

### 测试与质量

| 工具 | 说明 | 安装 |
|:-----|:------|:------|
| **executeautomation/mcp-playwright** | 浏览器测试自动化 | `npx @executeautomation/mcp-playwright` |
| **getsentry/XcodeBuildMCP** | iOS/macOS 构建与测试 | `brew install xcodebuild-mcp` |
| **puppeteer-mcp** | Headless Chrome 控制 | `npx puppeteer-mcp` |

### 调试与监控

| 工具 | 说明 | 安装 |
|:-----|:------|:------|
| **mcp-inspector** | MCP 服务器调试工具 | `npx @modelcontextprotocol/inspector` |
| **@sentry/mcp-server** | 错误监控与性能追踪 | `npx @sentry/mcp-server` |
| **chrome-devtools-mcp** | Chrome 开发者工具调试 | `npx chrome-devtools-mcp` |

### 文档与知识

| 工具 | 说明 | 安装 |
|:-----|:------|:------|
| **@upstash/context7-mcp** | 上下文感知的开发者文档查询 | `npx @upstash/context7-mcp` |
| **@notionhq/notion-mcp-server** | Notion API — 文档管理 | `npx @notionhq/notion-mcp-server` |
| **simple-memory-mcp** | 轻量持久记忆+知识图谱 | `npx simple-memory-mcp` |

### 实用工具

| 工具 | 说明 | 安装 |
|:-----|:------|:------|
| **mcp-proxy** | MCP SSE↔Stdio 代理 | `npm install -g mcp-proxy` |
| **ollama-mcp-bridge** | 本地 Ollama ↔ MCP 桥接 | `npm install -g ollama-mcp-bridge` |
| **5ire** | 跨平台 MCP 桌面客户端 | `brew install --cask 5ire` |
| **@mastra/mcp** | MCP 服务器框架 | `npx @mastra/mcp` |

---

## 五、不推荐的项目及理由

| 项目 | 不推荐理由 |
|:-----|:-----------|
| **CrewAI** 做长期编排 | 角色固定，跟青色动态组织哲学冲突（适合原型，不适合生产） |
| **AutoGen** (pyautogen) | 微软已弃坑进入维护模式，社区 fork 不稳定 |
| **MetaGPT** | 面向软件公司的角色模拟，跟 ETO 的通用 Agent 协作不是一回事 |
| **LangGraph** | 图固定，不够动态；ETO 需要的是运行时画图不是预定义图 |
