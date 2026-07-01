# Plan: Bootstrap Bundle + Profile 修复 + 本地模型

> 创建日期: 2026-07-02 | 来源: Roy (Claude Code)
> 审计: 给 Reasonix 编码前由 Roy 确认

---

## 目标

新手首次使用 ETO 时从"白板"到"能用"的一键初始化，同时修掉路由的已知缺陷：

1. **Agent Profile weights 永远为空** -> plan 路由的 agent 匹配失效
2. **没有本地模型 provider 选项** -> 必须有 `ollama` / `deepseek` / `skip` 切换
3. **缺少 Bootstrap Bundle（新手引导包）** -> profiles/skills/tasks 全白屏

---

## Bootstrap Bundle — 统一新手包设计

> Seed Data + Onboarding Flow + Init Script 三块合为一个 artifact。

### Bundle 目录结构

```
eto/bootstrap/                  ← 新增核心模块
├── __init__.py                 # bootstrap() 总入口，编排全步骤
├── seed_profiles.py            # 种子 Agent Profile → ~/.pi/etoprofiles/profiles.json
├── seed_sample_skills.py       # 种子经验数据 → ~/.eto/memory/skills.jsonl
├── seed_sample_tasks.py        # 种子示例任务 → pi history
└── config_template.py          # eto-config.json 模板

pi-bootstrap.cmd                ← Windows 入口（一行）
pi-bootstrap.sh                 ← bash 入口
```

### Bundle 编排流程

```
python3 -m eto.bootstrap
  │
  ├─ Step 1: mkdir ~/.eto/memory/
  ├─ Step 2: seed_profiles.py (→ profiles.json)
  ├─ Step 3: seed_sample_skills.py (→ skills.jsonl)
  ├─ Step 4: seed_sample_tasks.py (→ history)
  └─ Step 5: 生成 eto-config.json（如不存在）
```

### `eto/bootstrap/__init__.py` — 总入口

```python
"""ETO Bootstrap Bundle — 新手一键初始化"""
import json, os, sys
from pathlib import Path

HOME = Path.home()
ETO_DIR = HOME / ".eto"
ETO_MEM_DIR = ETO_DIR / "memory"
PI_DIR = HOME / ".pi"

def run(force=False) -> dict:
    """运行 Bootstrap Bundle，已存在的跳过。返回每一步状态。"""
    steps = []
    ETO_MEM_DIR.mkdir(parents=True, exist_ok=True)
    steps.append({"step": "prepare_dir", "status": "ok"})

    from eto.bootstrap import seed_profiles
    r = seed_profiles.init(str(PI_DIR / "etoprofiles" / "profiles.json"))
    steps.append(r)

    from eto.bootstrap import seed_sample_skills
    r = seed_sample_skills.init()
    steps.append(r)

    from eto.bootstrap import seed_sample_tasks
    r = seed_sample_tasks.init()
    steps.append(r)

    config_path = PI_DIR / "eto-config.json"
    if not config_path.exists() or force:
        provider = "deepseek" if os.environ.get("DEEPSEEK_API_KEY") else "ollama"
        from eto.bootstrap.config_template import make_config
        config_path.write_text(make_config(provider), "utf-8")
        steps.append({"step": "config", "status": "created"})

    return {"status": "bootstrap_complete", "steps": steps}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    result = run(force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

### `eto/bootstrap/seed_profiles.py` — 种子 Agent Profile

**文件**: `eto/bootstrap/seed_profiles.py`

```python
"""种子 Agent Profile，首次安装时写入 profiles.json"""
import json
from pathlib import Path

