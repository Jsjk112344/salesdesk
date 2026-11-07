"""Render plain explanatory cards matching the approved conversational narration."""

# ruff: noqa: E501
import argparse
import asyncio
import json
import subprocess

from playwright.async_api import async_playwright

from scripts.render_demo_assets import CSS, LOGO, ROOT, VIDEO


async def main(only=None):
    out = VIDEO / "cards-v4"
    out.mkdir(exist_ok=True)
    work = ROOT / ".local/video-prep/cards-v4"
    work.mkdir(parents=True, exist_ok=True)
    facts = json.loads((VIDEO / "recording-facts-v3.json").read_text())
    cards = {
        "manual": (
            "The morning review",
            ["Review open leads", "Check available cars", "Prepare follow-ups"],
            12,
        ),
        "title": (
            "Your AI enterprise<br>sales analyst",
            ["Reviews overnight. Prepares the follow-ups."],
            8,
        ),
        "matched": (
            f"{facts['group']['matched_in_stock']:,}",
            ["at-risk leads matched to a car in stock"],
            7,
        ),
        "gross": (
            f"${facts['group']['recoverable_gross']:,.0f}",
            ["estimated gross associated with those matches"],
            9,
        ),
        "workflow": (
            "Ready for the morning",
            ["Customers to follow up with", "Available cars to offer", "Drafts to review"],
            12,
        ),
        "end": ("Your AI enterprise<br>sales analyst", [], 4),
    }
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        for name, (title, lines, duration) in cards.items():
            if only and name not in only:
                continue
            listing = "".join(
                f'<div class="item" data-i="{i}">{line}</div>' for i, line in enumerate(lines)
            )
            footer = ""
            footer_line = ""
            if name in ("workflow", "end"):
                footer = '<div class="urls">salesdesk.149.28.51.139.sslip.io<br>github.com/Jsjk112344/salesdesk</div>'
                footer_line = (
                    "<footer>Sample dealer group · SalesDesk drafts; people send.</footer>"
                )
            html = (
                '<!doctype html><meta charset="utf-8"><style>'
                + CSS
                + """
section{background:#142e34;color:#f5f7f6;padding:80px}.brand{font-size:48px;margin-bottom:55px}.mark{width:64px;height:64px;border-radius:16px}.mark svg{width:46px;height:46px}h1{font-size:88px;line-height:1.16}.items{display:flex;gap:30px;justify-content:center;margin-top:55px}.item{font-size:32px;line-height:1.4;padding:24px 30px;border:1px solid #4e686d;border-radius:14px;max-width:520px}.urls{font-size:25px;line-height:1.7;margin-top:38px}footer{position:absolute;bottom:155px;font-size:22px;color:#b2cdc9}.body{opacity:var(--alpha,1);transform:translateY(var(--rise,0px))}
"""
                + '</style><section class="center"><div class="body"><div class="brand">'
                + LOGO
                + "<b>SalesDesk:</b></div><h1>"
                + title
                + '</h1><div class="items">'
                + listing
                + "</div>"
                + footer
                + "</div>"
                + footer_line
                + "</section>"
            )
            if name in ("matched", "gross", "title"):
                html = html.replace(
                    "</style>",
                    ".items .item{border:0;padding:0;max-width:1250px;font-size:40px}</style>",
                )
            if name in ("matched", "gross"):
                html = html.replace("<h1>", '<h1 id="count">', 1)
            path = VIDEO / f"card-v4-{name}.html"
            path.write_text(html)
            await page.goto(path.as_uri())
            await page.evaluate("document.fonts.ready")
            frames = work / name
            frames.mkdir(exist_ok=True)
            for frame in range(31):
                await page.evaluate(
                    "t=>{document.documentElement.style.setProperty('--alpha',Math.min(1,t/.3));document.documentElement.style.setProperty('--rise',(8*(1-Math.min(1,t/.3)))+'px')}",
                    frame / 30,
                )
                if name in ("matched", "gross"):
                    await page.evaluate(
                        "({t,n,money})=>document.querySelector('#count').innerText=(money?'$':'')+Math.round(n*(1-Math.pow(1-Math.min(1,t),3))).toLocaleString('en-US')",
                        {
                            "t": frame / 30,
                            "n": facts["group"][
                                "matched_in_stock" if name == "matched" else "recoverable_gross"
                            ],
                            "money": name == "gross",
                        },
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
                    "-vf",
                    f"tpad=stop_mode=clone:stop_duration={duration},format=yuv420p",
                    "-t",
                    str(duration),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "fast",
                    "-crf",
                    "18",
                    "-threads",
                    "4",
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
