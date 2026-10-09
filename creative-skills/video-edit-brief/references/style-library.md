# Style library: the 28 Katana presets

Contents
1. How to use this library
2. Index of the 28 presets
3. Verbatim: Grunge Aura (VISUAL LANGUAGE, NUMERICAL COMPOSITING RECIPE, TITLE CHOREOGRAPHY, EMBEDDED EDIT MAP)
4. Verbatim: Many Lies (global look, effects, 48-shot timeline)
5. Verbatim: Lights Out (locked timeline, text slots, lighting rule, theme adaptation)
6. Verbatim: Last Katana (timeline, sections, global look, no-edge rule)
7. Verbatim: Physical Body (product definition, effects, 38-slot timeline)
8. Where to find more recipes in the raw files

## 1. How to use this library

- Use it as a catalogue of ready-made edit styles: pick the preset closest to the look and pacing you want, read its row, then open its raw file and its edit map.
- Only 1 of the 28 files (Grunge Aura) follows the pure author master-prompt structure (execution contract, input contract, fixed reference, preset lock, visual language, subject adaptation, numerical compositing recipe, title choreography, embedded edit map, audio, execution, delivery). 11 are long slot/kit presets whose useful part is a locked timeline plus text/asset slots and a review checklist. 16 are short stubs: they only point at a reference video; for those, the edit map in `katana-refs` is the whole specification (cut rhythm, cadence, flashes, inverts, look statistics).
- The pipelines in the raw files (kits, sandboxes, pinned downloads, specific generator models and tool calls) belong to the original platform. Ignore them; take the timeline, the numbers, the text slots, the lighting rules and the review checklists.
- The edit maps are detector proposals measured on the preset's reference copy. The copy can differ from the shipped template (for example the Many Lies map covers 601 frames at 20 fps while the template is 366 frames at 24 fps). When a preset states its own lock (resolution, fps, frame count), that lock wins; the map's frame counts are only a pacing reference. The fps in a map header is the rate of the analysed preview copy and can be a resampled rate (the Kawaii Pop map says 15 fps while the template runs at 30 fps), so treat the durations quoted for stubs as approximate.
- The stubs' one-line descriptions below are derived from the map statistics (luma, saturation, hue, warmth, cuts per second, flashes, cadence), not from watching the video. Watch the reference before relying on them.
- The verbatim sections are copied character for character except that em-dashes became hyphens and two platform links were dropped. Original names of franchises and creators appear only in file names or quotes; do not copy characters, logos, costumes or names into your own work.

