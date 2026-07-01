# Plan: 交互式 Onboarding Flow

> 创建日期: 2026-07-02 | 来源: Roy (Claude Code)
> **核心原则**: 引导用户创建第一条真实数据，不塞假种子。

---

## 设计决策

Bootstrap Bundle（静态基础设施）保留原样：profiles/skills/config 种子文件，用于 pip install/GitHub push。

但 **session_start 的引导 UI** 需要完全替换为交互式流程：

```
用户视角: T0 → T1 → T2 → T3 → T4
─────────────────────────────────────
T0: 首次启动检测 → "🦋 ETO 你好！多 Agent 编排系统。来配置一下？"
T1: 用户确认 [是/跳过]
T2: 选 provider (deepseek / ollama / skip) → 保存 to eto-config.json
T3: 引导创建第一条真实任务："试试说——帮我写个 Python hello world"
T4: 用户描述任务 → ETO plan 路由 → coder + auditor → 展示结果
     "首次配置完成！之后直接说话就行。"
```

---

## 改动清单

### D1: Onboarding State 文件

**新建**: `~/.eto/memory/onboarding.json`

```json
{
  "version": 1,
  "first_session_at": null,      // ISO timestamp
  "seen_welcome": false,         // 是否见过欢迎消息
  "provider_set": false,         // 是否已选 provider
  "first_task_done": false,      // 是否已完成第一条真实任务
  "current_step": 0,             // 当前引导步骤 (0=未开始, 1=welcome确认, 2=provider选择, 3=引导任务, 4=完成)
  "skipped": false               // 用户跳过过（不回溯）
}
```

**读取逻辑**: `~/.eto/memory/onboarding.json` 存在 → 非首次；不存在 → T0 检测为首次。

---

### D2: Onboarding Flow 实现（TS 侧，eto/extensions/eto.ts）

#### 2a. onboarding helpers（新模块，在 session_start handler 之前）

```typescript
interface OnboardingState {
  version: number;
  first_session_at?: string;
  seen_welcome: boolean;
  provider_set: boolean;
  first_task_done: boolean;
  current_step: number; // 0..4
  skipped: boolean;
}

const ONBOARDING_PATH = join(require("os").homedir(), ".eto", "memory", "onboarding.json");

function loadOnboardingState(): OnboardingState {
  try {
    if (existsSync(ONBOARDING_PATH)) return JSON.parse(readFileSync(ONBOARDING_PATH, "utf-8"));
  } catch {}
  return { version: 1, seen_welcome: false, provider_set: false, first_task_done: false, current_step: 0, skipped: false };
}

function saveOnboardingState(state: OnboardingState): void {
  const dir = join(require("os").homedir(), ".eto", "memory");
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  writeFileSync(ONBOARDING_PATH, JSON.stringify(state, null, 2), "utf-8");
}

/** T0: 检测是否首次 + 是否需要引导 */
function needOnboarding(state: OnboardingState): boolean {
  return !state.skipped && !state.first_task_done;
}
```

#### 2b. session_start handler 重写

**当前**（eto.ts ~line 364）：简单显示品牌标语。

**改为**：T0 检测 → T1-T4 逐步引导。

```typescript
pi.on("session_start", async (_event, ctx) => {
  const bsState = loadBootstrapState();
  const onbState = loadOnboardingState();

  // ── Bootstrap check ──
  if (!bsState.profiles) {
    // profiles.json 不存在 → Bootstrap Bundle 未运行
    ctx.ui.setWidget("eto-route", [
      "╭── ETO 初始化提示 ─────────────╮",
      "│                                │",
      "│  请先运行 Bootstrap Bundle：    │",
      "│    python3 -m bootstrap        │",
      "│  这只需 10 秒。                │",
      "╰──────────────────────────────────╯",
    ]);
    return;
  }

  // ── Onboarding flow (T0) ──
  if (needOnboarding(onbState)) {
    switch (onbState.current_step) {
      case 0:
        // T0 → T1: welcome + 确认
        onbState.first_session_at = new Date().toISOString();
        saveOnboardingState(onbState);
        showWelcomeStep(ctx);
        break;

      case 1:
        // T1 → T2: provider selection (if user confirmed)
        if (onbState.provider_set) {
          onbState.current_step = 3; // skip to step 3 (task guide)
          saveOnboardingState(onbState);
          showTaskGuideStep(ctx);
        } else {
          ctx.ui.setWidget("eto-route", ["⏳ 请选择 provider..."]);
        }
        break;

      case 2:
        // T2 → T3: provider selected, save and proceed
        onbState.provider_set = true;
        onbState.current_step = 1; // go back to confirm
        saveOnboardingState(onbState);
        showTaskGuideStep(ctx);
        break;

      case 3:
        // T3 → T4: first task done
        onbState.first_task_done = true;
        onbState.current_step = 4;
        saveOnboardingState(onbState);
        ctx.ui.notify("🎉 首次配置完成！之后直接说话就行。", "info");
        ctx.ui.setWidget("eto-route", ["📋 ETO 等待中...", "输入任务开始"]);
        break;

      case 4:
        // Already done — no special UI needed (normal flow handles)
        ctx.ui.setWidget("eto-route", ["📋 ETO 等待中...", "输入任务开始"]);
        break;
    }
    return; // onboarding takes control, don't do normal routeTask yet
  }

  // ── Normal flow (bootstrap complete + onboarding done) ──
  ctx.ui.setWidget("eto-route", ["📋 ETO 等待中...", "输入任务开始"]);
});
```

#### 2c. step handlers（session_start 辅助函数）

