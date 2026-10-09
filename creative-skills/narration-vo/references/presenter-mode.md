# Presenter mode: a talking-head narrator inserted into an existing edit

Contents
1. When this applies and the consent rule
2. Two ways to get the talking head
3. Script budget for a presenter
4. Green-screen identity reference (master prompt)
5. Talking-clip prompt (master prompt)
6. Voice replacement and lipsync notes
7. Framing, eyeline and gesture
8. Compositing: cutout, badge, fullframe (numbers)
9. Keying notes (Premiere Pro / After Effects)
10. QC and delivery
11. Presenter brief template

## 1. When this applies

Use it when the user has a finished or rough video (the base) and wants a person ("put me in as the narrator", "my face as the host", "talking head over my clip") to appear on screen and speak over it. The base picture is preserved; the person is added on top.

Hard rules:
- The photo must show the user or another consenting, non-public person. Refuse to build a presenter from a celebrity, politician or private individual who has not agreed.
- Preserve the base video's picture and cover its full duration unless the user names a range.
- Supplied script text is authored text: split only at sentence boundaries, keep every word in order, invent nothing.
- This is a video job. A static photo overlay, an audio-only voice-over, or generic dubbing are different tasks (use the audio workflow in SKILL.md for those).

## 2. Two ways to get the talking head

| Route | How | Pick when |
|---|---|---|
| A. Real footage | The person records themselves in front of a green or plain wall, lens at eye level, reading the script | Best quality, real lipsync, real eyeline. Always the first suggestion if the person can film |
| B. Generated from a photo | A video model that renders a speaking person from a reference image makes one 10 s clip per script block on a green background; the voice is then replaced with the locked voice | The person cannot film, or the same host must appear in many videos |

Route B facts that shape everything below: one generation is about 10 s, so one clip = one script block; clip audio is only the person's voice; the model's native voice differs per clip, which is why the voice is replaced afterwards.

Poor fits: wide shots with a person walking, hands doing precise work, side profile, and long continuous takes over 10 s without a cut; route B drifts in identity over long runs, so cut between blocks rather than hide the seams.

## 3. Script budget for a presenter

- A presenter clip speaks at a brisk steady pace: **3.1 to 3.5 words/sec, 31 to 35 words per full 10 s block**, proportionally fewer for a partial final window. This is faster than the 20 to 23 words of a voice-over-only block because the person is on screen and the pace reads as conversational.
- Polish estimate: 25 to 28 words per 10 s block (about 0.8 of English). Calibrate on one clip.
- `blocks = ceil(base_duration / 10)`. The final window shorter than 10 s: generate the normal 10 s clip, then trim the talking clip (audio and video) to the measured remaining duration before compositing. Do not pad, loop, or leave the 10 s tail.
- No script supplied: transcribe the base video's speech (any STT) and write the presenter lines around it, or ask for the lines; do not invent facts.
- If the supplied text cannot fit the grid, report both counts and ask whether the base duration or the covered range should change.
- Run each block through `python3 scripts/fit_narration.py --text "<line>" --seconds 10 --lang <code> --wps 3.3` (3.3 is the presenter articulation pace) before generating.

## 4. Green-screen identity reference (master prompt)

Make ONE reference image from the person's photo, 9:16, with an image model that edits a supplied photo faithfully. Verbatim except for pronouns:

```text
Edit this photo. Keep the PERSON identical - same face, hairstyle, clothing, skin tone,
pose and framing, copied faithfully, not beautified and not a lookalike. Change one thing
only: replace the background with a perfectly uniform flat chroma-key green screen
(#00B140), evenly lit, no gradient, shadow or vignette, filling everything behind the
person. No green spill on the person; preserve clean hair edges.
```

If the model fails twice or refuses, retry the same prompt on a second image model. Inspect the result: face unchanged, no green on skin or clothes, hair edges clean.

## 5. Talking-clip prompt (master prompt)

One per block, 9:16, 10 s, the green-screen image attached as an identity reference. Verbatim template:

```text
IDENTITY REFERENCE (appearance only, not a start frame): copy the attached person and
solid green background faithfully. The first frame already catches them mid-speech, never
frozen. They look into the front camera and say in <DELIVERY>, in <LANGUAGE>:
"<BLOCK LINE VERBATIM, 31-35 WORDS FOR A FULL BLOCK>". Say every word exactly once at a
brisk steady pace, then hold a calm engaged look. For a partial final window, size the line
to that window even though the clip is 10 seconds. Camera locked; small natural head and
shoulder gestures only. Audio is only the clear voice. Keep the background uniformly vivid
green. No repeated or improvised words, captions, watermark, camera motion, beautification,
background change, or frozen opening.
```

Rules: put the line in quotes inside the prompt; one line per clip; generate every block's clip, retry only failed blocks (at most twice); confirm the spoken words match the line (listen or transcribe) since models sometimes improvise.

## 6. Voice replacement and lipsync notes

