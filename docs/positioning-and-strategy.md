---
type: strategy
tags: [positioning, landscape, enforcer, three-body, qinshihuang]
timestamp: 2026-06-19
---

# ETO 竞品定位与战略蓝图

> 不是又一个 AI Agent，是一种组织 AI Agent 的制度。

---

## 1. CLI AI Agent 主流阵营全景

### 八位主力

| Agent | 定位 | 编成质量 | 模型自由 | 生态 | 成本控制 | 门槛 | 安全性 | 亮点 | 致命短板 |
|:------|:-----|:--------|:--------|:-----|:--------|:-----|:------|:-----|:--------|
| **Claude Code** 🏆 | 性能天花板 | ⭐⭐⭐⭐⭐ | ❌ | ✅✅ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 长上下文200K不降质，子Agent编排 | 封闭生态，月费无预测性，三连bug |
| **Codex CLI** 🛡️ | 安全标兵 | ⭐⭐⭐ | ❌ | ✅ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Rust原生OS沙箱，Goals系统 | OpenAI锁死，可靠性飘忽(6/10) |
| **Goose** 🦆 | 开放全栈 | ⭐⭐⭐ | ✅✅ | ✅✅ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Linux Foundation托管15+提供商 | 编码质量一般，非编码专用 |
| **Aider** 📜 | Git原教旨 | ⭐⭐⭐⭐ | ✅✅ | ❌ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 自动commit，架构师/编辑双模型 | 无MCP/浏览器/GUI，手动上下文 |
| **Cline** 🦎 | 全能覆盖率 | ⭐⭐⭐⭐ | ✅✅ | ✅✅ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Plan/Act双模式，浏览器自动化 | 冗余啰嗦高token，Roo Code fork已死 |
| **OpenHands** 💻 | 自托管自主 | ⭐⭐⭐⭐ | ✅✅ | ✅ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Docker沙箱，SWE-bench 72-77% | Docker依赖，无MCP，设置复杂 |
| **Pi (pi-mono)** 🫗 | 极简基座 | ⭐⭐⭐ | ✅✅ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | <1K token系统提示，Tree会话可分支 | 无权限系统，无MCP，无审核链 |
| **OMP (oh-my-pi)** ⚡ | 最全工具集 | ⭐⭐⭐⭐ | ✅✅✅ | ✅✅ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Hashline编辑，LSP/DAP，32工具 | Fork上游合并风险，升级不光滑 |

### 八位选手的共同盲区

所有主流工具都在**「单 Agent 问-答-做」范式**内——它们的差异是**同一个维度的不同刻度**（谁更准、谁更快、谁更安全）。

| 共性 | 表现 | ETO 的反向 |
|:----|:-----|:-----------|
| **单体架构** | 一个 LLM 会话干所有事 | **多 Agent 管道** — 每站有专精角色 |
| **线性执行** | prompt→exec→done，不回头 | **REWORK 一等公民** — 审计打回自动重做 |
| **无文化身份** | 工具感强，全是接口 | **组织隐喻** — 三省六部/三体/大英公务员 |
| **单一模式** | 不管什么任务，同一套交互 | **4 种管道拓扑** — research/build/debate/full |
| **无反馈回路** | 输出即终点 | **审核链** — 一审二审刑部三关 |
| **无形式化交接** | 模型自己决定下一步 | **VERDICT/FEEDBACK 协议** — 节点间有契约 |
| **规则内置** | 规则写在代码里 | **智子独立规则引擎** — 规则在外不在内 |

Pi 和 OMP 的血缘关系像 **Debian 与 Ubuntu**——一个极简纯净，一个开箱即用。但**它们都是单 Agent 范式**，与 ETO 的多 Agent 管道不在同一赛道。

---

## 2. ETO 的独特生态位

> **别人做「更聪明的 Agent」，ETO 做「更聪明的一组 Agent 怎么协作」。**

### 扬什么长（空白市场）

**① 多 Agent 管道编排器，不是又一个编码 Agent**
- 所有主流工具在抢「单个 Agent 能干多少事」
- ETO 回答「怎么让多个专精 Agent 协作」
- Claude Code 虽也有子 Agent，但那是**单体套娃**（一个 Claude 拆子 Claude），不是异构管道

**② 组织制度，不是聊天界面**
- Agent 行为由**它在组织中的职位**决定，不是靠 prompt 临时指定
- 礼部是内容科、兵部是研发科——身份即职责，职责即工具
- 组织制度经过了 1400 年验证（三省六部历史）

