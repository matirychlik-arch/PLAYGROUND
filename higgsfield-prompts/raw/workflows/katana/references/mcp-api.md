# MCP API reference for katana

Resolve tools by operation from the live callable catalog and use their exact returned identifiers. The metadata checked during this revision uses separate `estimate_image_cost` and `estimate_video_cost` operations, `models_get` / `models_search`, canonical media roles, batches of at most 6 and galleries of at most 24. Historical prices and observations below are not current guarantees.

Read `analysis/task-contract.json` first: REMIX is the default and follows the authored output plan;
EXACT is selected only by an explicit complete-reconstruction request. Scope-specific locks remain
binding in either mode. Task mode is not a provider `params.mode`; do not send `remix` or `exact` as
API values. Source-reconstruction examples below are conditional, not the default creative direction.

Never ask creative, font, identity, voice, budget or approval questions; never open pickers, consent widgets or waiting-for-user states. Reuse suitable authorized assets and infer unspecified production choices under the selected mode. Complete free preparation and create a finite live-priced required plan with bounded retries. Use existing task authorization under account and platform rules, constrained by any user/account limit; a numeric user budget is optional. Mandatory service consent cannot be bypassed: if execution requires fresh interactive consent, use an already authorized supported fallback that satisfies the plan or report that branch as blocked or partial declaratively and continue independent work. Do not purchase credits, start subscriptions or add unlimited retries.

## Video submission allowlist

Check every single request and batch item before both pricing and submission. Fresh video generation, draft, retry, extension or new motion uses exactly `seedance_2_5`, never another Seedance version, Kling, Veo, Wan or a substitute alias. Current Seedance 2.5 constraints are modes `t2v`, `omni_reference`, `video_edit`, `video_extension`, durations 4–30 whole seconds and resolutions 480p/720p/1080p; verify the prepared request against the live contract. Image generation continues to use image models; do not use Seedance 2.5 for stills.

Exceptions are task-required transformations of supplied source footage: `hf_mult_replace_object` for subject replacement and `hf_mult_motion_control` for motion transfer. Record why the source performance needs preservation; neither is the default route for a remix. Anime does not force a preset or Styles route. A source-frame + uploaded-identity image operation (§5.3) can prepare exact replacement or a new planned composition (§5.4), followed by still/code assembly or Seedance 2.5 motion. Genjutsu presets or Styles are optional only under verified contracts; never add a forced restyle or extra job. Catalog Genjutsu IDs and public Restyle preset IDs are distinct, never interchangeable. An unavailable preset does not authorize another fresh-video model. Local rendering, `sam_3_video` segmentation and `remove_background` remain allowed post-production utilities even when their output is a video mask; they are not alternate engines for new creative footage. Load [Genjutsu routing](genjutsu-routing.md) for the verified Styles capability and its distinction from direct Genjutsu edits. Do not inject Styles preset fields into a motion-transfer model that does not support them.

Celebrity source footage is eligible for supported source-anchored Genjutsu edits under the actual tool/content rules; it is not categorically forbidden. Keep the original subject when no identity change was requested. Preserve source timing, motion and untargeted details; do not label a generated celebrity performance as genuine archival footage. No identity disguise, dropped evidence or model switch may evade a real rejection. The no-question, no-consent-widget contract remains unchanged.

**Genjutsu prompts:** direct edits and catalog presets use one short sentence, at most two and at most 40 words. State the operation plus a small preservation rule; media supply identity, appearance, scene and choreography. Do not add detailed demographics, garment inventories, camera/effect narration or scene reconstruction. A verified preset may take an empty prompt only when its contract allows it and the selected preset with the input media already defines the result. This limit does not constrain image-edit prompts or Seedance 2.5 timecoded generation prompts.

**Request blocks are SHAPES, not settings.**

- In every request below, `model`, `mode`, `resolution`, `duration` and `aspect_ratio` come from the
  job's line in `plan/gen_plan.json`. They are written `"<from plan line>"`, or
  `"<from plan line: seedance_2_5>"` where the call fixes the value and the plan line must say the same.
