Read the ugc-video entrypoint and shared execution references first. This file
contains only the selected format; shared duration, cleanup, transport and failure
contracts apply to every stage.

# UGC review video

Produce one hosted 9:16 MP4. Keep one creator identity through every board and
clip. Each board is a 21:9 sheet of eight vertical 9:16 slots; one video clip
turns those slots into eight internal hard cuts.

## Hard rules

- Use one `character_media_id` for every board and clip. Never regenerate it
  mid-run or replace it with an inline description.
- Generate boards sequentially; generate ready clips through grouped batch
  calls only after every clip prompt is written.
- Never bake text into generation. Burn text only after render and only when
  the user opted in.
- Complete the shared mandatory board cleanup; never continue with a raw board.
- Default to English speech with an American accent unless explicitly changed.
- When a product is present, never greet or reintroduce it after board 1; later
  segments continue mid-thought.
- Hide model names, job IDs, internal phases, and intermediate mechanics from
  the user.

## Safety and truth gate — before intake or generation

If any item below fails, do not generate and do not route around the gate:

- **Creator authorization:** use only a generated adult age 21+ or a consenting
  adult non-public person whose image the user is authorized to use. A supplied
  photo is not permission to impersonate its subject. If third-party consent is
  unclear, ask once; decline public figures, celebrities, minors, and deceptive
  identity use. Never clone or imitate a supplied person's voice.
- **Allowed promotion:** decline political persuasion and promotion of prohibited
  or age-restricted goods or services, including adult sexual content, products,
  or services; gambling; illegal or regulated drugs, drug paraphernalia, and
  prescription medication; tobacco or nicotine; weapons, explosives, or harmful
  materials; counterfeit or illicit goods; extremist goods; deceptive or
  high-risk financial services; malware or spyware; fraud; and covert
  surveillance. A neutral educational mention is not a product promotion and
  belongs outside this workflow.
- **Truthful claims:** `approved_claims` is the complete allowlist of product
  claims supplied by the user. Preserve each allowed claim verbatim; never
  strengthen, combine, infer, or derive another claim. With no allowlist, create
  claim-free copy about visible materials, controls, application, packaging, and
  other directly observable mechanics.
- **No synthetic testimonials:** a generated creator is a host or demonstrator,
  never a real customer. Do not invent purchase, ownership, use, results,
  before/after outcomes, ratings, reviews, social proof, relationships, or lived
  experience. First-person experience is allowed only when a consenting user
  supplies the exact script and confirms it describes their own experience.
- **Transparent framing:** describe product-present output as a brand demo,
  creator concept, or sponsored creative—not an organic customer review. When a
  post package is requested, include an appropriate ad/sponsorship disclosure.

## Phase 0 — Intake

After the safety and truth gate passes, parse an optional product photo or URL,
duration, creator photo or requested gender, and
explicit overrides for location, hair, ethnicity, outfit register, mood, props,
language, accent, music, `approved_claims`, and on-video text.

Classify specificity:

- `auto`: 1–5 words with no scenario; choose the complete treatment.
- `guided`: 1–3 sentences of tone or rough flow; preserve that direction.
- `director`: 4+ sentences, scenario, shot list, or location sequence; map the
  supplied beats one-to-one to slots.

Ask only for real gaps, bundled into one question: duration (offer 10s, 15s,
30s, 45s) and creator photo/gender when absent. Never ask for a product merely
because none was supplied; lock `product_reference:null` and
`product_description:null` and continue with creator-led, scenario-driven UGC. Include
an accent or physical quirk option only when the brief already signals origin or
deliberately unusual character energy. Never ask about locked models, aspect
ratios, boards, resolution, audio, batching, or identity training.

Do not start paid generation until the required creator input and duration are
resolved. The later text/post-package choice is the only sanctioned second ask.

## Phase 1 — Normalize the optional product

If a product photo or URL was supplied, read `references/product-intake.md` and
follow it exactly. Resolve once:

- `product_reference`: confirmed attachment or imported HTTPS image `media_id`;
- canonical `product_description`;
- `tier`: `luxury`, `premium`, or `drugstore` from visual packaging cues only;
- `category` and exact usage/opening mechanic.
- `approved_claims`: exact user-supplied strings, or an empty list.

Reuse those values verbatim downstream. Never infer price, invent claims or
creator experience, or
replace a blocked/thin product page with a stock or generated product. If no
product was supplied, skip the reference, keep both product fields null, and
use the no-product branches in `ugc-board.md`, `ugc-clip.md`, and monologue craft.

## Phase 2 — Lock the creator

If the safety gate established that the user is authorized to use an attached
creator photo, call `media_upload_widget` with `type:"image"`, save its
`media_id` as `character_media_id`, and do not ask for confirmation again.

Otherwise read `references/ugc-character.md`, resolve the required variety rolls
and creator prompt, then submit one headless image request:

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

Wait with `jobs_wait` until terminal. On success save the returned `job_id` and
`result_url` as `character_media_id` and `character_url`. This identity is a
mandatory board input. Keep wardrobe fixed unless the story explicitly changes
context.

## Phase 3 — Write the monologue

Read `references/monologue-craft.md`. Preserve only allowlisted user-supplied
claims and the requested tone; never invent the creator's history or experience.
apply its density, hook, persona, story-shape, accent, and anti-slop rules. Split
the final monologue into N board segments. Save the exact full text to
`output/script.txt` in the later sandbox assembly command; if a hook plate may be
burned, also save its headline to `output/hook.txt`.

## Phase 4 — Generate boards sequentially

Read `references/ugc-board.md`. For K=1..N, build the complete board prompt and
submit exactly one `generate_image_batch` request with stable index K:

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
        "medias": [
          { "value": "<product_reference>", "role": "image" },
          { "value": "<character_media_id>", "role": "image" }
        ]
      }
    }
  ]
}
```

For K>1 append the cleaned previous board job ID as the final `image` media. If
there is no product reference, remove it and renumber every `@ImageN` declaration
to match the remaining media order. Wait until terminal before continuing.

Read `references/boards.md` and complete mandatory cleanup and inspection before continuing.

## Phase 5 — Write and submit clips

Read `references/ugc-clip.md`. Write every clip prompt before submitting any
video. Carry K, N, duration, board role, monologue segment verbatim, specificity,
persona, and board/character/product references.

Submit clips with `generate_video_batch`, stable index K, and groups of at most
six. For N>6, finish one group before submitting the next because the current
full-profile surface cannot accept a larger batch. Each request uses:

```json
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
      { "value": "<product_reference>", "role": "image" }
    ]
  }
}
```

Drop the product media when absent. Seedance 2.5 produces native speech with
`mode:"omni_reference"` and `generate_audio:true`; never call
`generate_audio`. Wait for all clips to become terminal. Retry only failed
indices with the corrected prompt; a successful retry replaces the old job ID at
that index.