**③ 审核链 + REWORK 作为核心架构**
- 主流工具输出一次性——错了用户手动改
- ETO 的审核链是**自动的**，打回自动重做
- 连续 2 轮 rework → 降级 redesign，同一问题 3 次 → 建议人工介入

**④ 四种 Loop 作为一等公民**
- Rework / Iteration / Watch / Cron
- 市面 Agent 无循环存储，ETO 有 `LoopContext` 接口
- Loop 不靠打补丁，是架构原生

### 避什么短（不跟风）

- **不做单 Agent 性能竞赛** — Claude Code 87.6% SWE-bench 是它的赛道，ETO 不追
- **不做 IDE 内嵌** — Cursor/Cline 已在抢这市场，ETO 打的是管道编排层
- **不做模型锁定** — TRSS 设计为 `$TRSS_LLM_CMD` 可配置
- **不做通用化** — ETO 是组织架构，不是通用聊天工具

### 发展什么特点（差异化卖点）

| 特点 | 说明 | 竞品对标 |
|:-----|:------|:--------|
| **文化记忆点** | 三省六部/三体/大英公务员——名字即故事 | Claude Code 是工具名，ETO 是世界观 |
| **Loop 一等公民** | 四种循环架构原生，非补丁 | 竞品无此概念 |
| **多模拓扑** | 同一管道走 4 种模式，direct→full 成本自适应 | 竞品模式单一 |
| **进化路径** | Amber → Orange O1-O5 组织演进 | 竞品是版本号升级，不是范式转换 |
| **智子规则引擎** | 独立于 Agent 的规则/权限/审计层 | 竞品规则内置在代码中 |
| **讽刺镜像 YMM** | 同一架构做正反两事——证明架构通用性 | 独有 |

---

## 3. 👑 智子：独立规则引擎层

### 三体世界观映射

秦始皇在《三体》人列计算机中指挥三十万士兵当逻辑门——映射到 ETO：

| 三体意象 | ETO 对应 |
|:---------|:---------|
| 三十万士兵当逻辑门 | 每个 Agent 的工具调用是逻辑单元 |
| 秦始皇站在高台指挥 | Enforcer 在三钩子监视（pre_llm/pre_tool/transform） |
| 统一指令体系 | 规则统一所有 Agent 行为 |
| 书同文车同轨 | 输出转换规则统一格式 |
| 不在计算中，而在计算之上 | 不在 pipeline 中，在 pipeline 之上 |

### 组织位置

```
            👑 智子（Enforcer）
        统一六国·书同文车同轨
       ┌─────────┼─────────┐
   秘书处     三总       六科
  (通政司)  (方案/审核/质控/审计)  (内容/研发/工程/数据/人事/情报)
```

### 技术对应现状

| 三体意象 | 技术实现 | 状态 |
|:---------|:---------|:-----|
| 统一六国 | 20 条规则覆盖所有行为场景 | ✅ 运行中 |
| 书同文 | `transform_llm_output` 输出转换 | ✅ 运行中 |
| 车同轨 | 路由表 12 板块统一调度 | ✅ 运行中 |
| 人列计算机 | pre_tool_call 钩子拦截/放行 | ✅ 运行中 |
| 律法在前 | 高优先级规则优先审查 | ✅ 运行中 |
| 商鞅变法 | 规则 YAML 热重载 | ✅ 运行中 |
| 焚书坑儒 | 静默禁用不符合规范的输出 | ⏳ 可加强 |

### 智子 CLI（设计目标）

核心设计哲学：**先找 peer，没有就开配置不同的 sub。**

#### Agent 调用优先级

```
qsh call 一个 Agent 干活时，按这个顺序找：
  
  ① 🥇 Peer Agent（外置）
     系统中已注册的独立 Agent
     例：claude-code / reasonix / openhands / gpt
     → qsh call claude-code "帮我重构"
  
  ② 🥇 如果①没有 → 开配置不同的 Sub Agent（内置）
     同一个 Agent runtime，但配置不同
     例：编码 sub vs 研究 sub vs 审计 sub
     各自有不同的 system prompt、工具集、模型
     
  ③ ❌ 不做的：配置相同的子进程克隆
     ——其他工具的做法，ETO 不做
```

#### 配置不同的 Sub Agent 示例