- `python3 $RR/ledger.py params $W --line <ID>` prints the exact skeleton for a line, and
  `--check '<params json>'` compares the params you are about to send (exit 1 = mismatch). A submitted value
  that differs from the plan line is unplanned spend: stop (generation.md §5, check #9).
- Every Seedance call carries `generate_audio:false` and `bitrate_mode:"high"` (free).
- Response examples, the probe table (§4) and job records keep the literal values that were actually
  seen.

Sibling docs named here (`generation.md`, `budget.md`, `sandbox.md`, ...) are `references/<name>.md`, read with
the available skill-resource reader or local package path. Do not call a bundle reader unless it actually exists in the live tool catalog.

---

## 0. Ground rules

A generation operation may spend credits immediately. Never send `get_cost:true` to an image/video generation call and assume it cannot submit: current image/video pricing has separate estimate tools. Use `generate_audio` with `get_cost:true` only while its live contract explicitly guarantees no generation.

Pass current canonical media roles (`image`, `video`, `audio`, `start_image`, `end_image`, `ref_element`) only where the selected model supports them. Reuse confirmed media/job IDs. Current tools may import authorized HTTPS images automatically; this is a media-library write even during a no-generation estimate. Never upload unrelated content or another project's identifiers. Keep raw sensitive biometrics and secrets out of external calls unless the applicable repository/provider rules permit the exact data flow.

Facial identity, expression and appearance changes must come from a supported authorized image model,
appropriate Genjutsu transformation or Seedance 2.5 footage. Never implement a face swap, morph,
landmark warp, pasted facial patch, skin retouch, face painting or face-only relighting with local code.
Model failure, an exhausted reserve or unavailable permission is not a reason to fall back to a local
face-changing script. Code may track positions and composite intact frames/subject layers with whole-layer
transforms, outer-edge masks, planned whole-shot grades and separate graphics; it must preserve
the underlying face. Model calls still require the existing media/account authority and finite plan.

The `context` field is analytics only: one short sentence, no names, URLs, credentials or biometrics. Before the first generation without a destination, read `get_preferences`; create a project only when its saved preference or an explicit user request calls for it. Otherwise omit `folder_id`.

Unknown submission outcomes must be resolved before retry. Prices and refunds must be verified; historical refunds do not release current budget. Mandatory platform consent cannot be bypassed or fabricated. If a fresh interactive choice is unavoidable, use an already authorized fallback or report a declarative blocked/partial result; never open a picker or ask for approval.

## 1. Operations used by the flow

| Operation                                            | Purpose                                                      | Current bound                                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| `models_get`, `models_search`                        | Read required model constraints and roles                    | Read-only                                                                               |
| `estimate_image_cost`, `estimate_video_cost`         | Price a complete prepared job without generation             | No job; may import supplied HTTPS images                                                |
| `generate_audio` with `get_cost:true`                | Price speech only if contract still supports it              | Existing selected voice pair required                                                   |
| `media_upload` → PUT → `media_confirm` | Import a user attachment | Use already accessible bytes and the current upload contract; no widget |
| `media_upload` → PUT → `media_confirm`               | Persist a sandbox-created output                             | Reserve before its producing command                                                    |
| `generate_image`, `generate_video`, `generate_audio` | Submit a planned job                                         | Count 1; may spend credits                                                              |
| `generate_*_batch`                                   | Platform batch contract, not this workflow's submission path | Platform max 6; this workflow uses one single request per ledger reservation            |
| `jobs_wait`                                          | Await results without a gallery                              | At most 8 jobs; timeout at most 15 seconds                                              |
| `show_generation_by_ids`                             | A separately required preview under its live contract        | At most 24 jobs; do not duplicate a single-generation widget or create an approval gate |
| `balance`, `transactions`                            | Reconcile authorized job costs                               | Read-only; availability depends on catalog                                              |
| `sandbox_exec`                                       | Reference analysis and compositing                           | Confirm current sandbox contract                                                        |

## 2. Getting media in and out

### 2.1 media_upload → PUT → media_confirm

**Reserve (VERIFIED schema).** `filename` or `files[]` (1–20 items), optional `content_type`. The extension
decides the kind: image, video and audio extensions become generation inputs. Other whitelisted extensions (pdf,
zip, tar, tar.gz, json, docx, csv, code files) become **general files** with a permanent URL, and those cannot be
used as generation inputs. `.tgz` is refused (VERIFIED live 2026-10-08, below).

```json
{
  "files": [
    { "filename": "ref.mp4", "content_type": "video/mp4" },
    { "filename": "hero.png", "content_type": "image/png" },
    { "filename": "c03_pad.mp4", "content_type": "video/mp4" }
  ]
}
```

Single file:

```json
{ "filename": "out_final.mp4", "content_type": "video/mp4" }
```

General file (project state archive `<slug>_vN_state.tar.gz`, JSON, zip):

```json
{ "filename": "katana-1008-x7_v2_state.tar.gz" }
```

**Response (FROM-EVIDENCE, Yaong 2026-10-08)**, one entry per file:

```json
{
  "uploads": [
    {
      "upload_url": "https://upload.higgsfield.ai/<user>/<media_id>.mp4?X-Amz-...&X-Amz-Expires=86400&X-Amz-SignedHeaders=content-type%3Bhost%3Bif-none-match&...",
      "media_id": "7f7ceae0-1b8a-4354-984f-a0c44b87066b",
      "url": "https://d2ol7oe51mr4n9.cloudfront.net/<user>/<media_id>.mp4",
      "expires_in_seconds": 86400,
      "method": "PUT",
      "content_type": "video/mp4",
      "instructions": "Upload the file using: curl -X PUT -H \"Content-Type: video/mp4\" --data-binary @file '<url>' ... then call media_confirm with type \"video\" and media_id \"...\""
    }
  ]
}
```

Facts:

- The final CDN `url` is returned **at reservation time**, before any byte is uploaded. The plan can record it up
  front. (FROM-EVIDENCE)
- The signature covers `content-type;host;if-none-match`. The PUT **must** send `If-None-Match: *` and the
  **`content_type` echoed in the response**, which can differ from the one requested. Yaong reserved
  `yaong_track_v1.wav`, got `content_type: audio/mpeg`, and the URL came back as `.mp3`. The printed
  `instructions` omit `If-None-Match`; follow this file, not the hint. (FROM-EVIDENCE, every project)
- Each slot is **single-use**, because `If-None-Match: *` refuses to overwrite. A PUT of an empty file burns the
  slot, so guard with `[ -s file ]`. (FROM-EVIDENCE, Aura) The exact HTTP code returned on a second PUT is
  UNVERIFIED; expect 412.
- **Every `rr_save` needs its own fresh slot**, and so does every Genjutsu clip and deliverable. Reserve the
  slots for a stage in ONE `media_upload files[]` call (state archive + clips, or final + side-by-side +
  state) before the producing command; one call saves several round trips. (VERIFIED live 2026-10-08)
- State archives were 78–184 MB in the live run because they carried `ref/src.*` (the yt-dlp original next to
  `ref.mp4`) and the prepared `plates/` JPEG and `mattes/` PNG sequences, all rebuildable (`render.py prep`).
  Keep them out of the archive (`sandbox.md`). (VERIFIED live 2026-10-08)
- A `files[]` reply is large, about 4k tokens per file because of the presigned URLs. 11–15 files came back as a
  file that had to be parsed by a script. Batch sources into one tar or zip when you can. (FROM-EVIDENCE, Aura and Altman)
- `upload_url` expires after 24 h. (FROM-EVIDENCE)
- Transient PUT failures happen (Altman c02). Retry on 5xx only. (FROM-EVIDENCE)

**PUT inside the producing sandbox command** (sandbox files vanish about 10 s after a call ends):

```bash
[ -s out/final.mp4 ] && code=$(curl -s -o /dev/null -w '%{http_code}' -X PUT \
  -H "Content-Type: video/mp4" -H "If-None-Match: *" \
  --upload-file out/final.mp4 '<upload_url>'); echo "PUT_HTTP=$code"
```

`rr_put <file> <upload_url> [mime]` in `rr.sh` wraps this. Pass the mime from the reservation response.

**Confirm (VERIFIED schema)** only after HTTP 200. `type` is required: `image`, `video`, `audio` or `file`
(`file` for general files such as the state archive). Add `media_id` for one upload, or `media_ids` for 1–20
uploads of that type (confirmed in parallel).

Single upload:

```json
{ "type": "file", "media_id": "<state_media_id>" }
```

Batch of the same type (≤ 20 ids):

```json
{ "type": "video", "media_ids": ["<film_media_id>", "<compare_media_id>", "<triptych_media_id>"] }
```

Response (FROM-EVIDENCE): `{"results":[{"media_id":"...","status":"uploaded","url":"https://d2ol7oe51mr4n9.cloudfront.net/..."}]}`.
The `url` field was absent in some image confirms, so keep the `url` from the reservation as the source of truth.

Mixed types need **one `media_confirm` call per type**, because `type` is a single field. (VERIFIED schema)

**Project state archive.**

- Name it `<slug>_vN_state.tar.gz` (N = the delivery or stage number) and reserve it as a general file.
- Pass the `content_type` from the reservation reply to `rr_save` as its second argument:
  `rr_save '<upload_url>' '<content_type>'`. The signature covers Content-Type; `rr_save` defaults to
  `application/octet-stream`, which is what the reply carries for `.tar.gz`, `.tar` and `.zip`.
- Then `media_confirm` with `type: file`, and keep the returned URL as the state URL.
- VERIFIED live 2026-10-08: `.tar.gz` (stored as `.gz`), `.tar`, `.zip` and `.json` reservations are accepted;
  `.tgz` is REFUSED ("Upload URL generation failed"). The reply's `content_type` was
  `application/octet-stream` for the archives (`application/json` for .json), whatever `content_type` the
  request asked for. Full round trip verified: `rr_save` → HTTP 200 → `media_confirm` → `restart:true` →
  `rr_restore` restored the workspace.
- The pre-deploy test bundle behind `RR_BUNDLE_URL` (`sandbox.md` §2.1) is uploaded the same way, as a `.zip`
  general file, because `.tgz` is refused; the bootstrap unpacks it with `unzip` (VERIFIED live 2026-10-08).

### 2.2 User-provided attachments

Reuse an existing confirmed media ID. For an attachment without one, use the Full profile's standard `media_upload` → PUT → `media_confirm` path with its accessible bytes. Reserve the appropriate image/video/audio destination, PUT the supplied file with the returned headers, then confirm only after the upload succeeds. The confirmed media ID is ready for generation; do not confirm it twice. This profile has no native attachment-path importer.

Never open an upload widget or request the same file again. If the connected client cannot access the supplied bytes through an authorized path, state that limitation without a question and continue independent work. Do not fabricate an ID or URL.

### 2.3 URL sources

Use the reference URL only through an available authorized retrieval/import operation. Do not invent a removed URL-import operation or a widget tool. A webpage URL is not a direct media URL. A supported sandbox fetch may produce a file for the standard output upload path. Preserve the actual downloaded frame grid and audio.

### 2.4 Pulling media into the sandbox

Use the actual authorized URL returned by the media or result tool. Never construct a CDN URL, reuse another account's URL, or assume access is public. Keep URLs out of analytics context and logs where sensitive.

## 3. Historical model facts (revalidate through current models_get)

Read model constraints only when required to prepare the request. Call the current model inspection operation with `{"model_id":"<catalog model id>"}`. Verify duration, roles and parameters before using any historical row below; account allowances are runtime data, never inherited from this file.

| Model id                            | Params (default)                                                                                                                                                                                                                                                                                                                                                                            | medias roles                                | Notes                                                                                                                                                         |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `seedance_2_5`                      | mode `t2v`/`omni_reference`/`video_edit`/`video_extension` (t2v); duration 4–30 (5); resolution 480p/720p/1080p (**720p**); `generate_audio` (**true**); bitrate_mode standard/high (standard); extension_mode backward/forward (only for video_extension); `draft` (false) "480p draft that can be finalized within seven days"; `draft_job_id` "Completed draft job to finalize at 1080p" | start_image, end_image, image, video, audio | aspect auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16. video_edit is billed by the source length and ignores duration and aspect. Not unlim.                           |
| `hf_mult_replace_object` (Genjutsu) | resolution 480p/720p/1080p (720p). No other params.                                                                                                                                                                                                                                                                                                                                         | image, video                                | aspect_ratios `[]`: output follows the input.                                                                                                                 |
| `hf_mult_motion_control` (Genjutsu) | resolution 480p/720p/1080p (720p)                                                                                                                                                                                                                                                                                                                                                           | image, video                                | aspect follows the input.                                                                                                                                     |
| `soul_2` (= `soul_v2`)              | quality 1.5k/2k (**2k**); `soul_id`                                                                                                                                                                                                                                                                                                                                                         | `image` ×1 max                              | 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3. supports_unlim. Jobs show model `text2image_soul_v2`, but `models_get text2image_soul_v2` returns **"Model not found"**. |
| `seedream_v5_pro`                   | resolution 1k/1.5k/2k (2k); width, height; `remove_bg` (false); `is_inpaint` (false)                                                                                                                                                                                                                                                                                                        | image                                       | 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3, 21:9 (no auto). supports_unlim.                                                                                          |
| `seedream_5_0_flash`                | resolution 1k/1.5k/2k (2k); width, height (metadata only)                                                                                                                                                                                                                                                                                                                                   | image                                       | auto plus the same list.                                                                                                                                      |
| `nano_banana_2`                     | resolution 1k/2k/4k (**1k**); `is_inpaint`                                                                                                                                                                                                                                                                                                                                                  | image, mask                                 | auto, 1:1, 3:2, 2:3, 4:3, 3:4, 4:5, 5:4, 9:16, 16:9, 21:9. supports_unlim.                                                                                    |
| `nano_banana_pro`                   | resolution 1k/2k/4k (2k)                                                                                                                                                                                                                                                                                                                                                                    | image                                       | no auto aspect. supports_unlim.                                                                                                                               |
| `gpt_image_2`                       | resolution 1k/2k/4k (1k); quality low/medium/high (low)                                                                                                                                                                                                                                                                                                                                     | `image`                                     | supports_unlim. CLI defaults to high+2k (6.5 cr); the MCP default is low+1k.                                                                                  |
| `gpt_image_2_5`                     | variant flare/sunburst (flare); quality low/medium/high/xhigh/max (low); resolution 1k/2k/4k (1k); background auto/opaque/transparent                                                                                                                                                                                                                                                       | image                                       | Wide aspect list including 27:16 and 4:5.                                                                                                                     |
| `video_background_remover`          | none                                                                                                                                                                                                                                                                                                                                                                                        | video                                       | Called through `remove_background`.                                                                                                                           |
| `sam_3_video` ("Remove Background") | `apply_mask` (true); `frames_count` (null = whole clip)                                                                                                                                                                                                                                                                                                                                     | video                                       | `prompt` is not listed by MCP but is accepted (CLI schema lists it; FROM-EVIDENCE).                                                                           |
| `seed_audio`                        | format wav/mp3/pcm/ogg_opus (wav); sample_rate (24000); speech_rate, loudness_rate, pitch_rate; voice_type preset/element plus voice_id                                                                                                                                                                                                                                                     | image, audio                                | supports_unlim. The default TTS model.                                                                                                                        |
| `elevenlabs_v4`                     | **`dialogue` required** (string_array of turns, up to 10 voices, 10,000 chars); stability; similarity_boost; batch_size 1–4                                                                                                                                                                                                                                                                 | none                                        | `generate_audio` also requires `prompt` (schema), so duplicate the text there.                                                                                |
| `mirelo_text_to_audio`              | `duration` required                                                                                                                                                                                                                                                                                                                                                                         | none                                        | **"Game pipeline only."** Do not use for standalone SFX (generate_audio description).                                                                         |

---

## 4. Non-generating cost preflight

For images call `estimate_image_cost`; for video call `estimate_video_cost`. Pass the same prepared `params` that would be submitted, without a `params.get_cost` field. Both contracts explicitly return an estimate without generating a job. Audio alone may use `generate_audio` with `params.get_cost:true` after validating its live contract and an existing selected voice pair.

```json
{
  "params": {
    "model": "hf_mult_motion_control",
    "prompt": "<reference-faithful instruction>",
    "resolution": "<from plan>",
    "count": 1,
    "medias": [
      { "role": "image", "value": "<current authorized image media_id>" },
      { "role": "video", "value": "<current driving video media_id>" }
    ]
  }
}
```

Use `cost.credits_exact` for the plan and ledger. Treat an absent price as unknown, not zero. Price every distinct configuration and real input duration, including retries and paid mattes. Check the live meaning of count; this workflow always uses one result per request. Verify any server adjustments and reuse `prepared_params` so URL references are not uploaded repeatedly.

An estimate's `input_check.generation_validated:false` means that input presence alone was checked; it does not validate moderation, duration, accessibility or readiness. Do not use a paid submit as a probe. Create the finite required plan and retry reserve before submission using existing task authorization under account and platform rules. A numeric user budget is optional; set the internal ceiling to current exact quotes for executable jobs plus verified finite upper bounds for dependent stages (§4.1), with bounded retries and any user/account limit. Record actual authority without claiming that internal registration is user approval. Constrain every submission and re-priced plan change by that ceiling; never increase it autonomously. Unknown authorization or price means an already authorized fallback or a declarative blocked/partial result, never a question.

If a legacy helper mentions `params.get_cost`, use the current dedicated non-generating image/video estimate operation. Never pass the legacy field to current image/video generation tools as a substitute.

### 4.1 Dependent stages without invented input IDs

Still → video → matte chains need a finite whole-workflow ceiling before the first paid job, but future result IDs do not yet exist. Declare each dependent plan line with `deferred:true`, `depends_on:["upstream_line"]` and `input_bindings:{"medias.0.value":"upstream_line"}`. The ledger also supports `media_id` and `draft_job_id` binding paths. Only bound ID fields may contain explicit `<...>` placeholders; prompts, media roles, model/settings, count and takes must already be concrete. Dependencies must be selected plan lines, cover the same upstream IDs as the bindings and form an acyclic graph.

Obtain a current non-submitting estimator/account upper bound whose actual contract covers that stage's settings without future input IDs. Record it with `ledger.py price-set $W --line ID --planning --credits C --source estimate_video_cost --evidence "<actual response>" --basis "<why this verified quote bounds the unresolved-input stage>"`; use the matching image estimator or `verified_account_quote` when appropriate. These native-credit bounds expire after 24 hours. A generic historical rate, guessed conversion or unrelated input price is not a verified bound. Never send placeholders to a provider or submit a job to learn its price. If no supported bound exists, exclude that unsupported branch and state the limitation.

`quote` includes deferred jobs as non-executable upper bounds; the first `approve` records the whole-workflow ceiling and bounded retries. Deferred `params` and `guard` refuse. When all named upstream jobs are completed, bind their actual ledger job IDs, set `deferred:false`, obtain a fresh exact quote for those real inputs, then repeat `approve` with the updated subtotal and unchanged hard cap. Every other registered setting stays fixed, and the exact per-job price cannot exceed its original planning bound. The ledger verifies the bindings against completed jobs from the named upstream lines. Activation preserves the existing ceiling; it never enlarges it. Now use the ordinary `params --check` → `guard` → single submit → immediate `add` cycle. Plans whose inputs are already available retain the ordinary exact-quote path.

## 5. Image calls

### 5.1 Identity still, fictional human (Soul 2.0)

```json
{
  "params": {
    "model": "<from plan line: soul_2>",
    "quality": "<from plan line: 2k>",
    "aspect_ratio": "<from plan line: 3:4>",
    "count": 1,
    "prompt": "<Required fictional subject from the task, necessary views, planned wardrobe and visual treatment. In EXACT retain source attributes except explicit changes. Neutral isolation background only for a documented intermediate.>"
  },
  "context": "Required fictional identity anchor for the planned video."
}
```

- Text-only, or at most **one** ref with role `image`. `soul_id` is for a trained Soul. (VERIFIED schema)
- 0.12 cr per image (VERIFIED). Done in under 40 s (FROM-EVIDENCE). 2k 3:4 output = 1536×2048; the requested
  white backdrop came back slightly grey (VERIFIED live 2026-10-08).
- The example prompt above is a SHAPE: hair and outfit come from the selected plan and user locks (source attributes in EXACT), never from a cookbook
  example (generation.md header rule: copy the structure, never the identity items).
- Count 1. An invented-person branch runs only for an explicit identity change. Select internally; never open a character picker. At most three attempts within the finite plan, then source reuse or a declarative limitation.
- Historical ad-multiplier Soul settings are not this workflow's creative defaults. Use this separate neutral identity-anchor recipe only when necessary for an explicitly requested fictional subject. It must not replace the actual scene reference, remove source props/text, or force an age, studio or outfit onto the final shot.

### 5.2 Optional source-aligned identity sheet (historical Seedream 5.0 Pro route)

Use only for a measured identity-consistency need not already solved by existing media or §5.3.
In EXACT the source frame retains structural/style/wardrobe authority and the portrait supplies only
the requested identity. The example below is for that branch. In REMIX apply the declared ownership
and planned wardrobe under §5.4; do not automatically lock the scene to the source. Do not impose a
white studio, new outfit, full-body pose or extra paid sheet on every output.

```json
{
  "params": {
    "model": "<from plan line: seedream_v5_pro>",
    "resolution": "<from plan line: 2k>",
    "aspect_ratio": "<planned supported sheet layout>",
    "count": 1,
    "prompt": "Prepare the required identity reference views. Image 1 controls wardrobe, materials and visual treatment; image 2 supplies only the requested identity. Preserve all unchanged source attributes.",
    "medias": [
      { "role": "image", "value": "<source frame media_id>" },
      { "role": "image", "value": "<authorized identity-only photo media_id>" }
    ]
  }
}
```

Historical price: 2.5 cr at 2k; about 70 s. Live-price the actual selected configuration. In EXACT an
explicit outfit/look change can amend the source-derived prompt; a supplied portrait alone does not
override unchanged source wardrobe. In REMIX wardrobe follows the authored plan and explicit locks.
For a necessary sticker, the historical `"remove_bg":true` 1k route returned RGBA 1024²; verify the current
contract and preserve the observed sticker's own shape, palette and lettering (generation.md G6).

### 5.3 Two-reference image edit for identity replacement or keyframes

Use this route for anime, stylized or photographic character replacement, a finished still/code-composited cut, a Seedance 2.5 start frame or a justified Genjutsu motion-transfer image. The following two-reference example is for EXACT or a locally locked source composition: the source frame supplies structure/style/composition and the uploaded character supplies identity. For a new REMIX scene, use §5.4 ownership and the actual necessary reference count instead of copying these exact-scene locks.

Default image model: `gpt_image_2_5`, or an already selected verified multi-reference image model. Inspect its actual resolution, aspect and reference constraints before preparing the request; do not copy historical prices or model-specific options. Image editing does not use Seedance.

```json
{
  "params": {
    "model": "<from plan: gpt_image_2_5 or verified selected multi-reference image model>",
    "aspect_ratio": "<measured source-frame ratio supported by the model>",
    "count": 1,
    "prompt": "The first reference fixes composition, existing style, textures, pose, camera angle, lighting, clothes and background. Replace only <target subject> with the identity from the second reference, rendered in the first reference's style. Preserve that replacement identity without averaging it with the original person's face. Do not import the second reference's background or outfit. Keep all untargeted subjects, props, typography and graphics unchanged.",
    "medias": [
      { "role": "image", "value": "<original source frame media_id>" },
      { "role": "image", "value": "<uploaded user identity image media_id>" }
    ]
  }
}
```

Use the full-resolution source cut frame. Preserve text/graphics unless an explicit clean-intermediate plan restores those same source pixels in compositing. Describe the first/second ownership in words; model tag binding must follow its actual contract. Never introduce a third generated face or use a text-only approximation of the source composition. Select internally with count 1 and bounded attempts, without questions.

After the image edit, use the still with measured whole-frame/layer motion when sufficient; do not
deform facial landmarks, paste a face or simulate expressions in code. Use Seedance 2.5 only if new
motion is needed. Use `hf_mult_motion_control` when exact source driving choreography requires it.
A direct `hf_mult_replace_object` route may take the uploaded identity photo directly when it is the
more faithful path, without paying for an unnecessary image intermediate. Genjutsu presets are optional,
never mandatory for all anime. Content refusals do not authorize disguising the same request or switching
routes to evade restrictions.

### 5.4 Remix assets and reference ownership

Use the selected verified image model and its supported media roles for a missing hero anchor,
location, prop or composition asset in `plan/creative-plan.json`. Reuse a suitable existing image
first. Supply only necessary authorized references and state what each owns: identity, design,
architecture/materials, visual treatment or a specifically locked composition. New framing, action
and light follow the authored scene unless a user lock or designated reference fixes them. An input
face does not automatically supply its background or photographic style. Location plates do not
silently override identity, camera or the chosen lighting plan. Resolve ownership before submission.

Use the conditional prompt structure in `generation.md` for scene context, spatial layout, camera,
action, light and continuity. Exact-source prompt wording in §5.2–5.3 is not mandatory here. Match
the requested output aspect where supported, preserve the intended identity/product, select one
result internally and keep every asset/attempt within the same priced plan. Do not paint or erase
a head to repair a reference sheet. Still generation remains an image-model operation.

---

## 6. Video calls

### 6.1 Seedance 2.5 omni_reference multi-shot plate

For REMIX, take duration, aspect, actions and composition from output slots in
`plan/creative-plan.json`, with explicit reference ownership and the prompt structure in
`generation.md`. For EXACT, use observed source slots and the source-preservation example below.
Both branches use the same verified API fields; generation `mode` remains a supported provider value.

```json
{
  "params": {
    "model": "<from plan line: seedance_2_5>",
    "mode": "<from plan line: omni_reference>",
    "duration": "<from plan line: sum of required shot slots>",
    "resolution": "<from plan line>",
    "aspect_ratio": "<from plan line>",
    "bitrate_mode": "high",
    "generate_audio": false,
    "prompt": "@image1 is the source-aligned composition and appearance reference. Preserve its measured framing, camera, pose, lighting, environment, textures, wardrobe, props, all performers and typography. <If a replacement is requested, @image2 supplies only the intended identity; preserve source wardrobe and every untargeted detail.> <Shot-by-shot motion and time slots from the completed source analysis.> Keep source text, logos and graphics unless an exact original-layer restoration plan explicitly covers a clean intermediate.",
    "medias": [
      { "role": "image", "value": "<source frame or accepted source-aligned keyframe id>" },
      {
        "role": "image",
        "value": "<optional intended identity image id; omit this entry if unnecessary>"
      }
    ]
  },
  "context": "Reconstruct the measured source shots with only the requested changes."
}
```

- **Plan fields.** The plan line states `"generate_audio": false` and `"bitrate_mode": "high"` explicitly (generation.md header), so `ledger.py params` / `--check` carry them. Use only fields supported by the live contract and matched by the plan.
- **Reference ownership.** In EXACT the source owns composition, lighting, texture, wardrobe, props, lettering and untargeted people; an identity image supplies only the requested identity. In REMIX use §5.4's scene-specific ownership. Historical examples never supply a new project's wardrobe, set or gestures.
- **Composition.** Reuse a suitable image or prepare a necessary keyframe. A supported `start_image` may pin the first frame; inspect later shots independently. Split into separate Seedance jobs when a shared plate cannot preserve required compositions. Source geometry is mandatory in EXACT or a scoped composition lock, not for every remix shot.
- **Cast and layers.** Keep the planned cast consistent through hidden-face appearances. EXACT restores every required source performer and layer; REMIX may author new cast arrangements and separate text/graphics while preserving user locks and the intended hero. Never omit a required person merely to simplify matting or erase locked lettering.
- **Duration = the sum of the shot slots**, and it must equal the plan line's duration (budget.md §4.3).
  Each slot is clamp(2 × the screen seconds the EDL needs from that shot, 2, 4); e.g. slots of
  2 + 3 + 2 + 3 s give duration 10. A continuous-routine plate is ceil(1.6–2 × the routine length). Round up and clamp to
  the live supported range. Treat 4–15 s as a sizing preference only; a longer required plan must use a supported length up to 30 s or split into complete jobs, never clamp away planned shots. Never copy duration 15 from the VERBATIM Katana prompts (generation.md G7): that project generated 11×
  what it used.
- **Tags:** `@image1`, `@image2`, ... follow the order of the `image` entries in `medias`. Lowercase
  `@image1` worked in Katana and Yaong. The Genjutsu and Ad Multiplier contracts use canonical `@Image1` /
  `@Video1`. (FROM-EVIDENCE) Audio refs would be `@audio1`, but see the next bullet.
- **`generate_audio:false` always.** The default is **true** (VERIFIED). **Never send `audio` with
  `generate_audio:true`**: that combination came back nsfw 4/4 in Yaong. Seedance also re-speaks an audio ref
  rather than passing it through. (FROM-EVIDENCE)
- Duration is an integer 4–30. An unsupported value is clamped or rounded, not rejected (VERIFIED schema text), so
  a 3 s request bills 4 s.
- Ref limits: at most 50 medias, at most 30 images including start/end. `t2v` accepts no media. `start_image` and
  `end_image` work only in `omni_reference`. (FROM-EVIDENCE, CLI model get) A `start_image` pins the first frame.
  Whether it also takes an `@imageN` slot is UNVERIFIED, so keep identity refs as `image`.
- Output: 24 fps; 4:3 1080p = 1664×1248 HEVC Main10 yuv420p10le, about 15 Mb/s; 15 s jobs take 5–15 min
  (FROM-EVIDENCE). **4:3 720p = 1112×834 H.264, 24 fps; a 10 s plate = 241 frames** (VERIFIED live 2026-10-08).
- **Timecodes are ordering hints.** In Yaong the gestures ran 1.5–2× slower than the timecodes and cuts slid
  ±0.5 s or more (FROM-EVIDENCE); in the 2026-10-08 Katana plate the five 2 s shot slots landed almost exactly on
  their timecodes (VERIFIED live). Adherence varies per plate, so choose in-points from the catalog sheet.
- The ref count, audio on/off, bitrate and aspect do not change the price. (FROM-EVIDENCE; 2 refs = 35 at 720p 5 s
  VERIFIED)
- Internal job fields (`multi_shots`, `multi_prompt`, `multi_shot_mode`, `speedramp`, `genre`) appear in job
  records but not in the MCP schema (VERIFIED, records). Do not send them. Use timecoded `Shot N (a-bs):` lines.

**Draft, then finalize (VERIFIED schema; draft and finalize prices VERIFIED live 2026-10-08; finalize quality
UNTESTED; a draft itself is a preview, never shipped footage):**

```json
{
  "params": {
    "model": "<from plan line: seedance_2_5>",
    "mode": "<from plan line: omni_reference>",
    "draft": true,
    "duration": "<from plan line>",
    "resolution": "<from plan line>",
    "aspect_ratio": "<from plan line>",
    "bitrate_mode": "high",
    "generate_audio": false,
    "prompt": "<same prompt>",
    "medias": ["<same medias>"]
  }
}
```

The draft is billed at 480p whatever the resolution (5 s = 15; a real 4 s draft was charged 12 and came back
752×560, VERIFIED live 2026-10-08). A completed draft finalizes at 1080p within 7 days:

```json
{
  "params": {
    "model": "<from plan line: seedance_2_5>",
    "draft_job_id": "<completed draft job_id>",
    "resolution": "<from plan line>",
    "mode": "<from plan line: omni_reference>",
    "duration": "<from plan line>",
    "aspect_ratio": "<from plan line>",
    "bitrate_mode": "high",
    "generate_audio": false,
    "prompt": "<same prompt>",
    "medias": ["<same medias>"]
  }
}
```

- **Finalize price (VERIFIED live get_cost 2026-10-08):** the full 1080p rate. A 4 s draft → **48**. The finalize
  is **always 1080p**: a `720p` resolution is ignored. Without `duration` it prices **5 s (60)**, so always pass
  the draft's own duration.
- **Economics:** draft + finalize = 12 + 48 = 60 for 4 s = 1.25× a direct 1080p job (48) and 2.1× a direct 720p
  job (28). Worth it only on a 1080p plan where more than about 20–25% of direct takes would be rejected, and
  only as an UNTESTED quality path: whether the finalize keeps the draft's motion and framing is unverified (no
  finalize job has run). Never on a 720p plan.
