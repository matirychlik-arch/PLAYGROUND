# prompts.md — faceless-video prompt templates

All image/video prompts in **English**. Only narration switches to the user's
language. `{STYLE}` = the ONE style formula, pasted byte-identical everywhere.

## 0. STYLE FORMULA (write once, reuse verbatim)
80–100 words, ≤2 sentences: line/surface work · shading · palette · one signature
accent · background treatment · motion timing · render discipline (positive form).
Always non-photorealistic. **House styles ship pinned formulas — take them verbatim
from `style-editorial-collage.md` (Editorial Motion Graphics — default for History AND
Explainer) / `style-paper-diorama.md` (History's named alternate), including their
PALETTE LOCK lines and {MOTION} mappings; do not re-derive.** Stickman Cartoon
(Explainer's second main direction) uses this generic formula (never name a real
comic/brand/IP):
> flat 2D webcomic cartoon, extremely minimal — uniform thin even-weight black
> outlines, egg-shaped heads with tiny dot eyes and a single line mouth, plain
> noodle limbs, solid flat color fills with NO shading, NO gradients, NO texture,
> deadpan minimalist design, plain flat solid-color backgrounds.

Stickman has no style file and no pinned image URLs, so its **catalog card
"Stickman Cartoon"** (`237dd06c-3729-4895-9672-1c623c4266e0`) IS its reference: Phase 1
RULE 0 resolves it and attaches the returned `media_id` to the style-key call.

## 1. Style key (seedream_v5_pro, 1k, chosen aspect — default 16:9)
Make it **pretty & legible**, not formless blobs — a small representative vignette so
the look reads clearly: "A clean {STYLE} STYLE SAMPLE: one simple recognizable subject
(a small friendly object or mini-scene) rendered in the style so its line weight,
shading and colours read at a glance. Balanced, attractive, easy to read. No palette
strip, no colour chips, no swatch bar, no colour squares, no labels, no text, no
watermark, no reference-sheet layout." (It's still a look anchor, not a final frame.)
**Tell the user** when showing it: a style key can look a little odd/abstract — that's
normal, it's only a reference for the look.
From uploads (style only), verbatim prefix: "Take only the visual render style and
color grading of the input image(s)… never use the characters, inscriptions, etc."

## 2. Assets (seedream_v5_pro, always 1k; pass style key as `image_references`; {STYLE} verbatim)
- **Character (2:3, 1k):** "Full-body character centered on a plain flat solid-color
  background, in THIS EXACT style: {STYLE}. Character: {desc — distinctive, readable
  silhouette}. No text, no watermark."
- **Location (CHOSEN aspect, 1k):** "{interior/exterior} … in THIS EXACT style: {STYLE}.
  {key furnishings + ONE named anchor object with a position}. Empty room — no people, no
  characters, no figures. Wide establishing. No text, no watermark."
- **Prop (1:1, 1k):** "A single isolated prop centered on a plain flat solid-color
  background, in THIS EXACT style: {STYLE}. Object: {desc}. No hands, no scene, no
  other objects. No watermark."

## 3. Block = one 10s H3 clip with FIVE hard-cut shots (the core template)
One `generate_video_batch.requests[]` item with model `minimax_h3`, `duration:10`,
`aspect_ratio` = the CHOSEN aspect
(default `"16:9"`; this workflow uses ONLY 16:9 / 9:16), `resolution:"2K"`, `medias` =
location → characters → props (role `image_references`), **max 7 refs per call** (keep the production packing even though H3 supports more) — only this block's assets; trim extra props/coverage first, never the
location or an on-screen character. If the response is a preset
recommendation instead of a job → resubmit the same call with `declined_preset_id` = the
recommended preset's id. Follow the Phase-4 live-schema/native-audio preflight;
only send `generate_audio:true` when that field is declared.

```
Style: {STYLE}; {MOTION} — the visual style is EXACTLY as in the reference images, same rendering, same surface treatment.
PALETTE LOCK: use ONLY the colors and the background treatment of the reference images ({e.g. flat off-white/clean webcomic background}). Do NOT introduce any new or foreign colors, no colored/gradient/painted backgrounds that aren't in the references, no recoloring of characters or objects.
A single 10-second scene of FIVE hard-cut shots. Do NOT open the video on any reference image or show a sheet/swatch — stage everything fresh, matching characters, room, colors and background to their references. Characters only emote and gesture, they do NOT talk. Motion starts on frame 1 (no opening freeze).
REFERENCES (look, identity, palette): @Image1 = LOCATION ({desc}). @Image2 = {CHARACTER A} ({desc}). @Image3 = {CHARACTER B}. @Image4 = {PROP}.
SHOT 1 — 0.0s to 2.0s — {SIZE+ANGLE}: {beat}.
HARD CUT.
SHOT 2 — 2.0s to 4.0s — {DIFFERENT SIZE+ANGLE}: {beat}.
HARD CUT.
SHOT 3 — 4.0s to 6.0s — {DIFFERENT SIZE+ANGLE}: {beat}.
HARD CUT.
SHOT 4 — 6.0s to 8.0s — {DIFFERENT SIZE+ANGLE}: {beat}.
HARD CUT.
SHOT 5 — 8.0s to 10.0s — {DIFFERENT SIZE+ANGLE}: {payoff}.
Five hard-cut shots at 2.0s, 4.0s, 6.0s and 8.0s, no dissolves, no fades. {MOTION}, continuous motion within each shot, never freezes.
```
**~2s per shot is the LAW: no shot longer than 2.5s** — a frame hanging 3–5s reads
as a slideshow, and every shot needs visible ACTION, not a held pose. Degradation:
a block failing generation twice at 5 cuts drops to 4 (2.5s grid) — that block only.
**Kids blocks use FOUR cuts** (2.5s each: `SHOT 1 0.0–2.5 … SHOT 2 2.5–5.0 … SHOT 3
5.0–7.5 … SHOT 4 7.5–10.0`, cuts named at 2.5s/5.0s/7.5s) with the WIDE → CU character
(reaction) → ECU detail → MEDIUM pattern, order varied every block — full pattern +
interplay staging in `references/kids-styles.md`. Everything below applies to both
templates:
```
AUDIO: {diegetic SFX only} — no voice, no narration, no music.
NEGATIVE: opening on a reference image, a sheet/swatch or a static first frame, leading freeze, dissolves or fades, NEW or foreign colors, colored/gradient/painted background not in the references, recolored characters, style drift, extra people, cloned characters, characters talking, lip-sync, on-screen text, captions, photorealism{2D-ONLY: , 3D render}, watermark.
```
**{MOTION} — match the style family.** Flat 2D styles (webcomic / stick-figure / flat
cartoon, Editorial Collage): `simple limited animation on twos` (collage prefers its
own token — see `style-editorial-collage.md`). Dimensional styles (Paper Diorama, 3D Papercraft, Fluffy
Toy, claymation…): `smooth simple handcrafted motion, subtle stop-motion feel` — and for
these DROP `3D render` from the NEGATIVE (it fights the look; the photorealism ban always
stays).
Vary shot sizes and ANGLE on every cut (WIDE / MEDIUM / CU / ECU / OTS / low / high).
**OTS is valid only when a named on-screen character's shoulder/head is intentionally
visible in the foreground.** In object-only, diagram, empty-location, or any other
characterless shot, never write OTS; use overhead/top-down, low/high, macro, lateral, or
another coverage angle instead. OTS without a referenced character makes the model
invent a person.
Only the FIRST block of a new location may open on a full establishing WIDE; later
blocks in the same location open on a fresh close/medium/coverage angle — never
re-establish the same wide. **≤2 consecutive blocks per location**, then move (new
location / coverage angle / variety insert). Vary the character's distance & screen
position; never park them back at the opening framing. **Every block carries at least
ONE impact beat** (a slam, stamp, snap, whip-pan hit, collapse) — name it in a SHOT line
and echo it in AUDIO; reference-grade explainers land an accent roughly every 3 seconds.
**Action grammar (all styles):** write SHOT beats as pure CHOREOGRAPHY — the {STYLE}
formula owns the look, so no style/color/material words inside beats; elements enter
STAGGERED ("A, then B, then C" — never simultaneously) with landing verbs (snaps into
place, stamps down, drops with a bounce, settles); exactly ONE camera behavior per
shot, stated once (slow push-in / static / gentle drift / whip) — two moves in one cut
reads as AI soup; the FINAL shot eases into a stable, still micro-moving final frame
(settled ≠ frozen — rule 21 holds).
On-screen TEXT is unreliable →
use SYMBOLS (⚠ / $ / ✓ / ✗), let the VO carry words. **Sole exception — Paper
Diorama's letterpress prop label** (ONE 1–2-word label per scene, fenced as
`no text anywhere except "<LABEL>", no gibberish letters, no captions` in place of the
NEGATIVE's `on-screen text, captions` pair — see `style-paper-diorama.md`); every other
style keeps the full text ban.
AUDIO line per block: **SFX follows choreography 1:1** — every motion verb gets at most
ONE cue, 2–4 cues per block + one room-tone bed (whooshes on moves, a stamp hit on the
impact beat, ticks on data steps, sparkles/dings for Kids, ambient of the place);
nothing sounds that didn't move; percussive, never musical — still "no voice, no
narration, no music" (voice + music bed are added in the Phase-6 mix, not inside the
clip).

**Compose from assets, full scenes.** Every clip is staged from the approved Phase-2
assets (location + characters + props as `image_references`) — a real dressed scene with
depth, matching the assets' colors/background, never a lone object on a foreign background.

## 4. Retry ladder (H3 nsfw / preset)
Preset recommendation instead of a job → resubmit the SAME call with `declined_preset_id`
= the recommended preset's id. On `nsfw`: resubmit ≤3× (change `seed` only if declared); if still failing,
reword (drop child/kid/childlike, avoid tight animal-face CU, calm the pose). On terminal
`nsfw` after retries: swap the beat's framing. Never drop a block.
