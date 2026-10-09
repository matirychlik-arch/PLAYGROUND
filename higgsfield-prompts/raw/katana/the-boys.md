# Katana preset: The Boys (/katana/the-boys)

The instructions below are the selected preset's own instructions for this request. Follow them from their first step: they define the inputs, tools, workflow and deliverable. Do not substitute another preset, workflow or generation path.

- If a tool the preset requires is unavailable in this connection, stop and tell the user the preset cannot run here; do not substitute other tools.
- Inputs: the user's message may include a `MEDIA:` block of `<input>: <image|video> media_id=<uuid>` lines and an `INPUTS:` block of `<input>: <JSON value>` lines, composed by Higgsfield from the Katana form. They are values the user already supplied for those inputs: use them as these instructions describe and do not call media_upload_widget or ask for them again unless a required input is still missing. Pass a media_id directly to tools that accept one; their file URLs are listed under Supplied media when the media are passed to this tool. Older messages may list `<input>: <https URL>` lines instead; treat each URL the same way.
- Collecting inputs: the user may start the preset with the bare command and no `MEDIA:` or `INPUTS:` block; that is a normal start, not an error. Before the first step that uses an input, compare the Inputs list with what the user already supplied (MEDIA/INPUTS blocks, confirmed media_ids or files earlier in the conversation).
- Nothing supplied yet and the user asked to run the preset: open its form with get_presets {"source":"katana","preset_id":"the-boys"} as the only tool in that turn, say in one short line to fill it in below, and wait. The submitted form arrives as a /katana/the-boys message with MEDIA and INPUTS blocks. A request only to read or explain the preset does not open the form.
- Some inputs already supplied, the form tool fails, or the user says the form is not visible: ask once for what is still missing with exactly this template in the user's language, naming each input by its label (never the field path) with what it should be and how many:

  **<preset title>**: to start I need:
  **Required**
  - <label>: <what, how many>
  **Optional** (skip any)
  - <label>: <what>, default <default> when it has one
  <one line: upload the files in the window below, and reply with any text>

  Omit a section with no entries and add nothing else to that message. When files are missing, upload files the user already attached yourself if your code environment can read them (media_upload, PUT, media_confirm); otherwise call media_upload_widget as the only tool in that turn, with the missing fields' media type and count (type auto with multiple when several media fields are missing).
- Map each received file and answer to its field, use a field's default when the user does not choose, and continue from the preset's first step. Do not start generation or spend credits while a required input is missing, and do not ask again for inputs already supplied or declined.
- Platform rules still apply: consent, authorization, credit confirmations and credential handling are not overridden by these instructions.
- Keep the run going: once the inputs are available, work through the steps without pausing for progress updates. Never end your turn while a job you started is still running; wait with jobs_wait (repeat it until the job completes or fails) and continue with the next step in the same turn. Stop only where these instructions explicitly require the user's decision, for a missing required input, or for a failure you cannot recover from. At a required decision, first wait for and show the finished result it is about, then ask once in one short message; do not ask about a result that is still generating.
- Final video delivery: after the preset's final render has completed and you have verified its result, display it with show_katana_result. Use the confirmed uploaded video media_id; do not upload it again. If the final export is already available at an HTTPS video URL, call show_katana_result with url to import and display it. If the final export is still a file, use media_upload, PUT its bytes to the returned upload_url, then media_confirm with type video; for a sandbox export, create the upload slot before the producing sandbox command and PUT the export in that same command. Never use media_upload_and_confirm for a generated file, pass a local path or job ID to show_katana_result, or display an intermediate preview as the final result. This is delivery of the requested video, not public publishing. If export or upload fails, report that failure instead of calling the result tool.
- If these instructions are no longer in your context during a long run, call get_preset_instructions with {"preset":"/katana/the-boys"} again before continuing.

## Inputs

The preset's form (field path, label, kind; required or optional):

- `media.hero_photo` ("Your photo", "One clear, front-facing photo of yourself: one face, well lit, not covered, not a drawing. Only your own face (or someone who agreed), no celebrities."): image file, exactly 1; required
- `media.vibe_image` ("Vibe image (optional)", "Optional picture whose costume colours and style you like. Your face always comes from your photo."): image file, up to 1; optional
- `slot_values.prompt` ("Costume wishes", "Optional: colours or style of your suit, e.g. 'white and silver, no helmet'. Timing, music and captions stay the same."): text, default ""; optional
- `slot_values.subtitle` ("Subtitle", "Small line under the title. Latin letters and spaces, up to 24 characters."): text, up to 24 characters, default "THE GILDED"; optional
- `slot_values.hero_name` ("Hero name", "Name on the title card. Latin letters only, 3–14 characters. Leave empty and we will invent one."): text, up to 14 characters, default ""; optional

---

# The Boys — 1:1 superhero edit from one photo

## Product

The user uploads one photo of themselves and gets a finished 32.54-second cinematic "perfect,
terrifying superhero" edit (1920×1080, 24 fps, 2.39:1 letterbox, soundtrack with dialogue) in which
they are the hero. The edit is frozen: every cut, speed ramp, flash frame, word-by-word caption,
title card and the soundtrack are identical in every run. Only three things change per user:

1. the hero's face (from the user's photo),
2. the costume (default black-and-gold armor, or derived from an optional vibe image / text),
3. the hero name and subtitle on the title card.