- Price the finalize through `estimate_video_cost` first. Submit its prepared params through generation only if that exact job is in the authorized finite plan; never use a generation call as a free probe.

**Preview restriction:** only `seedance_2_5` drafts are allowed. Do not use another video model for cheaper previews or failed-job fallbacks.

### 6.2 Genjutsu replace (hero inside the reference's own footage)

```json
{
  "params": {
    "model": "<from plan line: hf_mult_replace_object>",
    "resolution": "<from plan line>",
    "prompt": "Replace <brief target-position cue> with @Image1. Keep the source wardrobe, motion and all other details unchanged.",
    "medias": [
      { "role": "image", "value": "<suitable supplied or prepared replacement-identity media_id>" },
      { "role": "video", "value": "<96-frame pad media_id (4.00 s)>" }
    ],
    "declined_preset_id": "<only if this prompt's preflight or submit bounced; read from that response>"
  }
}
```

- **Per cut, on 96-frame pads for short inputs.** SWAP is one job per cut. A whole-reel replace is an
  UNTESTED historical experiment line, never the default (§15.1). Prefer a suitable supplied replacement
  image. A source-aligned prepared image is conditional on a measured fidelity need and supported media
  roles; do not buy an unnecessary keyframe or transfer a portrait's clothes/background into the source.
