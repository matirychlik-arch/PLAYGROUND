---
name: viral-effects-library
description: Seed library of 87 viral video effects (hooks, reveals, transitions, surreal, product, painting recreations, style looks), 18 product camera-move master prompts and 130+ motion-transfer preset names, plus the method for turning any effect description into a ready-to-paste prompt for KLING, Seedance 2 (EN + ZH) or Higgsfield Cinema Studio, and for chaining effects into a 10-15 s hook sequence. Use it whenever the user wants a scroll-stopping opening, a wow effect, a transition idea, a product camera move or "something viral" for a short video, even if they never name the library. Trigger on - efekt wiralowy, viralowy efekt, hook, haczyk na start, otwarcie filmu, przejście, transition, efekt wow, surrealistyczny efekt, klon, zniknięcie, topnienie, ruch kamery produktu, najazd, obrót produktu, whip pan, crane, orbit 360, zrób efekt jak z TikToka, pomysł na hook do reklamy, prompt do KLING, prompt do Seedance. For editing or re-casting footage that already exists (swap a person or product, make N variants of an ad) use video-edit-prompting instead; for a full multi-shot cinematic prompt from a scene idea use seedance-director or cinematic-prompt-builder.
---

# Viral Effects Library

A seed library of video hooks and effects plus the recipe that converts an effect description into a generator prompt. The catalog gives the idea (what the viewer sees); this skill adds the parts a video model needs (subject lock, beats, camera, end state).

## When to use / when not

Use when:
- the user needs an opening hook, a transition, a reveal, a surreal moment or a product camera move for a short video or ad;
- the user names an effect ("Vanish", "Eyes in", "klon", "zniknięcie") or describes one and wants the generator prompt;
- the user wants 2-3 effects chained into a 10-15 s hook sequence;
- the user asks which motion-transfer idea fits their clip (preset names in `references/genjutsu-motions.md`).

Do not use when:
- footage already exists and parts of it must change (swap person, product, background, make variants): use `video-edit-prompting`;
- the user wants a full scripted multi-shot scene with dialogue: use `seedance-director` (Seedance) or `cinematic-prompt-builder`;
- the user needs a still image only: write an image prompt, and use this skill only for the start frame of a clip.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

1. Subject: a person, product or character, ideally with a reference image. No image means describe identity anchors in words.
2. Goal: hook (0-3 s), transition, reveal, product showcase, or style look. Default: hook.
3. Tool: KLING, Seedance 2, Higgsfield Cinema Studio, other. Default: write one tool-neutral English prompt and add a KLING and Seedance variant.
4. Duration and aspect: default 5 s for a single effect, 9:16 vertical, 1080p. Product camera moves default to 6 s.
5. Audio: default silent (add sound in the editor). Ask only if dialogue or lip-sync is wanted.
6. Chain: single effect or a sequence (then also ask what the last frame must hand off to).

If the user gives only a vibe ("coś szalonego na start reklamy kremu"), pick 2 candidate effects from the catalog, name them with their original descriptions, recommend one, and write the prompt for it. Do not ask 6 questions first.

## Workflow

1. **Pick the effect.** Open `references/effects-catalog.md`, go to the group matching the goal (1 hooks, 2 reveals, 3 transitions, 4 surreal, 5 product, 6 painting recreations, 7 style looks). For a product camera move go to `references/camera-moves.md`. For "copy this motion onto my character" go to `references/genjutsu-motions.md`. Quote the catalog description back in one line so the user confirms the idea.
2. **Check feasibility for the tool.** Effects that need two people interacting, perfect text, long takes (over 10 s) or exact physics are risky; say so and simplify (see QA checklist).
3. **Fill the 7-slot recipe** (below) from the description. Convert every abstract phrase in the description into a visible physical event: "reality warp" becomes "the buildings behind her bend and ripple like liquid while she walks at normal speed".
4. **Write the camera sentence separately** from the action. One move per clip (push, orbit, whip pan, crane, locked). Camera vocabulary and tested 6 s master prompts are in `references/camera-moves.md`.
5. **Set the end state.** Last second = stable, readable frame. For a transition, the end state is the first frame of the next scene. For a loop, the end state equals the start state.
6. **Adapt to the tool** (adapters below), then run the QA checklist.
7. **For a chain**, write one prompt per clip and a handoff table (see Hook sequences).

