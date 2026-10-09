# QA gate, delivery and handoff

Run the gate on the actual encoded file before presenting it as the finished result. The
gate is free: it runs in the sandbox with ffprobe, ffmpeg and numpy, and you look at the sheets
yourself with `image_paths`. A render is never judged from exit codes.

Why the gate exists, from past projects:

| Project                  | What reached the user                                                              | What a gate would have caught                                                                                                                |
| ------------------------ | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Yaong v2                 | 285 frames                                                                         | The reference has 283 video frames; its container says 9.517 s because of the audio. The final also carried no bt709 transfer/primaries tags |
| Polarity triptych (Aura) | 233 frames against the film's 230                                                  | frame count                                                                                                                                  |
| Katana RC1/RC2           | the limiter left +0.4 / +1.0 dBFS peaks after AAC encoding                         | true peak on the encoded file                                                                                                                |
| Katana handoff           | listed 23 fixes as "confirmed"; at least 2 were not applied                        | never mark what was not re-checked                                                                                                           |
| Altman v2                | words misplaced, holed or faded on 5 cuts                                          | the pair sheets at text frames                                                                                                               |
| Altman v3                | 60p-native motion came back 24p-stepped (c12: 36 → 14 unique frames, c08: 32 → 13) | cadence per cut                                                                                                                              |
| Signal v5 (Aura)         | grey matte holes between the legs on a white backdrop                              | mask edges at 100%                                                                                                                           |

Stages: render → **gate** (§1) → fixes (§2, then the gate again) → deliverables (§3) → message (§4) →
handoff (§5).

## Mode and validation target

Read `analysis/task-contract.json` (`mode`, `mode_reason`, `explicit_locks`, `creative_freedoms`) and `plan/creative-plan.json` before QA. REMIX is the default for a new deliverable; EXACT requires an explicit whole-edit 1:1 / same-sequence / subject-only replacement request. A specific exact property is an explicit lock, not a reason to force the entire remix onto the source timeline. Continue an existing deliverable under its saved contract, updated only by the latest user steering; do not silently reset its mode on a revision.

The source breakdown and its legacy `format_lock` are SOURCE evidence. REMIX is tested against the authored `output_target`, shot/story/motif plan, intended identity and explicit user locks. Its new order, scenes, duration, frame count, text or format are not failures merely because they differ from the reference. EXACT is tested against the locked source and explicit requested changes. Never rewrite source metadata to make an output pass, or call a new authored scene an observed source event.

## 1. The gate

Run it on every version before showing it, and again after every fix. Write the result to
`qa/gate_v<N>.md`: one line per check with PASS / FAIL / NOTE and the frame numbers. Do not show a
version with an open BLOCK item. If a BLOCK cannot be fixed after two targeted free repair passes and at most one paid retry per
failed job within the internal hard cap and any existing user/account limit, save the work and report the limitation without a
question. If reliable live pricing or task/account authority is unavailable, use a supported
authorized free route or state the blocked/partial result declaratively. Mandatory service consent
cannot be bypassed and never creates a question or waiting state in this workflow. Never relax the
cap or fabricate a pass.

The visual gate covers EVERY decoded output frame and every output second, including the partial tail. Use the output's actual PTS grid and its declared target in both modes; EXACT inherits source timing except explicit user changes. Batch readable contact sheets and native crops without reducing coverage. Machine checks, playback alone, sparse keyframes or two overview sheets are insufficient. EXACT additionally requires complete source/output comparison through the declared mapping (§1.4), including explicit timing/format changes; equal indices apply only when the grids actually match. REMIX uses reference comparisons for relevant aesthetic/motion/material/type evidence and specifically locked intervals, not invented one-to-one shot correspondence. Fresh eyes (§1.6) never replaces this complete inspection.

### 1.1 Checks

| #   | Check                    | How                                                                                                                                     | Pass rule                                                                                                                                                                                                                        | Severity                             |
| --- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | Frame count              | Decode the delivered output; compare with the task's target                                                                             | REMIX equals `creative-plan.output_target.frames`; EXACT equals locked source video frames except explicit changes. Never use audio/container duration as video frame count                                                      | BLOCK                                |
| 2   | Presentation timing      | Actual decoded PTS and endpoint, rational rates; source comparison only for exact timing locks                                          | Match `output_target`; EXACT preserves corresponding source relative PTS within time-base tolerance except explicitly changed timing, which follows the declared mapping. Equal average fps never proves VFR timing              | BLOCK                                |
| 3   | Duration and ending      | Actual video endpoint; N/fps only on verified CFR; audio endpoint separately                                                            | Match the authored ending in REMIX or source ending in EXACT except explicit changes, including required audio tail; no accidental truncation                                                                                    | BLOCK                                |
| 4   | Format and color         | Width, height, SAR, pixel format, color metadata                                                                                        | Match `output_target` and explicit locks. EXACT preserves source interpretation; any planned REMIX conversion is real and documented, never an HDR retag                                                                         | BLOCK (size) / FIX (tags)            |
| 5   | Audio                    | Probe, packet/timing checks, encoded loudness and §1.3                                                                                  | Planned song/SFX/dialogue present and synchronized. Exact-audio claim needs identical packets AND correct relative A/V offset; new mix true peak ≤ −1.0 dBTP                                                                     | BLOCK (missing required audio) / FIX |
| 6   | Complete visual coverage | Every output frame/second; full aligned pairs additionally in EXACT (§1.4)                                                              | Actually inspected gap-free manifest, readable detail for every effect/text/transition event; sparse catalog sheets are navigation only                                                                                          | BLOCK                                |
| 7   | Story, trick or motif    | Planned shot roles, causal/reveal order or visual development; source evidence                                                          | REMIX fulfills its chosen story arc or visual motif through purposeful shots; a non-narrative edit does not need an invented plot. EXACT performs the measured source device at its locked frames                                | BLOCK                                |
| 8   | Identity and cast        | Every intended appearance including back/profile, body crops, occlusion, distance, reflections and stylization; every frame with extras | Correct identity and continuity for ALL planned target shots; no role swap or substituted mannequin; preserve intended concealment rather than revealing a hidden face                                                           | BLOCK                                |
| 9   | Text, logos and marks    | Full-output sheets and native crops of text/garments/screens/props                                                                      | REMIX matches its authored words/design and explicit locks; EXACT retains source words/marks unless changed. No pseudo-letters or doubled captions; retained footage keeps its actual credit marks                               | BLOCK                                |
| 10  | Mask edges               | Native crops in bright/dark/fast-motion and hair states, plus full-frame inspection                                                     | No holes, halos, lag or chewed silhouette; no local face/head repair                                                                                                                                                             | FIX                                  |
| 11  | Bars and edges           | Every frame edge against the planned composition                                                                                        | No accidental bars, rotation wedges or cropped required elements. Intentional REMIX layout is documented; EXACT retains source framing                                                                                           | BLOCK                                |
| 12  | Cadence and retiming     | Actual repeated/unique frames and all retimed output intervals                                                                          | REMIX follows authored motion/cadence without accidental judder; EXACT matches source holds/steps/cadence except specifically requested retiming, checked against its declared mapping. A coarse uniqueness ratio proves neither | FIX                                  |
| 13  | Text placement           | Cue/box plan and every rendered text event                                                                                              | REMIX follows its typography design and locks; EXACT matches source glyph geometry/timing/occlusion. No unintended clipping, fallback font or unreadable mandatory words                                                         | FIX                                  |
| 14  | Look and material        | Native crops of every distinct output texture/light/grade state, linked to relevant source evidence                                     | REMIX has a coherent authored aesthetic with purposeful material, texture and effect choices; EXACT matches measured source look. No accidental muddy faces or default decorative effects                                        | FIX                                  |
| 15  | Declared source reuse    | Compare each reused segment with its true source range and intended mapping                                                             | Reuse attribution and timing are correct; an unchanged-pixel claim needs direct evidence. Do not apply unaligned global PSNR to a remix                                                                                          | BLOCK                                |
| 16  | Cut/event positions      | Every planned output boundary and its adjacent frames                                                                                   | REMIX follows its authored timeline; EXACT follows locked source boundaries or their explicitly requested time mapping. No neighboring-shot leak or lost event                                                                   | FIX                                  |

