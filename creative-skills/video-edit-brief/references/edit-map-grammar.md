# Edit-map grammar: the vocabulary for describing any edit

Contents
1. Conventions (frames, time, coordinates)
2. The one-line trick and edit families
3. Cut kinds (what a boundary can be) and false cuts
4. Cadence patterns (how many unique images per second)
5. Motion vectors (camera, subject, digital)
6. Look descriptors (global and per cut)
7. Flashes, solids, inverts, maybe-cuts, activity zones
8. Transitions, effects, layers (defined type lists)
9. Text events and the text inventory
10. Audio descriptors
11. Shot size, identity visibility, shot roles, meaning layer
12. How to read the machine edit-map format (with two real examples)

All lists below are the defined vocabularies of the Katana analysis stage, copied as-is. Use these exact words in edit-map cells so a collaborator (human or AI editor) reads them the same way. Free text goes in notes.

## 1. Conventions

- Frames are absolute and 0-based. `f1` is inclusive. A cut is the first frame of the new shot.
- Cuts are contiguous: the first `f0` is 0, each `f0` is the previous `f1` + 1, the last `f1` is `N - 1`.
- Seconds, for a constant frame rate: shot start = f0 / fps; inclusive end converts to (f1 + 1) / fps; frame centre = (f + 0.5) / fps. Use the centre time only to pick a representative still, never as a boundary.
- Keep fps rational: 29.97 is 30000/1001, 23.976 is 24000/1001. Do not round the render grid or accumulate rounded timecodes.
- Source length is measured from video frames, not from the container or the audio. Example: a reference with 283 video frames at 30 fps is 9.433 s even if the container says 9.517 s because the audio runs longer.
- Coordinates are fractions of the frame (`coords: frame`) or of the picture window (`coords: window`) when the picture sits in a bigger canvas.
- Flash, blur, burn and dissolve frames belong to the shot they sit in. When a transition straddles a cut, its frames are split between `transition_out` of shot A and `transition_in` of shot B.
- Never read a 5 or 10 fps sampling as the cut list. Automatic cut detection is a proposal: past detectors found 19 of 49 cuts on a whip edit, 9 of 35 on a strobe edit, 28 of 54 on another, and fired every 2 frames on grainy xerox footage. The frames are the ground truth.

## 2. The one-line trick and edit families

Write this sentence before any per-cut work:

> **The trick of this ref is** <the device> **on** <what timing/structure> **so that** <what the viewer feels or gets>.

Then list the frames where the trick happens (`trick_frames`: `[[f0, f1, "what happens"], ...]`). Refine it after the every-frame read but keep it one sentence.

Tests for a good line:
1. Could a stranger rebuild the reference's idea from it?
2. Does it name what changes over time, not only how it looks?
3. Would the remake be obviously wrong without it?

If the reference has no trick beyond "fast cuts on the beat", say so: the trick is then the cut rhythm plus the look.

Real examples:
- Signal: every traffic-signal change swaps the walker's outfit and brings in an element of the signal's colour, on the bar, so each beat reads as a transformation. (A remake that copied the timing and lost this trick was rejected.)
- City Rhythm: a locked-camera photo series where one detail changes every 1-2 frames, so the city seems to rearrange itself on the beat. (It was treated as video; it is a photo series.)
- Chant edit: each syllable of the chant becomes a different graphic on its beat (arc letters, a word on the face, a giant letter behind her, a typed word), with an overexposure burn hiding every jump cut.
- Zine edit: one girl turned into a photocopied zine: hard B/W threshold, one accent colour, a boiling pen contour and doodles, cut on every beat, looping back to its first frame.
- Quote edit: a motivational sentence spelled across film heroes, one or two words per cut fading in inside a rounded window, often behind the hero's head.

Edit families (pick the dominant one; per-shot routes override it):

