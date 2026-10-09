# Analysis: deconstructing the reference (free stage)

This stage costs 0 credits (`sandbox_exec` is free) and decides almost every credit spent later. Its
products are the measured source record `analysis/breakdown.json`, the task contract below, and a separate authored output plan. Source observations never silently become output locks.
Nothing paid starts until the breakdown and finite verified-priced whole-workflow plan exist and task/account
authority covers them under `references/budget.md`. Continue autonomously within that hard cap;
do not ask for credit confirmation, present a consent control or wait for a user reply. The internal
ledger records a plan and never creates authority. If a service requires unavailable interactive
consent, use a supported authorized fallback or state a blocked/partial result declaratively. Never
bypass permissions, buy credits or increase the cap. Dependent stages may carry verified current non-executable planning upper bounds under `budget.md` §8.2 / `mcp-api.md` §4.1; they still require real upstream result IDs and fresh exact quotes before activation/submission. Never invent future media IDs or shrink the whole-workflow ceiling to the first ready still. Creative and font choices remain autonomous.

Identify requested facial/identity changes separately from camera motion, grading and source graphic overlays. Face boxes/landmarks are read-only measurements for QA, tracking and whole-plate alignment; the CODE route may not swap, warp, paste, redraw or retouch a face/head. Route likeness and facial-feature changes to a supported authorized image/video model, preserving the composition required by the authored plan or exact source lock. Missing model capability never becomes a local face-edit fallback. Record a source cheek/eye sticker as a separate observed graphic, not as anatomy to reconstruct in code. Background-cleanup masks must cover every visible person, including extras and complete head/hair silhouettes.

Why it matters, from past projects:

- **Signal v2 (Aura)** copied the timing and lost the trick (an outfit change plus a colour-matched
  element on every signal). Rejected.
- **City Rhythm v7 (Aura)** was treated as video. The reference was a locked-camera photo series.
  Verdict: "вообще не то".
- **Yaong v1** was analysed on 10 fps sheets, which missed the main transition: a 3–5 frame
  overexposure "flashlight" burn. A second pass at native fps found it.
- **Altman** included about 176 credits of hidden-face cuts. Their role must be checked against replacement scope and continuity; face visibility alone never proves that processing was unnecessary.
- **Auto cut detectors** found 19 of 49 cuts (whip edit), 9 of 35 (strobe edit) and 28 of 54. On
  grainy xerox footage the detector fired every 2 frames.

The sheets are the ground truth. The detectors only make proposals.

## Task mode, source evidence and output target

Before planning, write `analysis/task-contract.json` with `mode` (`remix` or `exact`), `mode_reason`, `explicit_locks` and `creative_freedoms`. **REMIX is the default.** Select EXACT only when the user explicitly requests the entire edit 1:1, the same sequence, or only a subject replacement with the rest preserved. A supplied reference, "like this", or a request for its style does not by itself select EXACT. A specific lock such as the same song or exact lettering locks that property in REMIX; it does not lock the entire edit. Infer the mode from the request without a question or confirmation. For a continuation/revision, retain the existing deliverable's task contract and apply the latest steering; a new independent deliverable defaults to REMIX.

- **REMIX:** inspect the complete reference as evidence, then author new scenes, order, timing, text and format as appropriate to the user's intent. Preserve explicit locks and intended identity; use observed aesthetic, material, typography, music and motion principles purposefully. New decisions need a shot/story reason, not permission for arbitrary glitch or random templates.
- **EXACT:** retain the source sequence, framing, actual timing, text, format and audio except explicit requested changes. All source-equality rules below apply to this mode or to specifically locked source properties/intervals.
- **Separate records:** `breakdown.ref`, `breakdown.cuts` and its legacy `format_lock` record measured SOURCE geometry/timing for analysis helpers. Keep their source frame indices and original master unchanged in both modes. They are not the REMIX output timeline. Save the output target and authored shots in `plan/creative-plan.json`: `output_target` (width, height, rational fps or PTS plan, frame count/video endpoint, audio endpoint, color policy), story/motif, shot roles, text/audio plan, source-evidence links and deliberate adaptations. Routing/renderer plans use this output target. Do not overwrite source metadata to make an output check pass.

Record an output decision as `authored`, its evidence and rationale, separately from `observed` source facts and `uncertain` interpretations. An intentional REMIX change is not an exact-match failure; an unmet explicit lock, production defect or uninspected range is. Do not claim that a creative addition was seen in the reference.

For an EXACT task with explicitly changed timing or format, keep the original source record and save the requested output target separately. Add `source_output_mapping` to the creative plan: source/output frame and PTS intervals, the requested transform/edit, remaining unchanged property locks and the actual user instruction authorizing each exception. QA checks the output target and mapped unchanged content; the legacy global same-grid check must not reject the very timing change requested. A lock on one property/interval stays local in either mode, and full native source/output inspection remains mandatory.

## Reference discovery and the three reference roles

Read [creative-quality.md](creative-quality.md) before research and motion planning. A supplied reference remains the primary source of observed craft and source facts; the task contract determines what the output must preserve. When none was supplied, proactively search current relevant TikTok and YouTube Shorts clips using the task's subject, audience, format and existing context. Check visible recency and popularity evidence at search time rather than calling a remembered example "popular". Select the best-fitting accessible primary autonomously; do not ask for a link or a vote. Discovery is free research, not permission to buy media or generate samples.

Actually view every shortlisted clip that remains eligible from beginning to end before selecting it. Use a supported full-clip viewer, or access the actual media and inspect complete frame coverage; listen to its audio through a supported listening capability when available. A search snippet, title, transcript, thumbnail, preview fragment or metadata page is not proof of viewing the video. Log inaccessible/unviewed candidates as rejected or unresolved, never as viewed. Try another authorized candidate or source when one cannot be inspected. If no suitable primary can actually be inspected, report that concrete capability limit without questions or an invented reference. An inaccessible explicitly designated reference must not be silently replaced by a discovered one.

Choose exactly one primary and save its identity and actual viewing evidence in `analysis/references.json`. For discovered clips record URL/media ID, creator/title when available, discovery date, publication date and visible engagement evidence, duration, complete viewed ranges, viewer/media evidence and selection reason. These are observations, not claims of creative ownership or permission to republish. After selection, run the same complete native-frame, per-second and audio analysis below as for a supplied reference; discovery never replaces it.

Every project must inspect and record three reference roles: **montage/motion**, **music/audio**, and **font/typography**. The primary can fulfill all three when its content is sufficiently clear. Record exact shot/transition evidence, an actually inspected/listened audio source or measured-only limitation, and native-resolution glyph specimens. "No text" or "silent" is an observed source state. In EXACT preserve it unless changed explicitly. In REMIX add text or music only when it serves the authored story and user intent, and label that addition in the plan. Supplementary clips, tracks and font specimens may inform creative freedoms; they never overrule explicit locks or masquerade as properties of the primary.

For required replacement or new music, inspect an authorized TikTok track source or a suitable stock music source; for required new/replacement SFX inspect stock recordings. In EXACT keep the primary soundtrack and existing SFX unless explicitly changed. In REMIX decide the soundtrack from the user intent, explicit locks and authored rhythm; reuse a suitable reference track or select an authorized available recording. Record source IDs, audition evidence and supported use conditions with the assets. Do not synthesize music, beats or SFX in code. Code may only measure, trim, align, mix and apply measured processing to selected existing audio. Download selected stock assets through an available permitted operation. If an asset remains inaccessible, retain actual source audio where it fits the task and document the unresolved change; never claim the missing asset was delivered or synthesize an imitation.

## 0. Order of work

Research and supported media viewing use the available search/browser/media tools. All decoding, measurement and compositing commands run in the sandbox. Start each processing command with `source "$HF_WORKFLOWS/katana/scripts/rr.sh"`
(`references/sandbox.md` §2) and `rr_ws <slug>`. End each multi-step call with `rr_save` unless the
next call follows immediately: files vanish ~10 s after a call ends.

| #   | Step                                     | Command / action                                                                                                                                                             | Output                                                                                                                                                                                                                   |
| --- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0a  | Resolve task contract                    | Default REMIX; EXACT only for an explicit entire-edit match / same sequence / subject-only replacement                                                                       | `analysis/task-contract.json`                                                                                                                                                                                            |
| 0b  | Discover/inspect reference roles         | Supplied primary first; otherwise search and fully view eligible TikTok/Shorts candidates; inspect montage, music and font evidence                                          | `analysis/references.json`                                                                                                                                                                                               |
| 1   | Fetch + probe, preserving original bytes | `python3 $RR/fetch_ref.py $W <link or media url>`                                                                                                                            | `ref/ref.mp4`, `ref/ref.json` (`fps` as a rational string, `nb_frames`, `video_duration`, `audio_duration`, `rotation`), `ref/meta.json` for page links                                                                  |
| 2   | Decode every frame                       | `python3 $RR/analyze_ref.py $W --review-size --no-window` without `--max-seconds` or `--no-every-frame`                                                                      | `analysis/analysis.json` (cut candidates with scores, window/letterbox, flashes, cadence, look stats per cut, text-region candidates, motion energy) + sheets of ≤125 KB each (§1.2); the script prints every sheet path |
| 3   | Audio                                    | `python3 $RR/audio.py beats $W`, `python3 $RR/audio.py cutsync $W`; `audio.py align` only when a second audio exists (§6.4)                                                  | bpm, beat grid, onsets, sections, loudness, cut-vs-onset table                                                                                                                                                           |
| 4   | Key frames                               | `python3 $RR/frames.py keyframes $W`                                                                                                                                         | full-res frame per cut (later the composition refs for stills)                                                                                                                                                           |
| 5   | Full-duration overview + timeline        | Inspect the cut overview, timeline and a one-second overview covering every second including the final partial second; batch images within tool limits (§1.1)                | first impression, structure, draft trick line (§2)                                                                                                                                                                       |
| 6   | Complete every-frame read                | Inspect every native-fps page in chronological batches, ≤4 images per call, for the entire reference; never skip steady or detector-confident spans                          | gap-free inspected-frame manifest plus per-second/event logs (§1.5–1.6)                                                                                                                                                  |
| 7   | Resolve all visual details               | Native-resolution crops and every-frame strips for all unclear texture, lighting, text, graphics, motion, effects and transitions (§1.4); split long ranges, never subsample | measured geometry, appearance and event timing                                                                                                                                                                           |
| 8   | Measure                                  | look crops + stats (§5), text boxes (§4), identity per cut (§7)                                                                                                              | numbers for the breakdown                                                                                                                                                                                                |
| 9   | Review motion three ways, then write     | Complete the three distinct internal reviews below; write `analysis/breakdown.json` (§8), validate (§8.6), `rr_save`                                                         | source evidence, separate authored output plan and `analysis/motion-reviews.json`                                                                                                                                        |
| 10  | Report progress                          | 3–5 plain-language lines (§10), with the labelled overview sheet when useful                                                                                                 | continue autonomously within verified task/account authority and the finite hard cap                                                                                                                                     |

