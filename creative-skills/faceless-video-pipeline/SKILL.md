---
name: faceless-video-pipeline
description: "Pipeline for narrated faceless videos (YouTube, TikTok, Reels, Shorts) in one locked visual style with ONE voice: topic sourcing, script (hook, build, turn, payoff, words per block), shot list with ready prompts per scene, voice-over spec for ElevenLabs or any TTS, captions spec and a Premiere Pro assembly brief. Types: Explainer, History (incl. long-form), Kids (incl. song), Picture Story (stills), Fairy Tale and Myth; pinned style packs and 22 presets. Use whenever a video has a narrator and generated visuals but no face on screen, even without the word faceless. Trigger on: film bez twarzy, faceless, kanał YouTube automation, wideo z lektorem, explainer, film historyczny, dokument, bajka, piosenka dla dzieci, baśń, legenda, scenariusz do filmu z lektorem, shot lista, prompty do scen, spójny styl, jeden głos lektora, napisy, brief montażowy Premiere. Route to narration-vo for fixing only the voice-over, ugc-video-scripts for ads with a person on camera, video-edit-brief to rebuild a reference edit."
---

# Faceless Video Pipeline

Turn a topic into a complete production package for a narrated video with no one on screen: script, scene-by-scene prompts in one locked style, voice-over spec, captions spec and an editor's assembly brief. The package is tool-agnostic; the user generates with their own tools (Nano Banana Pro, KLING, Seedance 2, Higgsfield Cinema Studio, ElevenLabs) and assembles in Premiere Pro.

Why the structure matters: a faceless video fails in four ways, a list-shaped script, style drift between scenes, a voice that changes or races, and visuals that decorate instead of showing what the line says. The pipeline fixes each at the source: a through-line and arc, a byte-identical style formula, one locked voice with a word budget, and shots that stage the nouns of their own line.

## When to use / when not

Use when the user wants a narrated video built from generated or illustrated visuals: explainers ("dlaczego X"), history, kids education or songs, narrated stills, fairy tales and myths, for a channel or a single video. Also use for pieces of it: only the script, only the shot list for an existing script, only the style lock.

Do not use when:
- The user only needs the voice fitted to timings or a talking-head inserted into an edit: use `narration-vo`.
- It is an ad with a creator on camera, product, offer: use `ugc-video-scripts`.
- The user hands over a reference edit to recreate cut by cut: use `video-edit-brief`.
- The task is one cinematic clip prompt: use `cinematic-prompt-builder` or `seedance-director`.
- Only a thumbnail is needed: use `thumbnail-design`.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

| Input | Default if not given |
|---|---|
| Video type | infer from the topic: facts = Explainer, past events = History, children = Kids, legend = Fairy Tale and Myth, "obrazki / stills" = Picture Story |
| Topic, or "find me topics" | if absent, run the five-topic round (`references/topic-sourcing.md`) |
| Pasted script | treat as authored text; split, never rewrite |
| Length | Explainer 1 min (6 blocks), Kids 1 to 3 min, Fairy Tale 2 to 3 min, Mannequin about 90 s, long-form 10 / 15 / 20 min |
| Aspect | 9:16 for TikTok/Reels/Shorts, 16:9 for YouTube long; ask if the platform is unknown |
| Narration language | the language the user writes in (Polish for Mati); visuals prompts always English |
| Style | channel default from `references/style-packs.md`; a style the user names is locked, never swapped |
| Accent color (collage, diorama) | choose by topic mood from the list in the style pack, lock one per video |
| Mode | animated clips (default) or narrated stills |
| Voice | the voice the user already uses; else propose one and record it |
| Captions | off unless asked; if on, look `clean` (Fairy Tale = `paper`) |
| Music | none, except Kids looks and Fairy Tale (wordless bed on by default) |

Ask the style question with the options and one-liners from `style-packs.md` (or the 22 presets in `references/explainer-presets.md`) in one message together with length and aspect, then proceed; do not interrogate.

## Workflow

