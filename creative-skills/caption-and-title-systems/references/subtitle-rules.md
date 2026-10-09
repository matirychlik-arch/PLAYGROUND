# Subtitle rules

Contents:
1. Safe zones and numbers per frame size
2. Size, line length, chunking
3. Timing and hold logic
4. Transcribe, verify, style, verify (the four gates)
5. Clearance from the picture (procedure)
6. Fonts, languages, Polish
7. SRT generation (script usage)

## 1. Safe zones and numbers

Platform UI margins keep text from being cut off. They do not establish clearance from the subject; see section 5.

| Profile | Frame | Top | Bottom | Sides | Safe box (px) |
|---|---|---|---|---|---|
| Portrait, Instagram Reels spec (standalone, UGC) | 1080x1920 | 10% = 192 | 16.7% = 321 | 11% = 119 | x 119-961 (842 wide), y 192-1599 |
| Portrait, faceless | 1080x1920 | 10% = 192 | 17% = 326 | 11% = 119 | x 119-961, y 192-1594 |
| Landscape, standalone | 1920x1080 | 10% = 108 | 17% = 184 | 7.5% = 144 | x 144-1776, y 108-896 |
| Landscape or square, faceless | 1920x1080 or 1080x1080 | 10% | 10% (108) | 7.5% (144 / 81) | bottom margin only 108 px |

Rule of thumb: keep the top 10% clear, the bottom 17% (portrait) clear, and the side margins clear, in every caption and title, unless the title is intentionally full-bleed art.

Font size floor: 2% of frame height and never below 14 px (38 px at 1920 high, 22 px at 1080 high). The compact UGC size is 2.6% of height (about 50 px at 1920).

## 2. Size, line length, chunking

- Cue length: at most 5 words and 32 characters (UGC, standalone). Faceless explainers allow 4 words and 42 characters. Punchy UGC variant: 4 words.
- Lines: one line by default. Two lines only when balanced (similar length), never a three-line block. If a cue cannot fit at the video's one font size, split it using the word clock; never discard words and never drop below the floor.
- One font size for the entire video. If a long cue does not fit, re-chunk it; do not shrink that one cue.
- Width check (rule of thumb): characters per line is about safe width divided by (0.5 x font size in px). At 50 px in an 842 px safe width that is about 33 characters, which matches the 32-character cue limit. At 80 px it is about 21 characters per line, so use 2 balanced lines or fewer words.
- Case: sentence case or original case for natural speech; ALL-CAPS only for the caps looks. Do not mix cases between cues.
- Stroke: a thick black stroke for caps looks; around 4.5% of font size for the bold look, about 12% for the compact UGC look. Without an outline, use a soft shadow only.
- No plate unless requested. Text stays small and out of the way.

## 3. Timing and hold logic

- Times come only from the audio, taken from the cleanest narration you have: per-block voice files shifted to their position in the edit (best), a continuous narration track, or the mixed sequence last. Never estimate times from the script or by generating, even if told to "time them from the script": a script supplies words, not times.
- Hold a caption until the next one appears while speech is continuous (a bridge across tiny gaps). Across a real pause, end it shortly after its own last word. Do not extend holds through pauses and do not extend cues across unchecked motion.
- Preserve every spoken word and the natural pauses.
- A cue should be on screen long enough to be read; very short cues (a single quick word) can share a cue with the neighbor if the 5-word limit allows.
- Back-to-back cues must not overlap: treat the out point as exclusive so the same frame never carries two captions.
- Do not add transitions or animation to captions unless requested. If requested, keep entrance and exit inside the cue's own duration.

## 4. Four gates, in order (none skipped)

Captions drift and lose words when a step is skipped. Transcribe, verify the transcript, style, verify the render.

1. **Transcribe on the cleanest audio.** Priority: per-block voice files, then separate continuous narration, then only the mixed sequence (in that case filter the voice range if your tool allows and give the known language). Premiere's Text panel and Whisper-style tools both work; set the language explicitly (Polish: `pl`).
2. **Verify the transcript before styling.** With an authored script, compare it to the transcript: if overall similarity is below about 0.90 or a whole block matches loosely, retry with a larger model or per-block alignment. If the word count per second is implausible without a script, retry with a larger model and the language set; if still thin, report an incomplete transcript instead of burning it. Spot-check three cues against the audio: near the start, middle and end. A constant offset points to the wrong audio source; growing drift points to bad alignment. Fix before styling.
3. **Style one look.** Apply the spec sheet. Keep the clean sequence as the immutable master; every retry or style change starts from the clean master.
4. **Verify the render.** Export, then check: duration matches the clean master within about 1 s; audio is present and ends within 0.2 s of the video end (a full video duration does not prove the voice tail survived); caption word count equals spoken word count; look at frames at two or more cue midpoints. Empty or odd-looking labels mean a glyph or font failure; no label means the burn or layer failed.

