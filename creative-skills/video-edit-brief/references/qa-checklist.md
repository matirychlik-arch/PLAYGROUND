# QA checklist for a finished edit (run it on the exported file, not the project)

Contents
1. Why the gate exists (past failures)
2. Set the validation target
3. The 16 checks (with severity and pass rules)
4. Audio rules
5. How to inspect: coverage you must reach
6. Identity, edges, look: the three crop sheets
7. Fresh eyes (optional)
8. Fix order
9. Deliver and report

Run the gate on the exported file you will hand over. A render that finished without error is not a pass. Write the result down: one line per check with PASS / FAIL / NOTE and frame numbers. Do not hand over a version with an open BLOCK item.

## 1. Why the gate exists

| Project | What reached the user | What the gate would have caught |
|---|---|---|
| Chant edit v2 | 285 frames | the reference has 283 video frames; its container said 9.517 s because of the audio. The export also carried no bt709 tags |
| Polarity triptych | 233 frames against the film's 230 | frame count |
| Edit RC1/RC2 | the limiter left +0.4 / +1.0 dBFS peaks after AAC encoding | true peak measured on the encoded file |
| Handoff list | 23 fixes marked "confirmed"; at least 2 were not applied | never mark what was not re-checked |
| Quote edit v2 | words misplaced, holed or faded on 5 cuts | frame-pair sheets at text frames |
| Quote edit v3 | 60p-native motion came back 24p-stepped (36 -> 14 unique frames, 32 -> 13) | cadence per cut |
| Signal v5 | grey matte holes between the legs on a white backdrop | mask edges at 100% |

## 2. Set the validation target

- Remix (default): the export is tested against YOUR planned output target (size, frame count, fps, ending, audio), your shot/story/motif plan, the intended identity and the user's explicit locks. A new order, scene, duration, text or format is not a failure because it differs from the reference.
- Exact: the export is tested against the locked source and the explicitly requested changes only.
- Never rewrite the source measurements to make the output pass. Never call a new authored scene an observed source event.

## 3. The 16 checks

BLOCK = do not call the edit finished. FIX = repair in bounded attempts (section 8), otherwise report as a limitation. NOTE = context, disclose if material.

| # | Check | How | Pass rule | Severity |
|---|---|---|---|---|
| 1 | Frame count | decode the export and count; compare with the plan | equals the planned frame count (remix) or the locked source count (exact). Never use audio or container duration as frame count | BLOCK |
| 2 | Presentation timing | actual frame timestamps and rational fps | matches the plan; equal average fps does not prove constant timing | BLOCK |
| 3 | Duration and ending | actual last video frame; audio end separately | the authored ending, including audio tail; no accidental truncation | BLOCK |
| 4 | Format and colour | width, height, pixel aspect, pixel format, colour tags | matches the plan; correct bt709 tags on SDR; never re-tag HDR as SDR | BLOCK (size) / FIX (tags) |
| 5 | Audio | probe streams, check sync, measure loudness on the encoded file | planned song/SFX/dialogue present and in sync; new mix true peak <= -1.0 dBTP | BLOCK (missing) / FIX |
| 6 | Complete visual coverage | look at every frame and every second (section 5) | gap-free; readable detail on every effect, text and transition | BLOCK |
| 7 | Story, trick or motif | compare with planned shot roles | the chosen arc or motif is delivered through purposeful shots; a non-narrative edit does not need an invented plot. Exact: the source device at its locked frames | BLOCK |
| 8 | Identity and cast | every appearance, including back, profile, body crops, occlusion, distance, reflections, stylization, extras | correct identity and continuity in ALL planned shots; no role swap or mannequin; intended concealment stays concealed | BLOCK |
| 9 | Text, logos, marks | full sheets and native crops of text, garments, screens, props | planned words and design; no pseudo-letters, no doubled captions; retained footage keeps its original attribution marks and watermark | BLOCK |
| 10 | Mask edges | 100% crops on bright, dark, fast-motion and hair states | no holes, halos, lag or chewed silhouette | FIX |
| 11 | Bars and edges | every frame edge vs the planned composition | no accidental bars, rotation wedges or cropped required elements. A declared hand-drawn border is intentional | BLOCK |
| 12 | Cadence and retiming | count unique and repeated frames in retimed intervals | planned cadence without accidental judder. A run of 2-3 identical frames inside a 0.3-1x cut that should move smoothly is a FIX | FIX |
| 13 | Text placement | each rendered text event vs the title table | no clipping, wrong font fallback or unreadable mandatory words | FIX |
| 14 | Look and material | native crops of every distinct texture, light and grade state | coherent chosen aesthetic; no accidental muddy faces or default decoration | FIX |
| 15 | Declared source reuse | compare each reused segment with its true source range | reuse attribution and timing correct | BLOCK |
| 16 | Cut and event positions | every planned boundary and its neighbouring frames | follows the plan; no neighbouring-shot leak, no lost event | FIX |