BLOCK = do not label an unfinished render complete. FIX = repair within bounded attempts (§2), otherwise report a production/lock limitation (§3.6). Intentional REMIX adaptations are not defects and need no apology as "not 1:1". An unresolved exact lock cannot be called matched. NOTE records non-blocking context; disclose material limitations without waiting for a question.

**Slow-motion fallback (#12)** for authored/generated footage; planned REMIX cadence or locked EXACT cadence takes priority over these technical defaults:

- **0.3–1×:** blend the two neighbouring source frames, weighted by the fractional index. Duplicated
  frames here judder (Jensanity f226, caught in QA).
- **Below 0.3×, or fast limbs:** nearest frame. Blending there reads as a matte halo.
- **Freeze holds:** integer frames.

A run of 2–3 identical frames inside a 0.3–1× cut intended to move smoothly is a FIX; intentional authored/source-stepped cadence is not.

### 1.2 Machine pass

**Unchanged, matching timing grids only (EXACT or scoped exact intervals):** run the two helper operations below on the delivered file and always pass `--ours`. `compare.py check` assumes a reference-aligned timing contract; `--expect-frames`/`--expect-size` do not make it understand deliberate retiming or a new REMIX timeline. Never require its global PASS for explicit duration/fps/timing changes in EXACT. For a matching locked interval in either mode, compare corresponding source/output ranges separately with verified offsets and rates.

**Explicitly changed EXACT timing/format:** verify actual output dimensions, frame count, rational fps/PTS, video/audio endpoints and conversion against `creative-plan.output_target`. Maintain the source/output interval mapping described in §1.4 and compare all unchanged content/properties through it. Source-equality failures caused solely by the documented user change are not production defects; unchanged intervals and unrelated properties remain locked. A format-only change may use `check --expect-size WxH` when timing still matches. A timing change needs the target/mapping pass, not `--expect-frames` plus an impossible global timing PASS.

**REMIX full-output pass:** probe/decode the delivered file against `creative-plan.output_target`, inspect its actual PTS map and endpoint, and measure its encoded audio. Generate complete native-output sheets with the existing `rrio.py sheet <output> <sheet> --indices <consecutive-indices> --max-bytes 120000`; repeat readable batches until the union covers every output frame. Independently check every authored cut/event, cue, motif and explicit lock. Record concrete measurements in `qa/gate_vN.md`; a hand-written PASS without evidence is insufficient. Use reference crop pairs with separately labelled source/output times for craft review, not a global equal-N assertion.

EXACT helper example:

```
python3 $RR/compare.py check $W --ours out/<slug>_vN.mp4 --audio-mode copy
python3 $RR/compare.py sheet $W --ours out/<slug>_vN.mp4 --frames 0,1,2,3,4,5,6,7 --out qa/pairs_all_B01.jpg --max-bytes 120000
```

- Without `--ours`, compare.py takes the newest mp4 in `out/` (a `final_vN` name first), which can
  be `out/base.mp4` or an older render.
- `check` writes `qa/check_<file>.json` with PASS / FAIL / NOTE per check, and exits 1 on any FAIL.
  It also lists both files' audio codec, sample rate, channels, MD5 and ebur128 loudness (check #5).
  `--expect-frames N --expect-size WxH` adjust only those checks. They do not disable source PTS/fps/duration comparison; use the target/mapping pass above for an explicitly changed timing grid.
- **Audio, `--audio-mode auto` (the default, D19):** an MD5-equal stream passes. Audio that is not
  bit-identical but is still the reference's own track (same codec and profile, sample rate and
  channels, integrated loudness within 0.5 LU (`--reuse-lu`), duration within one frame) passes as
  "not bit-identical (acceptable)" under the legacy machine check, with `true_peak` as a NOTE: the −1 dBTP limit is for new mixes
  only. Anything else is treated as a new mix and gets the true-peak rule. Report any
  mismatch as a fidelity difference under §1.3. For reference audio, run `--audio-mode copy` to demand the MD5;
  the legacy auto pass is not sufficient for exact audio. `mix` evaluates a new mix selected by the REMIX plan or explicitly requested in EXACT.
