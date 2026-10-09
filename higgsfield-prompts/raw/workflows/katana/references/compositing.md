# Compositing: renderers, EDL schema, effect catalogue, grading and audio recipes

Local compositing handles grade, grain, flashes, transitions, text, stickers, doodles, cut-outs,
face-tracked graphics and camera moves without generation credits. Music and SFX use actual audio assets: preserve the reference/user track or use a suitable available stock/library recording; never synthesize music, beats, whooshes or effects in code. Historical Katana and Yaong assembly revisions
were code changes; facial appearance corrections are outside that scope. This file covers the canvas compositor kit in
`$RR/comp/` in full (sections 2-8), the ffmpeg recipes for grading, real-footage montages and audio
(sections 9-11), and the frame-exact rebuild `assemble.py` + `textlayers.py` (section 14).

Paths: `$RR` is the verified workflow scripts directory, normally
`$HF_WORKFLOWS/katana/scripts`; `$W` is the project workspace (`references/sandbox.md`).
Processing commands run in an available authorized sandbox. Read `references/<x>.md` from the
actual local package path or an available verified workflow-retrieval operation. Discover the
operation and its callable schema; do not assume a tool named a bundle-file reader exists.

## 1. Pick the renderer

Read `analysis/task-contract.json` before choosing the renderer. **Remix is the default; exact applies only to an explicit exact-reproduction request.** `explicit_locks` constrain both modes, and `creative_freedoms` permit the other output decisions. Keep observed source facts in `analysis/breakdown.json`; author the output in `plan/creative-plan.json` with its `output_target`, story or visual motif, output shot roles and `source_evidence`. In remix, source frame count, duration, shot order, composition and wording are not automatic output locks. Choose the canvas/slot renderer for a newly authored timeline. Section 14's reference-grid rebuild is for exact work or deliberately source-locked portions only; do not force a remix into it.

**No face or identity edits in code.** Do not use local face-swap libraries, head/face pastes, landmark or mesh warps, facial inpainting, skin retouching, or hand-drawn eyes, nose, mouth, hair or anatomy to create or repair likeness. Identity changes and facial corrections must come from a supported authorized image/video model with the supplied references; an unavailable route remains an explicit limitation, never a local pixel-edit fallback. Code may track coordinates, apply measured or authored whole-plate camera transforms and global grades, composite a complete generated subject with its mask, preserve or author separate text/graphics, and assemble recorded audio. It must not rebuild the face. Face tracking measures locations; it does not authorize altering the tracked features. `hairfix` remains disabled in both modes.

Complete [reference analysis](analysis.md) before the final production plan or any video generation: decode the full native-frame sequence, inspect every frame sheet and finish the per-second log across the entire timeline. All reference intervals, transitions and audio events must be accounted for. A sparse contact sheet, sampled clip or scene-level description is insufficient. If a section cannot be inspected, record the limitation and continue only independent work; never guess an effect, texture or transition to fill that gap.

Every exact-mode EDL shot, layer and transition must trace to observed source frames. A remix EDL traces to authored shot roles and applicable source evidence: it may create new scenes, camera angles, text and transitions within the user's locks. Its output frame grid is separate from the source analysis grid. The analysis and
`assemble.py` cut schema uses inclusive `f0`/`f1`; retain those fields unchanged. For an EDL renderer
that consumes half-open timing, convert explicitly to [f0,f1+1): start f0/fps and end (f1+1)/fps
on a verified constant-fps grid, or the actual decoded PTS boundaries for variable frame rate.
Coverage manifests likewise use [start,end_exclusive). Never mix these conventions. Record the
peak as an actual frame index, intensity over time, texture scale/direction/motion, blend operation and opacity, spatial mask/occlusion, stacking order, font geometry and source cadence. Inspect entry, peak, overlap and exit frames. In exact mode reconstruct each observed mechanism; document uncertain matches rather than asserting exactness. In remix use that analysis to choose deliberate effects for the new action and rhythm, recording their intended role and authored timing. Preserve intentional source roughness wherever locked or part of the chosen visual grammar; avoid generic cleanup or random preset decoration.

All numeric defaults and recipes below describe engine behavior only. Set creative parameters from the mode-aware plan and disable unplanned default layers. Exact mode matches source repetition, blending, timing and layers, with every output interval reviewed against its source interval. Remix reviews every output interval against the authored plan, continuity and explicit locks; intentional new content has no pixel-identical source counterpart. A favorable similarity score never proves exact 1:1 reconstruction. Seeded noise can animate a chosen texture, but must not randomly choose a different creative treatment for every shot.

In exact mode, reference fidelity overrides example settings and compositor convenience defaults. For a 1:1
request without explicit changes, prefer source stream copy or KEEP of all frames and audio. For a
requested localized change, modify only that region/time span. Match measured dimensions, rational
fps, frame count, crop, cadence, color properties, text, logos, watermark, identities and sound.
Do not add grain, stickers, SFX, margins, face avoidance, retiming or a new grade absent from the
reference. Examples are schemas, never design defaults. A generic glitch, stock transition or default font cannot replace measured source structure: reconstruct only the observed effect and match its texture, displacement, timing and layers frame by frame. If a renderer forces a different output,
choose an existing capable route or record the limitation; do not call that difference 1:1.

The bundled canvas renderer and encoder recipes below use an 8-bit SDR/bt709 pipeline; they do
not preserve HDR, higher bit depth or arbitrary source color metadata. When those properties are locked,
prefer source-stream reuse or an existing verified capable route; an unavailable faithful route leaves
an explicit color/bit-depth deviation, never a 1:1 claim or question. Remix may select an SDR output when
unlocked; record it in `output_target` and apply a verified conversion rather than merely retagging
HDR as bt709. Comparison previews may also be SDR; label them separately from the master.

The bundled canvas compositor, `assemble.py` and `textlayers.py` use a constant-rate frame grid.
Their source/plate preparation now checks actual decoded presentation timestamps and refuses VFR
instead of silently duplicating frames or flattening timing. Native-frame analysis remains available.
For exact or timing-locked VFR, preserve source streams where that fulfills the task or use an available
route retaining measured PTS and each frame interval. Verify that timing again with `compare.py`.
Equal frame count and average fps do not prove equal timing. Do not normalize locked VFR merely to
satisfy a helper; report an unavailable faithful route as partial. An unlocked remix can deliberately
map VFR material to its chosen constant output grid using an available verified conversion before
preparation; record the mapping and review motion/cadence rather than treating it as exact.

| Reference family                                                                   | Renderer                                                                                                                      | Why                                                                                          |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Hero swapped inside the reference's own footage (Genjutsu; window-in-canvas reels) | **Renderer A** (section 14): `$RR/assemble.py` (frame-exact rebuild) + `$RR/textlayers.py` (text from the reference's pixels) | Keeps the reference's own frames, window, baked text and audio; only the swapped cuts change |
| Authored remix or model-generated character/world with planned graphic overlays    | `$RR/comp/render.py` + `$RR/comp/engine.js` (this kit) + a project `comp/fx.js` for planned graphics the engine lacks         | Independent output timeline; facial appearance comes from the model, not code                |
| Montage of real footage (user clips, archival, sports), grade + speed + overlays   | ffmpeg slot engine (section 10)                                                                                               | Long sources, few graphics; ffmpeg filters are enough and fast                               |
| Pure typography / motion graphics                                                  | this kit, `special: color` shots + text events                                                                                | No plates needed                                                                             |

Mixing is normal: render the canvas comp, then grade/finish the result with an ffmpeg chain (section 9),
or feed supported constant-frame-rate `assemble.py` output into the kit as a plate. Whole-plate transforms, global grades and separate graphics are allowed; do not isolate and alter facial/head pixels to repair likeness.

## 2. Architecture of the kit

```
$RR/comp/engine.js   effect library + EDL interpreter (Canvas2D, no deps). Tables: LOOKS CAMERA LAYERS FACE
                     TRANSITIONS TEXT STICKERS DOODLES SPECIALS. API: RRC.boot / renderFrame / cues / register / hook
$RR/comp/page.html   loads engine.js, W/comp/edl.json and (if present) W/comp/fx.js; exposes window.renderFrame(i);
                     modes: render | stills | info | live preview
$RR/comp/render.py   prep (plates + mattes) | render | info | sfx | serve. Stdlib HTTP server on 127.0.0.1 serving W
                     (and the kit at /_rr/, $HF_WORKFLOWS at /_hf/), frame sink POST /frame/<i>, N headless Chrome
                     shards, ffmpeg encode (exact frame count), audio mux and aligned recorded-SFX bed mixing
$RR/comp/examples/   mixed_media/{edl.json,fx.js} (Katana port), kawaii/{edl.json,fx.js} (Yaong port)
```

Data flow:

```
plates mp4 --render.py prep--> W/plates/<clip>/00000.jpg.. + clip.json   (JPEG, BT.601 full range, 0-based)
matte mp4  --render.py prep--> W/mattes/<clip>/00000.png.. + clip.json   (white RGB + alpha)
faces.py track ------------->  W/faces/<clip>.json (+ .meta.json)
W/comp/edl.json + fx.js -----> Chrome shards: renderFrame(i) -> JPEG (--fmt png: PNG) -> POST /frame/i -> W/comp/frames/%05d.jpg
                               shard 0 also posts info (warnings, sticker log) + SFX cues
frames --ffmpeg--> x264 crf 18 yuv420p bt709 (-frames:v N) --mux--> W/out/comp.mp4
                   + ref audio stream-copied, or music+SFX mixed through alimiter(level=disabled) -> AAC 256k
```

Workspace files the kit reads or writes:

| Path                                                               | What                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plates/<clip>/%05d.jpg`, `plates/<clip>/clip.json`                | `{n, fps, fps_str, w, h, pattern, start, src, src_w, src_h, src_start_frame, prep_args}`. `prep_args` records the actual source/size/range/filter/quality and matte settings with workspace-relative input paths. With saved inputs and exact metadata, lean saves omit the images (and corresponding matte PNGs); `rr_rebuild` repeats that preparation. Legacy metadata without exact arguments keeps its images. |
| `mattes/<clip>/%05d.png`, `mattes/<clip>/clip.json`                | `{n, w, h, pattern, start, mode, src, fps}` (usually half the plate width)                                                                                                                                                                                                                                                                                                                                          |
| `faces/<clip>.json` (+ `.meta.json`)                               | `faces.py track` output: per-frame `{f, box:[x,y,w,h], score, eyes:[[x,y],[x,y]], nose, mouth:[[x,y],[x,y]], src}`                                                                                                                                                                                                                                                                                                  |
| `comp/edl.json`, `comp/fx.js`, `comp/stickers/`, `comp/fonts/`     | the project (saved by `rr_save`)                                                                                                                                                                                                                                                                                                                                                                                    |
| `comp/frames/` (+ `preview/`, `stills/`, `unused/`)                | every frame dump: the render, `--preview`, `--stills`. `rr_save` leaves out `comp/frames*` and `comp/stills/`; the next render recreates them                                                                                                                                                                                                                                                                       |
| `qa/comp_stills.jpg`                                               | stills QA sheet (`--stills`; the stills themselves are in `comp/frames/stills/`)                                                                                                                                                                                                                                                                                                                                    |
| `comp/render.log`                                                  | timestamped progress (poll it in background runs)                                                                                                                                                                                                                                                                                                                                                                   |
| `comp/render_summary.json`, `comp/info.json`, `comp/sfx_cues.json` | render stats, EDL validation and visual cue diagnostics; SFX audio comes from an actual recording                                                                                                                                                                                                                                                                                                                   |
| `out/comp.mp4`, `out/comp_preview.mp4`, `out/comp_part.mp4`        | deliverables                                                                                                                                                                                                                                                                                                                                                                                                        |

Rendering rules the engine guarantees:

- Frame `f` is sampled at `t = (f + 0.5) / fps`. A shot owns the frames whose sample time is in `[t0, t1)`.
  Local time `lt = t - t0`. Source frame `si = floor((src + lt*speed) * clip.fps)` (clamped). 24 fps plates
  in a 30 fps edit at speed 1 therefore repeat one frame in four, like the Yaong final.
- Slow motion (6.1.1): at `0.3 <= |speed| < 1` the plate is the two neighbouring source frames blended by the
  fractional index; below 0.3x, with `blend: false`, on freezes and on stutters it is the whole frame `si`.
  Mattes, faces and `S.si` always use the whole frame.
- Randomness is only `hash(a,b,c)` / `rng(seed)` keyed by frame, boil step `b = floor(f / canvas.boil)` and
  effect seeds. Any frame renders identically in any shard, order or rerun (the test checks stills == render).
- Logical coordinates are canvas pixels (`canvas.w x canvas.h`); `--preview` renders at half the physical size
  with the same geometry (only the per-pixel xerox grain differs).
- Output length is exactly `canvas.frames`: use the authored `output_target` in remix and the reference's decoded frame count in exact mode unless explicitly changed.

## 3. Quick start (sandbox)

Write the final EDL only after complete native-frame analysis and the full per-second timeline log have established every source event, and every paid job of the batch is terminal and catalogued (plates, in-points). A job that
turns terminal after the EDL exists: catalogue it and review the EDL before rendering. In the 2026-10-08 Katana
run a 10 s plate of five timecoded 2 s shots landed almost exactly on its timecodes (VERIFIED live); still take
the in-points from the catalog sheet, since gestures inside a shot drift.

```bash
<BOOT> && rr_ws <slug>
# lean state saves drop these frame folders; after a cold rr_restore run rr_rebuild first (references/sandbox.md section 9)
python3 $RR/comp/render.py prep $W gen/plate_A.mp4 --clip A --width 1440 --mask gen/plate_A_matte.mp4   # cover-cam edits
python3 $RR/comp/render.py prep $W gen/plate_B.mp4 --clip B --mask gen/plate_B_matte.mp4 --close 8      # native size for face-lock
python3 $RR/faces.py track $W --clip gen/plate_B.mp4 --name B          # only where graphics follow a face
cp $RR/comp/examples/kawaii/edl.json comp/edl.json                      # schema only; replace all content/settings from the mode-aware creative plan
python3 $RR/comp/render.py info $W                                      # validate: frames, warnings, sticker placement
python3 $RR/comp/render.py render $W --no-sfx --stills cuts                      # QA sheet qa/comp_stills.jpg (look at it)
# foreground holds ~250 frames of a 1440x1080 xerox edit (26 s, section 12); background:true for anything longer:
rr_bg logs/render.log python3 $RR/comp/render.py render $W --no-sfx && rr_put out/comp.mp4 '<UPLOAD_URL_MP4>' \
  && rr_save '<UPLOAD_URL_STATE>' '<STATE_CONTENT_TYPE>'
