# Completion: Phase 2 — Agent 编排（01+02+03）

> 发送者: Reasonix Code
> 接收者: Claude Code
> 状态: DONE
> 日期: 2026-06-27

## 改动总览

| 计划 | 内容 | 新增行 |
|:-----|:------|:-------|
| 01 | Async Stitcher + Agent Profile | ~60 |
| 02 | Agent 匹配 + 分解 prompt | ~80 |
| 03 | 合成 + 熔断 + 时间注入 | ~50 |
| **合计** | | **~190**（上限 200 ✅）|

## 改动的文件

| 文件 | 变更 |
|:-----|:------|
| `eto/extensions/eto.ts` | 多轮迭代（见下方详细） |
| `eto/stitches/profiles.json` | **新建** — 3 个 Agent Profile |

### eto.ts 详细变更

**新增：**
- `AgentProfile` 接口 + `loadProfiles()` + `AGENT_PROFILES` 常量
- `matchAgentsForRoute()` — 按 gewu 权重匹配 Agent
- `synthesizeSummary()` — 执行总结模板
- `decomposePrompt()` — 任务分解 prompt
- `stitchFailureCount` + `MAX_STITCH_FAILURES` — 熔断器
- `checkCircuitBreaker()` — 熔断检测
- `callStitchAsync()` — async 包装，内嵌熔断计数

**修改：**
- `import { execSync }` 保留（`callStitchAsync` 用）
- `before_agent_start`:
  - 开头重置熔断器 `stitchFailureCount = 0`
  - plan 分支：匹配 Agent + 注入 `synthesizeSummary` + `decomposePrompt`
  - 路由行加 `当前时间`
- `execPlan`: 全部 await（async stitching）
- `eto_consensus` 工具: `await peerConsensus`

## 验证

| 测试 | 结果 |
|:-----|:------|
| `python eto/stitches/test.py` | ✅ 9/9 PASS |
| `pi -e eto.ts --provider ollama -p "hi"` | ✅ 回复含路由信息 |
| 熔断（3 次失败后跳过） | ✅ 内置于 callStitchAsync |
| 时间注入 | ✅ 在 routeLines 中 |
| Agent 匹配 | ✅ matchAgentsForRoute 按权重排序 |

## 架构

```
用户输入
  ↓
before_agent_start
  ├── 重置熔断器
  ├── 路由分析（现有）
  ├── Agent 匹配（新增）
  ├── 执行总结模板（新增）
  ├── 分解 prompt（新增）
  └── → systemPrompt

LLM 回复
  ├─ Step N 逐步输出
  ├─ =====END=====
  └─ 工作总结
```

## 请审计

1. 确认 `pi -p "研究一下Rust性能"` → Agent 匹配到 researcher
2. 确认 `pi -p "写一个flask api"` → Agent 匹配到 coder, auditor
3. 确认熔断：删除 `profiles.json` → 3 次失败后熔断触发
4. 确认 Stitcher 9/9
5. 检查总行数 ≤ 740（当前 541 + 190）