Exact script arguments: `python3 $RR/<script> --help`. Use the script for actual accepted argument names, never to override the no-question, fidelity or
budget policy. Legacy diagnostics do not create intake or credit questions. Resolve them within
existing task/account authority or stop that operation without asking or waiting for the user.

`fetch_ref.py` preserves the original downloaded media bytes at the legacy `ref/ref.mp4` path; inspect the real container/codec rather than inferring MP4 from that name. It must not automatically crop odd dimensions, change color/bit depth, normalize cadence or replace/delete the original. Create any needed SDR or resized preview as a separate labelled file; analysis and exact comparison retain the original source.

Full native-frame analysis is mandatory for the selected primary reference, regardless of duration, cut count or credit cost. Shortlisted candidate clips must still be fully viewed before selection; supplementary evidence is inspected for its documented role.
Decode all N video frames into chronological native-fps contact sheets before selecting a route.
An overview or detector result never replaces inspection. Batch decoding, viewing and persistence
within resource limits; continue through the remaining batches autonomously. A speed target is not
permission to skip frames. Reuse cached sheets and parallel independent ranges when supported.
The mandatory baseline uses `--no-window` because the helper otherwise crops to its detected
picture window. Keep the detected window/letterbox metadata separately for detail measurement
and explicitly copy the measured source window into the render plan when needed: full-canvas
inspection does not mean that the source lacks a window. Add window/texture crops separately.

## 1. Reading the sheets

### 1.1 What you look at

- **Overview sheet** (`sheets/overview_pNN.jpg`): one mid frame per proposed cut, up to 40 per page.
  Use it for classification and the trick line; it is not complete temporal coverage. Also make
  a one-second overview: one representative frame for every interval [k,min(k+1,D)), including
  the final partial interval, and include frame N-1. Select from the decoded frame timestamp map
  with `rrio.py sheet ref/ref.mp4 sheets/seconds_pNN.jpg --indices <comma-separated-indices>
  --max-bytes 120000`, splitting the explicit list into readable pages. The source-verified
  `--indices` option prevents the helper's default adaptive sampling.
- **Timeline** (`sheets/timeline.jpg`): the cut score, structure, histogram and luma curves with cut
  markers and frame ticks. Read it with the overview; spikes, flat stretches and strobing guide
  additional magnification, never which frames may be omitted.
- **Every-frame pages** (`sheets/ef_NNN.jpg`): every frame at the reference's native fps, labelled
  with its **absolute frame index**. A page holds 48 frames for landscape (8 × 6) and about 50 for
  portrait (10 × 5): 2 s at 24 fps, 1.6 s at 30, 0.8 s at 60. Use these for cuts, transitions, text
  in/out and inserts. Never read a 5 or 10 fps sampling as the cut list.
  - **Which pages:** all of them, in order. `analysis/analysis.json` `sheets.every_frame[]` gives
    each page's inclusive `f0`–`f1`. Inspect every page from F0 through F(N-1), including steady
    holds, blank frames, low-motion passages and the fractional tail. Detector flags prioritize
    additional crops only. No duration threshold, confidence score or clean look exempts a range.
    Inspect the full canvas as well as the picture window. If generated sheets crop away borders,
    captions or other canvas pixels, add full-canvas consecutive-frame sheets with `rrio.py sheet
    --indices`; window crops alone never establish complete visual coverage.
  - The detector's marks are proposals only: a red bar is a cut, orange a low-confidence cut,
    magenta a burst sub-cut, yellow a flash or solid frame, violet an invert, a grey `?` a near
    miss, and `=` a repeat of the previous frame.
- **Strips and crops:** native resolution around anything ambiguous (§1.4).

### 1.2 Image budget per call

`image_paths` takes at most 4 JPEG/PNG files and **512 KiB in total**.

- Run the machine pass with **`analyze_ref.py $W --review-size --no-window`**. It caps every sheet (every-frame
  pages, overview, timeline, detail) at 125 KB, so **4 pages fit in one `image_paths` call**.
  Measured on the Yaong ref: 6 every-frame pages of 48 frames at 1588 px wide, 116–123 KB each, with
  frame labels and faces still readable.
- Without `--review-size`, pages may be up to 500 KB each (`--page-bytes`), which means one page per
  call. If you have such pages, re-run with `--review-size` instead of dropping any.
- For every image call, check actual file byte sizes and pack at most four files whose summed
  size is at most 524,288 bytes (512 KiB). Four files of 125,000 bytes fit; larger images may require
  two files or one. Never assume that three larger files fit. Split batches without omitting pages.
- Never drop a page you need to fit the budget. Split across calls instead.

### 1.3 Label check (on the first page)

The first tile of a page must carry the page's start frame, not 0. `analyze_ref.py` pages do this
by construction: page 2 of the Yaong ref starts at F48. The check matters for sheets you make with
ffmpeg. There, a `drawtext %{n}` placed after `select` numbers the selected frames 0..k; it has to
come **before** `select` to print absolute indices. If labels restart at 0 on every page, every frame
number you log is wrong. Fix the sheet before reading on.

### 1.4 Zooming in

For a script-made zoom, run
`python3 $RR/analyze_ref.py $W --review-size --no-window --cuts-from analysis/analysis.json --detail 35:40`.

- It writes `sheets/detail_35_40.jpg`: at most 12 frames per sheet, at native pixels when the region
  fits 4 across. Pick the region with `--detail-crop x,y,w,h`.
- It re-runs the whole pass (a few seconds) and rewrites `analysis/analysis.json` and every sheet.
  `--cuts-from analysis/analysis.json` keeps the cut list you have corrected so far.
- Never use `--no-every-frame` or `--max-seconds` for the full analysis. A re-run rewrites sheets;
  keep the inspected manifest consistent with its source. The existing `--detail A:B` samples
  spans over 48 frames, so split each detail range into chunks of at most 48 consecutive frames
  or use explicit `rrio.py sheet --indices` lists. Never let detail sampling hide a transition.

Or pull the frames by index with ffmpeg, which leaves `analysis.json` alone:

```
ffmpeg -v error -y -i ref/ref.mp4 -vf "scale=450:-2,drawtext=fontfile=${FONT}:text='%{n}':x=4:y=4:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6,select='between(n\,35\,40)',tile=3x2:padding=3,format=yuvj420p" -fps_mode passthrough -frames:v 1 -q:v 5 sheets/zoom_35_40.jpg
```

- Select frames by index. Never use `-ss` for an exact frame; it lands 1–2 frames off on x264.
- `${FONT}` is any existing TTF, e.g. `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`; check it
  with `ls`.
- Keep the braces: in zsh, `$FONT:text` is parsed as a `:t` modifier and the filter breaks.
- `format=yuvj420p` before a JPEG output avoids the mjpeg "non full-range YUV" refusal of newer
  ffmpeg.

### 1.5 Keep a running event log while reading

One line per event, by frame. It is what the breakdown is written from, and it goes into
`analysis/events.txt` so subagents and later sessions can reuse it:

```
f0-3   magenta pixel-mosaic flash (entry), sharpening on f2-3
f4     starburst + lilac cut-out outline on; letters N-Y-A-N fly in from f5
f12-15 letters leave - NOT a cut, same shot
f19    burn to white begins (flashlight) - same shot
f22    CUT hidden inside the burn (new pose, both hands up); burn decays to f24
f24    word "ICH" on the face, white bold italic; 4th letter by f34
f29-33 zoom punch + blur pulse with a thin dark frame
f37-39 vertical smear, word smears out - same shot; next shot sharp at f40
```

### 1.6 Complete inspection manifest and per-second log

Save `analysis/coverage.json` with source identity, decoded frame count N, exact rational fps,
duration, inspected ranges, sheet paths, detail-crop evidence, unresolved ranges and a decoded
frame-to-PTS map. `analysis/frames.json` now records decoded `relative_pts`, `time_base`, verified CFR status and the actual final endpoint; verify these against ffprobe when needed. For constant
fps, derived f/fps timestamps are acceptable when the stream confirms that grid. For variable frame
rate, retain actual PTS. Cut/detail/every-frame page times use that map; cadence-rate detectors and timeline second ticks remain nominal approximations and must not set event timing. CFR-only export/prep/assembly helpers reject unsupported VFR rather than normalizing it. Preserve source streams or use an existing verified PTS-aware route; never silently
substitute nominal timestamps. Record each actually viewed sheet/range as [start,end_exclusive),
its path, timestamp bounds, reviewer and any detail crops. A generated sheet is not inspected until
seen. The union of inspected ranges must cover [0,N) with no gaps; duplicates/overlaps do not fill
missing frames. Verify every integer frame index and the final frame against the manifest.
These manifests are written and audited by the agent; bundled scripts do not generate them or
validate their coverage. Explicitly sort valid inspected ranges, reject out-of-bounds/empty ranges,
merge overlaps, and verify the merged union is exactly [0,N). Check each path exists and was
actually viewed. Check second intervals cover [0,D), including the partial tail, with frame/PTS
references consistent with the decoded map. Record PASS only after both union checks succeed.
A successful `analyze_ref.py` or breakdown validator exit is not an inspection-coverage check.

Save `analysis/seconds.json` with one entry for each [k,min(k+1,D)) interval, including a fractional
last interval. Each entry records its actual frame span, corresponding sheet evidence, cuts and all
observed changes, or an explicit unchanged state. Cross-reference `analysis/events.txt` and the
per-cut breakdown. For every cut and second record texture/grade/grain, lighting, graphics, camera
and subject motion, text, effects and transitions. Every changing event records start, peak and end
frame, corresponding PTS, layer order, opacity curve, speed/easing and measured visible parameters;
record uncertainty explicitly and enlarge source detail to resolve it. Static attributes inherit
an explicit state until their next measured change, not an uninspected assumption.

