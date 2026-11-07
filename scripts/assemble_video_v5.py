"""Assemble the 197-second universal-hook cut with script-led scene stops."""

# ruff: noqa: E501
import argparse
import json
import subprocess

from scripts.assemble_demo_video import FFMPEG, ROOT, VIDEO, probe

WORK = ROOT / ".local/video-prep/edit-v5"


def run(args):
    subprocess.run([FFMPEG, "-v", "error", "-y", *args], check=True)


def encode(name, source, duration, offset=0, still=False, chapter=None, chapter_offset=0, tempo=1):
    out = WORK / f"{name}.mp4"
    inputs = ["-loop", "1", "-framerate", "30"] if still else ["-ss", str(offset)]
    vf = f"setpts={tempo}*(PTS-STARTPTS),fps=30,scale=1920:1080:flags=lanczos,tpad=stop_mode=clone:stop_duration={duration},setsar=1,format=yuv420p"
    filters = ["-vf", vf]
    if chapter:
        layer = (
            f"setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={duration + chapter_offset},"
            f"trim=start={chapter_offset}:duration={duration},setpts=PTS-STARTPTS,"
            "chromakey=0xFF00FF:0.25:0.12"
        )
        filters = [
            "-i",
            str(VIDEO / "cards-v3" / f"lower-{chapter}.mp4"),
            "-filter_complex",
            f"[0:v]{vf}[base];[1:v]{layer}[label];[base][label]overlay=0:0:shortest=1,tpad=stop_mode=clone:stop_duration=1,format=yuv420p[out]",
            "-map",
            "[out]",
        ]
    run(
        [
            *inputs,
            "-i",
            str(source),
            *filters,
            "-frames:v",
            str(round(duration * 30)),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-threads",
            "4",
            str(out),
        ]
    )
    return out


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    shots, segments = [], []
    position = 0

    def add(name, source, duration, label, **kwargs):
        nonlocal position
        segments.append(encode(name, source, duration, **kwargs))
        shots.append(
            {
                "shot": name,
                "label": label,
                "start": position,
                "end": position + duration,
                "source": str(source.relative_to(ROOT)),
                "source_options": kwargs,
            }
        )
        position += duration

    cards = VIDEO / "cards-v5"
    add("01-hook", cards / "hook.mp4", 8, "Universal follow-up hook")
    add(
        "02-maria",
        VIDEO / "scenes/v3-maria.mp4",
        12,
        "Maria example with verified last-contact history",
        offset=2,
    )
    add("03-proof", cards / "proof.mp4", 6, "Dated industry benchmark: 42.7% and 61.2%")
    add("04-thesis", cards / "thesis.mp4", 6, "Connect lead to offer in time")
    previous = json.loads((VIDEO / "shot-manifest-v4.json").read_text())
    for shot in previous["shots"]:
        if shot["start"] >= 39:
            add(
                "carry-" + shot["shot"],
                ROOT / shot["source"],
                shot["end"] - shot["start"],
                shot["label"],
                **shot["source_options"],
            )
    assert position == 197
    (WORK / "concat.txt").write_text("".join(f"file '{s}'\n" for s in segments))
    (VIDEO / "shot-manifest-v5.json").write_text(
        json.dumps(
            {
                "duration_seconds": position,
                "fps": 30,
                "shots": shots,
                "provenance": "Adds original editorial hook/stat/thesis graphics and reuses accepted v4 walkthrough sources; no new review, inference, customer send or UI manipulation.",
            },
            indent=2,
        )
        + "\n"
    )
    finish()


def ass_stamp(seconds):
    cs = round(seconds * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def finish():
    raw = VIDEO / "salesdesk-v5-nosubs.mp4"
    run(
        [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(WORK / "concat.txt"),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(raw),
        ]
    )
    timeline = json.loads((VIDEO / "timeline-v5.json").read_text())
    header = (VIDEO / "subtitles.ass").read_text().split("[Events]")[0]
    events = [
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for cue in timeline["cues"]:
        text = cue["text"].replace("\n", r"\N")
        events.append(
            f"Dialogue: 0,{ass_stamp(cue['start'])},{ass_stamp(cue['end'])},Default,,0,0,56,,{text}"
        )
    ass = VIDEO / "subtitles-v5.ass"
    ass.write_text(header + "\n".join(events) + "\n")
    final = VIDEO / "salesdesk-v5.mp4"
    run(
        [
            "-i",
            str(raw),
            "-vf",
            f"subtitles='{ass}':fontsdir='{VIDEO / 'fonts'}'",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-threads",
            "4",
            "-movflags",
            "+faststart",
            str(final),
        ]
    )
    review()


def review():
    manifest = json.loads((VIDEO / "shot-manifest-v5.json").read_text())
    selected = [s for s in manifest["shots"] if s["shot"] not in ("carry-12", "carry-17")]
    font = VIDEO / "fonts/Inter-SemiBold.ttf"
    for i, shot in enumerate(selected, 1):
        moment = shot["start"] + min(
            shot["end"] - shot["start"] - 0.5, max(1.5, (shot["end"] - shot["start"]) / 2)
        )
        run(
            [
                "-ss",
                str(moment),
                "-i",
                str(VIDEO / "salesdesk-v5.mp4"),
                "-frames:v",
                "1",
                str(VIDEO / "_review" / f"v5-shot-{shot['shot']}.png"),
            ]
        )
        run(
            [
                "-ss",
                str(moment),
                "-i",
                str(VIDEO / "salesdesk-v5.mp4"),
                "-vf",
                f"scale=480:270,drawtext=fontfile='{font}':text='{shot['start'] // 60}m{shot['start'] % 60:02}s - {shot['end'] // 60}m{shot['end'] % 60:02}s':fontcolor=white:fontsize=18:box=1:boxcolor=0x142e34:x=w-tw-8:y=h-th-8",
                "-frames:v",
                "1",
                str(WORK / f"review-{i:02}.png"),
            ]
        )
    run(
        [
            "-framerate",
            "1",
            "-start_number",
            "1",
            "-i",
            str(WORK / "review-%02d.png"),
            "-vf",
            f"tile=4x{(len(selected) + 3) // 4}:nb_frames={len(selected)}:padding=8:margin=8:color=0x142e34",
            "-frames:v",
            "1",
            str(VIDEO / "_review/v5-contact.png"),
        ]
    )
    checks = {}
    for name in ("salesdesk-v5-nosubs.mp4", "salesdesk-v5.mp4"):
        info = probe(VIDEO / name)
        stream = info["streams"][0]
        assert len(info["streams"]) == 1 and stream["codec_name"] == "h264"
        assert (
            stream["width"] == 1920
            and stream["height"] == 1080
            and stream["r_frame_rate"] == "30/1"
        )
        assert int(stream["nb_frames"]) == 5910 and float(info["format"]["duration"]) == 197
        checks[name] = {
            "duration_seconds": 197,
            "frames": 5910,
            "video": "1920x1080 30fps H.264",
            "audio": "none",
            "bytes": int(info["format"]["size"]),
        }
    (VIDEO / "v5-export-check.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finish-only", action="store_true")
    parser.add_argument("--review-only", action="store_true")
    args = parser.parse_args()
    if args.review_only:
        review()
    elif args.finish_only:
        finish()
    else:
        main()