```yaml
# qsh config.yaml
agents:
  # Peer Agent（外置，通过 CLI 调用）
  claude-code:
    type: peer
    command: "npx claude"
    model: "claude-sonnet-4"
    
  reasonix:
    type: peer  
    command: "reasonix run"
    model: "deepseek-v4"

  # 配置不同的 Sub Agent（内置，同一 runtime）
  # 分工不同：不同的系统提示、工具集、模型
  researcher:
    type: sub
    system_prompt: "你是一个研究助手，擅长文献检索、数据分析、交叉验证。"
    allowed_tools: [web_search, web_extract, read_file, write_file]
    model: "gemini-2.5-pro"       # 研究用 Gemini
    
  engineer:
    type: sub
    system_prompt: "你是一个资深工程师，擅长代码开发、重构、调试。"
    allowed_tools: [terminal, read_file, write_file, patch]
    model: "claude-sonnet-4"      # 编码用 Claude
    
  auditor:
    type: sub
    system_prompt: "你是一个安全审计员，严格检查每个环节。"
    allowed_tools: [read_file, search_files]
    model: "gpt-4.1"              # 审计用 GPT
    
  planner:
    type: sub
    system_prompt: "你是一个方案设计师，擅长架构规划和任务拆解。"
    allowed_tools: [read_file, write_file]
    model: "claude-opus-4"        # 方案用 Opus
```

#### 命令设计

```
qsh call <agent> <task>              # 调用 Agent（自动按优先级找）
qsh call --peer claude-code <task>   # 强制用 peer
qsh call --sub engineer <task>       # 强制用配置 sub
qsh pipeline <task>                  # 多 Agent Pipeline（自动编排）
qsh watch <pipeline-id>              # 监控运行
qsh stop <pipeline-id>               # 强制停止

# 示例
qsh call --peer claude-code "重构函数"        # → 直接调 Claude Code
qsh call --sub engineer "写个 API 路由"       # → 开配置好的编码 sub
qsh pipeline "写一个 CLI 工具"                # → 自动编排：planner→engineer→auditor
```

#### 一个任务三种走法对比

```
其他工具：
  master Claude → sub Claude (克隆)  → 同质，同一模型，同一工具集
                  sub Claude (克隆)
                  sub Claude (克隆)

ETO 最佳（有 peer）：
  qsh call claude-code "写代码"      → 真正的 Claude Code，完整工具集
  qsh call reasonix "做研究"         → 真正的 Reasonix，web + 分析
  qsh call terminal "部署"           → 原生终端

ETO 次优（无 peer，走配置 sub）：
  qsh call --sub planner "出方案"     → 用 Opus，只读文件
  qsh call --sub engineer "实现"      → 用 Sonnet，可调 terminal
  qsh call --sub auditor "审查"       → 用 GPT，只读
```

#### 为什么这个架构好

| 场景 | 走 peer | 走配置 sub |
|:-----|:--------|:-----------|
| 系统中已装 Claude Code | ✅ 直接调用，完整能力 | — |
| 系统中已装 Reasonix | ✅ 直接调用 | — |
| 系统只有这个 Agent 一个 runtime | — | ✅ 开 3 个不同配置的 sub，分工协作 |
| 需要控制的 token 成本 | ❌ 外部进程不可控 | ✅ sub 有预算帽（智子控制） |
| 需要隔离的工具集 | ❌ 外部进程自带全部工具 | ✅ sub 只能访问允许的工具 |
| 生产环境稳定性 | ✅ 独立进程，一个挂不影响其他 | ✅ 受智子监控，可自动重启 |

#### 智子作为编排中心

```
qsh 的完整架构：

         ┌────────── qsh ──────────┐
         │    智子编排/规则/审计    │
         │                         │
    ┌────┴────┐           ┌────────┴────────┐
    │ Peer 层  │           │  Configured Sub  │
    │ 外置 Agent│           │  内置配置差异 Sub  │
    ├──────────┤           ├─────────────────┤
    │ claude-code│          │ planner (Opus)    │
    │ reasonix  │          │ engineer (Sonnet) │
    │ openhands │          │ researcher (Gemini)│
    │ terminal  │          │ auditor (GPT)     │
    └──────────┘           └─────────────────┘
    
    所有调用过智子：规则检查 → 权限检查 → 预算检查 → 放行
```

### 从历史陷阱到 CLI 方案

