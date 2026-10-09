Read the ugc-video entrypoint and shared execution references first. This file
contains only the selected format; shared duration, cleanup, transport and failure
contracts apply to every stage.

# UGC try-on video

Produce one hosted 9:16 MP4 with a single locked creator identity and wearable
product. Each board is a 21:9 sheet of eight vertical 9:16 slots; one Seedance
clip turns those slots into eight narrative beats separated by seven hard cuts.

## Hard rules

- Use one `character_media_id` for every board and clip.
- Board 1 slot 1 is the muted pre-wear outfit with one plain kraft bag. From
  slot 2 onward, the product is worn and the bag never returns.
- Never depict a costume change, opening the kraft bag, or lifting the product
  from it. The hard cut performs the change.
- Slots 4 and 6 are hand-free garment macros; no hand touches the fabric.
- No mirrors or reflections. Lock hair, face, product silhouette, color, print,
  and design across the video.
- Generate boards sequentially. Write all clip prompts before grouped video
  submission.
- Complete the shared mandatory board cleanup; never continue with a raw board.
- Never bake text into generation. Optional text is post-render only.
- No CTA tail. End naturally on the final spoken beat.
- Default to English with an American accent unless explicitly changed.

## Safety and suitability gate — before intake or generation

If any item below fails, do not generate and do not route around the gate:

- **Creator authorization:** use only a generated adult age 21+ or a consenting
  adult non-public person whose image the user is authorized to use. A supplied
  photo is not permission to impersonate its subject. If third-party consent or
  adult status is unclear, ask once; decline public figures, celebrities,
  minors, non-consenting people, and deceptive identity use. Never silently
  age-transform a request and never clone or imitate a supplied person's voice.
- **General-audience fashion:** this workflow is for ordinary garments,
  footwear, bags, jewelry, and wearable accessories presented as a fit or style
  demonstration. Decline intimate apparel, lingerie, underwear, fetish wear,
  transparent garments, sexualized styling, nudity, or an emphasis on intimate
  anatomy. Do not adapt a disallowed request into a different outfit.
- **Allowed promotion:** decline political persuasion and promotion of
  prohibited or age-restricted goods or services, including adult sexual
  products or services, gambling, illegal or regulated drugs, prescription
  medication, tobacco or nicotine, weapons, counterfeit or illicit goods,
  extremist goods, deceptive or high-risk financial services, malware,
  spyware, fraud, and covert surveillance.
- **Truthful presentation:** preserve only product claims supplied by the user;
  never infer performance, results, purchase, ownership, endorsement, or lived
  experience. A generated creator presents a brand-authorized concept, not an
  organic customer testimonial.

## Duration and board progression

| Total duration |     Boards | Clip durations                  |
| -------------- | ---------: | ------------------------------- |
| 4–15s          |          1 | total duration                  |
| 16–19s         |          2 | balance both to at least 4s     |
| 20–30s         |          2 | 15, remainder                   |
| 31–45s         |          3 | 15, 15, remainder               |
| 46–60s         |          4 | 15, 15, 15, remainder           |
| >60s           | ceil(D/15) | 15 each, final clip at least 4s |

Use these arc roles:

- K=1 `BOARD_1_TRY_ON_CANONICAL`: PRE_WEAR, WEARING, FRONT_POSE,
  TEXTURE_CLOSEUP, TURN, DETAIL, STYLE_POSE, FINAL_LOOK.
- K=2 `BOARD_2_TRY_ON_HOME_TOUR`: continue through other rooms in the same
  home.
- K=3 `BOARD_3_TRY_ON_OUTDOOR`: all outdoor; light rain from slot 2, dry hair,
  wet-detail macros, no reflections.
- K=4 `BOARD_4_TRY_ON_HOME_REFLECT`: settled indoor reflection.
- K≥5 `BOARD_K_TRY_ON_LOOP`: alternate established and new compatible places.

## Phase 0 — Intake

After the safety and suitability gate passes, parse product photo or URL,
duration, attached authorized adult creator photo or desired generated-adult
gender, plus explicit location, appearance, mood, language, accent, claims, and
text choices. Classify the brief as `auto`, `guided`, or `director`.

Ask once for real gaps: product, duration (offer 10s/15s/30s/45s), and creator
photo or gender. Offer accent/quirk only when the brief already signals origin
or unusual creator energy. Never ask about models, boards, aspect ratios,
resolution, audio, transitions, or identity training.

## Phase 1 — Normalize the product

Read `references/product-product-intake.md`. Resolve and reuse verbatim:
`product_reference`, confirmed `product_video_reference`, canonical wearable
description, tier, category, materials, drape, absent features, and visible
side. Never infer price, claims, or an unseen side.

## Phase 2 — Lock the creator

If an authorized adult creator photo is attached and the gate has established
consent, import it with `media_upload_widget` and use that confirmed ID
without re-asking or editing the photo.

Otherwise read `references/try-on-ugc-character.md`, settle fresh variety rolls and
write one creator prompt. Submit:

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

Wait with `jobs_wait`, then lock `(character_media_id, character_url)` to the
returned job ID and result URL. Never replace the identity mid-run except under
the bounded character re-roll below.

## Phase 3 — Write the monologue

Use roughly 12–20 words for ≤10s, 20–28 for 11–12s, and 28–35 for 13–15s.
Split into one segment per board; the clip reference distributes it across the
eight beats. Board 1 is a personal-want mini-story. Later boards continue
mid-thought. Remove AI-tell openers, generic praise, repeats, unsupported
claims, and any CTA. The first word of each segment must be hook content, not a
recording warm-up.

Save the exact full monologue to `output/script.txt` during assembly.

## Phase 4 — Generate boards sequentially

Read `references/ugc-try-board.md`. For each K submit one stable-index
`generate_image_batch` request using `gpt_image_2`, `aspect_ratio:"21:9"`,
`resolution:"2k"`, `quality:"high"`, and media in this order: product,
character, then cleaned previous board when K>1. Match `@ImageN` declarations
to that order.

Wait until terminal before creating K+1. Keep the returned board job ID and
result URL.

Read `references/boards.md` and complete mandatory cleanup and inspection before continuing.

## Phase 5 — Write and submit clips

Read `references/ugc-try-clip.md`. Write every clip prompt before submission.
Carry K, N, duration, arc role, monologue segment verbatim, specificity,
persona, garment contract, and references. Enforce the six lip-sync beats and
two silent macro voiceover beats described in the reference.

Require a confirmed `product_video_reference`. Submit stable K requests through
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

Seedance 2.5 renders native speech with `mode:"omni_reference"` and
`generate_audio:true`; never call `generate_audio`. Wait for all jobs
and retry only failed indices.
