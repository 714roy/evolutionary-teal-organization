# Phase 2-01: Async Stitcher + Agent Profile

> 日期: 2026-06-27
> 优先级: P1（Phase 2 基础设施）
> 执行端: Reasonix
> 依赖: 无

---

## 一、背景

Phase 1 的 `callStitch()` 用 `execSync`——在单次顺序调用时够用。Phase 2 需要并行调用多个 Stitcher，必须异步。

Agent Profile 是 Phase 2 的新数据层——告诉 ETO 有哪些 Agent 可用、各擅长什么。

## 二、改动

### 2.1 Async Stitcher（`eto/extensions/eto.ts`）

把 `callStitch()` 从 `execSync` 改成 `execFile` + Promise：

```typescript
// Before (sync) — Phase 1
function callStitch(module: string, fn: string, ...args: any[]): Record<string, unknown> | { _error: true; message: string } {
  const script = join(STITCHES_DIR, ...module.split(".")) + ".py";
  const input = JSON.stringify({ fn, args });
  try {
    const out = execSync(`python3 "${script}"`, { input, encoding: "utf-8", timeout: 30000 });
    return JSON.parse(out.trim());
  } catch (e: any) {
    return { _error: true, message: e.message };
  }
}
```

```typescript
// After (async)
import { execFile } from "child_process";
import { promisify } from "util";
const asyncExecFile = promisify(execFile);

async function callStitchAsync(module: string, fn: string, ...args: any[]): Promise<Record<string, unknown> | { _error: true; message: string }> {
  const script = join(STITCHES_DIR, ...module.split(".")) + ".py";
  const input = JSON.stringify({ fn, args });
  try {
    const { stdout } = await asyncExecFile("python3", [script], { input, encoding: "utf-8", timeout: 30000 });
    return JSON.parse(stdout.trim());
  } catch (e: any) {
    return { _error: true, message: e.message };
  }
}
```

**同步调用点：**
- `peerConsensus()` → 改调 `callStitchAsync`
- `electCoordinator()` → 改调 `callStitchAsync`
- `executePlanViaMaestro()` → 改调 `callStitchAsync`

**同样改成 async：**
- `peerConsensus()` → `async`
- `electCoordinator()` → `async`
- `executePlanViaMaestro()` → `async`
- `execPlan()` → `async`（已经是）
- `before_agent_start handler` → 已经在 async 函数里

### 2.2 Agent Profile（`eto/stitches/profiles.json`）

新建 `eto/stitches/profiles.json`，纯数据文件，不引入 JSON 以外的格式：

```json
[
  {
    "name": "researcher",
    "label": "研究员",
    "specialty": "research",
    "description": "信息收集、深度分析、整理报告",
    "weights": { "knowledge": 0.9, "research": 0.95, "code": 0.2, "solution": 0.3 },
    "maxSubtasks": 2
  },
  {
    "name": "coder",
    "label": "编码员",
    "specialty": "code",
    "description": "编写代码、重构、调试",
    "weights": { "knowledge": 0.3, "research": 0.2, "code": 0.95, "solution": 0.5 },
    "maxSubtasks": 3
  },
  {
    "name": "auditor",
    "label": "审计员",
    "specialty": "solution",
    "description": "风险评估、共识审批、质量审查",
    "weights": { "knowledge": 0.5, "research": 0.4, "code": 0.4, "solution": 0.9 },
    "maxSubtasks": 1
  }
]
```

在 `eto.ts` 中添加加载函数：

```typescript
import { readFileSync } from "fs";

// 模块级加载，只执行一次
const AGENT_PROFILES: AgentProfile[] = loadProfiles();

interface AgentProfile {
  name: string;
  label: string;
  specialty: string;
  description: string;
  weights: Record<string, number>;
  maxSubtasks: number;
}

function loadProfiles(): AgentProfile[] {
  const profilePath = join(STITCHES_DIR, "profiles.json");
  try {
    return JSON.parse(readFileSync(profilePath, "utf-8"));
  } catch {
    // 降级：文件不存在时返回默认角色
    return [
      { name: "researcher", label: "研究员", specialty: "research", description: "", weights: {}, maxSubtasks: 2 },
      { name: "coder", label: "编码员", specialty: "code", description: "", weights: {}, maxSubtasks: 3 },
      { name: "auditor", label: "审计员", specialty: "solution", description: "", weights: {}, maxSubtasks: 1 },
    ];
  }
}
```

## 三、测试

```bash
# 1. 同步功能不变
cd eto/stitches && python test.py    # 9/9 必须通过

# 2. 扩展加载无报错
pi -p "hello" --print                # 不应有 stitcher 错误

# 3. Profile 加载
grep "profiles.json" eto/extensions/eto.ts  # 确认引用
```

## 四、不做

- ❌ 热加载 Profile（模块级一次加载够了）
- ❌ YAML/TOML（纯 JSON，ETO 不需要配置文件格式）
- ❌ Profile 编辑工具（文本编辑器直接改 JSON）
- ❌ Profile 验证（JSON parse 失败即降级）

## 五、成功标准

- [ ] `callStitchAsync` 是 async 函数，正常返回
- [ ] `peerConsensus()` / `electCoordinator()` / `executePlanViaMaestro()` 改为 async
- [ ] 所有已有调用点改为 await
- [ ] `profiles.json` 存在且可读
- [ ] `loadProfiles()` 文件不存在时降级不崩溃
- [ ] Stitcher 9/9 测试通过
- [ ] Sync→Async 改动后 `pi -p "hello" --print` 正常输出

## 六、变更文件清单

| 文件 | 变更 |
|:-----|:------|
| `eto/extensions/eto.ts` | callStitch→callStitchAsync + 3 调用方 async + loadProfiles |
| `eto/stitches/profiles.json` | **新建** — Agent Profile 数据 |

## 七、完成回执要求

1. 列出改动的所有 async 函数签名
2. 确认是否引入新依赖（期望：无）
3. Stitcher 测试输出 + pi print 输出
4. 如果遇到执行错误，说明错误内容和修复方案