| 历史陷阱 | 根因 | 智子 CLI 方案 |
|:---------|:-----|:---------------|
| Pipeline 不能中途停（P37） | AgentFlow 并行 STOP 信号不可靠 | `qsh stop` → SIGTERM 整个进程树 |
| LLM 输出格式不可控（P30/32/33） | markdown 污染 KEY=VALUE 提取 | 后处理钩子，正则校验再放行 |
| 跨会话状态靠 /tmp 文件 | 重启即丢失 | 状态注册表 `~/.qsh/state/` 持久化 |
| MCP 噪音污染产出（P31） | agentmemory 探针混入 | 输出过滤器自动剥离 |
| 节点权限无差别 | 礼部也能调 terminal | `qsh permit --role=礼部 --allow=reasonix` |
| 成本无法按阶段控制 | 循环烧完才发现 | `qsh budget --cap=$0.05` |
| Agent 死循环无检测（P24/25） | rework 3 次才人工介入 | 看门狗自动打断同输出循环 |
| 规则版本依赖 git | 改了就改，无追溯 | `qsh rollback <rule> <v>` |

---

## 4. ☀️🌙⭐ 三体决策引力模型

### 三体 = 三个分析引力源

三体问题是三个天体互相拉扯——映射到 ETO 的决策分析，每个问题都有三个引力源：

| 体 | 本质 | 问的问题 | 高权重走 |
|:--|:-----|:---------|:--------|
| ☀️ **太阳（理体）** | **逻辑** — 推理链、约束、因果 | 这事成立吗？推导严密吗？ | 审查重、REWORK 多 |
| 🌙 **太阴（实体）** | **事实** — 数据、证据、可验证 | 证据在哪？数据支持吗？ | 调研重、司天监全开 |
| ⭐ **太白（得体）** | **品味** — 审美、文化、语境 | 这事合适吗？有辨识度吗？ | 礼部重、刑部把关 |

### 权重 → MODE 映射

```
权重分布             →  MODE
────────────────────────────────────────
☀️ 高 + 🌙 高       →  research（调研报告）
🌙 高 + ⭐ 高       →  debate（决策评估）
⭐ 高 + ☀️ 高       →  build（方案设计）
☀️🌙⭐ 全高         →  full（全节点）
某一极高（>0.8）     →  direct（快速通道）
☀️🌙⭐ 互相拉扯     →  full + rework（乱纪元校准）
```

### 三体周期 vs Pipeline 状态

| 周期 | 三体状态 | Pipeline 行为 |
|:-----|:---------|:--------------|
| **稳定纪** 🌤️ | 一个引力明显主导 | direct 通道，低成本快速产出 |
| **恒纪元** ☀️🌙⭐ | 三体和谐 | 标准 mode 执行 |
| **乱纪元** 🌪️ | 三体拉扯不可预测 | full pipeline + rework 循环校准 |
| **广播纪元** 📡 | 需要第三方视角 | 引入 YMM 讽刺镜像审查 |

### 与通政司三镜的关系

```
通政司接旨
  → 三镜分拣（格物/析理/合验）→ 确定任务类型
  → 三体赋权（理体/实体/得体权重）→ 确定各维度权重
  → 根据权重映射 MODE → 走对应 Pipeline
```

三镜是**任务分拣工具**，三体是**决策引力模型**。三镜更浅、三体更深。两者叠加使用。

### 三体世界观命名彩蛋

| 概念 | ETO 对应 | 技术实现 |
|:-----|:---------|:---------|
| **智子** | 规则引擎 + 路由表 | 无处不在的规则监控 |
| **二向箔** | `transform_llm_output` | 降维成标准格式 |
| **曲率驱动** | subagent 并行调度 | 超光速执行 |
| **黑暗森林** | `stop-command` | 暴露即打击 |
| **人列计算机** | Pipeline 节点链 | 并行逻辑门阵列 |

---

## 5. ETO 完整架构图

```
                 👑 智子（Enforcer）
              ⚖️ 规则/权限/审计/转换
              统一六国·书同文车同轨
                     │
         ┌───────────┼───────────┐
         │           │           │
      秘书处      三总体系     六科执行
    (通政司)   ┌──┴──┐    ┌──┼──┼──┼──┼──┐
    三镜分拣  方案  审核 内容 研发 工程 数据 人事 情报
    三体赋权  质控  审计
         │           │
         └───────────┴──Loop 系统──┐
                    │              │
                Rework        四种 Loop
                Iteration    (type/maxRounds/currentRound/
                Watch        previousOutput/previousAudit/
                Cron         artifacts)
                     │
                     ▼
             ☀️🌙⭐ 三体决策
             理体/实体/得体
              权重 → MODE
                     │
            ┌────────┼────────┐
            ▼        ▼        ▼
        research   build    debate    full
           /        /        /        /
          ▼        ▼        ▼        ▼
         YMM 讽刺镜像（可选审查）
```

