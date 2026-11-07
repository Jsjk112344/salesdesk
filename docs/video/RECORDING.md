# SalesDesk v5 recording hand-off

Current cut: **3:17 (197 seconds)**, H.264, 1920×1080, 30 fps, silent.

- [Captioned video](salesdesk-v5.mp4) · [Clean video](salesdesk-v5-nosubs.mp4)
- [Contact sheet](_review/v5-contact.png) · [Opening and scene stops](video-plan-v5.md)
- [Narration](narration-v5.txt) · [SRT](subtitles-v5.srt) · [Cue timeline](timeline-v5.json)
- [Industry source notes](SOURCES-v5.md) · [Dated evidence](industry-sources-v5.json)
- [Shot sources](shot-manifest-v5.json) · [Export checks](v5-export-check.json)
- [Previous v4 hand-off](RECORDING-v4.md)

## Read and alignment

The opening stops are **0:08 / 0:20 / 0:26 / 0:32**: universal hook, Maria,
industry proof, then thesis. Start the enterprise introduction at 0:32. The opening
is brisker; use a conversational pace for the retained walkthrough. The exact
spoken script is below. Dates and publisher names on the stat card are not spoken.

The two industry figures apply to qualified dealer website leads and, for the
purchase window, only those that eventually purchased. Maria's number of calls is
unknown; her verified last contact was seven days ago. No extra call history,
industry lost-dollar figure, customer send or proven recovery is invented.

The 54 captions are paced guides, not alignment to recorded audio. Record the VO,
then match the SRT to the actual delivery before the final audio export. Maria's
match, timeline and draft are explained throughout 1:43–2:20; there is no long
silent SMS hold. Captions sit below the message. Camera/cursor remain settled.

## Clean script

Every sales team has the same leak. Not bad products, not bad salespeople. Leads that go quiet, and nobody follows up in time.

Take Maria. She wanted a blue RAV4 Hybrid nine days ago. Her last contact was a week ago. That car sold. A silver alternative sat at the same dealership for 74 days.

Nearly half of qualified leads are mishandled. Most eventual buyers purchase within three days.

Sales slip away when nobody connects the lead to the right offer in time.

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
uv run python -m scripts.prepare_video_v5
uv run python -m scripts.render_video_v5
uv run python -m scripts.assemble_video_v5
```

These commands use existing accepted v3/v4 source footage and original graphics.
No new review, inference, app deployment or customer contact is triggered. Original
execution evidence remains in `recording-facts-v3.json`; its 127.493-second review
is shortened explicitly by the retained “2 min 7 sec” card. It is separate from
this edit's running time. Industry evidence is separate from the synthetic sample.

## Final audio and submission

The exports contain no recorded/synthesised voice, music or effects. If the voice
recording already matches this guide, it can be added without re-encoding video:

```bash
ffmpeg -i docs/video/salesdesk-v5.mp4 -i voiceover.wav \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k \
  -af apad -t 197 -movflags +faststart SalesDesk-final.mp4
```

Otherwise align the voice and captions with the clean video in your editor first.
Check the actual signed-in submission form, upload the final video/slides, and
submit by the owner's **Sunday November 8, 2026, 16:00 ET target**. No upload,
submission or receipt is claimed here. Prior v4/v3 files remain available.