1. **Intake and defaults.** Fill the table above. Compute N = duration seconds / 10 blocks. Pacing law: 6 blocks per minute, five hard-cut shots of about 2 s per block (Kids four of 2.5 s), one VO line per block, an impact beat about every 3 s, stills change picture about every 1 s. Long-form (10+ min) and stills have their own rules in `references/format-variants.md`; read it before planning them. Warn about the size of a long-form run before starting.
2. **Topic.** Stated topic: go on. No topic or "randomizer": the five-topic research round. A pasted script or a channel link: follow the rules in `references/topic-sourcing.md`. Factual topics get quick research first (hook stat, 3 to 5 concretes, the counterintuitive turn); keep a Sources list.
3. **Style lock.** Pick the style (default per channel type, or the user's), copy its STYLE FORMULA, PALETTE LOCK, {MOTION} slot and NEGATIVE from `references/style-packs.md` verbatim, lock the accent. Produce the style-key prompt. The formula is pasted byte-identical into every later prompt; that is the whole consistency mechanism.
4. **Through-line and roster.** Name ONE physical object or process that appears in every block and escalates to a payoff. Plan characters (2:3), locations (enough that no place carries more than 2 consecutive blocks, each with a coverage angle) and props (1:1, the through-line first). Write the asset prompts from `references/prompts-and-blocks.md`. Long-form: build the ERA MAP first.
5. **Script.** Follow `references/scriptwriter.md` exactly: arc hook, build, turn, payoff; cold open of at most 8 words; one idea per block; 20 to 23 English words per block (Kids 17 to 21; Polish about 16 to 19, see `narration-vo`), at most two sentences, numbers as words, line hygiene. Run the rewrite pass and the numeric checks. Show the whole script table to the user, name the through-line, and continue in the same turn unless they ask for changes.
6. **Shot list.** For each block write five shots (Kids four) with size and angle varied, choreography-only beats, the through-line state, one impact beat, an AUDIO line, and the complete block prompt from `references/prompts-and-blocks.md` (Route A: multi-shot clip) or per-shot keyframe + animation prompts (Route B). Check the variety rules: no adjacent equal sizes, no re-establishing a location, OTS only with a named visible character, at most 2 consecutive blocks per location, every block stages the nouns of its own line.
7. **VO spec.** One locked voice, one delivery phrase repeated verbatim, one line per block, rules and line hygiene from `references/vo-and-captions.md`. For Polish or any non-English narration, run each line through the `narration-vo` fit check (its `fit_narration.py`) to confirm it fits the window.
8. **Captions spec** (only if on): clock from the clean voice takes, words from the script, look and placement from `references/vo-and-captions.md`; hand off to `caption-and-title-systems` for styling.
9. **Assembly brief.** Fill the template in `references/assembly-brief.md`: tracks, centering formula, level law, finishing (Posterize Time 12 fps for on-twos looks), export checks.
10. **QA** with the checklist below, then deliver the package in the Output format. Offer the thumbnail (`thumbnail-design`) and, for series, a channel style lock reused next time.

Generation order for the user's tools: style key -> assets -> clips (or keyframes then animation) -> voice takes -> measure -> assemble -> captions. Voice takes can run in parallel with clips once the script is locked. Regenerate only failed items; never drop a block.

## Output format

Deliver one markdown package with these sections in this order. Prompts are in fenced code blocks, ready to paste.

````markdown
# <Video title> - production package
Type: <Explainer|History|Kids|Picture Story|Fairy Tale> | Length: <N> blocks = <s> s | Aspect: <9:16|16:9> | Language: <pl|en>
Through-line: <object, how it escalates, how it resolves>
Sources: <urls or "n/a (fiction)">

## 1. Style lock
Style: <name> (<user's pick | default>) | Accent: <color or none> | Motion: <token>
STYLE FORMULA (paste in every prompt):
```
<formula with {ACCENT} filled>
```
PALETTE LOCK: <line>      NEGATIVE: <line>
Style key prompt:
```
<prompt>
```

## 2. Asset roster
| ID | Type | Aspect | Prompt (formula pasted) | Used in blocks |
|----|------|--------|-------------------------|----------------|

## 3. Script (arc roles; words counted)
| # | Role | Location | VO line (<lang>) | Words | Through-line state |
|---|------|----------|------------------|-------|--------------------|

## 4. Shot list - one block per heading
### Block <n> - <arc role> - <location> - refs: <asset ids, max 7>
VO: "<line>"
```
<full block prompt: Style/PALETTE LOCK/references/SHOT 1-5 with size+angle and timings/AUDIO/NEGATIVE>
```
(Route B: keyframe prompt + animation prompt per shot)

## 5. VO spec
Voice lock: <engine, model, voice, settings> | Delivery phrase: "<phrase>"
| # | Line sent to TTS | Words | Target speech s | Notes (cues) |
Level law: voice 1.0, SFX 0.12, music <0.10|0.05> ducked | Loudness -16 LUFS

## 6. Captions spec
<on/off, look, language, clock, placement, font check for Polish diacritics>

## 7. Assembly brief
<template from references/assembly-brief.md filled in>

## 8. QA log
<checklist results, open issues>
````

For a partial request (only the script, only the shot list) deliver just those sections, keeping their numbering.

## Tool adapters

- **Nano Banana Pro:** style key, character/location/prop sheets and stills. It takes several reference images, so attach the style key plus assets; give any text as an exact string in quotes (but this pipeline keeps in-frame text off except the diorama label). For Picture Story edit frames, pass only the previous frame as reference with the "keep EXACTLY, change ONLY" prompt.
- **KLING:** animate a keyframe or a block: one subject, plain action verbs, the camera move in its own sentence, 2 to 3 s per shot in Route B. Multi-cut-in-one-clip prompts are less reliable here, so default to Route B and cut in Premiere.
- **Seedance 2:** accepts English and Chinese prompts; try the 10 s five-shot block prompt (Route A) on one block first and count the cuts that come back; fall back to Route B if it merges shots.
- **Higgsfield Cinema Studio:** use for hero blocks or establishing shots where you want explicit camera control; keep the formula and references identical to the rest of the video.
- **ElevenLabs (or any TTS):** one voice, identical settings on every take; Polish needs a multilingual model and a calibration take; bracket cues only on models that support them. Details in `references/vo-and-captions.md` and `narration-vo`.
- **Premiere Pro / After Effects:** assembly, mix, Posterize Time 12 fps for on-twos looks, captions (Text panel transcription on the clean voice track). After Effects for any animated map, ribbon or title the clips cannot produce. Brief in `references/assembly-brief.md`.
- **Figma / Illustrator / Photoshop:** poor fit for generation; use Figma only for a roster board or style sheet and Photoshop/Illustrator for thumbnails or fixing a flawed asset.

## QA checklist

- [ ] One style formula, byte-identical in every prompt; one accent color for the whole video; the user's named style was not swapped.
- [ ] Through-line is in every block, escalates, and the payoff block resolves it; it has its own prop asset.
- [ ] Hook sentence is at most 8 words (Explainer, History); Kids opens with the question and answers it in block 1.
- [ ] Build blocks fail the reorder test; the turn changes what the viewer thought; the kicker echoes the hook.
- [ ] Every VO line: 20 to 23 words (Kids 17 to 21; Polish about 16 to 19), at most 2 sentences, numbers as words, no filler, one new concrete, no phrase of 5+ words repeated.
- [ ] Every non-English line passed `fit_narration.py`; no line RUSHED or UNDER.
- [ ] Each block has 5 shots (Kids 4), no adjacent equal sizes, no re-establishing wide, OTS only with a named visible character, at most 2 consecutive blocks per location, one impact beat, SFX 1:1 with motion.
- [ ] Each block's shots stage the concrete nouns of its own line.
- [ ] No on-screen text except the diorama letterpress label; no real brand, studio or person names in prompts; no `child/kid/childlike` tokens.
- [ ] Facts and numbers traceable to the Sources list; honest uncertainty stated in long-form.
- [ ] Voice: one identity, one delivery phrase, no time-stretch; level law and per-block loudness within 3 dB.
- [ ] Captions: timing from clean takes, words from the script, Polish diacritics verified, safe zones respected.
- [ ] Total length = N x 10 s; no dissolves between blocks; no leading freeze.
- [ ] After generation: cut count checked per block, identity/palette checked against assets, regenerate only the failing block.

## References

- `references/scriptwriter.md`: read before writing any script; through-line, arc, VO line craft, rewrite pass, numeric limits and pacing numbers.
- `references/style-packs.md`: read at style lock; every style formula, palette lock, motion slot and negatives verbatim (Editorial collage, Paper Diorama, Mannequin, Cinematic Storybook, Watercolor, Stickman, Flat 2D Papercraft, five Kids looks), channel defaults, cross-channel rule, music moods.
- `references/explainer-presets.md`: read when the user wants to browse or name one of the 22 presets, or asks for a look without a pinned formula (starter formulas).
- `references/prompts-and-blocks.md`: read when writing asset prompts, block prompts (5-cut and Kids 4-cut), Route B keyframes, and the retry ladder.
- `references/format-variants.md`: read for Kids (question-first skeleton, interplay), Song mode, Talking Characters, Picture Story frame rules, long-form History (ERA MAP), Fairy Tale.
- `references/vo-and-captions.md`: read when specifying voice, line hygiene, level law, mix verification and captions.
- `references/topic-sourcing.md`: read when the topic is not given, a script is pasted, or a channel link is provided.
- `references/assembly-brief.md`: read when writing the Premiere/AE assembly brief and export checks.
