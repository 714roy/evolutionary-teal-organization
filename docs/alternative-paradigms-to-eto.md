---
type: design-spec
title: 替代范式在 ETO 中的应用映射（深扩版）
description: Active Inference 的具体接入方案 + World Model / JEPA 的层次化潜空间规划，以及液态网络/超维计算/Neuro-Symbolic 的应用分析
tags: [eto, ai-paradigms, active-inference, world-model, jepa, neuro-symbolic, architecture, research]
timestamp: 2026-06-20
---

# 替代范式 × ETO 架构映射（深扩版）

> 五大范式，重点深挖 Active Inference 和 World Model——它们是 ETO 从琥珀色进化到青色的理论引擎。

---

## 1. Active Inference / 自由能原理 → ⭐⭐⭐ 最高优先级

### 核心机制

大脑不是「从输入算出输出」。它维护一个**生成模型**（对世界如何运作的全部假设），然后同时做两件事：

- **感知（Perception）**：更新模型来拟合感官输入，降低 surprise
- **行动（Action）**：采取行动让世界符合模型预期，主动降低 surprise

自由能 = 模型对世界的预测误差。系统持续最小化这个量。

### 为什么这对 ETO 是根本性的

ETO 当前最深层的问题是：**Agent 失败之后怎么办？**

现在的答案（三省六部琥珀色）是「审核链打回重做」——这是事后修补，不是系统学习。
Active Inference 给的答案是：**失败不是异常，是信号。系统靠预测误差驱动进化。**

```
当前 ETO（事后修补）：
Agent 执行 → 结果不满意 → 打回重做 → 下次还走老路

Active Inference ETO（信号驱动）：
Agent 执行 → 结果不满意（预测误差↑）
  → 两条路同时启动：
    路径1（感知）：更新生成模型
      「原来兵部不擅长写文档 → 下次同类任务换人」
    路径2（行动）：主动采样降低误差
      「再试一次，但这次换方式」
  → 误差持续高位 → 更新先验（智子加规则）
  → 反复同模式低误差 → 固化（变成默认路由）
```

### 具体接入方案：五层改造

#### 第一层：TealContext → 生成模型（Generative Model）

当前的 TealContext 是**被动存储**（放记忆、放提议、放日志）。Active Inference 要求它升级为**主动生成模型**——能从当前状态预测「什么路由方案会有什么结果」。

```typescript
interface GenerativeModel {
  // 三层生成模型
  strategic: {  // 通政司层——任务类型 × 路由方案
    predict(task: Task, route: Route): OutcomePrediction;
    update(observation: Outcome): void;
  };
  tactical: {   // Fable-5 层——行为模式 × 任务场景
    predict(mode: BehaviorMode, context: TaskContext): ModePrediction;
    update(observation: Outcome): void;
  };
  operational: { // Agent 层——工具调用 × 执行环境
    predict(tool: Tool, params: any): ToolPrediction;
    update(observation: ToolResult): void;
  };
}

// 生成模型的输出是一个预测分布（不是单点）
interface OutcomePrediction {
  expectedQuality: number;       // 期望质量 0-1
  confidence: number;            // 置信度
  expectedTokens: number;        // 预期成本
  expectedTime: number;          // 预期耗时
  similarPastCases: CaseRef[];   // 相似历史案例
}
```

#### 第二层：通政司三镜 → 精度加权感知（Precision-Weighted Perception）

当前三镜独立分析三个维度（格物/析理/合验），然后出三体权重。Active Inference 的精度加权机制要求：

- **每个维度有一个精度值（precision）**，表示该维度在当前任务中的可靠度
- 高精度维度主导感知更新，低精度维度被抑制

```typescript
interface PrecisionWeightedThreeMirrors {
  // 三镜各自输出：判断 + 精度
  mirror1: { verdict: 'content'|'framework'|'research'; precision: number };
  mirror2: { verdict: 'end-user'|'ai-reprocessing'|'collaboration'; precision: number };
  mirror3: { verdict: 'personalized'|'generic'|'academic'; precision: number };
  
  // 精度加权融合——不是平等投票
  // 精度高的镜子权重更大
}
```

