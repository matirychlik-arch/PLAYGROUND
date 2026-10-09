# Numerical compositing recipe: grammar, rules and starting numbers

Contents
1. Time base and sampling rules
2. Recipe notation (the shot block you write)
3. Layer stack (draw order)
4. Camera: scale / position / rotation keyframes, punches, ladders, shakes
5. Speed and time remap
6. Looks and grades (numbers)
7. Flash, strobe, overlay, invert rules
8. Transitions (durations and numbers)
9. Graphics layers, stickers, doodles, collage panels
10. Safe zones and the no-edge rule
11. Title choreography
12. Audio hit alignment and mix numbers
13. Worked numeric recipes from real presets
14. Gotchas

The numbers come from the Katana compositor defaults and from the fixed recipes of the 28 presets. Treat them as reproducible starting settings at the preset's own resolution, then adjust when readability suffers. Scale pixel values by (your width / the width stated). Frame-based values assume the stated fps; convert seconds by multiplying by your fps.

## 1. Time base and sampling rules

- Work in integer frames; convert to seconds only for audio. Start of a shot = f0 / fps, end = (f1 + 1) / fps (half-open [t0, t1)).
- A frame f is sampled at t = (f + 0.5) / fps. A shot owns the frames whose sample time lies inside [t0, t1). Local time lt = t - t0.
- Source frame index = floor((src_in + lt x speed) x source_fps). A 24 fps clip in a 30 fps timeline at speed 100% therefore repeats one frame in four. That is correct for a pulled-down look and wrong for a smooth one; decide on purpose.
- Output length is exactly the planned frame count. Verify by decoding the export, not by reading the duration.
- Random-looking effects (grain, boil, scratch, doodle wobble, glitch blocks) must be deterministic: key them by frame number and a fixed seed so any frame renders identically on any re-render. Boil step b = floor(f / boil_interval) with boil_interval 2 frames for doodle wobble, 1 frame for grain.
- Beat times: `b8` means beat 8 = beat_t0 + 8 x 60 / bpm. Cuts normally sit on whole or half beats; bursts on 1/16 notes.

## 2. Recipe notation

One block per shot, in this fixed order. Property names are the ones used throughout this pack; values are the numbers an editor types into keyframes.

```
R<id>  f<f0>-<f1>  (<t0>-<t1> s)  src: <clip> @ <in-point>  speed <n>%  cadence <native|stepped 2,2,1|...>
  cam    scale <a>% -> <b>% over f<x>-<y> <ease>; anchor (<ax>,<ay>); pos (<x>,<y>) -> (<x>,<y>); rot <deg>; shake <amp px> <dur f>
  look   <grade name or levels/curves values>; grain <sigma or amount>; vignette <n>; bloom <n>
  layers (bottom to top) <name: spec>, ...
  fx     <effect: frames, opacity/amount per frame>, ...
  trans  in: <type, frames>; out: <type, frames>; hides_cut: <yes|no>
  text   <title ids from the title table>
  audio  <hit ids from the hit table>
```

Keyframe shorthand: `prop @f<n> = value [ease]`, with `[lin]`, `[in2]`, `[in3]`, `[out2]`, `[out3]`, `[inout]`, `[outback]` (quadratic/cubic in, out, in-out, overshoot). Animated number form used by the compositor: `{from a, to b, ease e, over d}` where d is a fraction of the shot duration.

Premiere/AE mapping of each property is in premiere-ae-mapping.md.

## 3. Layer stack (draw order, bottom to top)

1. Plate: the footage with its camera transform (scale, position, rotation, speed).
2. Trail (ghost of earlier frames), applied before the look.
3. Look: grade, threshold, duotone, levels.
4. Back graphics: everything behind the subject (giant letters, starburst, stairs/pixel squares, panels).
5. Subject: outline/halo, cut-out of the subject from its matte re-drawn over the back graphics, glow.
6. Over graphics: contour, face-anchored graphics, doodles, stickers (sticker layer at order 50), global text (order 60).
7. Post: full-frame treatments (B/W, tint, invert, rgb split, strobe, light leak) and transitions.
8. Final: vignette, grain, dust, border. Finishing always goes last so texture is integrated, not sitting under the graphics.

A typical full finish after all graphics (Many Lies preset): 0.65 px soften, highlight bloom (screen blend at 42%, computed at quarter resolution), vignette (-38% at the corners), film grain sigma 0.032. Every frame except pure black gets it.

