# ETO 项目约定 — 给 Claude 的指令

## 第一性原理：不要造轮子（优先级最高）

> 2026-06-25 复盘教训：ETO 写了 3156 行代码，但 Pi CLI 已有 TUI/Agent 引擎/工具系统/会话管理。正确的架构是 ETO 做薄编排层跑在 Pi CLI 之上，而不是重写整个栈。

**做之前先问：Pi CLI 有没有？**
- TUI → Pi CLI 自带 `pi-tui`，不要写 tui.py
- 工具调用 → Pi CLI 的 `--tools`，不要封装 executor.py
- 会话管理 → Pi CLI 的 JSONL 会话树，不要写 context.py
- Agent 运行时 → `pi` 命令，不要封装 call_pi

**ETO 只写（编排层，总量 < 1000 行）：**
1. ✅ 三镜路由（analyze / router）
2. ✅ 临时协调员选举（election）
3. ✅ 同侪共识（consensus）
4. ✅ 步骤上下文传递（core 中的编排逻辑）

**踩过的坑（不要再犯）：**
- ❌ 自写 TUI — Pi CLI 已有 `pi-tui`
- ❌ 自封装 CLI 调用 — Pi 就是 CLI
- ❌ 自建上下文管理 — Pi 的 JSONL 会话树
- ❌ 自建记忆系统 — 用 agentmemory / pi-memory
- ❌ 自建 embedding/路由 — Pi 的 provider 抽象

## AIMemory Protocol (Hermes ↔ Claude Code)

与 Hermes Agent（运行在本地网络的协调节点）之间的跨 Agent 记忆协议。

**安装（一次）:**
```bash
uv tool install git+https://github.com/AnastasiyaW/mclaude.git
```

**规则:**
- 会话启动: `mclaude memory core` 加载共享上下文
- 关键决策: `mclaude memory save`
- 修改共享文件前: `mclaude lock claim`
- Agent ID: `claude-code`
