# Empty States (ES) Test — ETO 空状态验证

> 目的: 确认 ETO 在所有"空/未配置/不可用"场景下不崩溃、不报错、优雅降级。
> 更新: 2026-07-02

## 场景清单

| # | 场景 | 触发方式 | 预期行为 | 实际 | 状态 |
|---|------|---------|---------|------|------|
| ES-1 | `skills.jsonl` 不存在 | 删 `~/.eto/memory/skills.jsonl` → 启动 | `matchSkillsForRoute` 返回 `[]`，widget 正常 | ✅ PASS |
| ES-2 | `profiles.json` 不存在 | 删 `~/.pi/etoprofiles/profiles.json` → 启动 | `loadProfiles()` fallback 到硬编码默认值 | ✅ PASS |
| ES-3 | `metrics.jsonl` 不存在 | 删 `~/.eto/memory/metrics.jsonl` → 运行 `/metrics` | 提示 "Metrics 不可用" | ✅ PASS |
| ES-4 | 无任务时 widget | 首次启动无历史 | 显示 "📋 ETO 等待中..." | ✅ PASS |
| ES-5 | LLM 路由 + keyword 都失败 | 关网 + 无可匹配关键词 | fallback 到 `{ code, direct }` | ✅ PASS |
| ES-6 | `onboarding.json` 不存在 | 首次启动 | 自动创建，显示 T1 欢迎 | ✅ PASS |
| ES-7 | peers 列表为空 | `GET /peers` | 返回 `{"peers":{}}` 无报错 | ✅ PASS |
| ES-8 | `eto-config.json` 不存在 | 删文件 → 启动 | `loadRouterConfig()` 返回默认 deepseek | ✅ PASS |
| ES-9 | ollama 不可达但 config 设了 ollama | 停 ollama 服务 → 运行任务 | `callOllama()` 返回 null → keyword fallback | ✅ PASS |
| ES-10 | `DEEPSEEK_API_KEY` 未设置 | 删环境变量 → 运行 | `callDeepSeek()` 返回 null → keyword fallback | ✅ PASS |
| ES-11 | `before_agent_start` 无 task | 空 prompt | event.prompt 为空 → 直接 return | ✅ PASS |
| ES-12 | bootstrap 未运行（profiles/skills 都不存在） | 全新环境 | `loadProfiles()` fallback 到硬编码值 | ✅ PASS |

## 快速验证命令

```bash
# ES-9: Ollama 不可达
ollama stop
pi -p "hello"
# 应显示 keyword route，不报错

# ES-10: 无 API key
set DEEPSEEK_API_KEY=
pi -p "hello"
# 应显示 keyword route，不报 Connection error

# ES-1: 无 skills
del %USERPROFILE%\.eto\memory\skills.jsonl
pi -p "写个函数"
# 应正常运行，无技能匹配

# ES-6: 首次启动
del %USERPROFILE%\.eto\memory\onboarding.json
pi
# 应显示 T1 欢迎 widget
```
