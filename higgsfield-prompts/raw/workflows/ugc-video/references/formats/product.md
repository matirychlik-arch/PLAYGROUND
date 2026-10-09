Read the ugc-video entrypoint and shared execution references first. This file
contains only the selected format; shared duration, cleanup, transport and failure
contracts apply to every stage.

# UGC product video

Produce one hosted 9:16 MP4. The product is the hero; any visible person stays
auxiliary and silent. Each board is a 21:9 sheet of four vertical 9:16 slots;
one Seedance clip turns those slots into four internal hard cuts.

## Hard rules

- Off-screen speech is part of this workflow's scope. For a silent/no-narration
  ad, route to ordinary video generation rather than adapting this workflow.
- A real product reference is required. Never invent or substitute one.
- Product is the hero in every slot. A person may be absent, hands-only,
  cropped, or POV, but never identity-locked or the focal subject.
- Voiceover only: no on-camera dialogue, lip-sync, greeting, or speaking mouth.
- Native Seedance speech only. Do not load or activate `narration`; never call
  `generate_audio` or `generate_audio_batch`, and never assemble a separate TTS
  track over these clips.
- Generate boards sequentially; submit ready clips in grouped batch calls only
  after every clip prompt is written.
- Complete the shared mandatory board cleanup; never continue with a raw board.
- Never bake text into generation. Add optional hook/subtitles only after the
  final video exists.
- Default to English voiceover with an American accent unless explicitly
  changed.
- Hide models, job IDs, internal phases, and intermediate mechanics.

## Phase 0 — Intake

Parse the product photo or product-page URL, duration, requested language and
accent, approved claims, music request, and explicit setting or demo overrides.
Ask only for missing product and duration, bundled once. Offer 10s, 15s, 30s,
and 45s for duration. Never ask about models, aspect ratios, resolution, boards,
audio, batching, identity, or transitions.

Do not start paid generation until product and duration are resolved. The later
text/post-package choice is the only sanctioned second ask.

## Phase 1 — Normalize the product

Read `references/product-product-intake.md` and follow it exactly. Resolve once:

- `product_reference`: confirmed media ID after media_import_url or attachment upload
  for image stages;
- `product_video_reference`: confirmed Higgsfield image UUID for Seedance;
- canonical `product_description`, including mechanics, hand-relative scale,
  visible side, absent features, label treatment, and one imperfection;
- `tier`, `category`, and `voice_gender`.

Reuse these values verbatim. Never infer price, invent claims, or replace a
blocked product page with stock or generated imagery.

## Phase 2 — Write the voiceover

Write off-screen voiceover only. Use roughly 12–20 words for ≤10s, 20–28 for
11–12s, and 28–35 for 13–15s. Split the total into one segment per board and
four beat-sized phrases per segment. Use sensory or mechanical specifics, not
generic praise. Remove greetings, repeated ideas, AI-tell phrases, and
unsupported claims. When an approved-claims list exists, preserve only exact
allowlisted strings.

Save the exact script as `output/script.txt` in the later assembly command.

## Phase 3 — Generate boards sequentially

Read `references/ugc-product-boards.md`. For K=1..N, write the complete prompt
and submit one stable-index request:

```json
{
  "requests": [
    {
      "index": 1,
      "params": {
        "model": "gpt_image_2",
        "prompt": "<board prompt>",
        "count": 1,
        "aspect_ratio": "21:9",
        "resolution": "2k",
        "quality": "high",
        "medias": [{ "value": "<product_reference>", "role": "image" }]
      }
    }
  ]
}
```

For K>1 append the cleaned previous-board job ID as the final `image` media and
match every `@ImageN` declaration to media order. Wait until terminal before
continuing.

Read `references/boards.md` and complete mandatory cleanup and inspection before continuing.

## Phase 4 — Write and submit clips

Read `references/ugc-product-clip-prompt.md`. Write every clip prompt before
submitting video. Carry K, N, duration, arc role, voiceover segment,
`voice_gender`, product description, board reference, and approved claims.

Require `product_video_reference` to be a confirmed UUID. Submit clips with
`generate_video_batch`, stable K indices, at most six per call:

Before the first submission, assert all three native-audio locks together:
`model:"seedance_2_5"`, `mode:"omni_reference"`, and
`generate_audio:true`. If any is absent, fix the video request; do not route to
`narration` or compensate with a separate audio call.

```json
{
  "requests": [
    {
      "index": 1,
      "params": {
        "model": "seedance_2_5",
        "prompt": "<clip prompt>",
        "count": 1,
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "duration": 15,
        "mode": "omni_reference",
        "generate_audio": true,
        "medias": [
          { "value": "<clean_board_job_id>", "role": "image" },
          { "value": "<product_video_reference>", "role": "image" }
        ]
      }
    }
  ]
}
```

Seedance 2.5 renders native voiceover with `mode:"omni_reference"` and
`generate_audio:true`; never call `generate_audio`. Wait for all
clips. Retry only failed indices and replace their prior job IDs.