Slow-motion fallback for check 12: 0.3-1x blend the two neighbouring source frames weighted by the fractional index; below 0.3x or on fast limbs use the nearest frame; freeze holds are integer frames.

### Quick commands (any machine with ffmpeg)

```
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,sample_aspect_ratio,pix_fmt,r_frame_rate,avg_frame_rate,nb_read_frames,color_primaries,color_transfer,color_space:format=duration -of compact=p=0 export.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,profile,sample_rate,channels -of compact=p=0 export.mp4
ffmpeg -hide_banner -nostats -i export.mp4 -map 0:a:0 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
# contact sheet with ABSOLUTE frame numbers (drawtext BEFORE select), 8 frames per page:
ffmpeg -v error -y -i export.mp4 -vf "scale=300:-2,drawtext=text='%{n}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.7,select='between(n\,0\,7)',tile=4x2" -fps_mode passthrough -frames:v 1 sheet_000.jpg
```

Select frames by index, never by seeking (`-ss`) for an exact frame; it lands 1-2 frames off on x264.

In an NLE you get the same by stepping with the arrow keys, displaying timecode or frames, and exporting stills at the checked frames.

## 4. Audio rules

- Original soundtrack reused: copy the stream, do not normalize or limit it. Require the same start offset relative to the first video frame. A different packet checksum is a fidelity difference; first remux from the original file.
- New mix (your remix audio, or a changed exact soundtrack): limiter ceiling low enough that the ENCODED file measures true peak <= -1.0 dBTP (set `level` off so the limiter does not renormalize to 0 dBFS); report integrated loudness; follow a requested loudness target.
- Listen with the actual playback when you can. Otherwise write "measured, not listened". Never claim an audible check from metrics alone.
- Lyric / song captions: verify the words in the final export (not only in a cue file): every cue's first, peak and last frame, spelling, actual loaded font, geometry, layer order and sync to the audio. After the last text render and the audio mux, inspect the beginning and all final seconds through the last video frame and planned audio tail. The last lyric stays for its interval, the song is still present, no short SFX file truncates it, and no unrequested silence or fade was introduced.
- Music and SFX are recordings; procedural noise, synthesized beats and generic whooshes fail audio QA.

## 5. How to inspect (coverage you must reach)

- Visual gate covers EVERY frame of the export and every second including the partial last second. Sparse key frames, two overview sheets or playback alone are not enough.
- Work in chronological batches of contact sheets (frames numbered absolutely), with native-size crops for anything unclear. Add a close look at every effect, text and transition at its start, peak and end frame.
- Write down which ranges you looked at; the union must be 0 to N-1 with no gaps. A partial report states the gaps.
- Check every cut boundary and the frames either side, every one-second interval, the first and last frames, and the single-frame inserts (white, black, solid, ghost) that sparse sheets miss.
- Exact mode additionally compares source/output pairs ("Original | Ours" sheets, 8-12 pairs per page, absolute frame labels) for every frame through the declared mapping. An explicit timing change needs a mapping-aware comparison, not same-index pairs. A similarity score never proves exactness.
- Remix: compare craft evidence (texture, type, motion, music) with labelled source and output times; do not pretend the timelines match.
- Fixing: after every fix, run the gate again, plus a regression check of the affected shots against the previous version.

## 6. Identity, edges, look: the three crop sheets

- Identity: one tile per shot where the face is clear, cropped around the face, plus the identity reference as the first tile. Check head shape, hair, brows, skin tone, moles, earrings, glasses and wardrobe per look. Then check every frame with a second person: generation has swapped roles, painted a faceless white mannequin and put the hero's hair on the wrong person.
- Face integrity: no face-swap tool, mesh warp, face paste, facial inpaint, manual eye/nose/mouth drawing or skin retouch changed identity pixels. Tracking and whole-layer transforms are fine; a separate decorative overlay must stay identifiable as an overlay. Background-cleanup masks must protect every visible person including extras and the full head and hair silhouette. If the generated face is wrong, regenerate it; never hide it with compositing.
- Mask edges: 100% crops at four places: brightest background, darkest clothing, hair, fastest motion. A matte that lags the plate is a frame-rate mismatch.
- Look: native crops for every texture, grade and light state, paired with the corresponding source frames (exact) or relevant labelled exemplars (remix). Compare brightness, neutrality, saturation and noise. Generated plates can arrive about 40% less saturated than a clean reference. An exact remake of a clean source adds no grain, vignette or accent colour.
- Threshold / xerox looks: crop every identity-legible medium close-up and close-up against the source. A default threshold can crush the face to near-black where the reference keeps eyes, nose and mouth readable; soften the whole-plate filter against the complete shot, never retouch the face locally.

