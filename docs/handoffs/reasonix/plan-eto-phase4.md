# Plan: ETO Phase 4 — Onboarding + 稳健性 + 智子

> 创建日期: 2026-07-02 | 来源: Roy (Claude Code)
> 执行: Reasonix（编码实现）→ Claude Code（审计）

---

## 概述

三件事独立推进，A→B→C 顺序依赖关系：

```
A (Onboarding) ─┐
                 ├──→ B (空状态测试验证) ──→ C (智子扩展)
B (空状态) ──────┘
```

A 改动的文件最多，先做。B 验证 A 没破坏东西。C 是新功能，最后。

---

## A: 交互式 Onboarding（替换现有 T0→T4 状态机）

**问题**: 当前 Onboarding 状态机（`eto/extensions/eto.ts` 的 `session_start` handler）推进步骤靠 switch-case，但 session_start 只触发一次——没有用户交互通道让 step 推进。所以 T0→T4 跑不到 step 2/3。

**改为 Grilling Pattern**（参考 mattpocock/skills 的 `grilling` 技能）：

核心原则：**一次只问一个问题，等用户回复再继续。**

### 流程

```
T0: 检测 first_run（onboarding.json 不存在）
    → widget: "🦋 ETO 你好！多 Agent 编排系统。开始配置？回复「是」"

T1: 用户回复「是」（在 before_agent_start 里检测 prompt）
    → widget: "选择 LLM Provider:
      1) DeepSeek API
      2) Ollama 本地模型
      3) 跳过（纯关键词）
      回复数字即可"

T2: 用户回复 1/2/3
    → 写入 eto-config.json
    → widget: "配置完成！试试描述任务：帮我写个 Python 程序"

T3: 用户描述真实任务
    → ETO plan 路由 → coder + auditor 执行
    → before_agent_start 检测到 current_step=3 → current_step=4
    → widget: "🎉 首次配置完成！之后直接说话就行。"
```

### 对 seed_sample_skills 的修改

当前 `seed_sample_skills.py` 写入 5 条硬编码 skill（circuit-breaker、empty-state-handling 等）。
改为：Empty（不注入假经验数据），改为由 Onboarding T3 创建真实任务后记录一条 skill 到 `~/.eto/memory/skills.jsonl`。

### 改动文件

| 文件 | 改动 |
|------|------|
| `eto/extensions/eto.ts` | Onboarding handler 重写为 grilling pattern（一次一问） |
| `eto/extensions/eto.ts` | 新增 `message_received` handler（如果有）或 `before_agent_start` 检测 |
| `bootstrap/seed_sample_skills.py` | 改为 empty seed（不写假数据） |
| `bootstrap/__init__.py` | 不再强制写入 skills 种子（空就空） |

### 验收 A

| # | 检查项 | 验证方式 |
|---|--------|----------|
| A1 | first_run 显示 welcome | widget 包含 "开始配置" |
| A2 | 用户说「是」→ 选 provider | provider 选择框出现 |
| A3 | 用户说跳过 → 不阻塞 | onboarding.skipped = true |
| A4 | 完成第一条任务 → 通知完成 | widget 包含 "首次配置完成" |
| A5 | 二次启动不再引导 | session_start widget = normal |
| A6 | seed_sample_skills 为空 | skills.jsonl 行数 = 0 |

---

## B: 空状态测试文档

**文件**: `docs/test/eto-empty-states.md`（新建）

### 测试矩阵

| # | 场景 | 触发方式 | 预期 |
|---|------|----------|------|
| ES-1 | skills.jsonl 不存在 | 删除 `~/.eto/memory/skills.jsonl` | `matchSkillsForRoute` 返回 []，不 crash |
| ES-2 | profiles.json 不存在 | 删除 `~/.pi/etoprofiles/profiles.json` | `loadProfiles` fallback 到硬编码默认 |
| ES-3 | metrics.jsonl 不存在 | 删除 `~/.eto/memory/metrics.jsonl` | `/metrics` 提示不可用 |
| ES-4 | widget 无任务时 | 首次启动 | 显示 "ETO 等待中..." |
| ES-5 | LLM + keyword 都失败 | 设 provider=deepseek + 删 API key | fallback 到 code/direct |
| ES-6 | 历史任务为空 | never called | widget 正常 |
| ES-7 | peers 列表为空 | start registry without peers | `registry.py` 返回 {}，不 crash |
| ES-8 | eto-config.json 不存在 | 删除 `~/.pi/eto-config.json` | `loadRouterConfig` 用默认值 |
| **ES-9** | Ollama 未安装但 config 设了 ollama | 设 provider=ollama + kill Ollama | 回退到 keyword，不 crash |
| ES-10 | DEEPSEEK_API_KEY 被删除 | unset env | keyword fallback |
| ES-11 | onboarding.json 不存在 | 首次运行 | `loadOnboarding` fallback 到 step 0 |
| ES-12 | sentinel.json 不存在 | 运行危险命令 | `loadSentinelConfig` 用默认规则 |

