# Katana preset: Last Katana (/katana/last-katana)

The instructions below are the selected preset's own instructions for this request. Follow them from their first step: they define the inputs, tools, workflow and deliverable. Do not substitute another preset, workflow or generation path.

- If a tool the preset requires is unavailable in this connection, stop and tell the user the preset cannot run here; do not substitute other tools.
- Inputs: the user's message may include a `MEDIA:` block of `<input>: <image|video> media_id=<uuid>` lines and an `INPUTS:` block of `<input>: <JSON value>` lines, composed by Higgsfield from the Katana form. They are values the user already supplied for those inputs: use them as these instructions describe and do not call media_upload_widget or ask for them again unless a required input is still missing. Pass a media_id directly to tools that accept one; their file URLs are listed under Supplied media when the media are passed to this tool. Older messages may list `<input>: <https URL>` lines instead; treat each URL the same way.
- Collecting inputs: the user may start the preset with the bare command and no `MEDIA:` or `INPUTS:` block; that is a normal start, not an error. Before the first step that uses an input, compare the Inputs list with what the user already supplied (MEDIA/INPUTS blocks, confirmed media_ids or files earlier in the conversation).
- Nothing supplied yet and the user asked to run the preset: open its form with get_presets {"source":"katana","preset_id":"last-katana"} as the only tool in that turn, say in one short line to fill it in below, and wait. The submitted form arrives as a /katana/last-katana message with MEDIA and INPUTS blocks. A request only to read or explain the preset does not open the form.
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
- If these instructions are no longer in your context during a long run, call get_preset_instructions with {"preset":"/katana/last-katana"} again before continuing.

## Inputs

The preset's form (field path, label, kind; required or optional):

- `media.character` ("Character", "Photo of the hero: one person, sharp face, frontal or 3/4, framed at least to the chest, no sunglasses."): image file, exactly 1; required
- `slot_values.name` ("Name", "Name line for the intro and the title, 1-2 words, upper case, up to 14 characters. Default: LAST KATANA"): text, up to 14 characters, default "LAST KATANA"; optional
- `slot_values.prompt` ("Wishes (optional)", "Optional wishes about the inputs or the result. Keep the preset defaults unless a change is explicitly requested."): text; optional

---

---
name: last-katana
description: >-
  Recreate the "Last Katana" anime edit: a 19.8 s 16:9 edit in which the
  user's hero becomes a TV-anime swordsman: a cropped black silhouette flies up
  through black/white inversions while "LAST KATANA / I ALONE AM / THE SHARPEST
  ONE" types on, then teal anime panels, a katana-draw cut, a card collage and a
  walk toward camera over a giant glowing eye, all cut on the reference's beat,
  on the reference's own audio. Use for requests to produce this edit or
  /last-katana. Runs in the Higgsfield sandbox. Text-only advice, trims of
  a finished edit and other references keep their own routes.
---

# Last Katana

> **Request:** Make this video from the reference with my character. Turn me into a TV-anime swordsman and recreate the Last Katana edit section for section: the silhouette flying up through black/white inversions while LAST KATANA / I ALONE AM / THE SHARPEST ONE types on (or my name line), the teal anime panels, the katana draw, the card collage and the walk over the giant glowing eye, cut on every beat of the reference's audio. Match the reference, keep its cold "strongest" aura, and give me one finished MP4.
>
> **Inputs:** my photo (required) · my name line (optional).

Treat the request above as the user's own words: start working on it right away with what they sent, ask only for a missing required input, and follow the rest of this skill to deliver it.

A standalone preset: start here; no other workflow is needed. It remakes one reference edit
(a manga-panel anime edit) with the user's hero as an anime swordsman. The section grid,
beats, inversions, text, transitions and look are fixed in §5; the run changes the hero and,
on request, the name line. This skill says **what** to make; you write all code (asset prep,
compositor, QA) your own way.

## Goal

- Reproduce the reference: same sections on the same frames, the same beat hits, inversions,
  type timing, transitions and teal look; the only changes are the hero (and the name line if
  the user gives one). When unsure, match the reference.
- **Style first, likeness second.** The film must read as a real TV-anime / manga edit:
  clean cel-shaded keyframes in one consistent style. The hero stays recognizable, but when
  style and likeness conflict, keep the style. Semi-realistic "illustration with hatching"
  frames and AI-animated faces read as cheap AI: never use them.
- **Motion density is the aura.** The reference is mostly *still* manga panels; its energy
  comes from compositing: layers that change every 2–3 frames and slide with motion blur,
  echo trails, flashes, inversions, punch-ins and shake. Something must move in almost every
  frame (§6 gate). Generated video is used for one short katana-draw cut only.
