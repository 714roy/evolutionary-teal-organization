# Phase 2 总览 — 真实 Agent 编排

> 日期: 2026-06-27
> 优先级: P1（Phase 1 基础设施已完成）
> 执行端: Reasonix（子计划依次执行）

---

## 一、为什么需要 Phase 2

Phase 1 完成了 ETO 的基础设施——三镜路由、Stitcher 硬化、Pi 集成。但现在路由完就结束了：**告诉用户「你的任务是 code→plan」然后让 Pi 正常执行。**

Phase 2 的目标是让 ETO **真正编排任务**：

```
Phase 1（现状）:
  用户 → 路由 → 通知 → Pi 正常执行

Phase 2（目标）:
  用户 → 路由 → 拆解子任务 → 匹配 Agent → 分发 → 收集 → 合成
```

---

## 二、设计原则（优先级排序）

### 1. 降级优先（Fail Graceful）

每个新功能必须有回退。如果 Agent Profile 不可用，路由照常工作（回退到 Phase 1）。不因新层导致旧功能崩溃。

```
profile 失败 → 用默认角色（coder/researcher/auditor）
decompose 失败 → 把完整任务交给 Pi
dispatch 失败 → 单 Agent 执行
synthesis 失败 → 顺序拼接结果
```

### 2. 数据驱动，不要状态机

Agent Profile 是纯数据（JSON 对象），不是服务。不引入数据库、缓存、持久化。不引入异步状态机。

```typescript
// ✅ 数据
const profiles = [{ name: "coder", specialty: "code", confidence: 0.9 }];

// ❌ 状态
class ProfileManager { async loadProfiles() { ... } register() { ... } }
```

### 3. 每层可独立测试

```
profile 层 → 输入: 路由结果 → 输出: 候选 Agent 列表
decompose 层 → 输入: 候选 Agent + 任务 → 输出: 子任务列表
dispatch 层 → 输入: 子任务 → 输出: 执行结果列表
synthesis 层 → 输入: 结果列表 → 输出: 合成字符串
```

每层一个纯函数，不依赖其他层。

### 4. < 200 行新增

Phase 2 代码增量不超过 200 行（当前 541 行，上限 1000 行）。宁愿少功能不堆代码。

第一性原理：**设计重于实现。** 50 行清晰的设计 > 200 行面面俱到的实现。

### 5. Sync → Async（仅限 Stitcher）

Phase 1 的 `callStitch` 用 `execSync`——在 Phase 1 够用（单次调用，步数少）。Phase 2 需要并行调用，必须异步。

改 `callStitch` 为 async + `execFile`/`spawn`，这是唯一必须动的根基代码。

---

## 三、架构

```
before_agent_start 钩子
│
├── 1. 路由（现有）────── 输出 route
│
├── 2. 匹配 profile（新）── 输出 agent 候选列表
│   └── eto/stiches/profiles.json（纯数据）
│
├── 3. 分解任务（新）──── 输出子任务列表
│   └── LLM prompt: "将任务拆给这些 Agent"
│
├── 4. 分发执行（新）──── 收集结果
│   └── async callStitch → 并行执行
│
├── 5. 合成结果（新）──── → systemPrompt
│   └── 按顺序拼接 + 摘要
│
└── 6. 鲁棒性守卫（新）── 全程
    ├── 超时: 每步 60s
    ├── 炸弹开关: 1 个失败 → 降级到全部由 Pi 执行
    └── 日志: 每步结果记到 system prompt
```

---

## 四、子计划拆分

| # | 计划 | 内容 | 新增代码 | 依赖 |
|:-:|:-----|:------|:--------|:-----|
| 01 | Async Stitcher + Profile | execSync→async + profiles.json | ~60行 | 无 |
| 02 | Decompose + Dispatch | LLM 分解 + 异步分发 | ~80行 | Plan01 |
| 03 | Synthesis + Guards | 结果合成 + 超时/熔断 | ~50行 | Plan02 |

每个计划独立验证，全部完成后再集成测试。

---

## 五、不做（明确不做的）

| 功能 | 理由 |
|:-----|:------|
| Agent 动态发现 | 需要 ProtoLink Registry，Phase 3 做 |
| 持久化 Profile | Pi 的 JSONL 会话树已有，不重复 |
| 分布式执行 | 单机够了，分布式是 Phase 3 |
| 实时心跳 | Pi 已有 session 管理 |
| Profile UI | TUI 是 Pi 的领域 |
| 超过 1000 行 | 硬约束 |

---

## 六、验证标准（通不过就拆）

1. `pi -p "写一个flask api"` (无 -e) → ETO 自动加载，无报错
2. Stitcher 9/9 测试继续通过（不因 Phase 2 导致 Phase 1 失败）
3. 每个新函数有至少 2 个测试用例（正常路径 + 降级路径）
4. 总行数 ≤ 740（当前 541 + 200 增量）
