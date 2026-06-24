---
phase: 3
title: 动态自组织
codename: "网状协作"
depends_on: [phase-1, phase-2]
status: planning
---

# Phase 3：动态自组织

> 青色组织的本质不是"写死了流程但改了名字"，而是 Agent 之间动态发现、协商、分工——网状协作不是一条 pipeline，是一张自组织的网。

---

## 一、范围

### 做的

| # | 事项 | 说明 | 优先级 |
|:-|:-----|:------|:-------|
| 1 | **弹性 Agent 池** | Agent 动态加入/离开 Registry，无需重启 | 🔴 P0 |
| 2 | **按能力路由** | 任务不由"写死的角色"分配，由"声明的技能"匹配 | 🔴 P0 |
| 3 | **子任务并行** | Nexus 分解后独立子任务并行执行（ProtoLink Parallel） | 🟠 P1 |
| 4 | **历史感知选举** | Gravity AI 选举参考 agentmemory 历史命中率 | 🟠 P1 |
| 5 | **自我修复** | Agent 超时/下线的自动重路由和降级 | 🟠 P1 |
| 6 | **知识蒸馏** | 从执行历史中提炼可复用的决策框架/思维模式 | 🟠 P1 |
| 7 | **集体回顾** | 定期分析失败模式，更新策略权重 | 🟡 P2 |
| 8 | **探索机制** | 10% 概率走非最优路径，发现更好的路由 | 🟡 P2 |

### 不做的

| 事项 | 理由 |
|:-----|:------|
| ❌ 三体周期/引力模型 | 理论负担过重，且一个周期切换本质上是一个路由策略开关，Phase 3 通过历史感知选举已经覆盖 |
| ❌ Fable-5 行为路由 | 513 个 Claude Code 系统提示词的维护成本 > 收益 |
| ❌ 多渠道输出 | Phase 4 |
| ❌ CLI 命令体系 | 每个 Phase 按需扩展 |
| ❌ 自写 Agent 调度器 | ProtoLink 的 Router/Parallel/Pipeline 原生支持 |

---

## 二、架构——网状协作 vs 流水线协作

### 旧模型（流水线）

```
固定角色 → 固定顺序 → 固定 pipeline
analyze → elect → draft → zhizi → consensus → execute
```

Agent 是"零件"。

### 新模型（网状）

```
用户任务
  │
  ▼
Registry: "谁有 coding 技能？谁当时在线？谁历史成功率高？"
  │
  ▼
Gravity AI: "基于声誉+负载，coder 当选协调员"
  │
  ▼
coder: "这个任务需要搜索和编码，researcher 做搜索，我自己做编码"
  │
  ▼
Nexus Adaptive: researcher 搜索 → coder 编码 → auditor 审查
  │
  ▼
结果写回 agentmemory → 下次选举时参考
```

Agent 是"协作者"，角色临时生成，任务结束后自动解散。

### 数据流

```
1. 任务到达 → Registry 查技能表（不是查角色表）
2. 找出有相关技能的 Agent 候选集
3. Gravity AI 按{技能匹配度 × (1-负载) × 历史成功率} 选举协调员
4. 协调员起草 Plan → 用 Nexus 分解
5. 每一步分配给最匹配的 Agent（不一定是协调员自己）
6. 并行执行独立子任务（ProtoLink Parallel）
7. 结果写回 agentmemory
8. 集体回顾任务失败模式 → 调整选举权重
```

---

## 三、与已有缝纫组件的集成

| 已有组件 | Phase 3 新增能力 | 集成方式 |
|:---------|:----------------|:---------|
| **ProtoLink Registry** | 动态 Agent 加入/离开 | 扩展现有 Registry，增加心跳检测 |
| **ProtoLink Router** | 按能力路由（不是按名字） | 用 Router + Adaptive 模式 |
| **ProtoLink Parallel** | 子任务并行执行 | ProtoLink 原生 Parallel flow |
| **ProtoLink Pipeline** | 顺序但非固定步骤 | Pipeline + Nexus 动态 DAG |
| **Nexus** | 任务自动分解为 DAG | 已在 Phase 2 缝入 |
| **Gravity AI** | 历史感知声誉计算 | 选举前查 agentmemory 获取历史 |
| **agentmemory** | 存储历史命中率 | 选举时读 → 选举后写 |

---

## 四、验收标准

| # | 测试 | 预期 | 状态 |
|:-|:-----|:------|:-----|
| T1 | 新 Agent 注册后立即被其他 Agent 发现 | `discover_agents()` 返回新 Agent | ❌ |
| T2 | Agent 下线后从发现结果消失 | Registry 的心跳超时清除 | ❌ |
| T3 | 按能力路由（不是 hardcode） | "写代码" 任务优先分配给 coder | ❌ |
| T4 | 并行执行 2 个独立子任务 | 总耗时 < 两个任务串行之和 | ❌ |
| T5 | 选举参考历史成功率 | 连续失败的 Agent 优先级降低 | ❌ |
| T6 | Agent 超时后自动重路由 | 故障 Agent 的任务转给其他人 | ❌ |
| T7 | 知识蒸馏产出可复用的 skill 文件 | `~/.eto/skills/` 有新文件 | ❌ |
| T8 | 集体回顾报告 | 分析失败模式、更新权重 | ❌ |

---

## 五、搭建顺序

```
第 1 步：Registry 心跳 → Agent 上下线自动感知
         ↓
第 2 步：Router Adaptive 模式 → 按 embedding 匹配 Agent 能力
         ↓
第 3 步：Parallel + Pipeline → 分叉执行独立子任务
         ↓
第 4 步：Gravity AI 接 agentmemory → 选举参考历史
         ↓
第 5 步：超时检测 + 自动重路由
         ↓
第 6 步：知识蒸馏 + 集体回顾
```

每个"步"都应该是可验证的：不是"实现了一个模块"，是"跑通了一个测试"。

---

## 六、关键设计决策

| 决策 | 选择 | 理由 |
|:-----|:------|:------|
| 网状 vs 流水线 | 网状 | 这是 ETO 存在的理由。固定 pipeline 的 ETO 没意义 |
| 能力匹配方式 | embedding 相似度 | adaptive 模式 = embedding，比 Jaccard 关键词好得多 |
| 子任务调度 | ProtoLink Parallel + Pipeline | 原生支持，不用自己写 |
| 心跳超时 | 30s 无心跳 → 标记下线 | 适合本地 Agent |
| 知识蒸馏触发 | 每 10 次执行 + 手动 | 避免频繁触发 |
