"""Pi CLI 执行器 (ETO-014) — 带工具回调 + 增强 JSON 提取"""
import subprocess, json, re, os, sys as _sys, shutil

_IS_WIN = _sys.platform == "win32"

# ── Pi CLI 探测 ──────────────────────────────────────────
# 跳过 shell 脚本包装，直接调用 node 入口（避免 Windows 编码问题）
_PI_CLI = None  # lazy init
_PI_NODE = None


def _resolve_pi():
    global _PI_CLI, _PI_NODE
    if _PI_CLI is not None:
        return _PI_CLI, _PI_NODE

    # 搜索 pi 可执行文件的位置
    pi_path = shutil.which("pi")
    if pi_path:
        # 检查是否是 Node.js 入口（shell 脚本 → 提取真实 .js 路径）
        try:
            with open(pi_path, "r", encoding="utf-8") as f:
                head = f.read(512)
            if head.startswith("#!/") and "node" in head:
                # Shell wrapper: 提取 JS 入口路径
                m = re.search(r'node\s+(.*?)(?:"\s*"\$@|\$@)', head)
                if m:
                    js_path = m.group(1).strip().strip('"')
                    if not os.path.isabs(js_path):
                        js_path = os.path.join(os.path.dirname(pi_path), js_path)
                    _PI_CLI = js_path
                    _PI_NODE = shutil.which("node") or "node"
                    return _PI_CLI, _PI_NODE
        except Exception:
            pass
        # fallback: 直接使用 pi 命令（Unix 或 shell=True 场景）
        _PI_CLI = pi_path
        _PI_NODE = None
        return _PI_CLI, _PI_NODE

    # 常见安装路径兜底
    for base in [
        os.path.expanduser("~/AppData/Roaming/npm"),
        "/usr/local/lib/node_modules/@earendil-works/pi-coding-agent",
        "/usr/lib/node_modules/@earendil-works/pi-coding-agent",
    ]:
        candidate = os.path.join(base, "dist/cli.js")
        if os.path.exists(candidate):
            _PI_CLI = candidate
            _PI_NODE = shutil.which("node") or "node"
            return _PI_CLI, _PI_NODE

    raise FileNotFoundError("pi CLI not found")

# 工具调用回调 —— TUI 通过 set_tool_callback() 注册，每次 call_pi 前后触发
# 无注册时 fallback 到 stderr 输出（审计发现 #2）
_on_tool_call = None  # callback: fn(tool_name: str, input_summary: str, output_summary: str)


def set_tool_callback(fn):
    """注册工具调用回调（用于 TUI 的流式工具可视化）"""
    global _on_tool_call
    _on_tool_call = fn


def _emit_tool_notify(model: str, inp: str, out: str | None):
    """通知 TUI 或 fallback 到 stderr（审计发现 #2 修复）

    stderr 输出仅在 ETO_DEBUG=1 时生效，避免子进程模式下
    [tool] 行泄漏到 TUI 输出流（用户反馈 #1）。
    """
    if _on_tool_call:
        try:
            _on_tool_call(model, inp, out)
        except Exception:
            pass
    elif os.environ.get("ETO_DEBUG"):
        status = f" after {out[:80].strip()}" if out else ""
        print(f"[tool] {model} {inp[:60]}...{status}", file=_sys.stderr)


def call_pi(prompt, system_prompt=None, tools=None, exclude_tools=None,
            model="ollama/qwen2.5-coder:7b", provider="ollama", timeout=120):
    """调用 Pi CLI 并返回 stdout（集成工具回调）

    prompt 通过 stdin 传递（避免 Windows 命令行编码问题）。
    """
    try:
        pi_js, node_bin = _resolve_pi()
    except FileNotFoundError:
        return "<ERROR: 'pi' command not found>"

    if node_bin:
        # 直接走 node pi-cli.js（跳过 shell 脚本包装）
        cmd = [node_bin, pi_js, "--print", "--mode", "text", "--provider", provider, "--model", model]
    else:
        # Unix 上 pi 可能是可执行二进制或符号链接
        cmd = [pi_js, "--print", "--mode", "text", "--provider", provider, "--model", model]

    if system_prompt:
        cmd += ["--system-prompt", system_prompt]
    if tools:
        cmd += ["--tools", ",".join(tools)]
    elif not exclude_tools:
        cmd += ["--no-tools"]
    if exclude_tools:
        cmd += ["--exclude-tools", ",".join(exclude_tools)]

    # 工具调用前触发回调
    cb_key = prompt[:120].replace("\n", " ")
    cb_model = f"{provider}/{model}"
    cb_input = f"[{','.join(tools or ['no-tools'])}] {cb_key}"
    _emit_tool_notify(f"pi({cb_model})", cb_input, None)

    try:
        result = subprocess.run(
            cmd,
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=timeout,
            shell=False,
        )
        stdout = result.stdout or b""
        stderr = result.stderr or b""
        stdout_str = stdout.decode("utf-8")
        stderr_str = stderr.decode("utf-8", errors="replace")

        if result.returncode != 0:
            err_msg = f"<ERROR: Pi exited with code {result.returncode}: {stderr_str.strip()}>"
            _emit_tool_notify(f"pi({cb_model})", cb_input, err_msg[:200])
            return err_msg

        output = stdout_str.strip()
        _emit_tool_notify(f"pi({cb_model})", cb_input, output[:200])
        return output if output else "<EMPTY>"

    except subprocess.TimeoutExpired:
        err_msg = f"<ERROR: Pi timeout after {timeout}s>"
        _emit_tool_notify(f"pi({cb_model})", cb_input, err_msg)
        return err_msg
    except FileNotFoundError:
        return "<ERROR: 'pi' command not found>"
    except Exception as e:
        return f"<ERROR: {e}>"