实现上：通政司输出三镜结论时，附加一个**置信度评分**。历史上总出错的那面镜子，精度自动降低。

```typescript
// 格物镜连续 5 次判断错误 → 精度从 0.9 降到 0.3
// 下次它的意见分量自动变小
// ——等价于 Bayesian 更新
function updatePrecision(mirrorId: string, wasCorrect: boolean) {
  precision[mirrorId] = bayesianUpdate(precision[mirrorId], wasCorrect);
}
```

#### 第三层：Fable-5 行为路由 → 策略选择（Policy Selection）

当前 Fable-5 路由是**确定性映射**（三体权重 → IF-ELSE → 行为模式）。Active Inference 要求在策略空间中做概率采样：

```typescript
// 当前
function selectMode(weights: ThreeBodyWeights): BehaviorMode {
  if (weights.sun > 0.8) return 'direct';
  if (weights.sun > 0.6 && weights.moon > 0.5) return 'research';
  // ...if-else 链
}

// Active Inference 版
function selectModeWithActiveInference(
  model: GenerativeModel, 
  task: Task
): { mode: BehaviorMode; expectedError: number } {
  const modes = ['engineer', 'researcher', 'writer', 'auditor', 'auto'];
  
  // 对每种模式在生成模型中 rollout
  const predictions = modes.map(mode => ({
    mode,
    prediction: model.strategic.predict(task, modeToRoute(mode))
  }));
  
  // 选期望自由能最低的模式
  // 自由能 = 预测误差 × 成本 + 信息增益奖励
  const scored = predictions.map(p => ({
    ...p,
    freeEnergy: 
      (1 - p.prediction.expectedQuality) * p.prediction.expectedTokens  // 误差成本
      - model.strategic.informationGain(task, p.mode)                   // 探索奖励
  }));
  
  return scored.sort((a, b) => a.freeEnergy - b.freeEnergy)[0];
}
```

**探索 vs 利用：** 当前 ETO 零探索——永远走确定性的路由。Active Inference 在自由能公式中加入**信息增益奖励**，让系统偶尔尝试没走过的路由，即使短期可能不是最优。即「乱纪元」的数学定义：当所有已知路径的期望误差都高时，系统自动进入探索模式。

#### 第四层：集体回顾 → 变分推断（Variational Inference）

当前集体回顾是**固定周期的质量检查**。Active Inference 把它变成**持续的模型校准**：

```
每 N 轮，或在检测到高预测误差时触发：
  ① 收集近期的 predictionError 序列
  ② 计算生成模型的证据下界（ELBO）
  ③ 如果 ELBO 持续下降 → 模型需要更新
  ④ 更新策略：调整三镜精度 / 调整行为路由权重 / 调整先验
  ⑤ 长期不用的「记忆」自动衰减（避免模型膨胀）
```

#### 第五层：智子 → 先验（Prior）

当前智子是**事后纠察**——Agent 执行完了它才检查越界。Active Inference 给它一个更根本的角色：

**智子不是警察，是先天假设。**

```typescript
interface QSHPrior {
  // 硬约束（不可违背）
  hardRules: Rule[];
  
  // 软先验（可被证据推翻）
  softPriors: {
    'type.document': { prefers: 'writer'; strength: 0.3 };
    'type.build':   { prefers: 'engineer'; strength: 0.7 };
    // strength 越高，需要越强的证据才能推翻
  };
  
  // 更新：当证据充分时，软先验可以被集体回顾调整
  updateSoftPrior(domain: string, evidence: Evidence[]): void;
}
```

硬规则不可学习，软先验可以被证据更新——这就是青色组织里「智子变成顾问」的数学表达。

### 接入路线图