Categories (from the catalogue): `aura_farming` (character/vibe edits), `motion` (motion-graphics or launch style), `clipping` (edits built from the user's own clip).

## 2. Index of the 28 presets

| slug | title | category | visual language (one line) | length / format | master prompt file | edit map |
|---|---|---|---|---|---|---|
| `grunge-aura` | Grunge Aura | aura_farming | Nearly monochrome editorial grunge: dense blacks, dirty paper whites, silver midtones, film grain, photocopy degradation, halftone, scratches, folded paper, scanner streaks, brief negatives, graphic collage; bold sans letter fragments and tiny technical annotations | 1620x1080 (3:2), 474 frames at 24000/1001 fps, ~19.77 s | author master prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/grunge-aura.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/grunge-aura.md` |
| `dreamy-streetwear` | Dreamy Streetwear | aura_farming | (derived from the edit map only) bright, near-monochrome with one orange accent; 2.1 cuts/s (37 cuts); smooth native cadence; 1 burst, 4 flashes, 5 inverts | map (preview copy): 450 frames at 25 fps, about 18.0 s, 600x450 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/dreamy-streetwear.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/dreamy-streetwear.md` |
| `power-suit` | Power Suit | aura_farming | (derived from the edit map only) mid-key, saturated orange, neutral-temperature; 0.5 cuts/s (42 cuts); 24p-in-60p pulldown cadence; 2 flashes | map (preview copy): 1932 frames at 25 fps, about 77.3 s, 600x450 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/power-suit.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/power-suit.md` |
| `outfit-check` | Outfit Check | aura_farming | (derived from the edit map only) mid-key, moderately saturated orange, warm; 0.6 cuts/s (8 cuts); smooth native cadence; 1 burst | map (preview copy): 288 frames at 21.43 fps, about 13.4 s, 600x1066 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/outfit-check.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/outfit-check.md` |
| `tiger-eyes` | Tiger Eyes | aura_farming | (derived from the edit map only) dark, moderately saturated green, neutral-temperature; 1.3 cuts/s (14 cuts); smooth native cadence; 4 flashes, 1 invert | map (preview copy): 264 frames at 24 fps, about 11.0 s, 600x450 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/tiger-eyes.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/tiger-eyes.md` |
| `frame-dance` | Frame Dance | aura_farming | (derived from the edit map only) very dark, moderately saturated orange, neutral-temperature; 0.7 cuts/s (13 cuts); pulldown_24in30; 3 flashes | map (preview copy): 452 frames at 23.976 fps, about 18.9 s, 576x768 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/frame-dance.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/frame-dance.md` |
| `tokyo-bloom` | Tokyo Bloom | aura_farming | (derived from the edit map only) mid-key, saturated red, neutral-temperature; 2.9 cuts/s (36 cuts); smooth native cadence; 3 bursts, 11 flashes | map (preview copy): 296 frames at 23.976 fps, about 12.3 s, 600x450 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/tokyo-bloom.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/tokyo-bloom.md` |
| `star` | Star | aura_farming | (derived from the edit map only) bright, moderately saturated blue, neutral-temperature; 1.2 cuts/s (20 cuts); mixed cadence; 8 flashes | map (preview copy): 326 frames at 20 fps, about 16.3 s, 600x338 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/star.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/star.md` |
| `blue-eyes` | Blue Eyes | aura_farming | (derived from the edit map only) dark, saturated blue, cool; 1.4 cuts/s (42 cuts); smooth native cadence; 15 flashes, 1 invert | map (preview copy): 720 frames at 23.976 fps, about 30.0 s, 600x450 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/blue-eyes.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/blue-eyes.md` |
| `dark-and-moody` | Dark and Moody | aura_farming | (derived from the edit map only) dark, black and white; 1.1 cuts/s (27 cuts); smooth native cadence; 11 flashes | map (preview copy): 592 frames at 25 fps, about 23.7 s, 600x450 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/dark-and-moody.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/dark-and-moody.md` |
| `painting-flow` | Painting Flow | aura_farming | (derived from the edit map only) mid-key, saturated orange, warm; 1.5 cuts/s (32 cuts); mixed cadence; 1 burst, 8 flashes, 1 invert | map (preview copy): 330 frames at 15 fps, about 22.0 s, 600x338 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/painting-flow.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/painting-flow.md` |
| `dark-aura` | Dark Aura | aura_farming | (derived from the edit map only) dark, moderately saturated cyan, neutral-temperature; 3.0 cuts/s (63 cuts); smooth native cadence; 7 bursts, 9 flashes, 1 invert | map (preview copy): 520 frames at 25 fps, about 20.8 s, 600x338 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/dark-aura.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/dark-aura.md` |
| `nocturne` | Nocturne | aura_farming | (derived from the edit map only) mid-key, saturated orange, warm; 0.9 cuts/s (25 cuts); smooth native cadence; 1 burst, 12 flashes | map (preview copy): 652 frames at 24 fps, about 27.2 s, 600x338 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/nocturne.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/nocturne.md` |
| `car-edit` | Car Edit | aura_farming | (derived from the edit map only) very dark, muted red, neutral-temperature; 1.4 cuts/s (34 cuts); smooth native cadence; 2 bursts, 25 flashes | map (preview copy): 360 frames at 15 fps, about 24.0 s, 600x338 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/car-edit.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/car-edit.md` |
| `xerox-3` | Xerox 3 | aura_farming | (derived from the edit map only) mid-key, moderately saturated red, neutral-temperature; 3.4 cuts/s (71 cuts); smooth native cadence; 11 flashes, 18 inverts | map (preview copy): 504 frames at 24 fps, about 21.0 s, 600x450 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/xerox-3.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/xerox-3.md` |
| `xerox-2` | Xerox 2 | aura_farming | (derived from the edit map only) mid-key, moderately saturated magenta, neutral-temperature; 3.0 cuts/s (66 cuts); smooth native cadence; 3 bursts, 3 flashes, 8 inverts | map (preview copy): 528 frames at 24 fps, about 22.0 s, 600x450 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/xerox-2.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/xerox-2.md` |
| `the-boys` | The Boys | aura_farming | Prestige superhero drama in a 2.39:1 letterbox: hero shots re-performed from fixed driver clips, generated B-roll chapters, word-by-word dialogue captions, a title card with name and subtitle, soundtrack with dialogue | 1920x1080 at 24 fps, 781 frames, 32.54 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/the-boys.md` | none |
| `kawaii-pop` | Kawaii Pop | aura_farming | Sugary idol backstage selfie vlog: bright airy white light, rosy skin, pale lilac starburst and offset halo, chunky white words snapping onto the face on every chant beat, magenta flashes and flashlight blow-outs on every cut, cat-paw gestures | 900x720 (5:4) at 30 fps, video 283 frames = 9.43 s (audio 9.52 s) | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/kawaii-pop.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/kawaii-pop.md` |
| `let-me-show-you` | Let Me Show You | aura_farming | Cream-studio aura edit: red lyric words behind the subject, matte-swap transitions, halo close-up, teal tint, light streak, amber film burns, eclipse-ring iris ending | 1920x1080 at 25 fps, 14.2 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/let-me-show-you.md` | none |
| `last-katana` | Last Katana | aura_farming | Cold TV-anime swordsman edit: black silhouette flies up through black/white inversions while lines type on, teal duotone manga panels, katana-draw cut, six-card collage, walk toward camera over a giant glowing eye; ~129 BPM | 1920x1080 at 30 fps, 594 frames, 19.8 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/last-katana.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/last-katana.md` |
| `pink-collage` | Pink Collage | aura_farming | Y2K girly 'aura' template: soft pink grade, pink halftone paper, round-dot transitions, sticker collages, dotted ornate frames, collectible aura cards, pencil-drawn ornaments, lettering alternating neon script and bouncy crayon; two drops of a 16-beat loop at 136.15 BPM | 1080x1080 (1:1) at 60 fps, 795 frames, 13.25 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/pink-collage.md` | none |
| `launch-cut` | Launch Cut | motion | 30-second product ad: live footage plus an animated clone of the product UI, kinetic type, a camera that moves through the app, visible triggers between scenes, one big final moment, end lockup with the call to action | 1920x1080 at 30 fps, 30 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/launch-cut.md` | none |
| `lights-out` | Lights Out | motion | Kinetic-typography edit built on red/black lighting recolored by one hue shift: start-light countdown, serif hero words partly behind the subject, tilted poster with words appearing like ink in water, panel flies, giant extruded words, letter-by-letter vanish, outro on a red gradient | 1280x720 at 30 fps, 523 frames, 17.433 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/lights-out.md` | none |
| `living-lab` | Living Lab | motion | Launch film alternating a BLACK instrument grid and CREAM specimen paper: dot-matrix model vision, thermal remaps, window grids, construction lines, orbits, rulers, coordinate labels, kinetic typography; macro nature, fashion portraits, matte-clay 3D | 1920x1080 at 24 fps, 30 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/living-lab.md` | none |
| `chrome-orbit` | Chrome Orbit | motion | (derived from the edit map only) bright, near-monochrome with one purple accent; 1.3 cuts/s (28 cuts); stepped low-fps cadence; 6 flashes, 2 inverts | map (preview copy): 252 frames at 12 fps, about 21.0 s, 960x720 | stub (reference wrapper): `<PLAYGROUND>/higgsfield-prompts/raw/katana/chrome-orbit.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/chrome-orbit.md` |
| `travel-edit` | Travel Edit | clipping | Travel mood edit: flash cuts, smears, echo trails, typed two-tone title, squash word, place word, handwritten line, end card; 180 slots in 28 sections cut to a fixed soundtrack | 1916x1078 at 20 fps, 560 frames, 28.0 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/travel-edit.md` | none |
| `many-lies` | Many Lies | clipping | Strobe music edit at 160 BPM (9 frames per beat): B/W and muted-colour shots, LIAR / FAKE / TRUTH word pops, red label boxes, video inside giant letters, triptych/2x2/3x3 collages, polaroids, marquees, text wall, flashes and glitches, ending on colour shots and a short negative | 1440x1080 (4:3) at 24 fps, 366 frames, 15.25 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/many-lies.md` | `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/many-lies.md` |
| `physical-body` | Physical Body | clipping | Overlay edit for the idea 'I am more than my physical body': B/W, teal, warm and violet looks, white/black flash frames, silhouette and star frames, tracking overlays with coordinate labels, 2.4:1 panel cascades, split screen, nested-panel tunnel finale, lower-case lyric captions | 1920x1080 at 30 fps, 354 frames, 11.8 s | long slot/kit prompt: `<PLAYGROUND>/higgsfield-prompts/raw/katana/physical-body.md` | none |

Notes: `kawaii-pop`, `launch-cut` and `let-me-show-you` also have `.part-2.md` continuation files in the same folder. `chrome-orbit` is a `motion` stub: its map (252 frames at 12 fps, 18 of 28 shots stepped, one purple accent over a bright field) is the only specification.


## 3. Verbatim: Grunge Aura

Format: author master prompt. The only preset in the pack with every canonical section. Note how every look word is paired with a number, how frames (not seconds) are the timing authority, and how the title gets an envelope in pixels plus a frame-by-frame life.

### VISUAL LANGUAGE

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/grunge-aura.md` lines 84-89

````
VISUAL LANGUAGE
Nearly monochrome editorial grunge: dense blacks, dirty paper whites, silver midtones, film grain, photocopy degradation, halftone screens, scratches, dust, folded paper, scanner streaks, brief negatives, hard cuts, and graphic collage.

Match the reference's changes in brightness, scale, and visual density at corresponding moments. Use quiet readable subject shots between aggressive transition frames. Texture must feel integrated into the image rather than like one static noise layer over the entire film. Preserve the face, silhouette, or product shape in the readable shots.

Typography uses bold sans-serif letter fragments, abrupt scale changes, broken alignment, tiny technical annotations, registration marks, and small frames. Render readable text in the compositor rather than relying on generated lettering. Use the supplied title or SUBJECT / 01; use IMAGE STUDY, FRAME 001, and END OF STUDY for secondary labels. Replace the reference's pack advertisements and creator signatures with neutral subject-specific text. Do not attribute the new edit to the reference creator.
````

### NUMERICAL COMPOSITING RECIPE

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/grunge-aura.md` lines 120-131

````
NUMERICAL COMPOSITING RECIPE
The following values come from the completed Claude renderer. Treat them as reproducible starting settings at 1620x1080, then adjust only when a new input loses readability.

- Crop without stretching to 3:2 around a subject-specific focal point. Remove genuine source letterboxing, but do not mistake a dark scene for black bars. Never expose mirrored faces or repeated object fragments at transformed frame edges.
- For every reference frame, measure grayscale mean and standard deviation once. For a subject frame g, form target = (g - mean(g)) / max(std(g), epsilon) * max(std(reference), 10) + mean(reference). Blend approximately 10% g with 90% target and clamp to 0..255. Reduce the strength for nearly uniform inputs or clipped faces. Match the reference's exposure progression, not just a single global black-and-white filter.
- Apply a small Gaussian softening, about sigma 1.4 px, vignette strength about 0.30, and animated grayscale grain with an initial sigma of 13, spatially softened around 0.6 px. Use a fixed master seed with deterministic frame offsets. Scale spatial effect sizes for preview resolution.
- Use halftone cells approximately 7–10 px, with strength animated to the relevant event. At frames 322–328, the completed implementation ramps halftone toward 0.8 before the block transition at 329–335.
- For selected bright accents, start around 1.45 * image + 30, clamped to 0..255. Selected horizontal motion-blur inserts use a kernel around 61 px. Block transitions use a small set of block sizes around 24, 40, 64, and 96 px, with a roughly 44 px grid; mix the outgoing and incoming subject compositions rather than introducing unrelated footage.
- Horizontal smear strips are approximately 4–40 px high with lateral offsets up to about 300 px and occasional 25x1 px blur. Clamp strip height to the remaining image rows. Apply intense distortions only at their assigned events.
- Use dust and fine scratches as time-varying finishing layers. Keep stronger photocopy thresholds, negative frames, torn-paper reveals, and block transitions localized to the montage map.
- Reuse clean reference textures where verified. Inspect every selected insert for hidden faces, hands, signatures, or captions; the label "texture" is not proof that a frame is safe to reuse.
- Remove old end-card lettering by local background reconstruction or inpainting, then typeset the new label. Do not hide old text with conspicuous black rectangles.
````

### TITLE CHOREOGRAPHY

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/grunge-aura.md` lines 133-140

````
TITLE CHOREOGRAPHY
Fit the current title into the reference's spatial envelope using measured text bounds. Do not simply replace MAKI with a longer word at fixed coordinates. Adjust line breaks, size, and tracking without distorting letterforms.

At 1620x1080, use the compact title area around x=528..1100 and y=462..620 as a starting envelope. The upper fragment begins near (528,462), the lower fragment near (598,540), and the supporting line near y=584. Derive positions for the current words from their actual widths.

Frames 21–22: oversized broken title fragments, around 270 px nominal size. Frames 23–27: partial fragments, ghosted letters, marginal microtype, and a small graphic waveform. Frames 28–31: remaining fragments and subtitle progressively appear. Frames 32–34: the title resolves into readable text. Frame 35: photocopy/grunge hit. Frames 50–64: compact light-on-dark title composition. Frame 65: short dark glitch.

Use available bold grotesk, monospaced/typewriter, and optional handwriting fonts. The completed renderer used TeX Gyre Heros, TeX Gyre Cursor, Poppins, and Noto; these are examples, not guaranteed dependencies. Select installed substitutes by shape and test the glyphs. Keep all words, initials, dates, icons, and microcopy subject-neutral or supplied by the user; remove hardcoded anime lore throughout the compositor, not only in the main title.
````

### EMBEDDED EDIT MAP

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/grunge-aura.md` lines 151-200

````
EMBEDDED EDIT MAP
Use the actual video to refine composition and effect behavior. The following frame map is the fixed structure:

0-15: dark wide or medium subject shot, subtle internal movement.
15-19: two brief negative/dirty scan phases.
19-37: bright paper title; scattered oversized letter fragments converge into a compact title; finish with a grunge hit.
37-46: return to the dark opening shot.
46-50: dense ornamental or object-based collage insert.
50-66: dark title layout, small white title, fine marginal text.
66-71: folded-paper and horizontal texture transition.
71-83: expressive medium or close subject shot.
83-96: tighter face, hand, or defining object detail.
96-112: alternate crop or angle, dark high-contrast framing.
112-122: scan streaks followed by graphic bars and rhythmic abstraction.
122-130: wider subject composition with horizontal lines.
130-138: abrupt close-up.
138-140: two-frame scratched insert.
140-160: extreme detail; halftone treatment followed by a cleaner readable version.
160-164: two brief paper/type fragments.
164-177: medium composition with a small action or displacement.
177-190: rapid close crops and details, ending in a paper-frame collage.
190-213: radial stripes, vertical bars, perspective space, vertical smear; connect abstract forms to the subject.
213-226: paper, frame number, vertical form, distressed surface, handwriting or notation textures.
226-238: airy wide composition, silhouette, or floating paper elements; final exposure accent.
238-240: dark two-frame ornamental hit.
240-255: readable wider subject composition with directional motion.
255-261: dark mesh followed by light folded material.
261-273: low angle or macro detail appropriate to the subject.
273-302: restrained high-contrast subject compositions with a scale change; brief black interruption at 279-281.
302-309: white paper, horizontal streaks, printed collage.
309-322: architectural or geometric forms related to the subject; exposure/negative accent and return.
322-341: expressive silhouette or detail behind a grid/halftone texture; small push-in.
341-350: strong readable pose or hero object angle.
350-356: dark handwriting texture.
356-367: close portrait or the subject's most recognizable feature.
367-369: dark two-frame texture hit.
369-379: final expressive subject close-up.
379-381: texture transition into darkness.
381-424: near-black card, tiny neutral label, faint dust.
424-426: two-frame texture flash.
426-474: black closing card with very small END OF STUDY.

Exact event boundaries:
[0,15,17,19,21,23,35,37,46,48,50,66,69,71,83,96,112,114,120,122,128,130,138,140,145,160,162,164,177,179,182,187,190,192,199,207,209,213,216,221,224,226,228,236,238,240,255,259,261,273,279,281,283,302,304,307,309,318,320,322,341,350,356,367,369,379,381,424,426,474]

These include brief visual events within shots. Do not interpret every boundary as a new scene. If direct frame inspection establishes a discrepancy, follow the actual original and retain integer-frame timing.

The accompanying historical renderer uses inclusive end frames, whereas this prompt uses end-exclusive ranges. Convert explicitly when adapting it. Assert that every frame 0..473 belongs to exactly one output segment, with no gaps, overlaps, or duplicate seam frames. Verify cached source keys and the frame shape/dtype before launching a long render.

Preserve the short implementation events inside the broader ranges: torn reveal around frame 71, a one-frame neutral code/technical graphic at 119, block transition at 329–335, and a brief edge ghost at 357. Adapt every visible word to the current subject. The closing title should fade out over approximately frames 460–472. Consult the actual reference for single-frame exposure and boundary behavior; old implementation files can contain approximations or defects and do not override the original reference.
````

## 4. Verbatim: Many Lies

Format: slot-based strobe edit. Fixed 160 BPM track, 48 shots in a 366-frame timeline at 24 fps; shots are refilled from one clip. Use it as a model of how to write a beat-locked timeline with grade, effects and text per shot.

### Global look, effects, music and timeline

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/many-lies.md` lines 206-271

````
## 5. The template, element by element

**Global look.** 24 fps, 1440×1080. Footage is cropped from the clip (zoom ≥ cover, never outside the source) and
graded per shot: `bw` = partial levels stretch + S-curve black-and-white; `color` = muted, slightly cool colour;
`pop` = B/W where only saturated warm hues (glowing red/orange eyes) stay in colour with a glow - a `pop` shot or
panel falls back to `bw` when the clip has no such eyes (with `--glow`, a painted warm eye glow is added). After the
graphics, RGB split and scanlines, every frame except the pure-black end gets a 0.65 px soften, a highlight bloom
(screen 42 % at quarter resolution), a vignette (−38 % at the corners) and film grain (σ 0.032). Text is Arial Bold
(Liberation Sans Bold in the sandbox), white; word pops and kinetic words have a soft drop shadow (not the outlined
FAKE, the black TRUTH or WHO ARE YOU?); marquees, red labels, the text wall, the counter and the viewfinder have
none. Accent red = RGB (0.88, 0.07, 0.09). Effects: **flash** = white overlay that decays (e.g. 0.6/0.2 = 60 % then
20 % white on a shot's first two frames; collage panels flash 55 % on the frame they appear), **punch** = zoom kick
that settles in 5 frames, **slit glitch**, **RGB split**, **scanlines** (2 px dark lines every 4 px, 14 %, on frames
0–8 and 288–296), **slices** (6 bands that slide in over 4 frames), **red wipe bar**, **shake**, **light leak**,
**video inside letters** (letters shrink from 1.2× to 1×), triptych / 2×2 / 3×3 **collages** popping panel by panel,
**polaroids** (white border, rotation, shadow), **marquees**, a scrolling **text wall** (every 3rd line in a red box),
a **“LIES 00xxx” counter** with a red dot (bottom right, frames 90–161, +13 per frame, restarts at 00361 on frame 117),
**viewfinder** brackets with timecode and “DON'T LOOK BACK”, **kinetic** words rising from the bottom.

**Music.** The template track (160 BPM, 9 frames per beat), frame 0 = the drop, 15.25 s; the last 6 frames are black.

**Timeline** (48 shots; frame numbers are output frames; “slot” = which moment of the clip fills it):

| frames | seconds | len | shot | footage (slot, kind) | grade | graphics and effects |
|---|---|---|---|---|---|---|
| 0–1 | 0.00–0.08 | 2 | x1 | eyesA (eyes) | pop | flash 0.6/0.2; zoom ×1→1.03; RGB split 0,1; scanlines |
| 2 | 0.08–0.12 | 1 | x2 | WHITE |  | scanlines |
| 3–4 | 0.12–0.21 | 2 | x3 | liar (face) | bw | zoom ×1→1.02; word "LIAR" 240px; scanlines |
| 5–6 | 0.21–0.29 | 2 | x4 | eyesB (eyes) | bw | scanlines |
| 7–8 | 0.29–0.38 | 2 | x5 | eyesA +4 (eyes) | pop | glitch on frame 8; RGB split 7,8; scanlines |
| 9–35 | 0.38–1.50 | 27 | walk | walk (walk) | color | zoom ×1→1.08; marquee "TRUST NO ONE" (top) + outlined "SO MANY LIES" (bottom); viewfinder "DON'T LOOK BACK" |
| 36–53 | 1.50–2.25 | 18 | wide | wide (wide) | color | zoom ×1→1.04; word "SO" 260px (36–44); slices 36–39; word "MANY" 260px (45–53) |
| 54–62 | 2.25–2.62 | 9 | det1 | det1 (detail) | color | zoom ×1→1.05; word "LIES" 240px in a red box wiping in |
| 63–65 | 2.62–2.75 | 3 | tell | tell (face) | bw | word "TELL" 220px; RGB split 63,64 |
| 66–67 | 2.75–2.83 | 2 | me | me (face) | bw | word "ME" 220px; RGB split 66 |
| 68–69 | 2.83–2.92 | 2 | the | the (face) | bw | word "THE" 220px; RGB split 68 |
| 70 | 2.92–2.96 | 1 | wh1 | WHITE |  | black word "TRUTH" 220px |
| 71 | 2.96–3.00 | 1 | truth | truth (profile) | bw | word "TRUTH" 220px |
| 72–89 | 3.00–3.75 | 18 | s0–s8 | strobe every 2 frames: strA (medium, bw, flash 0.7/0.25 on every A, real time) ↔ strB (eyes, pop; B start advances at 0.35× so the eyes barely move) | bw/pop | "I SEE THROUGH YOU" 64px bottom; RGB split 72,73 |
| 90–98 | 3.75–4.12 | 9 | fake | fake (profile) | bw | punch 0.06; outlined word "FAKE" 300px; slices 90–93; shake 90–93; counter starts; RGB split 90,91 |
| 99–107 | 4.12–4.50 | 9 | stop | stop (profile) | bw | zoom ×1→1.04; red label "STOP LYING" |
| 108–116 | 4.50–4.88 | 9 | knew | knew (face) | bw | zoom ×1→1.05; red label "YOU KNOW WHAT YOU DID" |
| 117–125 | 4.88–5.25 | 9 | tri | triptych tri1 / tri2 / tri3 at +0/+3/+6 | bw | red labels TRUTH / LIES / SECRETS with their panels; RGB split 117 |
| 126–134 | 5.25–5.62 | 9 | watch | watch (hero) | bw | zoom ×1→1.04; word "WATCH ME" 108px low |
| 135–143 | 5.62–6.00 | 9 | grid4 | 2×2 grid g4a (pop) / g4b / g4c / g4d at +0/+2/+4/+6 | bw | red label "EYES DON'T LIE" centre from +1; RGB split 135 |
| 144–161 | 6.00–6.75 | 18 | stack | stackS (medium) | bw | zoom ×1→1.05; text wall (TRUST NO ONE, NOTHING IS REAL, SAY IT AGAIN, BEHIND THE EYES, NO MORE SECRETS, SO MANY LIES); red wipe 159–161 |
| 162–197 | 6.75–8.25 | 36 | det2 | det2 (detail) | color | zoom ×1→1.1; slices 162–165; red label "THE TRUTH HURTS" top from +2; red light leak from +4; polaroids cut1 / cut2 / cut3 at +9/+18/+27 |
| 198–206 | 8.25–8.62 | 9 | kn1 | kn1 (bright) | bw | zoom ×1.1 held; video inside "TRUST / NO / ONE" (320px) on black |
| 207–208 | 8.62–8.71 | 2 | wh2 | WHITE |  |  |
| 209–212 | 8.71–8.88 | 4 | glow | glowF (face) | bw |  |
| 213–215 | 8.88–9.00 | 3 | bk1 | BLACK |  | "WHO ARE YOU?" 90px |
| 216–233 | 9.00–9.75 | 18 | hit | hit (medium) | bw | flash 0.85/0.45/0.18; punch 0.08; zoom ×1→1.05; slices 216–219; marquee "NO MORE LIES" (top) + red "BURN IT ALL DOWN" (bottom); RGB split 216–218 |
| 234–242 | 9.75–10.12 | 9 | say | say (profile) | bw | red label "SAY IT AGAIN" |
| 243–251 | 10.12–10.50 | 9 | kn2 | kn2 (bright) | bw | zoom ×1.1 held; video inside "LIES" (500px) on red |
| 252–269 | 10.50–11.25 | 18 | grid9 | 3×3 grid: centre g94 +0, corners g90/g98/g92/g96 +2/+3/+4/+6, edges g91/g97/g93/g95 +7/+8/+10/+11 | bw | red label "NOTHING IS REAL" centre from +4; RGB split 252 |
| 270–287 | 11.25–12.00 | 18 | hero1 | hero1 (hero) | pop | zoom ×1→1.06; "EYES" → "EYES DON'T" → "EYES DON'T LIE" 88px (6 frames each) |
| 288–289 | 12.00–12.08 | 2 | bliar | bLiar (face) | bw | flash 0.5/0.1; word "LIAR" 240px; RGB split 288,289; scanlines |
| 290 | 12.08–12.12 | 1 | wh3 | WHITE |  | scanlines |
| 291–292 | 12.12–12.21 | 2 | bfake | bFake (profile) | bw | outlined word "FAKE" 300px; scanlines |
| 293–296 | 12.21–12.38 | 4 | btruth | bTruth (eyes) | pop | glitch on frame 293; zoom ×1→1.04; word "TRUTH?" 220px; RGB split 293; scanlines |
| 297–305 | 12.38–12.75 | 9 | know | know (medium) | color | zoom ×1→1.04; "I KNOW." 60px; red wipe 303–305; RGB split 297 |
| 306–341 | 12.75–14.25 | 36 | hero2 | hero2 (hero) | color | zoom ×1→1.1; slices 306–309; red marquee "TRUST NO ONE" top; red leak; kinetic SO (+0) / MANY (+10) / red-boxed LIES (+19) rising |
| 342–356 | 14.25–14.88 | 15 | back | back (back) | color | zoom ×1→1.03; "SO MANY LIES." 56px centre |
| 357–359 | 14.88–15.00 | 3 | neg | back +15 (back) | color | zoom ×1.03 held; negative; RGB split 357–359 |
| 360–365 | 15.00–15.25 | 6 | end | BLACK |  | (no grain) |

````

### People and slot kinds (how moments are picked)

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/many-lies.md` lines 272-315

````
**People and slot kinds.** `prep` groups faces into people with face identities (SFace); the **hero** is the person
with the most face screen time, or the one you name with `"hero"` (§7). Close-up kinds frame the hero and fall back
to the largest face only when the hero is not available: `eyes` (extreme close-up, eye distance ≈ 40 % of the width),
`face` (face ≈ 58 % of the height), `hero` (best frontal close-up, held, ≈ 66 %). Person kinds prefer the hero but
accept anyone: `profile` (face present, not frontal), `medium` (face ≈ 20 %, person in the space), `walk` (long
moving shot), `back` (turned away / leaving, late in the clip; never an empty frame), `bright` (light footage inside
the letters). `wide` (whole frame, action) and `detail` (below the face / no face: hands, clothes, objects) take any
footage. Zoom is capped at 3.0 to avoid soft upscales, so small faces give looser close-ups (warning “wanted zoom …
capped”). Moments never cross a source cut unless nothing else fits, keep ≥ 1 s apart when the clip allows, timeline
neighbours avoid the same source shot, and collage / polaroid panels may reuse moments (they are recaps).

**Slots** (names for fixes; case-sensitive):

| slot | kind | shots | what it should show |
|---|---|---|---|
| eyesA | eyes | x1, x5 | eyes ECU of the drop |
| liar | face | x3 | hard stare for LIAR |
| eyesB | eyes | x4 | second eyes ECU |
| walk | walk | walk | walking / turning, 27 frames |
| wide | wide | wide | action wide shot, 18 frames |
| det1 | detail | det1 | hand / object detail under LIES |
| tell, me, the | face | tell, me, the | three different close-ups |
| truth | profile | truth | profile under TRUTH |
| strA | medium | s0, s2, s4, s6, s8 | strobe A: the person in the space |
| strB | eyes | s1, s3, s5, s7 | strobe B: eyes |
| fake | profile | fake | confrontation / profile for FAKE |
| stop | profile | stop | profile, STOP LYING |
| knew | face | knew | angry close-up, YOU KNOW WHAT YOU DID |
| tri1, tri2, tri3 | medium, face, eyes | tri (panels) | triptych TRUTH / LIES / SECRETS |
| watch | hero | watch | frontal close-up WATCH ME |
| g4a, g4b, g4c, g4d | eyes, eyes, face, face | grid4 (panels) | 2×2 grid |
| stackS | medium | stack | medium shot under the text wall, 18 frames |
| det2 | detail | det2 | long colour detail, 36 frames, polaroids on top |
| cut1, cut2, cut3 | face, face, medium | polaroids | polaroids on det2 |
| kn1, kn2 | bright | kn1, kn2 | light footage inside TRUST NO ONE / LIES |
| glowF | face | glow | 4-frame stare after the white |
| hit | medium | hit | the hit: punch + flash, 18 frames |
| say | profile | say | shouting / talking profile, SAY IT AGAIN |
| g90 … g98 | eyes / face alternating | grid9 (panels) | 3×3 grid |
| hero1 | hero | hero1 | EYES DON'T LIE close-up, 18 frames |
| bLiar, bFake, bTruth | face, profile, eyes | bliar, bfake, btruth | the burst before the finale |
| know | medium | know | I KNOW. medium, colour |
| hero2 | hero | hero2 | SO MANY LIES hero close-up, colour, 36 frames |
| back | back | back, neg | walking / turning away: finale and its negative |
````

## 5. Verbatim: Lights Out

Format: slot-based kinetic-typography edit, 17.433 s. Look at how every text slot has a length limit, how every footage slot has a purpose and a lighting rule, and how themes only swap placeholders.

### Audio hit points

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/lights-out.md` lines 159-168

````
The timeline is cut to a hard-hitting hip-hop/trap beat. Key hit points (seconds):

`3.633 (main drop) · 4.77 · 5.20 · 5.56 · 7.33 · 7.43 · 8.00 · 8.40 · 9.32 · 9.68 · 10.70 · 10.90 · 11.13 · 12.80 · 13.60 · 14.52`

- Audio must be the user's own or licensed by them. Do not fetch music from anywhere.
- Trim so the track's main drop lands at **3.633 s**: `offset = drop − 3.633`.
  - If `offset ≥ 0`: `ffmpeg -y -ss <offset> -i <src> -t 17.434 -vn -ac 2 -ar 48000 audio.wav`
  - If `offset < 0`: pad the start: `ffmpeg -y -i <src> -af "adelay=<ms>:all=1" -t 17.434 -vn -ac 2 -ar 48000 audio.wav` with `ms = round(−offset·1000)`.
- If `audio_drop_seconds` is absent, find the drop as the largest onset-energy jump in the first 90 s (e.g. `ffmpeg … -af astats` per 50 ms window, or `sox` stat), state the chosen time, and offer to adjust.
- No audio → render silent and tell the user to add sound on the platform from its licensed library.
````

### Template timeline (locked)

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/lights-out.md` lines 170-195

````
## Template timeline

Locked. Listed so you can judge previews and explain the edit; never change it.

| Time (s) | Section | Footage | What happens |
|---|---|---|---|
| 0.000–3.633 | Start lights | `c1` at 1.3× speed | Five lamps light one by one, then go out. Chromatic glint sweep at 2.8–3.1. |
| 3.633–3.833 | Assembly | `c2` over the last c1 frame | Subject assembles through diagonal shard masks. `lights` word goes from stretched to normal (scaleY 2.5→1 in 4 frames). |
| 3.633–4.50 | Hero 1 | `c2` + matte | Serif word partly behind the subject (depth), slow drift and shrink. Dark diagonal slashes, red haze background. |
| 4.50–4.77 | Light leak | - | Smoky diagonal leak from bottom-left to white-pink (92%). |
| 4.77–5.20 | Hero object | `c3` + matte | Object slides left→right through the giant `out` word. Red-top gradient. |
| 5.20–5.40 | Noise transition | - | Black blotches eat the frame, red `fear` word grows through (slow-start ease). |
| 5.40–5.56 | Red word | - | Full-height serif `fear` word, soft vertical beam. |
| 5.56–5.73 | Noise transition | - | Into the poster. |
| 5.73–7.33 | Poster | S4 still | Tilted (−16°) newspaper sheet in dark-red space, panning down. Words appear and leave like ink in water: `full`, `thr` (white on charcoal plate), `no`, `brakes` (photo-filled, slides in with a smear), `limits`. Red light wash from 7.05. |
| 7.33–7.43 | Red flash | - | Red light over the poster (75%), then a 50% mix into the next shot. |
| 7.43–9.42 | Hero front | `c5` scaled 0.78 + matte | Shockwave and shake on entry. Red gradient, vertical beam, glitch blocks. `racer` slides in with a streak. Anamorphic flares at 8.0 and 8.4. Six panels fly into the corners from 8.05 (3 live clips + 3 stills). `win`/`fast` fly in. Pull-back 8.4–9.0. Zoom-blur and outline `legend` from 8.9. `rise` plate slams at 9.32. |
| 9.42–9.68 | Giant 3D word | - | Huge extruded `go`, diagonal beam, `rise` plate. |
| 9.68–9.82 | Shatter | - | `go` breaks into shards. |
| 9.82–10.70 | Halftone assets | S3, S1, S6 cutouts | 3 large soft halftone assets drifting. Giant 3D `push` and `faster` rise. Slow camera roll. |
| 10.70–10.90 | Serif punch | - | `now` punches in (1.8→1.0). |
| 10.90–11.13 | Jagged bloom | - | Irregular white-pink bloom fills the frame. |
| 11.13–12.80 | Hero back | `c7` + matte | Match-cut from bloom into the neck backlight. Zoom-out 1.35→1.0, bright red gradient. `forever` letters vanish one by one with flicker; the middle letter stays. Then `heart`/`strong` labels with growing bars. |
| 12.80–14.52 | Exit + type | `c7` | Red blotch-textured `legacy` word behind the subject. Subject exits left on an ease-in (12.85→14.1) with a motion trail. Parallax: `always` ×1.8, `top` from 13.3, blurred `first`, typing `tag------`. 13.6: white blur flash → `we` blur→sharp → `believe` letters pop every ≤0.07 s with baseline bounce. Whole-word zoom 14.1–14.3. |
| 14.52–14.60 | White wipe | - | Hard white panel from the left. |
| 14.60–17.433 | Outro | `c8` brightened + matte | Subject centered on a red gradient, slow zoom-out. `end_words` change every 0.3 s on the chest. Fade to ~18% from 15.6. |
````

### Text slots

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/lights-out.md` lines 197-228

````
## Text slots

`config.json → words`. Words are auto-uppercased and auto-fit to frame width. Keep the recommended lengths so the composition stays like the original. Words must be short, punchy, original (imperative verbs, identity nouns), never lyrics.

| Key | Default | Role | Length |
|---|---|---|---|
| `lights` | LIGHTS | Serif hero word over subject | 4–8 |
| `out` | OUT | Giant wide serif behind object | 2–4 |
| `fear` | FEARLESS | Full-height red serif | 5–9 |
| `full` | FULL | Poster red word 1 | 2–5 |
| `thr` | THROTTLE | Poster white-on-plate | 5–9 |
| `no` | NO | Poster giant red | 2–3 |
| `brakes` | BRAKES | Poster photo-filled | 4–7 |
| `limits` | LIMITS | Poster black | 4–7 |
| `racer` | RACER | Grotesk behind front hero | 4–7 |
| `win` / `fast` | WIN / FAST | Flying side words | 2–5 |
| `born` | BORN TO WIN | Small chest label | ≤14 |
| `rise` | RISE | Red-on-white slam plate | 3–6 |
| `legend` | LEGEND | Outline serif during zoom-blur | 4–8 |
| `go` | GO | Giant 3D, intentionally cropped | 2–3 |
| `push` / `faster` | PUSH / FASTER | Giant 3D, intentionally cropped | 3–6 |
| `now` | NOW | Serif punch | 2–4 |
| `forever` | FOREVER | Letter-by-letter vanish | 5–9 |
| `heart` / `strong` | HEART / STRONG | Small side labels | 4–7 |
| `legacy` | LEGACY | Blotch-textured background word | 4–8 |
| `always` / `top` / `first` | ALWAYS / TOP / FIRST | Parallax layers | 3–7 |
| `tag` | P1 | Typing prefix | 1–3 |
| `we` | WE | Blur→sharp lead-in | 2–4 |
| `believe` | BELIEVE | Final letter-pop word | 5–9 |
| `end_words` | 10 words | Outro sequence, 0.3 s each | 1–6 each |

Fonts in the kit cover Latin only (Anton, Playfair Display, Montserrat). If the user wants words in another script (Cyrillic, CJK, Arabic…), say so and propose Latin words; do not render missing-glyph boxes.
````

### Lighting rule and slot prompt templates

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/lights-out.md` lines 242-255

````
**Lighting rule for all slots:** always generate in **red/black** lighting, whatever the final accent. The template keeps only the red channel as color and recolors the whole frame at the end via `accent_hue_shift`.

| Slot | File(s) | Used for | Still prompt template | Video motion prompt |
|---|---|---|---|---|
| S1 Countdown | `st/1.png` → `clips/c1.mp4` | Opening (lamps light one by one, then all off around clip-second 4.2); halftone asset; live panel | `Cinematic 3D render of {COUNTDOWN_OBJECT}, mounted slightly tilted 10 degrees, floating in a pitch-black void with a deep maroon radial glow behind it, heavy vignette, all elements unlit dark grey glass, low-key moody lighting, subtle film grain, no logos, no text, no letters` | `Static locked-off shot with very slow push-in. {COUNTDOWN_ACTION}: the lights switch on one by one from left to right in saturated red with soft bloom, about every 0.6 seconds, until all are lit; then all switch off at once. Pitch-black void, maroon glow behind, no camera shake, no text.` |
| S2 Hero helmet | `st/2.png` → `clips/c2.mp4` | Hero 1 (3.6–4.8); live panel | `{HERO} in {HERO_GEAR}, three-quarter view, upper body, completely desaturated black-and-white except a single red specular glint on {HERO_ACCENT}, deep maroon backlight haze behind, crushed blacks, high contrast editorial sports poster lighting, film grain, no logos, no sponsor text, no letters` | `{HERO} slowly turns head toward camera, subtle breathing, red light glint sliding across {HERO_ACCENT}, slow cinematic drift of camera to the right, dark red haze moving in background, black and white mood, no text.` |
| S3 Hero object | `st/3.png` → `clips/c3.mp4` | Object slide (4.77–5.4); halftone asset; panel; streak texture | `Top-down overhead shot of {HERO_OBJECT}, perfectly centered horizontally, front pointing right, monochrome silver-grey with deep black shadows, on a matte black background fading to dark red at the top edge, clean silhouette, cinematic, no logos, no sponsor text, no numbers` | `Top-down overhead camera tracking {HERO_OBJECT} as it moves forward fast to the right, slight motion blur, black ground, camera locked overhead, no text.` |
| S4 Print photo | `st/4.png` (still only) | Poster sheet bands; `brakes` photo fill; panel | `Graphic magazine spread printed on textured off-white paper with halftone grain, a black-and-white aerial photo of {CROWD_SCENE}, cropped into bold diagonal stripes, thick red and black graphic bars, generous blank areas, printed sports poster aesthetic, dramatic side lighting, no text, no letters, no logos` | - |
| S5 Hero front | `st/5.png` → `clips/c5.mp4` | Hero front (7.43–9.42), scaled to 0.78 | `{HERO} standing front-facing with arms crossed, {HERO_GEAR}, centered, full upper body with generous headroom, desaturated dark outfit, hard red rim light from both sides, pure black background with a soft red glow behind the head, empty negative space left and right, no logos, no sponsor text, no letters` | `{HERO} stands still with arms crossed, slight head tilt down then up toward camera, red rim light pulsing slowly, very slow push-in, black background, no text.` |
| S6 Tech parts | `st/6.png` (still only) | Halftone asset (luma-keyed); panel | `Inverted x-ray style negative photograph of {TECH_PARTS}, negative grayscale with glowing white edges on dark grey, several parts floating at different angles, technical and aggressive, red light leak from the left side, no text, no logos` | - |
| S7 Hero back | `st/7.png` → `clips/c7.mp4` | Hero back + exit (11.13–14.5) | `{HERO} seen from behind, shoulders and back of the head, plain {HERO_TOP} desaturated grey, intense white backlight hitting the back of the neck creating strong bloom and slight chromatic fringing, deep red ambient haze, black lower third, moody cinematic, no logos, no text` | `{HERO} seen from behind stands still, shoulders rise with a deep breath, intense white backlight flickers slightly with bloom, red haze drifting, very slow push-in toward the back of the neck, no text.` |
| S8 Hero close-up | `st/8.png` → `clips/c8.mp4` | Outro (14.6–17.43) | `Close-up of {HERO} with head bowed, face partly hidden in shadow, hands clasped together near the chin, desaturated, strong dark red rim light from top-left and a soft red fill, about 60 percent of the frame in shadow (subject clearly readable), quiet introspective mood, fine film grain, no logos, no text` | `Head bowed, hands clasped near the chin, almost static, slow breathing, the red rim light slowly dims, very slow push-in, quiet introspective mood, no text.` |

`{HERO_TOP}` is the garment on the back/shoulders (motorsport: `race suit collar`).
````

### Theme adaptation

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/lights-out.md` lines 257-271

````
## Theme adaptation

Fill the placeholders per theme. Keep framing, lighting and camera language identical to the default.

| Theme (`slot_values.theme`) | {COUNTDOWN_OBJECT} / {COUNTDOWN_ACTION} | {HERO} + {HERO_GEAR} / {HERO_ACCENT} | {HERO_OBJECT} | {CROWD_SCENE} | {TECH_PARTS} |
|---|---|---|---|---|---|
| `motorsport` (default) | motorsport start-light gantry, five round lamps in a row / five lamps light up | anonymous racing driver, full-face helmet and dark race suit / dark visor | modern open-wheel formula race car | a motor race starting grid with cars lined up | race car suspension arms and wheel assemblies |
| `boxing` | arena countdown clock with five round red indicator lights / five indicators light up | anonymous boxer, hooded robe and taped hands / red glove highlight | pair of boxing gloves on a canvas floor | packed arena around a ring from above | hand wraps, mouthguard, gloves and headgear |
| `football` | stadium countdown board with five round lights / five lights light up | anonymous player in a dark kit, face in shadow / red rim on shoulder | football on a pitch with chalk lines | stadium crowd and pitch from above | boots, studs, shin guards, ball panels |
| `basketball` | shot-clock with five round lights / five lights light up | anonymous player in a dark jersey / red rim on arm | basketball on a court from above | arena crowd around the court | sneakers, ball, hoop and net hardware |
| `street` | five-light vintage stage light bar / five stage lights light up | anonymous model in an oversized dark jacket and sunglasses / red glint on lenses | sneaker or designer bag shot top-down | crowd at a night street event from above | watch movement, zippers, buckles, chains |
| `gaming` | five-segment LED countdown bar / five segments light up | anonymous player in headset and dark hoodie / red LED glint on headset | game controller top-down | esports arena crowd from above | keyboard switches, controller internals, circuit boards |
| `custom` | derive from the brief in the same style | always anonymous | one iconic object, top-down | crowd/venue from above | 4–6 technical parts of the world |

Every theme still keeps five lamps/segments in S1 - the opening depends on it.
````

### Review checklist

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/lights-out.md` lines 355-369

````
## Review

Look at real frames, not assumptions:

- 3.633: the word is stretched on the first frame; the subject assembles from shards.
- 4.73: the leak is smoky, not a round white blob; faint letters remain.
- 5.30: the noise transition is only partly through (slow start).
- 6.0–6.8: poster words are large, readable, not colliding; the `thr` plate is readable.
- 7.5–8.9: the front hero is fully in frame, no head crop; panels sit in the corners.
- 9.5 / 10.2: giant 3D words are cropped on purpose, no artifacts.
- 11.0→11.13: the bloom flows into the neck backlight.
- 13.0–14.1: the subject exits smoothly, no jump; layers move at different speeds.
- 14.40: `believe` letters sit on one baseline and don't overlap `we`.
- 15.0: the outro subject is clearly visible.
- Accent: after `accent_hue_shift` the color looks intentional; skin and white text are not tinted wrong.
````

## 6. Verbatim: Last Katana

Format: reference remake with a numeric build (19.8 s anime impact edit). The densest numeric description in the library: easing formulas, offsets in px, blur sizes, punches, glints, flashes and the no-edge rule.

### Timeline and impact frames

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/last-katana.md` lines 261-284

````
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

````

### Sections

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/last-katana.md` lines 285-376

````
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
  two soft gaussian columns (σ 90 and 160 px) sweeping left → right over 0.4 s, ≤ 55 % - never
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
and falling: A - #4 6.45–6.95 (+700 → +300 px, scale 1.2, 50 %), panel 3 as a toned layer
6.95–7.45 (+650 → +200 px, 50 %); B - #4 13.5–14.05 (+700 → +250 px, 50 %), panel 1 toned
14.2–14.75 (−600 → −150 px, 45 %). Before blending, push the overlay's paper to pure white
(levels `(x − 0.12)/0.7`) and feather its edges (smoothstep over 18 % of each side), so only
ink and shadows show - never a rectangle. Flares A 7.24 at (0.55, 0.42) · B 14.12 at
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
````

### Global look

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/last-katana.md` lines 378-388

````
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
````

### No layer edge in frame (hard rule)

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/last-katana.md` lines 390-397

````
### 5.4 No layer edge in frame (hard rule)

Every shifted, scaled or rotated layer (plates, clips, cutouts, overlays, the collage frame)
is scaled up just enough that its edge never enters the frame: scale ≥ 1 + 2·|dx|/W + 2·|dy|/H
(+ 0.04 per degree of rotation). Rotate on an oversized canvas (+12 % each side) and crop the
centre; never rotate an already frame-sized image (black corners). Cutouts whose body touches
the source edge (#1 bottom/right, #6 bottom) must keep that edge outside the frame. Overlays:
paper → white and feathered (above). Light effects are soft gaussians, never hard bars.
````

## 7. Verbatim: Physical Body

Format: slot-based overlay edit, 11.8 s. A frame-accurate map of looks, flashes, tracking overlays, cascades and a nested-panel tunnel.

### Product definition and timeline map

Source: `<PLAYGROUND>/higgsfield-prompts/raw/katana/physical-body.md` lines 51-135

````
## 1. The product: what the edit is

One template, one input. Everything except the footage is fixed:

- **Music:** the template track (Kaivon - "I Am Not My Body" in the reference arrangement, about −14 LUFS) with three
- **Lyric captions** (white, lower-case sans, 52 px, frame centre, soft dark halo): `I` 59–66, `am` 67–76, `more`
  77–95, `than` 96–101, `my` 102 and 105–109, `physical` 110–126, `body` 127–133.
- **Looks:** B&W (soft / normal / hard, faint cool shadows), teal, warm, violet, natural colour; auto exposure per
  shot; light sharpening; every frame ends with a 0.16 vignette and fine mid-tone grain.
- **Effects:** white and black flash frames; a white **subject-silhouette** flash; a violet **star frame** (the
  brightest light source zoomed ×3 with a star field, screen-blended into the next shot); camera-flash **bursts**;
  **tracking overlays** (thin white dots, "x: 645   y: 1027" coordinate labels, bezier arcs, big rotating circles);
  hard-edged **2.4:1 panel cascades** (3 panels landing 3–5 frames apart, later a mirrored cascade); a **split
  screen** (full body left, face right); a **grow-to-full** panel (64 % → 78 % → 82 % → full frame on the third hit);
  single-panel **pops**; pixel noise + RGB-split **glitch**; **zoom blur** across a cut; **motion blur**; **echo
  trails**; a **light leak**; a **jagged zig-zag wipe**; sparkles; and the **nested-panel tunnel** finale (centred
  panels 92 → 82 → 72 → 63 → 55 → 47 → 40 %, each a new moment, stars on top, fading to 15 %).

**Timeline map** (output frames, 0-based, 30 fps). The clip fills 38 footage slots; slot names are in `code`:

| frames | picture (slot) | look / effect |
|---|---|---|
| 0 / 1–3 | black / white | |
| 4 | subject silhouette (`open`) | white matte on black |
| 5 | star frame (`orb`) | violet + stars |
| 6–9 | opening shot (`open`), frame 6 screen-blended with the star frame | teal |
| 10–16 | `run1` (fast motion) | B&W hard, flash burst |
| 17–21 | `wide1` + tracking label | B&W |
| 22–43 | `fairy` (person + action) + cascade `casA` 28, `casB` 31, `casC` 36 + sparkles | teal / warm |
| 44–50 | `worm` (action); 47 pixel noise; 48–50 glitch | warm |
| 51–53 / 54–58 | white / black | |
| 59–102 | `hero` (long dramatic shot with light); captions; 100–102 highlights only | B&W |
| 103–104 | white (lead-in to hit 1) | |
| 105–136 | `eye` ECU + tracking arcs; split left `body` from 127 | colour / teal |
| 137–144 | split `body` + `facer`; zoom blur 143–144 | teal |
| 145–160 | `push` (push-in) + tracking (hit 2) | teal |
| 161–164 | `glint` highlights + bloom | warm |
| 165–178 | `whip` (motion-blurred) + mirrored cascade `mcA` 169, `mcB` 172, `mcC` 175 | violet / teal |
| 179–181 / 182–184 | `strike` + burst / white | warm |
| 185–190 | `hands` | warm |
| 191–201 | `pose` (full figure) + tracking | B&W |
| 202–223 | `touch` + sparkles + tracking; pop `pop1` 212; `profile` grows 64 % (217) → 78 % (222) → 82 % (223) | teal |
| 224–244 | `profile` full frame (hit 3); pop `pop2` 232 | teal |
| 245 | white | |
| 246–282 | `run2`: motion blur, echo trails from 252, tracking circles; pops `r1` 260, `r2` 268, `r3` 273; light leak 278–280 | B&W |
| 283–292 | `dark` (low-angle face) + label | B&W hard |
| 293–295 | jagged wipe `dark` → `hand` | |
| 296–304 | `hand` (played at 0.7) + label | B&W |
| 305–353 | tunnel: `hand` shrinks to 92 %, then `fin1` 82 % (309), `fin2` 72 % (318), `fin3` 63 % (323), `fin4` 55 % (325), `fin5` 47 % (331), `fin6` 40 % (338); stars; tracking on the newest panel; fade from 338 | teal |

All 38 slot names (also the item names for `fixes.json`): `open orb run1 wide1 fairy casA casB casC worm hero eye
body facer push glint whip mcA mcB mcC strike hands pose touch pop1 profile pop2 run2 r1 r2 r3 dark hand fin1 fin2
fin3 fin4 fin5 fin6`.

**Parts of the edit by name** (for requests like "make the intro brighter"):
- intro (0–58, ~0–2 s): `open orb run1 wide1 fairy casA casB casC worm`;
- hero shot (59–104, the captions): `hero`;
- middle (105–244): `eye body facer push glint whip mcA mcB mcC strike hands pose touch pop1 profile pop2`;
- ending (245–353): `run2 r1 r2 r3 dark hand fin1 fin2 fin3 fin4 fin5 fin6`.

**Tunnel panels** stack inside each other, so each is fully visible only until the next one lands - `fin1` 9 frames,
`fin2` 5, `fin3` 2, `fin4` 6, `fin5` 7, `fin6` 16 - and then only its rim shows. For these slots the first frames of
the window are what the viewer sees.

**How moments are picked** (deterministic scorer, so you can judge the review sheets): each slot has a kind -
`eyes` (`eye`: ECU, eye distance 45 % of the width), `face` (`casB casC facer dark fin3 fin4`: face 50 % of the
height), `profile` (`profile fin6`: turned head), `medium` (`fairy push touch fin2`), `figure` (`open body pose pop2
r1 fin5`: whole body / back view), `hero` (`hero fin1`), `detail` (`casA hands hand`: hands / torso below a face),
`glow` (`orb`: the brightest small light), `glint` (`glint`), `action` / `run` / `whip` (motion), `wide` (`wide1 mcA
pop1`: the space). Windows avoid black / title-card frames and white flashes, avoid crossing source cuts and keep 0.5 s
apart while the clip allows. There are two kinds of slot: **full-frame** slots, and **panels** in groups - `cas1` =
`casA casB casC`, `cas2` = `mcA mcB mcC`, `pops` = `pop1 pop2`, `runpops` = `r1 r2 r3`, `finale` = `fin1`–`fin6`.
Full-frame slots never share a moment with each other; panels never share one within their group, but may reuse
full-frame moments. Faces come from a YuNet detector, which has **no identity** (it does not know who the main
character is) and can see faces in textures (roses, foliage, patterns). Zoom is capped so a source pixel is enlarged
at most 3.2× (1080p sources: zoom 3.2; 4K: twice that); the summary says "capped" when a close-up wanted more, and
adds "(tiny or false face: check the tile)" when it wanted more than twice the cap. Clips under ~10 s visibly reuse
moments ("reuses footage"). The frame-4 silhouette is keyed from the colours of the person box (grown from the face
in the `open` window) against the frame border; with no face it keys the brightest part of the frame.

---

````

## 8. Where to find more recipes in the raw files

All paths are under `<PLAYGROUND>/higgsfield-prompts/raw/katana/`.

| File | Section | What it gives you |
|---|---|---|
| `kawaii-pop.md` | 9. Assembly (lines 368-460) | cut list in frames, phrase template table, eye-line framing numbers, palette hex values, word sizes in eye-distance units, blow-out/magenta/blur/slash transition numbers, B&W bridge with letterbox bars |
| `pink-collage.md` | 1. The product, 2. Beat map (lines 46-105) | beat-by-beat time table at 136.15 BPM, text-slot rules, lettering styles |
| `lights-out.md` | Cost and approval, Appendix | text defaults and the config structure |
| `living-lab.md` | 7. The template, element by element (lines 265-316), 8. Slots | dot-matrix, thermal and grid effects, 28 clip slots |
| `launch-cut.md` and `.part-2.md` | Part B production method | 30 s product-ad structure: scenes, UI clone, triggers, final moment, lockup |
| `travel-edit.md` | Product, FX frames | 180-slot mood edit with flash cuts and echo trails |
| `let-me-show-you.md` and `.part-2.md` | 5-6 | matte-swap transitions and the house look (raised exposure and contrast, clean grain, flash-light transitions, amber film burns) |
| `the-boys.md` | Product | frozen 32.5 s timeline concept: word-by-word captions, title behind the head, speed ramps; the pipeline is platform-specific |
