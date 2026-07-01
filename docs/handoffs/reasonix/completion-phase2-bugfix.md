# Completion: Phase 2 Bugfix — Unicode + Retry

> 发送者: Reasonix Code
> 接收者: Claude Code
> 状态: DONE
> 日期: 2026-07-01

## Bug 1: Unicode 乱码 ✅

在 3 个 stitcher Python 文件加 `sys.stdout.reconfigure(encoding="utf-8")`：

| 文件 | 改动 |
|:-----|:------|
| `eto/stitches/comms/a2a.py` | +encoding fix |
| `eto/stitches/consensus/vote.py` | +encoding fix |
| `eto/stitches/election/elect.py` | +encoding fix |

## Bug 2: LLM retry 暴露 ✅

| 改动 | 值 |
|:-----|:----|
| `llmRoute` AbortSignal.timeout | 15000ms → **2000ms** |
| `routeTask` fallback | 已有立即降级逻辑（无需改） |

Ollama 连不上时 2s 快速超时→静默降级到 keywordRoute，不再触发 Pi SDK 的 3 次重试。

## 验证

| 测试 | 结果 |
|:-----|:------|
| Stitcher 9/9 | ✅ 全部通过 |
| `pi -e eto.ts -p "hi"` | ✅ 正常加载 |
| `llmRoute` timeout 值 | ✅ 已改为 2000ms |

## 请审计

1. 确认 3 个 Python 文件有 `sys.stdout.reconfigure`
2. 确认 `AbortSignal.timeout` 为 2000
3. 确认 Stitcher 9/9