```
Phase 1 —— 插桩（下周末就能干）
  TealContext 加 predictionError 追踪
  通政司输出加 confidence 评分
  集体回顾改查误差序列

Phase 2 —— 概率化（2-3 周）
  三体权重从标量升级为分布（均值 + 精度）
  路由从确定性改为概率采样
  Fable-5 行为选择走自由能最小化

Phase 3 —— 学习闭环（1-2 月）
  智子规则部分软先验化
  系统从执行历史自动调整路由权重
  乱纪元自动触发探索模式
```

---

## 2. World Model / JEPA → ⭐⭐ 次高优先级

### 核心机制：为什么是 latent space？

标准 LLM 范式在**输出空间**做预测——直接预测下一个 token、下一段代码、下一段 markdown。问题是输出空间太大了（数万个 token 的词汇表 × 数万步的序列），绝大多数预测细节是浪费。

JEPA（Joint Embedding Predictive Architecture）在做的事：

```
输入 x → 编码器 → 潜表示 z
                    ↓
          在潜空间预测 z'（轻量、高效）
                    ↓
          解码器 → 投射回输出 y（只在必要时）

潜空间维度 = 64~512 维（远比 token 空间小）
预测内容 = 抽象结构（任务类型、难度、所需能力），不是具体 token
```

### 与 ETO 的深层映射

#### 通政司本质上就是一个编码器

当前通政司把原始任务文本压缩成**三体权重**——这就是一个编码过程。但问题是：

```
当前：编码器（通政司）→ 3 维向量 [☀️, 🌙, ⭐]
      然后用 if-else 解码成路由决策
```

3 维太少了。JEPA 告诉你：**抽象表示空间的维度应该更高（64~256 维），解码器应该更丰富（不是 if-else，而是生成式解码）。**

```typescript
interface JEPA_Tongzhengsi {
  // 编码器：任务文本 → 潜表示
  encode(task: string): LatentVector;  // 输出 128 维向量
  
  // 在潜空间做 rollout（核心）
  rollout(z: LatentVector, nPaths: number): RolloutPath[];
  
  // 解码器：最优潜路径 → 具体路由指令
  decode(path: RolloutPath): RouteInstruction & Fable5Mode;
}
```

#### 层次化潜空间：三层抽象映射 ETO 三层

ETO 天然有三层粒度，JEPA 要求在每层维护独立的潜空间：

```
L3 战略层（通政司）
  潜空间内容：任务类型、复杂度、领域、预期成本
  预测内容：应该走 pipeline 还是 direct？什么 MODE？
  更新信号：路由准确率、用户满意度

       ↓ 战略决策约束战术空间

L2 战术层（Fable-5 行为路由）
  潜空间内容：行为模式偏好、工具组合、自主度
  预测内容：应该用什么身份框架？带什么工具描述？
  更新信号：工具调用成功率、任务完成质量

       ↓ 战术决策约束操作空间

L1 操作层（Agent 工具链）
  潜空间内容：每一步该用什么工具、什么参数
  预测内容：下一步 bash 还是 write？先读还是先写？
  更新信号：工具执行结果、错误率
```

**每层的预测误差反馈给上一层**——Agent 工具调用失败，不仅仅是操作层更新，还会反传信号到战术层（「这个场景不该用这个行为模式」），再到战略层（「这类任务不该走这个 MODE」）。

这就是 ETO 从「单层审核链」进化为「多层预测误差反传」的关键。

#### 潜空间 rollout vs 实际执行

这是 JEPA 对 ETO 最直接的价值——**在潜空间模拟多种方案，不在 token 空间执行。**

```
实际执行：
  Agent 真的调工具 → 真的写文件 → 真的花时间 + 花 token

潜空间 rollout（通政司在派发前做的）：
  在 128 维潜空间里用轻量预测器模拟
  「派兵部 + 工程师模式 → 预期质量 0.85，成本 2000 tokens」
  「派礼部 + 写作模式 → 预期质量 0.72，成本 500 tokens」
  比较后选最优
```

**rollout 的预测器不是 LLM**，而是一个轻量模型（线性回归 / 小 MLP / 查表），基于历史执行数据训练。成本 = 一次矩阵乘法 ≈ $0.000001，不是一次 LLM 调用 ≈ $0.001。

