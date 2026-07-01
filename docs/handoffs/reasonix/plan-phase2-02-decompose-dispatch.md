# Phase 2-02: Task Decomposition + Multi-Agent Dispatch

> 日期: 2026-06-27
> 优先级: P1（Phase 2 核心逻辑）
> 执行端: Reasonix
> 依赖: Plan 01（Async Stitcher + Profile）

---

## 一、背景

Plan 01 提供了异步 Stitcher 和 Agent Profile 数据。现在利用它们做真正的任务编排：

1. **分解**：根据任务和可用 Agent，拆成子任务
2. **分发**：每步子任务 -> 对应的 Python stitch（异步并行）
3. **收集**：所有结果回来后再继续

## 二、核心逻辑

### 2.1 matchAgents() — 匹配 Agent 到路线

```typescript
function matchAgentsForRoute(gewu: string): AgentProfile[] {
  // 按 gewu 权重降序排列
  return AGENT_PROFILES
    .map(p => ({ profile: p, score: p.weights[gewu] || 0 }))
    .filter(x => x.score >= 0.3)       // 只有够格的
    .sort((a, b) => b.score - a.score)
    .map(x => x.profile);
}
```

**降级**：没有匹配的 Agent → 返回 default [coder, researcher, auditor]（Phase1 行为）

### 2.2 decomposeTask() — 分解任务

不写分解算法。让 LLM 来做：

```typescript
async function decomposeTask(task: string, agents: AgentProfile[]): Promise<string[]> {
  // 不调 LLM API，通过 systemPrompt 引导 Pi 本身做分解
  // 在 before_agent_start 注入分解指令
  const agentDescriptions = agents.map(a => `- ${a.name} (${a.label}): ${a.description}`).join("\n");
  return [
    `## ETO 任务分解`,
    `可用 Agent：`,
    agentDescriptions,
    ``,
    `请按以下步骤执行：`,
    `1. 首先，将任务拆解成不超过 ${agents.length} 个子任务`,
    `2. 每个子任务标注由哪个 Agent 执行`,
    `3. 子任务之间如果有依赖关系，标注依赖`,
    `4. 按顺序执行，前一步输出传递给下一步`,
    `5. 全部完成后，输出汇总结果`,
  ].join("\n");
}
```

**关键设计决定**：ETO 不做任务分解算法。分解是 LLM 的能力，ETO 只提供 context（可用 Agent 列表 + 约束条件）。理由：

- LLM 分解比硬编码 DAG 更灵活
- 不引入 DAG 运行时的复杂度
- Agent 列表变化时不需要改代码

### 2.3 dispatchTasks() — 分发执行

```typescript
async function dispatchTasks(subtasks: string[], agents: AgentProfile[]): Promise<any[]> {
  // 并行执行所有子任务
  const results = await Promise.allSettled(
    subtasks.map((step, i) => {
      const agent = agents[i % agents.length];
      return callStitchAsync("comms.a2a", "execute_task", step, agent.name);
    })
  );

  return results.map((r, i) => {
    if (r.status === "fulfilled" && r.value && !("_error" in r.value)) {
      return { step: i, agent: agents[i % agents.length].name, output: r.value };
    }
    return { step: i, agent: agents[i % agents.length].name, _error: true };
  });
}
```

**并行安全**：`Promise.allSettled`——一个失败不影响其他。

**降级**：全部失败 → 回退到单 Agent 执行（调用原来的 `execPlan`）。

### 2.4 集成到 before_agent_start

```
if (route.route === "plan") {
  const matchedAgents = matchAgentsForRoute(route.gewu);
  const decomposePrompt = await decomposeTask(task, matchedAgents);
  // 注入到 systemPrompt，不提前执行 Stitcher
  // 让 Pi 在回复中逐步输出结果
  return { systemPrompt: decomposePrompt + "\n\n" + (event.systemPrompt || "") };
}
```

**关键设计决定**：子任务不在 before_agent_start 中提前执行。Pi 启动后，LLM 在对话中逐步输出 `>> Step N` 结构。ETO 只提供框架，不控制执行流。

### 2.5 结果收集

在回复格式中要求结构化的输出结尾：

```typescript
routeLines.push("回复格式要求：");
routeLines.push("1. 每完成一步，先输出 >> Step N (Agent: xxx)");
routeLines.push("2. 全部完成后，输出：");
routeLines.push("====END====");
routeLines.push("工作总结：");
routeLines.push("- 目标: " + task);
routeLines.push("- 执行者: " + matchedAgents.map(a => a.name).join(", "));
routeLines.push("- 完成步骤: [N步]");
routeLines.push("- 改动文件: [列出改动的文件]");
routeLines.push("- 结果: [总结执行结果]");
```

## 三、测试

```bash
# 1. 匹配测试
pi -p "研究一下Rust的性能特征"     # → matched: [researcher, coder]

# 2. 代码任务
pi -p "写一个flask登录api"         # → matched: [coder, auditor]

# 3. 共识任务（不变）
pi -p "删除这个模块"               # → consensus 路由，不触发 decompose

# 4. 简单任务（direct）
pi -p "什么是ETO"                  # → direct 路由，不触发 decompose

# 5. 降级测试
# 删除 profiles.json 再试
pi -p "写一个flask api"            # → 应正常降级到默认 Agent
```

## 四、不做

- ❌ 复杂 DAG 执行器（交给 LLM 自然语言控制流）
- ❌ 子任务重试逻辑（Phase 3）
- ❌ Agent 间通信（Phase 3 的 ProtoLink）
- ❌ 动态 Agent 注册（Phase 3 的 Registry）

## 五、成功标准

- [ ] `matchAgentsForRoute` 按 gewu 权重返回排序的 Agent 列表
- [ ] 无匹配时降级到默认 3 个 Agent
- [ ] `decomposeTask` 注入合理的分解 prompt（不崩溃）
- [ ] `before_agent_start` 中 plan 分支注入分解 prompt
- [ ] 回复格式被 Pi 正确解析（>> Step N 格式）
- [ ] Stitcher 9/9 继续通过
- [ ] 总新增行数 ≤ 80

## 六、变更文件清单

| 文件 | 变更 |
|:-----|:------|
| `eto/extensions/eto.ts` | 新增 matchAgentsForRoute + decomposeTask + 修改 before_agent_start |
| 无其他文件 | profiles.json 已在 Plan 01 创建 |

## 七、完成回执要求

1. `matchAgentsForRoute` 对每种 gewu 的匹配结果
2. 测试 1-5 每种场景的 `pi -p` 输出
3. 确认 Stitcher 9/9 测试通过