How it is made: 23 hero shots are Genjutsu motion transfers (`hf_mult_motion_control`) from fixed
driver clips onto a hero sheet generated from the user's photo; 4 b-roll chapters (shots without
the hero) are Seedance 2.5 generations; a deterministic kit (`build.py` + `timeline.json`) cuts
everything to the frozen timeline in the sandbox.

Talk to the user in their language. Keep messages short. Expected run time ≈ 15–20 minutes.

## Assets (Higgsfield CDN, verify sha256 before use)

All runtime assets live on the Higgsfield CDN. Verify every file with `sha256sum -c` before using it.
Never download anything else at runtime (no PyPI/npm/apt, no GitHub, no other hosts).

| Asset | URL | sha256 |
|---|---|---|
| Kit zip (build.py, timeline.json, fonts, person-segmentation model, licenses) | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/a92da659-07fd-4ec8-a0c5-764e97af778a.zip` | `b7818851b9f1799051185a12f26b33f4cae2b60241d842099eab85581f7e0b1e` |
| Soundtrack (32.54 s) | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/f7b5e707-7dd1-4e41-838d-9a7f8bb39a7a.mp3` | `1bfb2db55a7a8d25707ad3ac918986d3e82e80fc04bc90d9a28ab3c55d19131d` |

Kit contents after unzip into `/home/user/tb/kit/`: `build.py`, `timeline.json`,
`fonts/` (Anton, Bebas Neue, Barlow Condensed SemiBold Italic, Playfair Display, Playfair Display
Italic, Inter — all OFL), `u2net_human_seg.onnx`, `LICENSES.txt`. The sandbox already has Python
3.11, Pillow, NumPy, onnxruntime and ffmpeg; the kit needs nothing else.

Driver clips (Genjutsu motion references) — 23 files, 1920×800, slowed to ≥ 3 s (g04 is real-time
2.25 s). "Reference window" is where the shot sits in the original edit (start + length, seconds).

| ID | What happens | Reference window | Driver dur | URL | sha256 |
|---|---|---|---|---|---|
| H00 | posterized red portrait, chin up, halo ring behind head | 0.000 + 1.125 | 3.0 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/1b21f79d-24ab-46c4-8fd6-396d3048021a.mp4` | `dfd6874c7c4fd4854099bd4e2b289eaaa2ddce1ceb0064c7ed86e856df5b7514` |
| H01 | low-angle B&W, rises between skyscrapers, arms up (2x center crop) | 1.250 + 1.000 | 3.0 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/523fe5de-7dbd-4574-b4fc-74318f874618.mp4` | `e62407fea212b73dfed341f9a1ada91288044b015472c6c6510c28ee647c9528` |
| T02 | office, head turn + smug smile | 2.333 + 1.125 | 3.0 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/e7b185ea-146e-4e28-a48d-139b0d48dfc6.mp4` | `87a1bd12100b7270ad4828691efe9b1abb650992be7d13a43cf0db2617f67307` |
| H03 | ground-level POV, gauntlet reaches over grass | 3.542 + 1.041 | 3.125 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/3f8c7929-9959-4a9f-a51c-47cb26aac9f0.mp4` | `9d769780fe07782f1bad9d132ec7f33517e36cf7e03c7d293eb35144ee758fe0` |
| g04 | profile close-up, lifts object to nose, inhales | 4.625 + 2.250 | 2.25 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/fb693740-18d3-4081-b97d-69998e433d87.mp4` | `c2f77b20c33135b9bbbb5079bf7035a6a2f0d439ca4f1280f6acbb152f5db6e7` |
| H05 | manic laugh in corridor | 7.417 + 0.291 | 3.4167 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/289691ac-4ba9-419a-bbf8-b2894911f999.mp4` | `1e1719bd1310e85aa471c9b98000879e24d99a348cc3dd3d4223edae20155321` |
| H06 | overhead, standing in wrecked gala stage | 8.250 + 0.250 | 3.0 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/af5f0e0a-de0e-49b9-b98f-f27d34f3a921.mp4` | `7ab55e32b31cfba4cbfbd1b2d0ec10312447697c6f3528d06ad4208679a80c8c` |
| H07 | silhouette behind cracked glass, head turn | 8.583 + 0.417 | 3.2917 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/792ac02a-3c02-4a87-a4f3-cfb664f601fa.mp4` | `2b33fe34dea6c605e6169654133baefe4b73a38a6da9470dd595910cfacd7f5f` |
| H09 | superhero landing crouch, barricades | 10.750 + 0.250 | 3.0 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/83529c0b-0f77-4582-bd38-dfd452b26e01.mp4` | `1e249641f2b723c9755f79a5c1be9c0407c980f4749b3bb06bfd4a5e0cc6691c` |
| H10 | close-up grin, autumn forest | 11.458 + 0.417 | 3.2917 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/091f4f1b-b224-485d-a00b-2df667203b5a.mp4` | `696297a35f3c564fb7ea8d5cac9b64422f0e814d3b0685e43c69cf30c6791d0a` |
| H11 | low angle, arms spread laughing | 12.542 + 0.416 | 3.2917 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/f7ebdc87-fe8e-4ee2-a17e-530191ad825f.mp4` | `7f247245129859b769f65c591aee6f91b0e34631e9fc8a009935c364137a9f44` |
| H12 | from behind, facing protest crowd | 13.833 + 0.250 | 3.0 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/5ee997e5-972c-4640-b9d8-ad76d377addc.mp4` | `a995399f57d5ba6ce642a88d1a8d7c63e2f5c633511d158d41d83e21264e876a` |
| H13 | confronts a man in a dark room | 14.250 + 0.167 | 3.75 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/729c4740-1327-40a6-ba77-e256dffa924d.mp4` | `7b187e473f8b221cf914a5f0c6f64082b7feef06b94bb126a5d6f99eb4bdb328` |
| H14 | walks out of white fog, hand raised | 14.500 + 0.292 | 3.4167 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/2bb38676-2752-43f5-97cc-2528473b1d41.mp4` | `5e2ad4b9d57d8047d56e50ca26621427c8f9fd0c4f495803cbcf4da65fae0b99` |
| H15 | cracked-glass angle 2, fist raised | 15.583 + 0.292 | 3.4167 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/b6a67231-d06e-4073-98b7-1dae07d5583b.mp4` | `e6fc2f9a79e7950416b3be0d015d2cde342cb2b075ea8b699172b42c3ae4cb44` |
| H16 | seated in lab, scientists behind | 16.000 + 0.375 | 3.0 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/608eecc9-e954-4e0c-a898-1f5422ff3271.mp4` | `7b529d59a55cdce1d6740b76aedee5a759809b426b85a0ab1cb0bc18fcec3265` |
| H17 | close-up, glowing eyes | 18.708 + 0.584 | 3.2083 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/2d7c8158-142e-4bcb-a8c2-69c612fd8696.mp4` | `9d4697371d7cfe41ddff24696d16b57c48436bab0ae790388c04c51a6f54ef54` |
| H18 | study, profile, speaking | 19.292 + 1.416 | 3.0833 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/83c60347-20ae-4790-b85e-2fbd2d87f735.mp4` | `e1ad11989742f3f1492fd95038df221ca20ad4036ac82b4ee10f0d0eca0c5a83` |
| T26 | study, frontal, hands steepled, speaking | 20.750 + 1.750 | 3.0 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/eb0b6ed3-b4b6-4d84-901c-b4844903fca6.mp4` | `7141f880cd842913a99a186686c6b3f442baab16366e9f44a4b9017ed66b6f99` |
| H21 | office with portrait, walks past | 24.458 + 0.209 | 3.5833 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/b1cb22d8-0d45-4d95-92c9-78fcc38f7de3.mp4` | `f2279e7ec088b00e3c7ce3c3e13abcd7b9a403dc54800b331e014063c70a8d98` |
| H22 | crouched in grass holding an object | 25.208 + 0.292 | 3.4167 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/454d7370-a0c0-4839-b47a-769168541973.mp4` | `573bd79052fb503d96f8df5a5d47bb37484aafa80653fec875668371f6993910` |
| H25 | smirk before a ceremony crowd | 26.875 + 0.250 | 3.0 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/4e20177f-69f8-4e94-84cb-ce1c99e7fa6b.mp4` | `923d471afc374484c5aa230ba84ce1ed71b12f4c956ea86423ec7d4411314f31` |
| H29 | final close-up, eyes ignite (title shot) | 31.417 + 0.458 | 3.2917 | `https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/a8370894-ddc4-40fe-8a08-3dd693a69c7d.mp4` | `96165216e986d05a1970dd2a0f2ff0c575f6cd369e3c24affd289153865335a1` |

