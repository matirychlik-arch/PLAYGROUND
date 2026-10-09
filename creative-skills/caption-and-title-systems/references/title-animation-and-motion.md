# Title animation and motion language

Contents:
1. Time and animation contract (clocks, lifetimes, keyframes)
2. Title primitives with Premiere and After Effects mappings
3. Motion language table (result to mechanism)
4. Starting recipes with numbers
5. Rules of restraint

The first three sections keep the source contract wording for the rules; each is followed by how to apply it in Premiere Pro and After Effects. Titles are node trees of text, shapes and media with timing; there is no title library and no per-frame script callback, so every motion is expressed as keyframes, sequenced clips, text animators or masks.

## 1. Time and animation contract

| Clock | Meaning | Premiere / After Effects equivalent |
|---|---|---|
| Source trim (`from`, `trimStart`) | Source seconds | Source in point inside the clip (Source Monitor / clip's own timecode) |
| Cut or composition `at` | Whole-project timeline seconds | Sequence time (timeline playhead) |
| Frame child `at` | Seconds after the parent starts | Layer start offset inside a precomp, relative to the precomp's own clock |
| Animation or keyframe `at` | Seconds after the target starts | Keyframe time relative to the layer or clip start (Premiere clip keyframes follow the clip; in AE keyframes live in the comp's time and travel with the layer, and nested comps run their own clock) |
| Inspect at | Whole-project timeline seconds, scenes concatenated | Playhead time on the full sequence |

Worked example: a composition placed at 10 s containing a child at 1 s places that child at 11 s. If the parent lasts 4 s and the child's duration is omitted, the child inherits 3 s. In AE terms: a precomp layer starting at 10 s whose inner layer starts at 1 s appears at 11 s of the parent timeline.

Lifetime rules:

- Lifetimes are half-open `[start, end)`: the start frame is shown, the end frame is not. Ancestors gate descendants: if the parent layer or precomp ends, everything inside it ends. Treat out points as exclusive so back-to-back titles never double-show a frame.
- Explicit child and animation spans must fit inside their owner. A keyframe beyond the end of the layer or precomp never plays; extend the owner or move the key.
- Keyframe times strictly increase, and the chain must end within the node's lifetime.
- An animation is an array of tracks (one chain per property). A keyframe's easing controls its outgoing segment (the segment leaving that key). Equal values at consecutive keys hold a state; a hold key retains the previous value until the next key.
- A finite repeat needs a closed chain (last key equals first key) and is equivalent to unrolled keys; in AE this is a loop expression on a closed chain.
- Offsets add and uniform scales multiply across stacked tracks (a layer scale of 50% under a parent at 200% is 100%). Other duplicate channels are refused: only one owner per replacement property (two things driving the same Position fight each other; in AE do not put keyframes and an expression on the same property by accident).
- Token-level text motion (per character, word or line) is a separate mechanism from whole-block motion; do not drive the same property with both.
- Tracks are evaluated from absolute time, so scrubbing backwards or jumping gives the same pose. Procedural randomness must use fixed seeds; anything depending on wall-clock time or per-frame mutable state is not an animation input (in AE: `seedRandom(n, true)`, never `time`-independent random).
- Pose-only tracks interpolate continuously. A shared counter that drives several bindings uses one held sample schedule at the scene fps for every binding (stepping one track does not quantize the others, the footage, or shader time). Independent animated values are not automatically coupled.
- Inspecting a clip at a time tells you the evaluated parameters, not proof that an effect rendered. Pixel comparisons need matching assets, fonts and runtime. Always judge by rendered frames.

## 2. Title primitives

| Primitive | Mechanism | Premiere / AE |
|---|---|---|
| Move, scale, rotate, fade | Animation tracks on the node, or choreography on a frame | Position / Scale / Rotation / Opacity keyframes (Motion effect in Premiere) |
| Blur and color | Raw tracks on blur or color properties, not pose | Gaussian Blur amount, Fill color keyframes (AE); Premiere via effect keyframes |
| Token entrance | Text motion by character, word or line | AE text Animator with Range Selector; Premiere: build in AE and export a MOGRT |
| Wipe | Edge reveal (frame reveal) or mask with animated width/height | Mask / Crop / Linear Wipe / track matte |
| Outline and draw-on | Text stroke color and width; shaped glyph contours via draw progress; path stroke width; mask reveals | AE Stroke on shape layers, Trim Paths on a path (true path-length draw-on); Create Shapes from Text then Trim Paths for outlined text draw |
| Reflowing resize | Animate a persistent frame's width or height | Responsive Design (Time/Position) in AE, or animate shape size with text anchored; Premiere: background box scales with text via Essential Graphics |
| Fixed-layout transform | Animate a frame or group transform | Parent null / precomp transform |
| State sequence | Sequence children, explicit child timing, or keyframe chains | Stacked clips or layers with in and out points; Sequence Layers in AE |
| 2.5D camera | Top-level z plus a camera | 3D layers plus a camera in AE; fake it with scale and position in Premiere |
| Effects | Ordered effects on a node; animate numeric parameters | Effect stack order matters (top applies first); keyframe the numeric parameter |
| Motion blur | Enabled with samples and shutter | Motion Blur switch and shutter angle (AE comp setting); effects evaluate across blur samples |

Notes that save time:

- A positioned frame can use a center origin so scale and rotation pivot at the middle (in AE, move the anchor point to the layer center, or use Pan Behind).
- Changing frame width or height triggers layout (reflow); a reveal does not reflow. Use a reveal when the text must not move, a resize when neighbors should make room.
- Text uses flat stroke color and stroke width on the text itself. A mask wipe is not a path-length-aware draw; for a real draw-on you need glyph outlines (shape layer) with Trim Paths.
- Path commands in the source support M, L, H, V, C, Q, Z (no arcs or smooth-curve shorthand). A path morph needs identical command skeletons (same number and kind of points) on both shapes; in AE shape-path keyframes need the same vertex count.
- Raw easing accepts named curves or four cubic-bezier handles. Choreography also supports steps, overshoot and bounded spring timing.
- Component-style titles (a reusable lower third) evaluate their inner nodes at local time zero; you place only the instance root on the timeline, and nested timing stays inside. In practice: build each title as its own precomp or MOGRT, drop it on the sequence, never key inner layers from the outer timeline.
- Text animator easing options in the source: linear, ease-out, and house. House is the source's own tuned strong ease-out with no public definition; approximate it with Easy Ease and a high influence (about 80-90%) on the incoming key.

## 3. Motion language (result to supported mechanism)

These are combinations of native features, not additional preset names.

| Result | Supported mechanism |
|---|---|
| Entrance / hold / exit | Frame motion with enter, settle and an end-anchored exit |
| Pop / overshoot / spring | Choreography easing objects, or explicit scale keys |
| Staggered cards | A timeline stagger with an each-offset; targets are immediate child frames |
| Word / character / line arrival | Text motion by word, character or line; one text clip |
| Wipe / phrase highlight | Clip plus reveal, or animated mask geometry |
| Counter and bar | One timeline leaf with targets: transform bindings plus an explicit counter |
| Slider / cursor / target coupling | Shared progress targets, or identical authored key times |
| State replacement | Timed sibling clips, opacity tracks, or sequence transitions |
| Repeated movement | Finite closed animation chain with repeat |
| Connector reveal / morph | Mask wipe, or matching path data with a morph progress value |
| Camera move / parallax | Parent frame transforms, or camera with top-level z |
| Particles / glitch | Finite generated shapes and deterministic authored keyframe tables |

Limits to remember: a mask wipe is not a path-length-aware stroke draw (shaped glyph outlines with a visible stroke support a true draw progress). Shared counters use held scene-fps samples for all coupled bindings, not a live text callback. A color tween is a solid-color change; gradient stencils need separate geometry and mattes. None of these mappings implies object identity across scenes: a title that "continues" into the next scene must be rebuilt there, or live on a single continuous layer.

Entrance / hold / exit in Premiere and AE: three keyed segments on one layer. Key the entrance over the first N frames, hold with two equal keys, key the exit over the last M frames anchored to the layer's end. If the title is retimed later, an end-anchored exit must be re-anchored (compiled exits in a scripted pipeline recompute on rebuild; hand-edited keys in an editor do not re-run any script).

## 4. Starting recipes with numbers

These are starting points of mine, derived from the web-motion numbers in the same source family (micro-interactions 150-300 ms, complex transitions up to 400 ms, exits 60-70% of the entrance, ease-out on enter and ease-in on exit, stagger 30-50 ms per item). Adjust to the edit's pace.

At 30 fps:

| Element | Entrance | Hold | Exit |
|---|---|---|---|
| Hook title (3-6 words) | 8-10 frames (0.27-0.33 s), ease-out, slide up 24 px and fade, or word-by-word 3-frame stagger | until the first body word starts | 5-6 frames, ease-in, fade or slide down 12 px |
| Section title card | 9-12 frames, mask wipe or scale 92% to 100% with fade | 1.0-1.8 s | 6-8 frames |
| Lower third | 8 frames slide in from the left plus fade; plate first, text 3 frames later | 2-3 s | 5 frames, reverse order |
| Pop (emphasis word) | scale 0% to 108% in 5 frames, settle to 100% in 4 frames | as needed | cut or 4-frame fade |
| Counter | count up over 20-30 frames with ease-out; hold the final value | 1 s | fade |
| Speech caption (static) | none (hard cut in and out) or 3-frame fade | cue duration | none |

Word-by-word entrance: per-word start pose opacity 0, y +16 px, scale 96%; stagger 2-3 frames per word; ease-out; overlap so the next word starts before the previous settles. Over 6 words that is under half a second of motion.

Stagger: 30-50 ms (1-2 frames) between list items; longer reads as slow.

Never let a title's entrance finish after the viewer needs to read it: the readable state must hold for at least the time to read it (about 0.3 s per word for short lines, plus 0.5 s).

## 5. Rules of restraint

- Every animation answers "what does this communicate?" (hierarchy, narrative order, feedback, state change). "It looked cool" means drop it.
- Use ease-out on enter and ease-in on exit; avoid linear except for continuous movement (a ticker, a progress bar).
- Animate transform and opacity as the primary vocabulary. Blur, glow and color shifts are seasoning.
- One signature motion style per video. Do not mix pops, wipes and slides in one title set; choose one entrance family and one exit family.
- If you cannot finish a motion properly inside the available time, ship a clean static title instead of a half-finished animation.
- Reduced complexity beats cleverness on mobile screens: the video plays small, so fine details and thin strokes vanish.
- Keep titles and captions from competing: when a title is on screen, suppress speech captions in that region or move one of them.
- Deterministic randomness only (fixed seeds), so a re-render matches.