### The 7-slot recipe (effect description to generator prompt)

| Slot | What to write | Why |
|---|---|---|
| 1 Subject lock | Who or what, 3-5 identity anchors from the reference (face, hair, outfit, product shape, label text), "same person throughout" | Effects stress identity; naming anchors keeps the face and label from drifting |
| 2 Start state | The first frame in one or two sentences: place, light, subject position | Gives the model a fixed point before the effect starts |
| 3 Action beat | The effect as 1-3 timed beats with verbs ("0-1 s: she stands still; 1-3 s: her body vanishes and the clothes fall flat") | Models follow ordered, concrete events better than adjectives |
| 4 Camera | One sentence, one move, stated separately ("The camera slowly pushes in at chest height.") | Mixed camera and action sentences cause the camera to wobble or drop the effect |
| 5 End state | What is on screen in the final second and that it holds still for 0.5-1 s | Clean cut point for editing and chaining |
| 6 Format | Duration, aspect ratio, "no text, no captions, no watermark", audio on or off | Prevents invented text and sets the grid |
| 7 Avoid | 3-6 items: morphing, extra limbs, duplicate subjects (unless the effect is clones), warped text | Puts the failure modes of the effect in a negative field or a closing line |

Lock first, effect second, camera third, end state last. The order matters because most models weigh the first sentences most.

### Loop and transition notes

- Loop: write the end state as the start state ("the frame returns to the opening pose and framing") and cut the last 2-3 frames in the editor for a clean crossfade.
- Transition out: end on a shape, color or motion direction that the next clip can start on (a doorway, a spinning object, a flash of white).
- Transition in: start the clip from the previous clip's last frame (extract it, use it as the start image).
- Whip, flash and eye dives hide a cut; use them when the two scenes differ in location or lighting.

## Hook sequences (chaining effects)

A 10-15 s hook is three beats, each a separate clip joined by a handoff:

| Beat | Time | Effect group | Job |
|---|---|---|---|
| A Hook | 0-3 s | 1 hooks or 4 surreal | Interrupt the scroll with one clear impossible event |
| B Bridge | 3-6 s | 3 transitions | Move from the gag to the product or setting without a hard cut |
| C Reveal | 6-12 s | 5 product or a camera move | Show the product clean, label readable |
| D Close | 12-15 s | locked hold or style look | CTA frame, logo, text added in the editor |

Rules for chaining:
1. One hero effect per clip. Two big effects in one 5 s clip fight each other.
2. The end state of clip N is the start state of clip N+1. Extract the last frame of N and use it as the start image of N+1, same aspect ratio and same lighting description.
3. Keep subject lock text identical across clips (copy-paste the slot 1 sentence).
4. Put on-screen text, logos and prices in the editor, never in the generator.
5. Style looks (group 7) are applied last to the finished cut or to every clip with the same words, never to some clips only.

Output a handoff table with columns: clip, effect, start state, end state, duration.

## Output format

Single effect: one card per effect.

````markdown
### <Effect name> (<group>)
Catalog idea: <original description, one sentence>
Tool: <KLING | Seedance 2 | Higgsfield | neutral>  |  <duration> s  |  <aspect>  |  <silent/audio>

```text
<ready-to-paste prompt in slot order 1-7, English>
```
Negative prompt (if the tool has the field): <slot 7 items>
Start image: <what to supply or generate>
Edit notes: <speed ramp, cut point, loop, text added in editor>
````

