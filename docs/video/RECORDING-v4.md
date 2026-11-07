# SalesDesk v4 recording hand-off

The current cut follows the approved conversational rewrite: **3:24 (204 seconds)**,
1920×1080, 30 fps, H.264, silent. The earlier v3 cuts remain unchanged.

- [Captioned review](salesdesk-v4.mp4) · [Clean video](salesdesk-v4-nosubs.mp4)
- [Contact sheet](_review/v4-contact.png) · [Scene stops](video-plan-v4.md)
- [Clean VO script](narration-v4.txt) · [SRT captions](subtitles-v4.srt)
- [Narration/cue timeline](timeline-v4.json) · [Shot sources](shot-manifest-v4.json)
- [Source review facts](recording-facts-v3.json) · [Export checks](v4-export-check.json)
- [Earlier v3 hand-off](RECORDING-v3.md)

## Voiceover

Record the approved script below as one natural read. The cut has breathing space
at paragraph boundaries. Maria is explained throughout 1:50–2:27: match breakdown,
contact timeline and draft. There is no long silent SMS hold in this version.

Import `salesdesk-v4-nosubs.mp4`, your voice recording and `subtitles-v4.srt` into
your editor. The 55 cues are a paced guide, not alignment to recorded audio.
Adjust the cues and holds to the actual delivery before the final audio export.
Captions stay bottom centre, below Maria's SMS. Chapter pills stay top left.
No music, sound effects or synthesized voice are included.

## Clean script

Nine days ago, Maria asked about a blue Toyota RAV4 Hybrid. The dealership last contacted her seven days ago. Since then, that car has sold.

There's still a silver RAV4 Hybrid available at the same dealership. It's been sitting there for 74 days, but nobody has followed up with Maria about it.

Across 24 stores, there are over a thousand leads that need attention.

A manager could work through those leads, check which cars are still available, and look for alternatives. But that means bringing together information from several stores, every morning.

SalesDesk is your AI enterprise sales analyst. It does that review overnight and prepares the follow-ups for your team.

At 2 AM, it starts reviewing each store's leads and inventory. Six stores run in parallel, in isolated sandboxes on Vultr.

Let's look at Sandy.

SalesDesk reviews its 375 open leads and flags 40 that need attention. Twenty-five have gone at least three days without contact. Others are waiting on a car that has sold, or have an appointment that needs following up.

It then checks the available inventory: 117 cars at Sandy and more than sixteen hundred at nearby sister stores.

Each potential match is scored against what the customer asked for, including the model, trim, budget and mileage. Cars that have been in stock longer get extra priority.

Qwen, running on Vultr Serverless Inference, uses those checked results to write Sandy's morning brief and three follow-up drafts for its priority leads.

The recorded review finishes across all 24 stores in two minutes and seven seconds.

Here's Maria's result.

The silver RAV4 is the same model and trim she originally asked about. It scores 98 out of 100, with the colour difference shown in the breakdown.

The manager can see her original enquiry, when she was last contacted, and when the blue car sold, all in the same view.

Below that is a draft message mentioning the available silver RAV4 and asking about her 2017 Honda CR-V trade-in. The salesperson has the context and a message ready to review before contacting her.

By the morning, Sandy's manager has a ranked queue of 40 follow-ups. They can review individual drafts or approve the queue together, then download the tasks and drafts for their salespeople.

Across the group, 1,007 at-risk leads have been matched to a car in stock. The estimated gross associated with those matches is about $3.4 million. Managers can use that view to decide where their teams should focus.

The scheduler and analysis jobs run on a Vultr VM. Qwen runs on Vultr Serverless Inference, and its output is validated before it reaches the approval queue.

SalesDesk gives your team a practical starting point each morning: which customers to follow up with, which cars to offer, and a draft they can work from.

SalesDesk. Your AI enterprise sales analyst.

## Rebuild

```bash
uv run python -m scripts.prepare_video_v4
uv run python -m scripts.render_video_v4
uv run python -m scripts.assemble_video_v4
```

These commands use existing accepted public footage, original cards and the
approved script. They make no model calls and schedule no review. The fixed
camera and settled cursor from the v3 polish are retained. Only the fan-out motion
graphic is shortened; app footage stays at normal speed. Holds use actual frames.

## Final audio and submission

After aligning the voice and captions, export the final cut with clear audio.
If the recorded voice already matches these timings, you can add it to the captioned
cut without re-encoding its video:

```bash
ffmpeg -i docs/video/salesdesk-v4.mp4 -i voiceover.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k \
  -af apad -t 204 -movflags +faststart SalesDesk-final.mp4
```

Check the actual signed-in form's limits, upload video/slides and submit by the
owner's **Sunday November 8, 2026, 16:00 ET target**. Save the receipt. No upload,
submission or recorded voice is claimed here.
