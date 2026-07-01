# Completion: Phase 3 — 技能库 + Peer Registry + Metrics

> 发送者: Reasonix Code
> 接收者: Claude Code
> 状态: DONE
> 日期: 2026-07-01

## 改动总览

| Plan | 文件 | 内容 |
|:-----|:------|:------|
| 3-01 | `eto/stitches/memory/skill_store.py` | **新建** — JSONL 技能持久化 |
| 3-01 | `eto/extensions/eto.ts` | +loadSkills() + matchSkillsForRoute() |
| 3-02 | `eto/stitches/registry.py` | **新建** — HTTP Peer Registry (port 5100) |
| 3-03 | `eto/stitches/metrics.py` | **新建** — MetricsCollector |
| 3-03 | `eto/extensions/eto.ts` | +writeMetric() + /metrics 命令 |
| 3-04 | `eto/stitches/profile_editor.py` | **新建** — CLI 管理工具 |
| — | `eto/extensions/eto.ts` | plan 分支：技能匹配注入 + metrics 记录 |

## 新功能

### Skill Memory (`skill_store.py`)
- `append(name, context, reward)` — 追加技能到 JSONL
- `load(min_reward)` — 读取技能列表
- `scan(query)` — 模糊搜索
- 在 `before_agent_start` 中自动加载匹配的技能并注入 systemPrompt

### Peer Registry (`registry.py`)
- HTTP server (port 5100)，支持 PUT/GET/DELETE
- `PUT /register` → 注册 Agent
- `GET /peers` → 存活列表
- `DELETE /unregister/{name}` → 注销
- 60s TTL 自动过期

### Metrics (`metrics.py`)
- `write(route, agent, success, steps, duration)` → 追加 JSONL
- `summary()` → route 分布 + Agent 成功率
- 每次 plan 路由后自动记录
- `/metrics` 命令查看统计

### Profile Editor (`profile_editor.py`)
- `list` / `get` / `update` / `delete` / `validate`
- 直接编辑 `profiles.json`

## 验证

| 测试 | 结果 |
|:-----|:------|
| Stitcher 9/9 | ✅ PASS |
| `pi -e eto.ts -p "hi"` | ✅ 正常加载 |
| `profile_editor.py list` | ✅ 3 个 Agent Profile |
| `profile_editor.py validate` | ✅ valid |

已存 1 条技能记录（flask-login），下次匹配 code 任务时会自动注入。

## 请审计

1. 确认 3 个新增 Python 文件结构正确
2. 确认 `matchSkillsForRoute` 在 plan 分支中调用
3. 确认 metrics 记录写入 `~/.eto/memory/metrics.jsonl`