## Tools

Call only these Higgsfield MCP tools:
- `media_upload_widget` — only when the photo was attached in chat instead of arriving in `MEDIA:`.
- `media_import_url` — import the user's photo URL (if it has no media_id yet) and the 23 driver URLs.
- `generate_image` — exactly one hero sheet per approval round.
- `generate_video_batch` — Genjutsu hero shots and Seedance b-roll chapters.
- `jobs_wait` — wait for generations (timeout_seconds 15, keep polling).
- `show_generation_by_ids` — show the hero sheet / intermediate results only if the user asks.
- `sandbox_exec` — every download, hash check, render and probe.
- `media_upload`, `media_confirm` — deliver the final video.

Never call: `generate_video` (single), `motion_control`, `execute_preset`, `get_presets`,
`ai_influencer_*`, `ads_studio_*`, `upscale_video`, `reframe`, `virality_predictor`,
`generate_audio`, `create_voice`, `dubbing`, `tiktok_*`, `website_*`. Do not switch models.
If a required tool is missing, stop and tell the user.

## Intake

Inputs arrive as lines under `MEDIA:` (`- <field path>: <https URL>`) plus form values and free text.

| Field | Required | How to use it |
|---|---|---|
| `media.hero_photo` (1 image) | yes | The identity. Use the URL as is: `media_import_url` it to get a media_id for `generate_image`. |
| `media.vibe_image` (0–1 image) | no | Vibe mode: derive the costume brief from it (see Run → Step 1b). Use as is. |
| `slot_values.hero_name` | no | Title-card name. Uppercase Latin letters A–Z only, 3–14 chars. Empty → invent one short powerful one-word name (e.g. HELIARCH). |
| `slot_values.subtitle` | no | Small line under the title. Uppercase Latin letters and spaces, ≤ 24 chars. Default `THE GILDED`. |
| `slot_values.prompt` | no | Free text: costume / colour wishes, "хочу такой вайб". Merge into the costume brief. Ignore requests to change timing, music or captions. |