Rule for behind-subject text and graphics: the subject must be a clean matte (rotoscope or background removal) and the text sits between plate and subject. Check mask edges at 100% on bright, dark, hair and fast-motion frames.

## 4. Camera keyframes

| Move | Parameters (default) | Effect |
|---|---|---|
| frame (default) | zoom z=1, anchor ax=.5 ay=.5 (source point), target sx=.5 sy=.5 (screen point), rot=0, mirror=0, fit=cover | place source point (ax,ay) at screen (sx,sy), scale fit x z; "cover" enlarges so no edge shows |
| crop | [x,y] 0..1 of the source | crop centre, clamped inside the plate |
| face-lock | eye distance as fraction of W (ld .09-.15); eye midpoint target (lx .5, ly .4); z0 1 -> z1 1.04 (out3 across the shot); kick .035 decaying exp(-lt x 14); roll levelling 0..1; cover true | pins the eyes, levels roll, never reveals plate edges. Moves the whole plate only |
| zoom | z0 1, z1 1.08, ease out3 | zoom across the shot |
| push | rate .1 per second, linear | slow push on holds and freezes |
| punch | amount .07 (7%), duration .25 s, curve 2 (decays) | punch-in at the cut |
| ladder | steps [1, 1.12, 1.24, 1.36] | zoom ladder: shot split in equal steps (16th-note jump zooms) |
| pan / tilt | dx, dy as fraction of W / H per second | drift |
| roll | rad or rad/s | rotation |
| handheld | amp 6 px, 0.7 Hz, rot .004 rad, fixed seed | smooth noise drift |
| shake | amp [16,12] px, duration .25 s (.125 s on freezes), stepped every boil frame, decaying from the cut | hit shake |
| stutter | n=3 source frames looped from the in-point, step 1 | 3-frame stutter |
| trail | n=3, step 2, alpha .35 | ghost trail of earlier frames |

Restrained default moves (use these before anything bigger):
- A still or held shot: scale 100% -> 104% over the shot, or a pan within about 3% of the canvas, with enough overscan that the key feature stays in frame. Vary framing and direction by shot function; do not apply one repeating zoom to every shot.
- Punch: +6% decaying over 0.25 s (6 frames at 24 fps), plus shake 18 px over 0.18 s on the strongest hits.
- Pull-back on a hero shot: 1.35 -> 1.0 over the shot (zoom out into a backlight).
- Larger smears and scale jumps belong to designated transitions only.

Hold-shot move table from the presets (time = seconds from shot start):
- eyes close-up: zoom 1.00 -> 1.15, easeOut, shake on the hit.
- clip shots: zoom 1.00 -> 1.14 (alt 1.05 -> 1.2).
- layered hero: scale 0.98 -> 1.08 (alt 1.08 -> 1.2); x drift -70 -> +60 px; rotation 0.8 deg x sin(2.1u).
- walk cut-out: push 1 -> 1.1, plus a 1.2% pulse on every background flip, 3 px bob.
- zoom ramps in a strobe edit: x1 -> 1.03 / 1.02 / 1.04 / 1.05 / 1.08 / 1.1 depending on shot length (about +4% on a 9 frame shot, +8% on a 27 frame shot, +10% on a 36 frame shot).

Bounce/overshoot easing for slams: scale per frame [1.3, 0.9, 1.06, 1] over 4 frames.

## 5. Speed and time remap

| Setting | What you get |
|---|---|
| speed 100% or above | whole frames (24 fps in 30 fps repeats one frame in four) |
| 30% to 100% (and reverse, ramps) | frame-blended slow motion: (1-w) x frame i0 + w x frame i1, where i0/i1 are the two source frames around the fractional index. Duplicated frames judder here |
| below 30% | nearest whole frame; a blend this slow reads as a ghost or matte halo |
| fast limbs, slowed generated faces | nearest frame at any speed (blend ghosts) |
| 0 (freeze) and stutter | always a whole frame; set the freeze frame explicitly |
| ramp | linear ramp to speed1 over the shot (e.g. 100% -> 50%) |

Typical presets: footage at 1.3x for an opening countdown; clips at 1.4x so a glint peak lands on the beat (pick the in-point so the peak hits the target frame); a hand shot at 0.7; strobe partner shot advancing at 0.35x so the eyes barely move; walks and holds at 1.0.