SEED_PROFILES = [
    {
        "name": "researcher", "label": "研究员", "specialty": "research",
        "description": "信息收集、深度分析、整理报告",
        "weights": {"knowledge": 0.9, "research": 0.95, "code": 0.2, "solution": 0.3},
        "maxSubtasks": 2
    },
    {
        "name": "coder", "label": "编码员", "specialty": "code",
        "description": "编写代码、重构、调试",
        "weights": {"knowledge": 0.3, "research": 0.2, "code": 0.95, "solution": 0.5},
        "maxSubtasks": 3
    },
    {
        "name": "auditor", "label": "审计员", "specialty": "solution",
        "description": "风险评估、共识审批、质量审查",
        "weights": {"knowledge": 0.5, "research": 0.4, "code": 0.4, "solution": 0.9},
        "maxSubtasks": 1
    }
]

def init(profiles_path: str = None) -> dict:
    if profiles_path is None:
        from eto.bootstrap import PI_DIR
        profiles_path = str(PI_DIR / "etoprofiles" / "profiles.json")
    p = Path(profiles_path)
    if p.exists():
        return {"status": "skipped", "reason": "profiles.json already exists"}
    p.write_text(json.dumps(SEED_PROFILES, ensure_ascii=False, indent=2), "utf-8")
    return {"status": "initialized", "count": len(SEED_PROFILES)}
```

### `eto/bootstrap/seed_sample_skills.py` — 种子经验数据

**文件**: `eto/bootstrap/seed_sample_skills.py`

写入 5 条典型 Skill Entry 到 `~/.eto/memory/skills.jsonl`：

```python
SEED_SKILLS = [
    {"skill_name": "dependency-circuit-breaker", "context": "外部调用必须加熔断，避免级联失败", "reward": 0.95, "source": "bootstrap"},
    {"skill_name": "empty-state-handling", "context": "空列表状态需有友好提示，不直接渲染空白", "reward": 0.85, "source": "bootstrap"},
    {"skill_name": "config-first-pattern", "context": "配置项必须从文件读取而非硬编码", "reward": 0.80, "source": "bootstrap"},
    {"skill_name": "keyword-fallback-safe", "context": "LLM 路由不可用时，关键词匹配必须有兜底默认值", "reward": 0.75, "source": "bootstrap"},
    {"skill_name": "graceful-degradation", "context": "任何外部依赖失败都应回退到安全模式，不能 crash", "reward": 0.90, "source": "bootstrap"},
]

def init() -> dict:
    from eto.bootstrap import ETO_MEM_DIR
    p = ETO_MEM_DIR / "skills.jsonl"
    if p.exists():
        return {"status": "skipped"}
    p.write_text("\n".join(json.dumps(s) for s in SEED_SKILLS) + "\n", "utf-8")
    return {"status": "initialized", "count": len(SEED_SKILLS)}
```

### `eto/bootstrap/seed_sample_tasks.py` — 种子示例任务

**文件**: `eto/bootstrap/seed_sample_tasks.py`

写入 2 条示例任务用于展示 widget + 路由效果（**注意：这是演示数据，不影响真实 history，标记 is_seed=True**）：

```python
SEED_TASKS = [
    {
        "task": "写一个 Flask REST API",
        "result": "已创建 app.py, routes/users.py",
        "route": "plan",
        "agent": "coder",
        "is_seed": True  # 标记为种子数据，bootstrap 时可清理
    },
    {
        "task": "调研 Rust vs Go 在微服务中的性能表现",
        "result": "已完成调研报告",
        "route": "consensus",
        "agent": "researcher",
        "is_seed": True
    }
]
```

> **注意**: seed_sample_tasks 不直接写 pi history（那是只读 API）。改为：写入 `~/.eto/memory/sample_tasks.json`，扩展的 `session_start` handler 读取后注入 widget 显示为示例。

### `eto/bootstrap/config_template.py` — 配置模板

```python
def make_config(default_provider: str) -> str:
    return json.dumps({
        "router": {
            "provider": default_provider,
            "models": {
                "deepseek": {"url": "https://api.deepseek.com/v1/chat/completions", "model": "deepseek-chat"},
                "ollama":   {"url": "http://localhost:11434/api/chat", "model": "qwen2.5-coder:7b"}
            },
            "fallback": "keyword"
        }
    }, indent=2)
