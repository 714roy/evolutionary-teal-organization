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
| `docs/handoffs/reasonix/plan-fix-profiles-and-local-model.md` | Claude Code | 📝 计划中（未开始编码） |
| `eto/extensions/eto.ts` | — | ⏳ 待改动 |
| `eto/stitches/` | — | ⏳ 待新增 seed_* 模块 |
| `.pi/extensions/` | — | ⏳ 待同步 |
| `docs/test/eto-empty-states.md` | — | ⏳ 待新建 |

## 协议

- **Claude → Reasonix**: `docs/handoffs/reasonix/plan-<任务名>.md`
- **Reasonix → Claude**: `docs/handoffs/reasonix/completion-<任务名>.md`
- 人类触发流转：「去看 docs/handoffs/reasonix/plan-xxx.md」→「审计」
- 改文件前先声明锁（在 INDEX.md 中登记持有者+操作），改完释放
