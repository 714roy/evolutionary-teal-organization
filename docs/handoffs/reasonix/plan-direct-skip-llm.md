# Bug Fix: direct 路由避免 Ollama 连接暴露

> 日期: 2026-07-01
> 优先级: P0（用户看到 N× "Connection error"）
> 执行端: Reasonix

---

## 问题

当任务被 keywordRoute 分类为 **direct**（如 "你好"、"what is ETO"），`before_agent_start` 仍然调用 `llmRoute()` → fetch Ollama localhost:11434 → 连不上 → AbortSignal.timeout(2000) 触发 → Pi SDK retry × N → 用户看到 Error。

**根因：** direct 路由本就不需要 LLM（关键词已经足够），但代码对所有 route 都先试 LLM，再 fallback keywordRoute。

---

## 修复方案：direct 任务提前分流

在 `before_agent_start` 中，先用 `keywordRoute()` 判断：如果是 direct 路由，直接走直出流程，不调 Ollama。

```typescript
// eto.ts before_agent_start handler 改动：

pi.on("before_agent_start", async (event, ctx) => {
  const task = event.prompt || "";
  if (!task) return;

  stitchFailureCount = 0;

  // ── 新增：direct 路由直接跳过 LLM ──
  const keywordResult = keywordRoute(task);
  if (keywordResult.route === "direct") {
    // 不需要 Ollama，直接走 direct 流程
    const confidence = (keywordResult.confidence * 100).toFixed(0);
    ctx.ui.setWidget("eto-route", undefined);
    
    const widgetLines = [
      `📋 ETO | ${keywordResult.gewu} → direct | ${keywordResult.coordinator} | keyword ${confidence}%`,
    ];
    
    const routeLines = [
      `## ETO 路由分析`,
      `当前时间: ${new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" })}`,
      `路由: ${keywordResult.gewu} → direct (keyword, ${confidence}%)`,
      `协调员: ${keywordResult.coordinator}`,
      "",
      "回复格式：",
      "【路由】一句话说明任务归类",
      "【回答】你的回答",
      "====END====",
    ];

    ctx.ui.setWidget("eto-route", widgetLines);
    return { systemPrompt: routeLines.join("\n") + "\n\n" + (event.systemPrompt || "") };
  }

  // ── plan/consensus 路由：继续走 LLM → keyword fallback 流程 ──
  // ... 原有逻辑不变（llmRoute + AbortSignal.timeout(2000)）
});
```

---

## 验证

1. `pi -e eto.ts "你好"` → **无** Error/Connection error 暴露
2. Widget 正常显示 "📋 ETO | knowledge → direct | researcher | keyword 70%"
3. 回复格式正确（有「路由」「回答」两行 + ====END====）

---

## 文件清单

| 文件 | 变更 |
|:-----|:------|
| `eto/extensions/eto.ts` | before_agent_start 中 direct 提前分流 |

就改一个文件、一个 handler。

## 完成回执要求

1. 输入 "你好" 后确认无 Connection error 暴露
2. Widget 内容正确（knowledge → direct）
3. LLM retry 错误数从 ~4→0