```

### Bootstrap Bundle + session_start 引导 UI

在 `eto/extensions/eto.ts` 的 `session_start` handler 里检测 bootstrap 完成状态：

- 检测到未 bootstrap（无 profiles.json）→ 自动调用 Python bootstrap → 显示引导 UI
- 检测到已 bootstrap → 显示正常 widget

```
╭── ETO 青色组织模式 ─────────────╮
│                                  │
│  🎉 Bootstrap Bundle 已完成       │
│                                  │
│  ✅ 3 Agent Profiles             │
│  ✅ 5 条种子经验                 │
│                                  │
│  📋 支持的类型：                  │
│    • 写代码 → 编码员 + 审查       │
│    • 调研分析 → 研究员            │
│    • 危险操作 → 审计审批           │
│                                  │
│  试试说一句话：                   │
│  "帮我写个 HTTP server"           │
╰──────────────────────────────────╯
```

引导完成后注入 Quick Start（仅第一次会话）：

```
[ETO Quick Start]
- 直接说话即可，无需 /eto 命令
- ETO 会自动判断你该用什么 Agent
- 看到 widget 里的路由结果 = ETO 在工作
- 输入 /metrics 查看运行统计
```

---

## 改动清单

### 1. 修复 Agent Profile weights（eto/extensions/eto.ts）

**问题**: `loadProfiles()` fallback 返回的 weights 全是 `{}`，导致 `matchAgentsForRoute` 永远筛掉所有人。

**文件**: `eto/extensions/eto.ts:26-35`

**改动**:
```typescript
// loadProfiles() fallback 改为硬编码默认权重
return [
  { name: "researcher", label: "研究员", specialty: "research", description: "", weights: { research: 0.9, knowledge: 0.7, code: 0.2, solution: 0.3 }, maxSubtasks: 2 },
  { name: "coder", label: "编码员", specialty: "code", description: "", weights: { knowledge: 0.3, research: 0.2, code: 0.95, solution: 0.5 }, maxSubtasks: 3 },
  { name: "auditor", label: "审计员", specialty: "solution", description: "", weights: { knowledge: 0.5, research: 0.4, code: 0.4, solution: 0.9 }, maxSubtasks: 1 },
];
```

**同时**: profiles.json（如果存在）的权重加载逻辑要合并到 fallback 之上，不要完全覆盖。当前要么读文件要么走 fallback → 改为 fallback-first + JSON 覆盖。

### 2. provider 配置动态化（llmRoute）

**改动**: `eto/extensions/eto.ts` — 读取 `.pi/eto-config.json` 获取 provider 配置

当前代码写死在 `llmRoute()`（第151-184行），要改成：
```typescript
async function llmRoute(task: string, config: RouterConfig): Promise<RouteResult | null> {
  if (config.provider === "ollama") {
    // 调 Ollama /api/chat endpoint
  } else if (config.provider === "deepseek") {
    const apiKey = process.env.DEEPSEEK_API_KEY;
    if (!apiKey) return null;  // fallback to keyword
    // 调 DeepSeek API
  }
  // config.provider === "skip" → 直接返回 null，只用 keyword
}
```

**新增**: `.pi/eto-config.json`（由 bootstrap bundle 自动生成）

### 3. 同步两版 eto.ts（清理重复）

**问题**: `.pi/extensions/eto.ts` (V3) vs `eto/extensions/eto.ts` (V3+)，内容不一致。

**决定**: 以 `eto/extensions/eto.ts` 为 source of truth。bootstrap bundle 的 config_step 自动建立 symlink 或复制。

### 4. LLM 路由置信度阈值调整

**当前**: `eto/extensions/eto.ts:204` — `confidence >= 0.3` 太低
**改为**: `>= 0.5`，低于 0.5 时在 widget 标注低置信度警告

### 5. 空状态 Bug 测试清单（ES-9 修复）

**文件**: `docs/test/eto-empty-states.md`（新建）

已知空状态场景：

| # | 场景 | 预期 | 实际（当前） | 状态 |
|---|------|------|-------------|------|
| ES-1 | skills.jsonl 不存在 | matchSkillsForRoute 返回空数组 | ✅ catch | PASS |
| ES-2 | profiles.json 不存在 | loadProfiles fallback | ✅ | PASS |
| ES-3 | metrics.jsonl 不存在 | /metrics 提示不可用 | TODO |
| ES-4 | widget 无任务 | 显示 "ETO 等待中..." | | PASS |
| ES-5 | LLM route + keyword 都失败 | fallback 默认值 | ✅ code/direct | PASS |
| ES-6 | 历史任务为空 | widget 正常 | TODO |
| ES-7 | peers 列表为空 | registry 无报错 | TODO |
| ES-8 | eto-config.json 不存在 | 默认 DeepSeek + keyword | TODO |
| **ES-9** | Ollama 未安装但 config 设了 ollama | 回退到 keyword | **❌ crash** | **FAIL** |
| ES-10 | DEEPSEEK_API_KEY 被删除 | keyword fallback | ✅ | PASS |

**重点修复**: ES-9 —— `llmRoute` Ollama unreachable 时必须有 graceful degradation（return null → keyword fallback），不能 throw/crash。

---

## 验收标准

### Part A — Profile + Router（改动 1-2+4）

| # | 检查项 | 验证方式 |
|---|--------|----------|
| A1 | `matchAgentsForRoute("code")` 返回 `[coder, auditor]` | grep profiles.json 或跑 bootstrap |
| A2 | `.pi/eto-config.json` 存在且 provider 生效 | cat 文件 + grep config.provider |
| A3 | Ollama unreachable 时不 crash（ES-9） | kill ollama + 运行任务 → keyword fallback |
| A4 | 置信度阈值 = 0.5 | grep `confidence >=` |

### Part B — Bootstrap Bundle（改动 3+6）

| # | 检查项 | 验证方式 |
|---|--------|----------|
| B1 | `python3 -m eto.bootstrap` exit code 0 | 实际运行 |
| B2 | profiles.json 生成且有 3 条 | cat + wc |
| B3 | skills.jsonl 生成且有 5 条 | cat + wc |
| B4 | eto-config.json 生成 | ls |

### Part C — Onboarding UI

| # | 检查项 | 验证方式 |
|---|--------|----------|
| C1 | session_start widget 显示引导序列 | 检查字符串 "欢迎" / "支持的类型" |
| C2 | Quick Start prompt 仅注入一次 | 二次启动不出现 |

---

## 实施顺序（两批）

```
Batch 1:
  Step 1 → Profile weights fix (eto/extensions/eto.ts)        — 5 min
  Step 2 → config_template.py + bootstrap/__init__.py         — 8 min
  Step 3 → seed_profiles + seed_sample_skills + seed_sample_tasks  — 10 min
  Step 4 → llmRoute provider switch (eto/extensions/eto.ts)   — 10 min
  Step 5 → ES-9 fix: ollama graceful degradation              — 5 min

Batch 2:
  Step 6 → session_start onboarding UI                         — 10 min
  Step 7 → empty states test doc (docs/test/eto-empty-states.md) — 5 min
  Step 8 → sync eto.ts versions                               — 5 min
```

总计约 45 分钟。

## 参考

- Profile weights 问题: `eto/extensions/eto.ts:31-33` + `matchAgentsForRoute`:40-46
- profiles.json source of truth: `eto/stitches/profiles.json:1-26`（有正确权重，JS fallback 覆盖了）
- profile_editor.py: `eto/stitches/profile_editor.py:1-87`（可复用 CLI）
- LLM Route: `eto/extensions/eto.ts:151-184`（写死 DeepSeek）
- registry: `eto/stitches/registry.py:6-9`（PEERS 空字典 = 白板）
