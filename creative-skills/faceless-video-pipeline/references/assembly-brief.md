# assembly-brief.md: building the cut in Premiere Pro (and After Effects)

Contents
1. Sequence and track layout
2. Placing clips and voice (centering formula)
3. Style-specific finishing (on twos, stepped motion, grain)
4. Audio mix steps
5. Captions pass
6. Export and verification
7. Assembly brief template

## 1. Sequence and track layout

- Sequence: 1920x1080 (16:9) or 1080x1920 (9:16), frame rate = the source clips' frame rate (read it; never hardcode 24/30), square pixels.
- Length = N x 10 s exactly (never shorter to fit short audio). Blocks sit back to back on a 10 s grid.
- Tracks:

| Track | Content |
|---|---|
| V1 | Block clips 1..N, hard cuts at the 10 s boundaries (no transitions unless the style calls for one) |
| V2 | Adjustment layer for finishing (Posterize Time for on-twos, grain), captions graphic track above |
| A1 | Narration voice, one clip per block, voice 1.0 |
| A2 | Clip SFX (the clips' own audio), about 0.12 relative to voice |
| A3 | Music bed, ducked under A1 |

- Stills videos: V1 = frames in order, each with its own duration (from the timestamp ledger), A1 = the ONE continuous narration.

## 2. Placing clips and voice (centering formula)

Each narration line is CENTRED in its block, so the picture never starts before the voice and the tail never hangs:
```
speech_len   = measured speech seconds of the take (head/tail silence ignored)
speech_start = where speech begins inside the file (seconds)
block_start  = (n - 1) * 10
place_file_at = block_start + (10 - speech_len) / 2 - speech_start
```
Example: block 3, speech 8.6 s, speech starts 0.12 s into the file: `20 + 0.7 - 0.12 = 20.58 s`.
Voice lines outside 7.2 to 9.5 s of speech are rewritten, not stretched. Never use Rate Stretch or Time Stretch on a voice take.
If a block's clip has no usable audio, keep A2 empty for that block; do not generate SFX with the speech model.

## 3. Style-specific finishing

- Cinematic Storybook (on twos): add an adjustment layer over the whole sequence with Posterize Time set to 12 fps. It re-times the update rate to 12 per second while leaving the audio and the container frame rate untouched.
- Flat 2D collage and Stickman: no extra finishing; a very light film-grain overlay is optional but keep it off Editorial (it is a clean print look).
- Paper Diorama: subtle grain and dust are already in the formula; do not stack more.
- Kids: keep everything clean and saturated; no grain, no vignette.
- Never add dissolves between blocks; hard cuts keep the pace.

## 4. Audio mix steps

1. Normalize the VOICE first (Essential Sound > Dialogue, or loudness normalize each take to about -16 LUFS), same preset on every take.
2. Then place SFX (A2, about 0.12 of voice) and the music bed (A3: about 0.10 generic, 0.05 for the Kids look and Cinematic Storybook), with Essential Sound > Music > Ducking keyed to A1.
3. Measure every 10 s block (mean volume). All blocks within about 3 dB of each other; spoken blocks about -18 to -21 dB mean. Remix any block more than 3 dB off. Ready check command is in `vo-and-captions.md` section 3.
4. Final loudness about -16 LUFS integrated; true peak under -1 dBTP.
5. No clipping on impact beats: SFX hits must never cover the first word of a line.

## 5. Captions pass

Run captions on the clean master after the mix is final (spec: `vo-and-captions.md` section 5). Premiere: Text panel > Transcribe sequence on the CLEAN narration track (mute music and SFX first), then replace the transcript words with the authored script words keeping timing, create captions, apply the look (`clean`, `paper`, `bold`), check Polish diacritics. For heavier styling use `caption-and-title-systems`. Export the SRT alongside the video.

## 6. Export and verification

- H.264 (or HEVC), high bitrate, AAC 320 kbps or 48 kHz PCM for the master; a clean master (no captions) is exported first and kept untouched, then the captioned version.
- 16:9 for YouTube long-form, 9:16 for Shorts/TikTok/Reels. For a 9:16 version of a 16:9 project, regenerate or recompose rather than crop key action.
- Verify the exported file: duration = N x 10 s within about 1 s; video and audio streams present; full playback without decode errors; three frames at 25 / 50 / 75 percent match the words spoken then; per-block loudness check; captions within safe zones; no leading freeze at 0:00.
- Thumbnail (optional): use `thumbnail-design` with the style key and a 3 to 6 word hook; 16:9 even for vertical videos.

## 7. Assembly brief template

```markdown
# Assembly brief - <title>
Format: <16:9 | 9:16>, <fps> fps, N = <blocks> blocks = <N*10> s
Style lock: <style name>, accent <color or none>, motion: <flat on twos | dimensional | stepped 12 fps>
Voice: <engine/model/voice id>, delivery phrase: <phrase>   Music: <file or none>, level <0.10 | 0.05>
Finishing: <Posterize Time 12 fps on V2 | none>   Captions: <off | clean | paper | bold>, lang <pl|en>

| Block | Start | Clip file | Voice file | Speech (s) | Place voice at | Impact beat (time) | SFX cues | Notes |
|-------|-------|-----------|------------|-----------|----------------|--------------------|----------|-------|
| 1 | 0:00 | block01.mp4 | voice01.wav | 8.6 | 0.70 - speech_start | 4.0 stamp | pop, stamp | cold open |

Tracks: V1 clips / V2 finishing + captions / A1 voice / A2 SFX 0.12 / A3 music ducked
Checks before export: loudness per block within 3 dB | total = N x 10 s | no dissolves | Posterize Time applied | diacritics render
Deliverables: final_clean.mp4, final_captioned.mp4, final.srt, sources.txt
```
