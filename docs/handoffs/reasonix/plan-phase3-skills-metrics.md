# Phase 3 — 技能库 + Peer Registry + Metrics

> 日期: 2026-07-01
> 优先级: P1（Phase 2 Agent 编排已就绪，现在需要持久化）
> 执行端: Reasonix
> 可用空间: ~604行（当前396 → 目标1000）

---

## 一、为什么需要 Phase 3

Phase 1 + 2 完成了：路由 → 匹配 → 分解 → 分发。但缺少：

```
没有记忆：每次会话都从零开始，Agent Profile 固定不变
没有学习：失败了不积累经验，不会自我进化
没有生态：Agent 无法动态发现彼此（硬编码的 3 个角色）
没有度量：不知道路由是否正确、哪个 Agent 做得好
```

Phase 3 的目标是让 ETO **从静态编排变成自适应系统**。

---

## 二、设计原则

### 1. JSONL 追加式持久化（不建数据库）

所有持久化走文件追加。不需要读写锁——每个 session 独立一行。

```jsonlines
# ~/.eto/memory/skills.jsonl
{"skill_name": "flask-login", "context": "需要 bcrypt + session", "reward": 0.9, "timestamp": "2026-07-01T14:30:00+08:00"}

# ~/.eto/memory/metrics.jsonl
{"route": "code→plan", "agent": "coder", "success": true, "steps": 3}

# ~/.eto/memory/peers.jsonl
{"name": "devops-agent", "ip": "192.168.3.50", "services": ["deploy", "monitor"], "joined": "2026-07-01"}
```

### 2. Skill = 文件，不是服务

技能注册就是写一个 JSONL 行 + 生成一个 `.md` 文件到 `~/.eto/skills/`。不需要启动新进程。

### 3. Peer = HTTP 简单协议

Peer registry 是 50 行的简单 HTTP server，不装 Redis/Docker。Agent 定期 ping /health。

---

## 三、子计划拆分

### Plan 3-01: Skill Memory（~80 行）

**文件:** `eto/extensions/eto.ts` + 新增 `eto/stitches/memory/skill_store.py`

```
功能：
- Agent 完成任务后，自动将经验保存为 skill
- Skill 结构: { name, description, context, reward, timestamp }
- 下次匹配时，优先搜索匹配的 skill → 注入 systemPrompt

实现：
1. 在 before_agent_start 中加载已有 skills（JSONL 读入）
2. 匹配度 ≥ 0.7 的 skill 注入到 systemPrompt
3. ETO consensus 工具调用后追加奖励记录

代码位置：
- eto.ts: loadSkills(), matchSkillsForRoute(), injectSkillContext() (~50行)
- stitches/memory/skill_store.py: SkillStore.append/load/scan (~30行)
```

### Plan 3-02: Peer Registry（~80 行）

**文件:** `eto/stitches/registry.py`（新增单文件）+ eto.ts 小改

```
功能：
- 简单 HTTP server（Python stdlib http.server），端口 5100
- PUT /register {name, ip, services, skills} → 注册 Agent
- GET /peers → 返回所有存活 Peer JSON
- DELETE /unregister/{name} → 注销
- Health check: GET /health/{name} → ping

使用场景：
before_agent_start → matchAgentsForRoute() 后，从 registry 获取远程 Peer
如果路由结果需要 consensus（高风险任务），分发给注册过的 Agent

代码：
- eto.ts: fetchPeers(), callRemotePeer() (~40行)
- stitches/registry.py: HTTP server + memory store (~40行)
```

### Plan 3-03: Metrics（~50 行）

**文件:** `eto/stitches/metrics.py`（新增）+ eto.ts 小改

```
功能：
- 每次路由 + Agent 匹配后写入 metrics.jsonl
- 统计指标: route分布、Agent成功率、平均执行步数
- 内置 CLI 命令: pi -e eto.ts --metrics → 输出当前统计

代码位置：
- stitches/metrics.py: MetricsCollector（write/query/count）(~30行)
- eto.ts: 在 before_agent_start 末尾调用 metrics.write() (~20行)
```