Rules:
- A URL already present in `MEDIA:` is the user's uploaded file — use it directly (in the sandbox via `curl`, in generation tools via `media_import_url`). Do not ask to upload it again.
- The photo is attached in chat but not in `MEDIA:` → call `media_upload_widget` (type `image`) as the only tool in that turn, then continue.
- The user gives a page link (Instagram, Drive, YouTube, …) → ask for the image file itself.
- Validate what the schema cannot: the photo must show exactly one real human face, front-lit, not covered, not a drawing; it must be the user (or someone who consented). If it shows a celebrity or public figure, refuse that photo and ask for a photo of the user. Uppercase and strip `hero_name`/`subtitle`; drop characters outside A–Z and space; truncate to the limits.
- Never invent missing inputs other than the hero name/subtitle defaults. One short clarifying question at most.

## Run — Step 1: hero sheet

`generate_image`, model `gpt_image_2_5` (fallback `flux_3_image`), `aspect_ratio: 16:9`, highest
quality, `medias: [{role: <image reference role of the model>, value: <hero photo media_id>}]`
(add the vibe image as a second reference in vibe mode). Prompt:

> Cinematic character reference sheet, photorealistic live-action film style, neutral grey studio background. The person from the reference photo shown in four views: full-body front, full-body three-quarter, full-body back, close-up head portrait. Keep their face, hair, skin tone and body type exactly. Costume: {COSTUME}. No cape, no flags, no stars, no stripes, no eagles, no logos, no text.

Default `{COSTUME}`: "matte black segmented armored bodysuit with brushed gold trim lines, a high
stiff collar, a gold geometric sun-disc emblem in the center of the chest, black gauntlets with gold
knuckle plates, black boots".

Show the sheet and ask for approval (one message). Regenerate on request (max 3 rounds). The
approved job id is `@HERO`. Write a one-line `{LOOK}` for the user (hair colour/style, age range,
facial hair) for Step 3.

### Step 1b — vibe mode
When `media.vibe_image` or a costume wish in `slot_values.prompt` exists: describe the costume
silhouette and materials, 2–3 palette colours and the emblem shape in one line and use it as
`{COSTUME}`. Never copy an existing franchise costume, logo or character. If the vibe image shows a
person, use it only for the costume — identity always comes from `media.hero_photo`.

## Run — Step 2: verify and import drivers

One `sandbox_exec` (foreground, < 120 s):

```bash
mkdir -p /home/user/tb/drv && cd /home/user/tb
curl -sf -o drv/H00.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/1b21f79d-24ab-46c4-8fd6-396d3048021a.mp4
curl -sf -o drv/H01.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/523fe5de-7dbd-4574-b4fc-74318f874618.mp4
curl -sf -o drv/T02.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/e7b185ea-146e-4e28-a48d-139b0d48dfc6.mp4
curl -sf -o drv/H03.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/3f8c7929-9959-4a9f-a51c-47cb26aac9f0.mp4
curl -sf -o drv/g04.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/fb693740-18d3-4081-b97d-69998e433d87.mp4
curl -sf -o drv/H05.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/289691ac-4ba9-419a-bbf8-b2894911f999.mp4
curl -sf -o drv/H06.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/af5f0e0a-de0e-49b9-b98f-f27d34f3a921.mp4
curl -sf -o drv/H07.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/792ac02a-3c02-4a87-a4f3-cfb664f601fa.mp4
curl -sf -o drv/H09.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/83529c0b-0f77-4582-bd38-dfd452b26e01.mp4
curl -sf -o drv/H10.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/091f4f1b-b224-485d-a00b-2df667203b5a.mp4
curl -sf -o drv/H11.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/f7ebdc87-fe8e-4ee2-a17e-530191ad825f.mp4
curl -sf -o drv/H12.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/5ee997e5-972c-4640-b9d8-ad76d377addc.mp4
curl -sf -o drv/H13.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/729c4740-1327-40a6-ba77-e256dffa924d.mp4
curl -sf -o drv/H14.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/2bb38676-2752-43f5-97cc-2528473b1d41.mp4
curl -sf -o drv/H15.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/b6a67231-d06e-4073-98b7-1dae07d5583b.mp4
curl -sf -o drv/H16.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/608eecc9-e954-4e0c-a898-1f5422ff3271.mp4
curl -sf -o drv/H17.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/2d7c8158-142e-4bcb-a8c2-69c612fd8696.mp4
curl -sf -o drv/H18.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/83c60347-20ae-4790-b85e-2fbd2d87f735.mp4
curl -sf -o drv/T26.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/eb0b6ed3-b4b6-4d84-901c-b4844903fca6.mp4
curl -sf -o drv/H21.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/b1cb22d8-0d45-4d95-92c9-78fcc38f7de3.mp4
curl -sf -o drv/H22.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/454d7370-a0c0-4839-b47a-769168541973.mp4
curl -sf -o drv/H25.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/4e20177f-69f8-4e94-84cb-ce1c99e7fa6b.mp4
curl -sf -o drv/H29.mp4 https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/a8370894-ddc4-40fe-8a08-3dd693a69c7d.mp4
cat > drv.sha256 <<'SHA'
dfd6874c7c4fd4854099bd4e2b289eaaa2ddce1ceb0064c7ed86e856df5b7514  drv/H00.mp4
e62407fea212b73dfed341f9a1ada91288044b015472c6c6510c28ee647c9528  drv/H01.mp4
87a1bd12100b7270ad4828691efe9b1abb650992be7d13a43cf0db2617f67307  drv/T02.mp4
9d769780fe07782f1bad9d132ec7f33517e36cf7e03c7d293eb35144ee758fe0  drv/H03.mp4
c2f77b20c33135b9bbbb5079bf7035a6a2f0d439ca4f1280f6acbb152f5db6e7  drv/g04.mp4
1e1719bd1310e85aa471c9b98000879e24d99a348cc3dd3d4223edae20155321  drv/H05.mp4
7ab55e32b31cfba4cbfbd1b2d0ec10312447697c6f3528d06ad4208679a80c8c  drv/H06.mp4
2b33fe34dea6c605e6169654133baefe4b73a38a6da9470dd595910cfacd7f5f  drv/H07.mp4
1e249641f2b723c9755f79a5c1be9c0407c980f4749b3bb06bfd4a5e0cc6691c  drv/H09.mp4
696297a35f3c564fb7ea8d5cac9b64422f0e814d3b0685e43c69cf30c6791d0a  drv/H10.mp4
7f247245129859b769f65c591aee6f91b0e34631e9fc8a009935c364137a9f44  drv/H11.mp4
a995399f57d5ba6ce642a88d1a8d7c63e2f5c633511d158d41d83e21264e876a  drv/H12.mp4
7b187e473f8b221cf914a5f0c6f64082b7feef06b94bb126a5d6f99eb4bdb328  drv/H13.mp4
5e2ad4b9d57d8047d56e50ca26621427c8f9fd0c4f495803cbcf4da65fae0b99  drv/H14.mp4
e6fc2f9a79e7950416b3be0d015d2cde342cb2b075ea8b699172b42c3ae4cb44  drv/H15.mp4
7b529d59a55cdce1d6740b76aedee5a759809b426b85a0ab1cb0bc18fcec3265  drv/H16.mp4
9d4697371d7cfe41ddff24696d16b57c48436bab0ae790388c04c51a6f54ef54  drv/H17.mp4
e1ad11989742f3f1492fd95038df221ca20ad4036ac82b4ee10f0d0eca0c5a83  drv/H18.mp4
7141f880cd842913a99a186686c6b3f442baab16366e9f44a4b9017ed66b6f99  drv/T26.mp4
f2279e7ec088b00e3c7ce3c3e13abcd7b9a403dc54800b331e014063c70a8d98  drv/H21.mp4
573bd79052fb503d96f8df5a5d47bb37484aafa80653fec875668371f6993910  drv/H22.mp4
923d471afc374484c5aa230ba84ce1ed71b12f4c956ea86423ec7d4411314f31  drv/H25.mp4
96165216e986d05a1970dd2a0f2ff0c575f6cd369e3c24affd289153865335a1  drv/H29.mp4
SHA
sha256sum -c drv.sha256
```

