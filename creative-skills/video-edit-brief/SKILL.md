---
name: video-edit-brief
description: "Turns a reference edit (reel, TikTok, ad) or a brief plus footage into an executable edit brief: edit map (cut kinds, cadence, motion, look, flashes, inverts, text), numerical compositing recipe (scale %, keyframes, strobe periods, overlay opacity, invert frames), title choreography, audio hit alignment and QA. Modes: edit the user's footage per brief, remix a reference's style onto a new subject (default), or rebuild it 1:1. Maps to Premiere Pro / After Effects keyframes or any AI editor; 28 style presets and 20 edit maps. Use for any request to copy, analyse, rebuild or QA a video edit. Trigger on: brief montażowy, rozpiska montażu, zrób edit jak ten, odtwórz ten reel, mapa cięć, shot list z referencji, edit na bit, strobe, keyframe'y w Premierze, animacja tytułów, sprawdź ten montaż, styl jak z TikToka. New generated clip: cinematic-prompt-builder / viral-effects-library. Existing clip changed by a video model: video-edit-prompting. Captions only: caption-and-title-systems."
---

# Video Edit Brief

Make an edit reproducible: reference (or brief) -> edit map -> numerical compositing recipe -> title choreography -> audio hits -> QA. The result is a brief an editor can type into Premiere Pro / After Effects keyframe by keyframe, or paste to an AI editor, and get the same edit twice. The method is lifted from Higgsfield's Katana workflow (reference-driven short-form edits) and stripped of its platform specifics.

Core idea: a reference is evidence, not a template. Separate what you OBSERVED (edit map) from what you AUTHOR (plan and recipe), and never describe a look in adjectives alone; give frames, percentages and pixels.

## When to use / when not

Use when:
- the user shows a reference edit and wants something "like this" with their subject, or the same edit rebuilt;
- the user has footage plus a brief and wants a cut plan with beat sync, effects and titles;
- the user wants a shot-by-shot analysis, or an edit checked against a plan;
- the user wants to write their own reusable style ("preset").

Do not use when:
- the task is one new generated clip: use `cinematic-prompt-builder`, `seedance-director` or `viral-effects-library`;
- an existing clip must be altered by a video model (swap person, product, background): `video-edit-prompting`;
- only captions or titles are needed: `caption-and-title-systems`; only voice-over: `narration-vo`;
- the idea or script does not exist yet: `concept-loop`, `viral-reel-builder`.

Pick the mode first (it changes what you may invent):
- SOURCE: the user's footage + a brief. The brief defines the result; no reference to copy. Choose cuts, pacing, crop, grade, effects and type to fit the brief. Do not generate what the footage already supplies.
- REMIX (default for any reference): keep the reference's grammar (rhythm, shot scale, motion, texture, typography, musical arc) and author new scenes, order, text and duration for the new subject. "Like this", "w stylu tego" and "zrób podobny" mean REMIX.
- EXACT: only when the user explicitly asks for a 1:1 rebuild, the same sequence, or a replacement of only the hero. Keep source order, framing, timing, text, effects and audio except the stated changes. Never claim exactness from a similarity score.
A lock on one property (same song, same title wording) locks only that property, not the whole edit. Continue a project in its saved mode until the user changes it.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

1. Mode (default REMIX) and explicit locks (song, wording, duration, format).
2. Reference: file or link. If you cannot play or decode it, say so and ask for frame sheets or a description; never claim to have watched an unseen video. If there is none and the brief is substantive, propose 1-3 reference candidates to inspect.
3. Subject and assets: photos, clips, product shots, logo, existing footage; which one is the hero. Note hidden-face, back and silhouette shots.
4. Output target. Defaults: 1080x1920 (9:16), 30 fps (24 for a cinematic feel), length of the reference or 15-20 s, SDR Rec.709, H.264.
5. Audio: the track (and its drop time), or "keep the reference audio". Without a track, plan around silence and mark where music will land.
6. Text: words, language (Polish needs diacritic-safe fonts), or "no text".
7. Tool: Premiere / After Effects (default for Mati), another NLE, or an AI editor.
Write explanations in the user's language (Polish for Mati); keep table headers, recipe keys and generator prompts in English.