- **Driving clip** (generation.md G9): `frames.py export $W --cut <id> --fps 24 --crop window` (muted), then
  `frames.py pad <cut.mp4> <pad.mp4> --mode pingpong` for a cut under 4 s of real time (exactly 96 frames). Probe
  the result: frames ÷ 24 must be the intended integer, and the line is priced from the probed count
  (`ledger.py guard $W --line <ID> --frames <probed count>`). Never pad a native-fps export of a 25/30/50/60
  fps reference: `pad` exits 2 on an fps mismatch unless `--retime`.
- **Roles:** use the current schema keys `image` / `video`, with at least 1 image and **exactly 1** video. (VERIFIED, input_check and tool description)
- **Only param: `resolution`** (480p/720p/1080p, default 720p). There is no duration or aspect: the output follows
  the input's aspect. (VERIFIED) At 1080p, a 4:3 input gives 1664×1248 and a portrait input gives 1248×1664
  (FROM-EVIDENCE). **At 720p a 994×830, 96-frame pad came back 1054×880, 24 fps, 89 frames (3.71 s, not 4.00)**
  (VERIFIED live 2026-10-08). Output size and length differ from the input: map frames back proportionally
  (`gen_index = round(padded_index × gen_frames / padded_frames)`; `assemble.py` does it, and the live c12 rebuild
  passed `assemble --control` on all 21 cuts).
