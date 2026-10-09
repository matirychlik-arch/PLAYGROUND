---
name: caption-and-title-systems
description: "Spec sheets for captions, subtitles, titles and animated text in short-form (9:16) video, made to apply in Premiere Pro Essential Graphics or After Effects, plus optional SRT generation. Covers caption styles per genre (UGC, faceless, website/demo), subtitle rules (words per cue, timing, safe zones, clearance from faces and UI, fonts incl. Polish diacritics), title animation timing and motion language, 9:16 layouts (split screen, PIP) and failure modes. Use whenever a video needs on-screen text, even if the user never names the skill. Trigger on: napisy, napisy do wideo, napisy na reelsa, captions, subtitles, SRT, karaoke, hook tekstowy, tytuł, lower third, animowany tekst, kinetic typography, safe zone, strefa bezpieczna, Essential Graphics, MOGRT, split screen, PIP, \"napisy zasłaniają twarz\". Route to thumbnail-design for static covers, cinematic-prompt-builder for generating footage, viral-reel-builder for scripts."
---

# Caption and Title Systems

Turn "I need text on this video" into a numeric spec sheet Mati can apply in Premiere Pro (Essential Graphics) or After Effects without guessing: fonts, pixel sizes, safe zones, cue rules, animation timings, layout geometry, and a QA pass on the exported file.

## When to use / when not

Use for any on-screen text in a vertical or landscape video: speech captions, hook text, title cards, lower thirds, animated words, counters, UI labels over screen recordings, split-screen and PIP layouts that carry text.

Do not use for: static thumbnails or covers (thumbnail-design), writing the voiceover script or hook (viral-reel-builder), generating the footage (cinematic-prompt-builder), color grading or audio mixing. If the footage text itself must be rendered by a video model, tell the user that video models garble text and that real text belongs in the edit; this skill is the edit side.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

- Genre: UGC (talking person, phone footage), faceless/explainer (voiceover over b-roll or stills), website/demo (screen recording or website cards plus voice). Default: UGC.
- Frame: size and fps. Default 1080x1920, 30 fps, 9:16.
- Language of the speech. Default Polish. Polish needs a font with full coverage of ą ć ę ł ń ó ś ź ż (and capitals); test the font with a Polish pangram before committing.
- Source of words: authored script (exact lines spoken) or only the audio. Authored text supplies spelling, audio supplies timing.
- Look: TikTok caps, heavy impact caps, clean geometric caps, handwritten paper, or compact sentence case (default for UGC and faceless).
- Titles needed: hook line at the start, section titles, lower thirds, end card. Default: hook only.
- Animation level: static (default for speech captions), word highlight, or kinetic. Animation is a deliberate style choice, not a default.
- Subject constraints: where the face, hands, product label, website cards or existing text sit during each cue.

## Workflow

1. **Classify and pick the system.** Map the genre to a caption system in `references/caption-systems.md`. Pick one look and hold it for the whole video; a second caption style mid-video reads as a mistake.
2. **Lock the geometry.** Compute the safe box for the frame (table in `references/subtitle-rules.md`). For 1080x1920: top 10% = 192 px, bottom 16.7% = 321 px, sides 11% = 119 px. Platform UI sits in those margins, so text there is cut off or covered.
3. **Get the words, then the times.** Transcribe the cleanest audio you have (separate voice track beats the mixed sequence). If an authored script exists, its words replace the transcript's words; its timing never replaces the audio's timing. Spot-check three cues (start, middle, end). A constant offset means the wrong audio source; growing drift means bad alignment. Fix before styling.
4. **Chunk into cues.** At most 5 words and 32 characters per cue for UGC and standalone captions, at most 4 words and 42 characters for faceless explainers. Cut at the word clock, never by evenly spreading words. Keep every spoken word. Optional: generate the SRT with `scripts/words_to_srt.py`.
5. **Place against the picture.** Scrub the clean edit cue by cue and mark protected regions (face including mouth and chin, hands and fingertips, product labels, website cards, tutorial step labels, hooks, any baked-in text). Prefer a low position, then the upper safe area. Never cover a face to keep a fixed position (full procedure in `references/subtitle-rules.md`). Faceless is the exception: one fixed bottom-center baseline, no subject hunting.
6. **Add titles and motion.** Choose entrance, hold and exit from `references/title-animation-and-motion.md`. Every animation needs a one-line reason (hierarchy, narrative, feedback, state change).
7. **Compose layouts if needed.** Split screens, PIP, talking head plus cards: use the geometry in `references/layouts-and-geometry.md`.
8. **Write the spec sheet** in the output format below, ready to key into Premiere or AE.
9. **QA on the exported file**, not on the timeline (checklist below). Check failure modes in `references/failure-modes.md` when something looks off.

Core rules worth memorizing:

- Captions stay small and out of the way: bottom of frame, never covering the subject, never a multi-line block filling the picture.
- One font size for every cue in the video. If a cue does not fit, re-chunk it; do not shrink that cue.
- Floor: font size never below 2% of frame height (38 px at 1920 high), and never below 14 px.
- Hold a cue until the next one appears while speech is continuous; across a real pause let it end shortly after its own last word. Never stretch a cue through a pause.
- Keep the clean master untouched. Every restyle starts from the clean sequence, never from a burned export.
- Timing comes from audio. An authored script can supply words, never times.
- Brand names, numbers and foreign words keep the authored spelling.

## Output format

