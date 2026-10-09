# prompts-and-blocks.md: prompt templates for the style key, assets and the 10-second block

Contents
1. Conventions
2. Asset prompts (characters, locations, props)
3. The block: one 10 s clip of FIVE hard-cut shots (template)
4. Kids block: FOUR cuts
5. Shot grammar (size/angle vocabulary, variety rules, action grammar, audio line)
6. Route B: per-shot keyframes when your video model cannot do multi-shot
7. Retry ladder and post-generation checks

## 1. Conventions

All image and video prompts are in **English**. Only the narration switches to the user's language. `{STYLE}` = the ONE style formula from `style-packs.md`, pasted byte-identical everywhere. The style key prompt lives in `style-packs.md` section 0.

Order of generation: style key -> assets (using the key as a reference) -> shots/clips (using the assets as references). Never generate a clip or still from the style key alone: every shot is a full staged scene composed from the approved assets, never a lone object on a blank background.

Pass the aspect ratio EXPLICITLY on every generation (default 16:9 for YouTube, 9:16 for TikTok/Reels/Shorts); it does not inherit from the style key.

## 2. Asset prompts (always small, 1k-class; style key attached as reference; {STYLE} verbatim)

- **Character (2:3):** "Full-body character centered on a plain flat solid-color background, in THIS EXACT style: {STYLE}. Character: {desc - distinctive, readable silhouette}. No text, no watermark."
- **Location (chosen aspect):** "{interior/exterior} ... in THIS EXACT style: {STYLE}. {key furnishings + ONE named anchor object with a position}. Empty room - no people, no characters, no figures. Wide establishing. No text, no watermark."
- **Prop (1:1):** "A single isolated prop centered on a plain flat solid-color background, in THIS EXACT style: {STYLE}. Object: {desc}. No hands, no scene, no other objects. No watermark."

Roster rules:
- Locations: MULTIPLE, not one. Enough distinct locations that none carries more than about 2 consecutive blocks (a 2 min / 12-block video wants 4 to 6). For each, 1 to 2 coverage angles (reverse, lateral, detail crop) so blocks in the same place are not the identical plate.
- The through-line object always gets its own prop asset.
- Optional variety inserts (esp. Kids): a subject on a clean solid color card, a pop-up diagram, an anthropomorphized object with a face.
- Long-form characters that age: one asset PER ERA, identity chain (later variants generated WITH the first incarnation attached: "the SAME person as in the reference, now {era changes}"); see `format-variants.md`.
- Keep at most 7 reference images per generation call; plan the roster so no shot needs more (location, then characters, then props).

## 3. The block: ONE 10 s clip of FIVE hard-cut shots

Use this when your video model follows a multi-shot prompt in one clip. Fill {} and paste. References in order: location, characters, props.

```
Style: {STYLE}; {MOTION} - the visual style is EXACTLY as in the reference images, same rendering, same surface treatment.
PALETTE LOCK: use ONLY the colors and the background treatment of the reference images ({e.g. flat off-white/clean webcomic background}). Do NOT introduce any new or foreign colors, no colored/gradient/painted backgrounds that aren't in the references, no recoloring of characters or objects.
A single 10-second scene of FIVE hard-cut shots. Do NOT open the video on any reference image or show a sheet/swatch - stage everything fresh, matching characters, room, colors and background to their references. Characters only emote and gesture, they do NOT talk. Motion starts on frame 1 (no opening freeze).
REFERENCES (look, identity, palette): @Image1 = LOCATION ({desc}). @Image2 = {CHARACTER A} ({desc}). @Image3 = {CHARACTER B}. @Image4 = {PROP}.
SHOT 1 - 0.0s to 2.0s - {SIZE+ANGLE}: {beat}.
HARD CUT.
SHOT 2 - 2.0s to 4.0s - {DIFFERENT SIZE+ANGLE}: {beat}.
HARD CUT.
SHOT 3 - 4.0s to 6.0s - {DIFFERENT SIZE+ANGLE}: {beat}.
HARD CUT.
SHOT 4 - 6.0s to 8.0s - {DIFFERENT SIZE+ANGLE}: {beat}.
HARD CUT.
SHOT 5 - 8.0s to 10.0s - {DIFFERENT SIZE+ANGLE}: {payoff}.
Five hard-cut shots at 2.0s, 4.0s, 6.0s and 8.0s, no dissolves, no fades. {MOTION}, continuous motion within each shot, never freezes.
AUDIO: {diegetic SFX only} - no voice, no narration, no music.
NEGATIVE: opening on a reference image, a sheet/swatch or a static first frame, leading freeze, dissolves or fades, NEW or foreign colors, colored/gradient/painted background not in the references, recolored characters, style drift, extra people, cloned characters, characters talking, lip-sync, on-screen text, captions, photorealism{2D-ONLY: , 3D render}, watermark.
```

**About 2 s per shot is the law: no shot longer than 2.5 s.** A frame hanging 3 to 5 s reads as a slideshow, and every shot needs visible ACTION, not a held pose. Degradation: a block that fails generation twice at 5 cuts drops to 4 (2.5 s grid); that block only.

{MOTION} by style family: flat 2D (webcomic, stick figure, flat cartoon, Editorial collage): `simple limited animation on twos` (collage has its own token in `style-packs.md`). Dimensional (Paper Diorama, papercraft, Fluffy Toy, claymation): `smooth simple handcrafted motion, subtle stop-motion feel`, and drop `3D render` from the NEGATIVE.

## 4. Kids block: FOUR cuts of 2.5 s

Pattern `WIDE establishing -> CU on the character (reaction beat) -> ECU on the detail/object -> MEDIUM (resolution)`, order varied every block (never the same sequence twice):