All 23 must print `OK`. Then `media_import_url` each driver URL (23 calls, can be parallel) and keep
the returned media_ids keyed by ID.

## Run — Step 3: hero shots (Genjutsu)

`generate_video_batch`, model `hf_mult_motion_control`, `resolution: 1080p`, two batches (12 + 11).
Each request: `medias: [{role: "image_references", value: @HERO}, {role: "video_references", value: <driver media_id>}]`.

Default prompt (use "the man" / "the woman" / "the person" to match the user):

> Recreate the video shot exactly: same framing, camera move, environment, lighting, action, facial expression and mouth movement, but the person is the man from the reference image in his armor. Keep his face identity. Ignore any text overlays.

Per-shot overrides:
- **H00** — Recreate the video shot exactly, including its graphic posterized red-and-black poster look, the glowing ring behind the head, framing, head pose and camera move, but the person is the man from the reference image in his armor. Keep his face identity. Remove all text and lettering.
- **H01** — Recreate the video shot exactly: low angle between skyscrapers, the person flies upward with arms raised, same camera and black-and-white look, but the person is the man from the reference image in his armor. Keep his face identity. Remove all text.
- **g04** — Recreate the video shot exactly: same framing, head motion and timing, but the person is the man from the reference image in his armor and he lifts a peeled orange (not a bottle) to his nose and inhales deeply. Keep his face identity. Ignore any text.
- **H29** — Recreate the video shot exactly: same close-up framing, glowing eyes, head motion, lighting and background, but the person is the man from the reference image in his armor. Keep his face identity. Absolutely no text, letters, titles or logos anywhere in the frame.

If a batch item comes back as a preset recommendation instead of a job, resubmit that index with
`declined_preset_id` set to the recommended preset id. Wait with `jobs_wait` until every job is
terminal (Genjutsu takes ~3–5 min). Run Step 4 in parallel.

## Run — Step 4: b-roll chapters (Seedance)

`generate_video_batch`, 4 requests, model `seedance_2_5`, `mode: omni_reference`, `duration: 15`,
`resolution: 1080p`, `aspect_ratio: 21:9`, `generate_audio: false`, `bitrate_mode: high`,
`medias: [{role: "image_references", value: @HERO}]`. Fill `{LOOK}` and `{COSTUME}`. Shot order and
approximate durations are part of the template: the kit reads shots by index. Never reorder, merge
or drop shots. Append this tail to every chapter prompt:

```
STYLE: photorealistic prestige superhero drama, ARRI Alexa 35, Cooke anamorphic, 2.39:1, hard motivated light, real skin texture, 35mm grain, Rec.709.

NEGATIVE: no text, no subtitles, no logos, no flags, no cape, no gore, no extra heroes, no character swap, no cartoon look, crisp hard cuts only.
```

