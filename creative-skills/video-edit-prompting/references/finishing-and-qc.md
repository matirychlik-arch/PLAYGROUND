# Finishing and QC for edited clips

Contents:
1. Probe the source
2. Why finals are silent and how to restore audio
3. ffmpeg recipe (audio extraction, offset, trim, remux)
4. Premiere Pro / After Effects equivalent
5. QC gates

Source note: this file generalizes the source-probe and finalization pipeline of a production edit workflow to plain ffmpeg and an editor. Edit models usually render silently, so the original audio is laid back under the new picture.

## 1. Probe the source

```bash
ffprobe -v error -show_streams -show_format -of json -- source.mp4
```

Record, once, from the JSON:
1. Primary video stream: prefer `disposition.default=1`, otherwise the first video stream that is not cover art (`disposition.attached_pic` not 1).
2. Duration: finite and positive from `format.duration`, falling back to the video stream's duration. Reject a duration outside your tool's accepted range (the reference workflow accepted 4.0 to 30.0 s).
3. Display aspect = (coded_width x sample_aspect_ratio) / coded_height, inverted after a 90 or 270 degree rotation (side data or `tags.rotate`). Default SAR 1:1.
4. Frame rate: `avg_frame_rate`, then `r_frame_rate`, falling back to 24 fps only for tolerance math.
5. Audio: the stream with `disposition.default=1`, otherwise the first audio stream; keep its absolute stream index. No audio stream means the source is silent.
6. Audio offset: `audio_start_time - video_start_time` when both are finite, otherwise 0.0.

Keep the exact source duration, its ceiling (use the ceiling as the requested render length so the render is never shorter than the source), display aspect, fps, audio stream index and offset.

## 2. Why finals are silent and how to restore audio

The edit model renders without sound. The final deliverable gets only the source's own default audio, aligned to the source timeline. If the source had no audio, the final is silent. Never deliver a silent substitute for an audible source: if audio extraction fails twice, fail that output.

## 3. ffmpeg recipe

Extract the source audio once. Try stream copy first, fall back to PCM:

```bash
ffmpeg -nostdin -y -i source.mp4 -map "0:$AUDIO_STREAM_INDEX" -vn -c:a copy source-audio.mka
# fallback only after copy failure
ffmpeg -nostdin -y -i source.mp4 -map "0:$AUDIO_STREAM_INDEX" -vn -c:a pcm_s24le source-audio.wav
```

Build the audio filter from the measured offset:

- positive offset: `adelay=<offset_ms>:all=1,asetpts=PTS-STARTPTS,apad=whole_dur=<duration>,atrim=duration=<duration>`
- negative offset: `atrim=start=<absolute_offset>,asetpts=PTS-STARTPTS,apad=whole_dur=<duration>,atrim=duration=<duration>`
- zero offset: `asetpts=PTS-STARTPTS,apad=whole_dur=<duration>,atrim=duration=<duration>`

Remux: discard any accidental generated audio, keep only the generated video stream, trim to the exact source duration and add the source audio:

```bash
# Audible source
ffmpeg -nostdin -y -i raw.mp4 -i "$AUDIO_ABS" \
  -filter_complex "[1:a:0]$AUDIO_FILTER[source_audio]" \
  -map 0:v:0 -map '[source_audio]' -t "$SOURCE_DURATION" \
  -c:v copy -c:a aac -b:a 192k -movflags +faststart final.mp4

# Silent source
ffmpeg -nostdin -y -i raw.mp4 -map 0:v:0 -t "$SOURCE_DURATION" \
  -c:v copy -an -movflags +faststart final.mp4
```

Do not use `-itsoffset`, `-shortest` or `-avoid_negative_ts make_zero`: they can shift or truncate the video timeline. If the generated video is too short, fail the output; do not loop or freeze frames to pad it.

## 4. Premiere Pro / After Effects equivalent

1. Import the source clip and the new render. Put the render on V1 and the source on V2 (muted) as a timing reference.
2. Align the first frames. Trim the render to the exact source duration with the razor or trim tools. Do not stretch it with Speed/Duration.
3. Keep the source's audio track on A1, unlinked from the source video; delete the render's own audio if any.
4. If the source audio started later or earlier than its video (offset), slide A1 by the same offset.
5. Re-add nothing to captions in the render: the source captions were preserved by the prompt; if they were not, rebuild them from the source (copy the caption layer's text, font, position and timing) rather than regenerating.
6. Export at the source frame rate and aspect; check the short edge (720 or 1080).

After Effects: use it to repair a caption or logo that the generator damaged (track the source element over the new render, mask it back) and to fix a short flash or pop at a cut.

## 5. QC gates

Probe each final and require all of these:

- plays and contains a video stream;
- duration within max(1/fps, 0.10) seconds of the exact source duration;
- display aspect within 1.5 percent relative error of the source;
- displayed short edge within 8 pixels of the selected 720 or 1080;
- audible source: an AAC audio stream exists; silent source: no audio stream.

Visual checks (watch the whole clip, not a thumbnail):
- the replaced person or product matches the reference in every shot, including cuts, reflections and shadows, and the original does not appear for any frame;
- unmapped people and objects are unchanged;
- captions, subtitles, logos and on-screen text are unchanged in wording, style, placement and timing;
- camera moves, cuts and pacing match the source frame for frame;
- no hands, fingers or limbs are fused with the new object; no flicker on edges of the replaced target.
