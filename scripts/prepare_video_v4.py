"""Build the approved conversational script's scene timings and guide captions."""

import json
import re
import textwrap

from scripts.record_demo_scenes import VIDEO

ENDS = [
    11,
    22,
    27,
    39,
    47,
    56,
    58,
    74,
    82,
    94,
    104,
    110,
    112,
    123,
    133,
    147,
    160,
    176,
    188,
    200,
    204,
]
BEATS = [
    "Maria's enquiry",
    "The available alternative",
    "Group scale",
    "The manager's review",
    "SalesDesk introduction",
    "Parallel review",
    "Sandy introduction",
    "Lead risk",
    "Inventory search",
    "Match scoring",
    "Qwen brief",
    "Recorded completion",
    "Maria result",
    "Match explanation",
    "Timeline explanation",
    "Draft explanation",
    "Manager approval",
    "Group totals",
    "Vultr architecture",
    "Morning workflow",
    "Close",
]


OVERRIDES = {
    4: [
        "A manager could work through those leads,",
        "check which cars are still available,",
        "and look for alternatives.",
        "But that means bringing together information",
        "from several stores, every morning.",
    ],
    9: [
        "It then checks the available inventory:",
        "117 cars at Sandy",
        "and more than sixteen hundred at nearby sister stores.",
    ],
    11: [
        "Qwen, running on Vultr Serverless Inference,",
        "uses those checked results to write Sandy's morning brief",
        "and three follow-up drafts for its priority leads.",
    ],
    12: ["The recorded review finishes across all 24 stores", "in two minutes and seven seconds."],
    15: [
        "The manager can see her original enquiry,",
        "when she was last contacted,",
        "and when the blue car sold, all in the same view.",
    ],
    16: [
        "Below that is a draft message mentioning the available silver RAV4",
        "and asking about her 2017 Honda CR-V trade-in.",
        "The salesperson has the context and a message",
        "ready to review before contacting her.",
    ],
    20: [
        "SalesDesk gives your team a practical starting point each morning:",
        "which customers to follow up with,",
        "which cars to offer, and a draft they can work from.",
    ],
}


def stamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def weight(text):
    # Numerals such as 117 take several spoken words, even though they occupy
    # only one token in the written script. Do not rush those caption beats.
    spoken_units = {
        "375": 5,
        "117": 4,
        "1,007": 4,
        "24": 2,
        "74": 2,
        "98": 2,
        "100": 2,
        "2017": 2,
        "$3.4": 3,
        "RAV4": 2,
        "CR-V": 3,
    }
    total = 0
    for word in text.split():
        core = word.strip(",.;:!?")
        total += spoken_units.get(core, max(1, len(word) / 7))
        total += 0.8 if re.search(r"[.!?]$", word) else 0
        total += 0.3 if re.search(r"[,;:]$", word) else 0
    return total


def phrases(text):
    clauses = re.split(r"(?<=[.!?])\s+|(?<=,)\s+", text)
    chunks = []
    for clause in clauses:
        words = clause.split()
        while words:
            chosen = []
            while words and len(" ".join(chosen + [words[0]])) <= 78:
                chosen.append(words.pop(0))
            chunks.append(" ".join(chosen))
    # Combine short adjacent clauses where a comfortable two-line caption permits.
    result = []
    for chunk in chunks:
        if result and len(result[-1]) < 32 and len(result[-1] + " " + chunk) <= 78:
            result[-1] += " " + chunk
        else:
            result.append(chunk)
    return result


def main():
    paragraphs = (VIDEO / "narration-v4.txt").read_text().strip().split("\n\n")
    assert len(paragraphs) == len(ENDS) == len(BEATS)
    cues, beats = [], []
    start = 0
    for i, (paragraph, end, label) in enumerate(zip(paragraphs, ENDS, BEATS), 1):
        chunks = OVERRIDES.get(i, phrases(paragraph))
        weights = [weight(c) for c in chunks]
        cursor = start + 0.2
        speech_end = end - 0.3
        usable = speech_end - cursor - 0.09 * (len(chunks) - 1)
        for chunk, w in zip(chunks, weights):
            duration = usable * w / sum(weights)
            lines = textwrap.wrap(chunk, width=42, break_long_words=False, break_on_hyphens=False)
            assert len(lines) <= 2, lines
            cues.append(
                {
                    "start": round(cursor, 3),
                    "end": round(cursor + duration, 3),
                    "text": "\n".join(lines),
                    "beat": i,
                }
            )
            cursor += duration + 0.09
        beats.append(
            {
                "beat": i,
                "label": label,
                "start": start,
                "end": end,
                "words": len(paragraph.split()),
                "narration": paragraph,
            }
        )
        start = end

    def normalized(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())

    assert normalized(" ".join(c["text"] for c in cues)) == normalized(" ".join(paragraphs))
    assert all(a["end"] <= b["start"] for a, b in zip(cues, cues[1:]))
    timeline = {
        "version": 4,
        "duration_seconds": ENDS[-1],
        "fps": 30,
        "word_count": sum(b["words"] for b in beats),
        "caption_basis": "Paced guide for the approved script; no recorded voice track supplied.",
        "beats": beats,
        "cues": cues,
    }
    (VIDEO / "timeline-v4.json").write_text(json.dumps(timeline, indent=2) + "\n")
    (VIDEO / "subtitles-v4.srt").write_text(
        "\n\n".join(
            f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}"
            for i, c in enumerate(cues, 1)
        )
        + "\n"
    )
    print(
        json.dumps(
            {
                "duration": start,
                "words": timeline["word_count"],
                "cues": len(cues),
                "max_characters_per_second": round(
                    max(len(c["text"].replace("\n", " ")) / (c["end"] - c["start"]) for c in cues),
                    2,
                ),
            }
        )
    )


if __name__ == "__main__":
    main()