Stepped look: to imitate 18 fps in a 30 fps timeline use a hold pattern of 2, 2, 1 (every 5 output frames show 3 distinct images), applied to graphics too.

## 6. Looks and grades

| Look | Parameters (default) | Effect |
|---|---|---|
| xerox / photocopy | black .13, white .80 (levels), grit .42 (noise into threshold), hard .62 (threshold mix), ink [10,10,10], paper [255,255,255], grain step 1 frame, optional keyed accent | S-curve levels + hard threshold with boiling grain; the key keeps one colour as a 2-tone ramp |
| accent key | channel mode lo .06 width .09 vmin .16; or hue window [h0,h1] deg, soft 15, sat .25, val .16; dark [10,38,0], light [196,255,52], amount 1, mix .4, lift .12, gain 1.1 | one colour survives the threshold (lime hair, pink) |
| duotone | paper = accent, ink [8,12,4], grit .5 | two-colour threshold |
| negative | xerox params, inverted | inverted xerox (outline turns white) |
| levels | black, white, hard .85 | per-shot levels |
| threshold | grit 0, hard 1 | pure threshold |
| bw | grayscale, contrast 1.22, brightness 1.04 | B/W |
| pink lift (kawaii grade) | brightness 1.08, contrast 1.02, saturate 1.12, soft-light rgba(255,160,210,.24), screen rgba(255,240,248,.03) | sugary lift |

Ramp a look across a shot: `black .06 -> 0 (in2) over 85% of the shot` (xerox opening up).

Readability after a global look: a hard threshold crushes backlit, specular and worm's-eye frames and can turn medium close-up faces near-black. Soften the levels per shot (use the open version, a ramp or `levels`) rather than retouching the face. Check every face close-up against the plain footage.