| family | when | typical build |
|---|---|---|
| F1a | the hero replaces the performer inside the reference's own footage and the reference's world stays (window, baked text, grade) | swap or keep the original shots |
| F1b | the hero re-performs the reference's motion in a new world | re-perform plus compositing |
| F2 | new character / new world under styled overlays (mixed media, kawaii, fashion/idol, zine) | generated plates plus compositing |
| F3 | montage of real events or real people | own footage or library footage plus compositing |
| F4 | remake from the user's own clips | own footage plus compositing, no generation |
| F5 | photo series / stop motion: locked camera, one detail changing per 1-2 frames | stills plus compositing |
| F6 | typography and shapes only | motion graphics |
| F7 | product or object swap | per product workflow |

## 3. Cut kinds

A boundary the detector or your eye proposes is one of these. The right column says how it shows when you step frame by frame.

| Kind | How it shows | Note |
|---|---|---|
| hard cut | content changes between two frames | default |
| whip / smear | 2-3 smeared frames; the content behind the smear changes in the middle; usually straddles the beat (2 frames before, 1 after) | 49 cuts by eye where a detector found 19 |
| hidden in a transition | burn / blur / mosaic / flash frames with a different pose or framing on each side | the burn can start 3 frames before the cut; the frame-diff jump at the cut can be smaller than the burn onset |
| invert / polarity | the frame flips negative; the content continues (effect) or changes (cut) | 1-frame inverts inside 1-6 frame shots |
| dark | both sides near-black; only shapes change | detectors miss these |
| same-tone | same background and palette, different pose or framing (jump cuts in one location) | selfie edits, white-cyc plates |
| 1-2 frame inserts | a single foreign frame: black, white, solid colour, a different shot, a ghost cross-blend | e.g. 1-frame flashes at f54 and f114, ghost blend at f113 |
| strobe sections | the picture alternates every 1-3 frames (shot/black/shot, or two shots ping-ponging) | about 35 picture changes in 230 frames |
| micro-cut bursts | a run of tiny shots on a ~4-6 frame grid | log ONE cut with cadence `burst` and put the sub-shots in notes |
| ink_wipe / matte_wipe | both images sharp on either side; a crisp or ragged edge travels (brush stroke, ink bleed, smoke, torn paper, graphic matte), usually over 2-6 frames | not a blur: a whip blurs the whole frame, a wipe has an organic edge, bristle streaks, splatter dots, often an ink-black or white rim; mid-wipe one frame holds parts of both shots at full contrast, a dissolve shows both at reduced contrast |

Machine edit-map labels for the kind column: `start` (first shot), `cut` (ordinary boundary), `burst sub[f, f, ...]` (a burst with its sub-shot frame indices). Confidence: `high`, `medium`, `low`.

### False cuts (detectors add these; do not log them as cuts)

- grain or xerox boil (a "cut" every 2 frames);
- flash frames, and in-plate exposure flashes;
- text pops, and PIP cards popping on;
- light flicker and camera shake;
- letters flying out.

## 4. Cadence patterns

Count unique frames per shot. Identical neighbouring tiles on a frame sheet are held frames.

Defined values for `cadence.pattern`:

`native pulldown_24in30 pulldown_24in60 stepped interp_slowmo blend_retime freeze speed_ramp burst`

| Pattern | Meaning |
|---|---|
| native | every frame unique |
| pulldown_24in30 | 24p in 30p: every 5th frame repeated |
| pulldown_24in60 | 24p in 60p: 2:3 pulldown |
| stepped | holds in a repeating pattern, e.g. 170 unique of 283 frames, about 18 fps in a 30 fps container (holds 2,2,1) |
| interp_slowmo | interpolated slow motion: every 60p frame unique |
| blend_retime | frame-blend retime: ghosted in-betweens |
| freeze | a held frame (integer frame) |
| speed_ramp | speed changes inside the shot; note frame and speed |
| burst | micro-cut run |

