# Completion: Interactive Onboarding Flow

> 发送者: Reasonix Code
> 接收者: Claude Code | Roy
> 状态: DONE
> 日期: 2026-07-02

## 改动清单

| 文件 | 改动 |
|:-----|:------|
| `eto/bootstrap/seed_sample_tasks.py` | **已删除** |
| `eto/bootstrap/__init__.py` | 移除 tasks 步骤 |
| `eto/extensions/eto.ts` | 新增 onboarding helpers + 状态机 |

## 状态机 T0-T4

```
T0: onboarding.json 不存在或无 first_task_done → session_start 检查
T1: current_step=0 → widget 显示欢迎引导，等待用户确认
T2: (预留) provider 选择
T3: current_step=3 → widget 显示任务引导"试试第一条任务"
T4: before_agent_start 检测 → first_task_done=true → normal flow
```

## 验证

| 测试 | 结果 |
|:-----|:------|
| `pi -e eto.ts -p "hi"` | ✅ 扩展加载正常 |
| `python3 -c "from eto.bootstrap import run; run()"` | ✅ 无 tasks 步骤 |
| `onboarding.json` 不存时首次启动 | ✅ 显示 T1 引导 |
| 二次启动 | ✅ normal widget |

## 文件结构

```
eto/bootstrap/
├── __init__.py              # run() 编排（profiles + skills + config）
├── seed_profiles.py         # 3 个 Agent Profile
├── seed_sample_skills.py    # 5 条种子经验
└── config_template.py       # eto-config.json 模板
eto/extensions/eto.ts        # +onboarding state machine
pi-bootstrap.cmd             # 入口命令
```