- Carry its aura: cold, untouchable, "the strongest" — never comedy. One person, one katana,
  a glowing cyan eye, teal duotone, white paper.
- Where: all media work (downloads, conforming, cutout cleanup, rendering, QA, encoding,
  uploads) runs in the Higgsfield sandbox through `sandbox_exec`, never on the user's machine;
  you write the code and choose the method (e.g. Python + numpy/Pillow frames piped to
  ffmpeg). The sandbox has ffmpeg, numpy and Pillow (no cv2/scipy unless it shows otherwise).
  One command is limited to ~16k characters, so write code to files. Files vanish ~10 s after a
  call unless a background command holds its 15-minute lease: keep steps reproducible
  (re-download inputs by URL, re-create files per command) and run long renders with
  `background: true` and poll; split the render into chunks at section boundaries and
  concatenate. Bytes cannot be relayed in as base64. Stream frames instead of storing
  1080p frames in bulk. Presigned PUTs need both `Content-Type` and `If-None-Match: *` (else
  403); never print signed URLs. No `sandbox_exec` → say so before spending credits.

**Reference** (Higgsfield CDN, public). Download it into the sandbox at the start of every run
and study it (contact sheets per section): the text describes it, the video shows it. Its
audio is the film's audio.

- 19.8 s, 594 frames, 1920×1080, 30 fps, AAC audio:
  `https://d30d7anzgyxsrg.cloudfront.net/user_3ByefnwR6sEVy13pzdD2kizfNIn/ddb5b889-322e-499e-a707-1086fcd721ff.mp4`
  (media_id `ddb5b889-322e-499e-a707-1086fcd721ff`)

**Fonts** (render all text yourself): **Didot Bold** (intro lines), **Inter SemiBold Italic**
(name title), **Songti** (kanji 刀), **Hiragino Sans** (kana かたな). If one is missing in the
sandbox, bring that exact font file in through a Higgsfield file upload (`media_upload` as a
file; zip it if `.ttf/.ttc` is refused) and fetch it inside. Do not substitute.

The trick in one line: the hero's black silhouette flies up from below the frame through
black/white inversions while the lines type on, the screen bursts into teal anime panels of the
hero with the katana, cut on every beat, and the hero walks toward camera while a giant cyan eye
flickers behind.

## 0. What is fixed and what can change

| Parameter | Default | Can change |
| --- | --- | --- |
| Hero | from the user's photo, as an anime character | any consenting real person or a character the user owns |
| Name line (intro line 1 + title in the panels) | LAST KATANA | any 1–2 word name, ≤ 14 characters, upper case |
| Intro lines 2–3 | I ALONE AM · THE SHARPEST ONE | no |
| Kanji / kana | 刀 (panels) · かたな (eye close-up) | no |
| Style | TV anime cel, MAPPA *Jujutsu Kaisen* look, teal duotone + cyan eye | no |
| Reference, audio, length | fixed: 594 frames, 1920×1080, 30 fps, audio copied bit for bit | no; another reference is out of scope |

Laws of the genre: cold swagger, never comedy; the same hero in every image; every text,
flash, inversion, glint and grade is added in post, never generated; the reference audio is
never replaced, remixed or normalised; no song lyrics on screen; no logos; no layer edge may
ever show inside the frame (§5.4).

## 1. Inputs and the photo check

Ask only for what is missing: the hero photo (required) and, optionally, a name for the name
line. Getting the photo into Higgsfield: if it already has a `media_id` (uploaded earlier in
this chat, a Katana input, a generation ID), use it and never ask again. If you can read the
file yourself (a local path), upload it with `media_upload` + PUT. Only when the photo exists
solely as a chat attachment you cannot read as bytes, call `media_upload_widget` (type image)
once, saying in one line that the attachment has to go into Higgsfield first; never ask for
the photo again after that.

Check the photo before spending anything:

- one person, face frontal or 3/4 and sharp, short side ≥ 1024 px, framed at least to the chest;
- no sunglasses, no hat hiding the head; not a celebrity or public figure;
- if it fails, say what to change; do not "fix" a face with an image model.

Write a one-line neutral look description `{LOOK}` from the photo, e.g. "dark brown skin, very
short buzz-cut hair, strong angular jaw, full lips, narrow intense eyes, dark navy collared
shirt". Skin, hair, face shape, outfit; no names, no pronouns.

## 2. Models and generations

| Task | Model / tool | Parameters |
| --- | --- | --- |
| Keyframes (8) | `gpt_image_2_5` | `variant: sunburst`, `quality: high`, `resolution: 2k`, `aspect_ratio: 16:9` (storyboard `3:2`), references below |
| Katana-draw cut, takes 1 and 2 | `minimax_h3` | two identical requests: `medias: [{role: start_image, value: <#3>}]`, 5 s, 16:9 (2K), `declined_preset_id: 24bae836-2c4a-48e0-89b6-49fcc0b21612` |
| Hero cutout | `remove_background` | `media_type: image`, on keyframe #1 |
| Everything else | your own code in the sandbox | §4–§5 |