### Plan 3-04: Agent Profile Editor（~60 行）

**文件:** `eto/stitches/profile_editor.py`（新增）

```
功能：
- CLI 工具编辑 Agent Profile（profile list/update/delete）
- JSON → YAML 自动转换，带格式验证
- 支持导入外部 profile（CSV/JSONL）

代码位置：
- stitches/profile_editor.py: ProfileCLI (~60行)
```

---

## 四、架构总览

```
before_agent_start
│
├── loadProfiles()           → Agent Profile（Phase 2 已有）
├── loadSkills()             → Skill Memory（Phase 3-01，新增）
├── fetchPeers()             → Peer Registry（Phase 3-02，新增）
├── matchAgentsForRoute()    → 匹配 Agent（Phase 2 已有）
│   └── 优先：skill 中找匹配 Agent
│   └── 备选：Profile weights 排序
│
├── decomposeTask()          → 分解子任务（Phase 2 已有）
├── execPlan()               → 分发执行（Phase 2 已有，async）
│
├── metrics.write(route, agent, success)  → 记录指标（Phase 3-03，新增）
└── stitcherSuccess ? storeSkill()       → 成功自动记 skill（Phase 3-01，新增）

profile_editor CLI           → 管理 Agent Profile（Phase 3-04，新增）
metrics CLI                  → 查看运行指标（Phase 3-03，新增）
```

---

## 五、不做

| 功能 | 理由 |
|:-----|:------|
| Agent 动态创建 | Phase 4，需要 Docker/容器 |
| Skill UI / 管理界面 | Pi TUI 领域 |
| 分布式调度（DAG/RPC） | Maestro 等成熟方案 |
| 实时推送 | WebSocket 太重 |
| 超过 1000 行 | 硬约束 |

---

## 六、验证标准

### Plan 3-01 Skill Memory：
1. 存一个 skill → `cat ~/.eto/memory/skills.jsonl` 确认有记录
2. 下次启动 → widget 显示匹配的 skill 名
3. Skill reward > threshold → systemPrompt 中注入该 skill 内容

### Plan 3-02 Peer Registry：
1. 注册两个 Agent → GET /peers 返回两者
2. 路由到 consensus → 自动尝试分发给远程 Peer
3. 注销一个 → GET /peers 只剩一个

### Plan 3-03 Metrics：
1. 跑 3 个不同任务 → metrics.jsonl 有 3 条记录
2. `pi -e eto.ts --metrics` → 显示 route分布 + agent成功率

### Plan 3-04 Profile Editor：
1. `python profile_editor.py list` → 显示当前 profiles
2. `profile_editor.py update researcher specialty research,research` → 成功更新
3. `profile_editor.py validate` → 格式验证通过

---

## 七、文件清单

| 文件 | 变更 | 新增代码 |
|:-----|:------|:--------|
| `eto/extensions/eto.ts` | Skill加载 + registry调用 + metrics记录 | ~80行 |
| `eto/stitches/memory/skill_store.py` | **新建** — Skill 持久化 | ~30行 |
| `eto/stitches/registry.py` | **新建** — HTTP Peer Registry | ~40行 |
| `eto/stitches/metrics.py` | **新建** — MetricsCollector | ~30行 |
| `eto/stitches/profile_editor.py` | **新建** — Profile CLI 工具 | ~60行 |

---

## 八、成功标准

- [ ] Skill Memory：存 → 读 → 注入 pipeline 全通
- [ ] Peer Registry：注册 / 发现 / 注销 正常
- [ ] Metrics：记录 + 查询正确
- [ ] Profile Editor：增删改查正常
- [ ] Stitcher 9/9 测试继续通过（不受影响）
- [ ] `pi -p` 无报错、无 UI 闪烁
- [ ] 总行数 ≤ 1000（~396 → ~604）

---

## 九、完成回执要求

1. 每个 Plan 的验证输出样本
2. Skill Memory: 存 skill 后下次启动 widget 显示
3. Metrics: `--metrics` CLI 输出
4. Profile Editor: `list/update/validate` 命令输出
5. Stitcher 测试输出