```typescript
// 潜空间预测器（轻量）
class LatentRolloutPredictor {
  // 输入：潜向量 + 路由方案
  // 输出：预期质量 + 预期成本
  predict(z: LatentVector, route: Route): { quality: number; cost: number } {
    // 简单的 MLP，~50K 参数
    // 训练数据：历史执行记录的潜向量 → 实际结果
    return this.mlp.forward(concat(z, route.encode()));
  }
  
  // 多个方案并行 rollout
  batchRollout(z: LatentVector, routes: Route[]): RouteScore[] {
    return routes.map(r => ({
      route: r,
      score: this.predict(z, r)
    }));
  }
}
```

### 世界模型的学习闭环

```
第 1 次请求：
  通政司编码任务 → 潜向量 z₁
  rollout 3 种方案 → 选 A（派兵部）
  实际执行质量 0.4（差）
  存储：z₁ + 方案A + 实际结果 0.4

第 5 次请求（同类任务，z₁ ≈ z₅）：
  预测器看到 z₅ 附近的历史：
    z₁→A=0.4,  z₂→A=0.35,  z₃→B=0.85,  z₄→B=0.9
  自动选 B（派礼部）——不要人写规则
  
第 10 次请求（又一个类 z 向量）：
  通政司不需要重新编码和理解任务
  直接在潜空间匹配最相似的历史 → 复用成功方案
```

这就是**通政司自己学到经验**，而不需要靠别人的反馈或修改代码。

### 当前 ETO 的先天 JEPA 基因

ETO 其实已经具备 JEPA 的基本骨架：

| ETO 组件 | JEPA 对应 | 差距 |
|:---------|:----------|:-----|
| 三体权重 [☀️, 🌙, ⭐] | 潜空间（但只有 3 维） | 需要扩到 64+ 维 |
| 通政司三镜分析 | 编码器（任务 → 抽象） | 输出是文本不是向量 |
| 路由决策 | 潜空间规划 | 一次决策不 rollout |
| 集体回顾 | 生成模型更新 | 不是持续在线更新的 |
| 各部执行 | 解码器 → 具体行动 | 不变 |

### 接入路线图

```
Phase 1 —— 增加潜空间维度
  三体权重从 [☀️, 🌙, ⭐] 扩到 [☀️, 🌙, ⭐, domain, complexity, ...]
  通政司输出结构化向量而非三体三值

Phase 2 —— 轻量预测器
  基于历史执行数据训练一个小 MLP
  每次路由前做潜空间 rollout 验证

Phase 3 —— 层次化
  拆成三层潜空间，各层维护独立的预测器
  下层误差向上层反传
```

---

## 3. World Model + Active Inference → 合并为 ETO 的青色引擎

这两个范式不是二选一——**它们是互补的：**

| | Active Inference | World Model / JEPA |
|:--|:----------------|:-------------------|
| 负责什么 | 学习的动力来源 | 学习的载体 |
| 提供什么 | 误差信号、更新规则 | 潜空间结构、预测器 |
| 形式 | `自由能 = 预测误差 + 探索奖励` | `潜向量 → rollout → 解码` |

**合并后的 ETO 核心循环：**

```typescript
function etoCoreLoop(task: Task) {
  // 1. 编码（World Model）
  const z = encoder.encode(task);        // 任务 → 128 维潜向量
  
  // 2. 在潜空间 rollout（World Model）
  const routes = generateCandidateRoutes(z);
  const predictions = latentRollout.predict(z, routes);
  
  // 3. 选自由能最低的（Active Inference）
  const selected = minFreeEnergy(predictions);
  
  // 4. 执行
  const outcome = executeRoute(selected);
  
  // 5. 计算预测误差（Active Inference）
  const error = computePredictionError(selected.prediction, outcome);
  
  // 6. 更新生成模型（两路并行）
  encoder.update(task, outcome);          // 改进编码
  latentRollout.train(z, selected, outcome); // 改进预测器
  
  // 7. 更新精度（Active Inference）
  updatePrecisionWeights(error);
}
```