- **Bars and a declared border (#11):** an edge bar the reference lacks is a FAIL, unless the frame is
  meant to have one. `check` reads the workspace EDL (`comp/edl.json`, or `--edl`): when it declares
  `post.border`, a shot's `fx.border` or a border layer (the Katana hand-inked frame), or when you pass
  `--expect-border`, bars up to `--border-max-frac` of the side (default 6 %) are a NOTE. A thicker bar
  or an all-black output still FAILs. A declared border passes fidelity review only when it is
  present in the exact reference or permitted by the REMIX composition/explicit user change; a detector exception is not creative evidence. VERIFIED live 2026-10-08: the Katana remake passed everything
  except a false `bars` FAIL caused by its intentional `post.border` ink frame, which is what this
  rule now excuses. For a border drawn outside the canvas kit, pass `--expect-border`.
- Always pass `--frames` with explicit consecutive indices for each bounded chronological batch
  and a unique `--out qa/pairs_all_BNN.jpg`; `--per-sheet 12 --max-bytes 120000` gives readable
  paginated pairs. Submit successive batches whose union is [0,N). The helper's default breakdown
  selection and its fallback 12 evenly spaced frames are insufficient. Do not use `--every` as a
  substitute: time rounding can duplicate or omit frames. Inspect every generated page, up to four
  per image call. Add native crops for unclear details and all measured event start/peak/end frames.
- Exact arguments: `--help`. Use the script for actual argument names; legacy diagnostics never override the no-question,
  fidelity or hard-cap policy.

For source-aligned EXACT CFR comparisons only, the fallback below supplies partial metrics for checks 1–5, 11, 12, 14 and 15 when the helper is unavailable. It does not verify actual PTS/audio offset or full inspection coverage; verify those separately. Never apply this same-index fallback to VFR or an unaligned REMIX timeline.
It was tested on the Altman and Yaong refs and finals; on 862 frames of 1080×1920 it takes ~4 s.
Run it in bash inside `$W`.

```
REF=ref/ref.mp4; OUT=out/$(basename "$W")_v1.mp4; BD=analysis/breakdown.json
for f in $REF $OUT; do ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,sample_aspect_ratio,pix_fmt,r_frame_rate,avg_frame_rate,nb_read_frames,color_primaries,color_transfer,color_space:format=duration -of compact=p=0 "$f"; done
for f in $REF $OUT; do ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,profile,sample_rate,channels -of compact=p=0 "$f"; ffmpeg -v error -i "$f" -map 0:a:0 -c copy -f md5 -; ffmpeg -hide_banner -nostats -i "$f" -map 0:a:0 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2; done
python3 - "$REF" "$OUT" "$BD" <<'PY' > qa/metrics_v1.json
import json, subprocess, sys
import numpy as np
ref, ours, bdp = sys.argv[1:4]
try: bd = json.load(open(bdp))
except Exception: bd = None
def size(p):
    s = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height", "-of", "json", p], capture_output=True, text=True).stdout)["streams"][0]
    return s["width"], s["height"]
(rw, rh), (ow, oh) = size(ref), size(ours)
W = 160; H = max(2, round(W * rh / rw / 2) * 2)
def frames(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", f"scale={W}:{H}:flags=area",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32)
R, O = frames(ref), frames(ours); n = min(len(R), len(O))
gR, gO = R @ [.299, .587, .114], O @ [.299, .587, .114]
def psnr(a, b):
    m = float(((a - b) ** 2).mean()); return 99.0 if m < 1e-6 else 10 * np.log10(255 ** 2 / m)
def sat(x):
    mx, mn = x.max(-1), x.min(-1); m = mx >= 40
    return round(float(((mx - mn)[m] / mx[m]).mean()), 3) if m.any() else 0.0
def uniq(g):
    return int(1 + (np.abs(np.diff(g, axis=0)).mean(axis=(1, 2)) > 0.3).sum()) if len(g) > 1 else len(g)
fails, review = [], []
if len(R) != len(O): fails.append(f"frame count {len(O)} != ref {len(R)}")
if abs(rw / rh - ow / oh) > 0.01: review.append(f"aspect {ow}x{oh} != ref {rw}x{rh} (ok only if the user changed the format)")
cuts = [(c["id"], c["f0"], min(c["f1"], n - 1), (c.get("route_suggestion") or {}).get("route")) for c in bd["cuts"]] if bd else [("all", 0, n - 1, None)]
per = []
for cid, f0, f1, route in cuts:
    p = {o: round(float(np.median([psnr(gR[i], gO[i + o]) for i in range(max(f0, 1), min(f1, n - 2) + 1)] or [0])), 1) for o in (-1, 0, 1)}
    ur, uo = uniq(gR[f0:f1 + 1]), uniq(gO[f0:f1 + 1])
    lr, lo = float(gR[f0:f1 + 1].mean()) / 255, float(gO[f0:f1 + 1].mean()) / 255
    per.append({"id": cid, "route": route, "psnr_-1_0_+1": [p[-1], p[0], p[1]], "unique_ref": ur, "unique_ours": uo,
                "luma_ref": round(lr, 3), "luma_ours": round(lo, 3)})
    if route == "KEEP" and (p[0] < 35 or p[0] < max(p[-1], p[1])):
        fails.append(f"{cid} KEEP cut: PSNR at 0 = {p[0]} dB (-1: {p[-1]}, +1: {p[1]}) -> not the original pixels or shifted")
    if ur >= 8 and (uo < 0.6 * ur or uo > 1.5 * ur):
        review.append(f"{cid}: unique frames {uo} vs ref {ur} (cadence differs)")
    if abs(lo - lr) > 0.06: review.append(f"{cid}: mean luma {lo:.2f} vs ref {lr:.2f}")
d = np.abs(np.diff(gO[:n], axis=0)).mean(axis=(1, 2)); dr = np.abs(np.diff(gR[:n], axis=0)).mean(axis=(1, 2))
dups = [i + 1 for i in range(len(d)) if d[i] < 0.3 and dr[i] >= 0.3]
if dups: review.append(f"{len(dups)} held/duplicate frames where the ref moves, first: {dups[:12]}")
b = max(1, W // 50)
def edges(g): return {"top": float(g[:, :b].mean()), "bottom": float(g[:, -b:].mean()), "left": float(g[:, :, :b].mean()), "right": float(g[:, :, -b:].mean())}
er, eo = edges(gR[:n]), edges(gO[:n])
for k in er:
    if eo[k] < 16 and er[k] > 32: fails.append(f"dark bar on the {k} edge (ours {eo[k]:.0f}, ref {er[k]:.0f})")
sr, so = sat(R[:n]), sat(O[:n])
if sr > 0.05 and abs(so - sr) / sr > 0.25: review.append(f"saturation {so} vs ref {sr}")
out = {"fails": fails, "review": review, "frames": [len(R), len(O)], "sat": [sr, so],
       "luma_p1_p50_p99": [[round(float(np.percentile(g[:n], q)) / 255, 3) for q in (1, 50, 99)] for g in (gR, gO)],
       "dup_frames": dups, "edges": [er, eo], "cuts": per}
print(json.dumps(out, indent=1))
PY
python3 -c "import json; d=json.load(open('qa/metrics_v1.json')); print('FAIL:', *d['fails'], sep='\n  '); print('REVIEW:', *d['review'], sep='\n  ')"
```

What it reported on real finals:

- **Yaong v2 vs its reference:**
  - FAIL: frame count 285 vs 283.
  - REVIEW: aspect 1440×1080 vs 900×720 (historical run with an explicit 4:3 request;
    never infer that choice for the current task); cadence 280 vs 170
    unique frames (the reference steps at ~18 fps); saturation 0.133 vs 0.196.
- **Altman v3 vs original:**
  - The 4 KEEP cuts passed at 39.7–43.8 dB with offset 0 best.
  - REVIEW: cadence on 8 swapped cuts (c12 14 vs 36, c08 13 vs 32, …); 261 held frames where the
    reference moves.
  - A cut wrongly marked KEEP (c13 had been swapped) came out at 29.3 dB → FAIL. The gate catches
    route mismatches too.

REVIEW lines are prompts to look, not verdicts. A luma or saturation difference on a cut that was
re-created on purpose may be right. Decide on the crops.

### 1.3 Audio rule

- **Reference audio reused unchanged** (EXACT default; optional REMIX choice):
  - Mux it with stream copy. `assemble.py` and `comp/render.py` do this themselves (`-c:a copy`, the
    whole track untrimmed when it starts at 0 and runs at most 0.5 s past the picture;
    `references/compositing.md` §11). A remux by hand:
    `ffmpeg -i video.mp4 -i ref/ref.mp4 -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart out/<slug>_vN.mp4`.
  - **Require an MD5-equal stream copy for exact audio.** The audio stream MD5 then equals the reference's (verified
    on Altman and Yaong).
  - In the sandbox (ffmpeg 5.1) both renderers' copies came out MD5-equal to the reference on
    2026-10-08: the Katana remake through `comp/render.py`, the Altman swap through `assemble.py`
    (VERIFIED live).
  - On local ffmpeg 8, `-c copy` with `-t 9.4333` or `-shortest` kept all 205 AAC packets of the Yaong
    reference and the MD5 unchanged; only the edit list got shorter. A hand remux with `-t` or
    `-shortest` is **not yet verified on the sandbox's ffmpeg 5.1**, so do not assume it: check #5
    measures the MD5 on every render.
  - **A different MD5 is a fidelity difference.** First remux from the original source. Matching
    codec, sample rate and loudness alone does not prove identical words, timing or sound. If the
    original stream cannot be retained, record the exact limitation in QA and delivery; do not call
    the audio 1:1. Do not ask to accept a substitute.
  - When the codec, profile, sample rate or loudness differ (e.g. HE-AAC in the reference, AAC-LC
    in ours), it is a FIX: remux by hand from the right file.
  - No loudnorm and no limiter on reused audio. Require the same audio start offset relative to the first video PTS (`compare.py check` audio_sync); identical packet MD5 alone can conceal a shifted soundtrack.
  - Copy from the same file you will show as "Original". Altman's finals carried the HE-AAC track
    while the delivered "original" had AAC-LC, so their MD5s could never match.
- **New mix** (authored REMIX audio or explicitly changed EXACT audio; user track, retained authorized audio, recorded stock/library SFX):
  - limit with `alimiter=…:level=disabled` (otherwise it renormalises to 0 dBFS);
  - measure the **encoded** file: `ebur128=peak=true` true peak ≤ −1.0 dBTP. Katana's limiter at
    0.84 still peaked +0.4 dBFS after AAC; 0.79 gave −1.2;
  - report integrated loudness;
  - follow a requested loudness target, or choose and record a suitable REMIX mix target autonomously; do not normalize an unchanged exact soundtrack merely to meet a generic target.
- Listen to aligned audio when an available tool actually supports playback/listening. Otherwise
  report "measured, not listened"; never claim an audible check from metrics alone.

### 1.3.1 Final lyrics, song and sound check

When the task requires lyric text (including source lyrics retained by EXACT), verify the required supplied/transcribed words in the final encoded video, not just in a cue file, prompt, preview or placeholder. Check every cue's first/peak/last frame, spelling, actual loaded font, geometry, planned layer order (source-exact when locked) and synchronization to the selected supplied audio. A video model failing to draw words is resolved by a deterministic text pass after the visual render. Final assembly does not mean moving all lyrics to an end card or accidentally extending the planned output duration. REMIX may intentionally plan a different ending; EXACT retains the locked source ending.

After the last text render and audio mux, inspect the beginning and all final seconds through the final video frame and planned audio tail (the source tail when preserved). Verify the last lyric stays for its measured interval, the song is still present, no short SFX file truncates it, and no unrequested silence/fade or `-shortest` cut was introduced. Listen when actual playback is supported; otherwise explicitly report measured-not-listened checks and inspect packet/cue timing. Preserve reference music/SFX or use actual authorized recorded assets; procedural noise, synthesized beats and generic whooshes fail this workflow's audio QA.

Identity coverage includes all targeted shots, including faceless, occluded, back-facing and wide views: preserve the user's intended character through silhouette, hair, clothing, proportions and motion while retaining planned occlusion (source occlusion in matched EXACT shots). Do not turn those shots into arbitrary mannequins or skip them because facial landmarks are unavailable.

### 1.4 Complete frame inspection and comparison scope