```
SHOT 1 - 0.0s to 2.5s - WIDE: {scene establishing beat}.
HARD CUT.
SHOT 2 - 2.5s to 5.0s - CLOSE-UP on {character}: {reaction to the narrator}.
HARD CUT.
SHOT 3 - 5.0s to 7.5s - EXTREME CLOSE-UP on {detail/prop}: {the thing itself}.
HARD CUT.
SHOT 4 - 7.5s to 10.0s - MEDIUM: {resolution / celebration beat}.
```

Everything else from section 3 applies (staggered entrances, one camera behavior per shot, settle at the end, impact beat, SFX 1:1). Kids audio line: playful diegetic SFX (sparkle dings, boings, pops, giggling bells, whooshes on hops), 2 to 4 cues tied to motions + a soft ambient bed, still "no voice, no narration, no music". If a 4-cut block fails twice, drop THAT block to three cuts.

## 5. Shot grammar

Vocabulary: sizes WIDE / MEDIUM / CU (close-up) / ECU (extreme close-up); angles eye-level / low / high / overhead (top-down) / lateral / macro; OTS (over the shoulder).

Variety rules (stop the "samey" problem):
- EVERY shot in a block differs in SIZE and ANGLE from its neighbours (MEDIUM, CU, low WIDE, ECU, overhead...). Adjacent shots never share a size.
- Only the FIRST block of a new location may open on a full establishing WIDE; later blocks in the same location open on a fresh close/medium/coverage angle. Never re-establish the same wide.
- At most 2 consecutive blocks per location, then move: a new location, a coverage angle, or a variety insert. Vary the character's distance and screen position; never park them back at the opening framing.
- **OTS is valid only when a named on-screen character's shoulder/head is intentionally visible in the foreground.** In object-only, diagram, empty-location or characterless shots never write OTS (the model invents a person); use overhead, low/high, macro or lateral.
- **Every block carries at least ONE impact beat** (a slam, stamp, snap, whip-pan hit, collapse). Name it in a SHOT line and echo it in AUDIO; reference-grade explainers land an accent about every 3 s.
- SHOW WHAT THE LINE NAMES: each block's shots stage the concrete nouns of its own VO line.

Action grammar (all styles): write SHOT beats as pure CHOREOGRAPHY. The {STYLE} formula owns the look, so no style, color or material words inside beats. Elements enter STAGGERED ("A, then B, then C", never simultaneously) with landing verbs (snaps into place, stamps down, drops with a bounce, settles). Exactly ONE camera behavior per shot, stated once (slow push-in / static / gentle drift / whip); two moves in one cut reads as AI soup. The FINAL shot eases into a stable, still micro-moving final frame (settled, not frozen).

On-screen text is unreliable, so use SYMBOLS (warning sign, $, check, cross) and let the VO carry words. Sole exception: the Paper Diorama letterpress prop label (`style-packs.md` section 4).

AUDIO line per block: SFX follows choreography 1:1. Every motion verb gets at most ONE cue, 2 to 4 cues per block + one room-tone bed (whooshes on moves, a stamp hit on the impact beat, ticks on data steps, sparkles/dings for Kids, ambient of the place). Nothing sounds that did not move. Percussive, never musical.

## 6. Route B: per-shot keyframes (when the video model cannot do multi-shot in one clip)

For each of the 5 (or 4) shots of a block, make a keyframe image then animate it for about 2 s.

Keyframe image prompt (Nano Banana Pro or any image model that accepts reference images):
```
{STYLE}. Compose this shot from the attached references: @Image1 = LOCATION, @Image2 = {CHARACTER}, @Image3 = {PROP}.
{SIZE+ANGLE}: {the moment at the START of the beat, one frame, characters mid-action not posing}.
Same colors, same background treatment, same character designs as the references. No text, no watermark, no extra people.
```
Animation prompt (KLING or Seedance 2, keyframe attached as the first frame, 2 to 3 s):
```
{ONE subject} {plain action verb phrase}, then {second action}. Camera: {one move, in its own sentence}. {MOTION}. Motion starts on frame 1. No talking, no text, no style change.
```
Assemble in Premiere with hard cuts at the 2 s grid (2.5 s for Kids); trim each clip to its slot, no dissolves. Seedance 2 accepts English and Chinese prompts; KLING behaves best with one subject, plain action verbs and the camera move in a separate sentence.

## 7. Retry ladder and post-generation checks

- Safety-filter false positives are common and probabilistic. Ladder: resubmit as is; then reword (drop `child`/`kid`, avoid tight animal-face close-ups, calm the pose); then swap the beat's framing; finally re-stage as an empty atmospheric location. Never drop a block and never deliver a gap.
- Style drift or realism creeping in: strengthen the shared STYLE and NEGATIVE text and regenerate ONLY that clip. Two identical failures mean the prompt must change.
- **Count the cuts that came back; video models under-deliver.** Example: 8 blocks x 5 cuts came back with 29 visible cuts (about 4 s per frame). Check:
  ```
  ffprobe -v error -select_streams v:0 -show_entries frame=pkt_pts_time \
    -of csv=p=0 -f lavfi "movie=blockNN.mp4,select=gt(scene\,0.3)" | wc -l
  ```
  A block with fewer cuts than asked, or any shot of 3 s or more, is regenerated ONCE with the cuts spelled out shot by shot. If it still under-delivers, keep it and note which blocks are slow. On FLAT looks the count under-reports (pixel change between similar compositions never crosses the threshold): re-measure with `scene,0.15` and treat a low count as a suspicion, not a verdict.
- No leading freeze: every block demands motion from frame 1. A block whose opening looks static is regenerated, never shipped as a still that starts playing a second later.
- Identity and palette check: compare each clip against its asset sheets; characters recolored or redesigned = regenerate.
