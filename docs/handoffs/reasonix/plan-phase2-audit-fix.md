# Phase 2 Audit Fix — 注释 + 死代码清理

> 日期: 2026-06-27
> 优先级: P2（非功能影响，纯清洁）
> 执行端: Reasonix
> 来源: Claude Code 审计 completion-phase2.md

---

## 一、问题清单

### Issue 1: `callStitchAsync` 注释与实际实现不符

**文件:** `eto/extensions/eto.ts` 第 168 行

```typescript
// Line 168: 当前注释（错误）
//  二、Stitcher — 调 Python 缝合层（async via spawn）

// Line 195: 实际代码
const out = execSync(...);  // ← 不是 spawn
```

**修复:** 改注释为 "外部调用用 await" 或类似描述，不要误导。

### Issue 2: `circuitBreakerWrap` 是死代码

**文件:** `eto/extensions/eto.ts` 第 233-237 行

```typescript
// Line 233-237: 定义但未在任何地方调用
function circuitBreakerWrap<T>(fn: () => T): T | null {
  if (!checkCircuitBreaker()) return null;
  try { const r = fn(); stitchFailureCount = 0; return r; }
  catch (e) { stitchFailureCount++; throw e; }
}
```

**修复:** 删除整个 `circuitBreakerWrap` 函数。熔断逻辑已在 `callStitchAsync` 中正确实现（第 188-190 行）。`checkCircuitBreaker()` 和 `stitchFailureCount` / `MAX_STITCH_FAILURES` 保持不变。

## 二、验证

```bash
# 1. Stitcher 测试不变
cd eto/stitches && python test.py    # 9/9

# 2. ETO 扩展加载无报错
pi -e eto.ts --provider anthropic -p "hello" --print | head -5
```

## 三、变更文件清单

| 文件 | 变更 |
|:-----|:------|
| `eto/extensions/eto.ts` | 改注释 + 删 `circuitBreakerWrap`（+1/-4） |
| 无其他文件 | 不影响任何功能层 |

## 四、完成回执要求

1. `callStitchAsync` 的新注释内容
2. `circuitBreakerWrap` 已确认不存在于 diff
3. Stitcher 测试输出