In REMIX, N and D below mean the decoded OUTPUT frame count and actual presentation endpoint. Inspect every output frame chronologically, all one-second intervals including the partial tail, every cut boundary and every effect/text/transition start/peak/end. Use native crops when sheets hide detail. Check story roles, scene order, motif development/payoff and continuity against `plan/creative-plan.json`; compare the chosen source examples for aesthetic, material, typography, music and motion principles. Label source and output times separately. New scenes have no invented source-frame equivalent.

Save `qa/inspection_vN.json` with `mode`, output identity/revision, decoded output count and PTS map, actual viewed [start,end_exclusive) ranges, sheet paths, detail/event evidence, findings and per-second coverage. Validate that these OUTPUT ranges union to [0,N) and seconds to [0,D), without gaps or out-of-bounds indices. Source observation coverage remains separately in `analysis/coverage.json`; it cannot substitute for viewing the final output. Any scoped exact locks additionally need their actual source/output mapping and aligned inspection. Continue small batches rather than skip frames or weaken the claim.

**EXACT with explicit timing changes:** save a `source_output_mapping` in `plan/creative-plan.json` containing source and output frame/PTS bounds, the actual requested time transform or edit, unchanged property locks and the user instruction authorizing each exception. Inspect both complete timelines and compare every retained source interval with its actual mapped output interval. For fps conversion, speed changes or holds, repeated source/output indices may be intentional; record those mappings rather than pretending equal indices. Track source and output coverage separately, including every native frame and second on each side; any deliberately omitted/added interval needs its explicit change reason. Use separately labelled native sheets/crop pairs or a verified mapping-aware comparison. `compare.py sheet` aligns equal relative presentation time and cannot apply an arbitrary offset, speed ramp or edit map. Do not use it globally for such a map or change the source master to make it align.

For the remainder of this section, N/D refer only to an unchanged, verified corresponding source/output timing grid. This **same-grid EXACT aligned-pair** recipe also applies to matching scoped intervals; it does not override an explicit timing change or force a REMIX onto the source grid.

Build chronological pair batches that include every frame from 0 through N-1. Match the exact
reference frame grid and PTS map; verify count/fps first so `compare.py sheet --frames` aligns each
output index to the correct source index. It maps pairs by actual presentation intervals, including VFR holds. A complete paired inspection still requires every source/output range in the manifests; repeated reference indices cannot fill a missing interval. Missing timing metadata is an explicit failure, not a nominal-fps substitute. Check all one-second intervals including the partial tail, all cut boundaries,
and every effect/text/transition start, peak and end; events get enlarged detail in addition to
full-coverage sheets. Compare layer order, opacity curves, movement/easing, texture, grain, grade,
lighting and typography against the analysis logs.

Save `qa/inspection_vN.json` containing actually inspected [start,end_exclusive) ranges, sheet paths,
PTS bounds and findings, plus coverage of each `analysis/seconds.json` interval and event.
The agent writes this manifest; `compare.py` does not validate it. Sort and merge actually
inspected ranges, reject empty/out-of-bounds ranges, verify every evidence sheet was viewed,
and verify the union equals [0,N) without gaps and second intervals cover [0,D). Unreadable detail or uninspected ranges block a complete QA
claim: continue smaller batches/crops without questions. A partial report states the exact gaps.
The sample command below illustrates a single explicit batch only; repeat with consecutive indices
until all frames are inspected. It is not an acceptable key-frame-only gate.

Render "ref | ours" pairs, 8–12 pairs per sheet, and look at all of them, 3–4 sheets per call
(≤512 KiB). `compare.py sheet` does this (§1.2). The fallback below was tested on Altman with
8 pairs and no crop: 1216×2168, 142 KiB at `-q:v 7` and 112 KiB at `-q:v 11`, with the labels still
readable. Before each call verify at most four image files and summed size at most 524,288
bytes. Keep `CROP` empty for the complete baseline: outer captions, borders and watermark must
remain visible. Produce separately named cropped detail sheets in addition to those baseline pairs.

```
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf   # any existing TTF
OUT=out/$(basename "$W")_v1.mp4           # the render under test
FR="0 1 2 3 4 5 6 7"                    # first consecutive batch; repeat to cover all N frames
CROP=""                                   # mandatory full-canvas baseline; detail crops are additional
SEL=$(for f in $FR; do printf 'eq(n\\,%s)+' "$f"; done); SEL=${SEL%+}
ROWS=$(( ($(echo $FR | wc -w) + 1) / 2 ))
LBL="drawtext=fontfile=${FONT}:text='%{n}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.7"
ffmpeg -v error -y -i ref/ref.mp4 -i "$OUT" -filter_complex \
 "[0:v]${CROP}scale=300:-2,${LBL},select='${SEL}'[a];[1:v]${CROP}scale=300:-2,${LBL},select='${SEL}'[b];[a][b]hstack,pad=iw+8:ih+8:4:4:white,tile=2x${ROWS},format=yuvj420p" \
 -fps_mode passthrough -frames:v 1 -q:v 7 qa/pairs_v1_01.jpg
```

- `drawtext` goes before `select` so the labels are absolute frame numbers.
- This runs in bash (the sandbox shell). In zsh, `$FR` does not word-split.

On the Altman v3 sheet this showed:

- a word already fading in at f16, where the reference has none (a 1-frame fade offset);
- the replace render dressing the shirtless boxer at f614 in the photo's grey crewneck.

Both are exactly the kind of finding the user would otherwise report.

### 1.5 Identity, edges, look: the three crop sheets

- **Separate image roles:** for image-based stylized replacements, compare structure and style
  against the extracted source frame and identity against the supplied character/photo. Verify
  source pose, camera, palette, line/shading texture, lighting, scenery and text remain faithful;
  the identity photo's background or photographic style must not leak into the reconstruction.
  This is the matched-shot test for EXACT or a scoped source-composition lock. For a new REMIX scene compare staging against the authored shot plan and identity against its intended reference. A Genjutsu/Styles preset is not a QA requirement.
- **Identity:** one tile per `face_clear` cut, cropped around the face (`faces.py` boxes when they
  exist, otherwise by hand from the key frame), plus the identity anchor as the first tile.
  - Check head shape, hair, brows, skin tone, moles, earrings, glasses, and wardrobe per look.
  - Then look at every frame with a second person: Genjutsu has swapped roles, painted a faceless
    white mannequin, and put the hero's hair on the wrong person.
- **Mask edges:** 100% crops in four places: brightest background, darkest clothing, hair, fastest
  motion.
  - Fixes in code: dilate/erode ×8 for holes in dark hair (Yaong), threshold max(RGB) > 8–9 for
    person-on-black mattes, an x-range clamp and a difference-key union for props SAM misses.
  - A matte that lags the plate is an fps mismatch (`color=…:r=<plate fps>`).
- **Look:** native crops for every recorded texture/grade/light state at `look.crop_frames`,
  paired with corresponding source frames in EXACT or relevant labelled material/style exemplars in REMIX, plus all output per-second intervals (`references/analysis.md` §5.2).
  - Compare brightness, neutrality, saturation and noise.
  - Seedance plates have come out ~40% less saturated than a clean reference. EXACT must not add grain, vignette or an accent to a clean source. REMIX must distinguish its planned treatment from an accidental generator/compositor mismatch.
  - **Threshold / xerox looks:** crop every identity-legible medium close-up and close-up, ref vs ours.
    In the 2026-10-08 Katana remake the default xerox levels crushed the hero's face to near-black
    where the reference keeps eyes, nose and mouth readable. Undo or tune only the whole-plate filter that caused that loss, against the complete source shot. Never retouch a face ROI, repaint features or change skin/hair locally. A wrong underlying face requires supported model correction, not code.

**Face integrity gate:** inspect every targeted appearance before and after local composition. Verify that no face-swap library, mesh/landmark warp, face/head paste, facial inpaint, hairfix, manual eye/nose/mouth drawing or skin retouch changed identity pixels. Read tracking coordinates and whole-plate camera transforms are permitted; a reference's separate graphic overlay must remain identifiable as that overlay. Confirm background cleanup masks protect every visible person, including extras and complete head/hair silhouettes, after dilation and in both held/current frames. If model output has an identity defect, correct it through a supported authorized model within the existing cap or disclose it; never hide it with code.