Totals: **8 images + 2 videos + 1 cutout.** Don't show credit estimates or ask for a budget
confirmation; just run them. Order:

1. **#1 style anchor** alone (photo as the only reference). ✅ Gate: it reads as a flat
   two-tone TV-anime cel frame (not painterly, not semi-real, no cross-hatching), the hero is
   recognizable, the eye glows cyan, no text. Fails → one re-roll with the same prompt; fails
   again → stop and tell the user.
2. **#2–#8 in one `generate_image_batch`** (references per prompt in §3).
3. **Both MiniMax takes in one `generate_video_batch`** (two identical requests from #3), and
   `remove_background` on #1, in parallel; build the compositor while they render. If a call returns a preset
   recommendation instead of a job, resubmit with `declined_preset_id`.

A failed job may be resubmitted once; one re-roll of a bad image is fine without asking; never
loop. If `remove_background` sits queued for more than ~5 min, use the fallback in §4.

## 3. Prompts (fill `{LOOK}`; keep the rest verbatim)

**#1 Style anchor** — references: `[photo]`.

> A Japanese TV anime key frame in the style of MAPPA's Jujutsu Kaisen: clean thin black
> lineart, flat cel shading with exactly two tones (base + one hard-edged shadow), sharp anime
> face design, no gradients except a soft glow on the eye. The character is an anime version
> of the person in the reference photo: {LOOK}. Pose: upper body in 3/4 rear profile, head
> turned back over the shoulder toward the viewer with a cold confident smirk; one hand grips
> the hilt of a katana resting on the shoulder. The near eye glows electric cyan with a light
> streak. Palette: monochrome teal — deep petrol-teal shadows, pale cyan-white highlights, the
> cyan eye is the only saturated accent. Composition 16:9: character on the right third, left
> side light pale background with faint manga sketch lines and speed lines. Pure 2D anime cel
> art — not photorealistic, not semi-realistic, no painterly brush texture, no 3D rendering.
> No text.

`STYLE` (opening of #3–#6): *Japanese TV anime key frame in the style of MAPPA's Jujutsu
Kaisen, matching the second reference image exactly: clean thin black lineart, flat two-tone
cel shading with hard-edged shadows, sharp anime face design, monochrome teal palette (deep
petrol-teal shadows, pale cyan-white highlights); glowing electric cyan eyes are the only
saturated accent. The same character as in the second reference image (anime version of the
person in the first photo): {LOOK}.* `END` (closing of #3–#6): *Pure 2D anime cel art — not
photorealistic, not semi-realistic, no painterly texture, no 3D rendering. No text.*

| # | References | Prompt |
| --- | --- | --- |
| 2 Silhouette | `[photo]` | A single flat solid pure black silhouette on a pure white background, nothing else. The silhouette is the upper body of the person from the reference photo ({LOOK}) seen in 3/4 rear profile, head turned to the right showing the profile of the face (nose, lips, chin readable in the outline). A katana hilt with a round tsuba guard and the end of the sheath stick up diagonally above the right shoulder, also part of the silhouette. Placed slightly right of center, top of the head at about 20% from the top edge, cropped at mid-chest by the bottom edge. Crisp razor-sharp edges, 100% black fill, no interior detail, no gradient, no shading, no shadow, no texture, no text. |
| 3 Katana draw | `[photo, #1]` | STYLE Close-up action frame, 16:9: the character holds the katana horizontally right in front of the lower half of the face, the blade half drawn from the black sheath with a sharp white glint on the steel; eyes narrowed, staring straight at the viewer, both glowing cyan. Pale background with dynamic diagonal speed lines. END |
| 4 Eyes close-up | `[photo, #1]` | STYLE Extreme close-up of the character's eyes and brow filling the whole 16:9 frame: both irises glow electric cyan with thin horizontal light streaks, a cold intense stare, sharp anime eyelid and brow lines, a few speed lines at the edges. END |
| 5 Storyboard | `[photo, #1]` | An anime storyboard sheet: exactly 6 equal rectangular frames in a strict 3-column by 2-row grid, separated by thick pure white gutters, with a pure white margin around the grid. Every frame is a TV anime key frame in the style of MAPPA's Jujutsu Kaisen matching the second reference image: clean thin lineart, flat two-tone cel shading, monochrome teal palette, glowing cyan as the only saturated accent. Same character as the second reference ({LOOK}). Frames: 1) extreme close-up of one glowing cyan eye; 2) a hand gripping the wrapped katana handle at the guard; 3) side profile with a cold smirk; 4) a few centimeters of blade sliding out of the sheath with a glint; 5) the character looking down, eyes shadowed with a faint cyan glow; 6) seen from behind, walking away with the sheathed katana over the shoulder. Each frame a clean rectangle with a thin black border. No text, no speech bubbles, no numbers. *(aspect 3:2)* |
| 6 Walk | `[photo, #1]` | STYLE The character walks straight toward the camera, centered, framed from the knees up, slightly low angle, head slightly lowered, eyes in shadow glowing cyan, menacing calm. A long dark open coat over the outfit, dark trousers, the sheathed katana held low in the right hand pointing down, left hand relaxed. IMPORTANT: completely plain flat pure white background, nothing else — no ground, no shadow, no lines — so the figure can be cut out cleanly. END |
| 7 Giant eye | `[#1]` | Background plate only, no character: one gigantic anime eye filling the entire 16:9 frame, drawn as a TV anime key frame in the style of MAPPA's Jujutsu Kaisen matching the reference image's style: clean thin lineart, flat cel shading, sharp stylized eyelashes; the iris glows saturated electric cyan with a bright pupil highlight and radial light rays. Around the eye: sharp radiating speed lines and broken angular frame lines like shattered glass. Palette monochrome teal (deep petrol-teal and pale cyan-white), only the iris saturated. Pure 2D anime art, no painterly texture, no 3D. No text. |
| 8 Sketch plate | `[#1]` | Background layer only for an anime composite, no main character in the foreground: pale cyan-white paper background in the style of the reference anime frame. On the left half, a large faded anime sketch of a hand gripping a katana hilt drawn in thin light-teal lines; on the right half, a faded giant close-up of the same character's face from the reference drawn in very light thin lines at low contrast. Diagonal speed lines and a few ink splatters. Overall light, airy and low contrast so a foreground character will stand out. Pure 2D anime art. No text. |

✅ Check every image: same face and outfit as #1, cel style (no hatching, no realism), no text,
no extra people, hands intact; #5 has six clean frames; #6 background is flat white. Re-roll a
failing image once.

**Videos** — MiniMax H3 only, two takes of the same prompt from #3 as start image (take 1 →
the first katana cut, take 2 → the second, so the repeat is not the same footage). The face must
stay one held drawing: only blade, glint, eye glow and speed lines move.

> For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is
> fully referenced.
>
> integrated_multimodal_description: [Shot 1] 2D-animated Japanese TV anime cut in the exact
> cel-shaded style of Picture 1 (MAPPA Jujutsu Kaisen look: clean thin lineart, flat two-tone
> cel shading, hard shadows, teal palette); it stays flat 2D anime for the whole clip and never
> becomes realistic or 3D. Limited animation on twos: the character's face and head remain the
> same held drawing, the features never morph. The character slides the katana blade out of
> its sheath to the right in one smooth motion; a sharp white glint races along the steel edge
> from the guard to the tip. The cyan eyes flare brighter, leaving thin cyan light streaks.
> Background speed lines streak diagonally. The camera holds a static shot, with one slight
> shake when the glint reaches the tip. End with the blade fully revealed and the glint at the
> tip. No text, no subtitles, no extra people.
>
> overall_soundscape: A crisp metallic shing of steel sliding from the sheath.
>
> non_diegetic_music: N/A

✅ Per take: still the same anime drawing as #3 (no morphing, no realism), blade moves, glint
visible, no text. MiniMax returns 2560×1440, 24 fps, with audio (drop it). Conform both takes to
1920×1080, 30 fps. Re-roll a failing take once; if only one take is usable, use it in both
slots from different in-points (slot 2 starts ≥ 1 s later in the take).

## 4. Asset prep

- **Hero cutout (#1):** `remove_background` returns an RGBA PNG. Check it over a loud colour:
  no halo, the katana handle kept. Queued > 5 min or broken: one `gpt_image_2_5` call with
  `background: transparent`, reference `[#1]`, prompt "Reproduce the reference anime frame
  exactly — same character, pose, framing, lineart, cel shading, colours, glowing eye and
  katana — but remove the entire background: only the character on a fully transparent
  background. No text."
- **Walk cutout (#6):** cut it yourself: flood-fill the near-white background (luma > ~0.91)
  from the borders, then also clear enclosed near-white gaps (between coat and sword) except
  cyan pixels; erode 1 px, feather ~1 px.
- **Silhouette (#2):** mask = luma < 0.5. Scale it to 0.7 of the frame, place its top-left at
  (0.20·W, 0.12·H), then **extend the body downward** by repeating its last full row for
  another frame height, so the figure is cut by the frame edge and never by its own bottom.
- **Storyboard (#5):** find the white gutters (rows/columns with mean luma > ~0.94) and cut
  the six frames (inset 4 px). Panels 1–6 = eye, hand on hilt, profile smirk, blade, looking
  down, from behind.
- **Eye point:** measure the glowing eye of #1 in normalized image coordinates (the run that
  built this preset: (0.554, 0.243)); glints are placed there through the same transform as
  the hero layer.
- **Conformed clips:** 30 fps frame sequences or streams, 1920×1080.

## 5. Build the film

Project: 1920×1080, 30 fps, **594 frames (19.8 s)**; output frame `n` is time `t = n/30`; a
section `t0–t1` covers `t0 ≤ t < t1`. Beat: ~129 BPM (eighth-note step ≈ 0.232 s); the drop
lands at **4.97 s**. Strong hits used below: 4.97, 5.41, 6.11, 6.80, 7.24, 8.17–9.12 (cards),
9.54, 9.78, 10.45, 12.28, 12.75, 12.98, 14.12, 14.35, 15.02–16.18 (cards), 17.09, 17.79.

### 5.1 Timeline

| t0–t1 (s) | frames | section | content |
| --- | --- | --- | --- |
| 0.00–4.20 | 0–125 | intro | silhouette fly-in, inversions, typed lines, bloom-out, cyan burst |
| 4.20–6.00 | 126–179 | layered 1 | hero cutout over cycling panel layers, name title + 刀 |
| 6.00–6.40 | 180–191 | eyes | #4 close-up, かたな glowing across the eyes |
| 6.40–7.45 | 192–223 | clip A | MiniMax take 1, katana draw + overlays |
| 7.45–8.05 | 224–241 | slide-out | clip A keeps playing, slides left, burns to white |
| 8.05–9.31 | 242–279 | collage 1 | six cards pop in on beats |
| 9.31–11.15 | 280–334 | walk 1 | walk cutout, background flips every 3 frames |
| 11.15–11.60 | 335–347 | whip | grey flash + whip into layered 2 |
| 11.60–13.20 | 348–395 | layered 2 | tighter hero, other layer order, title + 刀 |
| 13.20–13.40 | 396–401 | whip | whip into clip B |
| 13.40–14.75 | 402–442 | clip B | MiniMax take 2, katana draw + overlays |
| 14.75–15.00 | 443–449 | slide-out | as above |
| 15.00–16.42 | 450–492 | collage 2 | six cards again |
| 16.42–18.69 | 493–560 | walk 2 | walk cutout, background flips every 2 frames |
| 18.69–19.30 | 561–578 | outro | warm red smear, fade to black |
| 19.30–19.80 | 579–593 | black | music tail |

**Impact frames** (2 frames each) at **6.80, 9.54, 14.12, 17.79**: dark areas and edges turn
white, everything else black, cyan kept.

### 5.2 Sections

**Intro (0–4.2).**
- Background white, silhouette black; they swap at every inversion: **0.2, 0.4, 0.9, 1.1, 1.8,
  2.1, 2.5, 3.2, 3.6 s** (black bg from 0.2, white from 0.4, black from 0.9, …).
- Fly-in: vertical offset `(1 − easeOut(t/0.5))·0.88·H − 22·t` px (positive = lower): at
  t = 0 only the top of the head shows at the bottom edge. Motion blur while flying (t < 0.5):
  average 12 sub-frame positions within the frame. easeOut(x) = 1 − (1 − x)³.
- Framing jumps on each inversion: scale per inversion index `i` = [1.0, 1.07, 1.0, 1.05, 0.97,
  1.06, 1.0, 1.08, 1.02, 1.1][i] × (1 + 0.035·t/4); x drift `26·sin(1.4t) + (i odd ? 22 : 0)` px;
  rotation `2.4°·sin(1.6t) + 6°·(1 − rise)` around (0.6·W, 0.9·H). The silhouette never stops
  moving.
- Text: Didot Bold 84 px, tracking 34 px, the **full line laid out centred at (0.42·W, 0.52·H)**,
  words revealed in place: 0.4 "LAST", 0.9 "LAST KATANA", 1.1 "I", 1.5 "I ALONE", 2.1 "I ALONE
  AM", 2.6 "THE", 2.8 "THE SHARPEST", 3.2 "THE SHARPEST ONE", gone at 3.6. Colour = the
  opposite of what is under each pixel (over the silhouette it flips, so it stays readable),
  with a soft shadow (blur 10 px, 50 %). A custom name replaces "LAST KATANA" (two steps: first
  word, then both).
- 3.85–4.15: the silhouette blurs out (to ~32 px) and blooms (add blur-40 copy × 1.2·k);
  4.08–4.2: cyan burst wipes in (pale cyan (0.85, 0.97, 1.0) with a deeper cyan (0.1, 0.7, 0.95)
  band rising from the bottom third).

**Layered panels (4.2–6.0 and 11.6–13.2).** Back to front: cycling layers → title → hero cutout
→ glints, beams, flares, flashes.
- **Cycling layers:** a new layer every **3 frames**, cycling through: pass 1 = #8, #3, panel 2,
  #4, panel 4, #6, panel 3, panel 6; pass 2 = #4, panel 4, #8, panel 1, #3, panel 5, panel 2,
  #6. Each layer is a **dense toned crop**, not thin lineart: `tone = grade(img, mix 0.85)·0.72 +
  0.28`; ink = max(line pass `clip(−(blur1.2(L) − blur4.5(L))·7)`, dark fill `clip((0.3 − L)·2.5)·0.35`);
  layer = `tone·(1 − 0.6·ink) + (0.08, 0.30, 0.36)·0.6·ink`, cyan pixels kept cyan. Scale cycles
  1.5, 1.9, 1.3, 2.2 (big crops: a giant hand, a giant face), vertical offset ±90–180 px per
  layer, slides 320 → −320 px across its 3 frames with alternating direction, horizontal motion
  blur ~50 px. The previous layer stays as a ghost: `min(current, previous·0.45 + 0.55)`.
- **Hero:** #1 cutout centred; scale 0.98 → 1.08 (pass 2: 1.08 → 1.2); x drift −70 → +60 px
  (pass 2: +80 → −60); rotation 0.8°·sin(2.1·u).
- **Title** between layers and hero: name line in Inter SemiBold Italic 88 px, tracking 26 px,
  colour (13, 51, 64), centred at (0.28·W, 0.50·H), drifting −40 px/s, fades in over 0.15 s,
  white glow (blur 6, 50 %), two ghost copies (+14 px x at 35 %, −10 px y at 20 %). Kanji 刀 in
  Songti 520 px at (0.43·W, 0.52·H), same colour at 60 %, in at +0.4 s (pass 2: +0.2 s).
- **Punches** 4.97, 5.41 | 12.28, 12.75, 12.98: zoom +6 % decaying over 0.25 s + shake 18 px over
  0.18 s. **Eye glints** 4.97, 5.64 | 12.28, 12.98: horizontal light streak at the eye point
  (vertical σ 6 px, horizontal σ 380·g + 40 px, core σ 22 px, colour (0.5, 0.95, 1.0)·1.4·g,
  g = (1 − u/0.35)²). **White flash** 5.47 (3 frames, `a·0.3 + 0.75`). **Light beams** 5.52 | 12.5:
  two soft gaussian columns (σ 90 and 160 px) sweeping left → right over 0.4 s, ≤ 55 % — never
  hard-edged bars. **Flares** 5.86 at (0.47, 0.70) | 13.0 at (0.50, 0.68): core σ 45 px, streak
  σ 9 × 320 px, halo σ 220 px, 0.3 s. Whoosh-in: horizontal blur 120 → 0 px over the first 0.1 s.

**Eyes close-up (6.0–6.4).** #4, zoom 1.0 → 1.15 (easeOut), shake on 6.11. かたな in Hiragino
Sans 96 px, tracking 60 px, centred at (0.50·W, 0.53·H) across the eyes, in at +0.11 s: cyan
glow (blur 14, colour (0.2, 0.8, 1.0)) + fill (0.75, 1.0, 1.0). Overlay panel 3 (6.15–6.4,
slides +600 → +250 px, 45 %).

**Katana clips (6.4–7.45 take 1, 13.4–14.75 take 2).** Play at **1.4×**; choose the in-point
so the glint peak lands on **6.80** (take 1) and **14.12** (take 2). Zoom 1.0 → 1.14 (B: 1.05 →
1.2), punches A 6.80, 7.24 · B 14.12, 14.35. **Double-exposure overlays** in darken blend
(`a·(1 − o) + min(a, layer)·o`), each sliding in with horizontal blur 40·(1 − k), opacity rising
and falling: A — #4 6.45–6.95 (+700 → +300 px, scale 1.2, 50 %), panel 3 as a toned layer
6.95–7.45 (+650 → +200 px, 50 %); B — #4 13.5–14.05 (+700 → +250 px, 50 %), panel 1 toned
14.2–14.75 (−600 → −150 px, 45 %). Before blending, push the overlay's paper to pure white
(levels `(x − 0.12)/0.7`) and feather its edges (smoothstep over 18 % of each side), so only
ink and shadows show — never a rectangle. Flares A 7.24 at (0.55, 0.42) · B 14.12 at
(0.52, 0.45).

**Slide-out (7.45–8.05, 14.75–15.0).** The previous clip keeps playing; push 1 → 1.08, slide
−700 px, horizontal blur 30 → 170 px, mix to white 0.97.

**Collage (8.05–9.31, 15.0–16.42).** Background (247, 251, 251). Panels 1–6 pop in at **8.17,
8.41, 8.64, 8.85, 9.00, 9.12** (collage 2: **15.02, 15.26, 15.49, 15.72, 15.95, 16.18**): width
400 px × cluster scale × (0.6 + 0.4·k), k = easeOut over 0.16 s, rising from +60 px; 6 px pale
border, soft shadow (blur 10, 35 %, offset 10/14 px). Offsets from centre (x·W, y·1.6·H) and
rotations: (−0.13, −0.06, −5°), (0, −0.11, 3°), (0.13, −0.05, 6°), (−0.12, 0.10, 4°),
(0.02, 0.08, −3°), (0.14, 0.11, −6°). Cluster scale 0.95 → 1.12; the whole frame drifts
(±30 px x, ±12 px y, ±1.5°). Last 0.15 s: zoom × 1.8 with blur into the walk.

**Walk (9.31–11.15, 16.42–18.69).** #6 cutout centred (vertical centre 0.42; walk 2: 0.40,
scale × 1.04), push 1 → 1.1, +1.2 % pulse on every background flip, 3 px bob. Background flips
every **3 frames** (walk 2: every **2**) through:
walk 1 `white, eye, eyelines, eye, eyecyan, eyelight, eyeinv, eye, eyelines, dark, eyecyan, eyelight`;
walk 2 `white, eye, eyelight, eyelines, eye, eyeinv, eyecyan, eye, eyelines, eyelight, dark, eye`.
Forced on hits: 9.54 eye, 10.45 eyecyan, 10.91 dark | 17.09 eye, 17.79 eyecyan, 18.46 dark.
Variants of #7 (zoom 1.05 → 1.35 over the section, ×1/1.04/1.08 and ±120 px offset per flip):
`eye` graded plate · `eyecyan` ×(0.35, 1.05, 1.35) + (0.15, 0.25, 0.3) · `eyelight` ×0.45 + 0.58 ·
`eyelines` line pass of the plate on white · `eyeinv` inverted, cooled · `dark` ×0.3 · `white`
0.96. Cyan rim light around the figure on eye / eyecyan / eyeinv / dark. Entry: white flash
over 0.12 s and a punch-in from 1.25 with blur 10 over 0.1 s. Punches 9.54, 9.78, 10.45 |
17.09, 17.79.

**Whips (11.15–11.6, 13.2–13.4).** Live, never frozen: the outgoing section keeps playing until
the midpoint, then the incoming one; first 35 % greyed (`a·0.4 + 0.33`); zoom 1 + 0.1·sin(πk),
slide (k − 0.5)·−500 px, horizontal blur 120·sin(πk) + 10 px.

**Outro (18.69–19.3), black (19.3–19.8).** Last walk frame smeared horizontally (80 → 200 px),
warm glow (0.95, 0.42, 0.25)·0.6·e^(−3u), fading to black by 19.3; black to the end.

### 5.3 Global look

- **Grade** on every generated image/clip: luma `L' = clip(1.04·L)^0.85` mapped through the
  teal duotone stops 0 → (0.05, 0.15, 0.19), 0.45 → (0.30, 0.52, 0.58), 0.78 → (0.68, 0.86, 0.89),
  1 → (0.96, 0.995, 1.0); mix **55 % duotone + 45 % original** (the cel colours survive). Cyan
  mask `clip((B − R − 0.22)·4)` keeps the eyes/glints cyan (×(0.7, 1.12, 1.3)) plus a glow (blur
  16, ×1.2). Eye plate #7: mix 0.4.
- **Bloom:** highlights above 0.62 blurred (r 22) and added at 35 %.
- **Echo trails:** blend each output frame with `max(current, previous output)` at 35 % in
  layered sections, 25 % eyes/clips, 30 % slide-outs, 15 % walks. None in the intro and collage.
- **Grain:** σ 0.018 at half resolution, 6 cycling patterns, off from 18.7 s.

### 5.4 No layer edge in frame (hard rule)

Every shifted, scaled or rotated layer (plates, clips, cutouts, overlays, the collage frame)
is scaled up just enough that its edge never enters the frame: scale ≥ 1 + 2·|dx|/W + 2·|dy|/H
(+ 0.04 per degree of rotation). Rotate on an oversized canvas (+12 % each side) and crop the
centre; never rotate an already frame-sized image (black corners). Cutouts whose body touches
the source edge (#1 bottom/right, #6 bottom) must keep that edge outside the frame. Overlays:
paper → white and feathered (above). Light effects are soft gaussians, never hard bars.

## 6. QA and gate (all must hold before delivery)

- 1920×1080, 30 fps, exactly 594 frames; the audio stream is the reference's, copied bit for
  bit (`-c:a copy`), never re-encoded.
- Sections, inversions, word timings, impacts and hits on the frames above; the name line is
  the user's (or LAST KATANA).
- **Style:** every image reads as the same TV-anime cel drawing; no semi-real faces, no
  hatching, no morphing in the clips; the hero recognizable in #1, #3, #4, #6.
- **Motion density:** count frame pairs whose mean absolute difference (grey, 160×90, 0–255)
  exceeds 3 — the reference has 429 of 593; the film must reach **≥ 380**. Below that: more
  layer cycling (2 frames), longer echo, more overlays, stronger drift — not more generations.
- **Edges:** scan every frame (grey, 480×270) for a straight vertical or horizontal step
  (> 0.12) running through > 55 % of the frame, or a 3 px border stripe differing by > 0.12 from
  the band next to it; look at every flagged frame; only content drawn inside a source image
  may remain (speed lines at an image edge, the collage zoom-blur).
- Side-by-side contact sheets (10 fps) of reference and film per section: same rhythm, same
  amount of movement, white paper and teal look; the silhouette is cut by the frame, never by
  itself.

Fix every failure before showing anything; do not list a fixable defect as a limitation.

## 7. Delivery

Deliver only one final MP4 video. Upload it with `media_upload` (`Last Katana v1.mp4`,
video/mp4) and a PUT; after HTTP 200 call `media_confirm` and show its confirmed URL or inline
player once. Keep QA sheets, comparisons, intermediate renders, generation IDs and project
files internal. Save versions as v1, v2…; never overwrite.

| Feedback | Fix |
| --- | --- |
| looks cheap / AI | re-roll the offending keyframe with the §3 prompt; never animate faces |
| face differs between shots | re-roll that keyframe with `[photo, #1]`; keep #1 as the anchor |
| not enough movement | layers every 2 frames, echo +0.1, extra overlays on the clips |
| layer edges / bands visible | §5.4 cover rule, rotation canvas, overlay levels + feather |
| faces too dark | lift the duotone mids (0.45 stop) or lower the mix to 0.45 |
| silhouette looks cut out | extend the body further down; it must leave through the bottom edge |
| other name | name line in the intro and the title |
| clip glint off the beat | move the clip's in-point |

## Out of scope (say so before generating)

- Another reference, length or aspect ratio; replacing or remixing the music.
- Animating the hero's face with video models, lip sync, dialogue.
- Song lyrics on screen, comedy, logos, end cards.
- Celebrities or people the user has no right to depict; more than one hero.

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
          "character"
        ],
        "properties": {
          "character": {
            "type": "array",
            "items": {
              "type": "string",
              "format": "uuid",
              "x-media": "image"
            },
            "title": "Character",
            "maxItems": 1,
            "minItems": 1,
            "description": "Photo of the hero: one person, sharp face, frontal or 3/4, framed at least to the chest, no sunglasses."
          }
        },
        "additionalProperties": false
      },
      "slot_values": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "title": "Name",
            "default": "LAST KATANA",
            "maxLength": 14,
            "description": "Name line for the intro and the title, 1-2 words, upper case, up to 14 characters. Default: LAST KATANA"
          },
          "prompt": {
            "type": "string",
            "title": "Wishes (optional)",
            "description": "Optional wishes about the inputs or the result. Keep the preset defaults unless a change is explicitly requested."
          }
        },
        "additionalProperties": false
      }
    },
    "additionalProperties": false
  },
  "reference_media": [
    {
      "url": "https://static-public-media.higgsfield.ai/katana-presets/published/6b020a6cd3ce94d3bae168f71ce5b2f98c641d714104957a60991889b3a0d659",
      "type": "video",
      "width": 1920,
      "height": 1080,
      "mime_type": "video/mp4",
      "placeholder": "data:image/webp;base64,UklGRnYAAABXRUJQVlA4IGoAAABQBACdASogABIAPk0gjEQioiEYBgAoBMS0gAHxdqt/AhIT05EE/clqrwQgAP7/tQJqHH2X3qFLtrzHYG6vofXm3V3mmQ9OBPjeWEP/5IADrZZuyI9JaddovVgSW2z6jN9s0eB9KrYUAAAA",
      "thumbnail_url": "https://static-public-media.higgsfield.ai/katana-presets/published/80d07cb123ff39148b762cea613037cd3c2200300671450c87b8c47370877a84"
    }
  ]
}
```