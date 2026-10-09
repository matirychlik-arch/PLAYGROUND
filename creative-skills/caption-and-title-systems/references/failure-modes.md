# Failure modes

Contents:
1. Symptom to cause to fix table (animation, layout, text)
2. Caption-specific failures
3. Evidence: what each check proves
4. Export notes
5. Delivery rules

## 1. Symptom, cause, fix

The left column is the source contract's symptom or refusal; the right column is how it shows up in Premiere Pro and After Effects.

| Symptom / refusal | Contract (source) | In Premiere / After Effects |
|---|---|---|
| Frame or motion field unknown | Installed tooling determines what is supported; source changes do not update an installed bundle | A MOGRT or preset made in a newer app version fails or loses properties in an older one; match versions |
| Fill under hug / unresolved slot | Fill needs a resolvable parent axis; absolute frames need dimensions | A layer sized "to fit" a box with no defined size collapses to zero; give the container explicit pixel dimensions |
| Child or keys exceed lifetime | Local spans must fit the owner; frames exclude their exact endpoint | Keyframes beyond the layer out point or precomp length never play; the last frame of a layer is not drawn |
| Animation object rejected | Animation is an array; frame motion is an object | One property, one chain of keys; do not mix a motion preset and manual keys on the same property |
| Duplicate property tracks | Replacement channels have one owner; raw offsets add and uniform scales multiply | Two drivers on one property (keys plus expression, or two Motion-effect copies) fight; use one owner per property |
| Incorrect shader animation target | Effect index selects a declared effect; effect parameter is its existing numeric key | Keyframing the wrong instance when two copies of an effect exist; name and reorder effects, then key the right one |
| Missing shader / texture / GL | Rendering fails; texture binding uses the imported handle, not a URL | A missing plug-in, font or footage placeholder renders as bars or fails the export; collect files and fonts |
| Shader raster overflow | Raster bounds exclude overflowing child or stroke or ink; clip or inset the content | Glows, blurs and strokes clip at the layer boundary; enlarge the layer (comp or precomp bigger than the content) or add padding |
| LUT / shader adjustment / HTML | Unsupported by the native renderer | Use app-native color tools; do not expect HTML or web rendering inside titles |
| Text fill / rect stroke object | Text uses color; rect uses flat stroke color and width; path has a stroke object | Different layer types expose different property names; text fill is "Fill", shapes have Fill and Stroke groups |
| Missing glyphs | Font registration does not establish glyph coverage; icon paths have no font dependency | Polish letters render in a fallback font or as boxes; test ą ć ę ł ń ó ś ź ż and use a covering face; use shape icons rather than icon fonts |
| Stretched footage | Fill stretches; contain and cover in a slot preserve aspect | Non-uniform scale or "Set to frame size" misuse; scale uniformly and crop |
| Unexpected source moment | Source in and trim are source time, not placement time | Clip shows the wrong moment: you set a timeline time where a source in point was needed |
| Lost human edits | A whole-script build replaces the timeline; fresh inspection plus bounded edits preserve other work | Regenerating a sequence from a script overwrites manual fixes; apply changes to the existing sequence |

Mixed-up clocks cause most animation bugs: a keyframe placed in timeline time when the layer expects layer-local time, or a source in point confused with placement. Re-read the contract table in `title-animation-and-motion.md` section 1 before debugging.

## 2. Caption-specific failures

| Symptom | Likely cause | Fix |
|---|---|---|
| Captions drift progressively | Bad alignment, wrong frame rate on import, or transcript made from audio that was later retimed | Re-transcribe on the final audio; match SRT frame rate to the sequence |
| Constant offset | Transcript made on a different audio source (e.g. pre-edit file, or video with lead silence) | Shift the whole track, or regenerate from the right source |
| Words missing | Quiet words skipped by speech-to-text, or chunking dropped a word | Compare caption word count to spoken word count; with an authored script verify every line |
| Wrong spelling of brands/numbers | Transcript used instead of the authored wording | Replace with authored words; keep the transcript only as the clock |
| One font size looks different on some cues | Cues were individually shrunk to fit | Re-chunk the cue; hold one size |
| Empty or odd letters | Font lacks glyphs and silently fell back | Pick a covering font; recheck after export |
| Caption sits on the face or label | Fixed position used for a UGC or demo video | Run the clearance procedure; do not shrink text to make room |
| Caption cut off at the edge | Outside the safe box, or stroke and shadow pushed past the frame | Move inside the safe box; include stroke and shadow in the bounds check |
| Caption flickers between cues | Overlapping or exclusive-out-point mistakes | Make cues non-overlapping; out point of one equals the in point of the next |
| Captions vanish at the end | Cue past the sequence end, or the caption track shorter than audio | Extend the track; check the tail of the voice |
| Burned export shorter or silent | Re-encode dropped the audio stream or trimmed the tail | Probe both streams; duration within about 1 s of the master and audio ending within 0.2 s of the video end |
| Hook and first caption collide | Hook outlived the first body word | End the hook at the first body-word boundary |

## 3. Evidence: what each check proves

- A dry-run or layout validation proves structure, not what the viewer sees.
- Inspecting parameters at a time proves evaluated values, not that an effect executed and not world-space geometry.
- Rendering a frame or exporting proves actual pixels; a contact sheet samples frames.
- A media probe proves the real streams; file extensions do not prove codecs or bit depth.
- A flat-frame sweep and a document check are not a visual or audio verdict.
- Ten-bit encoding does not guarantee ten-bit processing; a shader or glow may still be processed at 8 bits.
- Frame equality requires matching assets, fonts and runtime. Matching file hashes are not required and usually do not occur (container metadata and encoders vary).
- An interrupted export, or a script that ran without an export call, is not a finished movie.
- Visual review has to be based on looking at frames of the delivered file, not on the settings or the prompt that produced it.

## 4. Export notes

- Project size and fps are fixed when the project is created: choose 1080x1920 at 30 fps (or the platform's native fps) before building layouts, not after.
- A typical delivery: H.264 at about 8 Mbps video target for 1080x1920, AAC audio. A bitrate target is not constant bitrate or an exact file size, and audio and container bytes are extra. Lossless and a bitrate target are mutually exclusive. Ten-bit HEVC or AV1 are options when the destination accepts them; platforms recompress anyway.
- Hardware encoding (GPU) and the compositor are independent; effect rendering can still differ between CPU and GPU paths. Judge by exported pixels.
- Browser or web previews of shader-like effects are not universally equivalent to the native render. Use native output for the final check.
- Picture-only overlays: composed media does not carry its audio; plan audio on the spine.
- Render cost depends on media, resolution, effects and concurrency; there is no fixed render-time estimate.

## 5. Delivery rules

- Deliver the finished video plus the SRT plus the clean master. Every retry starts from the clean master.
- If captions fail, deliver the clean video and say what failed and at which interval. A caption failure is never a failed job.
- Return only what was verified. Name any unverified stage (for example, "inspected the export at 6 frames; did not step through every cut").