- After each clip is generated, run a speech-to-speech voice changer on the clip with the locked voice. It replaces the timbre and keeps the clip's timing, so the mouth movement stays in sync. Each result must keep the block's duration and contain audio.
- Never add a separate lipsync pass: it re-renders the mouth and tends to break identity and teeth.
- Do not time-stretch the talking clip to fit the base cut. Re-cut the base or rewrite the line.
- Route A (real footage): a natural voice needs no replacement; if the user wants a studio voice, replace speech-to-speech the same way, never text-to-speech over a moving mouth.
- Extract the block's audio from the talking clip at full length (no trimming) and loudness-normalise to -16 LUFS so it sits like any other voice-over take; do not re-centre it in a window or the lips lose sync.

## 7. Framing, eyeline and gesture

- Eyeline: the person looks into the front camera (the lens), not at the script and not at the base picture; a slight glance away at the very end of a block is natural, a roaming eye is not.
- Camera locked, no push-ins on the talking clip; motion in the final edit comes from the cut, not from the head shot.
- Framing: head and shoulders, centred, eyes in the upper third; leave headroom of about one third of the face height. A tight face-only crop reads badly in the badge style, a very loose full body shrinks the face in the cutout style.
- Gestures: small natural head and shoulder movement only. No big hand gestures, no turning away, no objects covering the mouth.
- Start mid-speech: a clip that starts frozen then "starts playing" a second later gets regenerated.
- Hold a calm engaged look at the end of the block so the cut out has clean pose.
- Clothing in the photo should be a solid mid-tone; green or very reflective clothing causes spill and holes in the key.

## 8. Compositing styles (numbers)

All three put the person over the base; the base picture is never changed.

| Style | Look | Numbers |
|---|---|---|
| `cutout` | Person cut out and placed flush in a bottom corner (facecam style); torso cut at the frame edge, so bottom corners only | height about 0.64 of the base height; keep a centre-cropped width of about 0.72 of the talking frame |
| `badge` | Loom-style circle on a flat paper-tone disc, with margin | disc diameter about 0.355 of base height; disc colour `#E8DFD0`; face offset about 40 px down inside the crop (about 130 px if the model framed tighter); use badge when hair edges are ragged or the key is poor |
| `fullframe` | Person keyed at base height, centred, flush bottom; the scene stays visible around them | use on hook, turn and closer blocks only |

Safe margins for badge placement:
- 16:9 landscape: 5 percent of width at the sides, 7 percent of height top and bottom (title safe).
- 9:16 portrait (1080 x 1920 basis): top 250 px (13.1 percent of height), bottom 320 px (16.7 percent), sides 120 px (11.2 percent). For bottom corners the right-hand margin widens to 21.8 percent of width because the engagement rail covers the right edge of the lower 40 percent.

Position default bottom-right; move to the opposite corner when it covers a subject or a caption area. Never cover the key content of the base. Keep captions and presenter on opposite sides.

## 9. Keying notes (Premiere Pro / After Effects)

- Sample the key colour from the clip's own corner, never assume #00B140: every generator renders a different green.
- Clean broadcast green (high saturation, almost no red): Ultra Key in Premiere or Keylight in After Effects, then a despill. Olive or natural greens (for example RGB 59, 129, 69) have near-neutral chroma and a standard chroma key wipes or ghosts the person; use a luma-invariant key instead: treat a pixel as wall when `g / (r+g+b) > 0.42` and `g > r + 10` and `g > b + 10`, shave the matte by 1 px, blur 1 to 1.5 px, then despill.
- Green spill on the person (not green-dominant) must stay opaque; if the face or jacket goes transparent the key is too aggressive.
- Never hand-tune chroma thresholds clip by clip; if the edge is ragged use the badge style instead.

## 10. QC and delivery

- Contact sheet: one frame per block. The presenter is opaque, fully inside the frame, clean-edged (no green fringe), and does not cover important base content. A failed block is regenerated/recomposited alone.
- Audio: original base audio is kept under the presenter when it is stereo and separable; if the base audio is a mono mix with speech and music baked together, they cannot be separated safely, so say that the original audio will be dropped before doing it.
- Final length matches the base duration within 0.1 s; audio and video both present on the joined file.
- Every supplied sentence survived in order, nothing invented.
- Offer burned captions separately; do not add them silently.
- Report: voice used, block count, covered duration, presenter position and style, whether original audio was dropped.

## 11. Presenter brief template

```markdown
# Presenter brief - <project>
Base video: <file>, <duration> s, <16:9 | 9:16>, audio: <stereo separable | mono mix>
Presenter: <name or "the user">, consent confirmed: yes
Route: <A real footage | B generated from photo>
Voice: <engine, voice id/type, language>   Delivery phrase: <one phrase>
Style: <cutout | badge | fullframe>   Position: <br | bl | tr | tl>
Blocks: <N> x 10 s (last window <x> s)   Words per block: <31-35 EN | 25-28 PL>
| # | Window | Line (verbatim) | Words | Base content under presenter | Status |
|---|--------|-----------------|-------|------------------------------|--------|
Premiere: V1 base, V2 keyed presenter (Ultra Key + despill), A1 presenter voice at -16 LUFS, A2 base audio ducked or muted
Open issues: <...>
```