## Workflow

### 0. Write the task contract (3 lines)
`mode` + reason, `locks` (what must not change), `freedoms` (what may). Everything below checks against it.

### 1. Read the reference (a human can do all of this by scrubbing)
1. Watch once at speed with sound. Write a first guess of the trick line and the sections.
2. Switch the player to frame display. Step with the arrow keys and mark the FIRST frame of every new shot. Never read a 5-10 fps skim as the cut list; automatic detectors (Premiere Scene Edit Detection, ffmpeg scdet) find well under half of the cuts on whip and strobe edits and fire on grain. Use them only as proposals.
3. Hunt the hard cases at native frame rate: cuts hidden inside flashes or burns, 1-2 frame inserts, strobe sections, invert frames, dark-to-dark cuts, whips that straddle the beat, micro-cut bursts. Drop the false cuts: grain boil, flash frames, text pops, light flicker, letters flying out.
4. For each shot note: frames, shot size, camera move (and whether the move is digital), cadence (count unique frames in a 10-frame window), look, effects, transitions in/out, text, layers.
5. Write the trick line: "The trick of this ref is <device> on <timing> so that <feeling>", then the frames where it happens. If there is none beyond fast cuts on the beat, say that.
6. Per-second log: one line per event with frames. Count stickers/doodles per second (density is what viewers judge).
7. Text inventory: for each word, in / full / out frames, size as % of frame height, centre, colour, animation, in front of or behind the subject.
8. Audio: tap the BPM and verify it: express the cut intervals in beats at the candidate BPM and at x2, x1/2, x3/4, x4/3; the right BPM puts most intervals on whole or half beats. Note the drop, the hits, any splice (energy jump off the bar grid) and the editor's SFX layer. Measure the share of cuts within +-2 frames of an onset.
9. Look crops: save 4 full-size stills (face close-up, darkest shot, brightest shot, a text frame) to compare against later.
10. Meaning: for every graphic and word, what it means relative to the beat, lyric or story, and what it becomes in the new edit.

What to ask an analysis tool (an AI that can see video, or a script) when you cannot scrub: (a) a cut list with absolute frame numbers and fps; (b) every flash, solid-colour and invert frame with frame range; (c) unique frames per shot (cadence) and any speed ramps; (d) camera move per shot, whether digital, with zoom and pan amounts; (e) mean luma, saturation, dominant hue, B/W flag per shot and globally; (f) all on-screen text with frame ranges, boxes and layering; (g) BPM, beat grid, drop, onsets and the cut-on-onset share; (h) the frame ranges with the densest change (strobes, bursts). Insist on frame numbers, not seconds, and tell it to flag uncertainty. Verify its answer on a frame sheet before trusting it.

### 2. Write the edit map
One table, fixed columns, one row per shot (a burst is one row with its sub-shots in the text cell). Use the vocabulary in `references/edit-map-grammar.md`. Frames are absolute, 0-based, `f1` inclusive; rows are contiguous and end on frame N-1. Keep observed facts (source map) separate from your authored plan (output map). In REMIX the source map is evidence: borrow its pacing (dur, cadence) and mechanisms, not its content.

