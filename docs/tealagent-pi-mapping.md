---
type: design-mapping
title: TealAgent ↔ Pi 映射设计
description: 将 design-spec 中抽象的青色 Agent 概念映射到 Pi (pi-mono) 的真实 API 和扩展机制
tags: [teal-agent, pi, mapping, implementation, architecture]
timestamp: 2026-06-21
---

# TealAgent ↔ Pi 映射设计

> 目标：消除架构层最大的不确定性——让抽象的 TealAgent（perceive/evaluate/reflect）在 Pi 上可落地。

---

## 一、核心映射

### TealAgent → Pi CLI

| TealAgent 概念 | Pi 映射 | 实现方式 |
|:---------------|:--------|:---------|
| `agent_id` | 进程标识 | Pi 进程的 PID + 任务 ID（编排层分配） |
| `specialty` | `--system-prompt` | 每个角色有独立的 system prompt 文件 |
| `tools` | `--tools`（allowlist） | 指定 Agent 可用的工具白名单 |
| `local_knowledge` | `--append-system-prompt` + 会话历史 | 每次执行时追加历史上下文 |
| `busy_ratio` | 编排层追踪 | 由编排脚本维护并发计数 |
| `perceive(ctx)` | tool 调用 | Pi 通过自定义 tool 读取 TealContext |
| `evaluate(proposal)` | 单独 Pi 调用 | 一个 Pi 实例专门做评估 |
| `reflect(feedbacks, plan)` | 单独 Pi 调用 | 一个 Pi 实例做调整 |

### 角色 ↔ System Prompt 文件

```
~/.eto/agents/
├── tongzhengsi.md       # 通政司：三镜分析
├── libu.md              # 礼部：调研
├── gongbu.md            # 工部：设计
├── xingbu.md            # 刑部：审计
└── zhizi.md             # 智子：规则审查
```

**调用方式：**

```bash
# 通政司 = Pi + 通政司 prompt
pi --print --provider ollama --model "qwen2.5-coder:7b" \
  --system-prompt "$(cat ~/.eto/agents/tongzhengsi.md)" \
  --tools "read,write" \
  "帮我分析AI行业竞争格局"

# 智子（审计模式）= Pi + 智子 prompt + 只读工具
pi --print --provider ollama --model "qwen2.5-coder:7b" \
  --system-prompt "$(cat ~/.eto/agents/zhizi.md)" \
  --exclude-tools "bash,write" \
  "审查这份产出"
```

---

## 二、TealContext 实现方案

### 架构

```
┌──────────────────────────────────────────┐
│  TealContext (JS/TS 模块, 独立进程)       │
│  ┌────────────────────────────────────┐  │
│  │  global_memory: Memento[]          │  │
│  │  active_proposals: Proposal[]      │  │
│  │  consensus_log: LogEntry[]         │  │
│  └────────────────────────────────────┘  │
│  API: perceive() / record() / query()    │
└──────────────────────────────────────────┘
         │                    ↑
         │ JSON-RPC / 文件     │ 自定义 tool
         ▼                    │
   Pi Agent ──────────────────┘
   (通过 tool 调用 TealContext API)
```

### 方案选择

| 方案 | 复杂度 | 优点 | 缺点 |
|:-----|:-------|:------|:------|
| **A. 文件传递** | 低 | 零依赖，立即可用 | 并发写入冲突 |
| **B. JSON-RPC 服务** | 中 | 支持并发，可跨进程 | 需要启动一个服务进程 |
| **C. Pi Extension** | 高 | 集成最紧密 | 需要开发 Pi 扩展插件 |

**推荐路线：** S1-S2 用方案 A（文件传递），S3 后升级为方案 B（JSON-RPC）。

### 文件传递方案（A）

```typescript
// teal-context/store.ts
// 以 JSON 文件存储，每个操作加文件锁

const STORE_PATH = '~/.eto/teal-context.json';

interface TealContext {
  global_memory: Memento[];
  active_proposals: Proposal[];
  consensus_log: LogEntry[];
}

function perceive(agentId: string): ContextSnapshot {
  const ctx = readWithLock(STORE_PATH);
  return {
    recent: ctx.global_memory.slice(-10),
    active: ctx.active_proposals.filter(p => p.status === 'pending')
  };
}

function record(entry: Memento): void {
  const ctx = readWithLock(STORE_PATH);
  ctx.global_memory.push({ ...entry, timestamp: Date.now() });
  if (ctx.global_memory.length > 1000) ctx.global_memory.shift(); // LRU
  writeWithLock(STORE_PATH, ctx);
}
```

