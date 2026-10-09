Read the ugc-video entrypoint and shared execution references first. This file
contains only the selected format; shared duration, cleanup, transport and failure
contracts apply to every stage.

# UGC unboxing video

## Format gate

The brief must request a creator-led reveal, not simply a product coming out of
its packaging. Do not introduce a visible creator or reaction arc to make a
product-only video fit this workflow. Once the format matches, collect the
creator identity, product and duration normally.

Produce one hosted 9:16 MP4 with one creator identity. Each board is a 21:9
sheet of four vertical 9:16 slots; one Seedance clip turns the board into four
internal hard cuts: PACKED → REVEAL → PRODUCT-FOCUS → SATISFACTION.

## Hard rules

- Use one `character_media_id` throughout.
- Board 1 slot 1 always shows a sealed, taped box and no product. The reveal is
  slot 2. The box is at the edge or gone in slot 2 and absent forever in slots
  3–4 and later boards.
- A real package photo is optional. Without one use one generic plain brown
  delivery box; never invent branding.
- Product analysis happens once and is reused verbatim.
- Generate boards sequentially; write all clip prompts before grouped video
  submission.
- Complete mandatory cleanup and inspection; stop dependent generation on failure.
- Never bake text into generation. Optional text is post-render.
- No greeting or reintroduction after board 1.
- Default to English speech with an American accent unless explicitly changed.

## Phase 0 — Intake

Parse product photo or URL, duration, attached creator photo or desired gender,
optional real-package photos, approved claims, language/accent, and explicit
look or location overrides. Classify specificity as `auto`, `guided`, or
`director`.

Ask once for missing duration (offer 10s/15s/30s/45s), product, creator
photo/gender, and whether a real package photo is available. If the user chooses
to attach a package but has not attached it, ask once for the actual image and
wait. A bare “yes” is not package media. Never ask about models, board count,
aspect ratios, resolution, audio, transitions, or identity training.

## Phase 1 — Normalize product and package

Read `references/product-product-intake.md`. Resolve `product_reference`, confirmed
`product_video_reference`, canonical product description, tier, category,
mechanics, hand-relative scale, visible side, and absent features.

Import real package photos once and keep their confirmed IDs. Otherwise set the
package reference to null and use the generic-box contract.

## Phase 2 — Lock the creator

If a creator photo is attached, import it once and use it unchanged.

Otherwise read `references/unboxing-ugc-character.md`, settle fresh variety rolls, write
one clean creator prompt, and submit:

```json
{
  "requests": [
    {
      "index": 0,
      "params": {
        "model": "soul_2",
        "prompt": "<creator prompt>",
        "count": 1,
        "aspect_ratio": "3:4",
        "quality": "2k"
      }
    }
  ]
}
```

Wait until terminal and lock the returned job ID and result URL.

## Phase 3 — Write the monologue

Use roughly 12–20 words for ≤10s, 20–28 for 11–12s, and 28–35 for 13–15s.
Split into one segment per board. Board 1 uses a caved-in confession or other
specific reveal-compatible hook, a body-event reaction at the reveal, one turn,
and a natural resolution. Later boards continue mid-thought.

Remove AI-tell warm-ups, generic praise, repetition, and unsupported claims.
The literal first word of every segment must be hook content. Save the exact
full monologue to `output/script.txt` during assembly.

## Phase 4 — Generate boards sequentially

Read `references/ugc-unboxing-board.md`. For each K submit one stable-index
`generate_image_batch` request using `gpt_image_2`, 21:9, 2k, high quality,
and media order product, character, optional real package, then cleaned previous
board for K>1. Drop absent media and renumber `@ImageN` declarations.

Wait until terminal before K+1. Keep each board job ID and result URL.

Read `references/boards.md` and complete mandatory cleanup and inspection before continuing.

## Phase 5 — Write and submit clips

Read `references/ugc-unboxing-clip.md`. Write all prompts before submission.
Carry K, N, duration, arc role, monologue segment verbatim, specificity,
character/product/package continuity, and approved claims.

Require confirmed `product_video_reference`. Submit stable K requests through
`generate_video_batch`, at most six per call:

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
          { "value": "<character_media_id>", "role": "image" },
          { "value": "<product_video_reference>", "role": "image" }
        ]
      }
    }
  ]
}
```

Seedance 2.5 supplies native speech with `mode:"omni_reference"` and
`generate_audio:true`. Never call `generate_audio`. Wait for all jobs
and retry only failed indices.
