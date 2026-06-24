# 死胡同台账 — ETO 项目

> 每条记录一条已验证走不通的路，防止跨会话重走。
> 格式：`## [日期] 标题 — 操作类型`

## 2026-06-23 TUI 复制问题 — 重写已知行为

**路径：** tui.py → tui_textual.py → 6 轮重写
**触发条件：** 进入 Textual 全屏后试图用 Ctrl+C 复制文本失败，认为是 bug
**真实原因：** 所有全屏 TUI（vim/htop/lazygit）都需要 **Shift + 鼠标选择** 才能复制。Textual 8.x 不例外。装 `pyperclip` 后才支持 Ctrl+C
**下游成本：** ~2 小时重写 6 版
**正确做法：** 先搜 "Textual copy paste" 看 FAQ，不自己踩

## 2026-06-23 入口文件冲突 — 诊断不全

**路径：** bin/eto → bin/eto.cmd → npm/eto.cmd
**触发条件：** `where eto` 看到一条路径就以为够了，没意识到 Windows 上 `.cmd` 优先级高于无扩展名文件
**真实原因：** 3 个入口并存，`.cmd` 先于无扩展名生效
**下游成本：** ~30 分钟查入口
**正确做法：** `where eto` 列全，`cmd /c "where eto"` 确认优先级，删多余入口

## 2026-06-23 YAML 转义坑 — 隐式假设未验证

**路径：** CLAUDE.md / skills 文件
**触发条件：** 在 YAML 双引号字符串里写 `\s` 正则
**真实原因：** YAML 双引号字符串会做转义处理，`\s` 不是合法 YAML 转义序列。要用单引号字符串或 `\s` → 写为 `\\s`
**下游成本：** ~15 分钟调试 YAML 解析错误
**正确做法：** 敲入 YAML 的转义规则：双引号里 `\n` `\t` `\\` 是合法的，`\s` `\d` 不是；正则用单引号

## 2026-06-23 RichLog.write() API 误用 — 假设错误

**路径：** tui_textual.py
**触发条件：** `self.rich_log.write(Text("a"), Text("b"))` 期望多参数拼接
**真实原因：** `RichLog.write()` 只接受一个 renderable 参数。多个文本要合并：`write(Text.assemble("a", "b"))`
**下游成本：** ~20 分钟
**正确做法：** 先 `pip list | grep rich` 看版本，再看 RichLog API 签名

## 2026-06-23 Textual Theme 注册 — API 版本漂移

**路径：** tui_textual.py
**触发条件：** 用 `App.register_theme()` 类方法调用
**真实原因：** Textual 8.x 中 `register_theme` 是实例方法（`self.register_theme()`）不是类方法
**下游成本：** ~10 分钟
**正确做法：** 读 `textual/app.py` 签名确认方法归属

## 2026-06-23 settings.local.json allow 列表冲突 — 配置漂移

**路径：** .claude/settings.local.json + .claude/settings.json
**触发条件：** 两个配置文件里 `permissions.mode` 和 `permissions.allow` 同时存在
**真实原因：** `bypassPermissions` 模式忽略 `allow` 列表，但两个文件声明不一致会冲突
**下游成本：** ~20 分钟
**正确做法：** 删一处的 permissions 段，保持单一来源