### 3. Plan the output (REMIX/SOURCE)
- Output target: size, fps (rational), frame count, audio endpoint.
- Concept: one logline, a story arc or a visual motif with setup, development, payoff mapped to shot ids. A product or abstract edit needs no invented plot.
- Shot roles (hook, identity, action, accent, reveal, consequence, transition, breath, payoff, closure) and for each: scale, action, camera, duration, text role, reused or new.
- Source bank: 6-10 compositions from the assets (wide, hero close-up, extreme detail, silhouette, material, context). The reference's N events are not N separate scenes.
- Missing-role inventory from clips you have actually seen; produce only what fills a gap.
- Rules: every effect has a scene purpose (reveal, conceal, accent, transition, contrast, motif). No random glitch, shake or palette change per cut.
- SOURCE mode: first inspect the footage (resolution, fps, duration, audio, frames across the whole length), log usable moments with in/out frames, then choose cuts, pace, crop, grade, effects and type from the brief. Plan a short representative preview (5-10 s) before the full build. A supplied image can be the subject of an animated edit (still plus camera keyframes).
- EXACT mode: the plan is the source map plus a list of requested replacements; add no new story beats. If the user changes timing or format, write a source-to-output frame mapping and compare through it.

### 4. Write the compositing recipe (numbers, see `references/compositing-recipe.md`)
Per shot: camera keyframes (scale %, position, rotation, anchor, frames, ease), speed and cadence, look values, layer stack (bottom to top), effects with per-frame amounts (flash 85/45/18, strobe period, RGB split px, overlay blend and opacity, invert frames), transitions with frames, and the no-edge check (scale >= 1 + 2|dx|/W + 2|dy|/H + 0.04 per degree). Use starting numbers from the recipe file and the style library; justify any change.

### 5. Write the title choreography
Title table: id, words, frames in / full / out, position (% of frame), size (% of frame height), font class, colour/stroke/shadow, animation, layer (front/behind), beat. Plan text before generating footage; render it last as a separate layer. Check glyph coverage (ą ć ę ł ń ó ś ź ż) and phone-size readability. Do not copy the reference's wording; copy its grammar.

