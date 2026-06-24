# ETO CLI — Fork Plan

> 目标: 在 pi-mono 基础上 fork 出 `eto` 命令，内置 ETO 青色编排逻辑

---

## Phase 1: Fork + 重命名（1-2 小时）

- [ ] **Fork 仓库**
  - `git clone https://github.com/earendil-works/pi-mono`
  - 推送到 `github.com/reoroy/eto-cli`

- [ ] **改包名**
  - `package.json`: `"name": "@reoroy/eto-cli"`
  - `package.json`: 清空 `"pi"` bin 项，加 `"eto": "dist/cli.js"`
  - `package.json`: `"description": "Evolutionary-Teal-Organization — 青色组织多 Agent 编排系统"`

- [ ] **改 CLI 入口**
  - `src/cli/args.ts`: 把 `"pi"` 替换为 `"eto"`
  - `src/bun/cli.ts`: 同上
  - 所有 CLI 帮助文本中的 `pi` → `eto`

- [ ] **改安装路径**
  - `~/.eto/` 替代 `~/.pi/`
  - `src/core/defaults.ts`: 改默认路径常量
  - `src/core/resource-loader.ts`: 改扩展/skill/主题搜索路径

- [ ] **改通知/标题**
  - TUI 标题: `"ETO"` 替代 `"pi"`
  - 启动通知: `"🦋 ETO 青色组织模式"`

## Phase 2: 核心功能（2-3 小时）

- [ ] **内置 ETO 扩展**
  - 把 `extensions/eto.ts` 的代码移入 `src/core/eto/`
  - 在 `AgentSession` 初始化时自动注册 ETO 钩子（不需要 `-e` 加载）
  - 保留对外部扩展的支持（用户仍可写自己的扩展）

- [ ] **默认模型**
  - `src/core/defaults.ts`: `defaultProvider: "ollama"`, `defaultModel: "qwen2.5-coder:7b"`
  - 仍支持 `--model qwen3.6` `--provider openai` 等自由切换

- [ ] **ETO 欢迎页**
  - 改 TUI 启动页显示 ETO Logo + 双栏信息
  - 快捷键列表带 ETO 特色命令

- [ ] **青色主题**
  - `src/tui/themes/`: 加 `eto-dark.ts` 青色配色
  - 默认应用

## Phase 3: 去冗余（1-2 小时）

- [ ] **砍掉不需要的包**
  - `pi-tui` → 保留（TUI 是核心）
  - `pi-ai` → 保留（提供商抽象是核心优势）
  - 各种可选依赖 → 评估是否保留

- [ ] **精简二进制体积**
  - pi v0.79.8 依赖 ~18 个 npm 包
  - 目标是去掉不需要的 provider SDK、UI 主题等

- [ ] **简化配置**
  - 默认配置最小化，不加载 53 个 marketing skills（~50MB）
  - 按需加载，用户需要时 `eto install skill web-search`

## Phase 4: 发布（1 小时）

- [ ] **编译测试**
  ```bash
  npm run build
  npm link
  eto -p "hello"
  ```

- [ ] **GitHub Release**
  - 创建 v0.1.0 release
  - 附二进制（可选）
  - README 更新

- [ ] **npm publish**
  ```bash
  npm publish --access public
  ```

---

## 不做的事（保持简洁）

| 事项 | 理由 |
|:-----|:------|
| ❌ 重写 Rust 层 | omp 做了，但 ETO 不需要 |
| ❌ 加 LSP/DAP | 青色组织编排不需要 |
| ❌ 加 40+ 提供商 | Pi 的 15+ 已经够用 |
| ❌ 砍掉 pi-ai | 提供商抽象是核心竞争力 |
| ❌ 大版本号跳跃 | 从 v0.1.0 开始，真实迭代 |

---

## 时间估计

```
Phase 1 (重命名)    1-2h
Phase 2 (核心功能)  2-3h
Phase 3 (去冗余)     1-2h
Phase 4 (发布)       1h
─────────────────
总计                 ~8h（一个完整工作日）
```
