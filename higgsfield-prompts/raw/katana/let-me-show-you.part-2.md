# Katana preset /katana/let-me-show-you: part 2 of 2

## 6. Run (preflight, photos, Genjutsu, review, fixes, render, delivery)

Order for every invocation: parse inputs (5.1) → 6.0 preflight → 6.1 photos → 6.2 drivers → 6.3 Genjutsu → 6.4 QA →
(6.5 if needed) → 6.6 render → 6.7 verify and deliver → 6.8 when `vertical` = yes.

### 6.0 Preflight

1. **`get_preferences`.**
   - `auto_create_project` false → omit `folder_id` everywhere.
   - `auto_create_project` true → call `list_workspaces` and pick the selected workspace (ask if ambiguous). Then call
     `create_project` once with `name: "Aura edit <RUN>"`, `workspace_id`, and `idempotency_key: "aura-<RUN>"`. Put its
     `default_folder_id` as `folder_id` on every Genjutsu request.
2. **`balance`.** Genjutsu 1080p costs ≈11 credits per output second:
   - A ≈ 66 (6.04 s output)
   - every other shot ≈ 44
   - all 9 ≈ **420**
   - recommend having ~500, which covers 1–2 retakes

   Under ~420: say how much is needed and offer `show_plans_and_credits` (`intent: "auto_refill"` when the balance is near zero, otherwise `"topup"`),
   relaying its response.
   Wait, then re-check `balance` after a top-up. If the user says their plan has unlimited Genjutsu, go ahead: the
   first submission will return `unlim_choice`. **Never start the first batch with fewer than 9 requests** (e.g. to fit a low balance): the render needs all 9
   clips. Resubmissions and retake batches carry only the shots being redone. Before
   each retake round, check the balance covers it.
3. **Tell the user the plan** in 2–3 lines (the "how long and how much" answer from section 1). Paid steps (the 9-shot
   batch, each retake round) follow the platform's consent rules. When those require confirmation, ask once for the
   whole batch with the credit estimate, not per shot. Otherwise continue straight to 6.1.

### 6.1 Character photos

1. **Get the photo URL(s)** (section 5).
2. **Collage, or a photo you haven't seen → split call 1** (F, step `split`).
   - **Several photos**: run call 1 once per photo, as step `split_<k>` (k = MEDIA order 1–3), with
     `image_paths: ["/home/user/aura_<RUN>_split_<k>/split/preview.jpg"]`.
   - **A photo whose preview shows ONE picture** is used as is: record its media_id (5.2) and URL as FULL or CLOSE now.

   The command:
   `python3 aura_kit/aura.py split '<photo url>' split`, with
   `image_paths: ["/home/user/aura_<RUN>_split/split/preview.jpg"]`.
   - **Look at the preview.** On a collage, the red boxes must sit exactly on the seams, with each numbered panel a
     single photo.
     - Missed or wrong seams → rerun call 1 with `--seam X[,X2]` at the approximate x positions (`--seam-y` for
       stacked panels).
     - `kind: "single"`: trust the preview, not the label.
       - Preview shows ONE photo → use it as is, with no call 2.
       - Preview shows several panels → rerun call 1 with `--seam X[,X2]` (side by side) or `--seam-y Y[,Y2]`
         (stacked) at the approximate seam positions. Auto-detection misses tall side-by-side collages (width/height
         ≤ 1.15) and all stacked ones. Convert from the preview: preview px × source width ÷ preview width.
   - **Choose panels.** FULL = the full-body panel; CLOSE = the frontal face close-up. Discard extra panels (profiles,
     back views); each Genjutsu request takes exactly one image.
   - **Split call 2** (F, step `split2`): reserve one `media_upload` slot per kept panel (`panel_<n>.jpg`,
     `image/jpeg`). Then run
     `python3 aura_kit/aura.py split '<photo url>' split <reuse> --keep <n1>,<n2> --put '<upload_url 1>' --put '<upload_url 2>'`.
     `<reuse>` is the `reuse` string call 1 printed (e.g. `--seam 916`, or `--seam-y …` for stacked). It keeps the
     panel numbers identical.
   - **Confirm.** Expect `PUT panel_<n>.jpg 200` for each, then `media_confirm` each (`type: "image"`). Record the
     FULL/CLOSE media_id and url.
3. **Assign roles** by looking at the photos (section 5 covers the no-full-body case).
4. **Fill the prompt slots** (section 7) from what you SEE:
   - Describe only what is visible. Never invent accessories.
   - **Pronoun rule:** use the user's own words if they gave gender or pronouns. Otherwise make the pronouns match
     `{WHO}`: "young woman" → she/her, "young man" → he/his, "person" → they/their.
5. **Detect the account** (section 3) from the photo's URL.

### 6.2 Driver media_ids

Owner account → use the cached IDs. Otherwise import all 9 (section 3). Record the shot → driver media_id map.

### 6.3 Genjutsu ×9 (≈420 credits, ~10–20 min)

Make one `generate_video_batch` call with all 9 requests. **Index = shot, always: A=0 B=1 C=2 D=3 E=4 F=5 G=6 H=7
I=8**. Retake batches keep these indexes; a batch holding only index 6 was accepted. Exactly one image per request:
- FULL photo for A, D, F, G, I
- CLOSE photo for B, C, E, H