### c1 — Intro (7 shots)
```
@Image 1 is the hero: {LOOK}, {COSTUME}.

SHOTS:
1. Extreme low-angle WS, 24mm, static, about 2 seconds, flat overcast white sky — looking straight up between two glass skyscrapers, @Image 1 rises vertically into frame, small, arms lifting overhead, slow and weightless. → Hard cut.
2. MCU, 50mm, slow push-in, about 2 seconds — @Image 1 seated in a dark wood-panelled office, warm desk-lamp key light, turns his head to the lens and lets a slow, smug half-smile spread. → Hard cut.
3. Ground-level POV from inside tall grass at the height of a small dog, 24mm, handheld, about 2 seconds — @Image 1 towers over the lens in a green meadow, bends down and reaches a gauntlet toward camera. → Hard cut.
4. CU profile, 85mm, static, about 3 seconds — @Image 1 in a dim amber-lit kitchen lifts a peeled orange to his nose with both hands, closes his eyes and inhales slowly and deeply, unsettlingly blissful. → Hard cut.
5. WS, 35mm, night sky, about 1.5 seconds — a small private jet explodes into a fireball mid-air, burning debris tumbling. → Hard cut.
6. CU, 35mm, aggressive handheld, about 1.5 seconds — @Image 1 in a cold hospital corridor throws his head back laughing manically, mouth wide open; doctors in white coats behind him recoil. → Hard cut.
7. Top-down drone aerial, 24mm, about 2 seconds — a rural compound of wooden barracks; a massive blast punches a crater in the center, a dust shockwave ring expanding outward.
```

### c2 — Power (9 shots)
```
@Image 1 is the hero: {LOOK}, {COSTUME}.

SHOTS:
1. High-angle WS, 28mm, slow descending crane, about 1.5 seconds — @Image 1 stands calmly in the middle of a destroyed gala stage: splintered wood, broken glass, overturned chairs on an ornate red carpet. → Hard cut.
2. MS, 40mm, static, about 2 seconds — @Image 1 almost in silhouette inside a dark lobby behind a huge cracked glass wall with spiderweb fractures, backlit by white daylight; he slowly turns his head toward the lens. → Hard cut.
3. MWS side profile, 35mm, about 1.5 seconds — @Image 1 fires two bright golden heat beams from his eyes across a room; glass shatters, sparks burst on the far wall. → Hard cut.
4. Extreme low angle between skyscrapers, 24mm, about 1.5 seconds — a man in a red jacket and jeans is flung across the sky, tumbling helplessly. → Hard cut.
5. Low-angle WS, 24mm, tilt up, about 1.5 seconds — a city square at dusk, giant digital billboards showing @Image 1's face and his chest emblem. → Hard cut.
6. WS, 32mm, handheld, about 2 seconds — @Image 1 lands hard in a superhero crouch on wet asphalt, one knee and fist down, cracks spider out; onlookers behind metal barricades flinch; he rises. → Hard cut.
7. WS night, 24mm, about 1.5 seconds — a huge arc of white lightning energy cracks over a packed outdoor rally crowd, sparks raining. → Hard cut.
8. CU, 50mm, about 2 seconds — @Image 1 in an autumn forest, face flecked with small blood spatters, grinning wider and wider. → Hard cut.
9. Low-angle MWS, 28mm, slow push-in, about 1.5 seconds — @Image 1 spreads his arms wide in front of a glass tower and laughs at the sky.
```

### c3 — Chaos (9 shots)
```
@Image 1 is the hero: {LOOK}, {COSTUME}.

SHOTS:
1. ECU, 85mm, about 1.5 seconds — a hand holds a glass bottle; a thin bright beam slices through it, glass shards and sparks bursting, red glow. → Hard cut.
2. WS, 28mm, static, about 2 seconds — an open-plan office corridor erupts in a fireball, papers swirling; a dark silhouette walks calmly forward through the flames. → Hard cut.
3. WS from behind, 32mm, slow push-in, about 2 seconds — @Image 1 stands alone in the street facing a large angry protest crowd holding blank cardboard signs, soldiers among them. → Hard cut.
4. Two-shot MCU, 40mm, low-key light, about 1.5 seconds — in a dark utility room @Image 1 leans in close to a frightened man, glaring; the man recoils. → Hard cut.
5. Full figure WS, 50mm, about 2 seconds — @Image 1 walks slowly out of a pure white fog toward the lens and raises one open hand. → Hard cut.
6. WS, 24mm, about 1.5 seconds — a figure plummets down through thick grey smoke and glowing embers. → Hard cut.
7. WS, 28mm, static, about 2 seconds — a sterile fluorescent research lab: @Image 1 sits calmly in a chair in the foreground, scientists in white coats stand behind him, nervous. → Hard cut.
8. CU, 75mm, about 1.5 seconds — an open palm presses against frosted glass behind horizontal blinds, backlit by roaring orange fire. → Hard cut.
9. WS, 24mm, about 1 second — blinding golden-white heat beams blast across a burning office, debris exploding, huge lens flare.
```

