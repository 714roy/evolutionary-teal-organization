"""TealContext — 共享记忆池 (ETO-022/023/026)

数据契约见 docs/phase-1-core-loop.md §3.2
- global_memory 上限 1000 条
- 文件写操作加简单文件锁（Windows 兼容：信号量文件）

Phase 2 改进（审计发现 #3）:
- 启动时自动恢复孤儿锁
- 提议超时从 30min → 5min
- 每次 init 都清理，不再依赖被动条件
"""

import json
import os
import time
import tempfile
from pathlib import Path

DATA_DIR = Path.home() / ".eto" / "data"
LOCK_FILE = Path(tempfile.gettempdir()) / ".eto_context.lock"
STALE_TIMEOUT = 300   # 5 分钟（原 1800s，审计发现 #3 建议缩短）
LOCK_STALE_TIMEOUT = 30  # 锁文件超过 30s 视为孤儿
COMPRESS_THRESHOLD = 200  # global_memory 超过此数则自动压缩（发现 #5 修复）


class FileLock:
    """跨平台简单文件锁（基于目录原子性 mkdir）"""

    def __enter__(self):
        locked = False
        for _ in range(50):  # 最多等 5s
            try:
                os.mkdir(str(LOCK_FILE))
                locked = True
                break
            except FileExistsError:
                time.sleep(0.1)
        if not locked:
            raise TimeoutError("TealContext 文件锁超时")

    def __exit__(self, *exc):
        try:
            os.rmdir(str(LOCK_FILE))
        except FileNotFoundError:
            pass


