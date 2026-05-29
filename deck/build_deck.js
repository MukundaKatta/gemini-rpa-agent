// UiPath AgentHack 2026 deck for gemini-rpa-agent.
// Run: NODE_PATH=$(npm root -g) node deck/build_deck.js
const pptxgen = require("pptxgenjs");

const p = new pptxgen();
p.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
p.author = "Mukunda Katta";
p.title = "gemini-rpa-agent - UiPath AgentHack 2026";

const C = {
  navy: "0B1733",
  navy2: "16245A",
  ice: "F4F6FB",
  white: "FFFFFF",
  orange: "F86A1E",
  gem: "4285F4",
  ink: "0F172A",
  muted: "5B6478",
  green: "12B886",
  line: "D7DEEA",
  codebg: "0E1C42",
};
const F = { head: "Georgia", body: "Calibri" };
const W = 13.3, H = 7.5;
const M = 0.7;

const shadow = () => ({ type: "outer", color: "0B1733", blur: 9, offset: 3, angle: 135, opacity: 0.13 });

function header(slide, kicker, title) {
  slide.background = { color: C.ice };
  slide.addShape(p.shapes.RECTANGLE, { x: M, y: 0.62, w: 0.13, h: 0.92, fill: { color: C.orange } });
  slide.addText(kicker.toUpperCase(), { x: M + 0.28, y: 0.58, w: 11.8, h: 0.32, fontFace: F.body, fontSize: 12.5, color: C.orange, bold: true, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: M + 0.28, y: 0.88, w: 12.0, h: 0.72, fontFace: F.head, fontSize: 29, color: C.ink, bold: true, margin: 0 });
}

function chip(slide, x, y, text, fg, bg) {
  const w = 0.32 + text.length * 0.105;
  slide.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.4, rectRadius: 0.2, fill: { color: bg } });
  slide.addText(text, { x, y, w, h: 0.4, fontFace: F.body, fontSize: 12, color: fg, bold: true, align: "center", valign: "middle", margin: 0 });
  return w;
}

// ---------- Slide 1: Title (dark) ----------
{
  const s = p.addSlide();
  s.background = { color: C.navy };
  // motif: stacked translucent blocks top-right
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 10.4, y: -0.7, w: 3.6, h: 3.6, rectRadius: 0.3, fill: { color: C.orange, transparency: 78 }, rotate: 18 });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 11.2, y: 4.6, w: 3.2, h: 3.2, rectRadius: 0.3, fill: { color: C.gem, transparency: 80 }, rotate: 12 });
  s.addText("UIPATH AGENTHACK 2026", { x: M, y: 1.5, w: 10, h: 0.4, fontFace: F.body, fontSize: 14, color: C.orange, bold: true, charSpacing: 4, margin: 0 });
  s.addText("gemini-rpa-agent", { x: M, y: 1.95, w: 11.5, h: 1.1, fontFace: F.head, fontSize: 56, color: C.white, bold: true, margin: 0 });
  s.addText("An RPA failure-diagnosis agent that runs inside UiPath Maestro.", { x: M, y: 3.15, w: 11.0, h: 0.6, fontFace: F.body, fontSize: 22, color: C.ice, margin: 0 });
  s.addText("Ask what broke. Get the failing step, the verbatim error, and the fix, in seconds.", { x: M, y: 3.8, w: 11.0, h: 0.5, fontFace: F.body, fontSize: 16, color: "9FB0D4", italic: true, margin: 0 });
  let cx = M;
  ["Maestro BPMN track", "Gemini 2.5 + ADK", "UiPath LLM Gateway", "Apache-2.0"].forEach((t) => {
    cx += chip(s, cx, 4.75, t, C.white, C.navy2) + 0.22;
  });
  s.addText("Mukunda Katta  ·  solo", { x: M, y: 6.7, w: 8, h: 0.4, fontFace: F.body, fontSize: 13, color: "8595BC", margin: 0 });
}

