# Phase 2 Bug Fix — Unicode乱码 + LLM retry 暴露

> 日期: 2026-07-01
> 优先级: P0（两 bug 都影响用户体验）
> 执行端: Reasonix

---

## Bug 1: Unicode 乱码

**症状：** `共识: �����`

**根因：** Windows CLI pipe UTF-8 → GBK 编码转换失败。Stitcher 返回的中文 JSON 被截断/乱码。

**修复方案：** 在所有 stitcher Python 文件中强制 stdout 为 UTF-8：

```python
# 在每个文件的 import 后加一行
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
```

**影响文件：**
- `eto/stitches/comms/a2a.py`
- `eto/stitches/consensus/vote.py`
- （如果 elect.py 有中文输出也加）

---

## Bug 2: LLM retry 暴露给 UI

**症状：** "Error: Connection error." × 3 + "⠦ Retrying (3/3)"

**根因：** `llmRoute()` fetch Ollama localhost:11434，连不上时由 Pi SDK 自动 retry（默认 3 次），重试过程暴露给用户。

**修复方案：**

### 方案 A：加 timeout（推荐）

在 `eto.ts` 的 `llmRoute` 中给 fetch 加超时——Ollama 连不上时快速失败而不是被 Pi SDK retry 拖住：

```typescript
// eto.ts llmRoute() 中的 fetch 调用，加一个短 timeout
signal: AbortSignal.timeout(2000),  // 2秒无响应直接超时
```

同时修改 `routeTask()` 的 fallback 策略：

```typescript
async function routeTask(task: string): Promise<RouteResult> {
  const llm = await llmRoute(task);
  if (llm && llm.confidence >= 0.3) return llm;
  
  // LLM 路由失败时，立即 fallback 到 keywordRoute
  // 不要等到 retry 全部完成才 fallback
  return keywordRoute(task);
}
```

关键：`routeTask()` 的 fallback 是**立即执行**而非**等待重试完成后执行**。如果 Pi SDK 强制 retry（不可配置），则需要加 AbortSignal.timeout(1000) 强制快速退出。

### 方案 B：静默降级（兜底）

如果 LLM 路由失败（超时/连接错误），不要向用户展示任何中间状态，只显示最终结果：

```typescript
// before_agent_start handler 中：
const route = await routeTask(task);
if (!route || !route.layer) {
  // 静默降级到 keywordRoute
  route = keywordRoute(task);
}
// ... 后续正常显示路由结果（不显示 LLM 失败过程）
```

---

## 文件清单

| 文件 | 变更 |
|:-----|:------|
| `eto/stitches/comms/a2a.py` | 加 `sys.stdout.reconfigure(encoding="utf-8")` |
| `eto/stitches/consensus/vote.py` | 同上 |
| `eto/stitches/election/elect.py` | 同上（如有中文输出） |
| `eto/extensions/eto.ts` | llmRoute 加 timeout + routeTask 静默降级 |

## 验证

1. `pi -p "写一个flask api"` — widget 中"共识: XX"显示正确无乱码
2. Ollama 关闭时，无 retry 暴露（只有最终路由结果）
3. Stitcher 9/9 测试通过

## 完成回执要求

1. Unicode 修复后的 stitcher stdout 输出样本
2. Bug 2 的 UI 显示效果确认
