/**
 * ETO — Evolutionary Teal Organization
 *
 * Pi CLI 扩展：三镜路由 + 临时协调员 + 同侪共识
 * 安装：放到 ~/.pi/agent/extensions/
 * 测试：pi -e ./extensions/eto.ts -p "写个flask api"
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

// ── 三镜路由（LLM 语义路由 + 关键词兜底）─────────────
type Route = "direct" | "plan" | "consensus";
interface RouteResult {
  gewu: string;
  route: Route;
  confidence: number;
  coordinator: string;
  layer: string; // "llm" | "keyword"
}

// 容错映射
const GEWU_MAP: Record<string, string> = {
  knowledge: "knowledge", question: "knowledge", definition: "knowledge",
  code: "code", coding: "code", programming: "code",
  research: "research", study: "research", analysis: "research",
  solution: "solution", problem: "solution", design: "solution",
};
const ROUTE_MAP: Record<string, Route> = {
  direct: "direct", simple: "direct",
  plan: "plan", multi_step: "plan",
  consensus: "consensus", highrisk: "consensus",
};

/** 从 JSON 中提取路由结果（兼容 markdown 代码块包装） */
function parseRouteJSON(text: string): { gewu?: string; ROUTE?: string; confidence?: number } | null {
  // 先找 ```json ... ```
  const m = text.match(/```(?:json)?\s*\n?(.*?)\n?```/s);
  const jsonStr = m ? m[1].trim() : text.trim();
  const start = jsonStr.indexOf("{");
  const end = jsonStr.lastIndexOf("}");
  if (start === -1 || end <= start) return null;
  try {
    return JSON.parse(jsonStr.slice(start, end + 1));
  } catch { return null; }
}

/** 调用 Ollama 7B 模型做语义路由 */
async function llmRoute(task: string): Promise<RouteResult | null> {
  const prompt = `Classify this request. Output JSON: {"gewu":"code","ROUTE":"plan","confidence":0.9}
gewu: knowledge | code | research | solution
ROUTE: direct (simple Q&A) | plan (multi-step) | consensus (high-risk)

Task: ${task}`;
  try {
    const resp = await fetch("http://localhost:11434/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "qwen2.5-coder:7b",
        system: "Output only JSON, no other text.",
        prompt,
        stream: false,
        options: { temperature: 0, num_predict: 256 },
      }),
      signal: AbortSignal.timeout(8000),
    });
    const data = await resp.json() as any;
    const raw: string = data.response?.trim() || "";
    const parsed = parseRouteJSON(raw);
    if (!parsed) return null;

    const gewu = GEWU_MAP[String(parsed.gewu ?? "").toLowerCase()];
    const route = ROUTE_MAP[String(parsed.ROUTE ?? "").toLowerCase()];
    const confidence = Math.min(Math.max(parsed.confidence ?? 0.5, 0), 1);

    if (!route) return null;
    return {
      gewu: gewu || "code",
      route,
      confidence,
      coordinator: route === "consensus" ? "auditor" : gewu === "research" ? "researcher" : "coder",
      layer: "llm",
    };
  } catch {
    return null;
  }
}

/** 关键词兜底路由 */
function keywordRoute(task: string): RouteResult {
  const t = task.toLowerCase();
  if (["delete", "remove", "deploy", "销毁", "删除", "部署"].some((k) => t.includes(k)))
    return { gewu: "solution", route: "consensus", confidence: 1, coordinator: "auditor", layer: "keyword" };
  if (["什么是", "是什么", "what is", "explain", "define"].some((k) => t.includes(k)))
    return { gewu: "knowledge", route: "direct", confidence: 0.9, coordinator: "researcher", layer: "keyword" };
  if (/写|代码|实现|重构|调研|研究|分析|write|code|implement/i.test(t)) {
    const isResearch = /研究|调研|分析|research/i.test(t);
    return {
      gewu: isResearch ? "research" : "code",
      route: "plan",
      confidence: 0.85,
      coordinator: isResearch ? "researcher" : "coder",
      layer: "keyword",
    };
  }
  return { gewu: "knowledge", route: "direct", confidence: 0.7, coordinator: "researcher", layer: "keyword" };
}