// ---------- Slide 2: Problem ----------
{
  const s = p.addSlide();
  header(s, "The problem", "The diagnosis is what burns the night, not the fix");
  const steps = [
    "Workflow fails overnight",
    "On-call gets paged",
    "Click 5 layers to the failing step",
    "Copy the error payload",
    "Paste a known fix",
  ];
  const n = steps.length, gap = 0.34, bw = (W - 2 * M - (n - 1) * gap) / n, by = 2.5, bh = 1.7;
  steps.forEach((t, i) => {
    const x = M + i * (bw + gap);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: by, w: bw, h: bh, rectRadius: 0.08, fill: { color: C.white }, line: { color: C.line, width: 1 }, shadow: shadow() });
    s.addShape(p.shapes.OVAL, { x: x + bw / 2 - 0.28, y: by + 0.22, w: 0.56, h: 0.56, fill: { color: i === n - 1 ? C.green : C.navy2 } });
    s.addText(String(i + 1), { x: x + bw / 2 - 0.28, y: by + 0.22, w: 0.56, h: 0.56, fontFace: F.head, fontSize: 20, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(t, { x: x + 0.12, y: by + 0.92, w: bw - 0.24, h: 0.7, fontFace: F.body, fontSize: 13.5, color: C.ink, align: "center", valign: "top", margin: 0 });
    if (i < n - 1) s.addText("→", { x: x + bw - 0.02, y: by + bh / 2 - 0.3, w: gap + 0.04, h: 0.6, fontFace: F.body, fontSize: 22, color: C.orange, bold: true, align: "center", valign: "middle", margin: 0 });
  });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.05, w: W - 2 * M, h: 1.25, rectRadius: 0.1, fill: { color: "FDEDE3" } });
  s.addText([
    { text: "The fix is almost always copy-pasteable. ", options: { bold: true, color: C.ink } },
    { text: "Finding it is what costs the night. ", options: { color: C.ink } },
    { text: "gemini-rpa-agent walks the same tools an on-call walks, but in seconds, with the canonical fix already in hand.", options: { color: C.muted } },
  ], { x: M + 0.35, y: 5.05, w: W - 2 * M - 0.7, h: 1.25, fontFace: F.body, fontSize: 16, valign: "middle", margin: 0 });
}

// ---------- Slide 3: What it does ----------
{
  const s = p.addSlide();
  header(s, "What it does", "One question in, a five-section diagnosis out");
  // prompt card (left)
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y: 2.35, w: 4.5, h: 3.4, rectRadius: 0.1, fill: { color: C.navy }, shadow: shadow() });
  s.addText("YOU ASK", { x: M + 0.35, y: 2.65, w: 3.8, h: 0.3, fontFace: F.body, fontSize: 12, color: C.orange, bold: true, charSpacing: 2, margin: 0 });
  s.addText("“Workflow wf-onboarding-pro-2026-001 failed at 09:14 UTC. What broke, and how do I fix it?”", { x: M + 0.35, y: 3.05, w: 3.85, h: 2.4, fontFace: F.body, fontSize: 18, color: C.white, italic: true, valign: "top", margin: 0 });
  s.addText("→", { x: 5.35, y: 3.7, w: 0.8, h: 0.7, fontFace: F.body, fontSize: 30, color: C.orange, bold: true, align: "center", valign: "middle", margin: 0 });
  // 5-section list (right)
  const secs = [
    ["ANSWER", "which workflow, which step, what broke", C.navy2],
    ["EVIDENCE", "verbatim error payload + step IDs, no paraphrasing", C.green],
    ["ROOT CAUSE", "one-sentence diagnosis", C.navy2],
    ["REMEDIATION", "copy-paste fix: old value, new value, retry command", C.navy2],
    ["NEXT STEP", "one follow-up check", C.navy2],
  ];
  const rx = 6.3, rw = W - M - rx, rh = 0.66, ry0 = 2.35, rg = 0.18;
  secs.forEach((d, i) => {
    const y = ry0 + i * (rh + rg);
    s.addShape(p.shapes.RECTANGLE, { x: rx, y, w: 0.1, h: rh, fill: { color: d[2] } });
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: rx + 0.1, y, w: rw - 0.1, h: rh, rectRadius: 0.05, fill: { color: C.white }, line: { color: C.line, width: 1 } });
    s.addText(d[0], { x: rx + 0.3, y, w: 2.0, h: rh, fontFace: F.body, fontSize: 13.5, color: d[2] === C.green ? C.green : C.ink, bold: true, valign: "middle", margin: 0 });
    s.addText(d[1], { x: rx + 2.25, y, w: rw - 2.4, h: rh, fontFace: F.body, fontSize: 12.5, color: C.muted, valign: "middle", margin: 0 });
  });
}

