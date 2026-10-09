---
name: video-edit-prompting
description: Write prompts that EDIT an existing video instead of generating a new one - replace a person, product, garment, background or on-screen text while preserving the cut, timing, camera, lighting and audio; copy motion from a driving video onto a new character; multiply one ad into N versions; recreate an ad for another market, language or cast. Use it for KLING motion and element edits, Seedance 2 reference-video modes, Higgsfield Genjutsu and Runway-style video-to-video, even when the user never says "prompt grammar". Trigger on - podmień osobę w filmie, zamień produkt w reklamie, zmień tło w wideo, edytuj wideo AI, wariacje reklamy, 10 wersji tej reklamy, pomnóż reklamę, przerób reklamę na rynek niemiecki, wersja na inny rynek, zmień język reklamy, nowy hook do gotowej reklamy, przenieś ruch na postać, motion transfer, video to video, v2v, zachowaj montaż i kamerę, podmień twarz, zmień ubranie w filmie. For text-to-video or image-to-video from scratch use seedance-director or cinematic-prompt-builder; for hook and effect ideas use viral-effects-library.
---

# Video Edit Prompting

Write the prompt that tells a video-to-video model what to change and what to leave alone. An edit prompt is a contract: a short list of operations plus an explicit lock on everything else (cuts, timing, camera, lighting, text, audio). Generators drift wherever the lock is vague, so the lock is written as carefully as the change.

## When to use / when not

Use when:
- a finished or shot clip exists and the user wants parts of it replaced, added, removed or restyled with the rest unchanged;
- one source ad must become several versions (products, cast, backgrounds, text, markets);
- the user wants the motion or camera of a clip copied onto another person, character or animal;
- an ad must be re-shot as new footage for another market, language or cast (recreate);
- only the hook or only the CTA of an ad must be replaced.

Do not use when:
- there is no source video: write a text-to-video or image-to-video prompt (`seedance-director`, `cinematic-prompt-builder`) or pick a hook from `viral-effects-library`;
- the user only needs dubbing, translation of existing footage or captions: use a dubbing/subtitle tool or the editor;
- the change is a simple trim, speed ramp or color grade: do it in Premiere Pro or After Effects.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

Collect everything missing in one message, right after the source arrives:

