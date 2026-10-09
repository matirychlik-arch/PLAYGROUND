# Master-prompt template: write your own "preset" for a style

Contents
1. What a preset is and why it works
2. Template A: reference-driven preset (fill-in)
3. Template B: slot-based preset (timeline + text slots + asset slots)
4. Annotated excerpt from a real preset (Grunge Aura)
5. Rules that make a preset reproducible
6. Checklist before you save a preset

A preset is a style frozen into one document so that any editor (you in Premiere/After Effects, a teammate, or an AI editor) can reproduce the look with a new subject. The 28 Katana presets show two build patterns. Template A is the author master prompt (reference + numerical recipe + embedded edit map). Template B is the slot-based preset: a fixed timeline whose slots are refilled with new footage, words and accent colour.

Why it works: the preset separates what never changes (timing, light/dark progression, title choreography, texture behaviour, transitions, audio, export settings) from what changes per project (subject, title, crops, focal points, accent). Every number is explicit, so two people get the same result.

## 1. Section order of an author master prompt

The proven order (headers in capitals in the real presets):

1. EXECUTION CONTRACT (who does the work; never stop at a treatment, storyboard or code listing; deliver a playable file; do not claim a render happened if it did not)
2. INPUT CONTRACT (the one required variable input, what it controls, what to do with extra material, default title)
3. FIXED REFERENCE (the reference video, its creator, what the reference controls versus what the subject controls)
4. PRESET LOCK (resolution, aspect, frame count, fps as a rational, duration, convention for ranges, what must not change)
5. VISUAL LANGUAGE (look in nouns and verbs; how brightness, scale and density should follow the reference; typography style)
6. SUBJECT ADAPTATION (identity anchors, shot-function translation table per subject type, source bank, immutable preset vs variable subject data, a restrained movement for stills)
7. NUMERICAL COMPOSITING RECIPE (starting numbers: crop, exposure matching, softening, vignette, grain, halftone, accents, blur, strips, dust, localisation rules)
8. TITLE CHOREOGRAPHY (envelope in pixels, frame-by-frame title life, fonts by class, subject-neutral microcopy)
9. EMBEDDED EDIT MAP (frame ranges with one-line purpose each, then the exact event boundaries as a list, plus the short events inside broader ranges)
10. AUDIO (use the original waveform; do not replace the track; handle codec delay)
11. EXECUTION (ordered steps: inspect, prepare, timeline, low-res preview, fix, final render, verify, deliver)
12. DELIVERY (file name, preview, optional comparison sheet, disclose deviations)

## 2. Template A: reference-driven preset (copy, fill, keep the headers)