def call_pi_stream(prompt, stream_callback=None, system_prompt=None, tools=None, exclude_tools=None,
                   model="ollama/qwen2.5-coder:7b", provider="ollama", timeout=120):
    """调用 Pi CLI 并逐行流式输出。

    stream_callback(line: str) 会在每行输出到达时被调用。
    返回完整输出文本。
    """
    try:
        pi_js, node_bin = _resolve_pi()
    except FileNotFoundError:
        return "<ERROR: 'pi' command not found>"

    if node_bin:
        cmd = [node_bin, pi_js, "--print", "--mode", "text", "--provider", provider, "--model", model]
    else:
        cmd = [pi_js, "--print", "--mode", "text", "--provider", provider, "--model", model]

    if system_prompt:
        cmd += ["--system-prompt", system_prompt]
    if tools:
        cmd += ["--tools", ",".join(tools)]
    elif not exclude_tools:
        cmd += ["--no-tools"]
    if exclude_tools:
        cmd += ["--exclude-tools", ",".join(exclude_tools)]

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # 丢弃 stderr（Model Warning 不影响功能）
            bufsize=0,                 # 无缓冲（Windows 不支持行缓冲二进制管道）
        )
        proc.stdin.write(prompt.encode("utf-8"))
        proc.stdin.close()

        full = []
        for line in iter(proc.stdout.readline, b''):
            decoded = line.decode("utf-8")
            full.append(decoded)
            if stream_callback:
                stream_callback(decoded)

        proc.wait(timeout=timeout)
        return "".join(full).strip()

    except subprocess.TimeoutExpired:
        proc.kill()
        return "<ERROR: Pi timeout>"
    except FileNotFoundError:
        return "<ERROR: 'pi' command not found>"
    except Exception as e:
        return f"<ERROR: {e}>"


def extract_json(text):
    """从文本中提取第一个 JSON 对象（4 种策略）"""
    text = text.strip()
    # 策略 1：全文本就是纯 JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 策略 2：Markdown 代码块 ```json ... ```
    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    # 策略 3：大括号包裹的第一个 JSON 对象
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    # 策略 4：正则扫描 score + concern（对抗严重格式不良的输出）
    try:
        score_match = re.search(r'(?:"score"|score)\s*[:\s]\s*([0-9]+(?:\.[0-9]+)?)', text)
        if score_match:
            score = float(score_match.group(1))
            score = max(0.0, min(1.0, score))
            concern = None
            cm = re.search(r'(?:"concern"|concern)\s*[:\s]\s*"([^"]*)"', text)
            if cm:
                concern = cm.group(1)
            return {"score": score, "concern": concern}
    except (ValueError, AttributeError):
        pass
    return None


def call_pi_json(prompt, system_prompt=None, tools=None, exclude_tools=None,
                 model="ollama/qwen2.5-coder:7b", provider="ollama",
                 timeout=120, retry=1):
    """调用 Pi 并期待 JSON 输出"""
    for attempt in range(retry + 1):
        raw = call_pi(prompt=prompt, system_prompt=system_prompt,
                      tools=tools, exclude_tools=exclude_tools,
                      model=model, provider=provider, timeout=timeout)
        result = extract_json(raw)
        if result is not None:
            return result
    return {"error": "Cannot parse Pi output as JSON", "raw_output": raw[:500]}