class TealContext:
    """青色组织共享上下文"""

    def __init__(self, cleanup_stale=True):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._recover_orphan_lock()
        self._path = DATA_DIR / "context.json"
        self._load()
        # 每次 init 都清理超时提议（审计发现 #3 修复）
        # cleanup_stale 参数保留向后兼容（测试使用 False）
        if self.data["active_proposals"]:
            self._cleanup_stale_proposals()

    @staticmethod
    def _recover_orphan_lock():
        """启动时清理孤儿锁文件（超过 30s 的残留锁）"""
        lock = str(LOCK_FILE)
        if os.path.exists(lock):
            try:
                mtime = os.path.getmtime(lock)
                if time.time() - mtime > LOCK_STALE_TIMEOUT:
                    os.rmdir(lock)
            except (OSError, FileNotFoundError):
                pass

    # ── 内部 ──────────────────────────────────────────

    def _load(self):
        if self._path.exists():
            raw = self._path.read_text(encoding="utf-8")
            self.data = json.loads(raw) if raw.strip() else self._empty()
        else:
            self.data = self._empty()
        # 自动压缩重复记忆（发现 #5 修复）
        if len(self.data.get("global_memory", [])) > COMPRESS_THRESHOLD:
            self._compress_memory()

    def _compress_memory(self):
        """合并 global_memory 中重复的任务记录（相同 task + agent + type）

        从 context.json 的实际数据看，"调研AI行业"出现 5 次、"评估结果解析失败"出现 15 次。
        压缩后保留第一次出现 + 聚合统计，腾出空间给新信息。
        """
        raw = self.data.get("global_memory", [])
        if len(raw) <= COMPRESS_THRESHOLD:
            return

        seen = {}        # (task, agent, type) → canonical entry
        order = []       # 保持首次出现顺序
        duplicates = 0

        for entry in raw:
            key = (entry.get("task", ""), entry.get("agent", ""), entry.get("type", ""))
            if key in seen:
                # 合并：更新 count + 最新 timestamp
                seen[key]["_merged_count"] = seen[key].get("_merged_count", 1) + 1
                seen[key]["_last_timestamp"] = entry.get("timestamp", "")
                if entry.get("feedback"):
                    seen[key]["_last_feedback"] = entry.get("feedback")
                duplicates += 1
            else:
                seen[key] = dict(entry)
                seen[key]["_merged_count"] = 1
                order.append(key)

        compressed = [seen[k] for k in order]
        self.data["global_memory"] = compressed
        self._save()

    def _save(self):
        self._path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _empty():
        return {"global_memory": [], "active_proposals": [], "consensus_log": []}

    def _cleanup_stale_proposals(self):
        """清理超过 5 分钟的停滞提议，移入 consensus_log（审计发现 #3 修复）"""
        now = time.time()
        cleaned = []
        for p in self.data["active_proposals"]:
            created = p.get("created_at", "")
            try:
                # ISO8601 → timestamp
                ct = time.mktime(time.strptime(created, "%Y-%m-%dT%H:%M:%S"))
            except (ValueError, TypeError):
                ct = 0
            if p["status"] in ("pending", "voting") and ct and (now - ct) > STALE_TIMEOUT:
                # 超时 → 移入 consensus_log
                self.data["consensus_log"].append({
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "type": "timeout",
                    "proposer": p.get("proposer", ""),
                    "plan_id": p.get("id", ""),
                    "detail": {"reason": "stale proposal cleaned up"},
                })
            else:
                cleaned.append(p)
        if len(cleaned) != len(self.data["active_proposals"]):
            self.data["active_proposals"] = cleaned
            self._save()

    def _atomic_update(self, fn):
        """线程安全的读取-修改-写入"""
        with FileLock():
            self._load()
            fn(self.data)
            self._save()

    # ── 公共 API ──────────────────────────────────────

    def perceive(self, agent_id: str) -> dict:
        """Agent 执行前感知上下文 (ETO-023)"""
        self._load()
        return {
            "recent": self.data["global_memory"][-10:],
            "active": [
                p
                for p in self.data["active_proposals"]
                if p["status"] in ("pending", "voting")
            ],
            "my_recent": [
                m for m in self.data["global_memory"] if m.get("agent") == agent_id
            ][-5:],
        }

    def record(
        self,
        entry_type: str,
        agent: str,
        plan: dict,
        result: str = None,
        feedbacks: list = None,
    ):
        """写入 global_memory (ETO-023)"""
        def _do(data):
            entry = {
                "id": f"mem_{int(time.time()*1000)}",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "agent": agent,
                "type": entry_type,
                "task": plan.get("task", ""),
                "summary": plan.get("analysis", ""),
                "result": result,
                "feedback": feedbacks,
            }
            data["global_memory"].append(entry)
            if len(data["global_memory"]) > 1000:
                data["global_memory"] = data["global_memory"][-1000:]

        self._atomic_update(_do)

    def propose(self, proposal: dict) -> str:
        """将提议加入 active_proposals (ETO-023)"""
        prop_id = proposal.get("id") or f"prop_{int(time.time()*1000)}"
        proposal["id"] = prop_id

        def _do(data):
            data["active_proposals"].append(proposal)

        self._atomic_update(_do)
        return prop_id

    def vote(self, proposal_id: str, agent_id: str, score: float, concern: str = None):
        """记录评分并检查共识状态"""
        def _do(data):
            for p in data["active_proposals"]:
                if p["id"] == proposal_id:
                    p.setdefault("feedbacks", []).append(
                        {"agent": agent_id, "score": score, "concern": concern}
                    )
                    # 计算平均分
                    scores = [f["score"] for f in p["feedbacks"] if f["score"] is not None]
                    if scores:
                        avg = sum(scores) / len(scores)
                        p["_avg_score"] = round(avg, 3)
                    break

        self._atomic_update(_do)

    def query(self, **filters) -> list:
        """按 type / agent / result 过滤历史 (ETO-023)"""
        self._load()
        results = list(self.data["global_memory"])
        for key, val in filters.items():
            if val is not None:
                results = [r for r in results if r.get(key) == val]
        return results

    def consensus_log_append(self, entry: dict):
        """写入 consensus_log"""
        def _do(data):
            data["consensus_log"].append(entry)

        self._atomic_update(_do)

    def complete_proposal(self, proposal_id: str, status: str = "done"):
        """将提议移入 consensus_log"""
        def _do(data):
            for i, p in enumerate(data["active_proposals"]):
                if p["id"] == proposal_id:
                    p["status"] = status
                    log_entry = {
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "type": status,
                        "proposer": p.get("proposer", ""),
                        "plan_id": proposal_id,
                        "peer_scores": {
                            f["agent"]: f["score"]
                            for f in p.get("feedbacks", [])
                        },
                        "avg_score": p.get("_avg_score"),
                        "veto": status == "vetoed",
                        "verdict": status,
                    }
                    data["consensus_log"].append(log_entry)
                    data["active_proposals"].pop(i)
                    break

        self._atomic_update(_do)