**T1 — welcome step**:
```typescript
function showWelcomeStep(ctx: ...) {
  ctx.ui.notify("╭── 🦋 ETO 你好 ─────────────────╮", "info");
  ctx.ui.notify("│                                │", "info");
  ctx.ui.notify("│  我是你的多 Agent 编排系统。    │", "info");
  ctx.ui.notify("│  你只需要描述任务，我会自动      │", "info");
  ctx.ui.notify("│  路由给合适的 Agent 执行。       │", "info");
  ctx.ui.notify("│                                │", "info");
  ctx.ui.notify("│  来配置一下？（约 30 秒）        │", "info");
  ctx.ui.notify("╰──────────────────────────────────╯", "info");
  // Wait for user response (via prompt/confirmation)
}
```

**T2 — provider selection**:
用户确认「是」后，问用哪个 LLM provider：
```
请选择 LLM Provider（影响路由）：

1) DeepSeek API（推荐，速度快，需 API key）
   export DEEPSEEK_API_KEY=sk-xxx

2) Ollama 本地模型（免费，无需联网）
   ollama pull qwen2.5-coder:7b

3) 跳过（纯关键词路由，无 LLM 语义分类）

直接回复数字即可。
```

**T3 — task guide**:
```
┌── 配置完成！来试第一条任务吧 ──────┐
│                                    │
│  ETO 已经就绪：                    │
│  • 3 Agent Profiles               │
│  • Skill Memory 已加载            │
│  • Router 已配置                  │
│                                    │
│  试试说：                          │
│  "帮我写个 Python hello world"     │
│                                    │
└────────────────────────────────────┘
```

**T4 — first task completed**:
当用户完成了第一次真实交互后（通过 session_start → before_agent_start 的流程检测），通知完成。

---

### D3: T1 confirmation（Pi CLI prompt/按钮集成）

问题：Pi CLI 的 `ctx.ui` 没有确认按钮。需要一种方式让用户回复「是」来继续。

**方案**: 用 widget + notify 提示用户，下次 user message 到达时检查 onboarding step。

```typescript
// T1: show welcome, wait for user reply
pi.on("message_received", async (event, ctx) => {
  const state = loadOnboardingState();
  if (!needOnboarding(state)) return; // normal flow
  
  if (state.current_step === 0) {
    // Check if user said something affirmative
    const msg = event.message || "";
    if (/是|好|行|可以|确认/.test(msg)) {
      state.seen_welcome = true;
      state.current_step = 1;
      
      // T2: prompt for provider selection
      ctx.ui.setWidget("eto-route", ["请选择数字 (1/2/3)"]);
      saveOnboardingState(state);
    } else if (/否|不|跳过|算了/.test(msg)) {
      state.skipped = true;
      saveOnboardingState(state);
      ctx.ui.notify("好的，之后随时输入 /eto-setup 重新开始引导。", "info");
    }
  }
  
  if (state.current_step === 1) {
    // T2: parse provider choice
    const num = parseInt(msg);
    if (num === 1 || num === 2 || num === 3) {
      await setProvider(ctx, num); // writes to eto-config.json
      state.current_step = 3;
      ctx.ui.setWidget("eto-route", ["配置完成！试试第一条任务"]);
      saveOnboardingState(state);
    }
  }
  
  if (state.current_step === 3) {
    // T3: user described a real task — this is the first task!
    // After before_agent_start completes successfully:
    state.current_step = 4;
    state.first_task_done = true;
    saveOnboardingState(state);
    ctx.ui.notify("🎉 首次配置完成！以后直接说话就行。", "info");
  }
});
```

**注意**: `message_received` 是 Pi CLI 的 hook，需要确认 API 是否支持。如果不支持，改为在 `before_agent_start` 里检测 onboarding step。

---

### D4: Bootstrap Bundle + seed_sample_tasks 清理

Bootstrap Bundle **保留** profiles/skills/config 的种子注入（这些是基础设施种子，不是假用户数据）。

**但删除** `seed_sample_tasks.py` — 不再需要示例任务数据，Onboarding Flow 引导用户自己写真实任务。

---

## 验收标准

| # | 检查项 | 验证方式 |
|---|--------|----------|
| O1 | 首次启动显示 welcome（有欢迎框） | session_start widget 包含 "你好" |
| O2 | 用户回复「是」→ 进入 provider 选择 | onboarding.json current_step → 1/2 |
| O3 | 选择 provider 后 eto-config.json 更新 | cat 文件确认 |
| O4 | T3 显示任务引导框 | widget 包含 "试试" |
| O5 | 用户完成第一条真实任务 → 通知完成 | onboarding.json first_task_done=true |
| O6 | 二次启动不再重复引导（current_step=4） | session_start widget = normal |
| O7 | 用户说「跳过」→ no more onboarding | skipped=true, 正常流程 |

## 实施顺序

```
Step 1 → 删除 seed_sample_tasks.py + 从 bootstrap/__init__.py 移除调用    — 2 min
Step 2 → 新增 onboarding helpers (D1+D2前半)                             — 8 min
Step 3 → session_start handler 重写为状态机 (D2后半)                     — 10 min
Step 4 → T1-T4 step handlers (welcome/provider/task_guide/complete)      — 10 min
Step 5 → before_agent_start 集成 onboarding completion 检测               — 5 min
```

总计约 35 分钟。

## 与 Bootstrap Bundle 的关系

```
Bootstrap Bundle (静态基础设施):
  ├── seed_profiles.json  → profiles.json ✅
  ├── seed_skills         → skills.jsonl   ✅  
  └── config_template     → eto-config.json ✅

Onboarding Flow (动态交互流程):
  ├── T0: 首次检测 (bootstrap_state + onboarding_state)
  ├── T1: welcome prompt
  ├── T2: provider selection → updates eto-config.json
  ├── T3: first task guide
  └── T4: completion notification

关系: bootstrap 必须先完成（基础设施就绪）→ onboarding 才能开始（用户引导）
```