Analysis is complete only when both temporal logs cover the entire video and every visual range
has been inspected. Missing frames, unreadable sheets, unresolved details or uninspected intervals
remain incomplete; continue smaller batches or native-resolution crops without asking questions.
If an actual capability limit prevents completion, state the exact uninspected ranges and do not
claim complete analysis or 1:1 fidelity. Preserve these manifests with the project state.

## Three internal motion reviews

After full source inspection and before any dependent generation or locked plan, reconsider the intended motion in three separate passes. Repeat all three against current composition previews before final rendering, then recheck the rendered sequence before delivery. Record `pre_generation`, `pre_render` and `pre_delivery` snapshots in `analysis/motion-reviews.json`, with the plan/output revision, inspected source intervals, decisions, corrections and unresolved defects. These are internal reviews, not questions, option menus, three generated alternatives or extra paid takes.

1. **Temporal rhythm and staging:** in EXACT compare source frame/audio anchors; in REMIX check anticipation, action, holds, accents and reveal order against the authored output timeline and chosen music. Explain how observed rhythm informed new decisions.
2. **Spatial camera and continuity:** check framing, lens/perspective, camera path, trajectory, scale, screen direction and occlusion through each output cut. Preserve measured source geometry in EXACT; in REMIX stage coherent new motion while retaining explicit locks and identity.
3. **Purposeful detail and reference compatibility:** in EXACT retain source-specific mechanisms. In REMIX test whether the new scenes, motif development and payoff use the observed material, texture, typography and motion vocabulary coherently; remove generic filler and accidental repetition. New motion may serve the new story without reproducing source frame positions.

Each pass needs its own evidence and conclusion; repeating "looks good" three times is not a review. A pass may correctly retain the original decision. Resolve deterministic defects before moving on; any corrective generation still obeys the existing attempt cap and finite plan. After a material motion, timing or camera change, refresh the affected evidence and all three review conclusions for the current revision. Do not claim the final review passed on the basis of an older plan or source-only analysis.

## 2. The one-line trick (write it before anything else)

After the overview sheet and before any per-cut work, write:

> **The trick of this ref is** <the device> **on** <what timing/structure> **so that** <what the viewer
> feels or gets>.

Then list the frames where the trick happens (`trick_frames`). Refine the line after the every-frame
read, but keep it one sentence. In EXACT, routing and QA test that device at the measured source frames. In REMIX, state which mechanism transfers, how it changes for the new story, and its authored setup/payoff frames; identical source positions are not required. Copying timing while losing the device is not faithful, and copying a device without serving the new subject is not a successful remix.

Real examples:

- **Signal (Aura), lost in v2:** "The trick of this ref is that every traffic-signal change swaps the
  walker's outfit and brings in an element of the signal's colour, on the bar, so each beat reads as a
  transformation."
- **City Rhythm (Aura), rejected v7:** "The trick of this ref is a locked-camera photo series where one
  detail changes every 1–2 frames, so the city seems to rearrange itself on the beat." That makes it a
  photo series: route STILL + CODE, not video.
- **Yaong:** "The trick of this ref is that each syllable of the chant becomes a different graphic on
  its beat (arc letters, a word on the face, a giant letter behind her, a typed word), with an
  overexposure burn hiding every jump cut."
- **Katana:** "The trick of this ref is one girl turned into a photocopied zine: hard B/W threshold, one
  accent colour, a boiling pen contour and doodles, cut on every beat, looping back to its first frame."
- **Altman:** "The trick of this ref is a motivational sentence spelled across film heroes, one or two
  words per cut fading in inside a rounded window, often behind the hero's head."

Tests for a good line:

1. Could a stranger rebuild the reference's idea from it?
2. Does it name what changes over time, not only how it looks?
3. Would the remake be obviously wrong without it?

If the reference has no trick beyond "fast cuts on the beat", say so. The trick is then the cut rhythm
plus the look. EXACT checks those directly; REMIX records how its authored rhythm and look use that evidence.

The trick line also suggests the **family**. `references/routing.md` §1 owns the families, their cues
and their pipelines; use its ids:

| family | when                                                                                                                            | typical routes                                                                                          |
| ------ | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `F1a`  | the hero replaces the performer inside the reference's own footage, and the reference's world stays (window, baked text, grade) | SWAP or KEEP; supported motion transfer only for the requested operation, never as an IP-refusal bypass |
| `F1b`  | the hero re-performs the reference's motion in a new world                                                                      | REPERFORM + CODE                                                                                        |
| `F2`   | new character / new world under styled overlays (mixed media, kawaii, fashion/idol, zine)                                       | GENERATE plates + CODE                                                                                  |
| `F3`   | montage of real events or real people                                                                                           | USER-FOOTAGE / LIBRARY + CODE                                                                           |
| `F4`   | remake from the user's own clips                                                                                                | USER-FOOTAGE + CODE, 0 generation                                                                       |
| `F5`   | photo series / stop motion: locked camera, one detail changing per 1–2 frames                                                   | STILL + CODE                                                                                            |
| `F6`   | typography and shapes only                                                                                                      | CODE                                                                                                    |
| `F7`   | product or object swap                                                                                                          | per `references/routing.md`                                                                             |

Mixed references are common (Altman: film montage plus banknote inserts and helmet shots). Pick the
dominant family; the per-cut routes override it.

**F3 (real-footage montage): distinguish reuse from new authorship.**
For a 1:1 request, use KEEP for accessible reference footage unless the user explicitly requested
replacement. Preserve its identity, shot order, branding, captions and watermark. Do not crop a
watermark or substitute stock footage to make the source look newly generated. Reusing supplied
media for this deliverable does not authorize publishing it. If an indispensable source is
inaccessible, state that limitation without a question or invented substitute. In REMIX, select/reorder authorized footage or generate missing story roles for the new subject; record reused material accurately and preserve any retained credit marks. Re-weight meaning under the task contract (§8.5), not a default source-sequence lock.

## 3. What to look for on the every-frame pages

Go through this list on every page and record each finding in the event log with frame numbers.

### 3.1 Cuts the detector misses

A cut is the **first frame of the new shot**. Flash, blur, burn and dissolve frames belong to the
shot they sit in. When a transition straddles a cut, its frames are split between `transition_out` of
cut A and `transition_in` of cut B.

| Kind                   | How it shows on the sheet                                                                                                     | Evidence                                                                                                                                        |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Whip / smear           | 2–3 smeared frames; the content behind the smear changes in the middle; usually straddles the beat (2 frames before, 1 after) | Showpiece: 49 cuts by eye, the engine found 19; ffmpeg scdet at 12 found none                                                                   |
| Hidden in a transition | burn / blur / mosaic / flash frames with a different pose or framing on each side                                             | Yaong: the burn starts f19 in the same shot; the cut is f22 inside it. The frame-diff jump at the cut (34) was smaller than the burn onset (47) |
| Invert / polarity      | the frame flips negative; the content continues (effect) or changes (cut)                                                     | Polarity: 1-frame inverts inside 1–6 frame shots                                                                                                |
| Dark                   | both sides near-black; only shapes change                                                                                     | f03: ffmpeg scene missed dark cuts f48–68                                                                                                       |
| Same-tone              | same background and palette, different pose or framing (jump cuts in one location)                                            | selfie edits, white-cyc plates                                                                                                                  |
| 1–2 frame inserts      | a single foreign frame: black, white, solid colour, a different shot, a ghost cross-blend                                     | Altman c04: 1-frame flashes at f54/f114, ghost blend at f113                                                                                    |
| Strobe sections        | the picture alternates every 1–3 frames (shot/black/shot, or two shots ping-ponging)                                          | Polarity: ~35 picture changes in 230 frames                                                                                                     |
| Micro-cut bursts       | a run of tiny shots on a ~4–6 frame grid                                                                                      | Altman c04: 12–14 banknote micro-shots. Log one cut with cadence `burst` and the sub-shots in `notes`                                           |

### 3.2 False cuts the detector adds

- grain or xerox boil (Katana: a "cut" every 2 frames);
- flash frames, and in-plate exposure flashes (Altman c14 f614–616);
- text pops, and PIP cards popping on (Altman c05 f126/134/146);
- light flicker and camera shake;
- letters flying out (Yaong f12–15).

### 3.3 Text events

For every word or block, record:

- `f_in` (first frame), `f_full` (first fully-on frame), `f_out_start`, `f_out` (last frame);
- the animation: fade length in frames, pop, typewriter per letter, slam, write-on, wobble, smear-out;
- whether the hero passes in front of any part of it;
- whether it crosses a cut.

Words that grow letter by letter are one event with a typewriter animation (Yaong "ICH" at f24 is
"ICHI" by f34). Measurement in §4.

### 3.4 Transitions

Name each one with its frames:

- hard cut; whip / smear;
- flashlight / overexposure burn (Yaong: 3–5 frames, burns to white, dark hair survives, pixel blocks
  on the face);
- pure white or black frames (Yaong: 2 white frames before each magenta entry);
- colour flash, pixel mosaic, glitch;
- blur pulse, with or without a thin dark frame;
- dissolve, invert, zoom punch, slide/wipe;
- ink-brush / matte wipe (below);
- split-strip stack sliding in on beats (Showpiece f172–212);
- mirror, match cut.

Note which source transitions **hide a cut**. EXACT hides the corresponding cut at the same measured boundary; REMIX may use the observed mechanism at an authored boundary with a documented purpose.

**Ink-brush and matte wipes** (`ink_wipe`, `matte_wipe`) reveal the next shot through a moving shape:
a brush stroke, ink bleed, paint smear, smoke, torn paper or a graphic matte, usually over 2–6 frames.
They are easy to log as a generic "smear" or "whip" and then get rebuilt as a blur, which is wrong.
Cues on the every-frame page:

- **Both images are sharp** on either side of the boundary. A whip or smear blurs the whole frame
  along one direction; a wipe has a crisp or ragged **edge** between two sharp pictures.
- The edge is organic: bristle streaks, dry-brush gaps, splatter dots, a ragged or torn outline, often
  an ink-black or white rim along it.
- It **travels** (sweeps across, grows from a point or a corner, bleeds outwards) while the outgoing
  picture stays where it was; nothing slides.
- Mid-wipe, one tile holds parts of both shots at full contrast. A dissolve shows both shots
  everywhere at reduced contrast instead.
  Log the type, frames, direction, edge colour and whether it hides the cut. Brazil's ink-brush wipe at
  23.8 s (into the statue in the clouds) was logged as "smear" by the skill run, while the run without
  the skill named it correctly. Rebuild recipes: `references/compositing.md` §6.5.