Machine edit-map extras: `short` (a shot of 1-3 frames, too short to classify), `mixed` (irregular holds, e.g. `holds=2,1,1,1,5,2,1,1,4`). The `holds=` list reads as the repeat count of each consecutive unique frame.

Record the speed of every retimed shot in `cadence.speed`: a number, or `[[frame, speed], ...]` for a ramp. Picking the frame method from the speed:
- 0.3-1x: blend the two neighbouring source frames, weighted by the fractional index. Duplicated frames judder.
- Below 0.3x, or fast limbs: nearest frame. Blending there reads as a matte halo.
- Freeze holds: integer frames.

Cadence mismatch goes both ways. Generated footage usually comes back at 24 fps, so a 60p-native shot may fall from 36 to 14 unique frames; a reference stepped at about 18 fps will look too smooth if rebuilt at native cadence. Both are fixable in the edit once known: re-apply digital motion at the output frame rate, or step frames to the reference's hold pattern. Flag fast-content shots (more distinct images per second than the source can carry) in the notes up front.

## 5. Motion vectors

Camera move values (`camera.move`):

`static handheld pan tilt push_in pull_out zoom orbit track crane whip shake face_lock`

Plus `digital: true/false`: true when the move is added in the edit (zoom punch, eased push-in, shake, face-lock, mirror, rotation) rather than being in the plate. Separate digital edit moves from in-scene camera motion; rebuild whole-plate digital moves at the output frame rate and do not duplicate motion already present in generated footage.

Machine edit-map motion cell: `<move> e=<energy> z=<zoom> pan=(<dx>,<dy>)`
- `move` one of: static, handheld, pan, tilt, push_in, pull_out, shake, subject_motion (the subject moves in a fixed frame), `n/a` (too short).
- `e` motion energy (0 = frozen). Relative, compare within one map. Rule of thumb read off the 20 maps: about 0-5 calm, 10-25 busy, 40-60 violent shake or whip.
- `z` signed zoom: positive = push in, negative = pull out. Rule of thumb from the maps: |z| above 1 is a fast punch, usually on 2-5 frame shots.
- `pan` normalized (dx, dy) drift of the frame content.

Examples of reading: `push_in e=32 z=0.69` is a fast punch-in; `shake e=61 pan=(-0.16,-0.27)` is a violent shake hit; `static e=0.0` is a held frame or solid.

Other digital moves seen in edits: eased push-in (a smooth ~10% push on 24p footage rebuilt at 60p), zoom ladder (16th-note jump zooms), punch-in at the cut that decays, boil-stepped shake decaying from the cut, 3-frame stutter, ghost trail, mirror (a flipped shot), roll.

## 6. Look descriptors

Per shot (machine cell): `BW` flag if black and white, `L<luma mean>`, `S<saturation mean>`, dominant hue name. Example: `BW L0.229 S0.047 None`, `L0.264 S0.409 cyan`.

Hue names that occur: none (neutral), blue, cyan, green, yellow, orange, red, magenta, purple.

Global look line: `bw` (all B/W), `accent_only` (B/W plus one saturated accent), `threshold` (hard two-tone), `luma_mean`, `contrast`, `sat`, `colorful`, `warmth` (negative = cool), `hue` (dominant), `bars` (letterbox bars or null).

The look object to write in a brief:

`class` (`clean` / `stylised`), `bw`, `desc`, `grain {present, size_px, boil_every}`, `halation`, `vignette`, `softness`, `cast`, `threshold`, `stats {mean_rgb, luma_p1_p50_p99, sat_mean}`, optional per-section changes.

Stats example (a warm film look): mean RGB 0.357/0.289/0.226, luma p1 0.006 / p50 0.197 / p99 0.884 means crushed blacks, no clipping, warm.

What to observe: B&W, threshold/xerox, duotone, one accent colour; grain size and whether it boils every frame or stays static; halation, glow, vignette, softness or compression mush; colour cast, crushed or lifted blacks; changes per section.