## 7. Fresh eyes (optional, one round)

For long or dense edits ask a collaborator (or a second AI pass) who has not seen the build to look at the complete export and list "what reads cheap, wrong, unreadable, mistimed, or like a different person". Filter what comes back:
- Exact mode preserves intentional source devices (strobe, two-frame flashes, a black ending). Remix checks whether each authored device serves the new story rather than defending it because the reference used it.
- Fix identity breaks, garbled text, dead holds, clipped words, judder, and missing or extra frames.
- Do not chase a score: accepted aura films scored 5-6.5 out of 10 from fresh eyes. After fixes run one regression check; a second review round existed once only to undo a regression the first round introduced. No second round unless the first found BLOCK items.

## 8. Fix order

1. Fix in the edit first (no new generation): timing and in-points, authored text and grade, the audio mux, mask edges of the complete generated subject, cadence (follow the planned pattern, re-apply digital zooms at the output frame rate), framing (follow the planned composition; an aspect mismatch never justifies a blind centre crop). Crop and pad replace paid reframing; blending frames replaces paid frame-rate boost.
2. Re-cast from what exists: another in-point in the same clip, another take already made, unused seconds of a plate, a still with camera keyframes. Source reuse is allowed only when it fulfils the task; a failed target replacement cannot become "keep original" because its face is hidden or small.
3. Regenerate only for a failure from this list: identity, wardrobe, garbled text or logo, anatomy, a matte-hostile background, or a missing beat that no other footage supplies. "A better take" is not a failure.
   - A single failed shot: regenerate that shot alone, as a clip about twice as long as its slot (gestures run 1.5-2x slower than prompted; hearts prompted at 2.7-3.6 s arrived at 8-9.75 s) and pick the in-point from actual frames, never from promised timecodes.
   - Half or more of a batch failing for one cause: fix the cause and redo the batch once.
   - One retry per failed item; never resubmit the same request hoping for luck; never regenerate a whole batch for one bad shot.
4. After every fix run the full gate again. Do not mark a fix as done until the gate shows it fixed on the new export.

## 9. Deliver and report

- Name versions v1, v2, ... Never call a version "final" or "accepted" before the user does.
- Deliver the export, plus the project file so revisions need no new generation. Exact: also an aligned "Original | Ours" comparison. Remix: a labelled craft comparison only if useful.
- Video: SDR bt709, H.264 High, yuv420p, CRF about 18, faststart is a safe default for short-form. Heavy per-frame grain makes huge files (about 29 Mb/s at CRF 20): produce a smaller social copy and keep the master.
- Report in plain words: what was made, what is generated and what is edit work (footage, text, stickers, transitions, grade and tracking are edit work; music and SFX are recordings with provenance), what was checked (frame count, sound, faces, text) and what is still off. Describe shots in words, not ids. Say "measured, not listened" when that is the case; never write "checked" for a check you did not run.
- Remix: state the authored changes that matter (new story, scenes, order, format, text, music) separately from unmet locks and production defects. Do not apologize for creative freedom. Exact: keep a short "not 1:1" list of real deviations.
- Example limitation lines: "the T of NINETY sits behind the new head on mid frames so it reads NINE,Y; fix is to move the word, but then it is no longer at the reference's position"; "slow-motion cuts step at 24 fps where the reference is smooth 60p; partly fixable by blending the two neighbouring frames"; "the two fastest shots move at 24 images per second where the reference shows 60; not fixable in the edit"; "your track instead of the reference's: the reference's music hides a jump at about 12.4 s that the cuts follow, so synchronization changes"; "lip-sync is approximate; the words on the face cover it".
- Handoff note for the next session: what this is, current versions and what changed, user decisions with their words (separate from your own choices), trick line and structure, pipeline as executed, timing grid, gotchas, remaining limitations. Prompts stay verbatim in English.

### Font QA

For unchanged locked words confirm original shapes, placement and animation. For authored words verify the font actually loaded, glyph coverage, bounds, spacing, weight and effects against the title design. A missing font never stops the edit: choose the closest loaded match, tune it, and list a material visible difference. Do not accept a blind Arial/Inter/browser fallback or a canned glitch preset.
