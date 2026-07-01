# Phase 2-03: Result Synthesis + Robustness Guards

> 日期: 2026-06-27
> 优先级: P1（Phase 2 完整性）
> 执行端: Reasonix
> 依赖: Plan 01 + 02

---

## 一、背景

Plan 01 和 02 做了分解和分发。现在需要：
1. **合成**：多个 Agent 的输出拼接成有结构的回复
2. **守卫**：超时、熔断、日志——防止坏代码导致静默失败

## 二、改动

### 2.1 Result Synthesis（`eto/extensions/eto.ts`）

当前回复格式已有 `>> Step N` 结构和 `====END====` 标记。补充同步摘要：

```typescript
function synthesizeResults(
  task: string,
  route: RouteResult,
  agents: AgentProfile[],
  outputs: string[]
): string {
  const lines = [
    `## ETO 执行总结`,
    ``,
    `目标: ${task}`,
    `路由: ${route.gewu} → ${route.route} (${route.layer} ${(route.confidence * 100).toFixed(0)}%)`,
    `协调员: ${route.coordinator}`,
    `执行 Agent: ${agents.map(a => a.label).join("、")}`,
    ``,
    `### 执行步骤`,
  ];

  outputs.forEach((o, i) => {
    lines.push(`**Step ${i + 1}** (${agents[i % agents.length].label}):`);
    lines.push(`  ${o.slice(0, 500)}`);
    lines.push("");
  });

  if (outputs.length === 0) {
    lines.push("_无执行输出（所有 Agent 失败或降级）_");
  }

  return lines.join("\n");
}
```

**注入方式**：回复格式中追加 `====END====` 标记后的 "工作总结" 段由 LLM 填充。`synthesizeResults` 作为 system prompt 的一部分提供模板。

### 2.2 超时守卫

给 `callStitchAsync` 添加每步骤单独超时：

```typescript
async function callStitchAsyncWithTimeout(
  module: string, fn: string, args: any[],
  timeoutMs: number = 30000
): Promise<Record<string, unknown> | { _error: true; message: string }> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const result = await callStitchAsync(module, fn, args);
    return result;
  } catch (e: any) {
    return { _error: true, message: `Timeout after ${timeoutMs}ms: ${e.message}` };
  } finally {
    clearTimeout(timer);
  }
}
```

### 2.3 熔断守卫（Circuit Breaker）

防止连续失败时无限重试：

```typescript
// 模块级计数器：在同一 before_agent_start 周期内
let stitchFailureCount = 0;
const MAX_STITCH_FAILURES = 3;

function checkCircuitBreaker(): boolean {
  if (stitchFailureCount >= MAX_STITCH_FAILURES) {
    console.warn("[ETO] 熔断触发：Stitcher 连续失败 3 次");
    return false; // 电路断开
  }
  return true; // 电路闭合
}

// 在 callStitchAsync 调用前
if (!checkCircuitBreaker()) {
  return null; // 跳过 Stitcher 调用，后续逻辑自动降级
}
```

每次 before_agent_start 开始时重置计数器：

```typescript
pi.on("before_agent_start", async (event, ctx) => {
  stitchFailureCount = 0; // 重置熔断器
  // ... 原有逻辑
});
```

### 2.4 降级链（完整路径）

```
执行链:
  matchAgents → [A1, A2, A3]
    ↓ 空? → [coder, researcher, auditor] (默认)
  decompose → [subtask1, subtask2]
    ↓ 空? → 整个任务作为唯一子任务
  dispatch → [{step, output}, {step, _error}]
    ↓ 全部 _error? → callStitch("comms.a2a", "execute_plan", task, [])
                        ↓ 也失败? → inject 原始任务到 systemPrompt
  synthesize → 结构化 summary
    ↓ 空? → 纯文本拼接
```

### 2.5 日志增强

每步的结果记录在 system prompt 中，方便审计：

```typescript
function buildAuditLog(results: any[]): string {
  return results.map((r, i) =>
    `[Step ${i + 1}] Agent: ${r.agent || "default"} | Status: ${r._error ? "FAIL" : "OK"} | Output: ${(r.output || "N/A").slice(0, 100)}`
  ).join("\n");
}

// injectAuditLog 追加日志到 systemPrompt
```

### 2.6 Auto Time Injection（顺便做，5 行）

```typescript
// 在 before_agent_start 中注入当前时间
routeLines.push(`当前时间: ${new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" })}`);
```

## 三、测试

```bash
# 1. 正常路径
pi -p "写一个flask登录api"
# 输出应包含: 执行总结、Agent 列表、Step 格式

# 2. 合成降级
# 故意让 profiles.json 解析失败
pi -p "写一个flask api"
# 应降级到默认 Agent

# 3. 熔断测试（手动模拟）
# 改 profiles.json 为无效 JSON → 连续调用应触发 3 次失败后熔断
# 观察日志是否有 "[ETO] 熔断触发"

# 4. 时间注入
# 输出应包含当前时间
```

## 四、不做

- ❌ 持久化熔断状态（每次 before_agent_start 重置）
- ❌ 多级超时（全局 30s 够了）
- ❌ 结果缓存（Phase 3）
- ❌ 失败重试（Phase 3 按需加）

## 五、成功标准

- [ ] `synthesizeResults` 返回结构化字符串
- [ ] 超时守卫正常返回 `{ _error: true, message }` 不崩溃
- [ ] 熔断器 3 次失败后跳过 Stitcher 调用
- [ ] 降级链每级都有回退
- [ ] 时间信息出现在 system prompt 中
- [ ] Stitcher 9/9 继续通过
- [ ] 总新增行数 ≤ 50

## 六、变更文件清单

| 文件 | 变更 |
|:-----|:------|
| `eto/extensions/eto.ts` | synthesizeResults + 超时 + 熔断 + 日志 + 时间注入 |

就这一个文件。不改 Stitcher、不改 profiles.json。

## 七、完成回执要求

1. 合成输出样本（一个完整任务的输出示例）
2. 熔断触发日志
3. 降级路径验证（故意制造故障 → 确认系统不崩溃）
4. Stitcher 9/9 测试输出