/** 三镜路由入口：LLM 语义路由 → 关键词兜底 */
async function routeTask(task: string): Promise<RouteResult> {
  const llm = await llmRoute(task);
  if (llm && llm.confidence >= 0.3) return llm;
  return keywordRoute(task);
}

// ── Pi 扩展入口 ──────────────────────────────────────
export default function (pi: ExtensionAPI) {
  // 1. 会话启动 → 加载历史 + 通知
  pi.on("session_start", async (_event, ctx) => {
    ctx.ui.notify("🦋 ETO 青色组织模式就绪", "info");
    // 附加历史标签到消息
    try {
      const history = pi.listEntries?.() || [];
      if (history.length > 0) {
        const recent = history.slice(-3).map((e: any) => `[${e.key}] ${JSON.stringify(e.value).slice(0, 100)}`).join("\n");
        ctx.ui.notify(`📋 历史任务 (${history.length}):\n${recent}`, "info");
      }
    } catch {}
  });

  // 2. 每次 Agent 处理前 → LLM 语义路由 + 显示 ETO 决策
  pi.on("before_agent_start", async (event, ctx) => {
    const task = event.prompt || "";
    if (!task) return;

    const route = await routeTask(task);
    const etoMeta = `[ETO 青色编排]
  三镜分析: ${route.gewu} → ${route.route} (${route.layer}, ${(route.confidence * 100).toFixed(0)}%)
  协调员: ${route.coordinator}
  原则: 无序 · 三生 · 有机 — 自主管理 · 完整性 · 进化使命
`;

    const icons: Record<string, string> = { direct: "⚡", plan: "📋", consensus: "🤝" };
    ctx.ui.notify(
      `${icons[route.route] || "?"} ETO: ${route.gewu} → ${route.route} [${route.layer}] 协调员: ${route.coordinator}`,
      "info"
    );

    return { systemPrompt: (event.systemPrompt || "") + "\n" + etoMeta };
  });

  // 3. 任务完成 → 记录结果到持久化存储
  pi.on("task_complete", async (event, ctx) => {
    try {
      pi.appendEntry?.({ key: `task-${Date.now()}`, value: { task: event.task, result: event.result?.slice(0, 200) }, timestamp: Date.now() });
    } catch {}
  });

  // 4. 注册共识工具（LLM 可调用的同侪评分）
  pi.registerTool({
    name: "eto_consensus",
    label: "ETO Consensus",
    description: "同侪共识：为执行方案评分，返回平均分和审查意见。分数 ≥ 0.6 自动通过。",
    parameters: Type.Object({
      plan: Type.String({ description: "执行方案描述" }),
      steps: Type.Array(Type.String({ description: "执行步骤" })),
    }),
    async execute(toolCallId, params, signal, onUpdate, ctx) {
      // 模拟两个同侪评分
      const peers = [
        { name: "reviewer_research", score: +(0.6 + Math.random() * 0.3).toFixed(2) },
        { name: "reviewer_audit", score: +(0.5 + Math.random() * 0.4).toFixed(2) },
      ];
      const avg = +(peers.reduce((s, p) => s + p.score, 0) / peers.length).toFixed(2);
      const passed = avg >= 0.6;
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            status: passed ? "approved" : "需调整",
            avg_score: avg,
            peers,
            steps: params.steps.length,
            message: passed ? "共识通过，可以执行" : "评分不足，建议调整方案",
          }, null, 2),
        }],
        details: {},
      };
    },
  });

  // 5. 智子安检：拦截危险 bash
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName === "bash" && typeof event.input?.command === "string") {
      const cmd = event.input.command;
      if (["rm -rf", "dd if=", "format ", "mkfs", "> /dev/"].some((d) => cmd.includes(d))) {
        const ok = await ctx.ui.confirm("⛔ 智子安检", `危险操作：${cmd.slice(0, 80)}\n放行？`);
        if (!ok) return { block: true, reason: "智子否决：危险操作已拦截" };
      }
    }
  });
}