---

## 4. 液态神经网络 → 有趣但遥远

（内容不变，保持简短）

### 核心机制

用 ODE（微分方程）替代固定权重层，神经元拥有「时间常数」，天生处理连续时序而不是离散步长。

### 与 ETO 的关系

当前 ETO 是**离散状态机**——通政司、各部、智子之间是明确的状态转换。液态网络给出的启示是：

> **三体周期（稳定纪/恒纪元/乱纪元/广播纪元）不应该用 if-else 判断，而应该是一个连续动态系统的自然轨迹。**

即：不是写死「理体>0.8 走 direct」，而是让通政司的决策本身是一个 ODE 系统的吸引子——系统自然收敛到某个路由方案。

**难度：极高。先不用。**

---

## 5. 超维计算 → 有趣的小工具

（内容不变，保持简短）

### 核心机制

用极高维向量（10000 bits）做符号操作。关键操作：
- **绑定**（Bind）：向量 A ⊕ 向量 B = 新向量
- **叠加**（Bundle）：向量 A + 向量 B = 模糊联合
- **旋转**（Permute）：时序关系

### 与 ETO 的关系

ETO 的三体权重 `[0.7, 0.2, 0.1]` 已经是一个三维修超维向量了。超维计算的 insight 是：

> Agent 的行为模板可以通过向量代数组合，而不是字符串拼接。

```
行为模式 = 
  identity(fable5) 
  ⊕ autonomy_strategy(high)     // 绑定
  ⊗ tool_pref(bash)             // 叠加
  ⊕ communication_style(terse)  // 绑定
```

**接入点：** 可以作为 Fable-5 行为路由的底层索引方案——用向量运算代替关键词匹配。

---

## 6. Neuro-Symbolic → 已经在用了

（内容不变，保持简短）

### 核心机制

神经网络做感知 → 投影到符号空间 → 符号推理引擎 → 降回网络输出。

### ETO 本身就是 Neuro-Symbolic

| 层 | 类型 | 说明 |
|:---|:-----|:------|
| Agent | 神经（neural） | LLM 做感知、理解、生成 |
| 智子 | 符号（symbolic） | 硬编码规则、越界检测、熔断 |
| 路由表 | 符号（symbolic） | 关键词匹配、权重阈值 |
| 通政司三镜 | 混合 | 三镜由 LLM 判断（神经），但走结构化输出（符号） |

### 可以被 ETO 吸收的

当前 ETO 的符号层（智子规则、路由表）是**静态的**——规则由开发者写死。Neuro-Symbolic 的前沿在让符号层**可微分**，即路由规则能从执行历史中自动学习。

这正是 ETO 从琥珀色到青色的关键一步——**不靠人写审核链，靠系统从历史中学出审核策略。**

---

## 总结：优先级路线图

| 范式 | 对 ETO 的价值 | 实现难度 | 优先级 | Phase |
|:-----|:-------------|:---------|:------|:------|
| **Active Inference** | 重构失败 → 学习闭环，青色化引擎 | 中 | ⭐⭐⭐ | Phase 1 下周可开始 |
| **World Model / JEPA** | 潜空间 rollout 省 100× 成本 | 中 | ⭐⭐ | Phase 1-2 并行 |
| **Neuro-Symbolic** | 智子规则可学习 | 高 | ⭐ | Phase 3 |
| **液态网络** | 三体周期连续化 | 极高 | 💡 | 远期 |
| **超维计算** | 行为模板向量索引 | 低 | 💡 | 远期 |

### 快速收益（Phase 1，下周就能干）

1. 通政司输出加 **confidence 评分** —— 当前完全没做
2. TealContext 加 **predictionError 追踪表** —— 纯数据结构
3. 三体权重从 3 维扩到 **6 维** —— 加 domain、complexity、urgency

这三个改动不需要新模型、不需要训练，就是改数据结构 + 加几行代码。