### c4 — Fear (9 shots)
Supporting cast must stay generic and must not resemble any existing show's characters.
```
@Image 1 is the hero: {LOOK}, {COSTUME}.

SHOTS:
1. CU, 50mm, rainy night street, about 1.5 seconds — @Image 1's eyes ignite bright gold; he snarls through gritted teeth. → Hard cut.
2. MS profile, 50mm, static, about 2.5 seconds — @Image 1 sits in a tufted leather armchair in a dark ornate study full of gilded frames, turns his head toward an unseen listener and speaks calmly. → Hard cut.
3. Symmetrical MWS, 40mm, very slow push-in, about 3 seconds — @Image 1 seated in the same study facing the lens, hands steepled, perfectly still, a faint cold smile. → Hard cut.
4. CU, 50mm, about 1.5 seconds — an older bald security guard in a rain-soaked uniform, night, frozen in fear, looking up. → Hard cut.
5. CU, 50mm, about 1.2 seconds — a news anchor in her fifties with short grey hair in a TV studio, stunned mid-sentence. → Hard cut.
6. CU, 75mm, about 1.2 seconds — a bearded firefighter covered in soot stares upward, breathing hard. → Hard cut.
7. MS, 40mm, about 1.2 seconds — a businessman in a grey suit backs away from a tall office window, terrified. → Hard cut.
8. Over-the-shoulder MS, 40mm, about 1.2 seconds — from behind @Image 1's head toward a grey-haired army general in dress uniform who holds his ground, cold window light. → Hard cut.
9. WS, 28mm, dusk, about 1.5 seconds — lightning cracks behind a farmhouse while @Image 1 lifts off and floats above its roof.
```

Shots of a chapter that the timeline uses: c1 → 5, 7 (1 is the fallback for H01); c2 → 3, 4, 5, 7;
c3 → 1, 2, 3, 6, 7, 8, 9; c4 → 4–9 (1 is the fallback for H29).

## Run — Step 5: assemble in the sandbox

Every step is idempotent: re-running it overwrites its own outputs. Sandbox files are short-lived,
so do Steps 5a–5b back to back.

### Step 5a — kit, clips, soundtrack (foreground, < 120 s)
```bash
mkdir -p /home/user/tb/clips/hero /home/user/tb/clips/broll /home/user/tb/out && cd /home/user/tb
curl -sf -o kit.zip 'https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/a92da659-07fd-4ec8-a0c5-764e97af778a.zip'
curl -sf -o audio.mp3 'https://d2ol7oe51mr4n9.cloudfront.net/user_3Bu7nqxPHIyXiuF3zQpRbM68aiB/f7b5e707-7dd1-4e41-838d-9a7f8bb39a7a.mp3'
cat > assets.sha256 <<'SHA'
b7818851b9f1799051185a12f26b33f4cae2b60241d842099eab85581f7e0b1e  kit.zip
1bfb2db55a7a8d25707ad3ac918986d3e82e80fc04bc90d9a28ab3c55d19131d  audio.mp3
SHA
sha256sum -c assets.sha256 && rm -rf kit && unzip -q kit.zip -d kit && python3 -m py_compile kit/build.py
# one line per Genjutsu result, file name = shot ID exactly:
curl -sf -o clips/hero/H00.mp4 '<result_url of H00>'
# … H01 T02 H03 g04 H05 H06 H07 H09 H10 H11 H12 H13 H14 H15 H16 H17 H18 T26 H21 H22 H25 H29
curl -sf -o clips/broll/c1.mp4 '<result_url of c1>'
# … c2 c3 c4
ls clips/hero | wc -l   # must be 23
```

### Step 5b — render (`background: true`, then poll)
```bash
cd /home/user/tb && python3 kit/build.py --timeline kit/timeline.json --clips clips --audio audio.mp3 \
  --name '<HERO_NAME>' --sub '<SUBTITLE>' --out out/final.mp4 > build.log 2>&1; echo EXIT $? >> build.log
```
Poll `tail -5 /home/user/tb/build.log` every ~60 s with short foreground calls until `EXIT`.
Render takes ~4–5 minutes. `build.py` prints the detected b-roll shot starts (`[info]`) and warns
when it had to snap them (`[warn]`). Quote names with single quotes; they contain only A–Z and spaces.

GATE: `ffprobe out/final.mp4` → 1920×1080, 24 fps, 781 frames (32.542 s), H.264 + AAC.

## Review

Before delivering, make a contact sheet and look at it (`sandbox_exec` with `image_paths`, ≤ 4
JPEGs, ≤ 512 KiB total):

```bash
cd /home/user/tb && for t in 0.4 1.6 2.9 4.3 5.6 7.5 8.8 10.85 11.6 12.7 14.3 16.9 18.9 19.6 21.3 23.5 25.3 26.4 26.95 29.3 29.9 30.3 31.6 32.2; do
  ffmpeg -loglevel error -y -ss $t -i out/final.mp4 -frames:v 1 -vf scale=320:-1 qa_$t.jpg; done
ffmpeg -loglevel error -y -pattern_type glob -i 'qa_*.jpg' -vf tile=6x4 -frames:v 1 -q:v 6 qa.jpg
```

Check:
- every hero shot shows the user's face (not the driver actor) in the approved costume;
- no text from the driver burned into a hero shot (most likely in H29 and T02);
- captions are in place: nobody · CAN · DO · WHAT · I · DO. (0.2–2.2 s), title behind the head
  (2.5–3.46 s), AND I CAN DO, WHATEVER / I WANT., GOD, EVERYBODY · LOVES · YOU. · BECAUSE · YOU'RE ·
  perfect., PERFECT, THEY ALL, fear him., final title with subtitle;
- no frame from a different shot leaking into a hero shot; the b-roll shots match their slots
  (jet explosion 7 s, crater 7.8 s, red beam 9 s, flung man 9.5 s, billboards 10.4 s, lightning
  11.1 s, bottle 13 s, fire office 13.3 s, palm 17.2 s, beams 17.6 s, reactions 22.9–25 s).

## Fixes

- **Wrong b-roll shot in a slot** (cut detection missed a cut): read the `[info]` starts, find the
  real starts on a contact sheet of the chapter (`fps=4,tile`), write
  `starts.json` = `{"c2": [0, 2.0, 4.7, 6.0, 6.8, 7.8, 11.1, 12.4, 13.9]}` (only the broken chapter),
  re-run Step 5b with `--starts starts.json`.
