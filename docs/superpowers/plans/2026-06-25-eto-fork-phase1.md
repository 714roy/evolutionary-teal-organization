# ETO CLI Fork — Phase 1: 基础重命名 + 核心功能

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 从 pi-mono 分叉出 `eto` CLI，保留核心引擎（pi-ai / pi-agent-core / pi-tui），去掉 53 个营销技能。

**Architecture:** Fork badlogic/pi-mono → 改包名/CLI 名 → 去冗余 skills → 内置 ETO 扩展 → 自定义 TUI 品牌。

**Tech Stack:** TypeScript (Node.js), Olla嵌入式

## Global Constraints

- 不改 pi-ai 和 pi-agent-core 的内核逻辑
- 不改 pi-tui 的渲染引擎，只改品牌文案
- ETO 扩展代码从外部文件改为内置加载
- 保持对 `--model` / `--provider` 的后向兼容
- `~/.eto/` 替代 `~/.pi/` 作为配置目录

---

### Task 1: Fork + 换皮

**File:** 从 `badlogic/pi-mono` fork 到 `reoroy/eto-cli`，本仓库即为工作目录

**Interface:** 新仓库 URL

- [ ] **Step 1:** 在 GitHub 上创建 `reoroy/eto-cli`（空仓库）

- [ ] **Step 2: Clone pi-mono 并设置上游**

```bash
git clone https://github.com/badlogic/pi-mono.git eto-cli
cd eto-cli
git remote rename origin upstream
git remote add origin https://github.com/reoroy/eto-cli.git
```

- [ ] **Step 3: 改 `package.json：`**

```json
{
  "name": "@reoroy/eto-cli",
  "version": "0.1.0",
  "bin": { "eto": "dist/cli.js" },
  "description": "Evolutionary Teal Organization - 青色组织多 Agent 编排系统"
}
```

- [ ] **Step 4: 提交并推送**

```bash
git add package.json
git commit -m "chore: rename pi to eto"
git push -u origin main
```

---

### Task 2: 去掉 53 个 marketing skills

**File:** 确认 skills 加载路径，排除非核心 skill

**Interface:** 编译后 `node_modules` 体积减少 ~50MB

- [ ] **Step 1: 找到 skills 加载入口**

在 `src/core/resource-loader.ts` 或类似文件中搜索 skills 目录扫描。

- [ ] **Step 2: 白名单只保留 core 和 developer skills**

保留: `ponytail`, `vcp-*`, `developer-*`
去掉: `ab-test-setup`, `ad-creative`, `aeo`, `c-level-skills` 等 53 个营销/产品/增长技能

- [ ] **Step 3: 验证编译后技能数**

```bash
npm run build
eto list-skills  # 确认只看到保留的技能
```

- [ ] **Step 4: 提交**

```bash
git commit -m "chore: remove 53 marketing skills, keep core + dev skills"
```

---

### Task 3: 改配置路径 `~/.pi/` → `~/.eto/`

**File:** `src/core/defaults.ts`

**Interface:** `~/.eto/` 替代 `~/.pi/` 配置文件目录

- [ ] **Step 1: 找到路径常量**

```typescript
// src/core/defaults.ts 中搜索 "~/.pi" 或 ".pi"
const PI_HOME = "~/.eto";  // 原来: "~/.pi"
```

- [ ] **Step 2: 替换所有 `.pi/` 引用为 `.eto/`**

```bash
grep -rn '\.pi/' src/ --include="*.ts"
```

将每个匹配改为 `.eto/`（包括 config/sessions/extensions 等子目录）

- [ ] **Step 3: 编译 + 测试**

```bash
npm run build
eto -p "hello"  # 确认在 ~/.eto/ 下创建配置
```

- [ ] **Step 4: 提交**

```bash
git commit -m "feat: rename config dir ~/.pi/ → ~/.eto/"
```

---

### Task 4: 内置 ETO 扩展

**File:** 新建 `src/core/eto/` 目录

**Interface:** ETO 路由在 AgentSession 初始化时自动注册

- [ ] **Step 1: 将 `eto.ts` 的 routeTask / execPlan / 智子逻辑移入 `src/core/eto/`**

```typescript
// src/core/eto/route.ts — 三镜路由
// src/core/eto/guard.ts — 智子安检
// src/core/eto/index.ts — 注册入口
```

- [ ] **Step 2: 在 AgentSession 初始化时自动注册 ETO 钩子**

`src/core/agent-session.ts` 中 `constructor` 或 `start()` 方法里:

```typescript
import { registerETO } from "./eto";
registerETO(this);  // 自动注入 before_agent_start / tool_call 钩子
```

- [ ] **Step 3: 编译 + 测试**

```bash
npm run build
eto -p "帮我研究什么是llm"  # 确认 ETO 路由生效
```

- [ ] **Step 4: 提交**

```bash
git commit -m "feat: built-in ETO routing/consensus/guard"
```

---

### Task 5: 自定义 TUI 品牌

**File:** `src/tui/` 中的欢迎页/标题/配色

**Interface:** TUI 显示 "ETO" 品牌而非 "pi"

- [ ] **Step 1: 改 TUI 标题**

在 `src/tui/` 中搜索 "pi" 替换为 "ETO"，包括头部标题、状态栏、启动信息

- [ ] **Step 2: 改默认颜色主题**

添加 `eto-dark` 青色主题
```typescript
// src/tui/themes/eto-dark.ts
export const etoDark = {
  primary: "#00b894",  // 青色
  background: "#1a1a2e",
  text: "#e0e0e0",
};
```

- [ ] **Step 3: 改启动欢迎页**

替换 Pi 的 ASCII art 为 ETO 品牌信息：
```
/ETO — 现在，我们是同志了
架构优于单体 · architecture > agent
无序 · 三生 · 有机 · Entropy · Trinity · Organic
```

- [ ] **Step 4: 编译 + 测试**

```bash
npm run build
eto  # 确认 TUI 显示 ETO 品牌
```

- [ ] **Step 5: 提交**

```bash
git commit -m "feat: eto branded TUI with green theme"
```

---

### Task 6: GitHub Release

- [ ] **Step 1:** 创建 v0.1.0-alpha release
- [ ] **Step 2:** 写 Release Notes
- [ ] **Step 3: Publish npm**

```bash
npm publish --access public
```