- clean: natural colour, no visible grain at 100%, no vignette, no cast beyond the scene's own light. An exact remake adds nothing: no grain, vignette or house accent colour.
- stylised: any of B/W, threshold, duotone, accent-only colour, visible or boiling grain, halation, light leaks, a hard contrast curve, or one cast across all shots. Measure grain size, boil interval, threshold and accent. An exact remake reproduces them; a remix carries chosen principles into its own documented look rather than randomizing a look on each cut.

A house B&W-plus-lime grade applied to colourful references was rejected four times ("colors wrecked, too much noise"): a deliberate variation must be distinguishable from an accidental colour mismatch.

## 7. Flashes, solids, inverts, maybe-cuts, activity zones

Sections of the machine edit map, with their exact vocabulary:

**Flashes** `(f0-f1 type note)`. Type is `black` or `white` (or `solid`/colour). Note values:
- `hides/marks a cut` (the flash covers the cut)
- `insert returns to the same shot` (a foreign frame inside one shot)
- `same shot on both sides` (a flash inside one continuous shot, not a cut)
- `opens the video` / `ends the video` (flash on the first / last frames)

**Solids** `(f0-f1 kind color)`: frames that are one flat colour, with a hex value. Examples: `f270-277 black #060404`, `f13-38 black #11110b`.

**Inverts**: a list `[{"f0": 82, "f1": 87, "cut": "c04"}]`, i.e. negative frames and the shot they sit in. Invert durations seen: 1 frame inside 1-6 frame shots (polarity strobes), 2-frame impact frames, 5-6 frame inverts on a hit. Invert applies to the whole frame including graphics.

**Maybe-cuts (unconfirmed)**: a list of frame indices the detector flagged but could not confirm. Check each on the frame sheet; most are grain, flash or text pops.

**Activity zones** `[{"f0": 427, "f1": 453, "big_changes": 18}]`: frame ranges where the picture changes a lot (many big frame-to-frame changes). They typically mark strobe sections, bursts and effect clusters. Inspect them at native frame rate first.

## 8. Transitions, effects, layers

Transition types (`transition_in`, `transition_out`, each `{type, f0, f1, hides_cut, note}`):

`cut whip flashlight white_frames black_frames color_flash mosaic glitch blur dissolve invert zoom_punch slide wipe ink_wipe matte_wipe split_strip mirror match_cut`

Description of the less obvious ones:
- flashlight / overexposure burn: 3-5 frames, burns to white, dark hair survives, pixel blocks on the face.
- white_frames / black_frames: pure white or black frames (e.g. 2 white frames before each colour entry).
- color_flash, mosaic, glitch: colour flash, pixel mosaic, glitch tiles.
- blur: blur pulse, with or without a thin dark frame.
- split_strip: a stack of strips sliding in on beats.
- match_cut: shape or motion continues across the cut.

Effect types (`effects`, each `{type, f0, f1, params}`):

`flash_white flash_black flash_color invert threshold duotone bw hue_shift blur_pulse zoom_punch glitch mosaic rgb_split shake strobe mirror light_leak exposure_flash ghost_blend freeze stutter split_screen`

Layer types (everything that is not the footage itself), each with `z` (`under_subject` / `over_subject` / `over_all`) and `track` (`static` / `subject` / `face` / `camera`):

| Layer type | Note |
|---|---|
| cutout_subject, outline, halo, contour | offset colour outline, white die-cut halo, boiling pen contour: colour, width in px, boil rate |
| panel, pip, collage_card, split_screen | position, size, pop-on frames |
| starburst, shape | behind or in front of the subject |
| sticker, doodle | COUNT them per second; density is what viewers judge. Note their scale relative to the subject (doodles of 30-80 px were too small for the reference; 290-510 px gestures were right) |
| frame_border, window, letterbox | rounded window inside a canvas, hand-drawn border, bars; measure the window |
| watermark | position, size, opacity |
| behind_text | words occluded by the subject: which letters are hidden on which frames |
| hud, light_leak, particles | when present |