// ---------- Slide 4: Architecture ----------
{
  const s = p.addSlide();
  header(s, "Architecture", "The agent runs through the UiPath Platform, end to end");
  const boxes = [
    ["UiPath Maestro", "BPMN Service Task starts and waits for the agent"],
    ["ADK LlmAgent", "Gemini 2.5 Flash, uipath_entrypoint.main"],
    ["UiPath LLM Gateway", "UiPathGemini routes every Gemini call"],
    ["RPA MCP server", "stub today, real orchestrator one env var away"],
  ];
  const n = boxes.length, gap = 0.55, bw = (W - 2 * M - (n - 1) * gap) / n, by = 2.7, bh = 2.0;
  boxes.forEach((b, i) => {
    const x = M + i * (bw + gap);
    const accent = i === 2 ? C.orange : C.navy2;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: by, w: bw, h: bh, rectRadius: 0.08, fill: { color: C.white }, line: { color: accent, width: i === 2 ? 2.5 : 1.2 }, shadow: shadow() });
    s.addShape(p.shapes.RECTANGLE, { x, y: by, w: bw, h: 0.12, fill: { color: accent } });
    s.addText(b[0], { x: x + 0.18, y: by + 0.35, w: bw - 0.36, h: 0.6, fontFace: F.head, fontSize: 16, color: C.ink, bold: true, align: "center", valign: "top", margin: 0 });
    s.addText(b[1], { x: x + 0.2, y: by + 1.0, w: bw - 0.4, h: 0.9, fontFace: F.body, fontSize: 12, color: C.muted, align: "center", valign: "top", margin: 0 });
    if (i < n - 1) s.addText("→", { x: x + bw - 0.06, y: by + bh / 2 - 0.3, w: gap + 0.12, h: 0.6, fontFace: F.body, fontSize: 24, color: C.orange, bold: true, align: "center", valign: "middle", margin: 0 });
  });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.35, w: W - 2 * M, h: 1.0, rectRadius: 0.1, fill: { color: "EAF0FB" } });
  s.addText([
    { text: "Why this satisfies the rule. ", options: { bold: true, color: C.gem } },
    { text: "Orchestration and agent logic run through the UiPath Platform: Maestro invokes the published agent, and every Gemini call passes through the UiPath LLM Gateway, not direct Vertex.", options: { color: C.ink } },
  ], { x: M + 0.35, y: 5.35, w: W - 2 * M - 0.7, h: 1.0, fontFace: F.body, fontSize: 14.5, valign: "middle", margin: 0 });
}

