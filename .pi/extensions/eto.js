/**
 * ETO — Evolutionary Teal Organization
 *
 * Pi CLI 扩展：三镜路由 + 临时协调员 + 同侪共识
 *
 * 安装：放到 ~/.pi/agent/extensions/ 或 .pi/extensions/
 * 或：pi -e ./extensions/eto.ts
 */
import { Type } from "typebox";
const CONSENSUS_KW = [
    "delete", "remove", "destroy", "deploy",
    "删除", "移除", "销毁", "部署",
];
const DEFINE_KW = ["什么是", "是什么", "what is", "explain", "define"];
function routeTask(task) {
    const t = task.toLowerCase();
    // Layer 0: 安全关键词
    if (CONSENSUS_KW.some((k) => t.includes(k)))
        return { gewu: "solution", route: "consensus", confidence: 1 };
    // 定义/解释 → direct
    if (DEFINE_KW.some((k) => t.includes(k)))
        return { gewu: "knowledge", route: "direct", confidence: 0.9 };
    // 编码/研究 → plan
    if (/写|代码|实现|重构|调研|研究|分析|write|code|implement/i.test(t))
        return { gewu: t.includes("研究") || t.includes("调研") ? "research" : "code", route: "plan", confidence: 0.85 };
    return { gewu: "knowledge", route: "direct", confidence: 0.7 };
}
// ── Agent 选举（匹配度）─────────────────────────────
const KEYWORD_MAP = {
    coder: ["write", "code", "implement", "build", "create", "refactor", "debug", "写", "编码", "代码"],
    researcher: ["research", "analyze", "search", "study", "report", "调研", "研究", "分析"],
    auditor: ["review", "audit", "check", "verify", "safe", "审查", "审计", "检查"],
};
function electCoordinator(task) {
    const t = task.toLowerCase();
    let best = "coder";
    let bestScore = 0;
    for (const [agent, kws] of Object.entries(KEYWORD_MAP)) {
        const score = kws.filter((k) => t.includes(k)).length;
        if (score > bestScore) {
            bestScore = score;
            best = agent;
        }
    }
    return best;
}
// ── Pi 扩展入口 ──────────────────────────────────────
export default function (pi) {
    // 1. 注册 eto_route 工具（LLM 可调用的三镜分析）
    pi.registerTool({
        name: "eto_route",
        label: "ETO Route",
        description: "三镜分析：分析用户任务并返回路由决策 (direct/plan/consensus)",
        parameters: Type.Object({
            task: Type.String({ description: "用户的任务描述" }),
        }),
        async execute(toolCallId, params, signal, onUpdate, ctx) {
            const result = routeTask(params.task);
            return {
                content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
                details: {},
            };
        },
    });
    // 2. 在每次 Agent 启动前注入 ETO 上下文
    pi.on("before_agent_start", async (event, ctx) => {
        const task = event.messages?.[0]?.content?.[0]?.text;
        if (!task)
            return;
        // 三镜路由
        const route = routeTask(task);
        const coordinator = electCoordinator(task);
        // 构造 ETO 上下文注入到 system prompt
        const etoContext = `
[ETO 青色组织编排]
  三镜分析: ${route.gewu} → ${route.route} (conf: ${route.confidence})
  临时协调员: ${coordinator}
  原则: "无序 · 三生 · 有机" — 自主管理 · 完整性 · 进化使命
`;
        return {
            systemPrompt: (event.systemPrompt || "") + "\n" + etoContext,
        };
    });
    // 3. 拦截危险工具调用（智子安检）
    pi.on("tool_call", async (event, ctx) => {
        const dangerous = ["rm -rf", "format", "dd if="];
        const cmd = event.input?.command || "";
        if (dangerous.some((d) => cmd.includes(d))) {
            const ok = await ctx.ui.confirm("智子安检", `⛔ 危险操作：${cmd}\n是否放行？`);
            if (!ok)
                return { block: true, reason: "智子否决：危险操作已拦截" };
        }
    });
    // 4. 会话启动时加载历史
    pi.on("session_start", async (event, ctx) => {
        ctx.ui.notify("ETO 青色组织模式已加载", "info");
    });
}
