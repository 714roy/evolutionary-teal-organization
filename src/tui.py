"""ETO TUI — 终端界面 (prompt_toolkit, 支持复制粘贴)

配色方案来自 Claude Chic。
"""

import sys, os, time, subprocess

if os.name == "nt":
    try:
        import colorama
        colorama.just_fix_windows_console()
    except ImportError:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.expanduser("~/.eto/data/history.txt")
os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

from rich.console import Console
from rich.text import Text
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style

console = Console(color_system="truecolor")
PROMPT_STYLE = Style.from_dict({
    "bottom-toolbar": "bg:#252525 fg:#666666",
})
try:
    ps = PromptSession(history=FileHistory(HISTORY_FILE))
except Exception:
    ps = None

# ── Claude Chic 配色 ──
C_ORANGE = "#e89800"
C_BLUE = "#55bbff"
C_GREY = "#888888"
C_DIM = "#666666"
C_DARK = "#333333"
C_BG = "#1a1a1a"
C_TEXT = "#cccccc"
C_GREEN = "#55ff55"
C_TIME = "#555555"


# ── 模块级代码块缓冲（跨 render_line 调用保持状态）──
_code_buf = []
_in_code = False


def sec_str(s):
    return f"{s:.1f}s" if s < 60 else f"{s//60:.0f}m{s%60:.0f}s"


def core_output(buf: list, task: str):
    """子进程运行 core.py main() 并实时流式输出

    用 subprocess 替代 threading（审计发现：原 Thread + stdout 替换方式
    导致界面冻结到执行结束，且渲染丢失 zhizi 等关键行）。
    """
    core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core.py")
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    proc = subprocess.Popen(
        [sys.executable, "-u", core_path, task],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        encoding="utf-8", errors="replace",
        bufsize=0,
        env=env,
    )
    for line in proc.stdout or []:
        line = line.rstrip("\n\r")
        if line:
            buf.append(line + "\n")
            # 实时流式渲染到终端
            render_line(line, console)
    proc.wait()