```
PRESET: <name>   (<one line: what it looks and feels like>)

EXECUTION CONTRACT
You are the editor and compositor. Produce a finished, playable video from the input using the fixed preset below. Do the inspection, preparation, compositing, render, QA and delivery yourself. Do not stop at a treatment, storyboard or prompt for another tool. Use the tools you actually have (<NLE / script / editor>); never claim a render or export that did not happen.

INPUT CONTRACT
Required: <SUBJECT_IMAGE | SUBJECT_CLIP | PRODUCT_SHOTS>. It defines the subject, appearance, design and medium. Pack images/clips shipped with the preset are reference material, not the subject.
Optional: <TITLE> (default: "<SUBJECT> / 01"), extra images of the same subject (support the subject, never change the preset).
A new image changes the subject, not the preset. Change music, aspect ratio, duration or style only when explicitly requested. If several subjects appear and none is specified, use the visually dominant one consistently.

FIXED REFERENCE
<link or file>, creator <name>. The reference controls: editing, timing, framing, light/dark rhythm, texture, typography, transitions and sound. The subject controls identity only. Replace the reference's principal human/object shots with the subject while keeping each shot's function. If the reference is inaccessible, ask for the file; never invent its contents.

PRESET LOCK
Final output: <W>x<H>, <aspect>, <N> frames at <num>/<den> fps (~<fps>), ~<seconds> s. Frame indices are the timing authority; ranges are start-inclusive, end-exclusive; frame <N-1> is last. Do not round the fps. Preserve: soundtrack, event order, short flashes, title positions, closing cards. Do not: change the duration, invent a new drop, swap the track.

VISUAL LANGUAGE
<2-3 sentences of nouns: grade, texture, contrast, grain, graphic elements>
<one sentence: how brightness, scale and density follow the reference moment by moment>
<one sentence: typography: font class, scale jumps, alignment, microcopy>
Readable subject shots sit between aggressive transition frames. Text is rendered in the editor, never expected from a generator.

SUBJECT ADAPTATION
Extract 3-5 identity anchors from the subject (face/silhouette, hair/outline, clothing/material, proportions, distinctive details) and keep them in every shot. Photographs stay photographic, drawings stay illustrated.
Shot-function translation:
- <subject type>: <silhouette, portrait, detail, ...>
- <product>: <overall shape, defining feature, material, edge, mark>
- <vehicle / architecture / artwork>: <...>
Missing angle? Use an available detail; never invent anatomy or product features.
Source bank: build ~6-10 compositions (wide/medium, hero close-up, extreme detail, silhouette, material, context) from the inputs. The reference's N events are not N independent scenes.
Two layers: (1) immutable preset: event timing, light/dark progression, title choreography, texture behaviour, transitions, soundtrack, export settings; (2) variable subject data: files, focal points, masks, crops, safe motion, title, labels.
Still-image motion: start crop/focal point/scale/translation per reused composition; restrained move = scale 1.00 -> 1.04 or pan within ~3% of the canvas, with overscan; vary direction by shot function; larger smears belong to designated transitions.

NUMERICAL COMPOSITING RECIPE (starting values at <W>x<H>; adjust only if readability fails)
- Crop: <rule, focal point>
- Exposure matching: <formula>
- Softening: <sigma>; vignette <strength>; grain <sigma, softening, seed rule>
- Texture: <halftone cell, strength curve, frames>
- Accents: <formula>; motion blur kernel <px>; block transition sizes <list>
- Strips/streaks: <height, offsets>
- Dust/scratches: <time-varying>; strong effects localized to the edit map.
- Reuse of reference textures: verify no faces, hands, signatures or captions in them.
- Old end-card text: remove by local reconstruction, not by black boxes.

TITLE CHOREOGRAPHY
Envelope: x=<..>..<..>, y=<..>..<..> at <W>x<H>; fragment anchors <list>.
Frames <a>-<b>: <what>. Frames <c>-<d>: <what>. ... Final fade <frames>.
Fonts by class: bold grotesk, monospace/typewriter, optional handwriting. Choose installed substitutes by shape and test glyphs. All words, initials, dates and microcopy are subject-neutral or supplied.

EMBEDDED EDIT MAP
<f0>-<f1>: <purpose>
...
Exact event boundaries: [<list>]
Short events inside broader ranges: <frame: event>, ...
If frame inspection disagrees with this map, follow the actual reference with integer-frame timing.

AUDIO
Use the original audio; preserve start, tempo, pitch and accents; account for codec delay; copy the stream when compatible. Do not replace the track, add another bed, add voice-over or insert arbitrary whooshes. A missing original is a missing asset, not permission to improvise.

EXECUTION
1 Inspect input, reference, tools. 2 Prepare the source bank and reusable textures. 3 Build the timeline (start/end frame, source, crop, scale, position, motion, typography, effect parameters per event; seeded randomness; clamp displacement). 4 Render one low-res preview; inspect flashes separately. 5 Fix concrete defects; final render (H.264, yuv420p, CRF 15-18 for dense grain); count frames. 6 Open the export: identity, duration, size, frame count, sound, readability, no stray signatures; check every frame of titles, short inserts and boundaries. 7 Deliver.

DELIVERY
<file name>.mp4 with preview; optional comparison sheet; disclose material deviations.
```

## 3. Template B: slot-based preset

Use when the style is a fixed timeline that you refill each time. Real examples: a 17 s kinetic-typography edit (8 stills, 6 animated clips) and a 15 s strobe edit cut to a fixed 160 BPM track (48 shots refilled from one clip).