// ---------- Slide 5: 4 MCP tools ----------
{
  const s = p.addSlide();
  header(s, "Tool surface", "Four read-only RPA tools, walked end to end");
  const tools = [
    ["list_workflows(active_only)", "Workflows plus last-run status. Finds the run whose status is failed."],
    ["get_workflow_run(run_id)", "Full step-by-step trace. Identifies the single failing step."],
    ["get_step_output(run_id, step_id)", "Verbatim error payload from the failing step."],
    ["suggest_retry(run_id)", "Canonical fix plus the retry command."],
  ];
  const gx = 0.5, gy = 0.45, cw = (W - 2 * M - gx) / 2, ch = 1.55, x0 = M, y0 = 2.45;
  tools.forEach((t, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = x0 + col * (cw + gx), y = y0 + row * (ch + gy);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, rectRadius: 0.08, fill: { color: C.white }, line: { color: C.line, width: 1 }, shadow: shadow() });
    s.addShape(p.shapes.OVAL, { x: x + 0.3, y: y + 0.32, w: 0.5, h: 0.5, fill: { color: C.navy2 } });
    s.addText(String(i + 1), { x: x + 0.3, y: y + 0.32, w: 0.5, h: 0.5, fontFace: F.head, fontSize: 18, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(t[0], { x: x + 1.0, y: y + 0.28, w: cw - 1.2, h: 0.5, fontFace: "Consolas", fontSize: 14.5, color: C.orange, bold: true, valign: "middle", margin: 0 });
    s.addText(t[1], { x: x + 1.0, y: y + 0.78, w: cw - 1.25, h: 0.65, fontFace: F.body, fontSize: 13, color: C.muted, valign: "top", margin: 0 });
  });
  s.addText("n8n-style MCP surface. One env var (RPA_API_URL, RPA_API_TOKEN) swaps the stub for a real orchestrator: UiPath, n8n, or self-hosted.", { x: M, y: 6.55, w: W - 2 * M, h: 0.5, fontFace: F.body, fontSize: 13, color: C.muted, italic: true, align: "center", margin: 0 });
}

// ---------- Slide 6: Verbatim evidence (dark) ----------
{
  const s = p.addSlide();
  s.background = { color: C.navy };
  s.addShape(p.shapes.RECTANGLE, { x: M, y: 0.62, w: 0.13, h: 0.92, fill: { color: C.orange } });
  s.addText("THE CONTRACT", { x: M + 0.28, y: 0.58, w: 11.8, h: 0.32, fontFace: F.body, fontSize: 12.5, color: C.orange, bold: true, charSpacing: 3, margin: 0 });
  s.addText("Verbatim, never paraphrased", { x: M + 0.28, y: 0.88, w: 12, h: 0.7, fontFace: F.head, fontSize: 29, color: C.white, bold: true, margin: 0 });
  // code card
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y: 2.2, w: W - 2 * M, h: 2.45, rectRadius: 0.1, fill: { color: C.codebg }, line: { color: "24386F", width: 1 }, shadow: shadow() });
  s.addText([
    { text: "EVIDENCE:", options: { color: C.green, bold: true, breakLine: true } },
    { text: '  {"error":"channel_not_found","ts":"1747559640.000100","channel_attempted":"#new-hires"}', options: { color: "CFE3FF", breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "REMEDIATION:", options: { color: C.orange, bold: true, breakLine: true } },
    { text: '  replace channel name "#new-hires" with channel ID C09NEW123HIRE, then retry the run', options: { color: "CFE3FF" } },
  ], { x: M + 0.4, y: 2.5, w: W - 2 * M - 0.8, h: 2.4, fontFace: "Consolas", fontSize: 15.5, valign: "top", margin: 0, lineSpacingMultiple: 1.25 });
  s.addText([
    { text: "The end-to-end smoke test re-runs the agent and asserts the exact string ", options: { color: C.ice } },
    { text: '"error":"channel_not_found"', options: { color: C.green, bold: true } },
    { text: " appears in EVIDENCE, character for character.", options: { color: C.ice } },
  ], { x: M, y: 5.0, w: W - 2 * M, h: 1.0, fontFace: F.body, fontSize: 16, italic: true, valign: "middle", margin: 0 });
}

