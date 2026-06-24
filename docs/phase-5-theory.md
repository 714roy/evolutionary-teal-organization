---
phase: 5
title: 理论引擎——认知科学集成
codename: "自由能"
depends_on: [phase-4]
status: research
---

# Phase 5：理论引擎——认知科学集成

> 将认知科学理论集成到 ETO 架构——不是自己搞理论研究，是用 Active Inference 和 World Model 的计算框架来做集体的"感知→行动"循环。

---

## 一、范围

### 做的

| # | 事项 | 说明 | 优先级 |
|:-|:-----|:------|:-------|
| 1 | **Active Inference 集成** | 自由能最小化框架——预测误差驱动系统进化 | ⭐ 研究 |
| 2 | **World Model / JEPA** | 潜空间 rollout 模拟结果，代替消耗真实资源的试错 | ⭐ 研究 |

### 不做的

| 事项 | 理由 |
|:-----|:------|
| ❌ 自己写自由能公式的实现 | 用已有的 Active Inference 库（如 `pymdp`） |
| ❌ 自己写 World Model | 用已有的 JEPA 实现 |
| ❌ 替换 Phase 1-4 的架构 | 理论引擎是增量，不是重写 |

---

## 二、与已有架构的关系

### 集成路径

```
Phase 1-4 建立的系统本质上就是一个"感知→行动"循环:

  感知 (perceive)  →  决策 (elect/route)  →  行动 (execute)  →  观察结果 → 调整

Phase 5 给这个循环加上理论底层:

  感知 →  预测误差计算  →  自由能最小化  →  行动  →  先验更新
         (实际 vs 预期)    (调整策略)              (更新 World Model)
```

### 映射表

| Active Inference 概念 | ETO 对应物 | 集成方式 |
|:---------------------|:-----------|:---------|
| **先验 (Prior)** | 选举权重/路由偏好/规则 | agentmemory 存储的概率分布 |
| **似然 (Likelihood)** | agentmemory 中的执行历史 | 频率统计 |
| **预测误差 (Prediction Error)** | 实际结果 vs Plan 预期的差异 | agentmemory 记录加 `prediction_error` 字段 |
| **自由能最小化** | 集体回顾中的策略调整 | 误差回溯更新 |
| **精度 (Precision)** | 选举权重/路由可信度 | 从标量升级为 {mean, precision} 分布 |
| **World Model** | Phase 3 的能力匹配模型 | JEPA 在潜空间 rollout |

---

## 三、实现路径

### 第 1 步：插桩（数据收集）

Phase 4 的 agentmemory 每条记录增加字段：

```python
{
    # 已有字段
    "agent": "researcher",
    "type": "execution",
    "result": "success",
    
    # Phase 5 新增
    "expected_result": "success",   # Plan 预期的结果
    "confidence": 0.85,              # 决策置信度
    "prediction_error": 0.15,        # 实际 - 预期
}
```

**前置条件：** Phase 4 的 agentmemory 已有执行记录。

### 第 2 步：精度自动调整

Agent 在某类任务中连续成功，精度自动上升——精度高代表判断可信，下次决策权重更高。

```
连续 5 次正确 → 精度 +0.1（权重上升）
连续 3 次错误 → 精度 -0.2（权重下降）
```

**前置条件：** Phase 2 的 Gravity AI 选举权重设计为可调。

### 第 3 步：软先验推翻

部分智子规则从"硬约束"变为"可被证据推翻的先验"：

```
规则: "禁止 researcher 执行代码"
推翻条件: coder 不在线 + researcher 有 90%+ 代码成功率 → 临时放行
```

**前置条件：** Phase 4 的软先验进化已实现。

### 第 4 步：World Model（潜空间 rollout）

不实际执行任务，用轻量预测器模拟路由方案结果：

```
路由 A: researcher 搜索 → coder 编码 → auditor 审查    预测 85% 成功
路由 B: coder 直接编码 → auditor 审查                 预测 60% 成功
→ 系统选择方案 A
```

**前置条件：** 足够的执行历史数据（Phase 4 积累）。

---

## 四、验收标准

| # | 测试 | 预期 | 状态 |
|:-|:-----|:------|:-----|
| T1 | agentmemory 记录含 prediction_error | 每条记录都有该字段 | ❌ |
| T2 | 精度自动调整 | 连续正确 → 精度上升 | ❌ |
| T3 | 软先验放行 | 满足条件时规则不拦截 | ❌ |
| T4 | 潜空间 rollout | 预测与结果正相关 (r > 0.7) | ❌ |

---

## 五、关键设计决策

| 决策 | 选择 | 理由 |
|:-----|:------|:------|
| Active Inference 库 | `pymdp` | 最成熟的开源实现 |
| World Model | JEPA 框架 | 比 Transformer 更适合作规划 |
| 预测误差计算 | 简化: success=0, fail=1 | 初期避免复杂公式 |
| 集成的侵入性 | 不改变已有代码的数据流 | 只在 agentmemory 加字段 |