def render_line(line: str, c: Console):
    """逐行渲染 core.py 输出到终端（实时流式，支持代码块缓冲）"""
    global _code_buf, _in_code

    raw = line         # 保留原始缩进（代码缩进有意义）
    s = line.strip()   # 用于模式匹配

    # ── 代码块缓冲 ──────────────────────────────
    if s.startswith("```"):
        if _in_code:
            # 关闭代码块 → 用 Syntax 渲染
            text = "\n".join(_code_buf)
            _code_buf = []
            _in_code = False
            if text.strip():
                lang = s.strip("`").strip() or "text"
                try:
                    c.print(Syntax(text, lang, theme="monokai",
                                   line_numbers=False, word_wrap=True))
                except Exception:
                    c.print(Text(text, style=C_TEXT))
            return
        else:
            _in_code = True
            _code_buf = []
            return

    if _in_code:
        _code_buf.append(raw)
        return

    # ── 空行 ──
    if not s:
        return

    # ── 系统噪声屏蔽 ──
    if any(s.startswith(p) for p in ("ETO Teal", "Time:")):
        return
    if s.startswith("[tool]") or s.startswith("[Tool]"):
        return  # 内部工具通知，用户不需要看到
    if s.startswith("Warning:") or s.startswith("warning:"):
        return  # Pi CLI 模型警告，不影响功能
    # 工具调用 JSON（Pi 函数调用输出，非用户可见内容）
    if s.startswith('{"name":') and '"arguments"' in s:
        return
    if s.replace("─", "").replace("-", "").strip() == "" and len(s) > 5:
        return
    if "match=" in s and "score=" in s and "->" not in s:
        return

    # ── 彩色渲染 ──
    if s.startswith("Task:"):
        # Task 行已由 prompt 回显，不再重复 Panel（用户反馈：去掉回声）
        return
    elif s.startswith("Agents:"):
        pass
    elif "Analyzing..." in s:
        c.print(Text(f"  路由: {s.split('ROUTE=')[-1]}", style=C_GREY))
    elif s.startswith("Electing"):
        c.print(Text(f"  选举协调员...", style=C_GREY))
    elif s.startswith("Coordinator:"):
        c.print(Text(f"  协调员: {s.replace('Coordinator:', '').strip()}",
                     style=f"bold {C_BLUE}"))
    elif s.startswith("Drafting"):
        c.print(Text(f"  分解任务...", style=C_GREY))
    elif s.startswith("Steps:"):
        c.print(Text(f"  {s}", style=C_GREY))
    elif s.startswith(("Consensus", "T-")):
        c.print(Text(f"  {s}", style=C_GREY))
    elif s.startswith("| ") and "score=" in s:
        c.print(Text(f"  {s.strip()}", style=C_GREY))
    elif s.startswith("平均评分"):
        ok = "V" in s or "通过" in s
        sty = f"bold {C_BLUE}" if ok else C_ORANGE
        c.print(Text(f"  共识: {s}", style=sty))
    elif s.startswith("V 共识"):
        c.print(Text(f"  共识通过 ✓", style=f"bold {C_BLUE}"))
    elif s.startswith("L 智子"):
        ok = "V" in s or "通过" in s
        c.print(Text(f"  智子: {s}", style=C_GREEN if ok else C_ORANGE))
    elif s.startswith("Action blocked"):
        c.print(Text(f"  ⛔ {s}", style=f"bold {C_ORANGE}"))
    elif s.startswith("["):
        if "veto" in s or "VETO" in s:
            c.print(Text(f"  ⛔ {s}", style=f"bold {C_ORANGE}"))
        elif "warn" in s:
            c.print(Text(f"  ⚠ {s}", style=C_ORANGE))
        else:
            c.print(Text(f"  {s}", style=C_GREY))
    elif s.startswith(("✗", "expired", "deadlock")) or "智子否决" in s:
        c.print(Text(f"  ✗ {s}", style=f"bold {C_ORANGE}"))
    elif s.startswith("->"):
        c.print(Text(f"  {s}", style=C_ORANGE))
    elif s.startswith("Executing"):
        c.print(Text(f"  执行...", style=C_GREY))
    elif s.startswith(">> Step"):
        # Step 标题行（streaming 模式）
        c.print(Text(f"  ● {s.replace('>>', '').strip()}",
                     style=f"bold {C_BLUE}"))
    elif s.startswith(">>"):
        c.print(Text(f"  {s.replace('>>', '').strip()}", style=C_TEXT))
    elif s.startswith(("Done", "完成")):
        c.print(Text(f"  ✓ 完成", style=f"bold {C_BLUE}"))
    elif s.startswith("!"):
        c.print(Text(f"  {s}", style=C_ORANGE))
    else:
        # LLM 输出 / 代码行 → 保留原始缩进
        c.print(Text(raw, style=C_TEXT))


def format_output(buf: list, task: str):
    """（保留兼容）渲染缓存的 core.py 输出为 Rich renderable list

    实时模式已用 render_line 替代，此函数仅在非流式回退时使用。
    """
    lines = []
    code_buf = []
    in_code = False
    results = []

    for raw in buf:
        line = raw.rstrip("\n")
        s = line.strip()
        if not s:
            continue
        if s.startswith("```"):
            if in_code:
                text = "\n".join(code_buf)
                if text.strip():
                    results.append(("code", text, s.strip("`").strip() or "text"))
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        results.append(("raw", s))

    for kind, s in results:
        if kind == "code":
            try:
                lines.append(Syntax(s, "text", theme="monokai", line_numbers=False, word_wrap=True))
            except Exception:
                lines.append(Text(f"  {s}"))
        else:
            lines.append(Text(f"  {s}", style=C_TEXT))

    return lines