## 9. Text events and the text inventory

For every word or block record:

`f_in` (first frame), `f_full` (first fully-on frame), `f_out_start`, `f_out` (last frame); the animation (fade length in frames, pop, typewriter per letter, slam, write-on, wobble, smear-out); whether the hero passes in front of any part of it; whether it crosses a cut. Words that grow letter by letter are one event with a typewriter animation.

Full text event fields: `id, f_in, f_full, f_out_start, f_out, text (null for lyrics), letters, font_class, weight, italic, size_pct_h, cx, cy, coords, box [x,y,w,h], color, stroke, glow, animation, layering (front/behind/difference), source (ref_pixels/retype/new_words/lyrics_file), crosses_cut, meaning`.

Inventory table (one row per event):

| id | frames (in / full / out) | words | font class | size % H | position (cx, cy) | colour | animation | layer |
|---|---|---|---|---|---|---|---|---|
| t03 | ~30 (faint) / 44-53 / 53 | GOTTA | ultra-condensed grotesk, caps | 40% of window H | 0.26, 0.28 (window) | #ffffff | slow fade in, ends at the cut | behind (head covers the A) |
| t04 | 49 / 51-53 / 53 | GET | didone serif, caps | 24% of window H | 0.74, 0.21 (window) | #ffffff | fade in 2 f, ends at the cut | front |
| y01 | 24 / 24 / 39 | (4 letters) | bold italic sans | 9% | 0.50, 0.42 | #ffffff | typewriter, 4th letter by f34, smeared out f37-39 | front, on the face |

How to measure: read frames on the every-frame pages, then confirm `f_in` and `f_full` on native crops (fades read from small tiles are often 1-2 frames off). Take the tight box of the letters at native resolution. For white letters, threshold min(R,G,B): clean bold sans at or above about 236, thin or grainy serifs about 190-215. `size_pct_h` = cap height divided by frame (or window) height. `cx, cy` = box centre as fractions. Sample the letter core for colour, not the edge; note stroke, shadow and glow. Layering is `behind` if the subject covers any letter on any frame, `front` otherwise, `difference` for blend-mode text.