### 测试脚本（Python / pytest）

每个 ES 对应一个 pytest case，使用临时 HOME 目录 + mock 文件：

```python
# docs/test/test_empty_states.py 示例
import os, shutil, tempfile, json
from pathlib import Path

def test_es1_skills_file_missing():
    """skills.jsonl 不存在时 matchSkillsForRoute 返回 []"""
    # setup: empty home dir, no .eto/memory
    # call: loadSkills()
    # assert: returns []
    
def test_es9_ollama_down_fallback():
    """Ollama unreachable 时 keywordRoute 兜底"""
    # setup: eto-config.json provider=ollama
    # call: llmRoute()
    # assert: returns null → keywordRoute takes over
```

### 验收 B

| # | 检查项 | 验证方式 |
|---|--------|----------|
| B1 | 12 个场景全部有测试 | grep 文件 |
| B2 | ES-9 实际跑过不 crash | Node.js fetch dead host → null |
| B3 | ES-1~12 测试脚本 exit code 0 | pytest 运行 |

---

## C: 智子扩展 — 规则增强

### 新增能力

#### C1: 频率限制

在 sentinel config 加 `rateLimit` 字段：

```json
{
  "enabled": true,
  "rateLimit": {
    "windowMs": 60000,      // 1 分钟窗口
    "maxPerWindow": 5,      // 窗口内 max 拦截/确认操作数
    "action": "block"       // 超限后行为
  },
  "logFile": "~/.eto/sentinel-log.jsonl",
  "rules": [...]
}
```

**实现**: `checkSentinel` 内维护一个 `Map<string, number[]>` 记录每条规则的触发时间戳，判断窗口内触发次数。

#### C2: 文件内容扫描

新增 scanner 函数，在 `write_file` 事件前检查内容：

```typescript
function scanFileContent(content: string, filepath: string): SentinelRule | null {
  // 检查是否含 API key 模式
  if (/(?:sk-|api_key|apiSecret).{10,}/i.test(content)) return ...;
  // 检查特定路径 pattern
  if (/\.(pem|key|p12|env)$/i.test(filepath)) return ...;
  return null;
}
```

#### C3: 重新加载命令

新增 `/sentinel-reload` 命令，热重载 sentinel 配置文件（不重启 Pi CLI）：

```typescript
pi.registerCommand("sentinel-reload", {
  description: "重新加载智子安全检查配置",
  handler: async () => { SENTINEL = loadSentinelConfig(); }
});
```

### 改动文件

| 文件 | 改动 |
|------|------|
| `.pi/eto-sentinel.json` | 加 rateLimit 字段 |
| `eto/extensions/eto.ts` | checkSentinel + rateLimit 实现 + 内容扫描 + reload 命令 |
| `docs/test/eto-empty-states.md` | ES-12 验证 |

### 验收 C

| # | 检查项 | 验证方式 |
|---|--------|----------|
| C1 | 同规则 5 次/分钟 → block | 模拟触发 6 次，第 6 次被拦截 |
| C2 | 写文件含 API 模式 → block | `write "sk-1234567890"` → 拦截 |
| C3 | `/sentinel-reload` 更新生效 | 改 config 然后 reload，新规则匹配 |
| C4 | ES-12 sentinel.json 缺失 → fallback | 删文件后 rule match 仍工作 |

---

## 实施顺序

```
Phase 4-A (Reasonix)
  Step 1 → seed_sample_skills.py 清空
  Step 2 → Onboarding grilling rewrite (eto/extensions/eto.ts)
  Step 3 → bootstrap/__init__.py 同步（删除 seed_skills 调用的示例）

Phase 4-B (Reasonix)
  Step 4 → docs/test/eto-empty-states.md 文档
  Step 5 → 测试脚本（pytest for each ES case）

Phase 4-C (Reasonix)
  Step 6 → .pi/eto-sentinel.json 加 rateLimit
  Step 7 → eto/extensions/eto.ts checkSentinel + scanFileContent + sentinel-reload
```

## 文件清单（最终状态）

```
eto/extensions/eto.ts        ← A 部分+ C 部分（onboarding + sentinel 增强）
bootstrap/seed_sample_skills.py ← A 部分（清空）
bootstrap/__init__.py        ← A 部分（同步）
docs/test/eto-empty-states.md  ← B 部分（空状态测试文档）
docs/test/test_empty_states.py  ← B 部分（pytest 测试脚本）
.pi/eto-sentinel.json        ← C 部分（rateLimit + 扫描规则）
.claude/rules/eto-guide.md   ← 已有，内容更新（按需）
```