The request shape is below. It is schematic: write all 9 requests out in full.
```json
{"context": "katana/let-me-show-you <RUN>: bare Genjutsu motion transfer of the user's character onto the reference shots",
 "requests": [
  {"index": 0, "params": {"model": "hf_mult_motion_control", "resolution": "1080p",
     "declined_preset_id": "24bae836-2c4a-48e0-89b6-49fcc0b21612",
     "prompt": "<prompt A from 7.2 with slots filled, then the {JEWELLERY} sentence>",
     "medias": [{"value": "<FULL photo media_id>", "role": "image_references"},
                {"value": "<driver A media_id>", "role": "video_references"}]}}
 ]}
```
Add `"folder_id": "<id>"` inside `params` only if preflight produced one.

**Submission problems:**
- `unlim_choice` instead of jobs: ask the user once, then send `use_unlim` with their answer on every later request.
- An item fails to submit: resubmit only the failed indexes.
- `429` / `rate_limit_reached`: wait with two sandbox calls (`sleep 30; echo ok`, `timeout_seconds: 60`), then
  resubmit only the failed indexes.

**Waiting:**
1. Call `jobs_wait` with `jobs: [{"index": i, "job_id": "…"}, …]` and `timeout_seconds: 15`.
2. If not all are terminal, wait with a sandbox call (`sleep 40; echo ok`, `timeout_seconds: 60`), then poll again.
3. Give the user a one-line status about every 3 polls.
4. Take each `result_url` from the jobs_wait result and record it with its job_id. A lost or expired URL can be
   fetched again with `jobs_wait` on the job_id.
5. When all are terminal, call `show_generation_by_ids` with the current indexed set. Do it again after every retake
   round, with the current 9 jobs.

