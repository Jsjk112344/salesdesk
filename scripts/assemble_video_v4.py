"""Assemble the conversational 204-second cut with script-led scene stops."""

# ruff: noqa: E501
import argparse
import json
import subprocess

from scripts.assemble_demo_video import FFMPEG, ROOT, VIDEO, probe

WORK = ROOT / ".local/video-prep/edit-v4"


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

    old = VIDEO / "cards-v3"
    cards = VIDEO / "cards-v4"
    scenes = VIDEO / "scenes"
    stills = VIDEO / "stills"
    add("01a", old / "opening.mp4", 3, "Maria's enquiry")
    add("01b", scenes / "v3-maria.mp4", 19, "Original interest and available alternative", offset=2)
    add("02", old / "scale.mp4", 5, "Group scale")
    add("03", cards / "manual.mp4", 12, "The manager's morning review")
    add("04", cards / "title.mp4", 8, "SalesDesk introduction")
    add("05", old / "fanout.mp4", 9, "Parallel review explainer", chapter=1, tempo=0.75)
    add("06", scenes / "v3-run.mp4", 2, "Real Group mid-run", offset=8, chapter=1, chapter_offset=9)
    add("07", scenes / "v3-run.mp4", 16, "Sandy lead risk", offset=29, chapter=2)
    add("08", scenes / "v3-run.mp4", 8, "Local and sister-store inventory", offset=41, chapter=3)
    add(
        "09",
        stills / "v3-match-score.png",
        12,
        "Match scoring",
        still=True,
        chapter=3,
        chapter_offset=8,
    )
    add("10", scenes / "v3-run.mp4", 10, "Qwen brief and three drafts", offset=60, chapter=4)
    add("11", old / "skip.mp4", 6, "Recorded run completion")
    add("12", scenes / "v3-maria.mp4", 2, "Maria result introduction", offset=2)
    add("13", stills / "v3-match-score.png", 11, "Maria model, trim, score and colour", still=True)
    add("14", scenes / "v3-maria.mp4", 10, "Maria enquiry and contact timeline", offset=2)
    add("15", scenes / "v3-maria.mp4", 14, "Maria draft and trade-in explanation", offset=10)
    add("16", stills / "v3-approve-queue.png", 6, "Ranked manager queue", still=True)
    add("17", scenes / "v3-approve.mp4", 3, "Actual approval click", offset=0.5)
    add("18", scenes / "v3-ready.mp4", 4, "Ready tasks and draft downloads")
    add("19", cards / "matched.mp4", 6, "Matched lead total")
    add("20", cards / "gross.mp4", 10, "Estimated gross associated with matches")
    add("21", old / "architecture.mp4", 12, "Vultr and validation")
    add("22", cards / "workflow.mp4", 12, "Practical morning workflow")
    add("23", cards / "end.mp4", 4, "Enterprise analyst close")
    assert position == 204
    (WORK / "concat.txt").write_text("".join(f"file '{s}'\n" for s in segments))
    (VIDEO / "shot-manifest-v4.json").write_text(
        json.dumps(
            {
                "duration_seconds": position,
                "fps": 30,
                "shots": shots,
                "provenance": "Reuses accepted v3 public footage and original editorial cards; no new review, inference, customer send or UI manipulation.",
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
    raw = VIDEO / "salesdesk-v4-nosubs.mp4"
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
    timeline = json.loads((VIDEO / "timeline-v4.json").read_text())
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
    ass = VIDEO / "subtitles-v4.ass"
    ass.write_text(header + "\n".join(events) + "\n")
    final = VIDEO / "salesdesk-v4.mp4"
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
    manifest = json.loads((VIDEO / "shot-manifest-v4.json").read_text())
    selected = [s for s in manifest["shots"] if s["shot"] not in ("01a", "12", "17")]
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
                str(VIDEO / "salesdesk-v4.mp4"),
                "-frames:v",
                "1",
                str(VIDEO / "_review" / f"v4-shot-{shot['shot']}.png"),
            ]
        )
        run(
            [
                "-ss",
                str(moment),
                "-i",
                str(VIDEO / "salesdesk-v4.mp4"),
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
            str(VIDEO / "_review/v4-contact.png"),
        ]
    )
    checks = {}
    for name in ("salesdesk-v4-nosubs.mp4", "salesdesk-v4.mp4"):
        info = probe(VIDEO / name)
        stream = info["streams"][0]
        assert len(info["streams"]) == 1 and stream["codec_name"] == "h264"
        assert (
            stream["width"] == 1920
            and stream["height"] == 1080
            and stream["r_frame_rate"] == "30/1"
        )
        assert int(stream["nb_frames"]) == 6120 and float(info["format"]["duration"]) == 204
        checks[name] = {
            "duration_seconds": 204,
            "frames": 6120,
            "video": "1920x1080 30fps H.264",
            "audio": "none",
            "bytes": int(info["format"]["size"]),
        }
    (VIDEO / "v4-export-check.json").write_text(json.dumps(checks, indent=2) + "\n")
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