```

State archive: reserve `<slug>_vN_state.tar.gz` with `media_upload` (a general file) before the command and pass
the `content_type` from that reply as `rr_save`'s second argument (`application/octet-stream` for archives,
verified live; never `.tgz`, which is refused); the presigned PUT is signed over it (`references/sandbox.md`
section 9).
`render.py $W ...` without a subcommand means `render`. Poll with `rr_wait logs/render.log 25` or read
`comp/render.log`. Never open a browser for the user; `render.py serve $W` only prints a URL.

## 4. render.py reference

```
render.py prep W VIDEO --clip ID [--width N | --height N | --native] [--quality 3] [--start F] [--count N] [--vf FILTERS]
                       [--mask MATTE] [--mask-mode divide|threshold|luma|alpha] [--mask-width N] [--thr 26] [--close N]
render.py render W [--edl comp/edl.json] [--fx /comp/fx.js] [--jobs N] [--preview | --rs 0.5] [--frames A:B]
                   [--stills LIST [--sheet qa/comp_stills.jpg] [--cols C] [--tile-w PX] [--max-bytes 500000]]
                   [--out out/comp.mp4] [--crf 18] [--preset medium] [--quality 0.93] [--fmt jpg|png]
                   [--audio auto|none|PATH] [--audio-start S] [--aac] [--sfx-file PATH | --no-sfx]
                   [--chrome PATH] [--gpu] [--timeout 1800] [--stall 120] [--clean]
render.py info W     -> comp/info.json + comp/sfx_cues.json (frames, shots, warnings, sticker log, boot ms)
render.py serve W [--port P]
```

- `prep`: plates go to `plates/ID/%05d.jpg` (0-based) with an explicit `bt709 -> bt601 full-range` matrix
  (Chrome decodes JPEG as JFIF); mean error vs the source < 1.5 levels. Default size is native; use
  `--width <canvas w>` for cover-fit edits (Katana: 1664x1248 -> 1440x1080) and native size for face-lock
  (zoom headroom: Yaong needed up to 1.8x). `--start/--count` trims (faces are offset by `src_start_frame`).
  `--vf` inserts ffmpeg filters before the scale (bake a grade). Mask modes:
  `divide` = `remove_background` output (subject on black, no alpha): alpha = matte / original with
  `if(lt(B,34),if(gt(A,10),255,0),clip((A*255/B-70)*1.9,0,255))`, `gblur=0.7`; `threshold` = luma > `--thr`
  (tv-range, 26 ~ 8/255 above black); `luma` = luma as alpha (SAM binary masks); `alpha` = the video's own
  alpha. `--close 8` = dilate x8 then erode x8 (fills holes, Yaong). Mattes are white RGB + alpha PNGs.
- `render`: shards `[0, frames)` over `--jobs` Chrome instances (default `min(cpus/2, 6, ceil(frames/40))`:
  4 on the 8 vCPU sandbox), JPEG dump at `--quality` into `comp/frames/`, then `libx264 -crf 18 -pix_fmt yuv420p`,
  BT.601 full -> BT.709 tv conversion, bt709 VUI (`h264_metadata` bsf), `-frames:v N`, `-r fps`. Verifies the
  encoded frame count. `--fmt png` dumps lossless PNG instead (about 5-10x bigger and slower; for pixel-exact QA
  of grain/threshold looks, or frames you grade further); the encode converts RGB -> BT.709 tv, so both dumps
  give the same picture. The frame count comes from `canvas.frames` (else `canvas.dur` rounded like the page's
  `Math.round`, else the last shot end) and must equal the count the page reports, or the render aborts.
  A shard that crashes or makes no progress for `--stall` seconds is relaunched once for its
  missing frames; a page error (EDL, fx.js, missing plates) aborts at once with the message.
  `--stills 0,24,60 | 1.5s,3s | cuts | A:B` renders stills (same pixels as the render) into `comp/frames/stills/`
  and a labelled QA sheet <= 500 KB for `image_paths`. `--preview` = half resolution -> `out/comp_preview.mp4`
  (dump in `comp/frames/preview/`).
  `--frames A:B` renders and encodes only that range (`out/comp_part.mp4`, audio offset follows).
- Audio (`--audio auto` = `edl.audio.src`, else `ref/ref.mp4|m4a`, else silent): without SFX the track is
  stream-copied (AAC/MP3; `--aac` forces AAC 256k), whole when it starts at 0 and is at most 0.5 s longer than
  the picture (the reference's own audio), else cut with `-ss`/`-t`; with SFX it is mixed (section 11) and
  checked for AAC overshoot. Results (copy/trimmed, `md5_equal` against the source track, codec, sample rate,
  LUFS, true peak, attempts) are in `comp/render_summary.json` `audio`.
- Chrome: `$CHROME`, the Playwright Chromium in `/ms-playwright`, the headless shell, macOS Chrome, then PATH.
  Flags: `--headless=new --disable-gpu` (+ `--no-sandbox --disable-dev-shm-usage` on Linux); extra flags via
  `RR_CHROME_FLAGS`. `--gpu` drops `--disable-gpu` (local Macs only; 3x faster on blur-heavy edits).

## 5. EDL schema (`W/comp/edl.json`)

Times: every absolute time field (`t0`, `t1`, `t`, text/sticker `t0/t1`, `wkeys`) accepts seconds (`3.423`),
beats on the `beat` grid (`"b8"`, `"b10.75"` = `beat.t0 + n*60/bpm`) or frame starts (`"f59"` = 59/fps).
`f0`/`f1` (integer frames) may replace `t0`/`t1`. Relative fields (`at`, `d`) are seconds from the shot start.
Colours: `"#rrggbb"`, `"rgba(...)"`, `[r,g,b(,a)]` or `"$name"` (palette entry). Animated numbers:
`{"from": a, "to": b, "ease": "lin|in2|in3|out2|out3|inout|outback", "over": 0.85, "at": 0}` (progress over
`over` x shot duration) work in looks and any `av`-resolved parameter.

```jsonc
{
 "canvas":  {"w": 1440, "h": 1080, "fps": 24, "frames": 120, "bg": "#ffffff", "boil": 2},
            // illustrative numbers; fps/frames come from output_target in remix, source grid in exact; boil = frames per doodle wobble step
 "beat":    {"bpm": 139.6, "t0": -0.015},          // grid for "b<n>" times and sticker burst steps (1/16 note)
 "palette": {"ink": "#0b0b0b", "accent": "#b6ff1f", "accent2": "#6fd600", "lav": "#c98be0", ...},  // defaults in 5.1
 "font_stacks": {"heavy": "...", "sans": "..."},  // CSS font-family fallbacks for font text
 "fonts":   [{"family": "Anton", "url": "comp/fonts/Anton-Regular.ttf"},              // font file (section 13: fonts)
            {"family": "Inter", "weight": 800, "css": "https://fonts.googleapis.com/css2?family=Inter:wght@800"}],  // or a stylesheet
 "look":    "x",                                    // default plate look for every shot (section 6.2)
 "looks":   {"x_ramp": {"type": "xerox", "key": true, "white": {"from": 0.68, "to": 0.42, "ease": "in2"}}},  // named presets
 "cam":     {"type": "facelock", "ld": 0.15},       // defaults merged under clips.<id>.cam and every shot's cam
 "clips": {
   "A1": {"frames_dir": "plates/A1", "mask_dir": "mattes/A1", "faces": "faces/A1.json",
          "pattern": "%05d.jpg", "start": 0, "n": 241, "fps": 24, "w": 1664, "h": 1248,   // read from clip.json when omitted
          "faces_size": [1664, 1248],                                                    // pixel space of the faces file if ambiguous
          "cam": {"crop": [0.5, 0.35]}}                                                  // illustrative only; use planned remix framing or locked source geometry (6.1.2)
 },
 "assets": {
   "stickers": ["comp/stickers/s01.png", "..."],     // or {"dir": "comp/stickers", "n": 30, "pattern": "s%02d.png", "start": 1}
   "sticker_look": {"type": "xerox", "key": true, "black": 0.05, "white": 0.92, "grit": 0.3},   // optional: run stickers through a look
   "cutouts": [{"clip": "f1a", "t": 1.5, "cam": {}, "look": null}],   // die-cut stickers of the subject (needs mask_dir)
   "cutout_look": null, "cutout_border": 16, "cutout_border_color": "#fffdf8"
 },
 "shots":    [ /* 5.1 */ ],
 "specials": [{"t0": "b7.75", "n": 2, "type": "black", "sparkle": false}],   // whole-frame inserts over the shots (n frames | d s | t1)
 "text":     [ /* global text events, 6.6 */ ],
 "stickers": [ /* sticker events, 6.7 */ ],
 "post":     {"grain": {"amt": 0.32}, "glow": 0.14, "dust": true, "border": true},   // fx applied to every shot (a shot's fx of the same name overrides; false disables)
 "sfx":      {"auto": false, "cues": [], "hits": false}, // synthesis disabled; mix actual SFX recordings only
 "audio":    {"src": "ref/ref.mp4", "start": 0, "sfx": false, "codec": "copy"} // no audio.beat; for a requested recorded SFX bed, set sfx_src to its verified aligned file
}
```

### 5.1 Shots

```jsonc
{"t0": "b8", "t1": "b9",        // t1 defaults to the next shot's t0 (or the end); f0/f1 for frames
 "clip": "b0",                  // or "special": "flash" | {"type": "collage", ...} (6.8); clip "FLASH|WHITE|BLACK|COLLAGE" also works
 "src": 3.0, "srcf": 72,        // source in-point (seconds or frame); first frame of the shot shows exactly this source frame
 "speed": 1, "speed1": 0.5,     // 0 = freeze; speed1 = linear ramp to this speed over the shot; negative = reverse
 "blend": false,                // slow-mo frame blend: default on at 0.3 <= |speed| < 1, true forces it < 0.3 (6.1.1)
 "loop": "clamp|loop|pingpong", // what happens past the clip end (clamp holds the last frame and warns)
 "cam":  {...},                 // 6.1 (merged over edl.cam and clips.<id>.cam)
 "look": "x" | {...},           // 6.2 (default edl.look)
 "fx":   {"contour": true, "doodles": 2, "punch": true, "word": {"text": "HANA", "at": 0.07}},   // named effects (6.3-6.5); true = defaults, number = {v: n}
 "layers": [{"type": "text", "text": "...", "phase": "over", "order": 120}],                 // ordered extra effects (same names as fx)
 "in":  {"type": "flashlight", "d": 0.14},   // transition sugar -> fx (6.5); "out" likewise; a list is allowed
 "face": {"box": [x0, y0, x1, y1]} | false,  // manual face box in source px (ECU / failed detection) or disable face graphics
 "bg": "#ffffff",                            // plate background where the camera reveals edges
 "seed": 13, "note": "free text"}