### 3.5 Layers

Everything that is not the footage itself:

| Layer type                                     | Note                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `cutout_subject`, `outline`, `halo`, `contour` | offset colour outline (Yaong lilac), white die-cut halo, boiling pen contour (Katana): colour, width in px, boil rate                                                                                                                                                                                                                      |
| `panel`, `pip`, `collage_card`, `split_screen` | position, size, pop-on frames                                                                                                                                                                                                                                                                                                              |
| `starburst`, `shape`                           | behind or in front of the subject                                                                                                                                                                                                                                                                                                          |
| `sticker`, `doodle`                            | **Count them per second.** Users judge density: "больше каракулей и стикеров, как в рефе" came back on both Katana and Yaong; Yaong v2 at ~100 stickers per 9.5 s drew no further complaint. Note their scale relative to the subject: Katana's 30–80 px doodles were too small for the reference and were replaced by 290–510 px gestures |
| `frame_border`, `window`, `letterbox`          | rounded window inside a canvas (Altman 996×836 at 42,540), hand-drawn border, bars. `analyze_ref.py` measures windows and letterbox; confirm on the sheet                                                                                                                                                                                  |
| `watermark`                                    | position, size, opacity, window or canvas coordinates                                                                                                                                                                                                                                                                                      |
| `behind_text`                                  | words occluded by the subject: which letters are hidden on which frames                                                                                                                                                                                                                                                                    |
| `hud`, `light_leak`, `particles`               | when present                                                                                                                                                                                                                                                                                                                               |

For every layer, note `z` (under subject / over subject / over all) and `track` (static, subject,
face, camera).

### 3.6 Grade and texture (observe here, measure in §5)

- B&W, threshold/xerox, duotone, one accent colour;
- grain: size, and whether it boils every frame or stays static;
- halation, glow, vignette, softness or compression mush;
- colour cast, crushed or lifted blacks;
- changes per section.

### 3.7 Camera moves

- **Real moves in the plate:** pan, tilt, push, orbit, handheld.
- **Digital moves added in the edit:** zoom punch, eased push-in (Altman c12: a smooth 60p ~10% push
  on 24p footage), shake, face-lock, mirror (Altman c09 is flipped), rotation.

Separate digital edit moves from in-scene camera motion. Rebuild required whole-plate digital moves at the output fps when appropriate; avoid duplicating motion already in generated footage. Local code must never animate or reshape facial features.

### 3.8 Speed and cadence

Count unique frames per cut. `analysis.json` has a cadence estimate per cut; confirm it on the sheet,
where identical neighbouring tiles are held frames.

Patterns:

- **native**: every frame unique;
- **24p in 30p**: every 5th frame repeated;
- **24p in 60p**: 2:3 pulldown;
- **stepped**: Yaong has 170 unique of 283 frames, ≈18 fps in a 30 fps container (holds 2,2,1);
- **interpolated slow-mo**: every 60p frame unique (Altman c08, c19);
- **frame-blend retime**: ghosted in-betweens (Altman c16, c17);
- **freeze**, **speed ramp** (note frame and speed), **burst**.

Generated footage comes back at 24 fps, so cadence mismatches go both ways:

- Altman's 60p-native cuts fell from 36 to 14 unique frames (c12) and from 32 to 13 (c08).
- Yaong's final had 282 of 285 frames unique against the reference's stepped ~18 fps. It moved
  smoother than the reference and nobody measured it.

Both are code fixes once known: re-apply digital motion at 60p, or step frames to the reference's hold
pattern.

**Record the speed of every retimed cut** in `cadence.speed`: a number, or `[[frame, speed], …]` for
a ramp. Compositing picks the frame method from it (`references/compositing.md`, slow motion):

- **0.3–1×:** blend the two neighbouring source frames, weighted by the fractional index.
- **Below 0.3×, or fast limbs:** nearest frame. Blending there reads as a matte halo.
- **Freeze holds:** integer frames.

