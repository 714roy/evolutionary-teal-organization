# Reasonix — 并行会话注册表

> 文件接力协议：Claude Code（计划审计）↔ Reasonix（编码实现）

| 会话 | Agent | 状态 | 焦点 | 最后活跃 |
|:-----|:------|:-------|:-----|:---------|
| main | Claude Code | ACTIVE | 计划/审计/统合 | 2026-07-02 |
| coder | Reasonix | CLOSED | Phase 2-01: Async Stitcher + Profile | 2026-06-27 |
| coder | Reasonix | CLOSED | Phase 2-02: Decompose + Dispatch | 2026-06-27 |
| coder | Reasonix | CLOSED | Phase 2-03: Synthesis + Guards | 2026-06-27 |

## 活跃锁

| 路径 | 持有者 | 操作 |
|:-----|:-------|:-----|
| `docs/handoffs/reasonix/plan-eto-phase4.md` | Claude Code | 📝 计划就绪 |
| `eto/extensions/eto.ts` | — | ⏳ Phase 4-A: Onboarding grilling rewrite |
| `eto/extensions/eto.ts` | — | ⏳ Phase 4-C: 智子扩展（rateLimit + scan + reload） |
| `bootstrap/seed_sample_skills.py` | — | ⏳ 清空种子数据（不写假 skill） |
| `bootstrap/__init__.py` | — | ⏳ 同步删除 seed_tasks 引用 |
| `docs/test/eto-empty-states.md` | — | ⏳ Phase 4-B: 空状态测试文档 |
| `docs/test/test_empty_states.py` | — | ⏳ Phase 4-B: 测试脚本 |
| `.pi/eto-sentinel.json` | — | ⏳ Phase 4-C: 加 rateLimit 字段 |

## 协议

- **Claude → Reasonix**: `docs/handoffs/reasonix/plan-<任务名>.md`
- **Reasonix → Claude**: `docs/handoffs/reasonix/completion-<任务名>.md`
- 人类触发流转：「去看 docs/handoffs/reasonix/plan-xxx.md」→「审计」
- 改文件前先声明锁（在 INDEX.md 中登记持有者+操作），改完释放