```

Per shot, `fx.stickers: false` / `fx.text: false` hide the global sticker / text layers (Katana's dead
silence), `fx.cutout: false` / `fx.outline: false` stop the automatic subject cut-out.

Draw order per plate frame: plate (camera) -> `trail` -> look -> **back** (graphics behind the subject) ->
**subject** (outline, cut-out of the subject from its matte, glow) -> **over** (contour, face graphics, doodles,
stickers at 50, global text at 60) -> **post** (full-frame treatments, transitions) -> **final** (vignette,
grain, dust, border). Specials draw their fill, then only the global layers / final fx in their `allow` list.

## 6. Effect catalogue

`S.fo` = the face on screen (eye midpoint, eye distance `D`, roll); "eye units" = multiples of `D`
from the eye midpoint, x right, y down, rotated with the face (Yaong `fp()`).

### 6.1 CAMERA (`shot.cam`; modifiers may also sit in `fx`, Katana style)

| Key                  | Params (default)                                                                                                                                                                                                     | Effect                                                                                                                                                      |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| frame (default type) | `z` 1, `ax` .5, `ay` .5 (source anchor, 0..1), `sx` .5, `sy` .5 (screen target), `rot` 0, `mir` 0, `fit` cover\|contain\|width\|height, `cover` false                                                                | Place source point (ax,ay) at screen (sx,sy), scale `fit x z`. `cover: true` enlarges/shifts so no edge shows                                               |
| `crop`               | `[x, y]` (0..1 of the source) or `y` alone                                                                                                                                                                           | Crop centre: sets `ax, ay` and `cover: true`, so the window is clamped inside the plate. Use authored framing in remix or measured locked geometry (§6.1.2) |
| `type: "facelock"`   | `ld` .12 (eye distance as fraction of W), `lx` .5, `ly` .4 (eye midpoint target), `z0` 1 -> `z1` 1.04 (out3 over the shot), `kick` .035 (x exp(-lt*`kick_rate` 14)), `lockRot` 1 (roll levelling 0..1), `cover` true | Yaong hard face-lock: eyes pinned, roll levelled, never reveals plate edges. Needs `clips.<id>.faces`                                                       |
| `zoom`               | `z0` 1, `z1` 1.08, `ease` out3                                                                                                                                                                                       | Zoom across the shot                                                                                                                                        |
| `push`               | `v`/`rate` .1 per s                                                                                                                                                                                                  | Linear push (Katana: on freezes)                                                                                                                            |
| `punch`              | `v`/`amt` .07, `d` .25 s, `curve` 2                                                                                                                                                                                  | Punch-in at the cut, decays                                                                                                                                 |
| `ladder`             | `steps` [1, 1.12, 1.24, 1.36] (or the array itself)                                                                                                                                                                  | Zoom ladder: shot split into equal steps (16th-note jump zooms)                                                                                             |
| `pan` / `tilt`       | `dx`, `dy` (fraction of W/H per s) / `v`                                                                                                                                                                             | Drift                                                                                                                                                       |
| `roll`               | `v` rad, `rate` rad/s                                                                                                                                                                                                | Rotation                                                                                                                                                    |
| `handheld`           | `amp` 6 px, `hz` .7, `rot` .004 rad, `seed` 7                                                                                                                                                                        | Smooth noise drift                                                                                                                                          |
| `shake`              | `amp` [16, 12] px, `d` .25 s (.125 on freezes), `every` boil frames                                                                                                                                                  | Katana boil-stepped shake decaying from the cut                                                                                                             |
| source fx `stutter`  | `n` 3, `step` 1                                                                                                                                                                                                      | Loops n source frames from the in-point (Katana 3-frame stutter)                                                                                            |
| fx `trail`           | `n` 3, `step` 2, `alpha` .35, `op`                                                                                                                                                                                   | Ghost trail of earlier source frames (before the look)                                                                                                      |

Camera keys merge `edl.cam` < `clips.<id>.cam` < `shot.cam`.

#### 6.1.1 Speed and slow motion

In exact mode preserve the reference's cadence and holds. In remix choose cadence, holds and speed
changes for the authored shot role, respecting timing locks. The table describes interpolation;
it does not prescribe smoothing or constant motion for every shot.

| Shot keys                                                                 | Plate frames                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `speed` 1 (default), or above 1                                           | whole frames (a 24 fps plate in a 30 fps edit repeats one frame in four, like the Yaong final)                                                                                                                                                                                                                           |
| `0.3 <= abs(speed) < 1` (reverse and `speed1` ramps are judged per frame) | **frame-blended slow motion**, the default: `(1 - w) * frame i0 + w * frame i1`, the two source frames around the fractional index `x = (src + lt*speed) * clip.fps - 0.5`, never earlier than the in-point. The accepted Aura films: frame-blended slow-mo, never duplicated frames (duplicates judder: Jensanity f226) |
| `abs(speed) < 0.3`                                                        | nearest whole frame: a blend this slow reads as a ghost or a matte halo                                                                                                                                                                                                                                                  |
| `blend: false`                                                            | nearest whole frame at any speed: fast limbs, slowed Genjutsu faces (blend ghosts)                                                                                                                                                                                                                                       |
| `blend: true`                                                             | forces the blend below 0.3x as well (slow drifts, backgrounds)                                                                                                                                                                                                                                                           |
| `speed: 0` (freeze), fx `stutter`                                         | always a whole frame: a freeze holds on an integer frame (set `srcf` to the frame you want)                                                                                                                                                                                                                              |

Mattes, faces, `trail` and fx.js see the whole frame `S.si`; `S.blend = {i0, i1, w}` when the plate is blended.
`collage` panels take the same `speed`/`blend` keys. Real-footage montages (section 10) do the same in ffmpeg on
the slot (`framerate` filter, section 10); never pay for `fps_boost` or deflicker, this is code. QA check #12 in
`references/qa-delivery.md` (frozen / duplicate frames, cadence per cut) catches the judder a missing blend leaves.

#### 6.1.2 Map generated takes to the selected output geometry

Probe actual take dimensions. In exact mode or for a framing lock, preserve the measured canvas,
picture window and subject placement: derive scaling, crop and padding from source comparisons.
An aspect mismatch alone never authorizes discarding locked heads, limbs, graphics or scenery.
In remix, compose whole plates for the authored shot role and `output_target`: deliberate crops,
reframing, scales and camera moves are allowed within locks. Verify that subject/action remains
legible and continuity intentional. If a locked mapping cannot be preserved, select an authorized
alternative or report the precise deviation without questions.

The kit's `cam.crop` enables cover-fit. Set per-shot coordinates from authored remix composition
or measured locked source crop. For example, `[0.5,0.35]` is an illustrative coordinate,
not a default or a rule for 4:3 footage. `render.py info` warnings about a taller take are prompts
to inspect the intended geometry, not instructions to crop automatically. `assemble.py` accepts
`crop: [x,y,w,h]` in generated pixels; compute this rectangle from the measured mapping, never a
fixed y range. Historical examples using 1664×1248 footage in a 16:9 window do not prescribe the
current canvas, crop or subject placement.

- Prefer local crop/pad over paid `reframe`, and local processing over paid `fps_boost` / deflicker only when the selected output plan actually needs it; never smooth away locked source cadence. Do not buy
  a video upscale of footage that ships at native size, or `video_analysis_create`. Never reframe a driving video.
  If an existing requested replacement requires a paid reframing route, use it only within the
  internal hard cap and any existing user/account limit; otherwise retain the best faithful free result and report its limitation.
  Follow existing task/account authority and `references/budget.md`; if a route needs unavailable
  interactive consent, use a supported authorized fallback or state the limitation. Never request
  an opt-in, credit confirmation or a changed canvas.

### 6.2 LOOKS (plate grade; `shot.look` or `edl.look`; string = preset/type, object = `{type|preset, ...}`)

| Type / preset            | Params (default)                                                                                                                                                                                                                                                              | Effect                                                                                                                                                                        |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `xerox`                  | `black` .13, `white` .80 (levels), `grit` .42 (noise into the threshold), `hard` .62 (threshold mix), `ink` [10,10,10], `paper` [255,255,255], `invert`, `grain_every` 1 (frames per noise step), `key`                                                                       | Katana xerox: S-curve levels, hard threshold with boiling grain; `key` keeps one colour as a 2-tone ramp                                                                      |
| `xerox.key`              | `true` = Katana lime hair. Channel mode: `channel` g, `lo` .06, `width` .09, `vmin` .16, `vw` .16. Hue mode: `hue` [h0, h1] deg (wraps), `soft` 15, `sat` .25, `val` .16. Both: `dark` [10,38,0], `light` [196,255,52], `amt` 1, `stoch` .8, `mix` .4, `lift` .12, `gain` 1.1 | Accent key (any colour: `{"hue": [300, 345], "light": "$accent"}` for pink)                                                                                                   |
| `duotone` / preset `duo` | `paper` $accent, `ink` [8,12,4], `grit` .5                                                                                                                                                                                                                                    | Two-colour threshold                                                                                                                                                          |
| `neg`                    | xerox params                                                                                                                                                                                                                                                                  | Inverted xerox (contour turns white automatically)                                                                                                                            |
| `levels`                 | `black`, `white`, `hard` .85                                                                                                                                                                                                                                                  | Katana per-cut levels (`lv`)                                                                                                                                                  |
| `threshold`              | `grit` 0, `hard` 1                                                                                                                                                                                                                                                            | Pure threshold                                                                                                                                                                |
| `grade`                  | `filter` (CSS filter string), `layers` [{`op` soft-light\|screen\|multiply\|overlay..., `color`, `alpha`}]                                                                                                                                                                    | Filter + colour washes. Preset `kawaii` = Yaong pink lift: `brightness(1.08) contrast(1.02) saturate(1.12)` + soft-light rgba(255,160,210,.24) + screen rgba(255,240,248,.03) |
| `filter`                 | `filter`                                                                                                                                                                                                                                                                      | Any CSS filter (`hue-rotate(90deg)`, `sepia(1)`, `blur(2px)`)                                                                                                                 |
| presets                  | `clean` (none), `x` (xerox + key), `xl` (x, black 0, white .5), `duo`, `neg`, `kawaii`, `bw` (grayscale, contrast 1.22, brightness 1.04)                                                                                                                                      |                                                                                                                                                                               |

Ramps: `{"type": "xerox", "key": true, "black": {"from": .06, "to": 0, "ease": "in2", "over": .85}}` (Katana `x>xl`).

**Readability after a global look.** A newly added full-plate threshold/grade can crush detail already present in the generated/source face. Undo or tune that same whole-plate filter against the intended full shot; compare background, subject and palette together. Use measured source appearance in exact mode and the authored look plus explicit locks in remix. This corrects the compositor's filter, not facial anatomy. Never apply a face-only curve, skin cleanup, facial ROI mask, painted highlight, missing-eye reconstruction or local retouch. If underlying generated features are wrong before grading, use a supported authorized model. A preset is never an automatic design default.

### 6.3 LAYERS (graphics and full-frame treatments; `fx.<name>` or `layers[]`)

| Name                | Phase   | Params (default)                                                                                                                                                   | Effect                                                                                                                                                                                                    |
| ------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `big`               | back    | `text`, `size` 600, `x0` .17, `x1` .83, `y` .55, `fill` $bigfill, `stroke` $bigstroke, `lw` 8, `at`, font keys                                                     | Giant letters behind the subject (Yaong DUL); forces the cut-out                                                                                                                                          |
| `stairs`            | back    | `seed` 3, `size` 34, `cells` [[i,j]..], `x` .025, `y` .028, `color` $pink, `color2`                                                                                | Pixel stair pattern                                                                                                                                                                                       |
| `outline`           | subject | `r` 14 px, `color` $outline, `blur` 3, `alpha` .95, `dx` 16, `dy` 6                                                                                                | Offset glow outline of the matte (auto with burst/big)                                                                                                                                                    |
| `cutout`            | subject | -                                                                                                                                                                  | Re-draws the subject from its matte over back graphics (auto)                                                                                                                                             |
| `glow`              | subject | `v` .14, `blur` 5                                                                                                                                                  | Screen-blended soft glow (Yaong)                                                                                                                                                                          |
| `contour`           | over    | `dist` 12, `w` 4.2, `zigs` 5, `color` ink (white on neg), `blur` 2.2, `seed`, `echo` false, `echo_dist` 26                                                         | Katana pen contour: marching squares on the matte, broken offset strokes + zigzag accents                                                                                                                 |
| `glint`             | over    | `from` [.18,.4], `to` [.54,.4] (screen 0..1; `src: true` = source px), `r` 175, `d` .28, `at`, `color` $accent                                                     | Sweeping accent star with rays                                                                                                                                                                            |
| `doodles`           | over    | `v` density 0..3 (= 0/5/10/16 marks) or `n`, `scratch` extra forced scratches, `mono`, `types` [...]                                                               | Katana ink doodles on a ring around the dilated silhouette, trailing the motion, avoiding face and text; punch(+shake) cuts add scratches                                                                 |
| `face_doodles`      | over    | `items` [{`t`, `o`:[x,y] eye units, `s`, `r`, `at`}] or auto: `pool`, `n` 6, `seed`, `ld`, `ly`, `ears`, `avoid_top`, `spacing` 1.35; `colors` {line, fill, blush} | Yaong boiling kawaii stickers locked to the face                                                                                                                                                          |
| `doodle`            | over    | `t` heart, `pos` [.5,.5], `size` 80, `rot`, `at`, `seed`, `alpha`                                                                                                  | One kawaii doodle at a screen position                                                                                                                                                                    |
| `word`              | over    | `text`, `at`, `dx` 0, `dy` 1.05 (eye units), `k` .8 (size = clamp(D*k, `min` 78, `max` 150)), `fill`, `stroke`, `lw` 4, `shadow`                                   | Word on the face with a 3-frame pop (Yaong HANA/SET)                                                                                                                                                      |
| `type`              | over    | `parts` [[text, bold\|thin\|heavy]], `at`, `dt` .05 s/char, `base` 0, `dx` 0, `dy` 1.15, `k` .86, `min` 80, `max` 140, `pos` (no face)                             | Typewriter (Yaong SARANG+HAE)                                                                                                                                                                             |
| `text`              | over    | one font-text item or `items` [...] with `at`/`d` relative to the shot (keys as TEXT.font)                                                                         | Captions inside a shot                                                                                                                                                                                    |
| `graffiti`          | over    | TEXT.graffiti keys with `at`/`d` relative to the shot                                                                                                              | A tag inside one shot                                                                                                                                                                                     |
| `slash`             | over    | `at`, `dx` 0, `dy` .75, `seed` 4, `n` 4, `fill`, `stroke`                                                                                                          | White slashes flying out (Yaong)                                                                                                                                                                          |
| `sparkle` / `splat` | over    | `pos`, `r`, `seed`, `color` / `items` [{`pos`, `r` 160, `n` 16, `color`, `color2`}]                                                                                | Ink sparkle / splatter field                                                                                                                                                                              |
| `bw`                | post    | `filter`, `bars` [top, bottom] px, `color`                                                                                                                         | B&W of the whole frame (+ letterbox bars, Yaong F1)                                                                                                                                                       |
| `letterbox`         | post    | `v`/`top`/`bottom` .1 (fraction of H), `color`                                                                                                                     | Bars                                                                                                                                                                                                      |
| `tint`              | post    | `color`, `v` .3, `op` screen, `d` (fades out over d)                                                                                                               | Colour wash                                                                                                                                                                                               |
| `tag`               | post    | `text`, `pos` bottom (or face), `bx` .5, `by` .9, `dx` -.45, `size` 34                                                                                             | Small handle / watermark (Yaong nabi.cam*)                                                                                                                                                                |
| `invert`            | post    | `at`, `d`, `amt` 1                                                                                                                                                 | Invert everything (graphics included)                                                                                                                                                                     |
| `rgbsplit`          | post    | `v` 6 px, `at`, `d`, `decay` s                                                                                                                                     | Red / cyan channel offset                                                                                                                                                                                 |
| `strobe`            | post    | `every` 2, `color` #fff, `amt` 1, `at`, `d`                                                                                                                        | Alternate-frame flashes                                                                                                                                                                                   |
| `leak`              | post    | `color`, `color2`, `amt` .55, `x` .85, `y` .2, `r` .6, `drift` .1, `seed`, `op` screen                                                                             | Drifting light leak                                                                                                                                                                                       |
| `vignette`          | final   | `v` .35, `r0` .45, `r1` .95, `color`                                                                                                                               |                                                                                                                                                                                                           |
| `grain`             | final   | `v`/`amt` .32, `op` soft-light, `tiles` 4, `cell` 2, `mono` true                                                                                                   | Pre-baked noise tiles offset per frame                                                                                                                                                                    |
| `dust`              | final   | `n` 14                                                                                                                                                             | Ink/white specks per frame                                                                                                                                                                                |
| `border`            | final   | `color` $ink                                                                                                                                                       | Katana hand-inked ragged frame edge. Its dark edge reads as bars to `compare.py check` (a false `bars` FAIL in the 2026-10-08 Katana run); a declared border is a NOTE (`references/qa-delivery.md` §1.2) |

### 6.4 FACE (need a face: `clips.<id>.faces` or `shot.face.box`)

This historical table contains separate decorative overlays anchored to tracking coordinates, not face-edit tools. Exact mode enables a graphic only when it exists in the source at measured frames/geometry. Remix may deliberately author a visibly separate graphic for the scene's motif; keep its layer distinct from the underlying face. A fang sticker is not permission to redraw teeth; blush, whiskers or `eye_sparkle` are not skin/eye corrections. Never auto-enable these from a template or use them to improve likeness, hide an identity failure or invent facial features. `faces.py` and `facelock` perform detection/whole-plate camera alignment, not local facial warping.

| Name     | Params (default)                                                                                                                                                                                  | Effect                                                                                                       |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `cheeks` | `color` $accent2, `force`                                                                                                                                                                         | Katana zigzag cheek marks under each eye (skipped where the track is interpolated > 6 frames unless `force`) |
| `fangs`  | `color` $accent, `len` .3, `dy`, `force`                                                                                                                                                          | Two accent fangs from the mouth line                                                                         |
| `ears`   | `at`, `size` .9, `dx` 1.25, `dy` -1.72, `colors`                                                                                                                                                  | Cat ears, clamped inside the frame                                                                           |
| `whisk`  | `at` .03, `dx` 1.05, `dy` 1.05                                                                                                                                                                    | Whiskers                                                                                                     |
| `blush`  | `at` .05, `dx` .78, `dy` .72, `size` .36                                                                                                                                                          | Blush hearts                                                                                                 |
| `ast`    | `dx` .02, `dy` .72, `size` .38                                                                                                                                                                    | Spinning asterisk on the nose                                                                                |
| `burst`  | `letters`, `seed` 1, `rot` 0, `dx` 0, `dy` .4, `r` 3.5, `ls` .88 (letter size), `lr` 2.95 (arc radius), `a0` -2.85, `a1` -.05, `ry` .66, `points` 15, `fill` $lavl, `stroke` $lav, `rays`, `lw` 3 | Starburst behind the subject (forces the cut-out) + popping arc letters in front (Yaong YAONG)               |

### 6.5 TRANSITIONS (time-windowed; `fx.<name>` or `in`/`out` sugar)

| Name                 | Sugar               | Params (default)                                               | Effect                                                                                                  |
| -------------------- | ------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `fin` / `fout`       | `flashlight` in/out | `d` .14 / .07, `k` 1 / .8, `blocks` true / false               | Yaong flashlight burn: exposure blow-out where darks survive + white bloom from the face + pixel blocks |
| `magenta`            | `magenta` in        | `at`, `d` .2, `from` 40, `color` $magenta, `color2` $magenta2  | Colour-washed mosaic entry                                                                              |
| `mosaic`             | `mosaic` in/out     | `at`, `d` .08, `from` 56, `to` 4                               | Mosaic dissolve                                                                                         |
| `glitch`             | `glitch`            | `at`, `d` .1, `amt` .55, `seed` 9                              | Mosaic tiles + white wash blocks                                                                        |
| `blur`               | -                   | `at`, `d` .12, `max` 16, `frame` true                          | Blur pulse with a thin frame (Yaong)                                                                    |
| `blurIn` / `blurOut` | `blur` in/out       | `d` .12 / .5, `max` 14 / 22, `at` (out: .05 or dur-d), `color` | Blur in from / out to a pale wash                                                                       |
| `white`              | `white` in/out      | `at`, `d` .067, `color`                                        | Solid frames (2 white frames = .067 s at 30 fps)                                                        |
| `flash`              | `flash` in/out      | `at`, `d` .1, `color`, `amt`                                   | Fading flash                                                                                            |
| `dip`                | `dip` in/out        | `d` .15, `color` #000                                          | Dip from / to a colour                                                                                  |

**Ink-brush and matte wipes** (breakdown `ink_wipe` / `matte_wipe`, identified as in `references/analysis.md` §3.4)
have no built-in, and a blur or smear is the wrong rebuild: the reference shows both shots sharp on either side of
a ragged edge. Two ways:

- **Canvas kit, cover version:** a project `fx.js` layer in the `post` phase that paints ink brush strokes
  (`U.poly` / `U.drawStrokes`, seeds from `hash()`) sweeping across the last 2–3 frames of shot A until the frame
  is covered, and sweeping off the first 2–3 frames of shot B. The cut hides under the ink.
- **Reveal version (shot B through the moving edge),** in ffmpeg on the two rendered slots or shots: a grayscale
  matte clip, white = the incoming shot, merged with `maskedmerge` in planar RGB (`gbrp`; in yuv420p the grey
  matte's neutral chroma mixes the two shots' colours 50/50 everywhere). Tested on local ffmpeg 8: before the
  wipe the output equals shot A, after it shot B, within x264 noise (the filter exists in 5.1). A procedural
  bristled edge sweeping left to right over 5 frames from frame 8:
  ```
  ffmpeg -f lavfi -i "color=black:size=<w>x<h>:rate=<fps>,format=gray" -frames:v <n> \
    -vf "geq=lum='255*lt(X+60\,1.25*W*clip((N-8)/5\,0\,1)+28*sin(Y/9)+14*sin(Y/2.7)+9*sin(Y*1.9))'" matte.mp4
  ffmpeg -i a.mp4 -i b.mp4 -i matte.mp4 -filter_complex \
    "[0:v]format=gbrp[a];[1:v]format=gbrp[b];[2:v]format=gbrp,gblur=sigma=1.2[m];[a][b][m]maskedmerge,format=yuv420p" \
    -frames:v <n> wipe.mp4
  ```
  Swap the `geq` edge for a real brush-stroke matte (an alpha PNG sequence, or a key of the reference's own wipe
  frames) when the shape must match. Direction, length and edge color come from the breakdown in exact
  mode or the authored transition in remix; the sample's 5-frame duration is not a creative default.

### 6.6 TEXT (global `text[]` events, absolute `t0`/`t1`)

**Plan before generation, overlay after visual assembly.** Remix may author a new message, hierarchy,
font treatment, placement and timing within user locks. Record those decisions in the creative plan,
keep supplied lyric wording, and render the final words deterministically; the footage model does not
own text accuracy. For exact mode or explicitly retained source typography, apply the matching rules below.

For unchanged locked words, preserve source text pixels or use faithfully traced vector contours; do not
make execution depend on identifying or obtaining the original font. Preserve the measured glyph
geometry, position, spacing, layering and animation. For explicitly changed words, inspect installed
and bundled fonts, choose the closest visible match, then tune weight, slant, size, tracking, line
height, stroke and shadow. Use supported text properties or measured per-glyph positioning; do not
invent renderer parameters. Retrieve a public font only when necessary and authorized capability
exists. Never ask for a font file, name, link, license or picker selection. If the exact face cannot
be identified or loaded, continue with the best available match and disclose any visible deviation;
missing fonts never create a user-input gate. Do not blindly fall back to Arial, Inter or a browser default: verify that the chosen face actually loaded, compare glyph shapes and bounds, and tune the closest visual match. Explicitly set text type, family, weight, style, stroke, shadow and animation from source measurements; the engine defaults are not reference typography.

**Lyrics and song captions are a final assembly step.** Preserve available supplied lyric wording, source text explicitly retained by the task, or checked words transcribed from supplied audio when used in the result. Save a timed local cue file; do not send full lyrics to video generation or depend on a model drawing exact words. Finish visual shots, apply the required words deterministically and mux the actual song. Exact mode keeps measured typography, cue timing and occlusion; remix aligns retained lyrics to the selected recording segment and can author typography/timing within locks. “At the end” means this production step, not an appended end card or accidental duration change. Add lyric captions only when called for by the task or authored remix plan. Do not retrieve full protected lyrics from an external song page to fill missing text; continue independent work and record unresolved words without inventing them. A model's inability to render lyrics is not a reason to omit the final text pass or block the edit.

For a new final text pass, the canvas engine supports timed `text[]` entries with explicit `type: "font"`, `t0`/`t1` or `f0`/exclusive `f1`; `font` is not the engine's default text type. Use the completed visual as the plate at its finished geometry/cadence and disable unrelated effects. Set the loaded font and chosen styling explicitly. Use verified subject masks for behind-subject text, or preserve source text pixels for a closer exact match. The engine does not transcribe or align lyrics automatically: derive and verify cue times against the selected supplied recording segment and mode-aware timeline, then render the words into the actual final artifact.

`graffiti` (Katana chisel-marker caps, glyphs A-Z 0-9 `! ? . , : - ' / + * # &`, lower case drawn as caps):
`word` | `lines` [..] (multi-line) | `text`, `t0`, `t1`, `mode` write\|slam\|hold, `region` (name or [x0,y0,x1,y1]
0..1; names: left right top bottom center full leftwide rightwide tl tr bl br tl2 lower title), `cap` 300 px,
`seed`, `under` true (last line; bool per line allowed), `nib` .14, `halo` .02, `halo_color` #fff, `ink`,
`echo` $accent (offset colour pass), `wkeys` [t per letter] (per-stroke write-on locked to beats) or `wdur`,
`sc` [1.3, .9, 1.06, 1] (slam scale per frame), `line_dx`, `line_rot`, `line_scale`, `leading` .25, `rot` -.05,
`slant` .1, `bounce` .11, `longbar`, `on_specials`. Write-on emits `marker` SFX per stroke, slam emits `slam`.
The engine shrinks scale-ins around faces and a 3% safe margin. Do not use that behavior when it
changes locked geometry or authored placement: use preserved text pixels or an existing exact-position
font/layer route. Exact mode matches source overlaps, edge distance and flash-frame halo; remix verifies its chosen layout.