### 1.6 Fresh eyes (optional, one round)

For long or dense edits, and only when your client can run subagents, you may run ONE reviewer
subagent that has not seen the build. Otherwise skip this step: the gate above is complete without
it. Give the reviewer:

- the task contract, authored plan, complete output sheets and crop evidence; aligned source pairs for EXACT or scoped exact locks;
- the brief: "what reads cheap, wrong, unreadable, mistimed, or like a different person".

Then filter what comes back:

- EXACT preserves intentional source devices (strobe, two-frame flashes, black ending); REMIX checks whether each authored device serves its new story and locks, rather than defending it solely because a reference used it;
- identity breaks, garbled text, dead holds, clipped words, judder, and missing or extra frames are
  fixed.

Do not chase a score: Aura's accepted films scored 5–6.5/10 from fresh eyes. After fixes, run one
**regression check**: compare affected shots/events against the previous version using their actual revision mapping; same-index pairs are valid only when timing stayed unchanged. Katana's
second review round existed only to undo a regression the first round introduced. No second review
round unless the first found BLOCK items.

## 2. Fix order

1. **Code for assembly defects only (0 credits).** This never covers facial appearance or identity. Use at most two targeted repair passes for a failing render,
   re-rendering and re-running the gate after each pass. What code covers:
   - EDL timing/in-points, authored text/grade and audio mux; source-exact values where the contract locks them;
   - mask edges for the complete generated subject, and separate permitted graphics from the authored plan or source; no isolated head paste or local face/feature patch;
   - cadence: follow the authored REMIX pattern or locked source pattern, re-apply whole-plate digital zooms at output fps, and the
     slow-motion rule of §1.1 (#12);
   - framing: follow authored REMIX composition or measured EXACT source geometry. An aspect mismatch alone never justifies blind cover-fit or a fixed crop center; inspect any intended crop against identity, subject visibility and explicit locks.
   - Do not use this rule to avoid a required model-based facial correction. Use code only for the permitted assembly operations above. Crop and pad replace `reframe`; minterpolate, tmix and frame
     blending replace `fps_boost` and deflicker; footage that ships at its native size never gets a
     video upscale.
2. **Re-cast from what exists (0 credits).**
   - another in-point in the same plate, another take or plate already paid for, unused plate
     seconds;
   - a still with code motion;
   - source reuse only when it fulfills the task. A failed target replacement cannot become KEEP because its face is hidden or small; an unavailable required change remains unresolved;
   - repair newly introduced pseudo-text and restore required lettering from actual source assets where suitable. REMIX authors its own planned text; do not erase credit marks from retained source footage or remove locked logos.
3. **Paid re-roll, only for a failure from the fail list.** The fail list: identity, wardrobe,
   garbled text or logo, anatomy, a matte-hostile background, and a missing beat the EDL needs that
   no other plate second supplies. "A better take" is not a failure, and neither is anything code or
   a re-cast can fix.
   - **Shot failure** (one planned shot fails): re-roll that shot alone as a single-shot job of
     max(4, ceil(2 × its slot)) seconds at the same resolution. Gestures run 1.5–2× slower than
     prompted; Yaong's hearts prompted at 2.7–3.6 s arrived at 8–9.75 s, so a bare 4 s job of a
     2.5 s slot misses them again. Genjutsu: the same cut again on its 96-frame pad; a
     motion-transfer part: that part again.
   - **Job failure** (the canary, or any job where half or more of its planned shots fail for one
     cause): fix the cause and re-run the whole job once. That run is the job's re-roll.
   - Fix the diagnosed failure against the authored plan and explicit locks; EXACT retains source framing/words except requested changes. Preserve required captions in final assembly even if replacement inputs need cleanup. Never resubmit the same request hoping for luck.
   - **One paid retry at most per failed job**, only if it fits the internal hard cap and every existing user/account limit and
     the guard passes. The guard may enforce legacy rules; also enforce the stricter internal hard cap and any user/account limit independently. When live price or
     task/account authority is absent, do not submit a paid retry; use an authorized fallback
     or report the limitation without asking or waiting:
     ```
     python3 $RR/ledger.py guard $W --line <line id> --reroll-of <job id> --reason "<fail-list item>" [--slot <slot s>]
     python3 $RR/ledger.py add $W --line <line id> --job <new id> --reroll-of <job id> --reason "<fail-list item>" [--slot <slot s>]
     ```
     - Pass `--slot` for a shot failure. The ledger then prices the single-shot job of
       max(4, ceil(2 × slot)) s at the line's resolution.
     - Leave it out, with `--reason "job failure"`, for a whole-job re-run.
     - Run `add` right after the submit returns, so every re-roll is logged with its reason. Exact
       flags: `ledger.py <subcommand> --help`.
   - Do not run a second paid retry, expand authorized scope, change the locked output target as an unrecorded workaround, or exceed
     the internal hard cap and any existing user/account limit. Use a faithful free route if available; otherwise state the
     limitation. Never ask for approval, credit confirmation or a cap increase. If mandatory
     service consent prevents execution, use an authorized fallback or state the blocked/partial
     outcome without asking, waiting or bypassing permissions.
   - Never re-run a whole batch for one bad shot.
4. **After every fix:** the full gate again, plus the regression pair sheet against the previous
   version.

Do not mark a fix as done until the gate shows it fixed on the new render (the Katana handoff
over-claimed "all 23 applied"). A FIX item you could not fix goes into the mode-appropriate limitations report (§3.6) with the reason; a deliberate REMIX adaptation is not a FIX.

## 3. Deliverables

Every delivery carries the film, actual spend/limitations summary and recoverable state when supported. EXACT additionally carries the aligned comparison; REMIX may include clearly labelled craft/interval evidence when useful, without pretending the whole timelines match. Version names are `v1, v2, …`. Never call a version "final"
or "accepted" before the user does.

### 3.1 The film

`out/<slug>_v<N>.mp4`:

- **Video:** follow `output_target` color/bit-depth policy and explicit locks. EXACT preserves source interpretation through stream reuse or a verified capable renderer; REMIX may intentionally choose a supported delivery format, while source masters remain unchanged. For an SDR/bt709 source, the bundled delivery recipe is
  H.264 High, `yuv420p`, CRF 18 and `-movflags +faststart`, with correct bt709 metadata.
  The bundled canvas pipeline cannot preserve HDR/higher bit depth. If no faithful supported
  route exists, deliver the closest feasible verified SDR conversion, explicitly label that
  deviation and do not claim 1:1 or ask a question. Retagging HDR pixels as bt709 is not conversion.
- **Format:** frame count, fps/PTS, endpoint and size from the authored `output_target`; EXACT derives these from source locks except explicit changes. REMIX does not inherit the source frame count. Use actual PTS when retaining variable-rate timing.
  The legacy `compare.py check` reports non-bt709/non-yuv420p tags as warnings regardless of source.
  Judge exact source locks or the authored color plan against probed metadata; do not alter correct tags merely
  to silence that warning. Verify dimensions explicitly because its default size mismatch is WARN.
- **Audio:** the chosen source stream or planned new mix (§1.3); AAC-LC 256k 48 kHz is an available delivery recipe, not an exact source-audio substitute.
- **Size:** heavy per-frame grain is large (Katana: 29 Mb/s, 100 MB for 27 s at CRF 20). Produce a smaller social copy when requested or required by the delivery target, preserving the verified master; no choice/confirmation prompt.

### 3.2 Getting files out of the sandbox

Files die ~10 s after a call, so upload in the same command that makes them (details in
`references/sandbox.md` §8–9 and `references/mcp-api.md` §2.1):

1. **`media_upload` first,** in ONE call with `files[]` for all files of this delivery (slots are
   single-use and the state save needs its own; VERIFIED live 2026-10-08):
   - the film `<slug>_vN.mp4`;
   - the comparison `<slug>_vN_compare.mp4` for EXACT, or only a genuinely useful labelled REMIX comparison artifact;
   - the triptych `<slug>_vN_triptych.mp4` when there is one;
   - the state archive `<slug>_vN_state.tar.gz`, a general file (never `.tgz`, which is refused). Keep
     the `content_type` from its reply for `rr_save`; for archives it is `application/octet-stream`
     (verified live; `references/sandbox.md` §9);
   - that is usually ≤4 files (each reply costs ~4k tokens per file).
2. **One sandbox command:** final encode (or remux) → applicable comparison/evidence render →
   `rr_save '<state upload url>' '<state content_type>'` → `rr_put <file> '<upload url>'` for each
   file. Each presigned URL is single-use. `rr_put` refuses a missing or empty file instead of
   burning the slot, and prints `HTTP <code>`. Long renders run as `background:true` with
   `rr_bg qa/render_vN.log "<encode && compare && rr_save … && rr_put …>"`; poll with
   `rr_status qa/render_vN.log` in short calls.
3. **`media_confirm` only after HTTP 200:** one call with type `video` for the mp4s, one with type
   `file` for the archive (one type per call).
4. Give the user the URLs. Never open a browser for them.

### 3.3 Comparison: "Original | Ours"

An EXACT deliverable carries comparison evidence covering its full source/output mapping. The recipe below is for a verified unchanged timing grid only. If the user explicitly changed timing, use a mapping-aware comparison or complete separately labelled source/output evidence with actual times and the declared exceptions; do not silently hold, trim or resample away the difference. REMIX does not require a full-length Original | Ours comparison: use only genuinely matching locked intervals or labelled craft evidence. This display is not the master or a VFR-fidelity proof. Script help defines arguments, never task-mode policy.

```
python3 $RR/compare.py sbs $W --ours out/<slug>_vN.mp4 --out out/<slug>_vN_compare.mp4
```

- **Panels:** all panels share one height, min(1080, the tallest input). Each panel keeps its own
  input's display aspect and shows it whole, never cropped, so a 4:3 Genjutsu take sits whole next
  to a 9:16 reference. Panels are separated by 16 px black gaps (`--gap`), with no outer margin. If
  the total width would exceed 3840 px (`--max-w`), the height shrinks until it fits. All sizes are
  even.
- **Labels:** an 80 px black band on top (`--band`). The labels are white and static, centred over
  each panel, at half the band height (40 px) in DejaVu Sans Bold (the first system TTF found;
  `--font`). They are drawn with Pillow in the sandbox, else ffmpeg drawtext, else a bitmap font.
  The words are `Original`, `Ours`, and `Genjutsu` in the middle of a triptych. They stay in
  English unless the user asks for other words (`--labels "Original|Opus 5.5 + Genjutsu"`).
- **Timing:** the master timeline is ours (`--master ours`, the default): its fps and its frame
  count. An input at another fps is resampled to it, shorter inputs hold their last frame, and
  longer ones are cut. On this unchanged-grid path, gate checks first establish the reference's count and timing; the display's resampling itself proves neither.
- **Audio:** `sbs` takes it from ours (`--audio ours`, the default). It is stream-copied when the
  audio is at most 0.5 s longer than the video; otherwise it is trimmed and re-encoded to AAC 192k.
- **Encode:** H.264 CRF 20 (preset medium), yuv420p, bt709 tags, faststart.
- **Check:** compare.py prints a JSON line. It exits 1 with a `warning` when the output's frame count
  differs from the master's. Then look at one frame of the result.

Fallback when compare.py fails: the same layout in plain ffmpeg. Run it in bash; the LAST file is
the master. It was tested on local ffmpeg 8 against compare.py's drawtext labels, and the frames
came out pixel-identical:

- Katana, side by side: 2896×1160, 360 frames, the same audio MD5.
- Altman, triptych with a 4:3 plate in the middle: 2688×1160, 862 frames, audio MD5 equal to the
  reference's.

The 3840 px cap was checked the same way. It has not run on ffmpeg 5.1 yet, and it ignores
rotation metadata.

```
cmp_panels() {  # cmp_panels OUT AUDIO_FROM FILE1 LABEL1 FILE2 LABEL2 [FILE3 LABEL3]; the LAST file (ours) is the master
  local OUT=$1 AUD=$2; shift 2
  local FILES=() LABS=(); while [ $# -gt 1 ]; do FILES+=("$1"); LABS+=("$2"); shift 2; done
  local K=${#FILES[@]} G=16 BAND=80 FS=40 MAXW=3840 M=${FILES[$((${#FILES[@]} - 1))]} i f
  local FONT=${FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf} T; T=$(mktemp -d)
  local N FPS; N=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nw=1:nk=1 "$M")
  FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=nw=1:nk=1 "$M")
  # compare.py panel_layout: one height H (min(1080, tallest input)), each panel at its own display aspect,
  # total width <= 3840 incl. 16 px gaps (H shrinks to fit), even sizes; colour matrix as rrio._in_matrix
  local L; L=$(for f in "${FILES[@]}"; do ffprobe -v error -select_streams v:0 \
    -show_entries stream=width,height,sample_aspect_ratio,pix_fmt,color_space -of csv=p=0 "$f"; done | awk -F, -v G=$G -v MW=$MAXW '
    function ev(x) { x = int(x / 2) * 2; return x < 2 ? 2 : x }
    { split($3, s, ":"); sn = s[1] + 0; sd = s[2] + 0; if (sn <= 0 || sd <= 0) { sn = 1; sd = 1 }
      a[NR] = $1 * sn / ($2 * sd); if ($2 > mh) mh = $2
      t709 = ($1 >= 1280 || $2 >= 1280 || ($1 >= 720 && $2 >= 720)) ? "bt709" : "smpte170m"
      cs["bt709"] = "bt709"; cs["smpte170m"] = "smpte170m"; cs["bt470bg"] = "bt470"; cs["bt2020nc"] = "bt2020"
      cs["bt2020c"] = "bt2020"; cs["smpte240m"] = "smpte240m"; cs["fcc"] = "fcc"
      m[NR] = ($4 ~ /^(rgb|bgr|gbr|argb|abgr|gray|ya|pal)/) ? "none" : ($4 ~ /^yuvj/) ? "smpte170m" : ($5 in cs) ? cs[$5] : t709 }
    END { k = NR; H = ev(mh < 1080 ? mh : 1080); t = G * (k - 1); sa = 0
      for (i = 1; i <= k; i++) { w[i] = ev(int(H * a[i] + 0.5)); t += w[i]; sa += a[i] }
      if (t > MW) { H = ev((MW - G * (k - 1)) / sa)
        while (1) { t = G * (k - 1); for (i = 1; i <= k; i++) { w[i] = ev(H * a[i]); t += w[i] }
                    if (t <= MW || H <= 2) break; H -= 2 } }
      printf "%d %d", H, t % 2; for (i = 1; i <= k; i++) printf " %d", w[i]; for (i = 1; i <= k; i++) printf " %s", m[i]; print "" }')
  set -- $L; local H=$1 EXT=$2; shift 2; local PW=("${@:1:K}") MX=("${@:K+1:K}")
  local FC="" IN="" X=0 PR SC
  for i in $(seq 0 $((K - 1))); do
    PR=$G; [ $i -eq $((K - 1)) ] && PR=$EXT
    SC="scale=${PW[$i]}:${H}:flags=bicubic"; [ "${MX[$i]}" != none ] && SC+=":in_color_matrix=${MX[$i]}:out_color_matrix=bt709"
    FC+="[$i:v]setpts=PTS-STARTPTS,fps=${FPS},${SC}:out_range=tv,setsar=1,format=yuv420p,"
    FC+="tpad=stop_mode=clone:stop=$((N + 2)),trim=end_frame=${N},settb=${FPS#*/}/${FPS%/*},setpts=N"
    [ "$PR" -gt 0 ] && FC+=",pad=iw+${PR}:ih:0:0:black"
    FC+="[p$i];"; IN+="[p$i]"
  done
  FC+="${IN}hstack=inputs=${K},pad=iw:ih+${BAND}:0:${BAND}:black,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709"
  for i in $(seq 0 $((K - 1))); do
    printf '%s' "${LABS[$i]}" > "$T/l$i.txt"
    FC+=",drawtext=fontfile='${FONT}':textfile='$T/l$i.txt':expansion=none:fontsize=${FS}:fontcolor=white"
    FC+=":x=${X}+(${PW[$i]}-text_w)/2:y=54-max_glyph_a"
    X=$((X + PW[i] + G))
  done
  local ARGS=(); for f in "${FILES[@]}"; do ARGS+=(-i "$f"); done
  ffmpeg -v error -y "${ARGS[@]}" -i "$AUD" -filter_complex "${FC}[v]" -map '[v]' -map "${K}:a:0?" \
    -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 \
    -color_trc bt709 -color_range tv -fps_mode passthrough -c:a copy -movflags +faststart "$OUT"
  local rc=$?; rm -rf "$T"; return $rc
}
S=$(basename "$W")
cmp_panels out/${S}_v1_compare.mp4 out/${S}_v1.mp4 ref/ref.mp4 Original out/${S}_v1.mp4 Ours
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,nb_read_frames -of compact=p=0 out/${S}_v1_compare.mp4
```

After rendering, check that the comparison's frame count equals its declared master target. On the unchanged-grid path that also equals the reference's count. Explicitly changed timing uses the mapped-evidence path above.

### 3.4 Triptych: "Original | Genjutsu | Ours" (when an aligned exact comparison applies)

Use this only where the source, model result and final have a verified timeline mapping; Genjutsu use alone does not require it for REMIX. The middle panel is the **raw Genjutsu output** on that timeline: ungraded, no text, no code
layers, so the viewer sees what the model did and what code added.

- **One full-length take:** the take itself, at its own aspect (a 4:3 take shows whole); a short
  tail holds its last frame.
- **Per-cut or per-part jobs:** place each raw output at its cut with the same frame mapping
  `assemble.py` uses. Cuts that no Genjutsu job produced show black, so the panel never passes off
  original pixels as model output. Say in the delivery message which cuts were Genjutsu.

```
python3 $RR/compare.py triptych $W --b out/genjutsu_raw.mp4 --c out/<slug>_vN.mp4 --out out/<slug>_vN_triptych.mp4
```

- `--a` defaults to `ref/ref.mp4`. The layout is the same as in §3.3, and ours (`--c`) is the master.
- **Audio:** the triptych takes it from the reference by default (`--audio a`). When our film
  carries a new mix (user track or recorded stock/library SFX), pass `--audio ours` so the triptych plays
  what we deliver.
- Fallback:
  `cmp_panels out/${S}_v1_triptych.mp4 ref/ref.mp4 ref/ref.mp4 Original out/genjutsu_raw.mp4 Genjutsu out/${S}_v1.mp4 Ours`.
  The 2nd argument is the audio source.

### 3.5 Spend report

From `python3 $RR/ledger.py summary $W` (see `references/budget.md` §8.3; the ledger is
`plan/ledger.json`). Before writing it:

- reconcile charges with `transactions` (match by model, time and amount). Expect foreign charges:
  during the 2026-10-08 test run (111.12 cr, reconciled exactly) another chat on the same account
  spent 496 cr on 8 Nano Banana 2 and 8 Seedance jobs in the same minutes (VERIFIED live). Count only
  the job ids in `plan/ledger.json`;
- call `balance`.

The report shows:

| Item (cuts)                  | Model · settings           | Quoted    | Charged   | Generated s | On screen s      | Status         |
| ---------------------------- | -------------------------- | --------- | --------- | ----------- | ---------------- | -------------- |
| Identity sheet               | seedream_v5_pro 2k         | 2.5       | 2.5       | —           | used in 4 plates | used           |
| Plate A (c01–c09)            | seedance_2_5 omni 720p     | 70        | 70        | 10          | 4.6              | used           |
| Re-roll c07 (identity drift) | seedance_2_5 omni 720p 4 s | 28        | 28        | 4           | 0.8              | used           |
| **Total**                    |                            | **100.5** | **100.5** | 14          | 5.4              | approved 214.5 |

Then one line each:

- credits per final second (charged ÷ seconds of the final). The 2026-10-08 Katana remake: quoted
  83.12 = charged 83.12, 71.12 cr of it used in the final, 7.9 cr per final second, against ~120
  for the original Katana project (VERIFIED live);
- utilisation (on-screen ÷ generated seconds) for **Seedance plates only**, against their 1.5–2.5×
  target. Genjutsu lines are listed as "fixed input (min-billed)" with no target: a 4.00 s pad for
  a 1 s cut is the minimum, not waste;
- waste, by line and reason (e.g. "plate B: 6 of 10 s unused, the gesture ran 2× slower than
  prompted");
- re-rolls, each with its fail-list reason, and any unplanned spend (`guard --next` submissions,
  with their reasons);
- refunds: say "blocked jobs were refunded automatically on this account (verified); confirmed in
  transactions" only after you found each `refund` transaction; name them with the time they cost,
  not as spend. Without the refund line, write "refund pending, not yet in transactions";
- balance before and after.

"Charged" comes from transactions, never from the quote. If reconciliation was not possible, write
"charged: not reconciled" instead of copying the quote.

### 3.6 Adaptations and unresolved limitations

For REMIX, briefly state the authored changes that matter (new story/scenes/order/format/text/music), then separately list unmet explicit locks or remaining production defects. Do not label every intentional difference "not 1:1" or apologize for fulfilling creative freedoms. For EXACT, retain a concise "Not 1:1" list of real source deviations. Never claim exact match from a similarity score or successful encoder exit.

The following are historical EXACT/adaptation limitation examples, not constraints on default REMIX:

Short and honest. For each item: what, where (the shot in words, with its cut id or time for the
overview sheet), why, and what fixing it would take (0 cr code / ~N cr / not possible). Typical lines
from past projects:

- "c06: the T of NINETY sits behind the new head on mid frames, so it reads NINE,Y. The new head is in
  a different place than the original actor's. Fix: move the word in code, 0 cr, but then it is no
  longer at the reference's position."
- "Every swapped cut wears the clothes from your photo; replace copies the photo's wardrobe (seen
  again in the 2026-10-08 Altman test). Fix: a photo in neutral clothing and a new swap, ~N cr."
- "Slow-motion cuts c08, c19 step at 24 fps where the reference is smooth 60p. Partly fixable in
  code: blend the two neighbouring generated frames by the fractional index (0.3–1×), 0 cr."
- "The two fastest shots, the punch (c02) and the sprint (c12), move at 24 images per second where the
  reference shows 60: the swap model takes 24 fps input, so some in-between images are gone. Not
  fixable in code; recorded in the fidelity limitations."
- "Your track instead of the reference's: the reference's music hides a jump at ~12.4 s that the cuts
  follow; your requested track changes the synchronization while the original cut timing remains."
- Historical explicit format-change example only: "4:3 instead of the reference's 5:4, as
  requested in that project." Never infer or attribute that choice to the current user; otherwise
  in EXACT keep the source aspect unless changed; in REMIX record the autonomously authored output aspect honestly, without attributing it to a user request they never made.
- "Lip-sync is approximate; the words on the face cover it."
- "The original song is retained; the added effect uses the recorded asset listed in the handoff." Never substitute code-built music or TTS for singing.

### 3.7 State for revisions

`<slug>_vN_state.tar.gz` (made with `rr_save '<url>' '<content_type>'`, uploaded as a general file;
`references/sandbox.md` §9) holds the whole workspace minus big caches and frame dumps: breakdown,
plans, EDL, `plan/ledger.json`, prompts, HANDOFF.md, PROMPTS.md.

- Give the user its permanent URL.
- In a new chat, revisions start with `source "$HF_WORKFLOWS/katana/scripts/rr.sh"` and
  `rr_restore <slug> '<state url>'` (SKILL.md, “Assemble, verify and deliver”), then `rr_rebuild` if it lists pending frame
  folders. Text, timing, colour and density changes then need no new generations.
- Generated videos in `gen/` stay in the tar (`rr_save` keeps every `.mp4` under `RR_SAVE_MAX_MB`,
  default 150 MB); what it left out is listed in `.rr_excluded.txt`. Anything missing is re-downloaded
  from its Higgsfield result URL, listed in HANDOFF.md.

## 4. Communication rules

- **Language:** the user's language (Russian if they write Russian). Prompts for generators stay in
  English. Comparison labels stay in English unless asked.
- **Progress:** one short line per stage, with what happened, what is next and an ETA for long steps.
  Example: "Анализ готов: 38 склеек, трюк — смена образа на каждом сигнале. Дальше смета." No walls of
  text between stages.
- **Delivery message:** 4–8 lines plus concise spend and mode-appropriate adaptation/limitation notes:
  - what was made, version number;
  - the actual result URLs (film, applicable comparison/evidence, state);
  - what is generated vs code;
  - what was checked, in plain words (frame count, sound, faces, text), and what is still off;
  - what to look at, by shot in words.
- **Never claim acceptance.** Write "v2 готова к просмотру", not "финал" or "принято". The user decides
  what is final. In the handoff, record "delivered v2, no feedback yet" until the user says otherwise.
- **Say what is model-generated and what is code,** per element:
  - footage: "generated with Seedance", "face swapped with Genjutsu", "your clips", "kept from the
    original";
  - text, stickers, doodles, transitions, grade, tracking: code;
  - music/SFX: the reference audio, user track, retained authorized generated audio, or actual stock/library recording, with provenance. Never synthesize a code beat or procedural SFX as a fallback.
- **Report QA truthfully:**
  - list the checks that passed;
  - name anything still off (the NOTE and FIX items) in plain words;
  - state whether audio was actually listened to with a supported tool; otherwise say "measured, not listened";
  - never write "checked" for a check you did not run.
- **Lyrics belong in the requested video:** preserve supplied/source words in timed local data and render them in the final deterministic text pass. Do not paste full lyrics into chat unprompted or send them to the video generator; this is not a ban on using user-provided lyrics or transcribing user-supplied audio. Do not retrieve full protected song lyrics from elsewhere. Show prompts in chat only when asked or in the handoff.
- **People and stylized references:** celebrity edits may use supported Genjutsu operations.
  Anime/stylized identity replacement may instead use source frame + user character/photo in an
  available image generator, followed by still/code rendering, Seedance 2.5 animation or supported
  Genjutsu motion according to fidelity. Never require a Styles preset or impose a blanket category
  ban. Fresh video generation uses Seedance 2.5 only. Respect actual service restrictions without
  circumvention; describe generated/edited media accurately and never present invented footage
  as authentic archival evidence. Source reuse does not itself authorize publishing.
- **Questions and confirmations:** none, including credits. Do not ask for uploads, fonts,
  preferences, variant picks, consent or budget approval. Continue automatically under verified
  task/account authority and the finite internal cap. If a service requires unavailable interactive
  consent, use an existing supported authorized fallback or state a blocked/partial result. Never
  start a user-waiting state, open a picker or count ledger registration as authority. Outside the
  cap, use a free fallback or an honest partial result without requesting an increase.
- **Plain words, not pipeline words.** The user is not an engineer. Never put internal terms in a
  user message: canary, plate, pad, route names (KEEP, SWAP...), `ip_detected`, guard, gate numbers,
  dB, script or tool names, model ids such as `seedance_2_5` (the model's name, "Seedance", is
  fine when you say what was generated). Say "a first test clip", "the generated background
  footage", "the film was refused as copyrighted footage", "kept from the original". Describe shots
  in words ("the close-up of her eyes", "the back view on the stairs"). When a cut id is
  unavoidable, show the labelled overview sheet with it: upload `sheets/overview_p01.jpg` (one image
  per overview page; tiles read `c03 f120-151`) as an image (a slot in the stage's `media_upload`
  call, `rr_put`, `media_confirm(type: image)`) so "c07" can be found at a glance.

## 5. Handoff: HANDOFF.md + PROMPTS.md + job ids

Write both files into `$W` at every delivery, so they ride in the state tar. Then print the job id
table in the chat as well: the sandbox is wiped constantly, so the conversation is the backup copy.
They follow the Katana and Yaong handoffs, which let a new chat continue without regenerating
anything. Prose is in the user's language; prompts stay verbatim in English.

### 5.1 HANDOFF.md

```
# <Project> — handoff for the next chat

> For Claude in a new chat: read this file fully, then PROMPTS.md. Resume the workspace with
> `source "$HF_WORKFLOWS/katana/scripts/rr.sh"` and `rr_restore <slug> '<state url>'`. Talk to the user in
> <language>, briefly.

## 1. What this is
Reference (<link>, <W×H>, <fps>, <N frames = S s>), what the user asked for (quote them), the hero /
character / product, source trick, task mode/reason, explicit locks and authored REMIX premise when applicable.

## 2. Current state
| Version | File / media id / URL | Frames · fps · size | Audio | What changed |
|---|---|---|---|---|
Feedback status: "<v2 delivered on <date>, no feedback yet>" (never "accepted" unless the user said so).

## 3. User decisions (do not revisit without a request)
Explicit locks and user decisions with their actual words; separately record autonomous creative choices and output target. Never present an inferred REMIX decision or internal spending ceiling as user approval. Preserve the saved task contract on continuation unless the latest user steering changes it.

## 4. Reference breakdown (short)
Trick line, structure by section, meaning mapping (which graphic means what, what replaced it),
transitions that hide cuts, cadence, look class. Full detail: analysis/breakdown.json.

## 5. Pipeline as executed
Routing per cut (counts per route and the cut ids), models and settings per job group, renderer
(assemble.py / comp/render.py) and its plan file, grading and audio choices.

## 6. How to resume and re-render
Exact sandbox commands: the rr.sh source line, rr_restore <slug> '<state url>' (+ rr_rebuild), re-download any generated media .rr_excluded.txt lists (list below),
render, gate, upload. Typical revision cost: 0 credits.

## 7. Files in the workspace
analysis/task-contract.json, analysis/breakdown.json, analysis/coverage.json, plan/creative-plan.json, plan/gen_plan.json, plan/ledger.json, comp/edl.json or plan/renders.json,
comp/fx.js, qa/gate_vN.md, ...

## 8. Higgsfield ids
| What | Job / media id | Result URL | Used in |
|---|---|---|---|
Reference upload, identity anchor, stills, plates, Genjutsu takes, mattes, voice, finals, state
archives (`<slug>_vN_state.tar.gz`).

## 9. Timing
Beat grid t(b) = phase + b × period, sections, and per plate the moments found on its catalog sheet
with source seconds (the in-points the EDL uses).

## 10. Gotchas met in this project
Model quirks, moderation wording, preset bounces, matte fixes, anything that cost time.

## 11. Authored adaptations and limitations
The mode-appropriate §3.6 list; deliberate REMIX choices separate from unmet locks/defects.

## 12. Spend
The §3.5 table and lines.

## 13. Remaining limitations
Record any unresolved difference and why the existing inputs, capabilities or internal hard cap prevent
completion. Do not add redesign ideas, questions, credit confirmation requests or pending-user
steps; state any unresolved service permission as a blocked/partial limitation.
```

### 5.2 PROMPTS.md

One section per job group, in the order the jobs ran:

- **Header:** model, mode and every parameter that matters (resolution, duration, aspect,
  `generate_audio`, bitrate, `declined_preset_id`), the media refs and their roles (`@image1` = …),
  and the count.
- **The prompt,** verbatim, in one fenced block.
- **Result:** job id(s), status, which cuts use it, or "unused" and why.
- **For still variants:** record the closest-reference variant selected automatically and the measured reason;
  retain any explicit user choice already present in the conversation.
- **Failed or rejected requests:** the prompt diff and the status (`nsfw`, `ip_detected`, preset
  bounce; blocked jobs were refunded automatically on this account (verified), confirm each in
  `transactions`), plus what changed in the version that passed. Yaong kept its 4 nsfw prompts with "do not
  repeat with an audio reference".
- **Plate catalogue timings:** where each gesture really is in each plate (Yaong logged them
  per plate in seconds), because the prompt's timecodes were not followed.

### 5.3 Job id table

Paste the output of `python3 $RR/ledger.py summary $W`: job id, model, settings, billed seconds,
quoted, charged, status, seconds on screen, used in. Put it in HANDOFF.md §8/§12 and in the chat
message. It is the only way the next session can find what was paid for.

## Font QA without an intake gate

In EXACT or locked/reused text, confirm original shapes, placement and animation. For authored REMIX or changed words, verify actual font loading, script coverage, glyph bounds, spacing, weight and effects against the authored typography design and its viewed reference evidence. Missing exact font assets never create a user question or stop the whole edit: choose the closest measured and actually loaded match, tune glyph geometry and list a material visual difference in the final report. Do not accept blind Arial/Inter/browser fallback or a canned glitch treatment; preserve exact typography locks or deliberately realize the authored REMIX design. Do not demand a font file, font name, link or license document from the user.
