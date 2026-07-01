# Bug Fix: Ollama 不可达时避免 retry 暴露

> 日期: 2026-07-01
> 优先级: P0（"你好"这类任务不该报 Connection error）
> 执行端: Reasonix

---

## 问题

直出路由（如 "你好"）→ `llmRoute()` → fetch Ollama localhost:11434 → 连不上 → Pi SDK retry × N → Error。

**根因：** Ollama 没开时，fetch 超时 → Pi SDK 自动重试 → 用户看到报错。**不应该这样。**

---

## 修复方案：`routeTask()` 先检查 Ollama 连通性

```typescript
// eto.ts 修改 routeTask() — 只改这一个函数

async function checkOllamaReachable(): Promise<boolean> {
  try {
    await fetch("http://localhost:11434/api/tags", { 
      signal: AbortSignal.timeout(500) 
    });
    return true;
  } catch { 
    return false; 
  }
}

async function routeTask(task: string): Promise<RouteResult> {
  // Ollama 活着才尝试 LLM
  const ollamaAvailable = await checkOllamaReachable();
  
  let llm: RouteResult | null = null;
  if (ollamaAvailable) {
    llm = await llmRoute(task);
  }
  
  // 有 LLM 结果且置信度够 → 用 LLM
  if (llm && llm.confidence >= 0.3) return llm;
  // 不管 Ollama 状态都 fallback keywordRoute（静默）
  return keywordRoute(task);
}
```

**行为变化：**
| Ollama | 之前 | 之后 |
|:-------|:-----|:------|
| 开着 | LLM → keywordFallback | LLM → keywordFallback（不变） |
| 关着 | Error × N + keywordFallback | keywordFallback（无报错） |

---

## 文件清单

| 文件 | 变更 |
|:-----|:------|
| `eto/extensions/eto.ts` | routeTask() + checkOllamaReachable() |

就改一个函数。

## 验证

1. Ollama 开：`pi -e eto.ts "研究一下Rust"` → LLM 正常分类
2. Ollama 关：`pi -e eto.ts "你好"` → 无报错，widget 显示 direct
3. `checkOllamaReachable()` 单独测试：`await fetch('http://localhost:11434/api/tags', {signal: AbortSignal.timeout(500)})`

## 完成回执要求

1. Ollama 关时 "你好" 无 Connection error
2. Ollama 开时正常走 LLM 路由
3. 总新增行数 ≤ 15