`font` (also `word`, `caption`): `text`, `t0`, `t1`, `pos` [x,y] 0..1 or `anchor: "face"` + `o` [dx,dy] eye
units + `size_eu` (clamped by `min`/`max`), `size` 96 px, `font` (CSS with `{S}` for the size) or
`family`/`weight`/`style`/`kind` (bold\|thin\|heavy -> font stacks), `fill` #fff, `stroke` $lav (null = none),
`lw` 5, `shadow` glow\|dark\|{color, blur, dx, dy}\|false, `align`, `rot`, `anim` none\|pop\|slam\|fade\|grow\|type,
`anim_d`, `pop` .18, `sc`, `dt`, `base`, `parts`, `fade_out` s, `boil` px, `alpha`, `sfx` (cue kind at t0).

### 6.7 STICKERS (global `stickers[]` events + `assets`)

Event: `t0`, `t1`, `kind` graphic\|cutout, `n` 1, `mode` burst (one every `step`, default 1/16 note) \| hold,
`ids` [1-based sticker indices], `size` [min, max] px (default 340 first / 210+ rest, cut-outs 340-460, scaled by
W/1440), `hero` (first >= 380 px), `slots` [[x,y]..] 0..1 (default 8 edge slots), `avoid` [[x0,y0,x1,y1]..],
`max_area` .25 (live stickers' share of the frame), `occ_ok` .25 (allowed overlap with the subject), `rot` .3,
`shadow` true. The planner (Katana) runs once at boot and is identical in every shard: it avoids faces of the
shots the sticker lands on, text boxes and the subject's matte, never stacks stickers, ends a sticker early
when a later shot's face would be covered, and logs `placed k/n` per event (`comp/render.log`). Each sticker
pops in over 4 frames (1.4, .9, 1.05, 1), boils, casts a hard offset shadow and slides off face/text boxes.
These are engine defaults only. When they differ from locked source geometry or an authored remix
placement, use fixed layers with explicit positions/timings or preserved source pixels. Exact mode
must not move source stickers or add unrequested ones; remix may author separate graphic layers.
Every placement emits a `slap` SFX cue.

### 6.8 SPECIALS (whole-frame inserts)

| Type      | Params                                                                                                                                                                                                           | Default `allow` (global layers / final fx on top) |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `flash`   | `color` $accent, `splat` true, `bigsplat`                                                                                                                                                                        | text, border                                      |
| `white`   | `color` #fff, `splat` true                                                                                                                                                                                       | stickers, text, dust, border                      |
| `black`   | `color` #000, `sparkle` true                                                                                                                                                                                     | border                                            |
| `color`   | `color`                                                                                                                                                                                                          | text, stickers                                    |
| `collage` | `bg`, `panels` [{`clip`, `src`\|`srcf`, `speed`, `rect` [x,y,w,h] 0..1, `cam`}], `brackets` true, `lines` [[[x,y]..]], `doodles` n, `keep` [[x0,y0,x1,y1]] (doodle-free), `look`, `duo_head` s (duotone first s) | stickers, text, dust, border                      |

Use them as shots (`"special": {...}`) or in top-level `specials[]` (they then override whatever shot is
under them for `n` frames / `d` seconds). Override the allow list with `"allow": [...]`.

### 6.9 DOODLES (shape library)

- ink (Katana, boil with `S.b`): zig, scratch, splat, rays, arrow, spark, cross, hatch, star, xx, bolt, bang.
- kawaii (Yaong, outline + white fill, boil every 3 frames): heart, spark, star, bow, blush, heartO, ear, dots,
  note, note2, squig, swirl, arrow, whisk, dash3, cross. Default sizes (eye units) note 1.0, note2 .9,
  heart .62, heartO .7, bow .75, spark .55, star .62, dots .6, swirl .6, squig .7, arrow .75, cross .45, dash3 .7.

### 6.10 Reference effect names (`references/analysis.md` breakdown) -> engine

| breakdown type                                              | engine                                                                                                             |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| flash_white / flash_black / flash_color                     | `white` / `dip` / `flash` transitions, or `special` white/black/color/flash frames                                 |
| exposure_flash                                              | `fin` / `fout` (flashlight)                                                                                        |
| invert, threshold, duotone, bw, hue_shift                   | look `neg` / `threshold` / `duo`, `bw` layer, look `filter` `hue-rotate(..)`; whole frame incl. graphics: `invert` |
| blur_pulse, zoom_punch, shake, freeze, stutter, slow_motion | `blur`, cam `punch`, `shake`, `speed: 0` (+ `push`), `stutter`, `speed` < 1 (6.1.1)                                |
| glitch, mosaic, rgb_split, strobe, light_leak, ghost_blend  | `glitch`, `mosaic`/`magenta`, `rgbsplit`, `strobe`, `leak`, `trail`                                                |
| mirror, split_screen                                        | cam `mir`; `collage` special panels                                                                                |
| transition `ink_wipe`, `matte_wipe`                         | no built-in: an `fx.js` ink-stroke cover, or `maskedmerge` through a matte clip (6.5)                              |

## 7. Project hooks (`W/comp/fx.js`)

`fx.js` is loaded after `engine.js` and before boot finishes. Use it for observed source mechanisms or authored remix graphics that the catalogue lacks, except facial/identity changes: no hook may warp, paste, redraw or retouch a face/head. Exact mode reproduces observed separate graphics; remix may author new separate graphics with a documented scene role. Never fork `engine.js`. A throwing `fx.js` aborts the render with its error.

```js
(function () {
  const U = RRC.util;
  RRC.register("LAYERS", "crown", {
    // tables: LOOKS CAMERA LAYERS FACE TRANSITIONS TEXT SPECIALS LOOK_PRESETS DOODLES
    phase: "over",
    order: 22, // back | subject | over | post | final; or phases: {back: {order, draw}, over: {...}}
    cut: false, // true for back graphics that need the subject re-drawn on top
    draw(S, p, x) {
      // S = frame state, p = params from the EDL (true -> {}, number -> {v}), x = 2D context
      if (!S.fo) return; // canvas logical px; base transform already set; use U.px() for blur/shadow lengths
      const [cx, cy] = U.fp(S, 0, p.dy ?? -1.9); // eye units -> screen
      U.poly(
        x,
        [
          [cx - 40, cy],
          [cx, cy - 50],
          [cx + 40, cy],
        ],
        { w: 5, color: "$ink", b: S.b, seed: 71 },
      );
    },
  });
  RRC.register("LOOKS", "mylook", (S, src, p) =>
    U.applyLook(S, src, { type: "grade", filter: "sepia(1)" }),
  ); // (S, srcCanvas, params) -> canvas
  RRC.register("CAMERA", "sway", {
    apply(S, p, g) {
      g.th += Math.sin(S.t * 3) * (p.v ?? 0.02);
    },
  }); // used as cam.sway
  RRC.register("DOODLES", "paw", {
    family: "kawaii",
    size: 0.55,
    draw(c, s, r, k) {
      /* unit space, k.LAV k.WH k.lw(px) */
    },
  });
  RRC.register("SPECIALS", "card", {
    allow: ["text"],
    draw(S, p, x) {
      x.fillStyle = U.col(p.color);
      x.fillRect(0, 0, S.W, S.H);
    },
  });
  RRC.register("TEXT", "mytext", {
    init(T, i) {},
    draw(S, T, x, i) {},
    cues(T) {
      return [];
    },
  });
  RRC.hook("afterLook", (S, x) => {
    /* S.looked is the graded plate canvas */
  });
  RRC.hook("ready", ({ R }) => R.log("placed " + R.sevt.length + " stickers"));
})();
```

Hooks: `init` and `ready` (once, `{R, E}`), per frame `beforeFrame`, `afterPlate`, `afterLook`, `after_back`,
`after_subject`, `after_over`, `after_post`, `after_final`, `afterFrame` (`(S, ctx, RRC)`; may be async).

Frame state `S`: `f`, `t`, `b` (boil step), `k` (shot index), `shot`, `lt`, `dur`, `u` (0..1), `fx`, `kind`
(plate\|special\|empty), `clip`, `si` (source frame), `blend` (`{i0, i1, w}` on blended slow-mo frames, else null),
`speed` (playback speed at this frame), `M` (source px -> canvas affine `[a,b,c,d,e,f]`), `cam`
(`{ax, ay, tx, ty, k, th, mir}`), `fo` (`{x, y, D, a, mx, my, mw, w, box:[x0,y0,x1,y1], ok, e0, e1}`), `plate`,
`mask` (ImageBitmaps), `looked` (graded canvas), `occ`/`lum`/`motion` (16 px grids after `doodles` ran),
`special`, `W`, `H`.
`RRC.util`: hash hs rng clamp lerp ease easeOut noise1 col rgbOf withAlpha mk reset copyFull px setM mapM img
fetchJSON framePath maskPath fp foOr popIn poly zigzag crPts drawStrokes splat splatField sparkle rays arrow
scratch crossDoodle hatch kawaiiDoodle asterisk starburst slashes outlinedText typeWord fontStr drawFontText
gLayout gDraw fitGraffiti mosaic glitchBlocks blurFrame flashlight contours penContour occFromMask lumaGrid
applyLook drawCutout drawOutline padR hit unionR win av T srcPick drawPick camOf.
Rules: keep every random choice on `hash()`/`rng()` with frame-derived seeds (no `Math.random`, no `Date`);
draw in logical px; full-frame copies go through `U.copyFull`.

## 8. Examples (`$RR/comp/examples/`, rendered end to end by `tests/test_comp.sh`)

These are historical effect demonstrations, not a preset to import wholesale. Remove default overlays unless explicitly chosen in the mode-aware plan: observed source graphics in exact, purposeful separate graphics in remix. They never form a facial-correction route, and their dimensions, fonts, shot count or sound do not define the current output.

**mixed_media** (Katana port; 5 s, 1440x1080, 24 fps, 139.6 BPM grid). Plates `b0`, `f1a`, `c0` prepped at
`--width 1440` with `divide` mattes; faces = the Katana tracks (`{bb, lm}` format, read directly). Shows:
xerox + lime key on every cut, a `x_ramp` levels ramp, `neg` and `duo` cuts, pen contour, ink doodles,
cheek zigzags, the fx.js `crown` layer, KATANA write-on locked to 8th notes riding through a lime `flash`,
a `collage` card (its half-speed panel is frame-blended, 6.1.1), a 2-frame black gap from `specials[]`, the drop (punch + shake + 4-sticker burst), a 16th zoom
`ladder` with 2 die-cut cutouts, a `stutter`, a `white` splatter frame with a sticker burst, HERE! slam, `border`

- `dust`. The historical fixture mixed synthesized SFX into the source track; disable those cues and use the actual source soundtrack or matching recorded assets in current work.
  Setup: `comp/stickers/s01,s08,s15,s20.png`, `faces/<clip>.json`, `ref/ref.m4a`.

**kawaii** (Yaong port; 4 s, 1440x1080, 30 fps from 24 fps plates, 134.4 BPM). Native 1664x1248 plates
`A1`, `B1` with `divide --close 8` mattes; faces from `faces.py` (A1 fixture; B1 via `faces.py convert-chrome`).
Every shot is face-locked (`edl.cam` default + per-shot `ld/ly/z0/z1`). Shows: magenta mosaic entry, starburst

- arc letters, ears / whiskers / blush, explicit and auto `face_doodles` (incl. the fx.js `paw` doodle), HANA
  with a flashlight burn and blur pulse, giant DUL behind the outlined cut-out, SET with the fx.js `eye_sparkle`,
  mosaic dissolve in + flashlight out, white frames, slashes + SARANG/HAE typewriter, a B1 tail with a blur-out
  and the `tag`, `kawaii` grade, glow .14, grain .32, reference track stream-copied. Its shot 1 matches the
  accepted Yaong final at 25.8 dB PSNR (same sticker layout).

Run either one: copy `edl.json` + `fx.js` to `W/comp/`, prep the plates/mattes/faces it names, then
`render.py info`, `render.py render --no-sfx --stills cuts`, `render.py render --no-sfx`.

## 9. Grading and finishing with ffmpeg

Where: per-shot looks belong in the EDL; a global film grade is cheaper as one ffmpeg pass on `out/comp.mp4`
(or baked into plates with `prep --vf`). The following is an SDR/bt709 recipe only. Keep
`-frames:v` and `-c:a copy`; retain source-correct color handling instead of applying its bt709
settings to HDR or other source formats (§1):

```bash
ffmpeg -i out/comp.mp4 -vf "<chain>,format=yuv420p" -c:v libx264 -crf 18 -preset medium \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -c:a copy -movflags +faststart out/final.mp4
```

Building blocks (all in ffmpeg 5.1):

- `eq=contrast=1.18:brightness=-0.03:saturation=0.55` (basic), `hue=s=0` (mono), `colortemperature=temperature=5200`.
- `curves=r='0/0 0.15/0.10 0.5/0.55 0.8/0.86 1/0.93':g='...':b='...'` (per-channel tone), `curves=preset=increase_contrast`.
- `colorchannelmixer=rr=..:rg=..:rb=..:gr=..:gg=..:gb=..:br=..:bg=..:bb=..` (channel mix, tints, B&W mixes).
- `lut3d=file=grade.cube:interp=tetrahedral` (any .cube; make one in numpy: identity grid -> your transform ->
  write `LUT_3D_SIZE 33` + rows `r g b` with r varying fastest).
- `noise=alls=9:allf=t` (grain), `vignette=angle=PI/4.6`, `rgbashift=rh=2:bh=-2` (chroma fringe), `gblur=sigma=0.7` (softness).

Brazil draft grades: starting points only. Brazil was never accepted (only a v1 draft exists) and these
hand-written chains were later replaced by fitted 33^3 LUTs. Match by measured stats (below), not by these
numbers. `SEPIA_CORE` is shared:

```
SEPIA_CORE = colorchannelmixer=rr=0.85:rg=0.25:rb=0.05:gr=0.22:gg=0.72:gb=0.06:br=0.18:bg=0.42:bb=0.32,
             curves=r='0/0 0.15/0.10 0.5/0.55 0.8/0.86 1/0.93':g='0/0 0.15/0.07 0.5/0.44 0.8/0.76 1/0.88':b='0/0 0.15/0.05 0.5/0.31 0.8/0.62 1/0.80'
sepia    eq=contrast=1.18:brightness=-0.03:saturation=0.55,SEPIA_CORE      dark  eq=contrast=1.32:brightness=-0.10:saturation=0.6,SEPIA_CORE
sepia_hi eq=contrast=1.05:brightness=0.06:saturation=0.45,SEPIA_CORE       bleach eq=contrast=0.55:brightness=0.36:saturation=0.35,SEPIA_CORE
warm     eq=contrast=1.14:brightness=-0.02:saturation=0.82,colorchannelmixer=rr=0.95:rg=0.10:gr=0.06:gg=0.88:gb=0.04:br=0.04:bg=0.14:bb=0.76,
         curves=r='0/0 0.12/0.07 0.5/0.53 1/0.95':g='0/0 0.12/0.06 0.5/0.48 1/0.9':b='0/0 0.12/0.05 0.5/0.42 1/0.84'
natural  eq=contrast=1.12:brightness=-0.02:saturation=1.0,curves=r='0/0 0.1/0.06 0.5/0.52 1/0.95':g='0/0 0.1/0.06 0.5/0.5 1/0.92':b='0/0 0.1/0.06 0.5/0.47 1/0.88'
vivid    eq=contrast=1.18:brightness=-0.03:saturation=1.25,curves=r='0/0 0.1/0.05 0.5/0.52 1/0.95':g='0/0 0.1/0.05 0.5/0.5 1/0.92':b='0/0 0.1/0.06 0.5/0.48 1/0.9'
bw       hue=s=0,eq=contrast=1.28:brightness=-0.03,curves=r='0/0 1/0.95':g='0/0 1/0.93':b='0/0 1/0.89'
bw_cool  hue=s=0,eq=contrast=1.35:brightness=-0.04,curves=r='0/0 1/0.86':g='0/0 1/0.9':b='0/0 1/0.93'
orange|red|teal  hue=s=0,eq=contrast=1.25..1.4,colorchannelmixer=rr=1.0:gg=0.52:bb=0.18 | rr=1:gg=0.28:bb=0.24 | rr=0.30:gg=0.88:bb=0.85
```

Finish chain (Brazil draft, a starting point as well; the colourist's later version lowered the grain to
`alls=4` and the fringe to 1 px): halation + softness + vignette + grain + chroma, run on the assembled edit:

```
format=gbrp,split[a][b];[b]curves=all='0/0 0.62/0 1/1',gblur=sigma=22,colorchannelmixer=rr=1:gg=0.55:bb=0.25[h];
[a][h]blend=all_mode=screen:all_opacity=0.32,gblur=sigma=0.7,vignette=angle=PI/4.6,noise=alls=9:allf=t,rgbashift=rh=2:bh=-2
```

For exact mode or a color lock, measure per-cut color stats (mean/percentiles per channel, saturation)
on 100% crops, adjust `eq`/`curves`, then check side by side (`compare.py`); a clean locked source stays
clean. Remix may author a deliberate global or per-shot grade and texture, checking the whole image
against the chosen visual grammar and readability. Do not add grain/halation by recipe alone.

## 10. Real-footage montage: the slot-engine pattern (Brazil draft)

Brazil exists only as an unaccepted v1 draft; the reusable part is the pattern, not its looks. An edit is a
list of slots, each rendered to an exact frame count, concatenated with stream copy, then one global finish +
audio mux:

```python
slot = {"n": 18, "src": "plates/clip07.mp4", "ss": 12.4, "speed": 0.5, "z": 1.15, "cx": 0.5, "cy": 0.45,
        "dz": 0.002, "flip": False, "grade": "sepia", "fx": ["bleach:3", "chroma:6", "shake:12"],
        "ov": [{"a": "assets/leak.mp4", "mode": "screen", "op": 0.6}], "text": ["text/t07.png"],
        "mix": {"src": "...", "mode": "screen", "op": 0.5}, "matte": {"a": "...", "b": {...}}}
# per slot: ffmpeg -ss <coarse> -i src -vf "trim=start_frame=<exact>,setpts=(PTS-STARTPTS)/speed,fps=FPS,
#   scale(cover)+crop|zoompan,hflip?,<grade>,<fx>" [+ overlays via blend / overlay] -frames:v n -c:v prores_ks -profile:v 3 seg.mov
# slow-mo slot (0.3 <= speed < 1, 6.1.1): replace fps=FPS by framerate=fps=FPS:interp_start=0:interp_end=255, which
#   blends neighbouring frames by position (ffmpeg 8 check: the slot's first 1-2 frames repeat the in-point; the
#   filter exists in 5.1, unverified there); keep fps=FPS (nearest) below 0.3x and on fast limbs
# verify the frame count (ffprobe -count_frames); pad short segments with tpad=stop_mode=clone
# concat: ffmpeg -f concat -safe 0 -i list.txt -c copy concat.mov ; then the finish chain + audio -> libx264 crf 15..18
```

fx vocabulary that worked: `smear` (`dblur=angle:radius`), `bleach` (eq brightness ramp-in over k frames,
`eval=frame`), `fadeout`, `chroma` (`rgbashift`), `glitch` (`rgbashift` + `noise`), `poster` (`lutrgb` floor),
`shake` (`pad` + `crop` with sin/cos of `n`), `dark`/`bright`/`soft`/`noise`, `echo` (`tmix=frames=k`),
`scratch` (`drawbox` with `random`), and `ink_wipe` / `matte_wipe` between two slots via `maskedmerge` through a
matte clip (6.5; a wipe is not a `smear`). Cache segments by a hash of the slot dict so a revision re-renders only
changed slots (6 local render slots in parallel). Build exact/locked slots from the measured source cut
list; build remix slots from authored shot roles and the selected audio's measured beat/vocal structure.
Choose each effect for its transition or scene purpose, never as automatic decoration.
Frame exactness: `-ss` before `-i` only as a coarse seek, then `trim=start_frame=` (or decode by index with
`rrio`); never trust `-ss` alone for the in-point.
Celebrity edits may use a supported Genjutsu edit/reperformance route when it best preserves the
reference. Anime/stylized remakes do not require Genjutsu or a Styles preset: a supported image
generator can use the extracted source frame for composition/style and the user's character/photo
for identity, then composite or move the complete still, animate it with Seedance 2.5, or use a
supported Genjutsu motion route when retaining that source performance is useful. Keep source pose,
camera, palette, texture and scenery only where exact or explicitly locked; remix may author them
for its new shot roles. Do not accidentally copy the identity photo's background or alter facial/head
pixels in local code. Fresh video generation uses
Seedance 2.5 only, without switching to another video model. Respect actual service restrictions and existing task/account authority.
Never present generated or edited material as authentic archival evidence; no consent questions
or permission bypasses are introduced by this workflow.

## 11. Audio

- **Reference audio reused (exact, or remix when it fits):** stream copy, no loudnorm, no limiter when retaining the original stream. Remix may instead select another actual TikTok/stock/library recording or edit the musical arc within locks; record the selected segment and output audio interval. An MD5-equal copy is required only for an exact-audio claim:
  `render.py` maps `-map 0:v -map 1:a -c:v copy -c:a copy` and copies the whole track, untrimmed, when it starts
  at 0 and is at most 0.5 s longer than the picture (the reference's own audio tail may run past the last
  video frame); a longer track or `audio.start` > 0 is cut with `-ss`/`-t`. AAC or MP3 is copied; `--aac`
  re-encodes MP3 to AAC 256k. `comp/render_summary.json` reports `md5_equal` (the audio stream's packet MD5
  against the source's: `ffmpeg -i X -map 0:a:0 -c copy -f md5 -`). A mismatch is a fidelity difference even when codec,
  sample rate and loudness match. First remux the original stream; if impossible, report it as not 1:1. `assemble.py` also copies the
  reference track whole (`-c:a copy`, no trim); a hand-made final remux follows the same rule. Both renderers'
  copies came out MD5-equal to the reference in the sandbox (ffmpeg 5.1) on 2026-10-08: the Katana remake through
  `render.py`, the Altman swap through `assemble.py` (VERIFIED live).
- **Final song mux and recorded SFX mix:** use the user's supplied song, retained authorized audio or a verified suitable stock/library asset. Perform this after visual/text assembly; code may align, trim and mix recordings, but must not compose or synthesize music/SFX. `DUR` is the measured source interval for exact/locked audio or the authored output audio interval for remix, including any intended tail, never a shorter preview export. Skip trim/pad when stream-copying the original track:
  `[1:a]aresample=48000,atrim=0:DUR,asetpts=PTS-STARTPTS,apad=whole_dur=DUR[m];[2:a]volume=0.6[s];
  [m][s]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.79:attack=1:release=40:level=disabled`
  -> AAC 256k. `level=disabled` stops alimiter from re-normalising to 0 dBFS; `normalize=0` keeps amix gains.
- **AAC overshoot:** the AAC encoder adds 1-2 dB of true peak (Katana RC1 +0.5, RC2 +1.0 dBFS). `render.py`
  measures `ebur128=peak=true` on the encoded file and re-runs the mix with a lower limiter until the true peak
  is <= -1 dBTP (Katana final: limit 0.79 -> -1.2 dBTP, -8.8 LUFS). Report LUFS / dBTP in the delivery.
- **Hidden music edits / offsets** in the reference: find them with `audio.py align` (windowed NCC) before
  building the EDL. Exact output uses the reference's time base; remix uses its authored grid and records
  any reused source/audio mapping. A reference can hide a splice even when no second
  track is at hand: `analysis/breakdown.json` `audio.hidden_edits` lists confirmed and `suspected` ones
  (`references/analysis.md` §6.4). Reusing the reference audio keeps the splice and costs nothing. When the user
  explicitly swaps the track in exact mode, preserve picture timing unless retiming is also requested.
  Remix may recut unlocked picture timing to its selected audio; record those decisions rather than
  blindly re-snapping every cut. Honor locks and verify synchronization in either mode.
- **Recorded SFX only:** retain useful source effects, always preserving locked source audio. For a planned missing effect select an available stock/library recording, record its provenance, align it to the measured exact event or authored remix event, then mix it. No code-generated kicks, claps, hats, noise/sine bursts or whooshes. For unmodified source audio keep `audio.sfx: false` and pass `--no-sfx`. For a recorded SFX layer, first align actual recordings into a bed, then pass `--sfx-file PATH` or set `audio.sfx_src` to that verified file; `--sfx` alone is insufficient. `audio.beat` is rejected, and the legacy `render.py sfx` command does not create audio. Automatic visual cues must not become synthesized sound. If no suitable authorized asset is available, retain suitable existing audio and disclose the missing effect without questions.
- **Tail integrity:** verify the assembled song through the intended final video frame and audio tail. Do not use `-shortest`, an arbitrary fade, an early text-pass export end or a short SFX file to truncate the plan. Exact mode keeps source duration/cadence and lyric cues; remix follows `output_target` and its aligned cues while preserving supplied words. Inspect the last cue and audio packets after final mux.
  The helper automatically retains a source tail up to 0.5 s at source offset zero, including recorded-SFX mixing and required transcoding. Partial `--frames` renders trim to the selected interval. For a longer intentional source tail or another measured audio interval, use a final explicit remux/mix with that verified interval and stream-copy the completed video; do not add video frames or silently accept the helper's shorter default.
- **Chants / vocals:** preserve the reference track in exact mode and when retained in remix. TTS is only for an explicit voice/audio change
  with a verified available capability, existing task/account authority and hard-cap coverage; never substitute it for original singing.

## 12. Performance (measured 2026-10-08)

| Setup                                                              | mixed_media (xerox, 1440x1080)                                              | kawaii (filters/blur, 1440x1080) |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------- | -------------------------------- |
| Mac M-series, 1 Chrome, software raster (`--disable-gpu`)          | 25 fps in-page (39 ms/frame)                                                | 13 fps (75 ms/frame)             |
| same, `--gpu`                                                      | 28 fps                                                                      | 40 fps                           |
| same, 4 Chrome                                                     | 36 fps wall incl. start-up                                                  | 27 fps                           |
| Chrome start + page boot                                           | ~1.5-3 s per instance (boot alone 0.03-0.35 s: stickers, cut-outs, planner) |                                  |
| encode 120 frames x264 crf 18 medium                               | 1.1-3.7 s                                                                   |                                  |
| prep 361 frames 1664x1248 HEVC 10-bit -> 1440 JPEG + 720 PNG matte | ~4 s per clip (Mac, 14 cores)                                               |                                  |
| `--preview` (half res)                                             | ~2x faster per frame                                                        |                                  |

**Sandbox (8 vCPU, software raster, 4 Chrome by default), VERIFIED live 2026-10-08 on the Katana remake**
(xerox look, 1440x1080, 24 fps):

| Step                                                                           | Time                                                                                      |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `render.py render`, 252 frames                                                 | 26 s in total: render 8.9 s (28 fps across the shards) + encode 12.8 s + start-up and mux |
| `render.py render --stills`, 16 frames + QA sheet                              | ~6 s                                                                                      |
| `render.py prep` of a 241-frame 1112x834 plate + its `remove_background` matte | ~9 s                                                                                      |

Blur-heavy looks (kawaii) render about half as fast as xerox on the Mac, so expect the same on the sandbox.
Plan: a foreground call must stay under ~45 s (`references/sandbox.md` section 1), so up to ~250 frames of a
xerox-type edit fit one foreground call; longer edits, blur-heavy looks or prep plus render in one command ->
`background: true` + `rr_bg`. Short edits are dominated by Chrome start-up, so more instances do not help below
~40 frames each.

## 13. Gotchas

- Set `canvas.frames` from remix `output_target` or the exact source grid; the encode is `-frames:v` exact and verified against that selected target.
- Plates for face-lock must stay at native size (zoom headroom); plates for cover-fit cams at canvas width.
- Faces files: `faces.py` writes clip pixels + `.meta.json` (size). Pixel files without a size are assumed to be
  in plate pixels; if their boxes overflow the plate and prep recorded a larger source size, source pixels are
  assumed (with a warning). Set `clips.<id>.faces_size` to remove all doubt. Chrome FaceDetector does not
  exist on Linux; use `faces.py` (YuNet).
- Cheek/fang overlays skip uncertain tracks. Do not force a guessed face position to paint features; only separate source-matched or deliberately authored graphics may use measured tracking coordinates.
- Mattes: `remove_background` returns the subject on black with no alpha, hence `divide`; dark clothing on a
  dark background breaks it -> `sam_3_video` binary mask + `--mask-mode luma`. The lavfi colour source rate
  (`r=`) must equal the clip fps and `alphamerge=shortest=1`, or frames drift / never end.
- Fonts: availability and real weights depend on the current environment; inspect the installed files and rendered glyphs instead of assuming a family or weight exists. A historical sandbox had Montserrat/Metropolis only as ExtraBold, so requesting a different weight silently kept ExtraBold. A historical test-edit workflow included League Gothic, UnifrakturMaguntia, Cormorant and Inter at
  `$HF_WORKFLOWS/test-edit/scripts/fonts/`, served by `render.py` as `/_hf/test-edit/scripts/fonts/<file>`
  (historical inventory only; inspect actual files and loaded weights first). Choose by measured source resemblance in exact mode or the authored message/visual grammar in remix, not this list or a default family.
  Only when needed and authorized, load another public face through `fonts[]` from Google Fonts,
  either a font file (`curl -fL -o $W/comp/fonts/Anton-Regular.ttf
  https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf`, then
  `{"family": "Anton", "url": "comp/fonts/Anton-Regular.ttf"}`; robust, saved with the state, loaded locally by
  every shard) or a css2 stylesheet (`{"family": "Anton", "css": "https://fonts.googleapis.com/css2?family=Anton"}`;
  needs the network in every Chrome shard). The engine only warns on font-load failure; its
  browser fallback does not select the closest face or tune geometry. The agent must inspect
  installed fonts, select a fallback, update EDL family/weight and geometry, rerender and compare
  stills. Continue without requesting font inputs; record visible differences and never claim
  exact identification without evidence.
- Canvas `ctx.filter` blur radii and shadow blur/offset ignore the transform: multiply by `U.px()`.
- Hard xerox thresholds destroy backlit, specular and worm's-eye frames (Katana QA#24-26): use `xl`, `levels`
  or a ramp on those cuts, and do not pay for 1080p detail a threshold throws away. They also crush faces on
  identity-legible medium close-ups to near-black (VERIFIED live 2026-10-08): check those stills against the
  reference and soften the levels per shot (6.2, "Faces under xerox").
- `post.border` (the inked frame edge) trips the `bars` check of `compare.py check`; declare it as intentional
  (`references/qa-delivery.md` §1.2) instead of removing a border the reference has.
- Wind-blown hair across the lips gets keyed to the accent ("lime lips"); narrow the key (`lo`/`vmin` or hue
  window) or switch the key off on that cut.
- The sticker planner may place fewer than requested (all slots blocked by faces/text/subject); read the
  `placed k/n` lines and loosen `slots`, `size` or `avoid`.
- A shot whose source runs past the clip end holds the last frame and warns; use `loop` or a later `src`.
- Slow motion duplicates frames only where you ask for it (`blend: false`, < 0.3x); a slowed shot that judders in
  QA #12 lacks the blend. Slowed Genjutsu faces and fast limbs ghost when blended: `blend: false` on those shots.
- An aspect-mismatched take requires intentional geometry (§6.1.2), not automatic cover-fit or a
  fixed crop center: preserve locked source content in exact, and verify authored framing in remix.
- Top-level `specials[]` override shots for their frames; shots with `special` replace the plate entirely.
- JPEG dumps are BT.601 full range; `render.py` converts to BT.709 tv explicitly. Re-encoding the frames by
  hand without `in_color_matrix=bt601:out_color_matrix=bt709` shifts hues by 2-4 levels.
- `comp/frames/` (render, `preview/`, `stills/`) is excluded from `rr_save`; `--stills` and partial renders reuse
  the same engine, so a still is pixel-identical to the same frame in the full render.
- Never open a browser for the user; `serve` prints a URL only.

## 14. Renderer A — frame-exact rebuild (assemble.py + textlayers.py)

**Scope: exact mode or an intentionally source-locked segment.** This renderer's source timeline,
frame-count, audio-copy and text-recall gates are technical invariants of this route, not default
creative constraints on remix. New remix scenes, shot order, duration or wording use the canvas/slot
renderer and its authored output target. Never rewrite source analysis to make new shots appear observed.

For a hero swapped inside the reference's own footage: Genjutsu SWAP and REPERFORM cuts, window-in-canvas reels
such as Altman. `assemble.py` decodes the reference once. Every timeline frame is either passed through
untouched (KEEP cuts, and everything outside the footage window) or gets its generated frame mapped, fitted,
graded and composited into the window. The result goes straight into one libx264 pipe, with no intermediate
PNGs and no ffmpeg overlay graph. The output has exactly the reference's decoded frame count, and the
reference audio is stream-copied whole (`-c:a copy`, section 11). `textlayers.py` then rebuilds on-screen text
from the reference's own pixels (never retyped) and lays it back at timeline fps. Both cost 0 credits.
`python3 $RR/assemble.py --help` and `python3 $RR/textlayers.py <cmd> --help` are authoritative; this section
is the working summary.

### 14.1 Order of work

```bash
# every step runs after `<BOOT> && rr_restore <slug> '<STATE_URL>'` (or rr_ws <slug>), as in section 3
# 0. Before ANY paid job: alignment gate on the original pixels (exit 3 = fix plan/edl.json first)
python3 $RR/assemble.py $W --control
# 1. Driving clips exported and padded (references/generation.md G9/G10); plan/renders.json lists them
#    with pad_video. Proves that each clip maps back onto the reference before you pay for it:
python3 $RR/assemble.py $W --control --dry
# 2. Text layers from the reference (free; do it between jobs_wait polls)
python3 $RR/textlayers.py layers $W                  # plan/text_specs.json -> text/<cut>/, qa/text_<cut>.jpg
# 3. Results in gen/, renders.json entries get "path" (+ "matte"); quick look at a few cuts (no audio)
python3 $RR/assemble.py $W --only c03,c07            # look at qa/fit_c03.jpg, qa/fit_c07.jpg
# 4. Full rebuild + text check (background: true; see 14.6)
rr_bg logs/asm.log "python3 $RR/assemble.py $W && python3 $RR/textlayers.py check $W"
# 5. plan/text_pass.json for the cuts textcheck.json lists under "fix" (+ logo), then the pass
python3 $RR/textlayers.py pass $W                    # out/base.mp4 -> out/text.mp4
python3 $RR/textlayers.py check $W --video out/text.mp4   # the cuts listed before should now pass
cp out/text.mp4 out/<slug>_vN.mp4                    # (out/base.mp4 when no pass is needed) -> references/qa-delivery.md §1
```

Text the model kept needs nothing: run `check` on every swapped cut and re-lay only the words that fail. Do
not strip and re-composite text pre-emptively (`references/routing.md` §2.6). `check` compares against the
layers `layers` built, so give `plan/text_specs.json` an entry for every swapped cut that carries text; cuts
without text need no entry.

### 14.2 Timeline, window and mask (shared by assemble.py, textlayers.py and frames.py)

- **Timeline:** `--edl FILE`, else `plan/edl.json`, else `analysis/analysis.json` (the first one with `cuts`).
  Cuts are inclusive `f0`/`f1` on the reference's frames (`start`/`end` exclusive is also accepted). A gap
  passes through with a warning; an overlap is an error (exit 2). `fps` is an exact fraction (`"60/1"`,
  `"30000/1001"`), never rounded. Per-cut `src_fps` or `cadence` gives the source cadence.
- **Window** (the footage rect generated frames go into). The first rule that applies wins:
  1. the timeline's `"window": false` means the full frame. `window` (`{x,y,w,h,radius}` or `[x,y,w,h]`) or
     `letterbox` (`{top,bottom,left,right}`) gives that rect; a rect equal to the frame is the full frame;
  2. an explicit `plan/edl.json` or `analysis/breakdown.json` window/format-lock window takes precedence over detector metadata;
  3. otherwise use the actual detected `canvas.window` / `canvas.letterbox` (or source crop metadata), then the full frame;
  4. `canvas.crop_used` describes analysis inspection only. The mandatory `--no-window` baseline never erases an actual source window or overrides the render plan. Keep all three helpers' selected window identical before export/assembly.
- **Plan window vs analysis window.** A plan window that differs from `analysis/analysis.json`'s picture area
  prints a warning with the rect. `frames.py export --crop window` follows the explicit plan/breakdown window. For a custom `assemble.py --edl` outside the shared plan paths, pass that exact measured rect to frame export with `--crop x,y,w,h`; verify the exported and assembled windows agree.
- **Mask** (the anti-aliased window edge). Candidates, in order: `--mask`, the timeline's `"window_mask"`,
  `plan/window_mask.png`, `analysis/window_mask.png`. A PNG (canvas size or window size, white = footage) is
  used **only when its lit-area bbox matches the window rect within 1 px**. A stale PNG from another window is
  skipped with a warning; this is expected after `--no-window` or a widened plan window. A mismatching
  `--mask` exits 2. Otherwise: no window means no mask; else a rounded rect with `window.radius`, or with the
  radius measured from the reference's ever-lit area (cached in `plan/window_mask.json`).
- **Edge leak.** `--control` measures how far the reference footage reaches past the window rect
  (`window_edge_leak_px` in the report). More than 1 px on a side means generated cuts would keep a strip of
  old footage there under `--canvas ref`. Widen the window in `plan/edl.json` to the lit area (and export
  with the matching `--crop`), or render with `--canvas black`.
- **Canvas.** `--canvas ref` (default) keeps every pixel outside the window from the reference, so KEEP cuts
  are bit-exact pass-through. `--canvas black` pads on black and multiplies by the mask.

### 14.3 `plan/renders.json`

`{cut_id: entry}`. Cuts not listed keep the reference pixels. Keys starting with `_` are ignored (use them for
notes). An unknown cut id exits 2.

```json
{
  "c03": { "path": "gen/c03.mp4", "pad_json": "gen/c03_pad.json", "pad_video": "gen/c03_pad.mp4" },
  "c07": {
    "path": "gen/c07.mp4",
    "pad_json": "gen/c07_pad.json",
    "pad_video": "gen/c07_pad.mp4",
    "matte": "mattes/c07_rb.mp4",
    "matte_mode": "black",
    "grade_match": 0.5
  },
  "c09": {
    "path": "gen/mt_full.mp4",
    "gen_range": [128, 150],
    "crop": [88, 0, 1487, 1248],
    "grade_match": 0.5,
    "blur": [[0, 700, 120, 836]],
    "blur_sigma": 12,
    "fit": { "tilt": 30, "zoom": 1.1, "ease": true }
  }
}
```

| Key                                     | Meaning                                                                                                                                                                                                                                                                                                                                                      |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`                                  | the generated clip (Genjutsu output, plate) or a still (png/jpg, held for the whole cut). Required, except under `--control --dry`                                                                                                                                                                                                                           |
| `pad_json`                              | the `frames.py pad` JSON (`orig_frames`, `padded_frames`, `keep_padded_index`, `fps`, `src`): the per-cut SWAP case                                                                                                                                                                                                                                          |
| `cut_json`                              | the `frames.py export` JSON with `src_index`; default `<pad src without .mp4>.json`, i.e. `cuts/<cut>.json`                                                                                                                                                                                                                                                  |
| `pad_video`                             | the padded INPUT clip, used as the stand-in render by `--control --dry`                                                                                                                                                                                                                                                                                      |
| `src_fps`                               | override the cut's source cadence                                                                                                                                                                                                                                                                                                                            |
| `gen_start` + `gen_fps`, or `gen_range` | without `pad_json` (a full MT take or a plate covering several cuts): `g = gen_start + round(rel × gen_fps / fps)`, or stretch the cut over these generated frames (inclusive)                                                                                                                                                                               |
| `crop`                                  | generated-pixel region `[x, y, w, h]` mapped onto the window. Default: the whole render, stretched                                                                                                                                                                                                                                                           |
| `fit`                                   | `{"scale", "offset"}` (= crop `[ox, oy, W/scale, H/scale]`), or auto `{"person_box": [x0,y0,x1,y1] of the hero in WINDOW px of the reference, "gen_box": the generated person in render px (else the matte bbox)}`. Plus `tilt` / `pan` (crop drift in render px over the cut; tilt > 0 = up), `zoom` (a digital push-in re-done at timeline fps) and `ease` |
| `grade_match`                           | pull each channel's mean/std this far (0-1) towards the reference cut; 0.5 is typical                                                                                                                                                                                                                                                                        |
| `blur`, `blur_sigma`                    | window-px boxes to blur (stray generated text), sigma default 12                                                                                                                                                                                                                                                                                             |
| `matte`, `matte_mode`                   | `remove_background` of THIS render: `black` (default, person on black), `mask` (white-on-black video) or a PNG dir. A final run also writes `mattes/fit/<cut>.mkv` (one frame per timeline frame, window size) for text layers behind the person                                                                                                             |

- The fit precedence is `crop`, then `fit.scale`/`offset`, then `fit.person_box`, then the whole frame.
  A crop whose aspect is more than 2% off the window's is stretched (warning). A crop larger than the render is
  shrunk (warning): a fit cannot zoom out past the render.
- **Frame mapping**, per timeline frame `rel` of a cut (integer maths on fractions, half-up rounding):
  - `k` = the source index. When the export's `src_index` is known, `k` is the exported frame that best matches
    reference frame `f0 + rel` among its time neighbours, which is exact for pulldown. Otherwise
    `k = round(rel × src_fps / fps)`.
  - `g = round(keep_padded_index[k] × gen_frames / padded_frames)`: the proven Altman mapping. A render whose
    frame count differs from `padded_frames` is rescaled, and the mapping note says so. VERIFIED live
    2026-10-08: replace at 720p on a 96-frame pad returned 89 frames (3.71 s, 1054x880, 24 fps); the rescale
    mapped it, `--control` passed on all 21 cuts, and the final had 862 frames with the baked text, the
    watermark and an MD5-equal audio stream.
  - A mapping that runs past the end of the render holds its last frame and warns (`CLAMPED`).
- The control's `hint: a plain fps-filter export of [...]` line concerns hand-made exports (an `ffmpeg
  fps=24` filter). `frames.py export $W --cut <id> --fps 24` (default `--phase auto`) already keeps one frame
  per distinct source image and writes `src_index`, which `assemble.py` matches. Do not hand-build
  `src_timeline_frames` lists.

### 14.4 The gate

PSNR is measured inside the window, on 160 px wide grey frames of the ENCODED output against the reference, at
offsets −1 / 0 / +1.

| Run               | What is rebuilt                                                                                                                                                                         | Gate                                                                                                                                                                       | Exit                         |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| `--control`       | every cut from the original pixels (renders ignored) → `out/control.mp4`                                                                                                                | every cut best at offset +0 and ≥ 35 dB (`--gate-db`)                                                                                                                      | 3 on fail                    |
| `--control --dry` | renders.json cuts through the generated path, with `pad_video` as the render (crop, fit, grade, blur and matte off); other cuts original → `out/control.mp4` (use `--out` to keep both) | **normal cuts:** best +0 and ≥ 35 dB. **Fast-content cuts** get their own floor: best +0 and ≥ max(25, min(35, export match − 2 dB)) (`--gate-fast-db` 25, `--gate-db` 35) | 3 on fail                    |
| final (no flag)   | renders.json as listed → `out/base.mp4`                                                                                                                                                 | kept (reference) cuts only: best +0 and ≥ 35 dB. Generated cuts print their PSNR as "new content", for information                                                         | 0; read `gate` in the report |

**Fast-content cuts (`--dry`).** A cut whose content shows more distinct images per second than the 24 fps
driving clip can carry (`runs_dropped` > 0 in `cuts/<cut>.json`, or a native / mixed cadence in the analysis with
unique ÷ of × fps above the export fps) loses source images in ANY 24p export, so it cannot reach 35 dB. Altman
c02/c05/c08/c12/c15/c16 sat at 27.6–34.8 dB. Such a cut passes when it is best at +0 and at or above
max(25, min(35, export match − 2 dB)), where "export match" is the PSNR of the exported images content-matched back
onto the reference (the best this export can do; the six Altman cuts measure within 0.2 dB of it). The run prints
`fast-content cut: 24p export drops N images (expected)` with the floor. A flat 25 dB would not do: Altman c05
driven one exported image late is 25.8 dB and still best at +0. These cuts are recorded as fidelity risks before a paid call
(`references/analysis.md` §3.8), because the generated result steps at 24 fps where the reference is smooth.

- **`--control` fails:** the timeline is wrong (cut bounds, fps, window), not the footage. Fix `plan/edl.json`
  before anything is paid.
- **`--dry` fails on a normal cut:** that driving clip does not map back: a wrong crop, a native-fps pad or a
  hand-made export. Best at ±1 means one frame off. Re-export with `frames.py export $W --cut <id> --fps 24
  --crop window`, re-pad and re-run. Never submit a clip that fails here.
- **A kept cut fails in a final run:** it was swapped or shifted, i.e. a route mismatch
  (`references/qa-delivery.md` #15).
- `--control` also writes `qa/cadence.json`: per cut an ESTIMATE of the cadence pattern and source fps. Confirm
  it on a sheet before relying on it.

**Report** (`out/base_report.json`, `out/control_report.json`, or `--report`), schema `rr.assemble/1`:
`mode` (`control` / `control-dry` / `final`), `frames_out` vs `frames_ref`, `window`, `window_from`, `mask`,
`audio`, `gate {db, pass, failed, scope}`, `window_edge_leak_px` (control), `secs_*`, and per cut: `source`
(`ref` / `gen`), `psnr {-1, 0, +1}`, `best_offset`, `unique_ref` / `unique_out` (far fewer unique frames than
the reference = held frames, judder), `ok`, `mapping`, `gen_index`, `render_frames`, `fit`, `crop`,
`warnings`, `sheet` and `matte_fit`. `qa/fit_<cut>.jpg` shows reference | ours with the matte outline at the
first, middle and last frame of each generated cut; look at it before the full render.

Exit codes: 0 ok, 1 runtime or ffmpeg error, 2 bad input (missing render, bad mask, unknown cut), 3 control
gate failed.

### 14.5 `textlayers.py`

Coordinates are WINDOW pixels (frame pixels when there is no window). `full`, the layers and the curves use
absolute timeline frames of `ref/ref.mp4`; frame numbers inside `text_pass.json` are relative to the cut. The
timeline and window are read exactly as in 14.2.

| Command                                                                            | Does                                                                                                                                                                           | Writes                                                                                                                                                                                                                        |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `layers $W [--specs plan/text_specs.json] [--cuts c01,c09]`                        | per layer, a static alpha keyed from the reference over its fully-on frames (grain and footage average out), plus an opacity curve per timeline frame                          | `text/<cut>/<name>.png`, `curves.json`, `layers.json`, `preview.png` (all layers white on grey: look for holes the old actor punched); `qa/text_<cut>.jpg` (ref crop / layer / diff)                                          |
| `check $W [--video out/base.mp4] [--cuts …]`                                       | per layer, recall (the reference's letter core is present) and spurious (extra white around it) over the fully-on frames; `behind` layers ignore pixels under the fitted matte | `text/textcheck.json` (`rr.textcheck/1`: per cut `fix` and per layer `recall`, `spurious`, `bad`, `hidden`; top-level `fix` = the cuts to fix). **FIX** when recall < 0.85 or spurious > 0.15. Exits 0 either way: read `fix` |
| `pass $W [--base out/base.mp4] [--specs plan/text_pass.json] [--out out/text.mp4]` | lays the layers (and logo) onto the base at timeline fps; frames outside the listed cuts pass through                                                                          | `out/text.mp4`, audio stream-copied from the base                                                                                                                                                                             |
| `logo $W --box x,y,w,h [--frames a-b]`                                             | keys a clean white watermark from the frames where the box surroundings are darkest (box a little larger than the logo)                                                        | `text/logo.png` (RGBA), `qa/logo.jpg`; sets `"logo"` in `plan/text_pass.json` unless `--no-update`                                                                                                                            |

**`plan/text_specs.json`** (for `layers` and `check`):

```json
{
  "c06": {
    "layers": [
      {
        "name": "big",
        "box": [75, 135, 932, 472],
        "full": [218, 222],
        "shape_lo": 236,
        "key": "white",
        "sat_lo": 30,
        "sat_hi": 70,
        "close": 3,
        "soft": 0.8,
        "fade": "auto",
        "stat": "mean",
        "repair": [{ "op": "mirror_x", "src": [535, 284, 580, 326], "axis": 541 }]
      }
    ]
  }
}
```

| Key                | Meaning                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| `name`, `box`      | layer name; `[x0, y0, x1, y1]` window px, a little larger than the letters                                    |
| `full`             | `[fa, fb]` absolute frames where the text is fully on, ideally not covered by the actor                       |
| `shape_lo`         | min-channel threshold of the letter shape, 190–238 (lower for thin or soft letters)                           |
| `key`              | `white`, or `black` for dark letters                                                                          |
| `sat_lo`, `sat_hi` | saturation gate: fully kept below `sat_lo`, dropped above `sat_hi`                                            |
| `close`, `soft`    | morphological close (px) and edge blur (sigma)                                                                |
| `fade`             | `in`, `inout`, `raw` or `auto` (`inout` when the text fades out)                                              |
| `stat`             | `mean`, `median` or `max` over the fully-on frames; `max` recovers letters the actor hides on SOME frames     |
| `repair`           | ops `copy`, `mirror_x`, `mirror_y`, `extend`, `fill`, `erase`, `close`, `open` on holes the old actor punched |

The opacity curve is (letter core − surrounding ring) / its fully-on value, forced monotonic.

**`plan/text_pass.json`** (for `pass`, and for `check`'s `behind` layers and mattes):

```json
{
  "logo": { "png": "text/logo.png", "x": 455, "y": 725 },
  "cuts": {
    "c09": {
      "layers": [
        {
          "name": "main",
          "behind": true,
          "glow": [8, 0.15],
          "backing": [18, 0.3],
          "color": [255, 255, 255],
          "shift": 0,
          "gain": 1.0
        },
        { "name": "top" }
      ],
      "matte": true,
      "cleanplate": { "box": [608, 250, 912, 596], "from": 6, "until": null },
      "inpaint": { "boxes": [[612, 258, 908, 590]], "lo": 215, "sat": 40, "frames": [0, 5] },
      "logo": true
    }
  }
}
```

| Key                      | Meaning                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `layers[].name`          | a layer built by `layers` (`text/<cut>/<name>.png` + its curve)                                                                                                                                                                                                                                                                                                      |
| `behind`                 | the letters go behind the person (alpha × (1 − matte))                                                                                                                                                                                                                                                                                                               |
| `glow`, `backing`        | `[radius, strength]`: screen of a blurred alpha; a dark halo under the letters for bright plates                                                                                                                                                                                                                                                                     |
| `color`, `shift`, `gain` | letter colour; curve delay in frames (positive = later); opacity multiplier                                                                                                                                                                                                                                                                                          |
| `matte`, `matte_clip_y`  | `true` = `mattes/fit/<cut>.mkv`, or a verified cut-aligned person mask covering the full frame/window. A behind-text layer requires the real matte. Cleanup requires the full exclusion mask of every visible person, including extras and head/hair silhouettes; `matte_clip_y` is prohibited with cleanplate/inpaint and may never isolate a head for replacement. |
| `cleanplate`             | background-only text cleanup from relative frame `from` through `until`; requires a full, cut-aligned exclusion matte covering every visible person, including extras and head/hair silhouettes for both held and current frames, so it cannot paste an old face/head/person into the result                                                                         |
| `inpaint`                | background-only removal of stray lettering in `[a,b]`; requires a full, cut-aligned exclusion matte covering every visible person, including extras and head/hair silhouettes, re-applied after dilation so cleanup cannot bleed into the face, head or body                                                                                                         |
| `hairfix`                | disabled: runtime refusal, not a hair/face repair tool. Use a supported authorized model for affected head/identity pixels; no local recoloring fallback                                                                                                                                                                                                             |
| `logo`                   | `true` draws the top-level `logo` on this cut                                                                                                                                                                                                                                                                                                                        |

Order per frame: background-only cleanplate/inpaint, source text layers, then logo. Layer alpha is multiplied by the window mask. Cleanup and behind-text operations require a verified aligned matte; missing protection fails explicitly. For an empty scene, use a verified all-zero subject mask. Never let these cleanup boxes or painted text repairs act as a face/head/feature patch. `repair` operations act on extracted letter alpha only, never facial anatomy.

### 14.6 Timings, memory and running in the sandbox

| Step (Altman: 862 frames, 1080x1920 @60, 21 cuts, 6 generated) | Local (Mac)             |
| -------------------------------------------------------------- | ----------------------- |
| `assemble.py --control` (encode + PSNR + cadence)              | 5–7 s                   |
| `assemble.py --control --dry`                                  | ~11 s                   |
| `assemble.py` final                                            | 10–12 s                 |
| `assemble.py --only` on one 96-frame cut                       | ~3.5 s                  |
| `textlayers.py layers`                                         | ~1 s per cut (3 layers) |
| `textlayers.py pass` (2 cuts)                                  | ~4–5 s                  |

- Expect 2–4× these times on the 8-vCPU sandbox. Run full `assemble.py` and `textlayers.py pass` /
  `check` chains with `background: true` and `rr_bg` (`references/sandbox.md` section 5), and end the
  command with `rr_save '<UPLOAD_URL_STATE>' '<STATE_CONTENT_TYPE>'`. `--only` reviews of one or two cuts
  fit a foreground call with `timeout_seconds: 120`.
- Memory is flat in cut length; everything streams. A producer thread decodes each render and its matte
  once, in order, and hands frames ahead through a byte-capped queue (`PREFETCH_BYTES` 192 MB).
  `textlayers.py layers` and `check` read only the layer boxes plus margins, and `pass` opens each matte only
  while the stream is inside its cut. Measured on 900 frames at 1080x1920 with a 750-frame matte cut:
  Python peaks below 1 GB (assemble ~0.9 GB, text pass ~0.55 GB, layers ~0.26 GB, check ~0.12 GB). The
  libx264 child adds ~0.8–0.9 GB at preset medium, so about 2 GB in total. That is fine on the ~7 GB shared
  sandbox; run one such job at a time.
- Outputs to keep: `out/base.mp4`, `out/text.mp4`, the reports, `text/`, `mattes/fit/` and `plan/`. `rr_save`
  carries them (Altman: ~11 MB per film at crf 14); files over `RR_SAVE_MAX_MB` (default 150) are left out
  (`references/sandbox.md` section 9).

A preset's exact-font or no-substitutes wording is not a user-input gate. Follow the user's autonomous-execution instruction: preserve source lettering or choose and tune the closest accessible face yourself. Do not request system-font archives, ask whether to use an analogue, or pause for a licensing discussion. Use supported sources; retrieval failure immediately selects an installed fallback. Missing font files alone never justify a blocked or partial video.

## Bundled Katana fonts

The existing Katana bundle includes League Gothic, UnifrakturMaguntia, Cormorant and Inter at `$HF_WORKFLOWS/katana/scripts/fonts/`, with font source and license records beside them. The compositor serves these assets as `/_hf/katana/scripts/fonts/<file>`. Select them only when their letterforms fit the task; otherwise use a suitable accessible face or preserved source lettering. Load the chosen font explicitly and inspect required glyphs without asking for font files.