---

## 6. TRSS 与 YMM 的定位更新

### 🏛️ TRSS（three-line-pipeline / 三总六科）
- **定位：** ETO 的标准实现——正版三省六部
- **血统：** 三省六部（唐代）→ 三总六科（现代企业）→ TRSS（GitHub）
- **核心价值：** 16 节点审核链 + 4 种模式 + Rework 循环
- **基座：** 当前基于 AgentFlow，未来可基于 Pi Extension

### 🫖 YMM（yes-my-mister / 大英公务员）
- **定位：** ETO 的讽刺镜像——证明架构通用性
- **血统：** Sir Humphrey 官腔 → 低效推诿管线
- **核心价值：** 同一骨架、相反设计目标 = 架构可塑性证明
- **现状：** 731 行 TypeScript CLI，5 命令（ymm / blame / committee / progress / compare）

### 两者关系

> TRSS 是「最理想的上班状态」，YMM 是「最真实的上班状态」。
> 两者共享同一套 pipeline 骨架，证明了 ETO 架构的设计不是特化解决方案——它能支撑相反的价值观。

---

## 7. 接下来的方向

### 短期（可立即开工）
- **更新 ETO README** — 加入智子 + 三体 + 完整架构图
- **补 links** — ETO → TRSS/YMM 的家庭树
- **定型三体权重** — 可以开几个真实任务跑一下权重分配

### 中期
- **智子 CLI 原型** — `qsh` 最小可行版本（rule list + audit + stop）
- **三体决策工具** — 输入任务走三体赋权 → 自动推荐 MODE
- **Watch Loop 实现** — 第一个真正的原生 Loop

### 远期
- **智子 + TRSS 组合部署** — Pi Extension 管道 + 独立规则引擎
- **ETO 作为开源项目** — 不是编码 Agent，是多 Agent 编排框架

---

---

## 8. 🔄 Dynamic Workflows — ETO 的实现引擎

### 核心定位重述

> **ETO 不是 Dynamic Workflows 的竞品。**
> **ETO = Dynamic Workflows（引擎） + 青色组织架构（设计） + 智子（治理）。**

Dynamic Workflows 提供了多 Agent 编排的**运行时层**——JS 脚本编排、subagent 并行、上下文隔离、结果校验。它解决的是「怎么让 N 个 Agent 一起干活」的工程问题。

ETO 回答的是**「这 N 个 Agent 以青色组织的原则——自主管理、完整性、进化使命——来协作」的组织问题。**

### 什么是青色组织

Frédéric Laloux 在《Reinventing Organizations》中定义了组织进化的五个阶段。ETO 的目标是**第四个阶段——青色**：

| 颜色 | 范式 | 核心特征 | AI Agent 对应 |
|:-----|:-----|:---------|:--------------|
| 🔴 冲动红 | 狼群 | 首领绝对权力 | 单 Agent 裸跑，无规则 |
| 🟤 琥珀色 | 军队/教会 | 层级分明、流程固化 | **三省六部/TRSS**（当前实现） |
| 🟠 橙色 | 机器 | 目标管理、创新竞赛 | 精英制 + 绩效调度（O1-O5） |
| 🟢 绿色 | 家庭 | 共识驱动、价值观导向 | 三体权重由共识决定 |
| **🦋 青色** | **生命系统** | **自主管理·完整性·进化使命** | **Agent 设计自己的 Pipeline** |

> 三省六部（TRSS）是 ETO 的 **琥珀色实现**——它有用，但不是终点。
> ETO 的愿景是用 Dynamic Workflows 模拟**青色组织**，让 Agent 像生命系统一样自我组织。

### 青色三原则 × Agent 编排

| 青色原则 | 含义 | ETO + DW 实现 |
|:---------|:-----|:--------------|
| **自主管理** | 没有固定层级，没有 master/sub-agent，所有 Agent 是 peer | subagent 根据能力自主领取任务、自主调用其他 Agent——而不是被上级分配 |
| **完整性** | Agent 可以发挥全部能力，不局限于预设角色 | Agent 之间可互为 peer——研究 Agent 觉得需要代码验证，直接 call Claude Code，不需要经过调度器 |
| **进化使命** | 系统有自己的方向，持续适应环境 | Pipeline 拓扑由三体权重动态生成，Agent 自主决定下一个 call 谁，不再有固定的 16 节点结构 |