Finishing blocks (8-bit SDR, starting points; match by measured stats, not by these numbers):
- Basic: contrast 1.18, brightness -0.03, saturation 0.55; mono = saturation 0; colour temperature 5200.
- Per-channel tone curve, e.g. R: 0/0 .15/.10 .5/.55 .8/.86 1/.93.
- Grain: noise amount 9 (temporal), or sigma 13 on a 0..255 grayscale grain softened by 0.6 px; sigma 0.032 in the Many Lies finish; sigma 0.018 at half resolution in the anime edit (6 cycling patterns).
- Vignette: strength 0.30 (grunge) / -38% corners (Many Lies) / 0.16 (Physical Body).
- Softness: Gaussian sigma 0.7-1.4 px.
- Chroma fringe: R/B shift +-2 px (1 px in the colourist's later version).
- Halation chain: take highlights above ~0.62, blur radius ~22, tint orange (R 1, G .55, B .25), screen at 32%. Bloom: highlights above 0.62 blurred (radius 22) and added at 35%.
- Echo trails: blend each frame with max(current, previous output) at 35% in layered sections, 25% on eyes/clips, 30% on slide-outs, 15% on walks; none in intros and collages.

Exposure matching (grunge preset): for each reference frame measure grayscale mean and standard deviation once. For a subject frame g, target = (g - mean(g)) / max(std(g), eps) x max(std(ref), 10) + mean(ref); blend about 10% g with 90% target, clamp 0..255. Reduce for nearly uniform inputs or clipped faces. The goal is to match the reference's exposure progression, not apply a single global B/W filter.

Generated footage: generated plates often arrive about 40% less saturated and slightly olive against a clean stock reference. Record source saturation and decide whether to match it.

## 7. Flash, strobe, overlay and invert rules

### Flash

- Flash = white overlay that decays. `0.6/0.2` means 60% white on the first frame of a shot and 20% on the second. Heavier hit: `0.85/0.45/0.18` (3 frames). Light hit: `0.5/0.1`. Strobe partner A: `0.7/0.25`.
- Flat white frames use #F7FAFC (not pure #FFFFFF) when matching airy pastel looks; use #FFFFFF for hard strobe whites. Solid black #000000.
- A "white frames" transition is 2 white frames (0.067 s at 30 fps), 1 on the last repeat.
- Fade flash: duration 0.1 s with a chosen colour and amount; dip to a colour 0.15 s.
- Exposure burn ("flashlight"): duration 0.14 s in, 0.07 s out. Brightness 1 + 1.35k, contrast 1 + 0.3k, saturation 1 - 0.45k with k = (1 - u/d)^1.4 (u = time since start, d = 0.33-0.45 s). Darks survive (hair stays dark; eyes and lips never burn out, so cap brightness at 1 + 1.35k). When k > 0.3 add pixel blocks: white 25-40 px squares over the face and hair edge, re-rolled every 2 frames.

### Strobe

- Strobe layer: alternate-frame flash `every 2` frames (colour #fff, amount 1) over a defined window.
- A strobe section alternates two shots every 2 frames (A, B, A, B...). Example: 18 frames = 9 slots; A is a medium shot with a 0.7/0.25 flash on every A, in real time; B is an eyes close-up advancing at 0.35x. Add a short line of text and an RGB split on the first 2 frames.
- Picture alternation every 1-3 frames; in a polarity edit about 35 picture changes in 230 frames.
- Burst: a run of tiny shots on a 4-6 frame grid; plan the sub-shots as separate rows if the editor needs to build them.
- Strobe safety (general guidance, not from the source presets): strobe sections flash many times per second, so keep them short and tell the client when an edit contains them. Accessibility guidance such as WCAG 2.3.1 limits flashing to three flashes per second; platforms may warn or restrict.

### Overlay

- Screen: light leaks, glow, sparkles, flares, bloom. Light leak: amount .55, screen blend, drifting; soft gaussians only, never hard-edged bars (light beams are two soft columns sigma 90 and 160 px sweeping across in 0.4 s, at most 55% opacity).
- Darken blend for double exposure: out = a(1 - o) + min(a, layer) x o. Overlays slide in with horizontal blur 40 x (1 - k), opacity rising and falling. Before blending push the overlay's paper to white (levels (x - 0.12) / 0.7) and feather its edges (smoothstep over 18% of each side) so only ink and shadows show, never a rectangle.
- Multiply: grain, ink, shadows; soft-light: colour washes and grain (grain tiles 4, cell 2, mono).
- Opacity ramps: fade a tint 30% -> 0 over d; fade final element to ~15-18% in an outro.

### Invert

- Invert flips everything under it, graphics included. Duration: 1 frame (polarity strobe inside 1-6 frame shots), 2 frames (impact frames), up to 5-6 frames (a hit).
- Impact frame (2 frames): dark areas and edges turn white, everything else black, keep the accent colour (cyan in the anime edit).
- Intro inversions: background white / silhouette black swap at listed times (e.g. 0.2, 0.4, 0.9, 1.1, 1.8, 2.1, 2.5, 3.2, 3.6 s). Text colour = opposite of what is under each pixel so it stays readable.
- Negative ending: 3 frames of negative with a 3-frame RGB split on the last shot, before black.

### Glitch and distortion

- RGB split: red/cyan channel offset 6 px, decays; or 0-1 px for small hits (set per frame: `RGB split 7,8` means on those two frames).
- Scanlines: 2 px dark lines every 4 px at 14% opacity, applied on named frames only (e.g. 0-8 and 288-296).
- Slice glitch: 6 horizontal bands that slide in over 4 frames. Horizontal smear strips 4-40 px high, lateral offsets up to about 300 px, occasional 25 x 1 px blur; clamp strip height to the remaining rows.
- Block transitions: block sizes about 24, 40, 64, 96 px on a roughly 44 px grid; mix outgoing and incoming subject compositions.
- Mosaic: 30 -> 4 px over the first 0.1 s (from 56 -> 4 over .08 s for a dissolve).
- Halftone cell 7-10 px, strength animated per event (ramp toward 0.8 before a block transition).
- Motion blur inserts: horizontal kernel about 61 px. Bright accents: 1.45 x image + 30, clamped.
- Shake on glitch: `shake 90-93` means frames 90 to 93 only.

## 8. Transitions

| Name | Duration / numbers | Effect |
|---|---|---|
| flashlight in / out | .14 s / .07 s, k = 1 / .8, pixel blocks on in | exposure blow-out where darks survive plus white bloom from the face |
| colour mosaic entry | .2 s, mosaic from 40 px, colour wash (magenta `#c34ca7` shadows to `#f6d2ea` highlights) | colour-washed mosaic entry; fades by ~0.35 s |
| mosaic dissolve | .08 s, 56 -> 4 px | pixel dissolve |
| glitch | .1 s, amount .55 | mosaic tiles plus white wash blocks |
| blur pulse | .12 s, max blur 16, with a thin frame | rising blur plus a thin dark frame (about 5 px grey inset border) over about 0.27 s, a vertical smear on the last 2 frames, then blur-in 0.1 s into the next shot |
| blur in / out | .12 s / .5 s, max 14 / 22 | blur in from / out to a pale wash |
| white | .067 s | solid frames |
| flash | .1 s | fading flash |
| dip | .15 s | dip from / to a colour |
| whip | live both sides, never frozen: outgoing plays to the midpoint, then incoming; first 35% greyed (a x .4 + .33); zoom 1 + 0.1 sin(pi k); slide (k - .5) x -500 px; horizontal blur 120 sin(pi k) + 10 px | whip pan. In a beat edit it straddles the cut: 2 frames before, 1 after |
| slide-out | previous clip keeps playing; push 1 -> 1.08; slide -700 px; horizontal blur 30 -> 170 px; mix to white .97 | exit |
| zoom-blur | zoom with radial blur across 2 frames | cut cover |
| ink / matte wipe | 5 frames; shot B revealed through a moving matte edge (procedural bristle edge, brush-stroke matte, torn paper) | not a blur: both shots stay sharp |
| zig-zag wipe | 3 frames, jagged | hard wipe |
| light-leak transition | smoky diagonal leak bottom-left to white-pink (92%) over ~0.27 s | |
| noise transition | black blotches eat the frame; the next word grows through with a slow-start ease | |
| white wipe | hard white panel from the left, 0.08 s | |

Each cut gets a transition in an effects-heavy edit (strongest on calls and hits), none in a pure hard-cut edit. The transition should hide the cut by being at maximum on the cut frame.

## 9. Graphics layers

| Layer | Key parameters | Notes |
|---|---|---|
| giant letters (behind subject) | size 600 px, x .17-.83, y .55, fill + stroke 8 px | forces a cut-out |
| outline | radius 14 px, blur 3, alpha .95, offset dx 16 dy 6 | offset glow outline of the matte |
| halo | matte offset ~ +10/+6 px, dilated to a ~12 px band | white die-cut halo |
| glow | .14, blur 5 | screen-blended |
| pen contour | distance 12 px, width 4.2, 5 zigzags, blur 2.2 | marching squares on the matte, broken offset strokes |
| glint | from (.18,.4) to (.54,.4), radius 175, .28 s, accent | sweeping star with rays |
| eye glint | horizontal streak at the eye: vertical sigma 6 px, horizontal sigma 380 g + 40 px, core sigma 22; colour (.5,.95,1.0) x 1.4 g, g = (1 - u/.35)^2 | on hits |
| lens flare | core sigma 45 px, streak sigma 9 x 320 px, halo sigma 220 px, 0.3 s; whoosh-in horizontal blur 120 -> 0 px over 0.1 s | |
| doodles | density 0-3 = 0/5/10/16 marks, ring around the silhouette trailing motion, avoid face and text; punch cuts add scratches | ink doodles; kawaii set boils every 3 frames |
| word on face | 3-frame pop; size = clamp(eye distance x .8, 78, 150) px; offset 1.05 eye-units below the eyes | face-anchored word |
| typewriter | 0.05 s per character (about 2 frames per letter), size k .86 clamp 80-140 | bold part + thin part |
| slashes | 2-4 tapered white blades with a coloured edge across the face diagonally, first ~0.4 s | |
| letterbox bars | equal bars top and bottom, each 11.7% of H (84 px at 720), slide in over 3 frames | |
| tint | colour, .3, screen, fades out over d | |
| starburst | centre (0, .4), R about 3.5 x eye distance, 0.6 -> 1 over .08 s then slow growth, ~15 spikes (outer .86-1.2 R, inner .5-.62 R), slow rotation | flat pale fill with thin edge |
| pixel stairs | 3-5 squares 35-45 px in a diagonal staircase top-left, one or two rotated 45 deg | |
| dust | 14 specks per frame | |
| border | hand-inked ragged frame edge | detectors may read it as bars; declare it on purpose |

### Stickers and doodle density

- Count per second and per shot; users judge density. A strong sticker edit sat around 100 stickers per 9.5 s; doodle/sticker scale 290-510 px at 1440 px width, hero sticker 380 px or more; cut-out stickers 340-460 px.
- Sticker pops in over 4 frames with scale steps (1.4, .9, 1.05, 1), then boils, casts a hard offset shadow and slides off face and text boxes. Max live area 25% of the frame, allowed overlap with the subject 25%, rotation +-0.3 rad.
- One sticker every 1/16 note (burst) or hold.
- Add a face-aware rule: stickers never cover faces of the shots they land on or text boxes.

### Collage, panels, polaroids

- Grid pops: panel by panel at the listed frame offsets (triptych +0/+3/+6, 2x2 +0/+2/+4/+6, 3x3 centre +0, corners +2/+3/+4/+6, edges +7/+8/+10/+11 at 24 fps). A panel flashes 55% on the frame it appears. Labels (red boxes) wipe in from +1/+4.
- Polaroids: white border, rotation, shadow; three polaroids at +9/+18/+27 frames over a long detail shot.
- Panel cascade (Physical Body): 3 panels at 2.4:1 landing 3-5 frames apart; mirrored cascade later; split screen (body left, face right); a grow-to-full panel 64% -> 78% -> 82% -> full frame on the third hit.
- Nested-panel tunnel finale: centred panels at 92 -> 82 -> 72 -> 63 -> 55 -> 47 -> 40% of the frame, each a new moment, stars on top, fade to 15%; each panel is fully visible only until the next one lands (9, 5, 2, 6, 7, 16 frames), so the first frames of each window are what the viewer sees.
- Collage card pop: width 400 px x cluster scale x (0.6 + 0.4k), k = easeOut over 0.16 s, rising from +60 px; 6 px pale border, shadow blur 10 at 35%, offset 10/14 px; cluster scale 0.95 -> 1.12; the whole frame drifts +-30 px x, +-12 px y, +-1.5 deg; last 0.15 s zoom x 1.8 with blur into the next section.
- Video inside letters: letters shrink from 1.2x to 1x, a bright clip inside giant type on black or red.
- Marquees: scrolling text band top and bottom (one solid, one outlined), counter such as "LIES 00xxx" (+13 per frame) bottom right with a red dot, viewfinder brackets with timecode, scrolling text wall where every 3rd line sits in a red box.

## 10. Safe zones and the no-edge rule

- No layer edge in frame: every shifted, scaled or rotated layer must be scaled up enough that its edge never enters the frame. Minimum scale >= 1 + 2|dx|/W + 2|dy|/H, plus 0.04 per degree of rotation. Rotate on an oversized canvas (+12% each side) and crop the centre; never rotate a frame-sized image (black corners). Cut-outs whose body touches the source edge must keep that edge outside the frame. This is the single most common visible amateur error in handmade zooms and shakes.
- Never expose mirrored faces or repeated object fragments at transformed frame edges.
- Remove genuine source letterboxing, but do not mistake a dark scene for black bars.
- Text safe margin: keep text inside a 3% margin of the frame at minimum; the compositor shrinks scale-ins around faces and a 3% safe margin.
- Vertical (9:16) platform UI: keep titles and faces out of roughly the top 10% and bottom 20% and away from the right edge column where action buttons sit; verify on the target platform's safe-zone template.
- Faces: titles never cover the eyes or mouth unless the occlusion is the design. When the subject passes in front of a word, hide whole letters deliberately and keep the word legible from the visible part.
- Intentional cropping (a word cut off by the frame) must read as design: giant 3D words cropped on purpose, no artifacts.

## 11. Title choreography

Plan the text before producing footage, then render it as a separate final layer. Footage models do not own text accuracy.

### Title table (one row per text event)

| id | words | frames in / full / out | position (cx, cy, % of frame) | size (% of frame height) | font class | colour / stroke / shadow | animation | layer | beat |
|---|---|---|---|---|---|---|---|---|---|

### Animation vocabulary with numbers

- pop: whole word in over 3 frames with scale overshoot (e.g. 0 -> 1.4 -> 0.9 -> 1.05 -> 1).
- slam: scale per frame [1.3, 0.9, 1.06, 1] over 4 frames; may include shake.
- typewriter: 0.05 s per character (about 2 frames per letter at 30 fps); the word may change weight midway (bold first part, thin rest).
- word-by-word: word 1, then words 1-2, then the rest, one step per beat.
- write-on (handwritten): per-stroke reveal locked to beats.
- fade: 2 frames in (fast) to a slow fade over the whole shot; fade-out over 12-13 frames at the end of a card (frames 460-472 of 474 in the grunge preset).
- stretched to normal: scaleY 2.5 -> 1 in 4 frames.
- letter pop: letters pop every 0.07 s or less with a baseline bounce.
- letter vanish: letters vanish one by one with flicker, the middle letter stays.
- blur to sharp: blur 14 -> 0 over 0.12 s.
- ink in water: words appear and leave like ink.
- punch in: scale 1.8 -> 1.0.
- smear out: vertical smear on the last 2-3 frames.
- parallax: separate layers move at different speeds (e.g. one word at x1.8).
- behind subject: word between plate and subject matte; slow drift and shrink for depth.
- extruded 3D: huge word, intentionally cropped, rising.
- boil: 1-2 px wobble every 2 frames on hand-made type.
- echo: offset colour pass behind the type.

### Rules

- A word must be on screen long enough to read. In a word chain on a strobe or beat grid (TELL / ME / THE / TRUTH at 3, 2, 2, 1 frames at 24 fps) the beat carries it and the sentence is already known; the same preset gives stand-alone words and labels 9 frames (0.37 s at 24 fps) and holds a word 18 frames. For text the viewer must read for the first time, hold longer; rule of thumb (not from the source): about 0.3 s per word, never under 0.5 s.
- One idea per shot. Text arrives on the cut or the beat, not between beats.
- Text scales with the subject: eye distance units for face words, % of frame height for the rest. Give a size range per format and test at phone size.
- Do not reuse the reference's wording in a remix; use the reference's grammar (size, placement, animation, beat relationship). In exact mode unchanged words come from source pixels or traced contours.
- Colour of type may flip with the background underneath (colour = opposite of what is under each pixel) so it stays readable.
- Check coverage of every glyph in the chosen font, including diacritics (Polish: ą ć ę ł ń ó ś ź ż). Fonts for display type often lack them.
- Supplied lyrics: keep wording exactly; align to the selected recording; render in the final text pass; do not paste whole lyrics into generation prompts.
- Replace reference watermarks and creator signatures with neutral subject-specific text.

### Grunge preset envelope (worked example)

At 1620 x 1080: compact title area around x=528..1100, y=462..620. Upper fragment starts near (528, 462), lower fragment near (598, 540), supporting line near y=584. Frames 21-22 oversized broken fragments at about 270 px nominal size; 23-27 partial fragments, ghosted letters, marginal microtype and a small waveform; 28-31 remaining fragments and subtitle appear; 32-34 title resolves into readable text; 35 photocopy hit; 50-64 compact light-on-dark title; 65 short dark glitch. Fit longer words by changing line breaks, size and tracking, never by distorting letterforms.

## 12. Audio hit alignment and mix numbers

- Build a hit table: every audio hit (kick, drop, snare, vocal syllable, riser end, silence) with its time in seconds and its frame. Each hit gets a picture event on that frame or 1-2 frames before it (cuts that lead the beat by about 2 frames feel on-beat; a picture that lags a transient reads late).
- Align by waveform, not by a guessed BPM: place a marker on the loudest transient and scrub to the exact frame. Account for codec delay when muxing.
- Key hit points example (a trap beat): 3.633 (main drop), 4.77, 5.20, 5.56, 7.33, 7.43, 8.00, 8.40, 9.32, 9.68, 10.70, 10.90, 11.13, 12.80, 13.60, 14.52 s. Align the user's track so its main drop lands on the template drop: offset = drop_in_track - 3.633; if negative, pad the start with silence of round(-offset x 1000) ms.
- Three big sub-boom hits (3.495, 4.895, 7.465 s in an 11.8 s edit) land on the biggest cuts; a duck of -6/-7 dB under spoken or lyric lines.
- Cut-on-onset share target: 0.7 or more (cuts within +-2 frames of an onset).
- Mix: limiter with the ceiling set so the encoded file stays at or below -1.0 dBTP true peak. A limiter at 0.84 still peaked +0.4 dBFS after AAC encoding; 0.79 gave -1.2 dBTP (about -8.8 LUFS integrated for a loud short-form edit). Measure the encoded file, not the project.
- SFX layer volume 0.6 relative to music as a starting point; SFX are actual recordings, trimmed and placed on the hit frames.
- Reuse of an original soundtrack: copy the stream, do not re-normalize, and keep the audio start offset equal to the original.
- Tail: keep the song through the last video frame and the planned tail; no `shortest`-style truncation, arbitrary fade or short SFX file that cuts the track.

## 13. Worked numeric recipes from presets

### Grunge editorial (1620 x 1080, 3:2, 474 frames at 24000/1001)

Dense blacks, dirty paper whites, grain sigma 13 (softened 0.6 px), Gaussian softening sigma 1.4 px, vignette .30, halftone 7-10 px ramping to 0.8 at frames 322-328 before a block transition at 329-335, bright accents 1.45 x + 30, horizontal motion-blur kernel 61 px, block sizes 24/40/64/96 on a ~44 px grid, smear strips 4-40 px high up to 300 px offset, dust and scratches time-varying, restrained move 1.00 -> 1.04 or a pan within 3%. Event boundaries at frames [0,15,17,19,21,23,35,37,46,48,50,66,69,71,83,96,112,114,120,122,128,130,138,140,145,160,...]. See style-library.md for the full text.

### Anime impact edit (1920 x 1080, 30 fps, 594 frames, ~129 BPM)

Silhouette fly-in offset (1 - easeOut(t/0.5)) x 0.88 H - 22 t px with 12-sample motion blur; inversion times 0.2, 0.4, 0.9, 1.1, 1.8, 2.1, 2.5, 3.2, 3.6 s; framing scale per inversion [1.0, 1.07, 1.0, 1.05, 0.97, 1.06, 1.0, 1.08, 1.02, 1.1]; cycling background layer every 3 frames; punches +6% decaying over 0.25 s with 18 px shake over 0.18 s; eye glints; flash `a x .3 + .75` for 3 frames; impact frames of 2 frames at 6.80, 9.54, 14.12, 17.79 s; walk background flips every 3 frames (second walk every 2); grade 55% duotone + 45% original; bloom threshold 0.62 radius 22 at 35%; grain sigma 0.018.

### Strobe confrontation edit (1440 x 1080, 24 fps, 366 frames, 160 BPM = 9 frames per beat)

Cuts of 9 frames (one beat) and 18 frames (two beats) with 36-frame holds; opening burst of 1-2 frame shots (flash .6/.2, scanlines on frames 0-8 and 288-296); word pops 220-300 px; strobe 18 frames; counter, marquees, text wall; ends on colour shots with a 3-frame negative then 6 black frames (no grain on the black).

### Chant edit (900 x 720 scaled to the output, 30 fps, 18 fps cadence, hold pattern 2,2,1)

Every cut gets a transition; flashlight burn with pixel blocks; magenta mosaic entry; closer shot with slashes and typewriter; B&W bridge with letterbox bars; eye line at 0.33 H (calls), 0.35-0.42 H (counts), 0.46 H (closer); eye distance 0.09-0.11 W; push-in 1 -> 1.06 through each shot.

### Panel/overlay edit (1920 x 1080, 30 fps, 354 frames)

Black / white frames at 0 / 1-3; silhouette flash frame 4; violet star frame 5 (brightest light source zoomed x3 with stars, screen-blended into the next shot); cascades at frames 28 / 31 / 36 and mirrored at 169 / 172 / 175; split screen from 127; lyric captions: I 59-66, am 67-76, more 77-95, than 96-101, my 102 and 105-109, physical 110-126, body 127-133 (52 px, centre, soft dark halo); tunnel finale from frame 305.

## 14. Gotchas

- A global threshold or grade can ruin faces on medium close-ups; soften per shot.
- Hair blowing across the lips can be keyed to the accent colour (lime lips): narrow the key on that shot.
- Zoom is capped so a source pixel is enlarged at most about 3x; a face close-up beyond that is soft. Plan wide enough source frames.
- A slowed shot that judders lacks frame blending; slowed generated faces and fast limbs ghost when blended; choose per shot.
- A shot whose source runs past the clip end holds the last frame; loop or choose a later in-point.
- An aspect-mismatched take needs intentional crop (subject placement, not a fixed centre crop).
- JPEG/screen-grab sequences are full-range BT.601; encode with an explicit conversion to BT.709 limited range or hues shift by 2-4 levels.
- The hand-inked border detectors read as bars: declare it as intentional.
- Heavy per-frame grain makes huge files (about 29 Mb/s at CRF 20): make a smaller social copy while keeping the master.
- Test every title at phone size and with Polish diacritics before locking the font.