- **Historical server enhancement:** some past job records contained long server-expanded prompts. This does not require a long submitted prompt. Keep the submitted operation and preservation clause brief; validate that the result retains source wardrobe and untargeted details.
- **Min length about 4 s.** 3.57 s failed with HTTP 422 and no body; get_cost rejected 3 s. (FROM-EVIDENCE)
  Ping-pong pad to 96 frames @24 (4.00 s).
- **Billing: replace = ceil(seconds) of the driving clip; MT = round(seconds).** On the same ~4 s clip replace
  quoted 35 and MT 28 at 720p (VERIFIED). **An exact 96-frame (4.00 s) pad bills 4 s: a real 720p replace job on
  one was charged exactly 28** (VERIFIED live 2026-10-08). A 4.04 s source billed 5 s (FROM-EVIDENCE), and this account's replace
  jobs on Altman's 100-frame (4.17 s) pads were charged 55 at 1080p (§13). Altman's get_cost on an exactly 4 s
  probe clip quoted 44 at 1080p (FROM-EVIDENCE). So always trim or pad to an exact integer, and re-probe your
  real 96-frame pad through the current video estimate operation before quoting.
- **Preset bounce:** a short replace prompt returned the IN THE DARK recommendation in get_cost (VERIFIED), and
  in the live run the swap prompt's get_cost bounce reproduced on submit until `declined_preset_id` was sent
  (VERIFIED live 2026-10-08).
- **Wardrobe:** the live c12 replace again dressed the hero in the photo's clothes (VERIFIED live 2026-10-08).
- **Moderation or IP rejection.** Do not transfer the same refused request to another model to defeat its restriction. Verify refunds, use a permitted faithful source-reuse route when possible, and report unresolved cuts without a re-ask. A refund does not enlarge the plan ceiling.
- Replace fails on a class change (car→person). (FROM-EVIDENCE)

### 6.3 Genjutsu motion transfer (requested source-anchored re-performance)

```json
{
  "params": {
    "model": "<from plan line: hf_mult_motion_control>",
    "resolution": "<from plan line>",
    "prompt": "Animate @Image1 with the source video's motion and camera movement, preserving the image's identity and appearance.",
    "medias": [
      {
        "role": "image",
        "value": "<suitable existing image id, or §5.3 two-ref still only if needed>"
      },
      { "role": "video", "value": "<24 fps driving clip, whole seconds, >= 4 s>" }
    ]
  }
}
```

- Same roles and resolution rules as §6.2. 28 cr for the ~4 s clip at 720p (VERIFIED). A second image adds no
  cost (FROM-EVIDENCE).
- **Reuse a suitable supplied/prepared image first.** Generate the §5.3 two-ref still only when needed to preserve the intended identity, scene and composition. A mismatched portrait background can contaminate the result; that observation does not require a new paid still for every cut. A content refusal never authorizes evasion.
- **Driving clip:** exported at 24 fps like §6.2. MT bills round(seconds): a cut under 4 s is ping-pong padded
  to 96 frames; a part whose fractional second is ≤ 0.1 s stays unpadded (≤ 2 tail frames are filled in code);
  any other part is freeze-padded to ceil(seconds). One full-length take only for a reference of ~11 s or less
  without burned graphics; otherwise parts, each paying its own rounding (generation.md G10).
- **Output geometry:** 1664×1248 and 1248×1664 are historical observations, not required source shapes. Probe the actual result and map it through the recorded source-aligned coordinates. Preserve source aspect, scale, positions and visible content; never force 4:3/3:4 or a fixed 0.35 crop centre. If a live input restriction requires padding, document a reversible mapping first and verify it after generation.

### 6.4 Whole-reference hero swap in one job: video_edit (UNTESTED historical experiment)

Only use when the current request already explicitly calls for this experiment and it fits the finite priced plan. Never offer optional paid experiments or add this on top of the required plan. Shape (VERIFIED from the ad-multiplier workflow text and the model schema):

```json
{
  "params": {
    "model": "<from plan line: seedance_2_5>",
    "mode": "<from plan line: video_edit>",
    "resolution": "<from the priced plan's required final settings>",
    "duration": "<ledger compatibility value only; ignored in video_edit>",
    "aspect_ratio": "<ignored in video_edit>",
    "bitrate_mode": "high",
    "generate_audio": false,
    "prompt": "<Ad-Multiplier-style edit prompt: @Image1 declaration, REPLACE the <source person> in every appearance, keep cuts/motion/camera/timing, then the exact block 'Preserve every caption, subtitle, and other untargeted on-screen text element from @Video1 exactly as it appears ...'>",
    "medias": [
      { "role": "video", "value": "<whole ref media_id, 4-30 s>" },
      { "role": "image", "value": "<hero media_id or job_id>" }
    ]
  }
}
```

The live `video_edit` contract ignores `duration` and `aspect_ratio`: actual input video duration
controls billing and the input controls framing. Probe and price that exact input; a rounded duration
field does not trim it or establish its price. If the verified request/ledger path permits omission,
omit these ignored fields. Do not force a low-resolution experiment or create an extra canary job.

Historical comparison only, not an allowed submission in this skill: the Ad Multiplier workflow used `model: "ad_multiplier"` with roles `video` then `image` (in that order),
`count: 1`, `duration_policy: "strict"` (a field that is not in models_get; its effect is UNVERIFIED) and
`mode: "video_edit"`, and it restores the source audio in post.

---

## 7. One reservation, one submission, immediate registration

The platform's `generate_video_batch` / `generate_image_batch` / `generate_audio_batch` contracts accept 1–6 `{index, params}` items, `count:1`, with a smaller live limit taking precedence. They do not support cost preflight inside submission. These are platform capabilities, not permission to batch this workflow's paid jobs.

**Operational rule:** use the single `generate_*` operation for exactly one prepared request. Reserve its full verified cost with the ledger guard, submit those exact runtime params, and immediately register the returned job ID against that reservation before reserving another job. Follow the current commands in `budget.md`; a successful guard alone is not a multi-request spending authorization. Linked atomic batch reservation is unsupported. Never run several independent guards and then submit a multi-item batch, including a canary batch.

The normal cycle is `ledger.py guard $W --line <ID>` → one `count:1` submission → `ledger.py add $W --line <ID> --job <JOB_ID>`. Record the verified current quote first with `ledger.py price-set $W --line <ID> --credits <C> --source <estimate_image_cost|estimate_video_cost|verified_account_quote> --evidence '<response reference>'` as described in `budget.md`. After an ambiguous submit, retain the reservation until the job is recovered. Release it only with `ledger.py release $W --evidence '<provider evidence of no job and no charge>'`; refund/bounce state changes also require evidence.

Validate the model allowlist and exact runtime params before reservation. The guard enforces the unchanged finite ceiling, retry limits and request/quote match. Internal plan registration records actual task/account authorization; it never creates user consent. Every family's first required job is its canary, submitted individually through this sequence. Later jobs of that family wait until it passes. Different families may have pending jobs only after each individual submission has been registered.

If a request returns a preset recommendation without creating a job, reconcile that no-job outcome using `budget.md` before retrying only that request with its returned `declined_preset_id`. Never treat a moderation refusal as such a recommendation. On a timeout or ambiguous response, keep the reservation committed and resolve the job before any new submission; never release it or charge again on an assumption. Record the actual submitted params and returned ID immediately, not after polling or other work.

Historical mixed-model batches and partial-success responses demonstrate why per-item outcomes matter. They are not operational recipes for the current serial reservation flow. No image, video or audio job may be hidden inside a batch that bypasses this guard.

Single `generate_*` responses (FROM-EVIDENCE, generate_image) look like
`{"results":[{"id":"<job_id>","type":"image","status":"pending","model":"...","params":{...}}]}`, with one result
per `count`. They also render a widget.

---

## 8. Waiting and results: jobs_wait

```json
{
  "jobs": [
    { "index": 3, "job_id": "<uuid>" },
    { "index": 7, "job_id": "<uuid>" }
  ],
  "timeout_seconds": 15
}
```

- 1–8 jobs per call. `timeout_seconds` is 0–**15** (default 15); 0 returns an immediate snapshot. (VERIFIED schema)
- Works on ids from the batch tools, single `generate_*` calls and `remove_background` (FROM-EVIDENCE: Katana
  polled `generate_image` and remove_bg ids).

**Response (FROM-EVIDENCE, Katana and Yaong):**

```json
{
  "jobs": [
    {
      "index": 0,
      "job_id": "...",
      "status": "completed",
      "type": "image",
      "model": "seedream_v5_pro",
      "result_url": "https://d8j0ntlcm91z4.cloudfront.net/<user>/hf_20261007_235304_<job_id>.png"
    },
    {
      "index": 1,
      "job_id": "...",
      "status": "in_progress",
      "type": "image",
      "model": "seedance_2_5"
    },
    { "index": 2, "job_id": "...", "status": "nsfw", "type": "image", "model": "seedance_2_5" }
  ],
  "summary": { "total": 3, "completed": 1, "failed": 1, "active": 1, "errors": 0 },
  "all_terminal": false,
  "timed_out": true,
  "poll_after_seconds": 10
}
```