def _welcome():
    """Claude Code 风格欢迎页——双栏 + 全信息"""
    console.print()

    # ── 左栏：Logo + 品牌 ──
    logo_lines = [
        "    ▐▛▀▀▀▜▌    ",
        "    ▐▛▀▀▀▜▌    ",
        "    ▐▛█▄▄▜▌    ",
        "     ▝▜██▛▘     ",
        "      ▝▀▀▘      ",
    ]
    logo = "\n".join(logo_lines)

    left = Text()
    left.append(Text(logo + "\n", style=C_BLUE))
    left.append(Text("\n", ""))
    left.append(Text("/ETO  —  Teal Organization\n", style=f"bold {C_TEXT}"))
    left.append(Text("青色组织多 Agent 编排系统\n", style=C_GREY))
    left.append(Text("\n", ""))
    left.append(Text("架构优于单体\n", style=f"bold {C_BLUE}"))
    left.append(Text("architecture > agent\n", style=C_DIM))
    left.append(Text("无序 · 三生 · 有机\n", style=f"bold {C_BLUE}"))
    left.append(Text("Entropy · Trinity · Organic\n", style=C_DIM))

    # ── 右栏：Tips + 状态 ──
    right = Text()
    right.append(Text("快速上手  Tips for getting started\n", style=f"bold {C_DIM}"))
    right.append(Text(f"  {'─' * 36}\n", style=C_DARK))
    right.append(Text("  输入任务开始 ETO 全流程：\n", style=C_GREY))
    right.append(Text("  三镜分析 / 3-Mirror Analysis\n", style=C_GREY))
    right.append(Text("  Agent 选举 / Election\n", style=C_GREY))
    right.append(Text("  同侪共识 / Consensus\n", style=C_GREY))
    right.append(Text("  流式执行 / Streaming Execution\n", style=C_GREY))
    right.append(Text("\n", ""))
    right.append(Text("当前状态  What's ready\n", style=f"bold {C_DIM}"))
    right.append(Text(f"  {'─' * 36}\n", style=C_DARK))
    right.append(Text("  Phase 1: A2A/Sanjing/Election/Execution  ✅\n", style=C_GREY))
    right.append(Text("  Phase 2: MCP/Skills/Governance  🟡\n", style=C_GREY))
    right.append(Text("  Phase 3: Dynamic Routing/Evolution  📋\n", style=C_GREY))

    # ── 双栏布局 ──
    body = Table.grid(padding=(0, 4))
    body.add_column(ratio=1, no_wrap=True)
    body.add_column(ratio=2)
    body.add_row(left, right)

    # ── 底部信息 ──
    import os as _os
    cwd = _os.getcwd()

    # ── 外层布局 ──
    outer = Table.grid(padding=(0, 0))
    outer.add_column()
    outer.add_row(body)
    outer.add_row(Text(""))
    outer.add_row(Text("  Qwen 2.5-Coder:7b @ Ollama (local)", style=C_DIM))
    outer.add_row(Text(f"  {cwd}", style=C_DIM))

    console.print(Panel(
        outer,
        title="Evolutionary-Teal-Organization",
        border_style=C_DIM,
        padding=(0, 1),
    ))
    console.print()


def _make_toolbar():
    """prompt_toolkit 底部工具栏"""
    return FormattedText([
        ("class:bar", "  输入任务 → 回车执行  |  /exit 退出  |  Ctrl+L 清屏  |  /clear 清屏  "),
    ])


def main():
    _welcome()

    while True:
        try:
            if ps:
                task = ps.prompt(" >> ", bottom_toolbar=_make_toolbar,
                                 style=PROMPT_STYLE).strip()
            else:
                task = input(" >> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not task:
            continue
        if task in ("/exit", "/quit"):
            break
        if task == "/clear":
            console.clear()
            _welcome()
            continue

        # 子进程流式执行
        buf = []
        t0 = time.time()
        core_output(buf, task)
        elapsed = time.time() - t0

        console.print(Text(f"  {sec_str(elapsed)}", style=C_TIME))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