```
PRESET: <name>   <duration> s, <W>x<H>, <fps> fps, <frames> frames

PRODUCT
What the user gives: <inputs>. What is fixed: structure, timing, transitions, typography motion, grade, music. What varies per user: <subject and props, words on screen, accent colour, audio>.

AUDIO
Hit points (seconds): <list>. Alignment rule: main drop at <t> s; offset = drop_in_track - <t>; negative offset -> pad the start.

TEMPLATE TIMELINE (locked)
| time (s) / frames | section | footage slot | what happens (effects, transitions, text) |

TEXT SLOTS
| key | default | role | length limit |
Words are short, punchy, original (imperative verbs, identity nouns), never lyrics. Fonts cover Latin only: warn about other scripts.

ASSET SLOTS
| slot | used for | still prompt template | motion prompt |
Lighting rule for every slot (e.g. always red/black, recolored globally at the end by one hue shift).

THEME ADAPTATION
| theme | placeholder A | placeholder B | ... |
Every theme keeps the structural element the opening depends on.

REVIEW CHECKLIST (look at real frames)
- <time>: <what must be true>

FIXES
| problem | fix | cost |

NEVER
1 Never change the template. 2 Approved parts stay frozen. 3 No real people or logos unless supplied and consented. 4 No lyrics on screen unless supplied. 5 Never claim a visual check you did not do.
```

Slot-type vocabulary from the real presets (use it to name your slots): eyes (extreme close-up), face (face about 58% of frame height), hero (best frontal close-up, held, about 66%), profile (face present, not frontal), medium (face about 20%, person in the space), walk (long moving shot), back (turned away / leaving, late in the clip), bright (light footage that sits inside letters), wide (whole frame action), detail (hands, clothes, objects below the face), glow (brightest small light), glint, action / run / whip (motion), figure (whole body or back view). Rules: a moment never crosses a source cut unless nothing else fits; moments sit at least 1 s apart when the clip allows; timeline neighbours avoid the same source shot; panels in collages may reuse moments (they are recaps); zoom capped so a source pixel is enlarged at most about 3x.

## 4. Annotated excerpt from a real preset (Grunge Aura, abridged)

Source: <PLAYGROUND>/higgsfield-prompts/raw/katana/grunge-aura.md (author master prompt, lines 40-221). Annotations in brackets are mine.

[1 INPUT CONTRACT: one required input, what it controls, what extras do, default title]
```
INPUT CONTRACT
The default and only required variable input is USER_IMAGE: the image attached by the user. It defines the subject, appearance, design, and visual medium. Images inside the preset package are reference materials, not USER_IMAGE.

The subject can be a person, fictional character, animal, vehicle, product, sculpture, building, or another clearly visible object. Adapt the shot content to that subject without changing the preset's editing language. Do not carry over Maki, Jujutsu Kaisen, names, footage, or assumptions from another task.

If the user supplies additional images or footage, use them as supporting material for the same subject. A new image changes the subject, not the preset. Change music, aspect ratio, duration, or style only when explicitly requested. If several subjects appear and none is specified, use the visually dominant subject consistently. Use a supplied title; otherwise use SUBJECT / 01.

```

[2 PRESET LOCK: rational fps, exclusive ranges, what must not change. Note the instruction to use integer frame indices as the authority.]

```
PRESET LOCK
Final output: 1620x1080, landscape 3:2, 474 frames at 24000/1001 fps (approximately 23.976), approximately 19.770 seconds. This is the completed adaptation's export cadence. Use integer frame indices as the timing authority; the source container may report the rounded rational 2997/125. Do not round the render to 24 fps or accumulate rounded timecodes. Ranges below are start-inclusive and end-exclusive; frame 473 is the last frame.

Preserve the reference soundtrack, event order, short flashes, title positions, and closing black cards. Do not turn this into a vertical phonk edit, change the duration, invent a new drop, or replace the original track with a convenient alternative.
```

[3 VISUAL LANGUAGE: nouns for the look, then a rule that couples brightness/scale/density to the reference, then typography class.]