- **Statuses:** `pending` (just submitted), `in_progress`, `completed` (has `result_url`), and the terminal
  failures `nsfw`, `ip_detected` and `failed`. `nsfw` counts in `summary.failed` (FROM-EVIDENCE). Whether
  `ip_detected` also counts there is UNVERIFIED, though it appears as a job status in this account's records
  (VERIFIED). Permanent lookup failures are returned once and count in `errors` (VERIFIED schema text).
- `type` shows `"image"` for video jobs while they are queued or in progress. This is cosmetic. (FROM-EVIDENCE)
- When `all_terminal` is false, call again after `poll_after_seconds`.
  - Between polls do **reference-side work only**: text layers from the reference, `fx.js`, the audio map, QA
    scripts.
  - **Do not catalogue plates, choose in-points or write the EDL until `all_terminal` is true for every paid job
    of the batch.** Katana's f3a (180 cr) finished 3 min after the edit design started on the 17 ready clips,
    was never catalogued, and held the better front-lit opener and blade draw. (FROM-EVIDENCE)
  - A job that turns terminal after the EDL exists must be catalogued, and the EDL reviewed, before rendering.
- Typical latencies (FROM-EVIDENCE): Soul under 40 s; Seedream 2k about 70 s; nano_banana under 3 min; Seedance
  5–15 min (1080p 15 s); Genjutsu several minutes; remove_background 1–7 min; sam_3_video about 1 min; nsfw
  verdict at the first poll, about 2.5 min. ip_detected refunds arrived 35 s to 4 min after submit (VERIFIED,
  records).
- **Display:** single `generate_image` / `generate_video` calls already show an auto-updating widget.
  Use `jobs_wait` to await them; do not call `show_generation_by_ids`, `job_display` or `show_generations`
  merely to refresh or redisplay those same results after completion. A separately required preview
  may use the available display contract, without a user approval gate. Historical headless batch
  display used up to 24 `{index, job_id}` entries; it does not authorize generation batches here.

```json
{
  "jobs": [
    { "index": 3, "job_id": "<uuid>" },
    { "index": 7, "job_id": "<uuid>" }
  ]
}
```

**Result URLs:** `result_url` from jobs_wait, or from job records (`show_generations` items carry `id, type,
status, model, params, results`; CLI records carry `result_url`, `thumbnail_url` and `min_result_url`, the last
always null on this account). Use only the authorized URL actually returned by the tool; do not construct a CDN path from historical naming patterns.
Fetch returned URLs through the supported sandbox operation (§2.4). (VERIFIED, records; FROM-EVIDENCE, jobs_wait)

---

## 9. Mattes

### 9.1 remove_background (video) → video_background_remover

```json
{
  "params": {
    "media_id": "<completed video job_id or confirmed video media_id>",
    "media_type": "video"
  }
}
```

- Response (FROM-EVIDENCE): `{"results":[{"id":"<job_id>","type":"video","status":"pending","model":"video_background_remover","params":{...}}]}`.
  Poll the id with jobs_wait.
- 1 cr per clip (VERIFIED: account transactions show "Video Background Remover -1"). The record stores
  `video_meta` (duration, frame_rate, frames_count).
- Output: the **person composited on black**, H.264 yuv420p, **no alpha**, frame-aligned with the input, main
  subject only. Rebuild alpha as matte ÷ original, or threshold max(RGB) > 8. Dark clothing and hair leave holes.
  (FROM-EVIDENCE)
- One Katana job failed outright; the resubmit worked. (FROM-EVIDENCE)

### 9.2 sam_3_video segmentation and local masks

Segmentation processes existing footage and is allowed under the creative-video model lock. Verify the live model contract and exact price, then use the finite authorized plan. Historical request shape:

```json
{
  "params": {
    "model": "sam_3_video",
    "prompt": "<the source subject to segment>",
    "apply_mask": false,
    "frames_count": "<source frame count>",
    "medias": [{ "role": "video", "value": "<source media_id or job_id>" }]
  },
  "context": "Source-aligned subject mask for compositing."
}
```

Use exactly one source video. A binary mask may require thresholding; inspect it against the actual source, clamp unwanted rails or microphones and union held props from an existing difference mask where needed. Preserve the source frame count and required subjects. Matte only the clips used by the EDL. If the service lacks a verified price or usable capability, use an existing mask or local compositor/segmentation operation; never guess a price or create new creative footage as a mask substitute.

---

## 10. Audio (only for an explicitly requested audio change)

EXACT preserves the reference soundtrack unless explicitly changed. REMIX uses the planned recorded
soundtrack, retaining the source when suitable and honoring every audio lock. Use speech generation
only when narration is requested, with an already selected exact `voice_id` + `voice_type` pair and a
priced authorized plan. Never invent a voice, copy an example ID or invoke a mandatory human picker.
If the pair is absent, continue eligible audio work and report the narration limitation without a question.

```json
{
  "params": {
    "model": "<from plan line: seed_audio>",
    "prompt": "<text to speak>",
    "voice_type": "preset",
    "voice_id": "<existing user-selected voice_id>",
    "format": "wav",
    "sample_rate": 48000
  }
}
```

```json
{
  "params": {
    "model": "<from plan line: elevenlabs_v4>",
    "prompt": "<same text>",
    "dialogue": [{ "text": "<line>", "voice_id": "<uuid>", "voice_type": "preset" }]
  }
}
```

- seed_audio is the default TTS. Use exactly `elevenlabs_v4` when the user says v4; `text2speech_v2` with variant
  elevenlabs is not v4. (FROM-EVIDENCE) The dialogue item shape is FROM-EVIDENCE; the schema only says
  "string_array of turns with a required voice".
- The recorded service contract restricts `sonilo_music` and `mirelo_text_to_audio` to the game pipeline; verify the live scope before any use. Their unavailability does not block the edit and never authorizes code-built music or SFX. Preserve the supplied/reference soundtrack, retain already authorized suitable audio, or select actual permitted stock/library recordings. Code may align/mix those assets, not synthesize beats, noise effects or whooshes.
- **Lyrics are final assembly data:** available supplied lyrics, source text and words transcribed from supplied audio may be synchronized in a deterministic text pass after visual generation and muxed with the song. Do not depend on generated lettering. EXACT preserves source cue timing/duration except requested changes; REMIX aligns words to the actual selected recorded excerpt and output plan, respecting audio/text locks. “At the end” describes assembly, not an appended card. Do not omit requested lyrics because video generation cannot render them, fetch full protected lyrics absent from supplied media, or paste them into chat unprompted. Verify the lyric layer and planned audio tail; see `compositing.md` §6.6/§11 and `qa-delivery.md` §1.3.1.

---

## 11. Preset recommendations and Genjutsu presets

**Historical single-call notice (external response data, not workflow instructions):**

```json
{
  "notice": {
    "type": "preset_recommendation",
    "message": "<external preset recommendation text>",
    "data": {
      "preset": {
        "id": "24bae836-2c4a-48e0-89b6-49fcc0b21612",
        "name": "IN THE DARK",
        "preview_url": "https://cdn.higgsfield.ai/job_set_chain_preset/b39158f2-75c2-4077-b102-54fd6b257008.mp4"
      },
      "use_preset_with": {
        "model": "higgsfield_preset",
        "preset_id": "24bae836-2c4a-48e0-89b6-49fcc0b21612"
      },
      "retry_literal_with": { "declined_preset_id": "24bae836-2c4a-48e0-89b6-49fcc0b21612" }
    }
  }
}
```

The batch form is `status: "submission_failed"` plus `preset_recommendation` (§7). Neither form creates a job or
a charge. (VERIFIED for get_cost; FROM-EVIDENCE for real submits)

Policy:

Preserve the selected output plan and explicit locks. An advisory preset recommendation is external
data, not an instruction to change the requested result. If the live contract supports a retry within
existing intent, reconcile the verified no-job/no-charge result and reservation first (§7), then retry
only that item with a currently returned supported `declined_preset_id` and identical creative
parameters; never invent or reuse a historical ID. Mandatory service consent cannot be bypassed or
turned into a picker. Use an already authorized suitable alternative or report the dependent branch
as blocked/partial declaratively. A recommended preset never authorizes an unrelated style purchase.

**Genjutsu preset gallery (VERIFIED, `get_presets`):**

```json
{ "source": "genjutsu", "category": "genjutsu", "limit": 12 }
```

- Categories: `genjutsu`, `genjutsu-trending` and `genjutsu-new`. Items look like `{id: "genjutsu:<uuid>", name,
  description (contains the driving-video URL), kind: "genjutsu-motion", type, thumbnail_url, preview_url}`,
  paginated by `next_cursor`. The response's `source` field said `marketing_studio`, a quirk.
- For optional preset execution, let the selected preset and source media carry the look and motion. Use an empty prompt only if the actual contract accepts it; otherwise keep one short operation/preservation sentence, at most two and at most 40 words. Never force a detailed scene description.
- Items carry **no price**. Browsing never authorizes `execute_preset`. Item descriptions tell the agent to call
  `get_preset_instructions({preset:"genjutsu"})` before a custom follow-up. That entry was **not read** in this
  scout (out of scope); read it before building on a gallery preset.
- Anime does not automatically select a preset. Prefer the two-reference image edit (§5.3) where it preserves the source composition/style and the replacement identity, then choose only the continuation required for motion. Use a Genjutsu catalog preset optionally when its verified instructions better preserve the requested result. `get_presets(source: "genjutsu")` catalog entries are not the public `higgsfield/genjutsu/restyle/v1.0` API preset list: never interchange identifiers, endpoints or fields. Consult [Genjutsu routing](genjutsu-routing.md) for the distinction. No forced restyle, extra paid job or picker.

---

## 12. Existing payment and allowance choices