### 分层架构

```
青色组织架构（ETO 设计哲学）
  自主管理 / 完整性 / 进化使命 / 三体决策
  ─────────────────────────────────────────────────
  智子（治理层）
  规则引擎 / 权限控制 / 审计日志 / 输出转换 / 预算帽
  ─────────────────────────────────────────────────
  Dynamic Workflows 运行时
  JS 编排脚本 / subagent 并行调度 / 上下文隔离 / 结果校验
  ─────────────────────────────────────────────────
  Agent 层
  Claude / GPT / Gemini / reasoning / terminal 等
```

### 青色 vs 非青色：同一引擎，不同组织制度

```
琥珀色（三省六部/TRSS）在 DW 上：
  ┌─固定的 16 节点 pipeline
  │  通政司→中书省→一审→礼部→兵部→…→刑部→早朝官
  │  每站有固定职责，不允许跨站
  │  审核链是硬编码的
  └─ 可靠但僵化

青色（ETO 终极形态）在 DW 上：
  ┌─动态生成的 pipeline
  │  subagent 自主认领阶段
  │  需要更多调研 → 🌙 实体权重自动升 → 更多调研 subagent
  │  需要更严格审核 → ☀️ 理体权重自动升 → 对抗式 subagent 加入
  │  pipeline 拓扑每轮不一样
  └─ 自适应且自进化
```

### 青色原则的 DW 实现方式

| 青色原则 | 当前（琥珀色） | 目标（青色） |
|:---------|:--------------|:------------|
| **自主管理** | 六科各配固定武器 | subagent 运行时自选工具 |
| **完整性** | 礼部只能写文档 | 任何 subagent 可以调用任何工具，三体权重动态调整 |
| **进化使命** | 16 节点固定 pipeline | Pipeline 由任务特征自动生成，不再预设 |

### 关键判断

> **Dynamic Workflows 是引擎，ETO 是操作系统。**
>
> 别人用 Dynamic Workflows：让更多 Claude 同时干活，更快。
> ETO 用 Dynamic Workflows：让不同身份的 Agent 按组织制度协作，更可靠。
>
> Dynamic Workflows 解决「规模」问题——1000 个 subagent 同时跑不崩。
> ETO 解决「质量 + 规模 + 治理」问题——跑出来的东西能被信任。
>
> 借用三体语言：DW 提供了人列计算机的硬件（30 万士兵），ETO 提供了组织制度（军阶/旗号/号令/奖惩）。没有组织制度，30 万人只是乌合之众；有了它，才是一个能计算三体问题的机器。

### 与其他引擎的关系

ETO 不绑定 DW——它是一个组织设计，可以在不同引擎上实现：

| 引擎 | 现状 | ETO 在上面能做什么 |
|:-----|:-----|:------------------|
| **Dynamic Workflows** 🔥 | ETO 的首选实现引擎 | 三省六部 + 智子 + 三体权重 |
| **Pi Extension** | 已有设计文档（tlp-pi-fork-plan） | TRSS Pipeline as Pi extension |
| **AgentFlow** | ETO 当前实际运行平台 | 三省六部已验证 16 节点全链 |
| **OpenHands** | 远期可能 | 沙箱化自主 Agent 管道 |

### 青色进化路径 × Dynamic Workflows

这是 ETO 真正独特的地方——**DW 只解决效率，ETO 解决组织的进化。**

```
阶段       组织范式           Dynamic Workflows 角色    ETO 增加
───────────────────────────────────────────────────────────────
阶段1 🟤    琥珀色（军队）   固定角色分工执行           审核链 + REWORK
         三省六部/TRSS                              可靠但僵化

阶段2 🟠    橙色（机器）     根据绩效分配 subagent     精英制调度 + 快速通道
         O1-O5 精英制                              灵活但仍被管理

阶段3 🟢    绿色（家庭）     subagent 有投票权        三体权重由共识决定
                                                    智子转变为宪章法官

阶段4 🦋    青色（生命系统）  subagent 自主决策        Pipeline 自设计
                                                    智子转变为顾问
```

每个进化阶段，Dynamic Workflows 的运行时能力不变（引擎），但 ETO 的组织制度在进化。