Produce this spec sheet as a markdown block, with real numbers filled in (no placeholders left):

```
# Caption/Title Spec: <project name>

## Frame
- Size / fps: 1080x1920 @ 30
- Genre: UGC | faceless | website-demo
- Language: pl
- Safe box: x 119-961, y 192-1599 (top 10% / bottom 16.7% / sides 11%)

## Caption style (apply in Essential Graphics > Text, or AE text layer)
- Font / weight: <family, weight>  (Polish glyphs verified: yes/no)
- Size: <px> (<% of frame height>), same for all cues
- Case: original | UPPER
- Fill: <hex>   Stroke: <px> outside, <hex>   Shadow: <x,y,blur,opacity or none>
- Plate: none | <hex, opacity, padding px, radius px>
- Alignment / anchor: center, baseline at y = <px>
- Max lines: 1 | 2 balanced     Max per cue: <n> words / <n> chars
- Animation: none | <word highlight rule>

## Timing
- Source of times: <voice track / mixed audio>   Words from: <script / transcript>
- Hold rule: hold to next cue when gap < <s>; else end <s> after last word
- Min cue duration: <s>

## Titles / hooks
| # | Text (exact string) | In (s) | Out (s) | Position | Entrance | Hold | Exit | Easing |
|---|---------------------|--------|---------|----------|----------|------|------|--------|

## Layout (if any)
<split / PIP geometry in px: x, y, w, h per slot, fit mode, corner radius>

## Clearance map
| Time range | Protected regions (norm. box) | Caption position |
|------------|-------------------------------|------------------|

## Export
- Codec / bitrate / audio: <e.g. H.264, 8 Mbps video target, AAC 48k>
- Deliver: final.mp4 + captions.srt + clean master (no captions)

## QA result
<filled after export check>
```

For SRT output, deliver a fenced `srt` block or the file produced by `scripts/words_to_srt.py` (usage in `references/subtitle-rules.md`).

## Tool adapters

- **Premiere Pro:** transcribe in the Text panel (check that Polish is in the language list for your version), edit the transcript, create the caption track, then style. Caption tracks have limited styling; to get strokes, plates, per-word color or motion, convert captions to graphics clips (menu names shift between versions, check yours) or build one text layer in Essential Graphics. Premiere has no per-character animators; if you need word or character entrances, build the title in After Effects and export it as a Motion Graphics Template (.mogrt) with Essential Properties for the text and color.
- **After Effects:** text layer plus Animators (Range Selector, based on Characters, Words or Lines) covers token entrances; shape layers for plates; masks or track mattes for wipes. Keep one comp per title, 1080x1920, same fps as the sequence, and expose Source Text through Essential Graphics for the MOGRT.
- **Burned-in by script or CLI:** if the user wants to skip the editor, the same rules apply to any burner: pass it the SRT, one font size, the safe margins above. Always view frames of the output afterward.
- **KLING / Seedance 2 / Higgsfield Cinema Studio:** do not ask these to render captions or titles; they can garble letters and drift between frames. Generate clean footage and add text in the edit. If a generated shot must contain a sign or screen with legible words, prompt the exact string in quotes and keep it short; verify every frame range it is on screen.
- **Nano Banana Pro:** good for a text-bearing still (title card background, end card, UI mockup for a website cutaway) because it renders quoted strings well; use it for stills, then animate in the edit. Poor fit for timed captions.
- **Figma:** fine for designing the caption style frame and title cards at 1080x1920 (type, plate, stroke) before keying values into Premiere; export PNG for stills, not for animated text.

## QA checklist

- Export the file, then inspect frames from the export: at least two frames at cue midpoints plus the longest cue, the shortest cue, and a cut boundary.
- Every caption present, readable, fully inside the frame, not clipped at glyph edges, wording matches the spoken cue.
- Caption words equal spoken words (no dropped or added words); brand spelling correct; Polish diacritics render (no empty boxes or fallback-font swaps).
- No caption covers a face, mouth, hands, product label, website card, tutorial label or another title.
- Text sits inside the safe box; nothing under platform UI zones.
- One font size across all cues; one style for the whole video.
- Cue timing matches audio at start, middle, end (no constant offset, no drift).
- Duration and audio of the export match the clean master (within about 1 s; audio ends within 0.2 s of video end).
- Animation: every title has an entrance, hold and exit that fit inside its clip; nothing pops on the cut frame by accident; reduced to the minimum the story needs.
- Clean master and SRT delivered alongside the captioned file.

## References

- `references/caption-systems.md`: read first when choosing a caption look; genre styles (UGC, faceless, website/demo), look presets (TikTok caps, impact, geometric, paper, clean), caption mechanisms (static, karaoke, walking highlight, plate, outline, reveal, token entrance).
- `references/subtitle-rules.md`: read when setting sizes, safe zones, cue length, timing, fonts, or when captions collide with the picture; includes the transcription-verify gate and the SRT script usage.
- `references/title-animation-and-motion.md`: read when animating titles or words; the timing contract, title primitives, motion language table, with Premiere and AE mappings.
- `references/layouts-and-geometry.md`: read for split screens, PIP, talking head plus cards, before/after, clip fit and scale math, corner radius gotcha.
- `references/failure-modes.md`: read when something renders wrong or before delivery; symptom to cause to fix, plus export notes.
- `scripts/words_to_srt.py`: dependency-free helper that turns word timestamps (Whisper-style JSON) into a chunked SRT with hold logic and optional authored-script word replacement.
