"""Time the owner's 0–32s opening and retained walkthrough without unsupported claims."""

import json
import re
import textwrap

from scripts.prepare_video_v4 import BEATS as OLD_BEATS
from scripts.prepare_video_v4 import ENDS as OLD_ENDS
from scripts.prepare_video_v4 import OVERRIDES as OLD_OVERRIDES
from scripts.prepare_video_v4 import phrases, stamp, weight
from scripts.record_demo_scenes import VIDEO

ENDS = [8, 24, 52, 58, 64] + [end + 25 for end in OLD_ENDS[4:]]
BEATS = [
    "Universal follow-up hook",
    "Dealership context",
    "Maria example",
    "Industry proof",
    "Lead-to-offer thesis",
] + OLD_BEATS[4:]
OVERRIDES = {
    **{k + 1: v for k, v in OLD_OVERRIDES.items() if k >= 5},
    1: [
        "Every sales team has the same leak.",
        "Not bad products, not bad salespeople.",
        "Leads that go quiet, and nobody follows up in time.",
    ],
}


def main():
    paragraphs = (VIDEO / "narration-v6.txt").read_text().strip().split("\n\n")
    assert len(paragraphs) == len(ENDS) == len(BEATS)
    cues, beats = [], []
    start = 0
    for i, (text, end, label) in enumerate(zip(paragraphs, ENDS, BEATS), 1):
        chunks = OVERRIDES.get(i, phrases(text))
        weights = [weight(c) for c in chunks]
        cursor = start + 0.15
        usable = end - 0.2 - cursor - 0.07 * (len(chunks) - 1)
        for chunk, w in zip(chunks, weights):
            duration = usable * w / sum(weights)
            lines = textwrap.wrap(chunk, width=42, break_long_words=False, break_on_hyphens=False)
            assert len(lines) <= 2
            cues.append(
                {
                    "start": round(cursor, 3),
                    "end": round(cursor + duration, 3),
                    "text": "\n".join(lines),
                    "beat": i,
                }
            )
            cursor += duration + 0.07
        beats.append(
            {
                "beat": i,
                "label": label,
                "start": start,
                "end": end,
                "words": len(text.split()),
                "narration": text,
            }
        )
        start = end

    def norm(s):
        return re.sub("[^a-z0-9]", "", s.lower())

    assert norm(" ".join(c["text"] for c in cues)) == norm(" ".join(paragraphs))
    assert all(a["end"] <= b["start"] for a, b in zip(cues, cues[1:]))
    timeline = {
        "version": 6,
        "duration_seconds": 229,
        "fps": 30,
        "word_count": sum(b["words"] for b in beats),
        "caption_basis": (
            "Paced guide with dealership context and expanded Maria example. "
            "No recorded VO supplied."
        ),
        "opening_fact_corrections": [
            "Last contact seven days ago; number of calls unknown.",
            "Purchase timing is conditional on eventual purchase, "
            "not all leads or buyer decision time.",
        ],
        "beats": beats,
        "cues": cues,
    }
    (VIDEO / "timeline-v6.json").write_text(json.dumps(timeline, indent=2) + "\n")
    (VIDEO / "subtitles-v6.srt").write_text(
        "\n\n".join(
            f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}"
            for i, c in enumerate(cues, 1)
        )
        + "\n"
    )
    print(
        json.dumps(
            {
                "duration": 229,
                "words": timeline["word_count"],
                "cues": len(cues),
                "opening_stops": ENDS[:4],
            }
        )
    )


if __name__ == "__main__":
    main()