```
VISUAL LANGUAGE
Nearly monochrome editorial grunge: dense blacks, dirty paper whites, silver midtones, film grain, photocopy degradation, halftone screens, scratches, dust, folded paper, scanner streaks, brief negatives, hard cuts, and graphic collage.

Match the reference's changes in brightness, scale, and visual density at corresponding moments. Use quiet readable subject shots between aggressive transition frames. Texture must feel integrated into the image rather than like one static noise layer over the entire film. Preserve the face, silhouette, or product shape in the readable shots.

Typography uses bold sans-serif letter fragments, abrupt scale changes, broken alignment, tiny technical annotations, registration marks, and small frames. Render readable text in the compositor rather than relying on generated lettering. Use the supplied title or SUBJECT / 01; use IMAGE STUDY, FRAME 001, and END OF STUDY for secondary labels. Replace the reference's pack advertisements and creator signatures with neutral subject-specific text. Do not attribute the new edit to the reference creator.
```

[4 NUMERICAL COMPOSITING RECIPE: every bullet is a number you can type into a keyframe or an effect. Note "starting settings, adjust only when readability fails".]

```
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
```

[5 TITLE CHOREOGRAPHY: an envelope in pixels, then frame ranges with what the type does in each.]

```
TITLE CHOREOGRAPHY
Fit the current title into the reference's spatial envelope using measured text bounds. Do not simply replace MAKI with a longer word at fixed coordinates. Adjust line breaks, size, and tracking without distorting letterforms.

At 1620x1080, use the compact title area around x=528..1100 and y=462..620 as a starting envelope. The upper fragment begins near (528,462), the lower fragment near (598,540), and the supporting line near y=584. Derive positions for the current words from their actual widths.

Frames 21–22: oversized broken title fragments, around 270 px nominal size. Frames 23–27: partial fragments, ghosted letters, marginal microtype, and a small graphic waveform. Frames 28–31: remaining fragments and subtitle progressively appear. Frames 32–34: the title resolves into readable text. Frame 35: photocopy/grunge hit. Frames 50–64: compact light-on-dark title composition. Frame 65: short dark glitch.
```

[6 EMBEDDED EDIT MAP (first 12 lines of 41): frame range plus one-line purpose, using light/dark and scale words.]

```
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
...
```

[7 Exact boundaries as a flat list, then the warning not to treat every boundary as a new scene.]

```
Exact event boundaries:
[0,15,17,19,21,23,35,37,46,48,50,66,69,71,83,96,112,114,120,122,128,130,138,140,145,160,162,164,177,179,182,187,190,192,199,207,209,213,216,221,224,226,228,236,238,240,255,259,261,273,279,281,283,302,304,307,309,318,320,322,341,350,356,367,369,379,381,424,426,474]

These include brief visual events within shots. Do not interpret every boundary as a new scene. If direct frame inspection establishes a discrepancy, follow the actual original and retain integer-frame timing.

The accompanying historical renderer uses inclusive end frames, whereas this prompt uses end-exclusive ranges. Convert explicitly when adapting it. Assert that every frame 0..473 belongs to exactly one output segment, with no gaps, overlaps, or duplicate seam frames. Verify cached source keys and the frame shape/dtype before launching a long render.
```

## 5. Rules that make a preset reproducible

- Give every duration in frames and every rate as a rational. State range convention (inclusive or exclusive) once and assert that every frame belongs to exactly one segment, with no gap, overlap or duplicate seam frame.
- Separate immutable timing from variable subject data in two layers.
- Express looks as measurements (levels, sigma, cell size, opacity, frames), not adjectives alone.
- Say which effects are localized to which frames. Intense distortions only at their assigned events.
- State the verification step for short events: sparse contact sheets miss one-frame flashes.
- Say what is forbidden: swapping the track, adding whooshes, hiding old text with black boxes, carrying over names or lore from another subject, attributing the new edit to the reference's creator.
- Put the edit map and the recipe in one document; a link to a reel is not a specification.
- For words: provide a default title and subject-neutral secondary labels (e.g. IMAGE STUDY, FRAME 001, END OF STUDY).
- Versioned kit/template presets: write "never change the template; customization only through the listed slots".

## 6. Checklist before you save a preset

- Could someone with only this page reproduce the first 3 seconds frame for frame?
- Are all numbers in the recipe tied to a resolution and a frame rate?
- Is there a table for text (id, frames, position, size, animation) or a title choreography per frame range?
- Is every audio hit listed with its time and frame?
- Is the subject-adaptation table complete for person, product, vehicle, architecture and flat artwork?
- Is there a QA list with at least: frame count, duration, dimensions, audio sync, text readability, no stray reference people/signatures?