// ---------- Slide 7: Why it fits ----------
{
  const s = p.addSlide();
  header(s, "Why it fits", "Built for the Maestro BPMN track");
  const pts = [
    ["Inside the platform", "Runs end to end in UiPath: a Maestro BPMN Service Task invokes the agent, and the LLM Gateway is on the hot path for every call."],
    ["A 1:1 track fit", "A BPMN Service Task calling a coded agent is exactly the track brief. Maestro Case is the documented fallback."],
    ["Stub-first design", "Judges reproduce the full demo with zero orchestrator setup. One env var flips the stub to a live orchestrator."],
  ];
  const n = pts.length, gap = 0.45, cw = (W - 2 * M - (n - 1) * gap) / n, y = 2.5, ch = 3.4;
  pts.forEach((d, i) => {
    const x = M + i * (cw + gap);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, rectRadius: 0.1, fill: { color: C.white }, line: { color: C.line, width: 1 }, shadow: shadow() });
    s.addShape(p.shapes.OVAL, { x: x + 0.4, y: y + 0.4, w: 0.7, h: 0.7, fill: { color: C.orange } });
    s.addText(String(i + 1), { x: x + 0.4, y: y + 0.4, w: 0.7, h: 0.7, fontFace: F.head, fontSize: 24, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(d[0], { x: x + 0.4, y: y + 1.35, w: cw - 0.8, h: 0.6, fontFace: F.head, fontSize: 18, color: C.ink, bold: true, valign: "top", margin: 0 });
    s.addText(d[1], { x: x + 0.4, y: y + 1.95, w: cw - 0.8, h: 1.3, fontFace: F.body, fontSize: 13.5, color: C.muted, valign: "top", margin: 0 });
  });
}

// ---------- Slide 8: What's next ----------
{
  const s = p.addSlide();
  header(s, "What's next", "Where gemini-rpa-agent goes from here");
  const items = [
    ["Test Cloud surface", "A second MCP surface for the third AgentHack track: list_test_runs, get_fragile_tests, suggest_test_fix."],
    ["Human Task approval", "A Maestro Human Task fork after diagnosis, so a person approves or rejects the fix before it auto-applies."],
    ["Watch-mode daemon", "Poll list_workflows(active_only) and only invoke Gemini on a new failed run, which pays for itself in gateway cost."],
  ];
  const y0 = 2.45, rh = 1.2, rg = 0.28;
  items.forEach((d, i) => {
    const y = y0 + i * (rh + rg);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y, w: W - 2 * M, h: rh, rectRadius: 0.08, fill: { color: C.white }, line: { color: C.line, width: 1 }, shadow: shadow() });
    s.addShape(p.shapes.RECTANGLE, { x: M, y, w: 0.13, h: rh, fill: { color: C.gem } });
    s.addText(d[0], { x: M + 0.45, y, w: 3.3, h: rh, fontFace: F.head, fontSize: 17, color: C.ink, bold: true, valign: "middle", margin: 0 });
    s.addText(d[1], { x: M + 3.9, y, w: W - 2 * M - 4.2, h: rh, fontFace: F.body, fontSize: 13.5, color: C.muted, valign: "middle", margin: 0 });
  });
}

// ---------- Slide 9: Close (dark) ----------
{
  const s = p.addSlide();
  s.background = { color: C.navy };
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: -0.8, y: 4.9, w: 4.0, h: 4.0, rectRadius: 0.3, fill: { color: C.orange, transparency: 80 }, rotate: 16 });
  s.addText("Diagnosis in seconds.\nThe fix already quoted.\nEvery call through the UiPath LLM Gateway.", { x: M, y: 2.2, w: 11.6, h: 2.4, fontFace: F.head, fontSize: 34, color: C.white, bold: true, lineSpacingMultiple: 1.15, margin: 0 });
  s.addText("github.com/MukundaKatta/gemini-rpa-agent", { x: M, y: 4.85, w: 11, h: 0.5, fontFace: "Consolas", fontSize: 16, color: C.orange, margin: 0 });
  let cx = M;
  ["Maestro BPMN", "Gemini 2.5", "ADK", "MCP", "Apache-2.0"].forEach((t) => {
    cx += chip(s, cx, 5.6, t, C.white, C.navy2) + 0.22;
  });
}

p.writeFile({ fileName: "/Users/ubl/gemini-rpa-agent/deck/gemini-rpa-agent-uipath-deck.pptx" }).then((f) => console.log("WROTE", f));
