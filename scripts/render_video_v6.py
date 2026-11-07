"""Render the universal hook, dated industry proof and lead-to-offer thesis."""

# ruff: noqa: E501
import argparse
import asyncio
import json
import subprocess

from playwright.async_api import async_playwright

from scripts.render_demo_assets import CSS, LOGO, ROOT, VIDEO


async def main(only=None):
    evidence = json.loads((VIDEO / "industry-sources-v5.json").read_text())
    timeline = json.loads((VIDEO / "timeline-v6.json").read_text())
    hook_cues = [c for c in timeline["cues"] if c["beat"] == 2]
    out = VIDEO / "cards-v6"
    out.mkdir(exist_ok=True)
    work = ROOT / ".local/video-prep/cards-v6"
    work.mkdir(parents=True, exist_ok=True)
    hook_titles = [
        "Let’s look at a<br>car dealership.",
        "Leads in the CRM.<br>Stock tracked separately.",
        "A customer’s first choice sells.<br>An alternative goes unnoticed.",
    ]
    style = (
        CSS
        + """
section{background:#142e34;color:#f5f7f6;padding:90px}.brand{font-size:42px;margin-bottom:65px}.mark{width:60px;height:60px;border-radius:15px}.mark svg{width:42px;height:42px}h1{font-size:88px;line-height:1.15}.motion{opacity:var(--alpha,1);transform:translateY(var(--rise,0px))}.context{font-size:28px;color:#b2cdc9;margin-bottom:40px}.stats{display:flex;gap:90px;align-items:flex-start;justify-content:center}.stat{width:650px}.stat strong{font-size:142px;color:#83dfbd;display:block;letter-spacing:-5px}.stat p{font-size:36px;line-height:1.4;max-width:630px;margin:22px auto 0}.source{position:absolute;left:90px;right:90px;bottom:190px;font-size:22px;color:#b2cdc9;line-height:1.55;text-align:center}
"""
    )
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        for name, duration in [("context", 16)]:
            if only and name not in only:
                continue
            if name == "proof":
                first, second = evidence["claims"]
                body = f'<div class="context">Industry benchmark · Qualified dealership website leads</div><div class="stats"><div class="stat"><strong>{first["value_percent"]}%</strong><p>of qualified leads<br>were mishandled</p></div><div class="stat"><strong>{second["value_percent"]}%</strong><p>of eventual buyers purchased<br>within 3 days of their inquiry</p></div></div>'
                footer = '<div class="source">Source: Foureyes · 2026 Automotive Dealer Benchmarks Report<br>Published April 22, 2026 · January–December 2025 website activity · foureyes.io</div>'
            else:
                title = (
                    hook_titles[0]
                    if name == "context"
                    else "Connect the lead to the<br>right offer in time."
                )
                body = f'<h1 id="title">{title}</h1>'
                footer = ""
            html = (
                '<!doctype html><meta charset="utf-8"><style>'
                + style
                + '</style><section class="center"><div class="motion"><div class="brand">'
                + LOGO
                + "<b>SalesDesk:</b></div>"
                + body
                + "</div>"
                + footer
                + "</section>"
            )
            path = VIDEO / f"card-v6-{name}.html"
            path.write_text(html)
            await page.goto(path.as_uri())
            await page.evaluate("document.fonts.ready")
            frames = work / name
            frames.mkdir(exist_ok=True)
            for frame in range(duration * 30):
                t = frame / 30
                local = t
                if name == "context":
                    index = 0 if t < 3 else (1 if t < 9 else 2)
                    local = t - [0, 3, 9][index]
                    await page.locator("#title").evaluate(
                        "(e,text)=>e.innerHTML=text", hook_titles[index]
                    )
                await page.evaluate(
                    "t=>{let a=Math.min(1,t/.25);document.documentElement.style.setProperty('--alpha',a);document.documentElement.style.setProperty('--rise',(8*(1-a))+'px')}",
                    local,
                )
                await page.screenshot(path=str(frames / f"{frame:03}.png"))
            subprocess.run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-y",
                    "-framerate",
                    "30",
                    "-i",
                    str(frames / "%03d.png"),
                    "-frames:v",
                    str(duration * 30),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "fast",
                    "-crf",
                    "18",
                    "-threads",
                    "4",
                    "-pix_fmt",
                    "yuv420p",
                    str(out / f"{name}.mp4"),
                ],
                check=True,
            )
            print(name, flush=True)
        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+")
    args = parser.parse_args()
    asyncio.run(main(args.only))