### 6. Align audio
Hit table: every hit with seconds and frame, the picture event it triggers (cut, flash, punch, slam, invert). Cuts on beats or 1-2 frames before them; target cut-on-onset share of 0.7 or more. Use real recordings (the reference track, the user's track, a licensed stock track) and recorded SFX placed on the hit frames; never synthesize music or whooshes. Plan the mix: duck -6/-7 dB under speech, limiter so the encoded file is at or below -1.0 dBTP.

### 7. Run the three motion reviews, then QA
Before building, on a preview, and before delivery: (1) timing and rhythm, (2) spatial motion and continuity, (3) distinctive detail and polish. Each needs its own evidence; "looks good" three times is not a review. Then run `references/qa-checklist.md` on the exported file, covering every frame.

### 8. Hand off
Deliver the brief (below). Premiere/AE operations for each recipe element are in `references/premiere-ae-mapping.md`. If something cannot be done in the target tool, say which element and give the nearest alternative.

### Pitfalls that sank past remakes

- Copying the timing but losing the trick (a remake with the cuts right and the per-beat outfit swap missing was rejected). Write the trick line first and test the remake against it.
- Treating a locked-camera photo series as video; it needs stills plus compositing.
- Skimming at 5-10 fps: a 3-5 frame overexposure burn that hid every jump cut was missed until the native-rate pass.
- Trusting the cut detector; it found 19 of 49, 9 of 35 and 28 of 54 cuts on three edits.
- Applying one house grade to every reference ("colors wrecked, too much noise"); match the reference's look or choose a documented one.
- Decorations too small or too sparse next to the reference; measure sticker/doodle scale and count per second.
- Own words over a lyric-driven edit: on-screen words that are the song's lyrics on their syllables read as fragments if replaced.
- Wrong frame count or ending (285 frames against 283; container length used instead of video frames).
- Smooth cadence where the reference steps at about 18 fps, or stepped footage where it was smooth.
- A limiter set so the encoded file peaks above 0 dBFS; measure after encoding.
- Carrying the reference's identity items (outfit, props, names, signatures) into the new edit.

## Output format

Produce one markdown brief with these fixed headings. Fill every table; use `-` for empty cells.

```
# EDIT BRIEF: <project>
## 1. Task contract
mode: SOURCE | REMIX | EXACT   reason: <...>
locks: <...>   freedoms: <...>
## 2. Trick
The trick of this ref is <device> on <timing/structure> so that <effect>.   family: F1a..F7   trick_frames: [[f0,f1,"..."]]
## 3. Output target
<W>x<H>, <fps> (rational), <N> frames = <s> s, audio <track, in/out>, delivery <codec>
## 4. Edit map (output)
| id | t0-t1 | dur | kind | cadence | motion | look | fx | text |
## 5. Global look and finish
grade, grain, vignette, bloom, softness, palette hex, font classes
## 6. Recipe per shot
R<id> f<f0>-<f1> (<t0>-<t1> s) src: <clip> @ <in-point> speed <n>% cadence <...>
  cam / look / layers (bottom to top) / fx / trans / text / audio
## 7. Title choreography
| id | words | in / full / out (frames) | position % | size % H | font class | colour / stroke | animation | layer | beat |
## 8. Audio plan and hit table
track, drop, bpm, offset;  | id | seconds | frame | sound | picture event |
## 9. Assets and source bank
| role | asset | in-point | status |   (+ per-cut generation briefs if footage must be generated)
## 10. QA and delivery
expected frame count, checks that matter for this edit, export settings
```

Cell conventions: `t0-t1` as `f0-f1 / s0-s1 s` (e.g. `f30-44 / 1.00-1.50 s`); `dur` in frames; `kind` from `start | cut | burst | strobe | whip | wipe | flash-hidden`; `cadence` `native | stepped 2,2,1 | pulldown_24in30 | freeze | speed 35%`; `motion` `push_in z=0.06 | shake e~20 | static`; `look` `B/W | L0.25 S0.10 cool | accent lime`; `fx` `flash_white 85/45/18; rgb_split 6px f30-31`; `text` title ids.

### Worked mini example (REMIX, 6 s teaser for a fictional sneaker "NOVA")

Contract: REMIX; lock = 120 BPM track, drop at 1.00 s; freedom = everything else. Target: 1080x1920, 30 fps, 180 frames (6.00 s), a beat = 15 frames. The trick: a hard flash-and-punch on every beat after the drop, with a 24-frame A/B strobe, so the product reads as impact.

```
| id  | t0-t1             | dur | kind   | cadence | motion                | look                  | fx                                              | text |
| c01 | f0-14 / 0.00-0.50 | 15  | start  | native  | push_in z=0.04        | dark, cool L0.20 S0.10| none                                            | -    |
| c02 | f15-29 / 0.50-1.00| 15  | cut    | native  | push_in z=0.08        | dark, cool            | flash_white 50/10 f15-16                        | -    |
| c03 | f30-44 / 1.00-1.50| 15  | cut    | native  | punch 106->100% 6f    | bright, warm L0.55    | flash_white 85/45/18 f30-32; rgb_split 6px f30-31; shake 16x12px f30-33 | T01 |
| c04 | f45-59 / 1.50-2.00| 15  | cut    | native  | pan 3% left           | bright, warm          | none                                            | T02  |
| c05 | f60-89 / 2.00-3.00| 30  | strobe | A native, B speed 35% | A push 100->104%, B 100->108% | B/W then colour | strobe A/B period 2f f60-83; flash 70/25 on each A; rgb_split f60-61 | - |
| c06 | f90-119 / 3.00-4.00| 30 | cut    | native  | push_in 100->110%     | bright, warm          | none                                            | -    |
| c07 | f120-149 / 4.00-5.00| 30| cut    | native  | zoom ladder 100/112/124% hold 10f | high contrast | invert f120-121 (adjustment layer) | - |
| c08 | f150-179 / 5.00-6.00| 30| cut    | native  | static                | clean                 | fade to black f170-179                          | T03  |
```
Recipe for c03 (the drop):
```
R03 f30-44 (1.00-1.50 s) src: shoe_hero.mp4 @ 00:00:02:10 speed 100% cadence native
  cam    scale 106% -> 100% over f30-36 [out3]; anchor (0.5,0.55); pos fixed (540,960)
         shake position amp 16/8/4/2 px on f30-33 (y at 75%), then 0; Hold keys
  look   contrast 1.18, saturation 0.9; vignette -30%
  layers plate; subject matte; T01 "NOVA" behind the subject (between plate and matte copy)
  fx     flash_white 85% f30, 45% f31, 18% f32 (Hold); rgb_split 6 px f30-31, 0 by f33
  trans  in: hard cut under the flash (hides_cut yes); out: hard cut
  audio  H02 @ f30
```
Recipe for c05 (strobe): A (wide) on frames 60,62,...,82; B (macro, 35% speed so it barely moves) on 61,63,...,83; B only f84-89. White flash on each A: 70% on its first frame, 25% on its second. Premiere: cut both clips into 2-frame pieces on a snap grid; AE: the strobe expression in `references/premiere-ae-mapping.md`.
```
| id  | words | in / full / out | position % | size % H | font class         | colour / stroke | animation                                  | layer                | beat |
| T01 | NOVA  | f30 / f33 / f44 | 50, 38     | 18       | condensed grotesk  | #FFFFFF, none   | slam scale 130,90,106,100 over f30-33      | behind subject (matte)| H02  |
| T02 | AIR 01| f45 / f55 / f59 | 50, 64     | 5        | mono caps          | #FFFFFF 90%     | typewriter 2 f/letter, hard out at the cut | front                | -    |
| T03 | [CTA] | f152 / f158 / f179 | 50, 52  | 6        | same as T02        | #FFFFFF         | fade in 6 f, hold, fade with the picture   | front                | H05  |

| id  | seconds | frame | sound            | picture event                       |
| H01 | 0.50    | 15    | snare            | flash 50/10 into c02                |
| H02 | 1.00    | 30    | drop (kick+sub)  | punch, flash 85/45/18, T01 slam     |
| H03 | 2.00    | 60    | riser end        | strobe starts                       |
| H04 | 4.00    | 120   | kick             | 2-frame invert                      |
| H05 | 5.00    | 150   | final hit        | cut to end card; fade f170-179      |
```
QA for this brief: 180 frames exactly (last frame 179); every cut index is a multiple of 15; the invert shows on two frames and also inverts the title; no layer edge visible during the punch (106% start covers the 16x12 px shake: 1 + 2x16/1080 + 2x12/1920 = 1.042, and the 16/8/4/2 px decay stays under the settling scale on every frame); the title is not cropped by the platform UI; true peak <= -1.0 dBTP.

## Tool adapters

- Premiere Pro / After Effects: the recipe is written so each line is one keyframe or one effect. Premiere = cutting, speed, adjustment-layer flashes and inverts, grade, audio, export. AE = camera expressions, shake/punch/ladder, text animators, tracking, roto, halftone/glitch, behind-subject text. Details and expressions: `references/premiere-ae-mapping.md`. Frame display first, 0-based frames.
- AI editor / another NLE: paste sections 1-10 as written and add "Build exactly these frames and values; do not retime or add effects; report any element you could not build." Tell it the output frame count and ask it to verify the export by decoding.
- KLING / Seedance 2 / Higgsfield Cinema Studio (footage you must generate for a cut): brief ONE shot per generation, never the whole montage; one subject, one legible action, camera move in its own sentence with magnitude and limit, no text or logos in the prompt (text is added in the edit). Ask for about 2x the seconds the edit needs, because gestures arrive late (1.5-2x slower than prompted); choose the in-point from the actual frames, never from the promised timecodes. Seedance 2 accepts EN+ZH prompts; KLING wants plain action verbs. These models are a poor fit for frame-exact montage, strobes, flashes, text and cadence tricks; do those in the edit.
  Per-shot brief:
  ```
  SHOT <id>: <on-screen seconds> s needed, request <2x> s, <aspect>
  References: image 1 = identity only (face, hair, outfit); image 2 = <location/prop/style> if needed
  Start state -> end state: <...>
  Action (one): <...>
  Camera: <framing/angle>; <one move + amount + limit>   (or: locked off)
  Light and material: <...>
  Locks: same identity and wardrobe in every shot; no text, no logos, no extra people
  ```
- Nano Banana Pro: keyframes, texture plates (paper, halftone, scratches), sticker sheets, and a clean still for a held shot; give exact strings in quotes if a word must appear, and still render final titles in the edit. Reuse one identity reference across a sequence.
- Figma / Illustrator / Photoshop: design the title lockups, stickers, frames and end card at the recipe's pixel size; export PNG/SVG with alpha and animate them in AE.
- A generator cannot reliably do: face edits in code, frame-accurate cuts, exact lyrics, legible long text, a specific cadence. Keep those in the edit; regenerate a face through the model, never retouch it.

## QA checklist

- [ ] Frame count, fps, size and ending equal the plan; counted by decoding the export, not from the timeline.
- [ ] Every frame and every second of the export was actually looked at (contact sheets with absolute frame numbers plus native crops at effects); single-frame inserts and flashes included.
- [ ] Each cut sits on its planned frame; each effect, text event and transition shows at start, peak and end frame.
- [ ] Identity correct in every planned shot (back, profile, hands, silhouette too); no local face retouch; extras handled; no stray reference people or signatures.
- [ ] Text: planned words, no pseudo-letters, glyphs (Polish diacritics) present, readable at phone size, clear of platform UI.
- [ ] No layer edges, black corners or accidental bars during zooms, shakes and rotations.
- [ ] Cadence and retiming as planned (no judder on 30-100% slow motion; stepped looks stepped on purpose).
- [ ] Look: native crops of each texture/grade state; faces not crushed by a threshold or grade.
- [ ] Audio: planned song and SFX present and in sync on the first and last hit; true peak <= -1.0 dBTP on the encoded file; say "measured, not listened" if you did not listen.
- [ ] Story or motif delivered as planned; three motion reviews recorded; explicit locks met.
- [ ] Report separates authored changes (remix) from unmet locks and defects; never call a version final before the user does.

## References

Paths written as `<PLAYGROUND>/...` are relative to the root of the PLAYGROUND repo (the folder that holds `higgsfield-prompts/` and `creative-skills/`); the 28 raw Katana master prompts and 20 reference edit maps live there, not inside this skill.

- `references/edit-map-grammar.md`: read before writing any edit-map row; the defined vocabularies (cut kinds, cadence, motion, look, flashes/solids/inverts, transitions, effects, layers, text, audio) and two real edit maps.
- `references/compositing-recipe.md`: read when writing recipe lines; layer stack, camera and speed numbers, looks and grades, flash/strobe/overlay/invert rules, transitions, graphics, safe zones, title choreography, audio mix numbers.
- `references/premiere-ae-mapping.md`: read when building in Premiere/AE; operations and expressions for every recipe element.
- `references/creative-quality.md`: read before planning in any mode; mode and lock rules, reference discovery, music and SFX, typography, effects discipline, the three motion reviews.
- `references/qa-checklist.md`: read before handing over; the 16 checks, audio rules, inspection coverage, fix order, reporting.
- `references/master-prompt-template.md`: read when writing a reusable preset for a style (two templates plus an annotated real excerpt).
- `references/style-library.md`: read to pick or borrow a style; index of 28 presets with paths to the raw files and the 20 edit maps, plus five presets' recipes verbatim.
- Raw sources: `<PLAYGROUND>/higgsfield-prompts/raw/katana/` (presets) and `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/` (edit maps).