When the live contract defines `use_unlim:false` as ordinary existing-credit billing, set false from already-established task/account credit authority to avoid an unnecessary allowance picker. This creates no new spending authority: the finite plan and account limits still apply. Set `use_unlim:true` or `use_free_gens:true` only from an applicable existing explicit allowance choice verified against live entitlements. Store supported choices as boolean plan-line fields before quoting; the ledger includes them in generated params and the exact-request fingerprint. Do not start trials or switch to an uncovered payment source. If authority is unavailable, use an already authorized faithful fallback or report a declarative limitation; never ask for spending confirmation.

If a tool returns `unlim_choice` without submitting, resolve it noninteractively only through a documented choice already covered by the authority above. Reconcile the no-job/no-charge reservation outcome first. A genuinely new mandatory payment choice or fresh interactive consent cannot be bypassed: do not invent consent, open a picker or purchase/trial widget, ask a question, or enter a waiting-for-user state. Use an already authorized faithful supported fallback or report the branch as blocked/partial declaratively. If a trial expires or a configuration is uncovered, do not silently switch payment sources or lower fidelity; continue only an already authorized covered configuration.

## 13. Failure statuses, refunds and canaries (VERIFIED from this account's records, 2026-10-08)

Matched one-to-one by count and timestamp in the saved transactions and the 100 most recent video jobs:

| Jobs (submit time)                          | Terminal status | Spend at submit | Refund                       |
| ------------------------------------------- | --------------- | --------------- | ---------------------------- |
| 6 × hf_mult_replace_object 1080p (03:47:24) | `ip_detected`   | 6 × -55         | 6 × +55 at 03:47:59–03:51:37 |
| 3 × seedance_2_5 720p 4 s (02:44:02)        | `nsfw`          | 3 × -28         | 3 × +28 at 02:44:07–02:44:10 |
| 1 × seedance_2_5 (02:46:14)                 | `failed`        | -28             | +28 at 02:46:34              |
| 1 × hf_mult_motion_control 1080p (04:03:03) | `failed`        | -44             | +44 at 04:03:46              |

Conclusions:

- `nsfw`, `ip_detected` and `failed` were **refunded automatically within ~5 s to about 4 minutes** in these historical account records. Current jobs require separate verification; account for their debits immediately.
- **What to tell the user:** report a current refund only after matching it in current `transactions`. If unresolved, state the debit and unknown refund status. Do not transfer this historical account claim to the current account or promise that blocks are free.
- The 6 × -55 replace charges are consistent with ceil billing of Altman's 100-frame (4.17 s) pads: 5 s × 11.
  That explains Altman's ~800 cr v1 (13 × 55 = 715 for the renders that succeeded) without any charged block.
- An HTTP 422 on replace for a too-short input was not charged (FROM-EVIDENCE, Aura).
- **A historical refund is not a guarantee.** Retain each debit against the plan until its refund is verified. A COMPLETED job whose footage is
  unusable also consumes the budget. Planned canaries limit this risk:
  - the canary is the cheapest planned job of each family (model + identity image set + set or world), at the
    final settings, so a pass is usable footage;
  - submit each family's canary individually through reservation → single request → immediate registration (§7); each family's other jobs wait for its own canary;
  - Moderation/IP rejections stop the refused generation path. Use only supported recovery that does not defeat the restriction; source reuse is preferred when it fulfills the request.
  - Never add a canary job that serves no cut. Filter verdicts arrive within minutes, so a canary is fast.
- `transactions` items carry `display_name`, `credits`, `action` (spend/refund) and `created_at`, but **no job
  id**. The ledger (`plan/ledger.json`, written by `ledger.py add` at submit) must store job ids and match refunds by
  display name, amount and time (`ledger.py status --state refunded`). Display names
  seen: "Seedance 2.5", "Higgsfield Genjutsu - Object Swap", "Higgsfield Genjutsu - Motion Transfer", "Video
  Background Remover", "Nano Banana 2", "GPT Image 2.5 Flare".

Ledger check template: `transactions` `{"size": 100}` (paginate with `cursor` = `next_cursor`), plus `balance`
`{}` at run start and end.

**Reconcile by model + time, and expect foreign charges (VERIFIED live 2026-10-08).** The live run reconciled
exactly: quoted 83.12 = charged 83.12 for the Katana remake, 111.12 in total with the swap. Meanwhile another
chat on the same account spent 496 cr (8 Nano Banana 2 + 8 Seedance at 16:49–16:53 UTC). So:

- match each ledger job to a transaction by display name (model) + amount + a time window around its own
  submit (and its refund, if blocked);
- list the transactions that match no ledger job as "not from this run" in the spend report; never add them to
  this run's spend, and never treat a balance difference as this run's cost;
- the balance before and after is only a cross-check when no other session is active.

---

## 14. Known errors and what they mean

| Symptom                                                                                                | Meaning                                                                                                                                                                                                                                                                | Action                                                                                                                                                                                                                   | Tag                                        |
| ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ |
| `notice.type = preset_recommendation` (single) / `submission_failed` + `preset_recommendation` (batch) | Server proposed a preset; no job, no charge                                                                                                                                                                                                                            | Resubmit only that item, same params + the `declined_preset_id` read from this response (§11)                                                                                                                            | VERIFIED / FROM-EVIDENCE                   |
| `unlim_choice`                                                                                         | User holds a covering allowance; nothing submitted                                                                                                                                                                                                                     | Honor existing explicit payment choice; otherwise authorized faithful fallback or declarative blocked/partial result, with no picker or question                                                                         | VERIFIED                                   |
| `unlim_*` rejection                                                                                    | See §12                                                                                                                                                                                                                                                                | See §12                                                                                                                                                                                                                  | VERIFIED                                   |
| "Cost preflight is not supported inside a batch submission"                                            | the verified non-generating estimate inside `*_batch`                                                                                                                                                                                                                  | Quote with single calls                                                                                                                                                                                                  | VERIFIED schema / FROM-EVIDENCE            |
| Status `nsfw`                                                                                          | Moderation (wording, audio + generate_audio:true, IP costume)                                                                                                                                                                                                          | Verify any refund; do not disguise the same refused request. Use supported source reuse or report the blocked cut                                                                                                        | VERIFIED refund / FROM-EVIDENCE causes     |
| Status `ip_detected`                                                                                   | Genjutsu recognised a known film or anime scene (per scene)                                                                                                                                                                                                            | Verify any refund. Do not transfer the same refused content to another model; supported source reuse or a declarative limitation only                                                                                    | VERIFIED refund / FROM-EVIDENCE            |
| Status `failed` (no reason)                                                                            | Confirmed job failure; cause may be unknown                                                                                                                                                                                                                            | Verify terminal status and account for its debit without assuming a refund. One corrective retry is allowed only within the priced reserve and remaining hard ceiling; log the new ID and verify any refund separately   | Historical refunds only                    |
| HTTP 422 with empty body on hf_mult_replace_object                                                     | Input video under ~4 s                                                                                                                                                                                                                                                 | Export at 24 fps, ping-pong pad to 96 frames (4.00 s); price through the current video estimate first                                                                                                                    | FROM-EVIDENCE                              |
| get_cost error for a Genjutsu clip under ~4 s                                                          | Same min-length rule                                                                                                                                                                                                                                                   | Pad                                                                                                                                                                                                                      | FROM-EVIDENCE                              |
| `adjustments.medias[i].role` requested image → used image                                              | Role coercion, harmless                                                                                                                                                                                                                                                | Send schema keys                                                                                                                                                                                                         | VERIFIED                                   |
| `Model not found: text2image_soul_v2` (models_get)                                                     | Job-record name differs from the MCP id                                                                                                                                                                                                                                | Use `soul_2`                                                                                                                                                                                                             | VERIFIED                                   |
| Historical URL importer rejected HTML                                                                  | A page URL, not a media file                                                                                                                                                                                                                                           | Use the supported sandbox fetch, then the standard output upload; the historical importer is unavailable                                                                                                                 | FROM-EVIDENCE                              |
| PUT 403 / signature mismatch                                                                           | Missing `If-None-Match: *` or a Content-Type differing from the reservation's `content_type` (e.g. `rr_put` without the reply's type when it differs from the extension default, or `rr_save` without its 2nd argument on a slot not typed `application/octet-stream`) | Resend with both headers (new slot if burned); `rr_save '<url>' '<content_type>'`                                                                                                                                        | FROM-EVIDENCE (inferred code)              |
| PUT 412                                                                                                | Slot already written (single-use)                                                                                                                                                                                                                                      | Reserve a new slot                                                                                                                                                                                                       | UNVERIFIED                                 |
| Historical sam_3_video cost → HTTP 500 (CLI)                                                           | Historical cost endpoint gap                                                                                                                                                                                                                                           | Segmentation is allowed, but unknown price prevents paid submission; use local or existing masks until a supported estimate is available                                                                                 | FROM-EVIDENCE                              |
| Transport timeout on any generate call                                                                 | Submission outcome unknown                                                                                                                                                                                                                                             | **Do not resubmit.** Check `transactions` for a spend at that minute and `show_generations` `{"only_completed": false, "type": "video", "size": 24}` for the job by prompt/params; retry only if it truly does not exist | VERIFIED rule / UNVERIFIED recovery recipe |
| jobs_wait `type: "image"` on a video job                                                               | Cosmetic while queued                                                                                                                                                                                                                                                  | Ignore                                                                                                                                                                                                                   | FROM-EVIDENCE                              |
| MCP connector: "server isn't responding" during a long foreground `sandbox_exec`                       | A foreground call that waited ~100 s (`rr_wait 100`) outlived the connector                                                                                                                                                                                            | Keep foreground waits ≤ 45 s; run long work with `background:true` and poll (`sandbox.md`)                                                                                                                               | VERIFIED live 2026-10-08                   |
| Transactions you did not make                                                                          | Another chat or session on the same account                                                                                                                                                                                                                            | Reconcile by model + amount + time; report them as "not from this run" (§13)                                                                                                                                             | VERIFIED live 2026-10-08                   |
| Replace returns fewer frames than the pad (89 for 96)                                                  | Output length follows the model                                                                                                                                                                                                                                        | Map frames proportionally (§6.2)                                                                                                                                                                                         | VERIFIED live 2026-10-08                   |
| Seedance output clamps duration                                                                        | Unsupported duration is coerced to the nearest allowed value                                                                                                                                                                                                           | Always send an integer 4–30                                                                                                                                                                                              | VERIFIED schema                            |