Sequence: the cards above, preceded by the handoff table. Seedance 2 and bilingual requests also get a Chinese copy of the action and camera slots (see adapter).

## Tool adapters

- **KLING**: image-to-video with the prepared start frame; plain action verbs, one subject, camera move in its own sentence; move the avoid list to the negative prompt field; if your version has an end-frame slot, supply the end state image for transitions. Keep clips 5 s for single effects; effects with two characters interacting are a poor fit, generate the characters separately.
- **Seedance 2**: accepts English and Chinese prompts; write the English prompt, then a Chinese copy of the action and camera slots (Chinese often reads more precisely for motion verbs). Use time-coded beats ("0-2s", "2-4s"). Reference images and clips are addressed by tags such as @Image1 and @Video1 where the interface supports them. The product camera-move master prompts were written for it (6 s, silent, 1080p, 3:4 or 9:16).
- **Higgsfield Cinema Studio**: the effect names in `references/effects-catalog.md` match an effects gallery there, so the preset by the same name can be selected and fed your image; for custom ideas paste the slot prompt. Motion-transfer names in `references/genjutsu-motions.md` need your own reference image plus a driving clip.
- **Nano Banana Pro** (image only, not a video tool): use it to prepare the start frame, the end frame, a clean product plate (shared start-frame prompt in `references/camera-moves.md`) or a character sheet. Give exact text strings in quotes if text must appear in the frame.
- **Premiere Pro / After Effects**: do speed ramps, match cuts, loop crossfades, text, logos, sound and the group 7 style looks (as grades and overlays) there. Generators handle one clean effect; the editor assembles the sequence.
- **Figma / Illustrator / Photoshop**: poor fit for motion; use them only for end cards and thumbnails.

Chinese slot template for Seedance 2 (translate the English action and camera slots; keep names and label text in the original language):

```text
主体：<身份锚点，3-5 个>，全程同一个人。
动作：0-2秒 <起始动作>；2-4秒 <特效动作>；4-5秒 <稳定画面>。
镜头：<单一运镜，例如缓慢推近>。
结尾：最后一秒画面静止稳定。无文字，无字幕，无水印。
```

## QA checklist

- [ ] The prompt names the subject anchors (face, outfit or product label) once, at the start.
- [ ] The effect is written as visible physical events with verbs, not adjectives or the catalog's "Built for" sentence.
- [ ] Exactly one camera move, in its own sentence.
- [ ] The last second is a stable frame; a chained clip ends on the next clip's start state.
- [ ] No on-screen text requested from the generator unless it is one short word; text goes in the editor.
- [ ] Clones, crowds and two-person interactions use a clip of 5 s or less and a locked camera; otherwise expect identity drift.
- [ ] Duration fits the tool (single effect 5-6 s; sequences are separate clips).
- [ ] Avoid list present, and it does not forbid the effect itself (do not write "no duplicates" for Clones).
- [ ] Product clips keep label text readable; if the model mangles it, regenerate with a tighter push-in or add the label in the editor.
- [ ] Output block is ready to paste, with the tool, duration and aspect stated.

## References

- `references/effects-catalog.md`: all 87 viral effect descriptions verbatim, grouped by use, with an alphabetical index. Read in step 1 to pick or confirm an effect.
- `references/camera-moves.md`: the 18 product camera-move master prompts verbatim plus the shared start-frame prompt. Read for any product shot, camera move, rotation, light or particle effect.
- `references/genjutsu-motions.md`: motion-transfer and object-replacement preset names (curated, trending, new) and when to choose which operation. Read when the user wants to copy a motion or swap a subject in a reference clip.
- `references/marketing-templates.md`: names and types of 231 motion-graphic and 418 product-shot templates, usable as look vocabulary. Read when the user wants an art-direction phrase or a style anchor.
- `references/effect-to-prompt-examples.md`: six worked conversions (catalog description to final prompt, with a Chinese copy and a 3-clip chain). Read before writing your first prompt in a session or when the output feels vague.