Text source, per event: `ref_pixels` (rebuilt from the reference's own pixels), `retype` (same words in new type only when source pixels cannot be used), `new_words` (authored words in planned slots), `lyrics_file` (words read from a timed file).

Classify the visible font style (class, weight, width, slant, case) and choose the closest available face by glyph geometry; do not claim exact font identification.

## 10. Audio descriptors

`bpm`, `bpm_check` (how you verified it), `period_s`, `beat_phase_s`, `downbeat_s`, `sections [{name,t0,t1}]`, `cut_on_onset_share`, `cut_lead_frames`, `hidden_edits [{t, from_s, to_s}]` or `{t, suspected: true, note}`, `sfx_layer [{t, type, note}]`, `speech` (none / vo / lyrics / chant), `lufs_i`, `true_peak_db`, `plan`.

Audio plan values: `reuse_ref_audio`, `user_track`, `tiktok_track`, `stock_track`, `voice_track`. No plan uses a code-made track, procedural music, a synthesized beat or generated SFX.

Beat grid: `t(b) = phase + b x period`. Example: t(b) = -0.015 + b x 0.42980 (a 139.6 BPM track).

Verify BPM by hand: express the cut intervals in beats at the candidate BPM and at x2, x1/2, x3/4 and x4/3; the right BPM puts most intervals near whole or half beats. Auto-BPM has been off by about 1, doubled, or stuck in a 4:3 ambiguity (99.4 true versus 130.7 detected). On chants, cross-check with word starts (words every 0.446 s = about 134 BPM).

Systematic offsets to note: cuts that lead the beat (about 2 frames early), whips that straddle it (2 frames before, 1 after), picture that lags transients (26-43 ms late on big hits with nearest-frame sampling).

Cut-on-onset share (share of cuts within +-2 frames of an audio onset): about 0.81 on well-made aura reels; one edit got 777k views at 77% on-beat cuts and 305k at 51% with another track. At or above about 0.7 the edit is onset-locked; low share means cuts follow picture or words.

Hidden music edits: a jump in offset when sliding the reference audio against the original song is a splice (example: 0-12.45 s plays song 3.45-15.90 s, then jumps to song 34.30 s). Without the song, suspect a splice at a sudden energy or timbre change off the bar grid, a section starting mid-phrase, or a skipped or doubled beat. The editor's own SFX layer (booms, whooshes, risers, shutters, ducks) is what remains after subtracting the song; list the events (13 whooshes at 1.5-5 kHz and ducks of -6/-7 dB in one reference).

## 11. Shot size, identity visibility, shot roles, meaning layer

`shot_size`: ECU / CU / MCU / MS / MWS / WS / EWS, `insert`, `graphic`.

`identity_visible` (apply the same words to planned output shots):

| value | meaning |
|---|---|
| face_clear | the face is readable: front or three-quarter, sharp enough to recognise |
| face_partial | profile, small in frame, heavy blur or partial occlusion |
| body_only | back turned, hood, helmet, hands, silhouette or another body crop |
| none | no person is present (never means merely "no readable face") |

On a requested identity replacement, hidden-face shots still need the target identity (hair, build, clothing, silhouette). Never reveal a concealed face just to make verification easier.

Semantic shot roles (observed role of each source cut, with frame evidence): hook/origin, identity, action, accent, reveal, consequence, transition, breath, payoff, closure. Describe what changes, what causes the next beat and what the viewer learns. A source can be non-narrative; do not invent a plot it lacks.

Meaning layer: for every graphic and text event write what it means relative to the words, the beat or the story, then what it maps to in the remake.
- A giant pink "N" behind the girl is the syllable NI of ichi-NI-san; the new chant's DUL took that slot as giant letters.
- ARIGATO types as ARI bold + GATO thin, so SARANGHAE typed as SARANG bold + HAE thin.
- Each word belongs to one sentence spread across cuts; losing a word breaks the sentence, not just a cut.
- When on-screen words are the song's own lyrics on their syllables, your own words over that audio read as fragments and get rejected.
- A reference that is a portrait of a nation cannot just be relabelled for one player: map the reference's beats and sections onto the user's subject first, then fill the rest.

A remake that keeps the shapes but breaks the meaning reads as random graphics.

Missing-role inventory (from clips and photos you actually viewed): `role`, `available_asset`, `viewed_range`, `usable_action`, `gap`, `planned_solution`. Produce missing actions, not a fresh version of every source cut. A supplied photo can serve identity or design; do not pretend it contains an unseen action.

## 12. Reading the machine edit-map format

The 20 reference maps in `<PLAYGROUND>/higgsfield-prompts/raw/katana-refs/<slug>.md` use this layout (they are detector proposals, not confirmed cuts):

```
# Katana reference edit map: <slug>
Generated ... (frames [0, N], crop {...}, src_fps F). Detector proposals, not confirmed cuts.
Totals: cuts C, bursts B, flashes X, solids S, inverts I; cadence patterns: native=.., mixed=.., ...
Global look: bw=.. accent_only=.. threshold=.. luma_mean=.. contrast=.. sat=.. colorful=.. warmth=.. hue=name(strength) bars=..

## Cuts (id f0-f1 | t0-t1 s | dur | kind/sub_cuts | conf | cadence | motion move/energy/zoom/pan | look bw/luma/sat/hue | flashes/inverts/text)
- cNN fA-fB | t0-t1s | dur | kind | conf | cadence holds=... | move e=.. z=.. pan=(..,..) | [BW] L.. S.. hue [flashes=n] [inv=n] [text=n]

## Flashes (f0-f1 type note)
## Solids (f0-f1 kind color)
## Inverts
## Activity zones
## Maybe-cuts (unconfirmed): ...
```

`text=5` on a cut means the detector found 5 text-region candidates, not 5 words. Two complete examples follow, one calm and one dense.

### Example A: a calm edit (7 cuts, no flashes)

```
# Katana reference edit map: many-lies
Generated 2026-10-09 with Higgsfield katana workflow `analyze_ref.py` over the preset's reference video (frames [0, 600], crop {"x": 0, "y": 0, "w": 1920, "h": 1080}, src_fps 20). Detector proposals, not confirmed cuts.
Totals: cuts 7, bursts 0, flashes 0, solids 0, inverts 0; cadence patterns: native=5, mixed=2
Global look: bw=False accent_only=False threshold=False luma_mean=0.42 contrast=0.741 sat=0.186 colorful=0.271 warmth=0.043 hue=orange(0.253) bars=null

## Cuts (id f0-f1 | t0-t1 s | dur | kind/sub_cuts | conf | cadence | motion move/energy/zoom/pan | look bw/luma/sat/hue | flashes/inverts/text)
- c01 f0-84 | 0.00-3.54s | 3.54s | start | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | static e=4.66 z=-0.056 pan=(0.054,0.0) | L0.466 S0.144 orange text=5
- c02 f85-194 | 3.54-8.12s | 4.58s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | static e=2.43 z=-0.001 pan=(0.0,0.0) | L0.452 S0.184 orange text=5
- c03 f195-261 | 8.12-10.92s | 2.79s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | static e=3.24 z=-0.032 pan=(0.0,0.0) | L0.349 S0.241 orange
- c04 f262-383 | 10.92-16.00s | 5.08s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | static e=1.75 z=-0.002 pan=(0.0,0.0) | L0.407 S0.215 orange text=2
- c05 f384-468 | 16.00-19.54s | 3.54s | cut | high | mixed holds=1,7,1,1,1,1,1,1,1,1,1,1... | static e=0.9 z=-0.012 pan=(0.0,0.0) | L0.415 S0.15 orange text=3
- c06 f469-545 | 19.54-22.75s | 3.21s | cut | high | native holds=4,1,1,1,1,1,1,1,1,1,1,1... | static e=1.66 z=-0.01 pan=(0.0,0.0) | L0.421 S0.21 orange text=1
- c07 f546-600 | 22.75-25.04s | 2.29s | cut | high | mixed holds=1,1,1,1,1,1,1,1,1,1,1,1... | static e=0.57 z=0.001 pan=(0.0,0.0) | L0.427 S0.156 orange text=5
```

### Example B: a dense edit (14 cuts, flashes, solids, one invert)

```
# Katana reference edit map: tiger-eyes
Generated 2026-10-09 with Higgsfield katana workflow `analyze_ref.py` over the preset's reference video (frames [0, 263], crop {"x": 0, "y": 0, "w": 600, "h": 450}, src_fps 24). Detector proposals, not confirmed cuts.
Totals: cuts 14, bursts 0, flashes 4, solids 5, inverts 1; cadence patterns: mixed=5, native=9
Global look: bw=False accent_only=False threshold=False luma_mean=0.245 contrast=0.812 sat=0.312 colorful=0.584 warmth=0.01 hue=green(0.123) bars=null

## Cuts (id f0-f1 | t0-t1 s | dur | kind/sub_cuts | conf | cadence | motion move/energy/zoom/pan | look bw/luma/sat/hue | flashes/inverts/text)
- c01 f0-12 | 0.00-0.54s | 0.54s | start | high | mixed holds=2,1,1,1,1,6,1 | pull_out e=13.93 z=-0.319 pan=(0.013,-0.075) | L0.264 S0.409 cyan
- c02 f13-38 | 0.54-1.62s | 1.08s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | static e=0.0 z=0.0 pan=(0.0,0.0) | L0.064 S0.566 green
- c03 f39-65 | 1.62-2.75s | 1.12s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | static e=2.06 z=-0.022 pan=(0.0,-0.058) | L0.204 S0.363 yellow
- c04 f66-87 | 2.75-3.67s | 0.92s | cut | high | mixed holds=2,1,1,1,1,2,3,1,1,2,1,6 | handheld e=16.5 z=0.064 pan=(0.029,0.036) | L0.348 S0.344 blue inv=1
- c05 f88-106 | 3.67-4.46s | 0.79s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | static e=0.48 z=0.001 pan=(0.0,0.0) | L0.162 S0.32 green text=2
- c06 f107-128 | 4.46-5.38s | 0.92s | cut | high | mixed holds=1,12,3,1,5 | static e=0.28 z=0.0 pan=(0.0,0.0) | L0.268 S0.382 green text=1
- c07 f129-151 | 5.38-6.33s | 0.96s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | static e=2.79 z=0.004 pan=(0.0,0.0) | L0.197 S0.115 None text=5
- c08 f152-161 | 6.33-6.75s | 0.42s | cut | high | mixed holds=1,1,1,1,1,1,1,3 | static e=0.0 z=0.0 pan=(0.0,0.0) | L0.227 S0.411 yellow flashes=4
- c09 f162-188 | 6.75-7.88s | 1.12s | cut | high | native holds=2,1,1,1,1,3,1,1,1,1,1,1... | static e=1.02 z=0.001 pan=(0.0,0.0) | L0.264 S0.432 green
- c10 f189-210 | 7.88-8.79s | 0.92s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | pull_out e=1.62 z=-0.365 pan=(0.0,0.0) | L0.127 S0.574 blue text=1
- c11 f211-225 | 8.79-9.42s | 0.62s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1,1... | subject_motion e=12.81 z=-0.02 pan=(0.0,0.0) | BW L0.332 S0.0 None text=5
- c12 f226-235 | 9.42-9.83s | 0.42s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1 | pull_out e=14.77 z=-0.358 pan=(-0.067,-0.033) | L0.318 S0.101 None text=3
- c13 f236-246 | 9.83-10.29s | 0.46s | cut | high | native holds=1,1,1,1,1,1,1,1,1,1,1 | push_in e=23.06 z=0.462 pan=(0.15,0.36) | L0.364 S0.349 green text=2
- c14 f247-263 | 10.29-11.00s | 0.71s | cut | high | mixed holds=4,1,1,1,1,1,1,1,1,1,1,1... | static e=3.64 z=0.015 pan=(0.0,0.0) | L0.287 S0.029 red text=5

## Flashes (f0-f1 type note)
f152-152 black hides/marks a cut; f154-154 black same shot on both sides; f156-156 black same shot on both sides; f158-158 black same shot on both sides

## Solids (f0-f1 kind color)
f13-38 black #11110b; f152-152 black #000000; f154-154 black #000000; f156-156 black #000000; f158-158 black #000000

## Inverts
[{"f0": 82, "f1": 87, "cut": "c04"}]

## Maybe-cuts (unconfirmed): 2, 6, 77, 78, 79, 81, 229, 246
```

Reading Example B: c08 is a 10-frame shot with 4 single-frame black inserts (flashes at f152, 154, 156, 158: "same shot on both sides" means a stutter inside one shot, not cuts); c04 carries a 6-frame invert (f82-87) and a handheld shake at e=16.5; c11 is the only B/W shot (`BW`, saturation 0); c13 is a violent push-in (z=0.46, pan 0.15/0.36) and c02 is a solid black hold (`static e=0.0`, solid f13-38 #11110b).

To use these maps as pacing evidence for a new edit, copy the duration column (`dur`) and the cadence column into your own map and re-decide content, motion and look for the new subject.