If captions cannot be made to pass, deliver the clean video, say what failed and at which interval. Never block delivery on captions.

## 5. Clearance from the picture (procedure)

Applies to standalone and UGC speech captions. Faceless uses the fixed bottom layout and skips this procedure.

1. Finish the clean edit first. Add captions after the edit is locked; any later cut invalidates the placement.
2. Scrub every cue. Check both cue edges and samples at most 0.25 s apart; also check cuts and fast movement between samples, because sampling is not tracking.
3. Write a clearance map (time range, protected box, caption position). Protect: the whole face including mouth and chin, both hands including every fingertip (separated fingers too), complete product labels, website cards, tutorial Step labels, hooks, and text already baked into the footage. Use conservative boxes that cover all movement inside the interval; split the interval at cuts.
4. Place the caption: prefer a low position; if blocked, try the upper safe area. Keep top 10%, bottom 17% (portrait) and side margins clear.
5. Never cover a face to keep a fixed position. If neither area fits, do not shrink text below the floor, add blank panels, crop the subject or change the aspect ratio. Ask for a composition repair (move or rescale the subject, shorten the cue, re-time the cut) or deliver with a flagged interval.
6. After export, review the exported file again, not the timeline: caption present with the right wording, no clipped glyphs, no overlap with face/product/UI/text, readable. A successful encode is not a visual pass, and a layout calculation is not an inspection.
7. Budget your own effort: one map plus one correction, one render plus one retry. A retry may re-chunk the same spoken words from the word clock or adjust readable styling; it does not change speech timing, drop words or move the protected boxes to make room.

New footage that will carry captions should leave a compact plausible text location; never reserve an empty half-screen.

## 6. Fonts, languages, Polish

- Default faces: TikTok Sans Bold or Montserrat ExtraBold for caps looks; Metropolis for compact UGC; Anton for impact; handwritten faces only for paper.
- Verify glyph coverage against the actual caption text. For Polish test ą ć ę ł ń ó ś ź ż and capitals ĄĆĘŁŃÓŚŹŻ. In the source tests, PatrickHand and PermanentMarker had no Cyrillic; do the equivalent check for Polish before trusting any handwritten face.
- A missing glyph must never produce an empty or substituted caption silently. Compare the first and last frame of the longest cue after export.
- Install fonts on the machine before opening the project (Premiere and AE substitute silently if the font is missing). For a deliverable that others will open, note the font names in the spec sheet.
- Language: set the speech language explicitly in the transcription tool; the "auto" guess fails on short clips and names.

## 7. SRT generation (optional)

SRT is the portable text-with-times format. Structure of one block: index line, `HH:MM:SS,mmm --> HH:MM:SS,mmm`, one or two text lines, blank line.

Get word timestamps first (any tool), e.g. with OpenAI Whisper CLI:

```bash
whisper voice.wav --language pl --model small --word_timestamps True --output_format json
```

Then convert with the helper (dependency-free Python 3):

```bash
python3 scripts/words_to_srt.py voice.json -o captions.srt --max-words 5 --max-chars 32
python3 scripts/words_to_srt.py voice.json -o captions.srt --script lines.txt --max-words 4 --max-chars 32 --case original
python3 scripts/words_to_srt.py voice.json -o captions.srt --lines 2 --case upper
```

Options: `--script FILE` replaces recognized words by the authored words when the token counts line up (otherwise it warns and keeps the recognized words), `--pause-break` starts a new cue after a gap, `--bridge` holds a cue to the next one across gaps shorter than that value, `--tail` is how long a cue lingers after its last word before a real pause, `--min-dur` sets the minimum cue length, `--lines 2` inserts a balanced line break. The defaults are starting points, not standards: tune by eye, then run the four gates above.

Import into Premiere via File > Import (captions) or the Text panel; Premiere applies its own caption styling, so restyle after import. For burned-in output the SRT is the timing source, not the style.