**最终状态：** 青色组织下的 ETO，Agent 不再走预设 pipeline，而是根据任务特征 + 三体权重 + 历史经验，自主生成最优协作拓扑。智子从「立法者」退化为「宪章守护者」——只拦根本性的越界，不干涉日常运作。

---

## 9. 🧠 记忆系统 — ETO 的长期记忆层

### 四层记忆架构

ETO 的记忆系统基于 **agentmemory**，分为四个层级：

```
记忆层级                  作用                    技术
─────────────────────────────────────────────────────────
🧩 Working (工作记忆)     当前会话中的上下文    agentmemory slots
📖 Episodic (情景记忆)    具体事件与决策记录    agentmemory observations
🧠 Semantic (语义记忆)    知识、概念、模式      gbrain 知识图谱
⚙️  Procedural (程序记忆)  怎么做——技能与规则   skills + enforcer rules
```

### 在 ETO 架构中的位置

```
        👑 智子（规则引擎）
               │
    ┌──────────┼──────────┐
    │          │          │
  Pipeline    记忆系统    输出转换
               │
     ┌─────────┼─────────┐
     │         │         │
  agentmemory  gbrain   NexSandglass
  (事实/决策)  (知识图谱) (状态快照)
```

### 关键设计

| 组件 | 用途 | 技术现状 |
|:-----|:-----|:---------|
| **Slots** | 当前会话关键状态（LoopContext、MODE/TYPE） | ✅ agentmemory slots |
| **Observations** | 自动捕获的对话观察 | ✅ agentmemory hooks |
| **Lessons** | 带有 confidence 分数的经验教训 | ✅ agentmemory lessons |
| **Consolidation** | 4 层记忆自动合并（working→episodic→semantic→procedural） | ✅ agentmemory consolidate |
| **NexSandglass** | 状态快照 + 复盘数据（offset/echo/entropy/stage） | ✅ 离线脚本 |
| **gbrain 知识图谱** | 结构化知识（人物/项目/公司关联） | ✅ 可用 |

### 与竞品对比

| | ETO | Claude Code | Codex CLI | Pi |
|:--|:----|:------------|:----------|:---|
| 持久记忆 | ✅ 4 层 + 图谱 + 教训 | ❌ 仅 CLAUDE.md 静态配置 | ✅ Goals 系统 | ❌ 无 |
| 跨会话状态 | ✅ slots 持久化 | ❌ 每次重新读文件 | ✅ Goals 追踪 | ✅ Tree 会话可恢复 |
| 教训系统 | ✅ confidence 加权 + 自动化巩固 | ❌ 无 | ❌ 无 | ❌ 无 |
| 知识图谱 | ✅ gbrain 实体/关系/探索 | ❌ 无 | ❌ 无 | ❌ 无 |
| 状态快照 | ✅ NexSandglass（entropy/stage 分析） | ❌ 无 | ❌ 无 | ❌ 无 |

### 智子 + 记忆的联动

记忆系统不是独立存在的——它受智子规则引擎保护：

```
qsh rule enforce "记忆必须走 agentmemory"
  → 拦截直接 write_file 的"存档"行为
  → 强制走 agentmemory save
  → 自动学习：记录什么内容常被存，什么话题常被查

qsh audit "记忆访问频率"
  → 显示最常 recall 的记忆
  → 发现记忆空洞（从未被查过的内容）
  → 自动建议清理或加固
```

---

## 附录：竞品 SWE-bench 数据（2026.06）

| 工具 | SWE-bench Verified | 备注 |
|:-----|:-----------------|:-----|
| Claude Code | 87.6% | 断层领先 |
| OpenHands (V1) | ~72.8% | Claude Sonnet 4.5 |
| OpenHands (V0) | ~77.6% | 有争议的旧 harness |
| Codex CLI | 未公开基准 | 不可靠 |
| Cline | 未基准 | Plan/Act 模式 |
| Aider | 未基准 | Polyglot 排行榜测模型而非工具 |
| Pi | 未基准 | 最小核心 |
| OMP | 未基准 | 但 hashline 提升编辑精准度 6-68% |
| **ETO (TRSS)** | **不追此赛道** | ETO 测的是多 Agent 协作效率，非单 Agent 准确率 |

---

*本文档归档于 2026-06-19，对应对话「CLI AI Agent 全景分析 + 秦始皇 + 三体制」*