1. The source video: length (check your tool's range; the reference workflow took 4 to 30 s), aspect ratio, has audio, has captions or on-screen text.
2. The edit: what changes, per target, and the ordered list of outputs or an explicit N. Default N = 1.
3. References: images for replacements (all, some or none). Multiple images are mapped one image to one target.
4. Resolution: 720p default (faster); 1080p on request.
5. The tool: KLING, Seedance 2, Higgsfield, Runway-style, other. Default: write the Seedance-style tagged prompt, then add the adaptation.
6. For a market version: target market, spoken language, product facts you may use, lines to say exactly.

Do not ask again for what is explicit. If references are promised, wait for them before generating. If the target, time range, reference mapping or list-to-output assignment is ambiguous, ask one bundled mapping question; do not guess.

## Workflow

### Step 1. Choose the mode

| The user says | Mode | Reads |
|---|---|---|
| "swap the product / person / background / garment, keep everything else", "N versions with different X" | Edit (replace/preserve) | `references/prompt-grammar.md`, `references/variant-matrix.md` |
| "make the same ad for Germany / in English / for Gen Z / with a local cast" | Recreate | `references/recreate.md` |
| "new hook only", "new CTA only" | Hook or CTA only | `references/recreate.md` section 5 |
| "make my character do the dance in this clip", "copy the camera move" | Motion transfer | Decision rule below |
| "put my product into this clip", "swap the character, keep the scene" | Object replacement | Decision rule below |
| Request fits both edit and recreate | Ask one question | Keep the original footage and change named targets, or re-shoot as new footage? |

### Motion transfer vs object replacement

| | Motion transfer | Object replacement |
|---|---|---|
| Keeps from the source | Choreography, gestures, timing, camera motion | The whole scene: shots, camera, setting, other people, lighting, audio |
| Changes | Who performs it (and usually the look and place from the reference) | One named target (object, product, garment, character) |
| Inputs | One driving video + reference image(s) of the new subject | One source video + reference image(s) of the replacement |
| Trigger words | copy, repeat, mimic, reproduce, transfer motion, dance, gestures, camera movement | replace, change, swap, put X instead of Y |
| Prompt style | Short brief: whose motion, onto whom, what stays | Edit grammar from `prompt-grammar.md` |

The user's requested operation outranks the preset or example it came from: an example built as a replacement can be used to copy motion, and the reverse. Use the user's own reference images, never an example's characters. If there are no reference images, say motion transfer and replacement need them (offer to make them with an image model such as Nano Banana Pro) instead of proceeding. Preset names are listed in the genjutsu-motions reference of the `viral-effects-library` skill.

### Step 2. Check the source

- Length inside the tool's range; do not trim, loop, freeze or stretch a source to fit. Cut long sources in the editor and run each piece separately.
- Render length = the next whole second above the source length, aspect ratio = the source's; the edit model renders silently and the original audio goes back on in finishing (`references/finishing-and-qc.md`).

### Step 3. Build the timed scene caption

Write (or obtain from a scene-analysis tool) a shot list: start-end seconds, who and what is on screen, camera move, on-screen text. Every timing in the prompt comes from this caption. Use whole seconds unless a real boundary needs one decimal. If the analysis is missing a requested target, redo it once; if it is still unusable, stop.

### Step 4. Plan the outputs (variant matrix)

Fill the variant table (`references/variant-matrix.md`): one row per final video, target with a unique plain-language anchor and visible range, replacement, clothing override, text edit. Zip ordered lists by position; never form a Cartesian product. N counts final videos, not assets.

### Step 5. Get the references

User images keep one fixed order: `@Image1..@ImageK`. A person image is a complete-look reference by default (face, hair, body, clothes, shoes, accessories). If an adult replacement has no image, make a stand-in person image (`references/variant-matrix.md` section 5). Never invent identity details for an image you cannot inspect; ask.

### Step 6. Write one prompt per output

1. Pick the template: **DETAILED** for any person identity replacement, multiple identity swaps, a swapped subject across several shots, interaction with props/reflections/shadows, three or more edit categories, or when asked for detail. Otherwise **COMPACT**. COMPACT is forbidden for a person identity replacement. Do not announce which one you used.
2. Write the operations with the sentence bank below, one operation per sentence.
3. Add the lock (what stays), the source-text preservation block, and for people the exclusion sentence.
4. Resolve every condition before writing: the finished prompt contains no "if", no alternatives, no options.
5. Validate with the list in `references/prompt-grammar.md` (Part B9).

### Step 7. Generate, finish, report

Submit one output at a time in list order; retry a failed output once; never duplicate a pending one. Then restore the source audio, trim to the exact duration and run the QC gates (`references/finishing-and-qc.md`). Report completed/total, resolution, duration and whether audio was restored.

## What stays locked, what changes

Locked by default, and named in every prompt: shots and cuts, camera moves, framing, composition, unmapped performers, setting, held and environmental props that are not targeted, lighting, color grade, pacing, timing, display aspect ratio, default audio, every caption, subtitle, label, logo and other on-screen text.

Changes only if targeted: the named person, product, object, garment, background, attribute, or an explicitly requested text edit.

Hard rules (each exists because models otherwise guess):
- Describe the replacement by its image tag and say "from @ImageN"; never say a replacement look comes from `@Video1`. Otherwise the model reuses the old person.
- A person replacement covers every appearance: through cuts, entrances, exits, occlusions, motion blur, transitions, reflections and shadows. Name each mapping separately; never write "replace everyone".
- The person image owns the complete look including clothes and accessories; the old wardrobe has no authority unless the user asked to keep named source clothing. Separate garment image or explicit clothing instruction overrides the clothing only.
- Preserve every untargeted caption and text. Never auto-remove, add or regenerate captions.
- Timings come from the caption, not from guesses; segments tile the full duration with no gaps or overlaps.
- Keep the prompt within about 3,900 characters (the reference limit; check your tool) and cite each attached image at least once.
- Shared lock sentences repeat verbatim across variants; only the operation and the alias change.

## Output format

Deliver the plan and then ready-to-paste prompts, in this shape:

````markdown
## Plan
Mode: <edit | recreate | hook/CTA | motion transfer | object replacement>   Tool: <tool>   N: <n>   Resolution: <720p|1080p>
Source: <length> s, <aspect>, audio <yes/no>, text/captions <yes/no>

| # | Operation | Target (anchor + range) | Replacement | Clothing override | Text edit | Output name |
|---|---|---|---|---|---|---|

References in order: @Image1 = <what>, @Image2 = <what>

## Prompts
### Output 1 - <name>
```text
<finished prompt, nothing else>
```
Media order: @Video1 (source), @Image1, @Image2
Settings: <resolution>, duration <ceil of source seconds>, silent render

### Output 2 - <name>
...

## Finishing
Restore source audio, trim to <exact duration> s, QC gates passed? <list>
````

COMPACT template (one operation sentence per changed segment, full duration tiled):

```text
TASK - VIDEO EDIT:
Preserve every caption, subtitle, and other untargeted on-screen text element from @Video1 exactly as it appears, including its wording, styling, placement, animation, and timing. Text physically attached to a replaced target follows that replacement.
<start>-<end>s: keep everything exactly the same
<start>-<end>s: <one operation sentence>. Keep every unrequested element, camera motion, lighting treatment, and overall color grading from @Video1 exactly the same.
```

Operation sentence bank:
- Replace (reference): `Replace only [target] in @Video1 with [replacement] from [@ImageN]`
- Replace (words): `Replace only [target] in @Video1 with [description]`
- Modify: `Modify only [target] in @Video1 so that [change]`
- Remove: `Remove only [target] from @Video1 and reconstruct the revealed area consistently with its immediate surroundings`
- Add: `Add only [element] at [caption-grounded placement] in @Video1`

Person exclusion (once per replaced person; DETAILED only):

```text
The original source person identified as [target] in @Video1 must never appear in any frame of the output. Replace that person completely with [ALIAS] from [@ImageN] in every appearance, transferring the complete reference-defined look and retaining only the original performance, pose, blocking, interactions, and timing.
```

DETAILED skeleton (full rules and a filled example in `references/prompt-grammar.md`, Parts B8 and C4):

```text
[@ImageN] - [ALIAS], the complete replacement look for [TARGET]: [identity, hair, outfit, footwear, headwear, eyewear, jewelry, accessories]. Transfer this entire look from @ImageN, including the full outfit and all worn accessories.
<source-text preservation block>
Video edit. Keep this @Video1 clip exactly as it is - the same shots and cuts, camera moves, framing, composition, unmapped performers, setting, untargeted held and environmental props, lighting, pacing, and timing. Change only [complete scope], keeping source blocking, poses, motion, position, screen placement, and timing while rendering each replacement person's complete image-defined look.
1. [REPLACE | MODIFY | REMOVE | ADD] - [target and operation, @ImageN binding, temporal scope, exclusion, interactions].
[IDENTITY | REFERENCE | EDIT] lock: [mappings, untouched content, anti-bleed rules].
Render [one imperative summary of the complete reference-defined look].
Everything else - [untouched people, objects, untargeted wardrobe, text, environment, lighting, camera moves, all timing] - stays exactly the same.
```

Motion-transfer brief (constructed from the operation definitions; keep it short and concrete):

```text
Copy the full-body motion, gestures, timing and camera movement of the driving video @Video1 onto the person in @Image1. The person keeps the exact face, hair, outfit and accessories from @Image1. Keep the framing, camera motion and duration of @Video1. [The setting comes from @Image1 | The setting stays as in @Video1.] No text, no captions, no watermark.
```
(Choose the bracketed option while planning; the finished prompt keeps only one.)

## Tool adapters

- **Seedance 2** (reference-video modes): accepts English and Chinese prompts; attach the source as `@Video1` and the references in order as `@Image1..N`. Use the tagged templates as written. Chinese copy of the COMPACT template:
  ```text
  任务 - 视频编辑：
  保留 @Video1 中所有字幕及其他未指定的屏幕文字，内容、样式、位置、动画和时间完全保持原样。与被替换对象物理相连的文字随替换对象一起变化。
  0-12秒：仅将 @Video1 中女士手里的罐子替换为 @Image1 中的橄榄油瓶。@Video1 中其他未要求修改的元素、镜头运动、灯光处理和整体调色保持完全不变。
  ```
  Chinese person exclusion: `@Video1 中的原始人物（[目标]）不得出现在输出的任何一帧中。在每一次出场中，用 @Image1 中的 [别名] 完全替换该人物，迁移参考图的完整外观，只保留原有的表演、姿势、走位、互动和时间。`
- **KLING**: use its video-to-video edit/element mode for replacements (source video + element images) and its motion-control mode for motion transfer (driving video + character image). Describe each change in plain action verbs, one operation per run, and write the lock as one sentence; if the interface has no tag syntax, refer to the images by role ("the product photo") in the order attached. Multi-person identity swaps with strict exclusion are a weak spot: split into one run per person.
- **Higgsfield Cinema Studio (Genjutsu)**: motion transfer and object replacement are two separate operations that each take reference images plus exactly one video. Put the user's brief in the prompt and choose the operation from the request, not from the preset it came from. Multiple edited variants of one clip is the multi-version case in `references/variant-matrix.md`.
- **Runway-style V2V**: one natural-language instruction, usually no tags. Use one COMPACT operation sentence plus "Keep camera, cuts, timing, lighting and all on-screen text unchanged"; run timed segments as separate jobs. Poor fit for person identity replacement with a strict exclusion.
- **Nano Banana Pro**: not a video tool. Use it to prepare the references (replacement product on clean background, person on a white studio background, location plate, character sheet) and to restore a damaged frame.
- **Premiere Pro / After Effects**: finishing, not generation. Trim to the exact duration, relay the original audio, rebuild damaged captions, hard-cut hook/CTA sections, add subtitles to recreate outputs, loudness match.
- **Figma / Illustrator / Photoshop**: only for preparing reference graphics (logos, pack shots, end cards).

## QA checklist

- [ ] Mode matches the request (edit, recreate, hook/CTA, motion transfer, replacement); ambiguity was asked once.
- [ ] Every operation names one target with a unique anchor and a timing taken from the caption; segments tile the full duration.
- [ ] Every attached image appears by its `@ImageN` tag at least once; no raw ids, file names or URLs.
- [ ] Replacement looks come "from @ImageN", never from `@Video1`.
- [ ] Each replaced person has an exclusion sentence; unmapped people are named as unchanged.
- [ ] The source-text preservation block appears exactly once; no automatic caption add/remove.
- [ ] The lock names cuts, camera, lighting, pacing and timing; the closing "everything else stays exactly the same" is present.
- [ ] No unresolved "if/or" in the finished prompt; length within the tool's cap.
- [ ] Variants are zipped by position; N equals the number of final videos.
- [ ] Output audio plan stated (restore source audio or silent source); duration and aspect checked after render.

## References

- `references/prompt-grammar.md`: the full replace/preserve grammar, COMPACT and DETAILED templates, validation list and filled examples. Read before writing any edit prompt, and again when a prompt fails validation.
- `references/variant-matrix.md`: counting rules, variant table, matrix patterns, stand-in person images, run order and failure handling. Read when the request is "N versions" or when a replacement person has no photo.
- `references/recreate.md`: recreate for another market/language/cast, hook-or-CTA-only rules, a manual procedure for generators without recreate mode, and a localization checklist. Read for any market or language version.
- `references/finishing-and-qc.md`: probe, audio restoration with ffmpeg or Premiere, exact-duration trim and QC gates. Read before delivering any edited clip.
