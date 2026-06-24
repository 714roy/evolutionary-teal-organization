# ETO Stitches — 缝合层

> 不写框架，只缝已有的开源项目。每层胶水代码 < 50 行。

## 依赖安装

```bash
# Python 包
pip install protolink        # A2A 通信
pip install votingai         # 共识投票
pip install lythonic         # 轻量 DAG 编排

# Node.js 包（Pi 扩展）
npm install @yylan/pi-memory # 长期语义记忆

# 本地源码（纯 Python，无需安装）
stitches/raft-lite/          # Raft 选举
stitches/maestro/            # 任务分解 DAG
```

## 各层

```
stitches/
├── comms/           ProtoLink A2A 通信
├── consensus/       VotingAI 共识投票
├── election/        raft-lite 协调员选举
└── routing/         Maestro / lythonic 任务分解
```

## 设计原则

1. 胶水代码 < 50 行/层
2. 不改上游源码
3. 每层可独立替换