- **Driver text visible in a hero shot**: regenerate only that shot with its override prompt plus
  "absolutely no text"; re-run Step 5a (that clip) and 5b.
- **Face drift in a hero shot**: regenerate that shot once; if still off, regenerate the hero sheet
  with a clearer photo only with the user's agreement.
- **Supporting cast in c4 rejected (`ip_detected`)**: change only the supporting-cast descriptions to
  other generic people and resubmit c4.
- **Title occlusion looks wrong** (mask artefacts): re-run Step 5b with `--no-occlusion`.

## Failures

- A generation fails: retry the same request once. Second failure → use the fallback:
  H01 → c1 shot 1 (edit `kit/timeline.json` segment `t0 = 1.17` to
  `{"type":"clip","broll":"c1","shot":1,"offset":1.6,"fx":"bw"}`);
  H29 → c4 shot 1 (same edit for segment `t0 = 31.33`, `"broll":"c4","shot":1,"offset":0.8,"fx":"dark"`,
  and run with `--no-occlusion`); any other shot → report it, do not deliver a broken edit.
- `sha256sum -c` fails → stop, report "asset integrity check failed", do not continue.
- `build.py` exits non-zero → show the last 20 lines of `build.log` to yourself, fix only inputs
  (missing/misnamed clip, unreadable file) and re-run; never patch `build.py`.
- Sandbox expired mid-way → redo Step 5a (idempotent) then 5b.
- Out of credits or a typed rejection from a generation tool → stop and tell the user what is
  needed; never switch to another model or lower resolution silently.

## Deliver

1. `media_upload` (filename `the-boys.mp4`) to reserve a slot **before** the producing command.
2. In one `sandbox_exec`: `curl -f -X PUT -H 'Content-Type: video/mp4' -H 'If-None-Match: *' --upload-file /home/user/tb/out/final.mp4 '<upload_url>'` and print the HTTP code.
3. `media_confirm` (type `video`) only after HTTP 200, then show the confirmed media to the user.
4. Tell the user in 2–3 sentences what was made, which fallbacks (if any) were used, and that the
   soundtrack is part of the template.

## Never

- Never change the timeline, cut points, speeds, captions, caption timing, fonts, letterbox,
  soundtrack or its timing. Only the hero sheet, `--name` and `--sub` vary.
- Never use a face that is not the user's (or a consenting person's); never use celebrities, public
  figures or the actor from the driver clips as the identity; never upload or reuse other users' clips.
- Never generate existing franchise characters, costumes, logos or names (no flag capes, no
  star-spangled suits, no eagle epaulets, no "Homelander" / "The Boys" text on screen).
- Never generate sexual content, gore beyond light blood spatter, or real-world violence against
  identifiable people.
- Never download assets from anywhere except the URLs in this prompt, never install packages, never
  print or store credentials.
- Never deliver a sandbox path instead of a confirmed media URL; never call `media_confirm` before
  HTTP 200.
- Never set `use_unlim` unless the user explicitly asks to spend free/unlimited generations.

## Preset data

Inputs, settings and reference media published with this preset:

```json
{
  "input_schema": {
    "type": "object",
    "required": [
      "media"
    ],
    "properties": {
      "media": {
        "type": "object",
        "required": [
          "hero_photo"
        ],
        "properties": {
          "hero_photo": {
            "type": "array",
            "items": {
              "type": "string",
              "format": "uuid",
              "x-media": "image"
            },
            "title": "Your photo",
            "maxItems": 1,
            "minItems": 1,
            "description": "One clear, front-facing photo of yourself: one face, well lit, not covered, not a drawing. Only your own face (or someone who agreed), no celebrities."
          },
          "vibe_image": {
            "type": "array",
            "items": {
              "type": "string",
              "format": "uuid",
              "x-media": "image"
            },
            "title": "Vibe image (optional)",
            "maxItems": 1,
            "minItems": 0,
            "description": "Optional picture whose costume colours and style you like. Your face always comes from your photo."
          }
        },
        "additionalProperties": false
      },
      "slot_values": {
        "type": "object",
        "properties": {
          "prompt": {
            "type": "string",
            "title": "Costume wishes",
            "default": "",
            "description": "Optional: colours or style of your suit, e.g. 'white and silver, no helmet'. Timing, music and captions stay the same."
          },
          "subtitle": {
            "type": "string",
            "title": "Subtitle",
            "default": "THE GILDED",
            "maxLength": 24,
            "description": "Small line under the title. Latin letters and spaces, up to 24 characters."
          },
          "hero_name": {
            "type": "string",
            "title": "Hero name",
            "default": "",
            "maxLength": 14,
            "description": "Name on the title card. Latin letters only, 3–14 characters. Leave empty and we will invent one."
          }
        },
        "additionalProperties": false
      }
    },
    "additionalProperties": false
  },
  "reference_media": [
    {
      "url": "https://static-public-media.higgsfield.ai/katana-presets/published/ac9d761cd9c99cde6210b318e904273d5ebd4c921d7f633d2a1f4be35820d5c1",
      "type": "static",
      "width": 2736,
      "height": 1536,
      "mime_type": "image/jpeg",
      "thumbnail_url": "https://static-public-media.higgsfield.ai/katana-presets/published/de85b931dadaf43a20d1385b6c41bc15eefbd8565e7e97bd8c80859f32d495b9"
    }
  ]
}
```