### Pi 集成方式

TealContext 对外暴露为 CLI 工具，Pi Agent 通过 `bash` tool 调用：

```bash
# Agent 感知上下文
tc perceive --agent-id=libu-001

# Agent 记录执行结果  
tc record --type=execution --agent=libu-001 --result=success

# 智子查询审计
tc query --type=veto --since=1h
```

---

## 三、Fable-5 行为注入方案

### 核心机制

```
通政司输出 → 选择行为模板 → 组装 system prompt → 启动 Pi Agent
```

```
Fable-5 routing logic（编排层实现）:

                 ┌─────────────────┐
                 │ 通政司输出        │
                 │ taskType + 权重   │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ 选择基础模板      │
                 │ 工程师/创作/研究  │
                 │ 审计/自动        │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ 按三体权重微调    │
                 │ 实体高→加工具    │
                 │ 理体高→加技能    │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ 组装 prompt      │
                 │ = 身份 + 框架    │
                 │ + 工具 + 技能    │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ pi --system-prompt│
                 │ "$prompt" ...    │
                 └─────────────────┘
```

### 模板文件结构

```
~/.eto/fable5/
├── identity/
│   └── fable5.txt              # Fable-5 身份声明
├── harness/
│   ├── core.txt                # 核心行为框架
│   ├── autonomy-high.txt       # 高自主性
│   ├── autonomy-low.txt        # 低自主性
│   └── communicating.txt       # 用户沟通指令
├── tools/
│   ├── bash.txt                # Shell 工具描述
│   ├── write.txt               # 写入工具描述
│   ├── read.txt                # 读取工具描述
│   └── search.txt              # 搜索工具描述
├── skills/
│   ├── debugging.txt           # 调试技能
│   └── code-review.txt         # 审查技能
└── reminders/
    ├── startup.txt             # 会话启动提醒
    ├── tool-choice.txt         # 工具选择提醒
    └── error-recovery.txt      # 错误恢复提醒
```

### 模板 → `--append-system-prompt`

```bash
# 工程师模式：高自主性 + 调试技能
PROMPT="$(cat identity/fable5.txt)
$(cat harness/core.txt)
$(cat harness/autonomy-high.txt)
$(cat tools/bash.txt)
$(cat tools/write.txt)
$(cat skills/debugging.txt)"

pi --print --provider ollama --model "..." \
  --system-prompt "$PROMPT" \
  --tools "bash,write,read,search" \
  "实现这个函数"
```

---

## 四、智子（规则引擎）实现方案

### 架构

```
┌─────────────────────────────────────────────┐
│  智子 (Pi Agent + 规则引擎)                  │
│                                             │
│  输入钩子: Agent 执行前                       │
│    ┌─ 规则匹配 → 放行 / 拦截 / 警告           │
│    └─ 预算检查 → 未超 / 超预算                │
│                                             │
│  输出钩子: Agent 执行后                       │
│    ┌─ 审计日志写入 TealContext                │
│    └─ 格式校验                                │
│                                             │
│  共识钩子: 决策时                            │
│    └─ CRITICAL 否决检查                      │
└─────────────────────────────────────────────┘
```

### 作为 Pi Agent 实现

```bash
# 智子审计模式
pi --print --provider ollama --model "qwen2.5-coder:7b" \
  --system-prompt "$(cat ~/.eto/agents/zhizi.md)" \
  --exclude-tools "bash,write" \
  --append-system-prompt "检查以下输出是否有越界行为: $(cat $output_file)"
```

### 规则引擎（独立 CLI）

```bash
# qsh — 智子规则管理 CLI
qsh rule list              # 列出规则
qsh rule add rule.yaml     # 添加规则
qsh rule test rule.yaml input.json  # 测试规则
qsh audit --since=1h       # 审计查询
qsh stop <pipeline-id>     # 强制停止
```