Duplicated frames on a 0.3–1× retime judder: Jensanity's f226 was caught in QA
(`references/qa-delivery.md` #12). Note in `cadence.note` which cuts carry fast limbs.

**Fast-content SWAP cuts.** A Genjutsu driving clip is exported at 24 fps, so a cut whose content shows
more distinct images per second than that loses some of them in ANY export: `native` or
`interp_slowmo` cadence at 30/60 fps, or a mixed cadence with unique ÷ of × fps above 24. Altman's c12
went from 36 to 14 unique frames. On every cut routed SWAP (or REPERFORM) that qualifies, write
`fast-content` into `cadence.note` with the unique-images-per-second figure. The plan and progress report flag
these cuts up front ("this shot will move at 24 images per second where the reference is smooth"), and
`assemble.py --control --dry` reports them as `fast-content cut: 24p export drops N images (expected)`
with their own PSNR floor (`references/compositing.md` §14.4). Code can re-apply a digital push at
output fps, but it cannot bring dropped images back.

## 4. Text inventory

Inspect the primary's native-resolution lettering and any needed supplementary font specimens; record their evidence under the typography role in `analysis/references.json`. Record a text-free reference as such. EXACT does not invent words; REMIX may author meaningful text under the task contract, separately from this source inventory. Every observed text event goes into `text_events` of its cut (schema §8). After writing the breakdown, print
the inventory as a table in `analysis/BREAKDOWN.md` for a quick check:

| id  | frames (in / full / out) | words       | font class                    | size % H        | position (cx, cy)   | colour  | animation                                         | layer                      |
| --- | ------------------------ | ----------- | ----------------------------- | --------------- | ------------------- | ------- | ------------------------------------------------- | -------------------------- |
| t03 | ~30 (faint) / 44–53 / 53 | GOTTA       | ultra-condensed grotesk, caps | 40% of window H | 0.26, 0.28 (window) | #ffffff | slow fade in, ends at the cut                     | behind (head covers the A) |
| t04 | 49 / 51–53 / 53          | GET         | didone serif, caps            | 24% of window H | 0.74, 0.21 (window) | #ffffff | fade in 2 f, ends at the cut                      | front                      |
| y01 | 24 / 24 / 39             | (4 letters) | bold italic sans              | 9%              | 0.50, 0.42          | #ffffff | typewriter, 4th letter by f34, smeared out f37–39 | front, on the face         |

(t03/t04 measured on the Altman ref, c03 = f30–53: letter pixels with min(R,G,B) ≥ 236 inside the window,
box GOTTA x 86–427 y 69–400, GET x 591–887 y 76–275; y01 read from the Yaong ref's every-frame sheets.)

How to measure:

- **Frames:** read them from the every-frame pages, then confirm `f_in` and `f_full` on native crops.
  Fades read from small tiles are often 1–2 frames off; the Altman audit found that on 8 cuts.
- **Box and size:** crop at native resolution and take the tight box of the letters. For white
  letters, threshold `min(R,G,B)`: clean bold sans ≥ ~236, thin or grainy serifs ~190–215.
  `size_pct_h` = cap height ÷ frame height (or window height, with `coords: "window"`). `cx`, `cy` =
  box centre as fractions.
- **Typography without questions:** in EXACT or locked/reused lettering, unchanged words use the reference's own text pixels or
  faithfully traced vector contours, preserving position, glyph geometry, spacing, layering and
  animation; no source font file is required. Classify the visible style without claiming exact
  font identification. For authored REMIX words or explicitly changed EXACT words, inspect installed and bundled fonts and
  select the closest visual match autonomously. Tune weight, slant, size, tracking, line height,
  stroke and shadow against source crops for exact locks or the authored typography design and viewed specimens in REMIX. Retrieve a publicly available font only when needed
  and an authorized retrieval capability is available. Never request a font file, name, link,
  license or picker selection. An unavailable exact font does not block work: continue with the
  best supported match and record a deviation from an exact typography lock, or a material authored-plan limitation, in QA.
- **Colour:** sample the letter core, not the edge. Note stroke, shadow and glow (`[sigma, strength]`).
- **Layering:** `behind` if the subject covers any letter on any frame, `front` otherwise,
  `difference` for blend-mode text (Altman c04).
- **Source,** decided per event:
  - `ref_pixels`: 1:1 text rebuilt from the reference's own pixels with measured opacity curves
    (`textlayers.py`). This passed in Altman v3, where retyping and per-frame keying both failed;
  - `retype`: same words in code typography only when source pixels/contours cannot be used;
    select and tune the closest available font autonomously and record visible differences;
  - `new_words`: supplied or authored REMIX words in planned output slots; in EXACT use only requested word changes in the preserved source style;
  - `lyrics_file`: words read from a data file.
- **Lyric handling:** keep permitted supplied words in a timed local file for the final deterministic text pass, with `letters` and cue IDs in the breakdown. Do not paste full lyrics into video-generation prompts or fetch full protected lyrics externally. Available user-supplied text/audio is not a reason to omit requested song captions; preserve required words; use measured source timing/audio in EXACT and checked output cue/song timing in REMIX. Never invent replacement lyric words.

## 5. Look measurement

### 5.1 Stats

`analysis.json` has per-cut look stats: mean RGB, luma p1/p50/p99, mean saturation, a B/W flag and a
grain estimate. Copy the reference-level values into `look.stats`.

Example (Brazil): mean RGB 0.357/0.289/0.226, luma p1 0.006 / p50 0.197 / p99 0.884 — crushed blacks,
no clipping, warm.

### 5.2 Native crops across every distinct texture and look state

Start with a face or skin close-up, darkest shot, brightest shot and text/graphic frame. Then add
native crops for every distinct texture, grade, lighting or grain state identified in the complete
per-second log; four global crops are only a baseline. A 2×2 crop sheet uses the existing command:

```
for F in 52 300 465 614; do ffmpeg -v error -y -i ref/ref.mp4 -vf "select=eq(n\,$F),crop=iw/3:ih/3:iw/3:ih/3" -frames:v 1 -q:v 3 qa/look_ref_$F.jpg; done
ffmpeg -v error -y -i qa/look_ref_52.jpg -i qa/look_ref_300.jpg -i qa/look_ref_465.jpg -i qa/look_ref_614.jpg -filter_complex "xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0" -q:v 4 qa/look_ref.jpg
```

Move the crop window onto the face, edge or texture you need. Record every source crop frame in `look.crop_frames` and its region/state in the per-second log. EXACT QA uses corresponding output frames; REMIX QA chooses output examples of the same material/look state, labels both source and output times, and does not imply temporal alignment.

### 5.3 Clean or stylised (source evidence for the output look)

- **clean**: natural colour, no visible grain at 100%, no vignette, no cast beyond the scene's own
  light. EXACT adds **nothing**: no grain, vignette or house accent colour. REMIX may author a different treatment only as a deliberate scene/story decision, not automatic polish.
- **stylised**: any of B/W, threshold, duotone, accent-only colour, visible or boiling grain,
  halation, light leaks, a hard contrast curve, or one cast across all shots. Measure grain size, boil interval, threshold and accent. EXACT reproduces them; REMIX carries chosen principles into its own documented look rather than randomizing a look on each cut.

Aura's four rejections on colourful refs came from a house B&W + lime grade ("Colors wrecked, too much
noise"). A deliberate authored variation must be distinguished from an accidental color mismatch; explicit color locks still control both modes.

### 5.4 Generated footage

Seedance plates came out ~40% less saturated and slightly olive against a clean stock reference
(Aura E). Record source saturation as evidence; compare output against the exact source lock or the intentional REMIX treatment, not a silent generator cast.

## 6. Audio forensics

### 6.1 Beats

`audio.py beats $W` gives bpm, period, phase, beat and onset times, sections and loudness. **Verify
the BPM by hand.** Auto-BPM has been off by ~1, doubled, or stuck in a 4:3 ambiguity (f07: 99.4 true
vs 130.7 detected).

The check:

1. Express the cut intervals from the breakdown in beats at the candidate BPM and at ×2, ×½, ×¾ and
   ×4⁄3.
2. The right BPM puts most intervals near whole or half beats.
3. On chants, cross-check with Whisper word starts (Yaong: words every 0.446 s ≈ 134 BPM).

Write what you did into `audio.bpm_check`.

### 6.2 Phase

Record `beat_phase_s` and the downbeat as a grid `t(b) = phase + b × period` (Katana's track:
t(b) = −0.015 + b·0.42980). Note systematic offsets:

- cuts that lead the beat (the CUR ref cut ~2 frames early);
- whips that straddle it (2 frames before, 1 after);
- picture that lags transients: Katana was 26–43 ms late on big hits with nearest-frame sampling.

### 6.3 Cut-on-onset share

`audio.py cutsync $W` reports the share of cuts within ±2 frames of an onset, and each cut's offset.
Aura reels sat at ~81%. One edit got 777k views at 77% on-beat cuts and 305k at 51% with another
track.

- **Share ≥ ~0.7:** the edit is onset-locked.
  - EXACT keeps source picture timing unless explicitly changed, including when only the track changes.
  - REMIX uses this as rhythmic evidence, then times its own cuts to the selected track and authored story. Retiming is a creative freedom unless explicitly locked.
- **Low share:** the cuts follow picture or words.

### 6.4 Hidden music edits and the added SFX layer

Run `audio.py align` when a second audio exists: the source song (user-supplied, or identified from an
on-screen credit), or the user's track against the reference. It slides windows of the reference audio
against the other track (windowed normalised cross-correlation) and reports the offset per window.

**Hidden splices.** A jump in offset is a hidden splice.

- Brazil: 0–12.45 s plays song 3.45–15.90 s, then jumps to song 34.30 s. One global offset dropped
  the correlation to 0.04–0.17 after the splice.
- Record it in `audio.hidden_edits`. EXACT audio reconstruction must reproduce the splice. REMIX may author new music edits, but its picture/lyric timing must follow the actual chosen track segments.

**Suspected splices without a second track.** You usually have no source song at analysis time. Still
note a suspected splice when the reference audio jumps: a sudden energy or timbre change that is not on
a bar line, a section that starts mid-phrase, a skipped or doubled beat in the `audio.py beats` grid,
or a section boundary in `beats.json` that does not sit on a downbeat. Record it in `audio.hidden_edits`
as `{"t": …, "suspected": true, "note": "energy jump off the bar grid"}`. It costs nothing while the
reference audio is reused. If the user explicitly swaps the track, record in the progress report: the cuts were timed
on the spliced music. EXACT preserves picture timing unless explicitly changed; REMIX plans new picture/audio timing under its locks. Report any unresolved sync difference (`references/compositing.md` §11).

**SFX layer.** The residual after subtracting the aligned song is the editor's own layer: booms,
whooshes, risers, shutters, ducks. Brazil had 13 whooshes at 1.5–5 kHz and ducks of −6/−7 dB.

- List the events in `audio.sfx_layer`.
- When the reference audio is reused, its existing SFX remain unchanged. When a requested music change requires separate effects, retain accessible original SFX or select actually auditioned stock recordings, then align/mix them at measured source times in EXACT or authored event times in REMIX. Record stock IDs and source/use evidence in `analysis/references.json`; never synthesize the sounds in code.

### 6.5 Words

When supplied audio contains VO, lyrics or a chant needed for the requested result, a supported transcription operation can create timed local cues. With the existing faster-whisper `small` model (`/opt/whisper-models`), use `word_timestamps=True` on a 16 kHz mono wav. For discovered supplemental music, analyze timing and structure without scraping or reproducing full protected lyrics.

- Whisper is ~0.27 s late on TTS and merges chant words. Slice words by the energy envelope, not by
  Whisper.
- Words go to `analysis/words.json`, not into chat.

### 6.6 Loudness

Record integrated loudness and true peak (`ffmpeg … -af ebur128=peak=true -f null -`) as the QA
reference.

### 6.7 Audio plan

Pick one:

- `reuse_ref_audio`: stream copy when keeping the actual source audio; default for an EXACT soundtrack lock and available in REMIX when it serves the plan. "Как в рефе" alone does not lock the whole video.
- `user_track`: the supplied track selected by user intent; EXACT preserves picture timing unless changed, REMIX may author a new timeline to it.
- `tiktok_track`: an actually inspected, available TikTok music source for required new/replacement music, with supported use and source evidence.
- `stock_track`: an actually auditioned stock music asset for required new/replacement music.
- `voice_track`: only explicitly requested speech with an already selected supported voice and finite plan; this is not a music or SFX generator.

No plan uses `code_track`, procedural music, a synthesized beat or generated SFX. EXACT retains reference silence; REMIX may select recorded music/SFX when the authored story needs them and no silence lock exists. A missing locked source track remains an explicit limitation; an intentionally selected REMIX track is an authored choice, not a failed source copy. Store the selected asset identifiers and source/audition evidence in `analysis/references.json`; code handles timing and mixing of those assets only.

Source length is always measured from actual video frames/PTS, not container or audio duration. In EXACT it locks output video timing unless explicitly changed. In REMIX `output_target` sets a separate video frame count/endpoint and audio ending. Yaong's exact-source case had 283 video frames (9.433 s), while the container said 9.517 s because of audio; that must not become an arbitrary 285-frame exact output.

## 7. Identity visibility per cut

For an explicitly requested identity replacement in an anime or other stylized reference, record
two distinct image roles: the extracted source frame controls composition, pose, camera, background,
lighting, palette, texture and rendering style; the user's character image or photo controls the
replacement identity only. Do not import the identity photo's scenery, photographic look or pose
unless explicitly requested. A supported image generator may combine both references to create the
matched replacement frame. Anime does not require a Genjutsu Styles preset: compare a generated
still plus code, animation of that still with Seedance 2.5, and a supported Genjutsu edit/motion route
against the measured source motion. Select the most faithful available route per shot autonomously;
no character picker, creative question or consent step is introduced. This matched-frame procedure applies to EXACT or a deliberately matched REMIX shot. New REMIX scenes may change staging/wardrobe under the authored continuity plan while preserving the intended identity and explicit locks; the identity photo never silently supplies its background or pose.

For every SOURCE cut, set `identity_visible` as an evidence descriptor, not a routing shortcut. Apply the same visibility vocabulary separately to authored output shots; their geometry/cast follow the task contract:

| value          | meaning                                                                 | scope and verification                                                                                                          |
| -------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `face_clear`   | the face is readable: front or three-quarter, sharp enough to recognise | For a requested target, verify identity and the source framing; otherwise preserve the original subject                         |
| `face_partial` | profile, small in frame, heavy blur or partial occlusion                | Include the target's shot; verify available identity and continuity cues while preserving the occlusion                         |
| `body_only`    | back turned, hood, helmet, hands, silhouette or another body crop       | Include the target's shot; verify subject continuity, pose, visible details and source geometry without revealing a hidden face |
| `none`         | no person is present; this never means merely "no readable face"        | Route the content according to the requested reconstruction/full-regeneration scope                                             |

Record all source identities as observations. EXACT does not replace an untargeted identity; REMIX uses the intended cast in its authored scenes rather than inheriting every source performer. For a requested replacement, track the intended subject through every appearance, including hidden-face and body-only shots, using adjacent-shot continuity. Record the target, source frames, connected cuts, requested change, route and verification evidence. For full regeneration, every required cut needs a reconstruction route. Existing authority and finite spending limits still apply; they do not make an incomplete replacement complete. Never ask for opt-in or credit confirmation.

**Performer match for a requested replacement.** On every targeted `body_only` or `face_partial` cut, record `performer_vs_hero` using visible hair, skin, build and other continuity evidence:

- `compatible`: the visible cues are compatible; this helps verification but does not authorize KEEP or exempt the cut from the requested replacement.
- `mismatch: <what>`: identify the concrete visible difference and use the most faithful supported reconstruction route within the plan. In EXACT preserve source pose/wardrobe and required proportions unless explicitly changed; in REMIX follow authored staging and character continuity without identity drift. If no authorized viable route completes the change, record the unresolved cut as an exact deviation or REMIX production/lock limitation; do not silently pass through the original performer or claim success.

KEEP is available for authorized source content that fulfills the plan, with a specific reuse reason. It cannot satisfy a required subject change or a new-generation requirement. A hidden face, compatible silhouette or low cost is not that reason. In a matched/replacement shot preserve the observed helmet, back view or silhouette; never reveal a concealed face merely to make identity QA easier. A new REMIX shot may use its own planned viewpoint. Follow `routing.md` §2.2 for the resulting route.

Also record:

- `shot_size`: ECU / CU / MCU / MS / MWS / WS / EWS, `insert`, `graphic`. It drives resolution sizing
  and face tracking;
- which hero is in the cut when there are two (Genjutsu swaps roles on two-performer refs);
- the other people who must **not** get the hero's face.

**Extra people.** EXACT preserves everyone visible, including partial figures; do not omit them or tighten the crop to simplify generation. REMIX may author a different cast/layout under the task contract, but every planned person must be accounted for and remain the correct identity. In both modes background cleanup excludes ALL visible people, their heads/hair and mask edges; changing the cast never authorizes a local face/head edit.

## 8. `analysis/breakdown.json`

### 8.1 Rules

- **Frames:** absolute 0-based indices of `ref/ref.mp4`; `f1` is inclusive.
- **Cuts are contiguous:** the first `f0` is 0, each `f0` is the previous `f1` + 1, and the last `f1`
  is `nb_frames − 1`.
- **Coordinates:** fractions of the frame (`coords: "frame"`) or of the window (`coords: "window"`).
- **Seconds:** for verified constant-fps sources, frame start is f/fps, center is
  (f+0.5)/fps and an inclusive frame end converts to (f1+1)/fps. Use center time only
  for selecting representative images, never as an event boundary. For variable frame rate,
  use decoded PTS and frame durations; do not derive boundaries from nominal fps.
- **Authority:** `breakdown.json` is the authority for observed SOURCE facts; `task-contract.json` controls locks/freedoms and the authored output plan controls REMIX timing/content. Where it disagrees with the
  detector proposals in `analysis.json`, also write the corrected cut list back into `analysis.json`
  `cuts`, so scripts that read it agree.
- **Vocabularies:** use the ones below. Free text goes in `desc`, `detail` and `notes`.

### 8.2 Reference-level fields

| field                | type | content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `schema`             | str  | `"rr.breakdown/1"`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `ref`                | obj  | from `ref/ref.json`: `path, width, height, fps` (rational string such as `"30000/1001"`, never rounded), `nb_frames` (decoded count), `video_duration, audio_duration, rotation, has_audio`                                                                                                                                                                                                                                                                                                                                   |
| `trick`              | str  | "The trick of this ref is …" (§2)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `trick_frames`       | list | `[[f0, f1, "what happens"], …]`: observed source anchors; EXACT QA maps these directly, REMIX authors separate motif/payoff anchors                                                                                                                                                                                                                                                                                                                                                                                           |
| `family`             | enum | `F1a F1b F2 F3 F4 F5 F6 F7` (§2 table; `references/routing.md` §1)                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `format_lock`        | obj  | legacy source-analysis field, not a REMIX output requirement: `width, height, fps, frames, aspect, canvas` (`full`/`window`/`letterbox`), `window {x,y,w,h,radius}` or null, `letterbox {top,bottom,left,right}` or null, `source: "ref"`, `note`; output changes belong to `plan/creative-plan.json.output_target`                                                                                                                                                                                                           |
| `look`               | obj  | `class` (`clean`/`stylised`), `bw`, `desc`, `grain {present, size_px, boil_every}`, `halation`, `vignette`, `softness`, `cast`, `threshold`, `stats {mean_rgb, luma_p1_p50_p99, sat_mean}`, `crop_frames [4 ints]`, optional `per_section`                                                                                                                                                                                                                                                                                    |
| `palette`            | list | `{hex, role (accent/text/flash/outline/background/skin), where}`                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `fonts`              | list | `{class, weight, italic, case, nearest, file, used_by [text ids]}`                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `audio`              | obj  | `bpm, bpm_check, period_s, beat_phase_s, downbeat_s, sections [{name,t0,t1}], cut_on_onset_share, cut_lead_frames, hidden_edits [{t, from_s, to_s, ncc}` or `{t, suspected: true, note}]` (§6.4), `sfx_layer [{t, type, note}], speech (none/vo/lyrics/chant), words_file, lufs_i, true_peak_db, plan (reuse_ref_audio/user_track/tiktok_track/stock_track/voice_track), plan_note`; retain source observations here and the selected output audio plan in `creative-plan.json` under SKILL.md “Typography, music and motion” |
| `meaning`            | list | `{what (layer/text id), means, maps_to}` (§8.5)                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `heroes`             | list | `{id, desc, cuts}`; `others`: the same shape for people who must stay themselves                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `global_layers`      | list | layer objects (§8.3) running through the whole reference: window, watermark, border, letterbox, grain                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `cuts`               | list | per-cut objects (§8.3)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `not_1to1`           | list | exact-fidelity limitations only, `{what, cuts, why}`; intentional REMIX differences belong to authored adaptations, while unresolved locks/production issues go in the QA limitations                                                                                                                                                                                                                                                                                                                                         |
| `reference_manifest` | path | `analysis/references.json`: primary choice, full-candidate viewing evidence and inspected montage/music/font roles; supplemental evidence informs documented REMIX freedoms or fills exact-analysis gaps                                                                                                                                                                                                                                                                                                                      |
| `motion_reviews`     | path | `analysis/motion-reviews.json`: temporal, spatial and distinctive-detail review records for the current pre-generation, pre-render and pre-delivery revisions                                                                                                                                                                                                                                                                                                                                                                 |
| `questions`          | list | always `[]`; resolve defaults from task contract/reference/context and record actual missing inputs as limitations; credit or platform consent never creates a user-question or waiting state                                                                                                                                                                                                                                                                                                                                 |

### 8.3 Per-cut fields

| field                             | type     | content                                                                                                                                                                                                                                                                                                                          |
| --------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                              | str      | `c01`, `c02`, … in timeline order                                                                                                                                                                                                                                                                                                |
| `f0`, `f1`                        | int      | first and last frame, inclusive, absolute                                                                                                                                                                                                                                                                                        |
| `content`                         | str      | observed source description, including its actual text/logos/identity; proposed REMIX changes belong to the authored output plan                                                                                                                                                                                                 |
| `hero_present`                    | bool     | the person we replace or re-create is in the cut                                                                                                                                                                                                                                                                                 |
| `hero`                            | str/null | hero id                                                                                                                                                                                                                                                                                                                          |
| `identity_visible`                | enum     | `face_clear` / `face_partial` / `body_only` / `none` (§7)                                                                                                                                                                                                                                                                        |
| `performer_vs_hero`               | str      | on `body_only` / `face_partial` cuts with a person: `compatible` or `mismatch: <hair/skin/build detail>` (§7); omit otherwise                                                                                                                                                                                                    |
| `shot_size`                       | enum     | `ECU CU MCU MS MWS WS EWS insert graphic`                                                                                                                                                                                                                                                                                        |
| `camera`                          | obj      | `move` (`static handheld pan tilt push_in pull_out zoom orbit track crane whip shake face_lock`), `digital` (true = added in the edit), `detail`                                                                                                                                                                                 |
| `cadence`                         | obj      | `unique`, `of`, `pattern` (`native pulldown_24in30 pulldown_24in60 stepped interp_slowmo blend_retime freeze speed_ramp burst`), `speed` (number or `[[frame, speed], …]`), `note` (`fast-content …` on SWAP / REPERFORM cuts above 24 images per second, §3.8)                                                                  |
| `effects`                         | list     | in-shot effects `{type, f0, f1, params}`. Types: `flash_white flash_black flash_color invert threshold duotone bw hue_shift blur_pulse zoom_punch glitch mosaic rgb_split shake strobe mirror light_leak exposure_flash ghost_blend freeze stutter split_screen` (use `references/compositing.md` names where it has the effect) |
| `transition_in`, `transition_out` | obj      | `{type, f0, f1, hides_cut, note}`. Types: `cut whip flashlight white_frames black_frames color_flash mosaic glitch blur dissolve invert zoom_punch slide wipe ink_wipe matte_wipe split_strip mirror match_cut` (`ink_wipe` / `matte_wipe`: §3.4)                                                                                |
| `layers`                          | list     | `{id, type, f0, f1, z (under_subject/over_subject/over_all), track (static/subject/face/camera), desc, color, size, count, meaning}`; types as in §3.5                                                                                                                                                                           |
| `text_events`                     | list     | `{id, f_in, f_full, f_out_start, f_out, text (null for lyrics), letters, font_class, weight, italic, size_pct_h, cx, cy, coords, box [x,y,w,h], color, stroke, glow, animation, layering (front/behind/difference), source (ref_pixels/retype/new_words/lyrics_file), crosses_cut, meaning}`                                     |
| `beat`                            | obj      | optional `{start_beat, on_onset, offset_frames}`                                                                                                                                                                                                                                                                                 |
| `route_suggestion`                | obj      | `route` (`KEEP CODE USER-FOOTAGE LIBRARY SWAP REPERFORM GENERATE STILL`, the router's routes in `references/routing.md` §2; SKILL.md's `FOOTAGE` is accepted as USER-FOOTAGE), `why`, `plate_group` (cuts served by one plate or job), `keyframe` (frame to use as the composition ref), `needs_matte`, `needs_face_track`       |
| `notes`                           | str      | boundary doubts, risks, burst sub-shots, anything QA must re-check                                                                                                                                                                                                                                                               |

### 8.4 Example (Yaong ref, frames 0–39, read from its every-frame sheets)

This describes the Yaong reference's own performer and graphics. Copy its structure, never its content:
every observed identity item (hair, wardrobe, props, words) in the breakdown comes from the reference. The example includes historical adaptation proposals; keep them separate from observations. EXACT output changes only requested attributes; REMIX output comes from its separate authored plan.

```json
{
  "schema": "rr.breakdown/1",
  "ref": {
    "path": "ref/ref.mp4",
    "width": 900,
    "height": 720,
    "fps": "30/1",
    "nb_frames": 283,
    "video_duration": 9.433,
    "audio_duration": 9.517,
    "rotation": 0,
    "has_audio": true
  },
  "trick": "The trick of this ref is that each syllable of the chant becomes a different graphic on its beat (arc letters, a word on the face, a giant letter behind her, a typed word), with an overexposure burn hiding every jump cut.",
  "trick_frames": [
    [5, 15, "chant letters on an arc around her"],
    [24, 39, "word typed on her face"]
  ],
  "family": "F2",
  "format_lock": {
    "width": 900,
    "height": 720,
    "fps": "30/1",
    "frames": 283,
    "aspect": "5:4",
    "canvas": "full",
    "window": null,
    "letterbox": null,
    "source": "ref",
    "note": ""
  },
  "look": {
    "class": "stylised",
    "bw": false,
    "desc": "blown-out white backstage, pink skin glow, soft glow, light grain, compression softness",
    "grain": { "present": true, "size_px": 1, "boil_every": 1 },
    "halation": false,
    "vignette": false,
    "crop_frames": [12, 24, 40, 55]
  },
  "palette": [
    {
      "hex": "#c9a2e6",
      "role": "outline",
      "where": "offset outline around the cut-out, starburst"
    },
    { "hex": "#ff3fc8", "role": "flash", "where": "magenta mosaic entry" }
  ],
  "fonts": [
    {
      "class": "bold italic sans",
      "weight": 800,
      "italic": true,
      "case": "upper",
      "nearest": "Montserrat ExtraBold Italic",
      "used_by": ["y00", "y01"]
    }
  ],
  "audio": {
    "bpm": 134.4,
    "bpm_check": "Whisper word starts every 0.446 s; cut intervals ~1 beat",
    "speech": "chant",
    "words_file": "analysis/words.json",
    "plan": "reuse_ref_audio"
  },
  "cuts": [
    {
      "id": "c01",
      "f0": 0,
      "f1": 21,
      "content": "adult woman, selfie framing, cat-paw hands under chin, white backstage room",
      "hero_present": true,
      "hero": "h1",
      "identity_visible": "face_clear",
      "shot_size": "MCU",
      "camera": { "move": "handheld", "digital": false, "detail": "phone selfie wobble" },
      "cadence": {
        "unique": 13,
        "of": 22,
        "pattern": "stepped",
        "speed": 1.0,
        "note": "~18 fps holds (2,2,1) in 30p"
      },
      "effects": [],
      "transition_in": {
        "type": "color_flash",
        "f0": 0,
        "f1": 3,
        "hides_cut": false,
        "note": "magenta pixel mosaic, sharpening f2-3"
      },
      "transition_out": {
        "type": "flashlight",
        "f0": 19,
        "f1": 21,
        "hides_cut": true,
        "note": "burn to white, hair stays dark, pixel blocks on the face; cut at f22 inside the burn"
      },
      "layers": [
        {
          "id": "L1",
          "type": "outline",
          "f0": 4,
          "f1": 21,
          "z": "under_subject",
          "track": "subject",
          "desc": "lilac offset outline around the cut-out",
          "color": "#c9a2e6"
        },
        {
          "id": "L2",
          "type": "starburst",
          "f0": 4,
          "f1": 18,
          "z": "under_subject",
          "track": "static",
          "desc": "lilac comic starburst behind her"
        },
        {
          "id": "L3",
          "type": "doodle",
          "f0": 5,
          "f1": 18,
          "z": "over_subject",
          "track": "subject",
          "desc": "white music notes",
          "count": 3
        }
      ],
      "text_events": [
        {
          "id": "y00",
          "f_in": 5,
          "f_full": 9,
          "f_out_start": 12,
          "f_out": 15,
          "text": null,
          "letters": 4,
          "font_class": "bold italic sans",
          "size_pct_h": 0.14,
          "cx": 0.5,
          "cy": 0.35,
          "coords": "frame",
          "color": "#ffffff",
          "animation": "letters fly in on an arc, fly out",
          "layering": "front",
          "source": "new_words",
          "crosses_cut": false,
          "meaning": "first chant word; letters on a ring"
        }
      ],
      "route_suggestion": {
        "route": "GENERATE",
        "why": "new character; identity-legible close-up",
        "plate_group": "A",
        "keyframe": 9,
        "needs_matte": true,
        "needs_face_track": true
      },
      "notes": "f12-15 is not a cut: the arc letters leave, same shot"
    },
    {
      "id": "c02",
      "f0": 22,
      "f1": 39,
      "content": "same woman, both hands raised near her head, white backstage room",
      "hero_present": true,
      "hero": "h1",
      "identity_visible": "face_clear",
      "shot_size": "MCU",
      "camera": { "move": "handheld", "digital": false, "detail": "" },
      "cadence": { "unique": 11, "of": 18, "pattern": "stepped", "speed": 1.0, "note": "" },
      "effects": [
        {
          "type": "zoom_punch",
          "f0": 29,
          "f1": 33,
          "params": { "blur": true, "thin_dark_frame": true }
        }
      ],
      "transition_in": {
        "type": "flashlight",
        "f0": 22,
        "f1": 24,
        "hides_cut": true,
        "note": "burn decays"
      },
      "transition_out": {
        "type": "whip",
        "f0": 37,
        "f1": 39,
        "hides_cut": true,
        "note": "vertical smear, the word smears out; next shot sharp at f40"
      },
      "layers": [
        {
          "id": "L4",
          "type": "shape",
          "f0": 25,
          "f1": 39,
          "z": "over_all",
          "track": "static",
          "desc": "pink pixel squares, top-left"
        }
      ],
      "text_events": [
        {
          "id": "y01",
          "f_in": 24,
          "f_full": 24,
          "f_out_start": 37,
          "f_out": 39,
          "text": null,
          "letters": 4,
          "font_class": "bold italic sans",
          "size_pct_h": 0.09,
          "cx": 0.5,
          "cy": 0.42,
          "coords": "frame",
          "color": "#ffffff",
          "animation": "typewriter (3 letters, 4th by f34), smeared out f37-39",
          "layering": "front",
          "source": "new_words",
          "crosses_cut": false,
          "meaning": "the count word 'one'; the new chant's HANA takes this slot"
        }
      ],
      "route_suggestion": {
        "route": "GENERATE",
        "why": "same plate as c01, next gesture",
        "plate_group": "A",
        "keyframe": 34,
        "needs_matte": true,
        "needs_face_track": true
      },
      "notes": "f37-39 is the same shot smeared, not a new cut (checked at 450 px)"
    }
  ]
}
```

### 8.5 The meaning layer

For every graphic and text event, write what it **means** relative to the words, the beat or the
story, then what it maps to in the remake (`meaning` field + the top-level `meaning` list).
In EXACT the mapping is identical except explicit requested changes. In default REMIX, map the observed meaning into the new subject/story; new words, symbols, props and scenes are allowed under the task contract. Record each as an authored addition/adaptation with its role and evidence, never as an observed source fact. The examples below illustrate meaningful adaptation, not a mandatory source sequence.

- **Yaong:**
  - The giant pink "N" behind the girl is the syllable NI of ichi-NI-san, so the new chant's DUL took
    that slot as giant letters.
  - ARIGATO types as ARI bold + GATO thin, so SARANGHAE typed as SARANG bold + HAE thin.
  - The tag "gxdskee*" is a handle; it became "nabi.cam*".
- **Altman:** each word belongs to one sentence spread across cuts. Losing a word breaks the
  sentence, not just a cut.
- **Night Ride (Aura):** the words on screen are the song's own lyrics, on their syllables. Our own
  words over that audio read as fragments ("EV / DON / GINE") and were rejected.
- **Showtime (Aura):** the reference's props are the performer's world. The user wanted them
  re-themed to the hero's world (computers, code, money), not kept.
- **Brazil:** an on-screen credit identified the track, and that made the hidden-splice check
  possible. The reference is a portrait of a nation; a user who wants it about one player needs the
  meaning re-weighted to that player. The dry-run plan kept the nation's structure and gave the
  player only ~6 s of 28: map the reference's beats and sections onto the user's subject first, then
  fill the rest.

A remake that keeps the shapes but breaks the meaning reads as random graphics.

### 8.5.1 Semantic shot roles and missing-role inventory

After the complete source read, give each source cut an observed role with frame evidence: hook/origin, identity, action, accent, reveal, consequence, transition, breath, payoff or closure. Describe what changes, what causes the next beat, and what the viewer learns; a role is an interpretation supported by frames, not a fact inferred from a filename. A source can be non-narrative; do not invent a plot it lacks.

For REMIX, write the new subject's premise/tension and desired ending in `plan/creative-plan.json`, then design only the roles needed to reach that ending. Each output shot records its purpose, start/end state, screen direction/camera, desired duration, identity/wardrobe continuity, text/audio function, reference evidence and whether it is reused, adapted or new. Introduce a visual motif with explicit setup, development and payoff mapped to actual output shot IDs; do not trust random effects to create it. The reference's shot count or order is not mandatory.

Build a missing-role inventory from ACTUALLY VIEWED user clips/photos and source evidence: `role`, `available_asset`, `viewed_range`, `usable_action`, `gap`, `planned_solution`. Generate missing actions/scenes, not a fresh version of every source cut by default. A supplied photo can serve identity/design; do not pretend it contains an unseen action. EXACT uses roles to preserve the source's meaning, without introducing new story beats.

### 8.6 Validate before saving

The following legacy validator checks the SOURCE breakdown only, in both modes; it never validates the REMIX output timeline. Run it right after writing that file. It checks contiguity, required fields,
vocabularies, text frames and continuity descriptors. It does not validate requested replacement scope, `coverage.json` or `seconds.json`. Separately validate task-contract mode/reason/locks/freedoms, the output target and every authored shot against them; verify targeted appearances, required generation/reuse scope and the explicit source coverage union checks in §1.6. Planned REMIX source reuse may serve its new story; it cannot replace a required identity change or newly generated deliverable.

```
python3 - analysis/breakdown.json <<'PY'
import json, sys
bd = json.load(open(sys.argv[1])); err = []; warn = []
ROUTES = {"KEEP", "CODE", "USER-FOOTAGE", "LIBRARY", "FOOTAGE", "SWAP", "REPERFORM", "GENERATE", "STILL"}
IDV = {"face_clear", "face_partial", "body_only", "none"}
N = bd["ref"]["nb_frames"]
if not str(bd.get("trick", "")).lower().startswith("the trick of this ref is"):
    err.append("trick line missing or not in the form 'The trick of this ref is ...'")
for k in ("family", "format_lock", "look", "palette", "fonts", "audio", "cuts"):
    if k not in bd: err.append(f"missing top-level '{k}'")
cuts = bd.get("cuts", []); prev = -1
for c in cuts:
    cid = c.get("id", "?")
    for k in ("f0", "f1", "content", "hero_present", "identity_visible", "shot_size", "camera", "cadence",
              "effects", "transition_in", "transition_out", "layers", "text_events", "route_suggestion", "notes"):
        if k not in c: err.append(f"{cid}: missing '{k}'")
    if c.get("f0") != prev + 1: err.append(f"{cid}: f0={c.get('f0')} but previous cut ended at {prev}")
    if c.get("f1", -1) < c.get("f0", 0): err.append(f"{cid}: f1 < f0")
    prev = c.get("f1", prev)
    if c.get("identity_visible") not in IDV: err.append(f"{cid}: identity_visible not in {sorted(IDV)}")
    r = (c.get("route_suggestion") or {}).get("route")
    if r not in ROUTES: err.append(f"{cid}: route '{r}' not in {sorted(ROUTES)}")
    pm = str(c.get("performer_vs_hero") or "")
    if c.get("hero_present") and c.get("identity_visible") in ("body_only", "face_partial") and not pm:
        warn.append(f"{cid}: set performer_vs_hero (compatible / mismatch: ...) for an identity-invisible cut")
    if r == "KEEP" and pm.startswith("mismatch"):
        warn.append(f"{cid}: KEEP but {pm} -> verify an untargeted reuse reason; a requested replacement cannot pass with this unresolved mismatch")
    if r == "KEEP" and bd.get("family") == "F3":
        warn.append(f"{cid}: KEEP in an F3 montage reuses another editor's pixels -> intended for a 1:1 request; preserve watermark and source attribution (§2)")
    for t in c.get("text_events", []):
        if not (t.get("f_in", -1) <= t.get("f_full", -1) <= t.get("f_out", -2)):
            err.append(f"{cid}/{t.get('id')}: need f_in <= f_full <= f_out")
        if not t.get("crosses_cut") and not (c["f0"] <= t.get("f_in", -1) and t.get("f_out", N) <= c["f1"]):
            err.append(f"{cid}/{t.get('id')}: outside the cut but crosses_cut is false")
    for e in c.get("effects", []) + c.get("layers", []):
        if "f0" in e and not (0 <= e["f0"] <= e.get("f1", e["f0"]) < N):
            err.append(f"{cid}: {e.get('type')} frames {e.get('f0')}-{e.get('f1')} out of range")
if cuts and prev != N - 1: err.append(f"last cut ends at {prev}; reference last frame is {N-1}")
fl = bd.get("format_lock", {})
if fl and fl.get("frames") != N and fl.get("source") != "user":
    err.append(f"format_lock.frames={fl.get('frames')} != ref nb_frames={N}")
print(json.dumps({"ok": not err, "cuts": len(cuts), "errors": err, "warnings": warn}, indent=1))
sys.exit(1 if err else 0)
PY
```

Fix every error. Resolve warnings from the reference and existing instructions; report only material
limitations. The script validates SOURCE structure, not the REMIX output plan, task mode, permission to spend or scope of content changes. Its historical F3/KEEP warning never turns REMIX into EXACT; resolve reuse against the actual task contract.

## 9. Parallel subagents for the breakdown

### 9.1 When

- **Use them** when the reference has more than ~25 cuts, runs longer than ~20 s, or carries dense
  layers (more than ~100 sticker or text events), and the client can run subagents with the
  Higgsfield tools.
- **Otherwise** do it yourself, section by section. One careful reader beats five careless ones: a
  67-agent shootout in Brazil never reached the draft, and Katana's review agents cost 5.56 M tokens.
- **How to split:**
  - performer-swap refs, where each cut gets its own route and prompt: **one agent per 3–4 cuts**;
  - template refs, where sections repeat a scheme (Yaong's two halves, Brazil's chapters, a strobe
    act): **one agent per act/section**.
  - At most ~6 agents, all launched in one message.

### 9.2 Before launching

1. Finish steps 1–5 yourself: the machine pass, audio, the **trick line and the family**. Agents work
   inside your frame; they don't invent it.
2. Write the draft cut list (detector proposals plus your overview corrections) and the event log so
   far.
3. Save the state (`references/sandbox.md` §9): reserve a `media_upload` slot for the general file
   `<slug>_v0_state.tar.gz` and keep the `content_type` from the reply. Run
   `rr_save '<upload_url>' '<content_type>'` in the sandbox, then `media_confirm(type: "file")`; the
   confirmed URL is the state URL. The sandbox is discarded ~10 s after the last call ends, and it is
   one machine per account, shared by every agent.

### 9.3 What each agent's prompt contains

- slug, state URL, `fps`, `nb_frames`, the window crop if any, the trick line, the family;
- its frame range plus 2 frames of overlap on each side;
- the §8.3 table and vocabularies, §3 (what to look for) and §1.2–1.4 (budget, labels, zoom
  commands);
- rules for its sandbox calls:
  - start each call with `source "$HF_WORKFLOWS/katana/scripts/rr.sh"`, then
    `rr_restore <slug> "<state_url>"` (it runs `rr_ws` and loads the state only when the workspace
    is empty);
  - zoom only with the ffmpeg command of §1.4, writing into its own scratch folder. Never re-run
    `analyze_ref.py`: it rewrites `analysis.json` and every sheet in the shared workspace;
  - foreground calls only, timeout ≤60 s;
  - never `background:true`, never `restart:true` (a timeout or restart wipes the sandbox for
    everyone);
  - scratch files only under `analysis/agents/<agent_id>/`;
  - `image_paths` ≤4 files and ≤512 KiB per call;
  - **no paid or upload tools** (no generate_*, remove_background or media_upload).

### 9.4 What each agent must return (as its final message, not as a sandbox file)

1. A JSON array of cut objects for its range in the §8.3 schema, with measured frames and boxes.
2. `boundary_changes`:
   `[{"cut": "c07", "field": "f0", "from": 120, "to": 122, "evidence": "f121 is a 1-frame white insert; new shot starts f122"}]`.
3. Event-log lines for its range (§1.5 format).
4. `doubts`: what it could not decide, with the frames to look at.
5. One summary line per cut, the full per-second log for the assigned range, and the manifest
   of every actually viewed frame range/sheet. Every assigned frame must be inspected.

### 9.5 After they return

1. Merge the arrays.
2. Resolve the seams yourself on a zoom strip of the 2-frame overlaps.
3. Run the §8.6 source validator, then `rr_save`.
4. Merge each agent's actually inspected ranges and per-second logs; verify their union covers
   [0,N) without gaps. Recheck every seam and doubtful frame yourself. Spot-check a cut per agent
   as an additional consistency check, never as a substitute for complete delegated inspection.

## 10. Summary to the user (end of analysis)

Send a short progress update and continue automatically within verified task/account authority
and the finite internal cap. Never ask for variants, fonts, uploads, quality, credit confirmation
or consent, and never wait for a user reply. Resolve mandatory service consent through an existing
supported authorized route; if none exists, finish independent work and state the blocked/partial
result declaratively without bypassing the service restriction.

Use 3–5 lines in the user's language: what the reference does; whether this is an authored remix or an explicitly exact reconstruction; the planned story/output and what remains locked; and any verified limitation. Distinguish measured source format from chosen output format, and reused pixels from new footage. Derive unspecified REMIX choices from intent and viewed evidence; EXACT inherits source details. If no reference was supplied, first perform the autonomous discovery and actual candidate viewing above. If a required input or capability remains unavailable after supported research, complete independent work and state the limitation declaratively. Do not invent footage or claim unviewed clips were inspected.

No pipeline jargon (canary, plate, pad, route names, `ip_detected`, guard, PSNR) and no bare cut ids:
describe shots in words ("the close-up of her eyes", "the back view on the stairs"). Attach the labelled
overview sheet so any id you do mention can be found: after correcting the cut list, refresh the sheets
with `analyze_ref.py $W --review-size --no-window --cuts-from analysis/analysis.json` so the labels match the
breakdown, then upload `sheets/overview_p01.jpg` (one image per overview page; tiles read
`c03 f120-151`) as an image (reserve its slot in the stage's `media_upload` call, `rr_put` it,
`media_confirm(type: image)`) and show it with the message (`references/qa-delivery.md` §4).

Then use `references/routing.md` and the finite autonomous cost plan in `references/budget.md`.
No user reply or confirmation is required by this workflow.

## 11. Pitfalls checklist

- [ ] Primary source is supplied or autonomously selected from actually viewed current relevant TikTok/Shorts candidates; search snippets never count as viewing.
- [ ] Montage, music/audio and typography reference roles inspected and recorded in `analysis/references.json`; supplemental evidence supports authored REMIX decisions without changing recorded source facts or explicit locks.
- [ ] All three motion reviews have distinct evidence and conclusions for the current revision in `analysis/motion-reviews.json`; EXACT retains source motion; REMIX motion serves its new story rather than arbitrary novelty.
- [ ] Required new music comes from an authorized TikTok or stock source, required new SFX from stock; no code-synthesized music, beats or effects.

- [ ] Frames selected by index (`select=eq(n\,N)` / `between(n\,a\,b)`), never by `-ss`.
- [ ] fps kept rational (29.97 = `30000/1001`); rotation respected (`ref.json` `rotation`).
- [ ] Source video frames/PTS are distinct from the authored output target. EXACT matches the locked source grid; REMIX is validated on its own planned grid and endpoint, never the source audio/container length.
- [ ] Sheet labels are absolute frame indices.
- [ ] Every decoded frame F0–F(N-1) inspected at native cadence; manifest union equals [0,N)
      with no gaps; one-second overview/log includes the fractional tail. No detector-based skips.
- [ ] Every distinct texture/effect/transition measured with start/peak/end frames, PTS, layering,
      opacity, speed and easing; native crops resolve small details; no detail span is subsampled.
- [ ] Wipes with a ragged edge between two sharp shots logged as `ink_wipe` / `matte_wipe`, not smear.
- [ ] Fast-content SWAP / REPERFORM cuts marked in `cadence.note` (§3.8).
- [ ] Suspected music splices noted in `audio.hidden_edits` (§6.4).
- [ ] F3: supplied reference pixels preserved for a 1:1 request; no cropped watermark or silent stock replacement.
- [ ] EXACT retains source people/framing except requested changes. REMIX follows the planned cast and staging; every intended identity is verified, including body-only/occluded shots (§7).
- [ ] Letterboxed and windowed refs measured inside the picture area. Bars make the look stats read
      "dark", and canvas text triggers false cuts.
- [ ] Cut proposals checked against grain, flashes, text pops and letters flying out.
- [ ] Cadence per cut counted, not assumed.
- [ ] Required supplied lyric cues are preserved in a timed local file for final assembly; no full lyrics in video prompts or external full-lyrics scraping.
- [ ] No paid call during analysis. If something can only be learned by generating, it goes into
      the mode-appropriate limitations or an internal first-test plan that fits the internal hard cap and any existing user/account limit; `questions` stays empty.
