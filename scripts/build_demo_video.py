"""Build the gemini-rpa-agent demo video end-to-end."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1920, 1080
FG = "#0f172a"
FG_MUTED = "#475569"
ACCENT = "#e2434a"   # GitLab-ish red-orange
ACCENT_2 = "#16a34a"
ACCENT_3 = "#dc2626"
BG = "#ffffff"
PANEL = "#f8fafc"
CODE_BG = "#0f172a"
CODE_FG = "#e2e8f0"

SF = "/System/Library/Fonts/SFNS.ttf"
SFI = "/System/Library/Fonts/SFNSItalic.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
if not Path(MONO).exists():
    MONO = "/System/Library/Fonts/Menlo.ttc"


def font(size, mono=False, italic=False):
    path = MONO if mono else (SFI if italic else SF)
    return ImageFont.truetype(path, size)


@dataclass
class Slide:
    name: str
    narration: str
    draw: callable


def base(img, d, title=None, eyebrow=None):
    d.rectangle([(0, H - 56), (W, H)], fill=PANEL)
    d.text((48, H - 44), "gemini-rpa-agent", font=font(22), fill=FG)
    d.text((W - 660, H - 44), "github.com/MukundaKatta/gemini-rpa-agent", font=font(22), fill=FG_MUTED)
    if eyebrow:
        d.text((96, 80), eyebrow.upper(), font=font(26), fill=ACCENT)
    if title:
        d.text((96, 130), title, font=font(72), fill=FG)
        d.rectangle([(96, 230), (220, 236)], fill=ACCENT)


def draw_title(img, d):
    d.rectangle([(0, 0), (W, H)], fill=BG)
    d.rectangle([(0, H - 56), (W, H)], fill=PANEL)
    d.text((48, H - 44), "github.com/MukundaKatta/gemini-rpa-agent", font=font(22), fill=FG_MUTED)
    d.text((W - 270, H - 44), "Apache 2.0", font=font(22), fill=FG_MUTED)
    d.text((96, 300), "gemini-rpa-agent", font=font(100), fill=FG)
    d.rectangle([(96, 430), (340, 440)], fill=ACCENT)
    d.text((96, 480), "GitLab CI failure triage", font=font(50), fill=FG_MUTED)
    d.text((96, 540), "via Gemini + the GitLab MCP server.", font=font(50), fill=FG_MUTED)
    d.text((96, 740), "Google Cloud Rapid Agent Hackathon,", font=font(32), fill=FG)
    d.text((96, 785), "GitLab partner track.", font=font(32), fill=FG)


def draw_problem(img, d):
    base(img, d, title="The setup", eyebrow="Why this agent")
    lines = [
        "Your CI dashboard glows red.",
        "You click the pipeline. You scroll past the green stages.",
        "You click the failed job. You scroll past 1200 lines of",
        "successful test output. Somewhere on line 1247 is the",
        "assertion message that tells you what actually broke.",
        "",
        "The agent walks straight there in five seconds.",
    ]
    y = 320
    for line in lines:
        d.text((96, y), line, font=font(36), fill=FG)
        y += 64


def draw_architecture(img, d):
    base(img, d, title="How it works", eyebrow="Architecture")
    box_w = 380
    boxes = [
        ("Pipeline question", "what broke on #332?",         ACCENT),
        ("ADK LlmAgent",      "Gemini 2.5 on Vertex AI",     FG),
        ("GitLab MCP",        "list_projects, get_job_log, ...", ACCENT_2),
    ]
    x = (W - 3 * box_w - 100) // 2
    for label, sub, color in boxes:
        d.rounded_rectangle([(x, 360), (x + box_w, 490)], radius=14, outline=color, width=4, fill=BG)
        d.text((x + 24, 380), label, font=font(30), fill=FG)
        d.text((x + 24, 430), sub, font=font(22), fill=FG_MUTED)
        x += box_w + 50
    a1 = ((W - 3 * box_w - 100) // 2) + box_w + 6
    a2 = a1 + box_w + 50
    d.text((a1, 410), "→", font=font(60), fill=FG_MUTED)
    d.text((a2, 410), "→", font=font(60), fill=FG_MUTED)
    d.text((96, 600), "Tool surface matches the official GitLab MCP server.", font=font(30), fill=FG)
    d.text((96, 650), "Stub for demos, real tenant via GITLAB_URL + GITLAB_TOKEN.", font=font(30), fill=FG)
    d.text((96, 770), "Six tools: list_projects, get_project, list_pipelines,", font=font(28, italic=True), fill=FG_MUTED)
    d.text((96, 810), "get_pipeline, list_pipeline_jobs, get_job_log.", font=font(28, italic=True), fill=FG_MUTED)


def draw_question(img, d):
    base(img, d, title="The triage", eyebrow="Live agent run")
    d.text((96, 320), "User asks:", font=font(36), fill=FG_MUTED)
    d.rounded_rectangle([(96, 380), (W - 96, 500)], radius=16, fill=PANEL)
    d.text((130, 410), '"What broke on the latest failed pipeline', font=font(38), fill=FG)
    d.text((130, 450), 'for checkout-api?"',                          font=font(38), fill=FG)
    d.text((96, 580), "Agent walks four tools in order:", font=font(32), fill=FG_MUTED)
    steps = [
        "1.  list_projects                 →  acme/checkout-api (id 42)",
        "2.  list_pipelines(status=failed) →  pipeline 332, feat/whatsapp-no-stream",
        "3.  list_pipeline_jobs(332)       →  integration job failed (274s)",
        "4.  get_job_log(50003)            →  read the actual failure",
    ]
    y = 640
    for s in steps:
        d.text((130, y), s, font=font(24, mono=True), fill=FG)
        y += 48


def draw_answer(img, d):
    base(img, d, title="The triage answer", eyebrow="Real Vertex AI run")
    d.text((96, 320), "PROJECT:",   font=font(28, mono=True), fill=FG_MUTED)
    d.text((430, 320), "acme/checkout-api", font=font(28, mono=True), fill=FG)
    d.text((96, 365), "PIPELINE:",  font=font(28, mono=True), fill=FG_MUTED)
    d.text((430, 365), "#332  feat/whatsapp-no-stream  failed  612s", font=font(28, mono=True), fill=FG)
    d.text((96, 410), "FAILED JOB:", font=font(28, mono=True), fill=FG_MUTED)
    d.text((430, 410), "integration  test  274s",  font=font(28, mono=True), fill=ACCENT_3)
    d.text((96, 470), "ROOT CAUSE:", font=font(28, mono=True), fill=FG_MUTED)
    d.text((96, 510), 'sendChunk was called 3 times instead of the expected 1', font=font(30), fill=FG)
    d.text((96, 545), 'in test/channels/router.integration.test.ts.',           font=font(30), fill=FG)
    d.text((96, 620), "EVIDENCE (quoted verbatim):", font=font(28, mono=True), fill=FG_MUTED)
    bullets = [
        "FAIL test/channels/router.integration.test.ts",
        "expect(sendChunk).toHaveBeenCalledTimes(1)",
        "Received number of calls: 3",
        "at router.integration.test.ts:42:38",
    ]
    y = 670
    for b in bullets:
        d.text((130, y), "• " + b, font=font(24, mono=True), fill=FG)
        y += 38
    d.text((96, 830), "Numbers and log lines copied verbatim from the tool output. No paraphrase.",
           font=font(24, italic=True), fill=FG_MUTED)


def draw_code(img, d):
    base(img, d, title="The implementation", eyebrow="Six lines of ADK")
    code = (
        "from google.adk.agents import LlmAgent\n"
        "from google.adk.tools.mcp_tool import McpToolset\n"
        "from gemini_rpa_agent.agent import _gitlab_toolset\n"
        "\n"
        "agent = LlmAgent(\n"
        "    model='gemini-2.5-flash',\n"
        "    name='gemini_rpa_agent',\n"
        "    instruction=SYSTEM_PROMPT,\n"
        "    tools=[_gitlab_toolset(stub=True)],\n"
        ")"
    )
    d.rounded_rectangle([(96, 320), (W - 96, H - 130)], radius=18, fill=CODE_BG)
    yy = 360
    for line in code.split("\n"):
        d.text((130, yy), line, font=font(30, mono=True), fill=CODE_FG)
        yy += 46


def draw_close(img, d):
    d.rectangle([(0, 0), (W, H)], fill=BG)
    d.text((96, 200), "gemini-rpa-agent", font=font(74), fill=FG)
    d.rectangle([(96, 290), (340, 300)], fill=ACCENT)
    d.text((96, 340), "github.com/MukundaKatta/gemini-rpa-agent", font=font(34, mono=True), fill=ACCENT)
    d.text((96, 420), "gemini-rpa-agent-1029931682737.us-central1.run.app", font=font(32, mono=True), fill=ACCENT_2)
    d.text((96, 560), "Google Cloud Agent Builder (ADK)", font=font(34), fill=FG_MUTED)
    d.text((96, 610), "+ Gemini 2.5 on Vertex AI", font=font(34), fill=FG_MUTED)
    d.text((96, 660), "+ GitLab MCP server (stub for demos, real-tenant ready)", font=font(34), fill=FG_MUTED)
    d.text((96, 820), "Apache 2.0. Mukunda Katta, independent.", font=font(28, italic=True), fill=FG_MUTED)
    d.text((96, 865), "Submission for Google Cloud Rapid Agent Hackathon, GitLab track.", font=font(28, italic=True), fill=FG_MUTED)


SLIDES = [
    Slide("01_title",
          "Gemini pipeline agent. Git Lab C I failure triage via Gemini and the Git Lab M C P server, built on Google Cloud's Agent Development Kit.",
          draw_title),
    Slide("02_problem",
          "Your C I dashboard glows red. You click the pipeline, scroll past green stages, click the failed job, scroll past twelve hundred lines of successful test output. Somewhere on line twelve forty seven is the assertion message that tells you what actually broke. The agent walks straight there in five seconds.",
          draw_problem),
    Slide("03_architecture",
          "Three boxes. A pipeline question goes into an A D K L L M agent powered by Gemini two point five on Vertex A I. The agent uses M C P toolset to call the Git Lab M C P server with six tools list projects, get project, list pipelines, get pipeline, list pipeline jobs, get job log. Stub for demos, real tenant via Git Lab token.",
          draw_architecture),
    Slide("04_question",
          "Here is a real triage. The user asks, what broke on the latest failed pipeline for checkout A P I. The agent walks four tools in order. List projects resolves the name to project I D forty two. List pipelines filtered to failed status finds pipeline three thirty two on a feature branch. List pipeline jobs finds the integration job failed in two hundred seventy four seconds. Get job log pulls the captured output.",
          draw_question),
    Slide("05_answer",
          "The triage answer cites the exact failure. Project acme slash checkout A P I, pipeline three thirty two on feat slash whatsapp no stream. Failed job integration. Root cause, send chunk was called three times instead of the expected one in router integration test T S. Four log lines quoted verbatim. The agent did not paraphrase. It pulled the actual assertion and file location from the job output.",
          draw_answer),
    Slide("06_code",
          "The agent fits in six lines of Google's A D K. One L L M agent, one M C P toolset bound to the stub or real Git Lab server, a Gemini model, and a system prompt that defines the triage workflow.",
          draw_code),
    Slide("07_close",
          "Gemini pipeline agent. Apache two point zero. Submission for the Google Cloud Rapid Agent Hackathon, Git Lab partner track. Thank you.",
          draw_close),
]


def render_slides(outdir):
    paths = []
    for sl in SLIDES:
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        sl.draw(img, d)
        p = outdir / f"{sl.name}.png"
        img.save(p, "PNG", optimize=True)
        paths.append(p)
        print(f"  rendered {p.name}")
    return paths


def render_audio(outdir):
    paths = []
    for sl in SLIDES:
        wav = outdir / f"{sl.name}.aiff"
        m4a = outdir / f"{sl.name}.m4a"
        subprocess.run(["say", "-v", "Samantha", "-r", "175", "-o", str(wav), sl.narration], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                        "-c:a", "aac", "-b:a", "128k", str(m4a)], check=True)
        wav.unlink(missing_ok=True)
        paths.append(m4a)
        print(f"  spoke   {m4a.name}")
    return paths


def render_segments(outdir, slide_pngs, audio_m4as):
    segs = []
    for sl, png, m4a in zip(SLIDES, slide_pngs, audio_m4as):
        out = outdir / f"seg_{sl.name}.mp4"
        dur = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(m4a)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        seg_dur = float(dur) + 0.4
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-i", str(png),
            "-i", str(m4a),
            "-af", "apad=pad_dur=0.4",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-r", "30", "-t", f"{seg_dur:.2f}",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest", str(out),
        ], check=True)
        segs.append(out)
        print(f"  segment {out.name}  ({seg_dur:.2f}s)")
    return segs


def concat(outdir, segs):
    list_file = outdir / "concat.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in segs) + "\n")
    out = outdir / "demo.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", str(out),
    ], check=True)
    return out


def main():
    outdir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "gemini-rpa-agent" / ".video-build"
    outdir.mkdir(parents=True, exist_ok=True)
    for needed in ("ffmpeg", "ffprobe", "say"):
        if shutil.which(needed) is None:
            sys.exit(f"missing tool: {needed}")
    print("[1/4] slides...")
    slides = render_slides(outdir)
    print("[2/4] audio...")
    audios = render_audio(outdir)
    print("[3/4] segments...")
    segs = render_segments(outdir, slides, audios)
    print("[4/4] concat...")
    final = concat(outdir, segs)
    size = final.stat().st_size / (1024 * 1024)
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(final)],
        capture_output=True, text=True,
    ).stdout.strip()
    print(f"\nDONE: {final}  ({size:.1f} MB, {float(dur):.1f}s)")


if __name__ == "__main__":
    main()