规则文件格式：

```yaml
# ~/.eto/rules/no_destructive_ops.yaml
name: no_destructive_ops
priority: 10
type: pre_execution
description: 禁止破坏性操作
match:
  tool: [bash, write_file]
  pattern: "rm -rf|dd if=|format|mkfs"
action: veto
message: "⛔ 禁止破坏性操作"
```

---

## 五、编排层实现

### 完整调用链

```
# 1. 通政司分析任务
TASK="帮我分析AI行业竞争格局"
ANALYSIS=$(pi --print --provider ollama --model "qwen2.5-coder:7b" \
  --system-prompt "$(cat agents/tongzhengsi.md)" \
  --tools "read,write" \
  "$TASK")

# 2. 解析通政司输出（提取 ROUTE、三体权重）
ROUTE=$(echo "$ANALYSIS" | jq -r '.ROUTE')
MODE=$(echo "$ANALYSIS" | jq -r '.MODE')

# 3. direct 或 pipeline
if [ "$ROUTE" = "direct" ]; then
  # 快速通道：一次 Pi 调用
  pi --print --provider ollama --model "qwen2.5-coder:7b" "$TASK"
else
  # pipeline：按 MODE 编排
  case "$MODE" in
    research)
      pi --print ... --system-prompt "$(cat agents/libu.md)" "$TASK"
      pi --print ... --system-prompt "$(cat agents/gongbu.md)" "..."
      pi --print ... --system-prompt "$(cat agents/zhizi.md)" "..."
      ;;
    build)
      pi --print ... --system-prompt "$(cat agents/gongbu.md)" "$TASK"
      pi --print ... --system-prompt "$(cat agents/xingbu.md)" "..."
      ;;
  esac
fi

# 4. 写入 TealContext
tc record --type=execution --result=success
```

---

## 六、与 Dynamic Workflows 的对接

当环境中安装了 Claude Code（DW 宿主）时：

```
DW JS 编排脚本（等价的 ETO pipeline）:

async function etoPipeline(task) {
  // 1. 通政司
  const analysis = await runPiAgent('tongzhengsi', task);
  const { route, mode, weights } = parseAnalysis(analysis);
  
  if (route === 'direct') {
    return await runPiAgent('assistant', task);
  }
  
  // 2. Fable-5 行为路由
  const behaviorPattern = fable5Route(mode, weights);
  
  // 3. 多 Agent pipeline (DW subagent)
  const result = await dw.pipeline(
    { agent: 'libu', prompt: task, ...behaviorPattern },
    { agent: 'gongbu', prompt: '基于调研产出设计方案' },
    { agent: 'xingbu', prompt: '审查以上产出' }
  );
  
  // 4. 智子审计
  await zhiziAudit(result);
  
  // 5. 记录 TealContext
  await tealContext.record(result);
  
  return result;
}
```

**关键点：** Pi 始终是 Agent 运行时，DW 只做编排——不改变 Agent 的行为逻辑。

---

## 七、验证 Checklist

在开始 S1 实现前逐项确认：

| # | 检查项 | 验证方式 | 状态 |
|:-|:-------|:---------|:-----|
| 1 | Pi 支持 `--system-prompt` | `pi --print --system-prompt "角色" "任务"` | ✅ 已验证 |
| 2 | Pi 支持 `--exclude-tools` | `pi --exclude-tools "bash,write"` | ✅ 已验证 |
| 3 | Pi 支持 `--append-system-prompt` | 追加行为指令 | ✅ 已验证 |
| 4 | Pi 支持 `--print` 非交互模式 | `pi --print "prompt"` | ✅ 已验证 |
| 5 | Pi 扩展安装机制 | `pi install git:...` | ✅ 可用 |
| 6 | 通政司 prompt 可用本地模型驱动 | — | ⚠️ 需实测效果 |
| 7 | TealContext 文件方案可读写 | — | ⏳ S2 验证 |
| 8 | 智子规则 YAML 解析 | — | ⏳ S3 验证 |
| 9 | Fable-5 模板拼接性能 | — | ⏳ S4 验证 |
| 10 | 多 Pi 进程并发编排 | Shell 并行调用 | ⏳ S1 验证 |
