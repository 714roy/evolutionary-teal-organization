# ETO 执行计划

> 基于 framework.md，按优先级焊代码

---

## Phase 1：打通完整流程（现在）

**目标：** `eto.ts` 能跑通 plan 路由的完整生命周期

### Step 1 — 重构 eto.ts 结构
把 eto.ts 拆成清晰的模块分区，为后续扩展做准备。

| 模块 | 行数 | 说明 |
|:-----|:-----|:------|
| routeTask | ~40 | 三镜路由（LLM + 关键词） |
| registerTools | ~40 | 注册 eto_route / eto_consensus 工具 |
| hooks | ~50 | before_agent_start / tool_call 钩子 |
| stitcher | ~40 | 调 Python 缝合层的桥接代码 |

### Step 2 — 写 stitcher 桥接
TypeScript 扩展调 Python 缝合层。

```typescript
// eto.ts → stitcher
async function callStitch(module: string, fn: string, args: any[]) {
  const result = await exec(`python3 eto/stitches/${module} --fn ${fn} ${JSON.stringify(args)}`);
  return JSON.parse(result);
}
```

### Step 3 — 实现 Plan 多步执行
路由=plan 时，不丢给 Pi 直接回答，而是：

```
plan → 
  ① eto.ts 检测到 plan 路由
  ② 调用 Maestro 生成 DAG
  ③ 通过 stitcher 调 Python 执行各步骤
  ④ 每步可选调 VotingAI 评分
  ⑤ 汇总结果返回用户
```

### Step 4 — 替换共识为真实 peer 评分
现在 `eto_consensus` 工具用随机数，改为调 VotingAI。

---

## Phase 2：Agent Profile 注册表（接下来）

**目标：** 路由不只按关键词，还按 Agent 的能力画像

```yaml
# profiles.yaml（示例）
agents:
  researcher:
    specialty: "信息调研、分析、报告"
    style: "严谨、学术、详细"
    tools: ["read", "bash", "web_search"]
    mcp: ["web-search", "arxiv"]
  coder:
    specialty: "编码、重构、调试"
    style: "实用、清晰、可维护"
    tools: ["read", "write", "bash", "edit"]
    mcp: ["github"]
```

---

## Phase 3：动态任务分解（长期）

**目标：** 不硬编码 3 步模板，而是每次由 LLM 生成 DAG

```
plan → LLM 分析任务 → 输出 Maestro YAML DAG → maestro submit 执行
```

---

## 当前开工：Phase 1 Step 1

重构 eto.ts，把代码分成清晰的模块，然后接 Step 2 的 stitcher 桥接。
