# Prompt blocks: the house prompt structure

Contents:
1. Assembly rules and per-field defaults
2. The 11 blocks (in this order)
3. Split frames
4. Surgical tweaks on a finished render
5. 3D logo prompt
6. Reference analysis contract
7. Ratio notes and pitfalls

Assemble ONE prompt per variant, in English (translate the user's scene description). Text
strings meant to appear in the image stay verbatim in the user's language. Copy the library
sentences exactly and fill every `<placeholder>`; a `<...>` slot never ships unfilled.
Precedence everywhere: explicit user ask > reference-extracted field > per-field default.

## 1. Assembly rules and defaults

Include / omit rules:
- Blocks 1 and 11: always (a non-photoreal medium replaces 1 with its medium contract and drops 11).
- Block 2: only if the user described exact content (or a reference supplied a `brief`).
- Block 3: always the default no-text line; the TEXT or BAKED UI variant only on an EXPLICIT user text request.
- Block 4: if ANY person or creature is in frame. Photo-referenced people get one Identity Lock each; text-described people are described here in prose (never in block 5) and end with `Expression: <emotion phrase>`.
- Block 5: if signature props exist or the key-elements default applies.
- Block 6: only with a logo.
- Block 7: only if a location is known.
- Blocks 8 and 9: always (use the default lines when nothing is known).
- Block 10: if any person is in frame (plain rig by default; colored rim ONLY when the user names a rim color).
- `<ratio note>` = "`<ratio>` aspect ratio". For 9:16 append the tall-canvas clause; with no people in frame say `the hero subject in the upper two-thirds` instead of `faces`.

Per-field defaults (apply to any field both the user and the reference left empty):
- ratio `16:9`, takes 1, emotion `shock` when a person is in frame.
- BACKGROUND: `bold, vivid saturated color-field gradient with punchy high-contrast tones matching the subject's palette, soft vignette, edge falloff`
- COMPOSITION: `the subject rendered LARGE and dominant — chest-up / medium-close, filling ~40–60% of the frame, pushed to the foreground on a power third, camera at eye level, strong separation from the background so the subject pops, shallow depth with a foreground accent element`
- KEY ELEMENTS: the most concrete depictable noun of the topic (your judgment), oversized, flying toward camera; omit when it would duplicate the SUBJECT.
- LOCATION: omit the block.

## 2. The 11 blocks (assemble in THIS order)

1. **Frame contract:** `Bold, punchy YouTube-thumbnail composite — poster-grade, photoreal and high-impact, NOT a muted cinematic movie still, <ratio note>, single unified frame — no split-screen, no diagonal divide, everything blends smoothly and organically across the same continuous shot.` For 9:16 add `subject framing adapted to the tall canvas, faces in the upper two-thirds`. Framework 8 "Graphical Representation" replaces this with a clean diagram/graphic brief and drops the photoreal + lighting-rig blocks. A non-photoreal medium (paper collage, flat motion graphics, storybook, cutout) replaces it with `reproduce the exact medium of <style>`, naming medium, materials, palette and rendering, ending `NOT photoreal, no real photography`.
2. **Scene brief** (if the user described exact content): `SCENE BRIEF (must be depicted exactly): <text>.`
3. **Text contract.** Default: `No text, no readable UI labels, no watermark.`
   Only when baked text is explicitly wanted: `TEXT: bold thumbnail headline text baked into the image, reading exactly "<TEXT>" — massive, ultra-legible sans-serif with a clean outline/glow treatment, placed where it never covers the subject's face. No other text, no watermark.`
   When the user EXPLICITLY asked for a text-based framework that carries an in-image UI element (Social UI, News Clip, Day badge, Map/Aerial callout), add instead: `BAKED UI: a <generic chat bubble / DM row / star-review card / breaking-news lower-third / DAY N badge / map callout label> reading exactly "<short text>", clean generic platform styling — NO real brand name, app name or network logo. Keep the text short and truthful to the video.`
   A text-carrying framework that was only auto-picked while exploring renders text-free instead. This is the ONLY sanctioned readable text besides the headline; every other prop stays text-free and wordmark-free.
4. **SUBJECT(s):** see emotions-and-lighting.md (identity lock). Up to 3 characters. **Render the subject LARGE and dominant — the clear hero, filling roughly 40–60% of the frame, chest-up or medium-close, pushed to the foreground and cleanly separated from the background; NEVER a small subject stuck in the lower third, never a distant video-frame look.** End with `All faces crisply sharp as the anchors of the shot.`
5. **KEY ELEMENTS:** signature props/effects that make it pop.
6. **LOGO** (if any). 2D: `the attached logo placed into the composition EXACTLY as provided — keep its shapes, colors and proportions untouched, clean 2D placement at a strong focal position, subtle drop shadow for separation, never covering the subject's face.` 3D: `the attached 3D logo render integrated into the scene as a physical volumetric object — glossy dimensional material, catching the scene's key light and rim light, casting a soft contact shadow, composited at a strong focal position without covering the subject's face.`
7. **LOCATION:** place, time of day, weather, atmosphere.
8. **COMPOSITION:** subject LARGE and foreground-dominant (fills ~40–60% of the frame, chest-up / medium-close) on a power third, strong subject-vs-background separation so the subject pops off the background; scale hierarchy, camera angle, depth layering.
9. **BACKGROUND TREATMENT (blended, not divided):** bold saturated color field, vivid punchy gradients, strong color contrast, texture, blur, edge falloff.
10. **LIGHTING (the YouTube rig, mandatory on people):** the plain or colored-rim sentence from emotions-and-lighting.md, verbatim.
11. **GRADE:** the grade sentence from emotions-and-lighting.md, verbatim, with `<ratio>` filled.

Pre-send checklist (any NO means fix the prompt first):
- [ ] Block 1 (or its split / non-photoreal substitution) is the FIRST block; GRADE is the LAST when it applies.
- [ ] Person in frame: lighting rig present verbatim + one identity lock per face photo.
- [ ] Style-reference thumbnail is NOT attached to the generator.
- [ ] One variant per generation (no shared batch prompt).
- [ ] No baked text ordered: the prompt contains `No text, no readable UI labels, no watermark.`

## 3. Split frames

Fires ONLY when the user asks for a split/panel LAYOUT ("split", "before/after", "versus
screen", "side by side") or the reference analysis returned `split=true`. `X vs Y` as a
SCENE means one unified frame with both subjects, no split. N = the number of
contenders/states/facets named (before/after and versus default to 2); N=2 means `halves`,
N>=3 means `vertical panels`. The split contract REPLACES block 1 and carries `<ratio note>` and
the 9:16 tall-canvas clause exactly as block 1 would.

Replace block 1 with: `SPLIT-FRAME thumbnail, <ratio note>: the frame divided into N <halves|vertical panels> by clean bold seams, each panel its own complete mini-scene, unified premium grade across all panels.` Then append exactly ONE mode sentence:

- **plain:** `Each panel shows one facet of the story: <panel 1: desc; panel 2: desc; ...>.`
- **before/after:** `LEFT panel: the BEFORE state — <desc>. RIGHT panel: the AFTER state — <desc>. Maximum visual contrast between the two states of the same transformation.`
- **versus:** `Each panel presents one contender lit and framed like a fighter poster: <panel 1: contender A desc; panel 2: contender B desc>. Equal visual weight, confrontation energy across the seam.`
- **custom:** `<the user's panel-by-panel description>.`

ALWAYS append: `No labels, no captions, no words, no numbers on or between the panels — the comparison reads purely visually. All panels graded as one premium image.`

## 4. Surgical tweaks on a finished render

Feed the FINISHED render back as the image to edit (an image-editing pass in the same or another
model). Every tweak prompt states everything else stays pixel-faithful. Each output becomes the
new source for the next tweak. Allowed scopes: expression only, background replacement only,
background recolor only, rim-light recolor only. Never regenerate the full composition for a
surgical request.

- **Emotion swap:** `Change ONLY the person's facial expression ... to: <phrase>. Keep identity, face structure, hair, pose, body, clothing, logo, background, lighting and composition EXACTLY unchanged, pixel-faithful — pure expression swap. Keep the YouTube thumbnail lighting rig intact.`
- **Background swap:** `Replace ONLY the background with: <desc>. Keep subject, face, identity, pose, clothing, logo and all foreground elements EXACTLY unchanged. Rebuild the lighting wrap around the subject so the new background's light direction, color and rim light read naturally — keep the YouTube rig.`
- **Background recolor:** `Shift ONLY the background color palette to dominant <color> tones. Keep the background's structure, content and depth exactly — only recolor. Rebuild the subtle ambient color wrap on the subject's edges but keep key light and fill on the face unchanged.`
- **Rim light recolor:** `Change ONLY the back light / hair light (rim light) color on the subject to <phrase> — the bright edge tracing hair, shoulders, silhouette. Do NOT change key light or fill; do NOT change background, pose, identity, clothing, logo, composition.`

## 5. 3D logo prompt

Run first, on its own, with the flat 2D logo attached; use the result as the logo reference in
the main render (block 6, 3D variant). Square 1:1, highest resolution available.

> Transform the attached 2D logo into a premium 3D logo render: extrude the exact logo shapes into glossy dimensional volumes, keep every letterform, proportion and brand color EXACT, high-end CGI product-render finish with soft studio reflections, subtle bevels, crisp edges, floating on a clean dark neutral studio background with a soft contact shadow. Centered, generous margins, no extra text, no watermark.

## 6. Reference analysis contract (vision to scene)

When the user attaches an example thumbnail, look at it yourself and extract these fields. The
reference drives energy, composition and style only; it never supplies a face and is never sent
to the generator. Ask once whether to **Match this reference** (closely preserve style,
composition and subject) or make a **Unique take** (loose inspiration only), unless the user
already said which.

```
brief (one dense sentence on the concept), subject (pose/action generically, NEVER a specific
identity), elements, location, composition, background, split (boolean), split_count,
person_count (0-3), emotion (one of the 11 presets or 'other'), emotion_detail (one vivid
sentence covering eyes, brows, mouth, head angle)
```

Field to block mapping: brief to block 2, subject to block 4, elements to block 5, location to
block 7, composition to block 8, background to block 9, split to the split branch, emotion +
emotion_detail to the Expression slot. The reference's subject prose attaches to the photo
characters positionally as their pose/action; it never ADDS a person. Fill any scene field the
user left empty with derive-from-reference instructions ("mirror the reference's framing logic...").

## 7. Ratio notes and pitfalls

- Render at the highest resolution the tool offers and downscale: 16:9 (YouTube, delivered at 1280x720), 9:16 (Shorts / Reels / TikTok covers, delivered at 1080x1920), 4:5 (Instagram feed, delivered at 1080x1350).
- 4:5 exists natively on Nano Banana Pro; many edit models have no 4:5. For tweaks on a 4:5 render, tell the user if the edit model forces 3:4 (crop change).
- Multi-reference runs: prepend the `IMAGE REFERENCES:` manifest numbering each image and its role.
- One variant per generation: a batch count would share one prompt, but emotions and takes each need their own.
- A thumbnail competes at ~120px wide: if emotion and hero element do not read there, fix the composition, not the resolution.