---

## 15. Server workflow findings that matter for katana

### 15.1 ad-multiplier (v1.5, VERIFIED text): one job to swap the hero across a whole ref?

Historical comparison, not an allowed alternate model: what that workflow promised for **edit mode** (`model: "ad_multiplier"`, `mode: "video_edit"`):

- Input: exactly one source of **4.0–30.0 s inclusive**. The workflow forbids trimming, splitting, looping or
  clamping an out-of-range source.
- It keeps "source motion, performance, choreography, camera, **cuts**, lighting, pacing, display aspect ratio,
  exact final duration". A person replacement "covers every appearance of that mapped source person ... through
  cuts, entrances, exits, occlusions, motion blur, transitions". Captions, subtitles, UI, motion graphics, labels
  and branding are preserved unless targeted. The identity image is authoritative for the **complete look**,
  clothing included, unless a clothing override is given.
- It renders **silently** (`generate_audio:false`), and the source's default audio is restored in a sandbox
  finalize step.
- Calls: one `generate_video` per output, `count:1`, never batched. Roles: `video` (source) first, then `image`
  refs in `@ImageN` order. `duration = ceil(source)`, `"duration_policy": "strict"`, `"aspect_ratio": "auto"`,
  resolution 720p or 1080p. The prompt must be ≤3900 chars and must contain the exact unconditional block
  "Preserve every caption, subtitle, and other untargeted on-screen text element from @Video1 exactly as it
  appears ...".
- The workflow analyses the source with `video_analysis_create` (3–5 min, paid) and retries a failed position once.

**Answer:** on paper, yes: a single video_edit job is designed to swap one person across every cut of a ≤30 s
clip while keeping cuts, timing and on-screen text. **For katana it is an UNTESTED historical experiment, never
the default.** Select a required identity-change route by measured fidelity: source-frame image editing, direct Genjutsu or a permitted Seedance edit, as applicable (§5.3/§6, `routing.md`).

- **Run only when already explicitly requested and included in the finite plan.** Do not offer an optional experiment or add it to the required plan.
- **Historical cost comparison only.** Past notes compared a 480p experiment with per-cut work using historical rates. Those figures are not a current quote, required preview resolution or authorization for another job.
- **Current execution:** use the exact live non-submitting estimate for the selected source, model, mode, resolution and duration, then register that finite required job. Choose settings from the measured delivery requirements. The first required job is its canary at intended final settings; do not automatically buy an unshippable draft followed by a second render. A separately requested experiment must already be included in the finite plan and must not silently add a follow-up purchase.
- **Routing tension.** The server's instructions say not to use ad-multiplier for one Genjutsu edit, and the
  `generate_video` description says "reserve ad-multiplier for explicitly requested independent variants". The
  same capability exists as `seedance_2_5` `mode:"video_edit"` (Ad Multiplier is "powered by Seedance 2.5",
  billed by source length; 4.04 s at 720p = 31 vs 28.29). If the user already requested it, use **`seedance_2_5`
  video_edit** (§6.4) with an Ad-Multiplier-style prompt.
- A whole-reel `hf_mult_replace_object` pass is the same kind of UNTESTED historical alternative.

Why it is not the default:

1. **Untested on fast-cut edits** (critic open question 1). Seedance redraws the frame, so garbled lettering,
   cut drift and loss of 1–3-frame flashes are plausible. The Altman user's own whole-reel MT pass (a different
   model, 14.04 s) lost the window, typography, cut sync and likeness quality (FROM-EVIDENCE).
2. **It redraws every frame**, so KEEP cuts lose their original pixels and the per-cut KEEP savings disappear.
3. A ref longer than 30 s would have to be split at cut boundaries, which is katana's own decision outside
   that workflow's contract.
4. Outputs are silent. Restore the ref audio by stream copy in finalize, as the workflow does. The workflow's
   paid `video_analysis_create` step is skipped: katana's sandbox analysis is free.

### 15.2 video-editing / Higgsedit (v1.0, VERIFIED text): can it be the renderer?

- Higgsedit is a native Node CLI (v0.14.0; the pinned release is `/opt/fable/VERSION.json`) with a JSX script API:
  `project({dir,size,fps,background})`, `p.add`, `p.cut(handle,{from,dur,at,fit})`, `p.compose(nodes,{at,dur})`,
  `p.frame`, `p.render(out,{codec,bitrate,depth,...})`. Commands are `higgsedit build|inspect|frame|sheet|render|do`.
- It covers frames, text, shaped fonts, masks and mattes, keyframes, transitions, a 2.5D camera, filters, motion
  blur, custom GLSL, contact sheets, and H.264/HEVC Main10/AV1 output.
- Limits: no HTML scenes, no runtime animation callbacks, no native LUTs, no shader adjustment nodes. GLSL is
  RGBA8, and 10-bit output can fall back to 8-bit compositing. There is no MCP publish or sync of editable
  projects; deliver a rendered file via media_upload.
- The text names a dev sandbox alias (`mcp-sandbox-dev`), and the brief's verified environment list does not
  mention `higgsedit`. **Whether it is installed in the production sandbox is UNVERIFIED.** One free check
  settles it: `command -v higgsedit && higgsedit --help | head && cat /opt/fable/VERSION.json`.

**Answer:** it could render cut assembly, text and simple mattes, but katana's effect catalog (Canvas2D
ctx.filter looks, composite-op textures, per-frame doodles, threshold or xerox looks, LUT-style grades) maps
better to the Chromium compositor, which is verified in the sandbox. Treat Higgsedit as optional and secondary,
not the renderer.

### 15.3 video-montage (VERIFIED text)

- Scripts are preinstalled at `$HF_WORKFLOWS/video-montage/scripts/` (`transcribe_words.py`,
  `audio_to_captions.py`, `make_captions.py`, `caption_placement.py`, `burn_caps_clean.sh`, `fetch_fonts.sh`,
  ...). The workflow says to run them in place and never read their contents into the conversation.
- Assembly rules worth reusing: probe every source; hard cuts by default; for matching codecs use an explicit
  concat manifest with stream copy; never claim success from an exit code, so verify duration, streams,
  first/last frames and every join; reserve upload slots before the producing command.
- Relevance: only for references with speech captions (burned subtitles). The katana text pass (pixels from
  the ref) covers stylised overlay text.

### 15.4 Server scene analysis (VERIFIED schema; not used by katana)

```json
{ "video_input_id": "<confirmed ref media_id>" }
```

or `{"youtube_url": "https://www.youtube.com/..."}` (YouTube hosts only). Then poll `video_analysis_status`
`{"video_analyze_id": "<id>"}` every 30–60 s until `completed` (scenes) or `failed` (fail_reason). It takes 3–5 min,
gets less accurate on long videos, and is paid (~2.2–2.3 cr per call observed, FROM-EVIDENCE). **katana never
buys it** (`budget.md` §1 never-buy list): its own sandbox analysis is free and frame-exact. The shape is kept
here only for reference.

---

## 16. Runtime identifiers

Use only the current user's supplied media, completed jobs and actual tool responses. Do not copy historical account IDs, creative identities, voice presets or stand-in media into probes or generation. A cost-only request may omit media only where the live estimate contract allows that omission; a price does not establish generation readiness.

## 17. Still unverified (needs a free probe or a canary)

Settled by the live run (VERIFIED live 2026-10-08), no longer open:

- the draft finalize price (full 1080p rate: 4 s → 48; no `duration` → 5 s / 60; always 1080p, 720p ignored);
- the charge for an exact 96-frame (4.00 s) replace pad at 720p (28, equal to get_cost);
- Genjutsu replace 720p output (994×830, 96-frame pad → 1054×880, 24 fps, 89 frames);
- Seedance 720p 4:3 output (1112×834 H.264, 24 fps) and the draft output (752×560);
- mixed models in one `generate_video_batch` call (accepted);
- a get_cost preset bounce reproduces on the real submit unless `declined_preset_id` is sent.

Still open:

1. Whether a finalized draft keeps the draft's motion and framing (no finalize job has run), and whether its
   real charge equals the get_cost figure.
2. The real 1080p charge on an exact 96-frame replace pad (44 by get_cost, FROM-EVIDENCE; no 1080p job yet).
3. Pre-emptive `declined_preset_id` on an item that did not bounce.
4. `seedance_2_5` video_edit as a whole-ref hero swap on a multi-cut edit. Only as the already explicitly requested experiment
   line (§15.1), never by default.
5. Seedance `start_image` versus `@imageN` numbering; a G4 keyframe as the `start_image` of a multi-shot plate
   (only shot 1 is pinned; untested); several reference frames as extra `image` to pose each shot
   (multi-ref structural pose refs; untested, must fit the actual model limits); nano_banana_2 tag binding.
6. Exact PUT error codes (a historical second PUT was expected to return 412); the removed
   legacy URL importer is not an available operation to probe.
7. Whether `ip_detected` counts in `jobs_wait` `summary.failed`.
8. Whether Higgsedit is present in the production sandbox.
9. `get_preset_instructions({preset:"genjutsu"})` content (not read in this scout).
10. The 2-ref still (§5.3) as an MT input, and whether nano_banana_2 refuses a famous film frame as an image ref.
11. Genjutsu 1080p output size for a non-4:3 pad (only 4:3 and portrait 1080p outputs are on record).