**Failed or blocked jobs** (these are not QA retakes and don't count as retake rounds):
- **Limit**: a shot gets at most **3 failed or blocked submissions**; count them as `fail=` in STATE. QA retakes are
  counted separately, as rounds (6.4). A batch carrying both resubmissions and QA retakes counts as one QA retake round
  only if it contains a QA retake.
- **Generation error**: resubmit; next time, a simpler prompt (drop the `{LOOK}` details).
- **Moderation or IP block**, at any point: go straight to a tighter crop of that shot's photo.
  - CLOSE shots (B, C, E, H): crop to head and shoulders.
  - FULL shots (A, D, F, G, I): keep head to shoes; trim only background, other people and logos.

  Steps:
  1. Reserve a slot (`crop.jpg`, `image/jpeg`).
  2. Run F step `crop`: `python3 aura_kit/aura.py crop '<photo url>' c.jpg --box <x0,y0,x1,y1> --put '<upload_url>'`,
     with `image_paths: ["/home/user/aura_<RUN>_crop/c_preview.jpg"]`. Fractions 0–1 are easiest.
  3. Expect `PUT c.jpg 200`, check the preview, then `media_confirm`. Record it in STATE as that shot's `img=`.
  4. If it is blocked again, use the other photo.
- **Meanwhile**, QA the finished shots (6.4), so any QA retakes can join the next submission.
- **Still failing after 3 failed submissions**: tell the user the render needs all 9 shots and offer a different photo, a
  different crop, or stopping.
- Never switch models. No IP block was hit with these drivers in testing.

**Credits:** count the cost of each COMPLETED job (44, or 66 for A). Failed or blocked jobs are refunded; check with
`transactions` if unsure. Never use a balance delta: other sessions share the account.

**Genjutsu behaviour (measured):**
- **Output timing**: 24 fps. Drivers B–I (3.3–4.3 s) give 4.04 s / 97 frames; A's 5.9 s driver gives 6.04 s / 145
  frames.
- **Frame mapping**: output frame i = driver frame i. The plan plays shots at speed 25/24, with in/out points in 24ths
  of a second. Never time-stretch clips.
- **Copies from the driver**: framing and camera, motion and expression, bags, and sometimes jewellery. Any figure in
  the driver's frames is copied too, which is why the drivers contain clean frames only.
- **Takes from the photo**: face, hair and outfit. It also tends to take the photo's backdrop, so the E (loft) and F
  (street) prompts explicitly ask for the video's location.

### 6.4 QA before rendering (always, two calls)

**First QA**: both calls start with this heredoc (each runs in its own fresh directory). The config holds all 9 clips
plus the CLOSE photo, or the source collage, which shows ears and neck best:
```
cat > qa.json <<'CFG_EOF'
{"clips": {"A": "<url>", "B": "<url>", "C": "<url>", "D": "<url>", "E": "<url>", "F": "<url>", "G": "<url>", "H": "<url>", "I": "<url>"}, "photo": "<CLOSE photo or collage url>"}
CFG_EOF
```

**Call 1, overview** (F, step `qa`): `python3 aura_kit/aura.py qa qa.json qa`, with
`image_paths: ["/home/user/aura_<RUN>_qa/qa/qa_1.jpg", "/home/user/aura_<RUN>_qa/qa/qa_2.jpg"]`.

**Call 2, detail** (F, step `qad`): `python3 aura_kit/aura.py qa qa.json qa --detail`, with
`image_paths: ["/home/user/aura_<RUN>_qad/qa/detail_1.jpg", "/home/user/aura_<RUN>_qad/qa/detail_2.jpg"]`.

Judge jewellery ONLY on the detail view, against the USER PHOTO tile in it. The overview tiles are too small: a copied
choker was invisible there and obvious in the detail.

| Check | Look for | Fix |
|---|---|---|
| Identity | same face, hair, makeup as the photo | retake with the CLOSE photo, or a cleaner `{LOOK}` |
| Outfit | the user's outfit, not the performer's black tweed | retake with `{OUTFIT}` spelled out more concretely |
| **Jewellery** (detail view, judge by item) | A defect is any piece NOT in the user's photo: CC logo earrings, pearl or crystal chokers, necklaces, drop earrings. CC earrings on a user who wears small studs ARE a defect. The user's own pieces going missing is not a defect; mention it. | Chokers, necklaces, big logo earrings → paint out that driver (6.5) and retake. Tiny drop earrings → mention as a residual and offer the fix. Never clean for jewellery the user owns. |
| Bags | D, G and I carry the performer's bag: part of the choreography | expected; mention a visible logo as a residual |
| Ghost figure | a stray silhouette or second person in the LAST pair (overview) | lower that shot's `tmax` via `plan_overrides` (section 8) |
| Backgrounds | E: dim moody loft with dark windows; F: dusk overpass with teal sky and blurred passers-by | retake E/F with the location sentence moved to the front |
| Hands / pose | broken hands, a pose that differs from the reference | retake that shot |
| Frame counts | printed per clip: 97 (A: 145) | count ≤ the last number of "edit uses frames lo..hi" → retake |

**Retakes (QA retake rounds):**
- Submit one new `generate_video_batch` holding all shots to redo, with their original indexes.
- The other clips stay valid.
- QA the retaken clips with a config listing only the retaken shots, plus `photo`, under steps `qa_rN` and `qad_rN`.
- Choose `image_paths` by shot group BEFORE the call: any of A–E → `qa_1`/`detail_1`; any of F–I → `qa_2`/`detail_2`.
  Never list a sheet for a group with no retaken shot.
- Do at most 2 retake rounds without asking the user.

**Partial QA**: if some shots are still being resubmitted (6.3), run the first QA on the finished ones (steps `qa`,
`qad`, choosing image_paths by group as above). QA the late shots under `qa_pN`/`qad_pN`. These are not retake rounds.

### 6.5 Jewellery paint-out (when the detail view shows copied jewellery)

B, G and H are already painted out in the registry. `clean` always starts from the registry driver, so a spec for B, G
or H only needs the new remnants. Several shots at once: run their tiles/clean steps in separate dirs, then retake them
all in ONE batch (one retake round).

1. **Locate**, in two F calls, both step `tiles_X` (each rebuilds the dir):
   - **Call 1**: `python3 aura_kit/aura.py tiles X t.jpg` with `image_paths: ["/home/user/aura_<RUN>_tiles_X/t.jpg"]`.
     These are whole frames at 1/4 scale: tile px × 4 = 1920×1080 px.
   - **Call 2**: `python3 aura_kit/aura.py tiles X z.jpg --every 3 --zoom x0,y0,x1,y1`, with a box about 300–800 px wide
     around the jewellery, and `image_paths: ["/home/user/aura_<RUN>_tiles_X/z.jpg"]`.
   - If the QA detail sheet already shows where the jewellery is (detail px × 2 = 1920×1080 px), you can skip call 1.
   - Read positions straight off the grid: yellow labels are x, cyan labels are y, in 1920×1080 px.
   - Labels read `driver n = ref r`. Key the spec by `r`; the last frame of the range is always included.
2. **Write ONE spec for the shot**:
   ```json
   {"ellipses":[{"keys":{"77":[1500,735],"83":[1560,742],"89":[1560,765]},"axes":[85,195]}]}
   ```
   - **Keys**: reference frame numbers, linearly interpolated. Earrings swing, so give a key every 3–4 frames; a choker
     can take one about every 8. Always include the first and last frame of the range.
   - **Ellipses** are axis-aligned (no rotation), diffusion-inpainted from their border. Size the semi-axes about 1.3×
     the jewellery's half-size, and cover any tilt plus the pendant. By shot scale:

     | Shot scale | Earrings | Choker / necklace |
     |---|---|---|
     | close-up (B, C, E, H) | ~[45–100, 100–200] (B used [85,195], H [95,200]) | ~[150–230, 60–90] |
     | medium (A, G, I) | ~[18–25, 25–35] | ~[90–100, 35–45] (G used [95,38]) |
     | wide (D) | ~[10–15, 15–20] | |

     Ready examples: `aura_kit/clean_specs/B.json`, `G.json`, `H.json`.
   - **`bands`** (`{"keys":{"<r>":[x0,x1,y_top]},"fill":[r,g,b]}`) flat-fill the rectangle x0..x1 below `y_top`, with a
     soft 10 px edge (fill defaults to [22,20,20]). Use them only for jewellery lying on dark clothing at the bottom
     edge of the frame.
   - **`frames`** is optional; if given, it must equal the shot's range: A 0–73, B 77–89, C 94–128, D 133–160, E 165–195,
     F 199–230, G 235–265, H 270–302, I 306–332.
3. **Preview, without uploading** (F, step `cprev_X`; takes seconds):
   - Heredoc `spec.json`, then `python3 aura_kit/aura.py clean X spec.json clean --zoom x0,y0,x1,y1`. Expect
     `PREVIEW_DONE`.
   - `image_paths: ["/home/user/aura_<RUN>_cprev_X/clean/prev.jpg"]`. It shows before|after pairs at 6 frames.
   - Remnants left, or skin/hair smeared too far → fix the keys or axes and preview again (at most 2 fixes).
4. **Upload** (F, step `clean_X`, 15–35 s; for A use B mode, ~50 s): reserve a NEW slot (`drive_X_clean.mp4`, `video/mp4`), then run the same
   command with `--put '<upload_url>'`. Expect `PUT drive_X_clean.mp4 200` and `CLEAN_DONE`, then `media_confirm`
   (`type: "video"`). This gives the new driver's media_id and url.
5. **Check** (F, step `chk_X`): `python3 aura_kit/aura.py sheet '<new driver url>' s.jpg --n 8 --crop x0,y0,x1,y1`, with
   `image_paths: ["/home/user/aura_<RUN>_chk_X/s.jpg"]`. The jewellery must be gone in every tile.
6. **Retake shot X** with the new driver media_id. Record the driver and the spec in the ledger.

A painted area can come back slightly waxy (seen on H's ear). Keep ellipses tight.

### 6.6 Render (background)

1. **Reserve two slots** right before: `aura_<RUN>_v<N>_edit.mp4` and `aura_<RUN>_v<N>_compare.mp4` (`video/mp4`).
   `N` starts at 1 and goes up with every render attempt or re-render. Record both media_ids and urls.
2. **Run** (B, step `render_vN`). The heredoc is `config.json` with the 9 current result_urls, both upload_urls, the
   label and the `plan_overrides`: the look from `slot_values.look` (5.1), merged with any shot fixes. The command line is `python3 aura_kit/aura.py render config.json work`.
3. **Poll** (4.2). Expected sequence:
   - `downloaded clips, reference and models (sha256 OK)`
   - `rendering 355 frames (about 3 min)`
   - `compose [ …s] frame N`, every 25 frames (≈0.45–0.6 s per frame)
   - `compose [ …s] done edit.mp4 0`
   - `building compare.mp4`
   - two probe lines (1920x1080 and 1920x2160, 14.2 s)
   - `PUT edit.mp4 200`, `PUT compare.mp4 200`, `RUN_DONE`, `EXIT 0`

   The total is about 3.5–5 min.
4. **Failures:**

   | Log shows | Fix |
   |---|---|
   | `ERROR: config.clips is missing shots`, `config.put_* must be a media_upload upload_url`, `clip X: unexpected URL` | Fix the config. |
   | `ERROR: download failed` | A clip URL is wrong or expired; refresh it with `jobs_wait` on its job_id. |
   | `sha256 mismatch` | A CDN asset changed; report it. |
   | `ERROR: compose failed` | Read the traceback (`tail -n 40`); fix the overrides. |
   | `ERROR: upload failed`, or any PUT that isn't 200 | Re-run as v<N+1> with two NEW slots. Don't confirm either old slot. |
   | `EXIT` without `RUN_DONE` | Read `tail -n 40`. |

5. **Confirm** both media_ids with `media_confirm` (`type: "video"`).

**Look-only changes** (flat look, softer, no burns; section 8) are just a new render version: reuse the recorded clips,
use new slots and N+1. That's 0 credits, ~4 min. For `plan_overrides`, merge the previous version's overrides (from
STATE) with the new look keys, so shot fixes such as `tmax` survive.

### 6.7 Verify, then deliver

**Check the result** (F, step `final_vN`):
```
python3 aura_kit/aura.py sheet '<compare url>' final.jpg --frames 20,66,80,110,150,180,215,250,285,318,340,352 --cols 4
```
Pass `image_paths: ["/home/user/aura_<RUN>_final_vN/final.jpg"]`. The top half of each tile is the reference; the bottom
half is ours. Expect:

| Frames | What you should see |
|---|---|
| 20, 66 | red lyric words behind the subject (A) |
| 80 | B close-up, still bright from the frame-76 flash tail (with flashes off, not brightened) |
| 110 | C |
| 150 | the D walk |
| 180 | E, dark loft |
| 215 | F, dusk street |
| 250 | G |
| 285 | H, white halo |
| 318 | I laughing |
| 340 | teal dark with the bright ring |
| 352 | black (the ring has faded) |

Amber burns may show at frame edges, unless burns are off.

**Reply to the user with:**
1. The compare link (reference on top, ours below), the edit link, and the 9:16 link when `vertical` = yes (make it
   first, 6.8).
2. One line on what was done: 9 Genjutsu shots plus the compositor, and the look of this version. The default is
   exposure +10 %, contrast, clean grain, flash transitions and amber film burns; otherwise name the overrides, e.g.
   "original flat look: no exposure lift, flashes or burns".
3. Credits: the sum over completed jobs, retakes included (e.g. 9 shots + 1 retake = 418 + 44 = 462).
4. Residuals you saw, e.g. a small earring on a shot or a bag logo. Offer the fix and its cost.
5. A note that the audio is the reel's track, with explicit lyrics later in the song: fine for internal tests, but clear
   the rights before publishing.
6. Offer only the extras not already delivered: the 9:16 version, if not made, and the other looks (aura, soft, flat,
   minus the current one).

Never paste presigned upload URLs.

### 6.8 Extras (from `slot_values.vertical` = yes, or on request)

- **Vertical 9:16** of the latest delivered edit (vN, unless the user names another):
  1. Reserve a slot (`aura_<RUN>_v<N>_9x16.mp4`).
  2. Run B step `vert_vN`: `python3 aura_kit/aura.py vertical '<edit url>' v.mp4 --put '<upload_url>'`. Default
     `--mode fill` keeps the whole picture on a blurred background; `--mode crop` is a centre crop that cuts the words.
  3. Poll for `VERTICAL_DONE`, then `media_confirm` (`type: "video"`).
  4. Check with F step `vchk_vN`: `python3 aura_kit/aura.py sheet '<9x16 url>' v.jpg --n 6 --cols 6`, with
     `image_paths: ["/home/user/aura_<RUN>_vchk_vN/v.jpg"]`. Expect 1080×1920 tiles: the full 16:9 picture centred on a
     blurred copy (fill), with the red words visible in the A tiles.
  5. Put the 9:16 link in the 6.7 reply when `vertical` = yes, otherwise send it. Add it to STATE `renders:`.
  6. Never use the generative `reframe` tool for this without asking: it costs credits.
- **Look change and 9:16 requested together**: render v<N+1> first (6.6), verify it (6.7), then make the vertical from
  v<N+1>'s edit url, and deliver all links together. The 9:16 follows the look the user asked for.
- **Look variants**: a new render version with `plan_overrides` (6.6, 0 credits).

### 6.9 Run ledger (keep it current)

After each milestone, put a compact STATE block at the end of your message. Milestones: photos ready, drivers ready,
batch submitted, batch done, QA verdict, each retake, slots reserved, render done, delivered, vertical done. The
first milestone is "inputs parsed".

```
STATE run=<RUN> v=<last attempted N> delivered=<N|none> lang=<ru|en> owner=<yes|no> folder_id=<id|none> use_unlim=<n/a|true|false> credits=<sum of completed jobs> rounds=<QA retake rounds>
inputs: look=<default|flat|soft> vertical=<yes|no> notes=<slot_values.prompt, ≤80 chars|none>
photos: SRC=<k:media_id url, …> | FULL=<media_id> <url> | CLOSE=<media_id> <url> | crops: <shot>=<media_id> <url>
prompt: WHO=<…> pronouns=<…> LOOK=<…> OUTFIT=<…> TOP=<…> JEWELLERY=<default|own: …>
shots: A idx0 img=<FULL|CLOSE|crop id> drv=<media_id> var=<std|simple|locfirst> job=<id> url=<result_url> subm=<n> fail=<n> | … | I idx8 …
specs: <shot>=<spec json> drv_url=<url>
overrides: <current plan_overrides json|none>
inflight: step=<step> slots=<media_id> <url>, … (cleared when done)
renders: v1 edit=<id> <url> compare=<id> <url> look=<default|flat|…> | v2 … | 9x16 v<N>=<id> <url>
residuals: <…>
```

**Resuming after a long gap:**
- Rebuild from the last STATE block.
- If a job_id is known but its URL is lost, call `jobs_wait` on it.
- If job ids are lost, `show_generations` lists recent jobs (recovery only; this overrides the tool's display hint). Match on model `hf_mult_motion_control`, the filled prompt
  text (the `{LOOK}` and `{OUTFIT}` strings) and the input image media_id; other sessions on the account may run the
  same template.
- Slots older than ~1 h are stale: reserve new ones.

## 7. Prompts

### 7.1 Slots

| Slot | Meaning | Example (woman) | Example (man) |
|---|---|---|---|
| `{WHO}` | visible subject noun; add "young" only if they clearly look young | `young woman` | `man` |
| `{THEIR}` | possessive per the pronoun rule (6.1) | `her` | `his` |
| `{THEY_WEAR}` | per the pronoun rule | `She wears` | `He wears` (neutral: `They wear`) |
| `{LOOK}` | face, hair, makeup as visible | `wispy curtain bangs, long dark-brown layered hair, rosy blush and coral lips` | `short black textured crop, light stubble, thick brows` |
| `{OUTFIT}` | full outfit as visible | `mint-green velour zip track jacket over a white cropped tank top, matching mint velour wide-leg pants, white sneakers` | `red leather biker jacket over a black crew-neck tee, black straight-leg jeans, black boots` |
| `{TOP}` | upper garment only | `mint-green velour track jacket` | `red leather biker jacket` |

**`{JEWELLERY}` sentence**, appended to EVERY prompt:
- **Default (no jewellery in the photo):**
  `{THEY_WEAR} NO earrings, NO necklace, NO choker and NO jewelry of any kind: bare ears and bare neck exactly as in the image.`
- **Jewellery visible in the photo:**
  `{THEY_WEAR} only the jewelry visible in the image (<describe it>); no pearl choker, no logo earrings.`

### 7.2 The 9 prompts (fill the slots, then append the `{JEWELLERY}` sentence)

| Shot | Photo | Prompt |
|---|---|---|
| A | FULL | `The {WHO} from the image performs exactly the movement of the person in the video, with the same framing and camera. Keep {THEIR} face, {LOOK}, and {THEIR} outfit from the image: {OUTFIT}. Cream seamless studio background. 35mm film look.` |
| B | CLOSE | `The {WHO} from the image performs exactly the head movement and expression of the person in the video, in the same tight close-up framing. Keep {THEIR} face, {LOOK}, and {THEIR} {TOP} from the image. Cream studio background. 35mm film look.` |
| C | CLOSE | `The {WHO} from the image performs exactly the head movement, lip movement and expression of the person in the video, in the same tight close-up framing. Keep {THEIR} face, {LOOK}, and {THEIR} {TOP} from the image. Cream studio background. 35mm film look.` |
| D | FULL | `The {WHO} from the image walks exactly like the person in the video, in side profile across the frame, with the same wide framing. Keep {THEIR} face, {LOOK} and {THEIR} outfit from the image: {OUTFIT}. Cream seamless studio. 35mm film look.` |
| E | CLOSE | `The {WHO} from the image performs exactly the movement of the person in the video: hand behind the head, slow head turn, same close framing, in a dim moody loft with dark windows like in the video. Keep {THEIR} face, {LOOK} and {THEIR} {TOP} from the image. Low-key cinematic 35mm look.` |
| F | FULL | `The {WHO} from the image moves exactly like the person in the video, walking at dusk on a city overpass and glancing back over the shoulder, with blurred passers-by and a teal evening sky like in the video. Keep {THEIR} face, {LOOK} and {THEIR} outfit from the image: {OUTFIT}. Cinematic 35mm night look.` |
| G | FULL | `The {WHO} from the image performs exactly the pose and movement of the person in the video, hands on hips, same medium framing. Keep {THEIR} face, {LOOK} and {THEIR} outfit from the image: {OUTFIT}. Cream studio background. 35mm film look.` |
| H | CLOSE | `The {WHO} from the image performs exactly the head tilt, smirk and expression of the person in the video, in the same tight close-up framing. Keep {THEIR} face, {LOOK} and {THEIR} {TOP} collar from the image. Cream studio background. 35mm film look.` |
| I | FULL | `The {WHO} from the image laughs and moves exactly like the person in the video, same medium framing. Keep {THEIR} face, {LOOK} and {THEIR} outfit from the image: {OUTFIT}. Cream studio background. 35mm film look.` |

Filled example (shot B, from the validated run):
`The young woman from the image performs exactly the head movement and expression of the person in the video, in the
same tight close-up framing. Keep her face, wispy curtain bangs, long dark-brown layered hair, rosy blush and coral lips,
and her mint-green velour track jacket from the image. Cream studio background. 35mm film look. She wears NO earrings,
NO necklace, NO choker and NO jewelry of any kind: bare ears and bare neck exactly as in the image.`

## 8. The plan and the look (what `render` builds; change it only via `plan_overrides`)

`plan_template.json` in the kit is the frame-exact plan of the reference:
- every shot uses zoom 1.0 (Genjutsu already matches the driver framing; don't add zoom)
- shots play at speed 25/24
- `tmax` is each shot's last used clip second: the first forward pass ÷ 24. A 73/24, B 12/24, C 34/24, D 27/24,
  E 30/24, F 31/24, G 30/24, H 32/24, I 26/24.
- F and I start at `tin` 1/24, which skips the driver's blank first frame

**Look layer defaults** (the user asked for these):

| Key | Default | Effect |
|---|---|---|
| `post` | `{"exp":1.10,"con":0.15}` | Exposure ×1.10 plus an S-curve contrast after the per-shot white balance. It also brightens the blank and cream-silhouette frames. |
| `grain`, `grain_fine` | `5.0`, `true` | Clean 1 px luma grain, lighter on highlights, cut to 30 % on the red text. |
| `flash` | frames `[76,93,132,164,199,234,269,306,353]`, strength 1.0, pre 1, decay 2.2, bloom 0.8, color [255,248,236] | Flash-light transition: it peaks on each swap's blank frame and the final cut, then decays over ~3–8 frames. |
| `burns` | 10 events `[start, frames, side, seed, strength]`, from `[20,14,"t",97,0.5]` to `[320,10,"l",101,0.6]` | Soft amber film burns hugging an edge or corner (`l r t b tl tr bl br`). |
| `burn_tint` | `0.6` (compose.py default; not in the template, set it via `plan_overrides`) | How strongly the burns tint cream/white frames. |

How the burns are built: three broad noise octaves (a finer octave read as fire on the night shot), screen-blended on
dark shots plus a hue tint so they show on cream. One burn leads into each transition, plus two light accents (frame 20
in A, frame 320 in I).

**Overrides:**
- Original flat look: `{"post":null,"flash":null,"burns":[],"grain_fine":false,"grain":4.0}`
- Softer: `{"post":{"exp":1.05,"con":0.08},"burn_tint":0.4}`
- No burns: `{"burns":[]}`
- Ghost fix: `{"shots":{"C":{"tmax":1.25,"bounce":true}}}`. tmax is in seconds, in multiples of 1/24; `bounce` plays
  back instead of freezing.

## 9. Reference anatomy (for answering questions and judging QA)

The reference is 1920×1080, 25 fps, 355 frames = 14.2 s, AAC stereo. The lyric is "Let me show you how to move…";
only the first line is typeset. The song has explicit lyrics later.

| Shot | Frames | Time | Picture | Driver (ref range) |
|---|---|---|---|---|
| A | 0–73 | 0.00–2.92 | full-body front on cream seamless, slow sway, hand to hair; red lyric words behind | 0–73 |
| B | 77–89 | 3.08–3.56 | tight 3/4 profile close-up, eyes to lens | 77–89, jewellery painted out |
| C | 94–128 | 3.76–5.12 | front close-up, mouthing the lyric | 94–128 |
| D | 133–160 | 5.32–6.40 | wide side-profile walk on cream, bag | 133–160 |
| E | 165–195 | 6.60–7.80 | dark loft close-up, hand behind head | 165–195 |
| F | 200–230 | 8.00–9.20 | dusk overpass, walking, glance back, blurred passers-by | 199–230 (199 blank, skipped) |
| G | 235–265 | 9.40–10.60 | medium, hands on hips, bag | 235–265, jewellery painted out |
| H | 270–302 | 10.80–12.08 | close-up head tilt + smirk, soft white halo | 270–302, jewellery painted out |
| I | 307–352 | 12.28–14.08 | medium laughing; end FX run over it from 13.04 | 306–332 (306 blank, skipped), held after 1.083 s |

**Transitions ("matte swap").** Every cut is a 2–4 frame swap built from the **incoming** shot's subject matte (MODNet,
hardened into sticker edges), then one blank cream frame (232,233,223):

| Frames | Swap |
|---|---|
| 74–76 | A + B cut-out under A's subject (B at 70 % on 74, 100 % on 75), blank 76 |
| 90–93 | B + C cream silhouette (90), C cut-out (91–92), both shifted dx −0.22; blank 93 |
| 129–132 | C + D cream silhouette, D cut-out, blank |
| 161–164 | D + E cream / dark / cut-out, all under D's walker; blank |
| 196–199, 231–234, 266–269 | cream silhouette → dark silhouette (incoming × 0.11) → cut-out → blank |
| 303–306 | H + I cream silhouette ghosting 35 % of I, dark silhouette, cut-out, blank |

**Lyric words** (shot A):
- Typeface: Archivo Black, squeezed to 0.92, colour (217,37,8), centred at y = 528 px.
- Size: rendered cap height ≈378 px. In the plan that is `text.cap` 354 plus a 12 px dilation; the ink gap is 51.
- Placement: behind the subject (occlusion matte).
- Timing: 0.40 LET · 0.60 ME · 0.80 SHOW · 1.00 YOU · 1.20 HOW · 1.44 TO · 1.72 MOVE · 1.96 LET · 2.08 ME · 2.24 SHOW ·
  2.40 YOU · 2.60 HOW · 2.84 TO. The last TO fades 2.845→2.995 and lingers behind the B cut-out.

**Grade:**
- Neutral cool cream. Each cream shot is auto white-balanced onto the backdrop target (222,222,213).
- Black point 0.06, contrast 0.12.
- E: black 0.07 / contrast 0.15. F: saturation 1.15 / exposure 1.08.

**Halo (H):** white bloom outside the subject: matte blur r = 85 px, (blur − matte)·1.5, capped at 0.42, colour
(250,249,244).

**Ending:**

| Time | What happens |
|---|---|
| 13.04–13.20 | thin light lines sweep up |
| 13.24–13.48 | the backdrop darkens into teal while the skin darkens neutrally; corner falloff from 13.44 |
| 13.44–13.60 | a cream streak band slides down |
| 13.52–14.08 | eclipse ring, radius 950 → 5 px, cream core with a teal glow, fading from 13.96 |
| 14.12–14.16 | cut back to the final laugh frame |

**Audio:** the reference's own 14.23 s AAC track, cut to 14.2 s; `apad` only guards against a shorter track. The
encoded edit's audio ends at ≈14.12 s. The beat is ≈0.52 s. The cuts sit on the editor's original frames, so nothing is
re-timed.

## 10. Failures and troubleshooting (all observed)

| Symptom | Fix |
|---|---|
| Genjutsu returns "IN THE DARK" or a preset suggestion | `declined_preset_id: 24bae836-2c4a-48e0-89b6-49fcc0b21612` on every request |
| `unlim_choice` in the response | Ask once; send `use_unlim` with the answer on every later request. |
| `429 rate_limit_reached` on submit | Two sandbox calls `sleep 30; echo ok`, then resubmit only the failed indexes. |
| Unknown or forbidden media_id for a driver | `media_import_url` the driver URL and retry. |
| Copied choker or earrings | Confirm on the detail view, paint out the driver (6.5) and retake. Prompt wording alone does not stop it. |
| Ghost or second figure late in a shot | Lower `tmax` (section 8). |
| Wrong background on E/F | Retake with the location sentence first. |
| Foreground call drops or times out | It ran > ~50 s; use background mode. |
| Files missing on the next call | The sandbox was wiped. Redo the step as one self-contained command. |
| Log missing after a background job | Read `log_path`/`status_path`. If gone too, `media_confirm` the slots (4.2). |
| `EXIT 2` with "can't open file aura_kit/aura.py" | Old command form. Use the 4.2 forms; kit download or sha errors then show in the log. |
| PUT 400/403 | Slot too old or already used. Reserve fresh slots right before use; one PUT per slot. |
| `media_upload` fails for `.onnx`/`.ttf` | Upload a `.zip`. |
| `split` says `single` on a collage | Trust the preview: rerun with `--seam <approx x>[,x2]` (or `--seam-y`). |
| `split` cut a single photo | Ignore the panels and use the original photo. |
| Imported photo has a different extension (.webp → .png) | Normal re-encode. Get the URL from `show_medias`. |
| No image returned from `image_paths` | Total > 512 KiB, a listed file was not written, or exit code ≠ 0. Pass at most 2 sheets and only files the call writes. |
| Balance dropped more than you spent | Other sessions share the account. Count your own completed jobs. |

## 11. Validated runs (2026-10-08, owner account)

**Mint-tracksuit run** (the sample to show the user):
- **Input**: the diptych `6273faad-4296-4c33-87b1-8519121741fb.webp` (CDN base). Split at 914–918 into a FULL
  (914 px) and a CLOSE (1082 px) panel.
- **Result**:
  - compare `https://d2ol7oe51mr4n9.cloudfront.net/user_3BtsEcww7blE0e9EKFuXmUaobas/c6872af0-0a1c-47f9-8cb4-17d946af0fb0.mp4`
  - edit `https://d2ol7oe51mr4n9.cloudfront.net/user_3BtsEcww7blE0e9EKFuXmUaobas/66187db0-5c38-44b3-bb27-b388ab9cc7db.mp4`
- **Genjutsu jobs**:

  | Shot | Job |
  |---|---|
  | A | 13779fc4-ed87-4daa-8873-4fed65286023 |
  | B | 7170f8b7-5959-4bf5-a308-6a7dbc68a858 (retake on the cleaned driver) |
  | C | d6271ca7-f283-48ca-b136-fdac977119c3 |
  | D | cd63f02f-b567-485c-a9ed-8b3541cf1879 |
  | E | 14891fa4-162f-4acb-92b7-38671168813a |
  | F | 17c4c260-745d-4f90-800d-73c93bd3a59c |
  | G | cb578b00-b11b-417f-959e-ff61a8bde400 |
  | H | 5b4811c7-242d-4838-8f7f-bce39c6c34e7 |
  | I | 90c97d93-32b2-45f5-92f0-6618bcb18368 |

  The submitted prompts varied slightly in wording from 7.2; section 7 is the canonical version.
- **Residuals**: small drop earrings on A, E and I; H's ear slightly waxy.

**Independent re-runs of this prompt:**
1. A fresh agent split the photo, imported a driver cross-account, generated a new G, then ran QA, render and verify.
   Everything passed. Its G came back with a copied crystal choker that only the detail view showed.
2. A second agent followed 6.5 on that G:
   - spec `clean_specs/G.json`: one choker ellipse, plus two earring tracks keyed every 3 frames
   - cleaned driver `b38d59be…`, now the registry G
   - retake job 8d287bd6-7499-41d5-9b1a-a9e195bba06a came back with a bare neck and no artifacts

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
          "character_photos"
        ],
        "properties": {
          "character_photos": {
            "type": "array",
            "items": {
              "type": "string",
              "format": "uuid",
              "x-media": "image"
            },
            "title": "Your character",
            "maxItems": 3,
            "minItems": 1,
            "description": "1–3 photos of the same person: ideally one full-body photo and one face close-up, or one collage with both. Sharp, face clearly visible, no sunglasses or group shots. Only you, someone who agreed, or a fictional/AI character."
          }
        },
        "additionalProperties": false
      },
      "slot_values": {
        "type": "object",
        "properties": {
          "look": {
            "enum": [
              "default",
              "flat",
              "soft"
            ],
            "type": "string",
            "title": "Look",
            "default": "default",
            "description": "Aura look: brighter, clean grain, flash transitions and amber film burns. Flat: the original reference grade. Soft: a gentler version of the aura look."
          },
          "prompt": {
            "type": "string",
            "title": "Notes about your character",
            "description": "Optional: pronouns, or clothes the photos don't show (trousers, shoes). Up to 500 characters."
          },
          "vertical": {
            "enum": [
              "no",
              "yes"
            ],
            "type": "string",
            "title": "Also make a 9:16 version",
            "default": "no",
            "description": "Adds a 1080×1920 vertical copy of the finished edit (the full picture on a blurred background). Free."
          }
        },
        "additionalProperties": false
      }
    },
    "additionalProperties": false
  },
  "reference_media": [
    {
      "url": "https://static-public-media.higgsfield.ai/katana-presets/published/caaec594154a1fa7a0af45c1495812c2e396e792ae2460ebada716f1166dd6e7",
      "type": "static",
      "width": 2000,
      "height": 1125,
      "mime_type": "image/webp",
      "thumbnail_url": "https://static-public-media.higgsfield.ai/katana-presets/published/c1a8989989ddcb9cd98dd80df65407595bd0123fac2f41276dfc1a2816b4814f"
    }
  ]
}
```

---
This is the last part. Follow the complete instructions from their first step.