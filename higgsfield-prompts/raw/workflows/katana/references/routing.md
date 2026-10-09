# Routing: where every output shot comes from

Read `analysis/task-contract.json` first. **REMIX is the default** for a new independent deliverable,
including a bare “remake” or “same vibe/style”: preserve explicit locks, the intended user identity and
the selected reference visual grammar while authoring the story, scenes, text, framing and length.
**EXACT** applies when the current request actually asks for 1:1, the same edit, only a subject replacement
or equivalent preservation. Negated/quoted examples are not toggles. The latest actual user steering
wins; a continuation keeps its selected mode. Scope-specific exact locks can exist inside REMIX.
EXACT preserves source duration, frame grid, fps, aspect, dimensions, subjects, appearance, text and
audio except explicitly changed elements. Choose the highest-fidelity route to the selected contract within authorized account resources and the bounded
execution cap; cost breaks ties between equivalent results. Reuse authorized source assets where useful,
but do not return the input unchanged and call it a new remake. Never ask questions, request approvals,
open consent pickers or wait for a user choice. Apply `references/budget.md` §8: compute a finite
live-priced plan under existing task/account authority; a numeric user budget is optional. If a service
requires interactive consent, use an already-authorized supported alternative or deliver a truthful
partial with a declarative limitation. Never bypass the service restriction.

**Inputs:**

- `analysis/task-contract.json`: `mode`, `mode_reason`, `explicit_locks`, `creative_freedoms`;
- `plan/creative-plan.json`: authored `output_target`, story or visual motif, output shot roles and `source_evidence`;
- `analysis/analysis.json` plus the per-cut breakdown (see `references/analysis.md`);
- the reference media, supplied assets and existing explicit changes; infer missing decisions from
  the reference and context without asking.

**Output:** `plan/routes.json` (shape in §5). Its jobs fill `plan/gen_plan.json`, which `ledger.py quote` prices.

**Where the rest lives:**

- model params and prompts for each route: `references/generation.md`;
- prices, sizing, resolution, the canary and the quote format: `references/budget.md`;
- what code does with the result: `references/compositing.md`.

Read these bundled files locally. At execution, discover available capabilities and verify their current
contracts; historical model ids and parameters below are evidence, not universal callable interfaces.

Status labels used below:

- **PROVEN** means a project shipped or got approval with it, and the project is named.
- **WORKED** means the generation itself was usable, but the film it went into was not accepted, or its
  acceptance is unknown.
- **VERIFIED (live 2026-10-08)** means it was measured in the paid test run of that day (111.12 cr,
  reconciled exactly with `transactions`; `references/budget.md` §10, "Measured run").
- **UNTESTED** means it is reasoned from the evidence and has never been run.

---

## Required video-engine policy

Fresh video generation, missing plates, previews, extensions and retries use only `seedance_2_5`. Genjutsu source-video transformations and suitable verified Genjutsu presets are optional exceptions, never mandatory for anime; still-image and masking tools remain separate. Read [genjutsu-routing.md](genjutsu-routing.md) for public-figure and anime branches. Famous identities are not categorically banned. No name obfuscation or model switching to defeat a content refusal is permitted. No branch introduces questions or approval gates.

Genjutsu prompt fields stay short: one sentence normally, at most two / 40 words. Keep the full frame-by-frame analysis and effects inventory in the plan, not the prompt; use the actual reference images/video to carry appearance and motion. Image-generation and Seedance prompts follow their own requirements.

**No code-based face changes.** Identity replacement, facial expression/feature changes and repair of
a generated face must use a supported authorized image-editing operation, the appropriate Genjutsu
transformation or Seedance 2.5 new footage. CODE never performs face swapping, landmark/mesh warping,
face-part pasting, identity blending, skin retouching, face painting or face-only grading/relighting.
Tracking, whole-frame/unaltered-subject-layer movement, outer matte-edge cleanup, whole-shot grades
and separate graphic overlays (measured source layers in EXACT, authored layers in REMIX) remain
compositing operations; they cannot alter the underlying face.
`STILL/CODE` means model-produced or already suitable imagery followed by that permitted composition,
never a cheaper local face replacement. If a required model route cannot run, report the actual gap
without inventing a code fallback or asking a question.

## 1. Reference families

Classify the reference's visual grammar after full analysis, then route the authored output. Family
selection never overrides explicit locks or the user's intended identity. In EXACT, F1 replacement
branches activate only for an explicitly supplied identity/world change and F2 preserves the reference
performer and look. The detailed F1–F7 preservation pipelines below describe **EXACT or an exact-locked
scope**; REMIX uses the following role-based adaptation before the technical router in §2. Mixed references
can combine families. The per-output-shot router then
overrides it cut by cut, because mixed references are common: Altman was a film montage with banknote
inserts and helmet shots, and Aura G was a car show where no person performs.

### REMIX: author roles, then choose sources

Keep measured source observations in `analysis/breakdown.json`; never overwrite them with invented
scenes. In `plan/creative-plan.json`, choose a story or visual motif and an output target that fit the
brief, then give each output shot an ID, role, required action/state change, intended screen duration,
identity/prop/location needs, relevant locks and source evidence. Useful roles include hook, context,
hero, action, detail, contrast, payoff and release; choose only roles the piece needs, with no fixed
shot count or mandatory narrative arc. A role describes why a shot belongs, not a copied camera setup.

Prefer a predominantly usable-footage pipeline: inspect the user's footage and authorized matching
source/library material first, prepare images only for missing identity/composition/asset needs, then
use Seedance 2.5 for missing new scenes. This is a practical preference, not a quota that prevents an
explicitly requested all-generated video or sacrifices the story. A portrait alone may require more
generation. Do not return the original unchanged as the remix.

| Reference family                  | REMIX adaptation                                                                                                                                                                                                                                                                                                                                            |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F1 / F2 people and styled montage | Use the intended user hero and selected graphic/lighting/rhythm grammar in a new sequence. Existing suitable footage, image preparation and Seedance are the normal mix. Use SWAP only for a selected local replacement; use REPERFORM only when that shot specifically needs the source motion/camera choreography. A new world alone does not require MT. |
| F3 real events / people           | Reorder authorized genuine footage around the new semantic idea and write appropriate new text. Preserve truthful provenance, explicit subject locks and source credits; generated illustration must never pretend to document a real event.                                                                                                                |
| F4 user footage                   | Build the new sequence from the strongest suitable moments; generate only genuinely missing role coverage. Availability does not justify irrelevant shots.                                                                                                                                                                                                  |
| F5 still / stop-motion            | Author the selected visual cadence with suitable existing/prepared stills and whole-layer composition. Video generation is conditional on needed continuous motion.                                                                                                                                                                                         |
| F6 motion graphics                | Author the new message and animation using the selected reference typography/texture grammar and explicit locks; choose fonts internally.                                                                                                                                                                                                                   |
| F7 product                        | Use supplied usable product footage/images, necessary product/location preparation and Seedance for missing motion. Local object replacement is optional when the selected source shot itself is wanted.                                                                                                                                                    |

Prepare reusable hero, location or prop assets only if multiple planned slots need stable details
that the available inputs cannot already supply. Record the served output IDs and the ownership of
each reference: identity, wardrobe if locked, location geometry/materials, prop design, or selected
style. A location plate does not implicitly own shot lighting or camera position; assign those in the
shot plan unless locked. No mandatory character sheet, neutral studio, number of locations or extra
asset stage. Never erase, paint over or alter faces/heads with code to make a sheet; a necessary model-generated body reference remains a permitted image operation. See `generation.md` for
optional causal prompt fields and image ownership.

### F1. Explicit identity or world replacement inside the reference footage

**Recognition cues in the breakdown**

- A human performer drives most cuts: `main_person_present` on most cuts.
- The user wants themselves or a character to replace that performer.
- The rest of the plate is the point: the window and frame, baked kinetic text, the film grade, PIP
  cards, the watermark. Typical sources are movie-clip montages, motivational reels, aura edits with a
  performer, and dance or sport clips.
- Text is often baked into the plate, sometimes behind the performer's head.

**Pipeline**

Choose sub-case F1a or F1b:

- **F1a, keep the ref's world** (Altman):
  1. Replace the requested subject in every shot where that subject appears, including back views,
     silhouettes, helmets, crops, hands, occlusions and distant shots. Establish subject continuity
     across cuts first (§2.2). Use source-frame + uploaded-identity preparation where needed; select
     SWAP, STILL/CODE or Seedance 2.5 according to the actual shot and verified operation. A hidden
     face never excludes the cut from the replacement plan. Submit jobs serially after the applicable canary.
  2. KEEP untargeted source layers or unrelated B-roll only when reuse fits the requested scope and
     has a recorded per-cut reason. Do not leave the original targeted performer unchanged because
     no face is readable, or silently KEEP a cut covered by a request to regenerate the full video.
  3. Use REPERFORM only when the requested change actually transfers motion. A content rejection is not a routing trigger: retain allowed source material or report the unresolved cut. Confirm refunds before recording them.
  4. Rebuild text from the reference's pixels on the MT cuts.
  5. Do a frame-exact reassembly.
- **F1b, move the hero into a new world** (Aura D/G/H):
  1. Prepare the intended world/identity in the image reference, then REPERFORM the muted source with MT and a short operation/preservation prompt (one sentence normally, at most two / 40 words). Let the media carry scene details.
  2. Run one full-length take for refs up to about 11 s without burned graphics. Otherwise split into
     parts at the ref's own cuts; each part pays its own rounding (§3.2).
  3. Use one take; include a second only when required reference coverage and the bounded execution
     cap support it. No optional-take menu (`references/budget.md` §6.1).
  4. Every effect, word and grade is done in code. Words behind the hero use a matte.

**Proof**

- **PROVEN F1a: Altman v3.** The user called it "финалку": 12 replace renders, 5 MT renders and 4
  original cuts.
- **VERIFIED (live 2026-10-08), one F1a cut end to end:** c12 exported at 24 fps and ping-pong padded
  to exactly 96 frames, replace at 720p charged exactly 28, the 89-frame output mapped back
  proportionally, `assemble.py --control` passed on all 21 cuts, and the baked words, the watermark and
  the audio (MD5-equal) were preserved.
- **PROVEN F1b: Aura.** 04 Alex Dark v2, 07 Showpiece v4 and 08 Polarity v9 were all approved. In all
  three, MT was the main source.

**Unproven**

- **A whole-reel pass** for a window-in-canvas montage: one replace, or one `seedance_2_5` video_edit.
  - It is untested and excluded by default. Run only an already explicitly requested experiment
    compatible with verified tool contracts and the bounded cap; do not offer it as a choice.
  - For Altman that is ceil(14.37) = 15 s × 3 = 45, while a shippable pass would be 15 × 7 = 105 @720p.
  - It competes with the per-cut plan: 352 @720p / 544 @1080p, or 380 / 588 with c21 swapped (§4.1).
  - The risk is that one IP-flagged scene blocks the whole reel (`references/budget.md` §4.7).
- Whether a replace prompt can keep the reference's wardrobe. In Altman, every replace output wore the
  photo's grey crewneck, and the 2026-10-08 run again dressed the hero in the photo's wardrobe
  (VERIFIED). Use the closest suitable supplied frame/photo; if none works, select a permitted
  route that preserves wardrobe or report the limitation without requesting a new image.
- A one-take MT for refs over 11 s.
- Grouping adjacent same-scene short cuts into one Genjutsu input. Never do it just to improve the
  utilisation ratio (§2.7).

### F2. Reference performer and world with styled overlays

**Recognition cues**

- One or two performers on a plain or high-key set: white cyclorama, white room, backstage.
- The footage itself is generic: dance, poses, gestures, close-ups, eye ECUs.
- The identity of the edit comes from overlays: stickers, doodles, pen contours, cut-outs with halos,
  graffiti or kinetic type, flashes, a xerox or duotone grade, a frame border.
- Preserve the reference performer, world and styling. A supplied replacement changes only the
  specifically requested attributes; never infer a recast from the presence of overlays.

**Pipeline**

1. Reuse a suitable reference frame or supplied matching anchor. Create one anchor only if technically
   required and authorized; preserve the observed subject. An explicitly requested new fictional
   subject may use one generated still, selected internally without presenting character choices.
2. Build only the necessary Seedance 2.5 `omni_reference` plates using the reference
   set, lighting, motion and framing; use a clean matte background only for elements composited back into
   that exact set. Use
   `generate_audio:false`, `bitrate_mode:"high"` (both written on the plan line) and no audio refs.
   - Each plate is sized as Σ slots (§3.1). A reference whose cuts repeat a few beat types may need only
     one: the 10.5 s Katana reference (26–30 cuts) was rebuilt from one 10 s plate (VERIFIED live
     2026-10-08).
   - A planned plate covering the family's hardest fidelity constraints is its canary.
   - At most one justified bounded re-roll per failed job; never add take-selection choices.
   - Only the hero's identity goes into a plate whose shots will be cropped to identity-legible
     close-ups. A second person (Yaong's friend) gets generated only for a shot that keeps her in the
     final framing (§2.5).
3. Use per-cut G8 clips whenever source-aligned new motion preserves the actual shot more faithfully
   than a shared plate or deterministic animation, including sub-second cuts. Satisfy the live model's
   minimum job duration while retaining the exact source interval in the edit; never drop a brief shot
   for billing efficiency.
4. Order mattes only for the clips the EDL uses for contours, cut-outs or behind-subject graphics.
5. A canvas compositor rebuilds every graphic, transition and grade.

**Proof**

- **PROVEN-ish: Katana v1.** It was implicitly accepted as a concept: the user built v2 on top of it.
  Katana v2 shipped with no verdict recorded.
- **PROVEN-ish: Yaong v2.** It was delivered with no revision requested; acceptance was implicit.
- Both projects did all their revisions in code at 0 cr: Yaong v1→v2, and Katana's 65 QA fixes.
- **VERIFIED (live 2026-10-08):** the 10.5 s Katana reference rebuilt with 1 Soul 2.0 still (0.12) + one
  10 s 720p plate (70) + 1 matte (1) = 71.12 used, 83.12 charged with a 12 cr draft probe: 7.9 cr per
  final second against ~120 in the original project. The five 2 s shots landed on their timecodes. The
  xerox threshold crushed faces on identity-legible medium close-ups. Correct an introduced whole-shot
  grade against the source; never retouch the face locally or paint missing facial detail.

**Unproven**

- 1 take per plate plus shot re-rolls, instead of Katana's two identical takes. This is the main saving
  in this family and has no controlled test.
- A `draft:true` plate finalized at 1080p. Its prices are VERIFIED (draft 4 s = 12, 752×560; the
  finalize is always 1080p at the full 1080p price, so draft + finalize = 1.25× a direct 1080p job;
  `references/budget.md` §2.3), but the finalize's fidelity to the draft is UNTESTED and it is excluded
  by default.
- 720p plates plus `bytedance_video_upscale` (excluded by default).
- A sticker sheet sliced by alpha.

### F3. Montage of real events or real people (sport, news, archival, culture B-roll)

**Recognition cues**

- Many unrelated sources, archival or broadcast look.
- Real public figures, real places, culture B-roll.
- A watermark or credit from the montage editor.
- Cuts are driven by music or vocals, not by one performer.

**Pipeline**

1. Preserve the reference subject, events, shot content, timing and audio. Use authorized reference
   elements, supplied source footage or existing licensed footage; do not replace a required event
   with a generic illustrative shot or fabricate archival moments.
2. KEEP may preserve actual reference elements when the task and available rights authorize reuse.
   Rebuild the edit and disclose reused elements. Passing through the whole original is not a remake.
   Preserve source watermarks and credits in reused footage.
3. CODE reconstructs the observed grade, transitions, type and sound treatment. Do not add an end card,
   new handle, new soundtrack or revised meaning unless explicitly requested.
4. If replacement footage is necessary, search and select the closest authorized source independently.
   Record provenance and why it matches the slot; do not wait for a sourcing-list choice. A missing
   exact source remains a stated limitation, not a license to invent an event.
5. Generation is eligible only for an actual reference element that existing footage/code cannot
   supply, inside the verified tool contract and bounded cap. Never create deceptive archival scenes.
6. Only an explicit subject-change request permits remapping the meaning layer; otherwise preserve
   the same subject and screen-time allocation. No intake questions or audio/generation menus.

**Proof**

- Brazil spent 0 cr. The user answered "только реальное" (only real footage). It got to draft v1 only and
  was never accepted.
- Its waste was agent tokens and wall clock (≈3 h, >4 M tokens), not credits.
- The Brazil dry-run eval (2026-10-08) for a requested subject-change version it kept 22 cuts of the editor's
  footage and cropped his watermark away with a 1.05× punch-in, put 140 cr of AI B-roll into the planned
  total, and gave Messi ~6 s of 28 (`references/budget.md` §9 #32).

**Unproven**

- Generated B-roll gap fillers matching a sepia-grain look.
- yt-dlp search inside the Higgsfield sandbox; verify availability before relying on it.
- Any public footage library for end users. Aura's "Higgsfield IG library" was a local index on that
  team's machine and is not available here.

### F4. Remake from the user's own footage

**Recognition cues**

- The user says they have clips, or attaches them.
- The ref's hero is a character the user owns footage of: fan edits, their own vlog, their own product
  shots.

**Pipeline**

- 0 generation.
- Reconstruct only the source's measured crops, retiming, punches, shakes, whips, flashes, grade and
  typography in code. Match their exact frames, trajectories and intensity; never add a canned glitch,
  shake, RGB split or flash to make an otherwise mismatched shot look edited.
- Transcribe the hero's real lines (faster_whisper in the sandbox) for captions.
- One source take often yields 2–6 cuts through different crops and zooms.

**Proof**

- **PROVEN: ref-match-edit, Maddy v5.** It was accepted: 27 shots from 2 user files, 0 cr.

**Unproven**: nothing specific. Choose this branch only when the supplied footage actually matches
the reference or a requested replacement; availability alone does not justify changed shots.

### F5. Photo series or stop-motion

**Recognition cues**

- A locked camera.
- Every 1–2 frames a different still: objects, vehicles or people change while the base shot stays.
- Little or no motion inside a shot.
- Held frames: mpdecimate drops many frames, or the cadence is far below the container fps.
- Examples: jewellery stop-motion, City Rhythm (a locked highway, ramp and facade with a new detail every
  1–2 frames).

**Pipeline**

- Stills, not video.
- One base image per series, then cheap image edits per frame, assembled in code with the
  reference's hold pattern.
- Code adds any push or zoom.

**Proof: NONE.**

- City Rhythm as video (v7) was rejected: "вообще не то". The photo-series fix was proposed, never run
  and never priced.
- The proposed form, about 250 Ideogram 4.5 edits, would cost 250 × 6.25 = 1,562.5 cr. That is not
  cheap.

**UNTESTED plan**

- First complete the source analysis and live-price the required series and bounded reserve: N unique
  frames × the actual unit quote, after identifying faithful frame reuse. Register the finite cap before
  any generation. Historical arithmetic for 250 frames was 250 × 0.5 = 125 with `seedream_5_0_flash`,
  or 250 × 1.5 = 375 with `nano_banana_2` 1k; these are not current quotes.
- Submit one planned representative still at final settings as the canary. Inspect it before the
  remaining required stills; do not add a five-image exploratory batch.
- The "stills over 10% of the quote" warning does not apply when stills are the plan
  (`references/budget.md` §3 rung 2).

### F6. Pure motion graphics or typography

**Recognition cues**

- No camera footage, or only solid or gradient fields.
- Kinetic type, shapes, UI, counters, line art.
- Every analysed cut has a near-flat colour histogram and no face.

**Pipeline**: CODE only, 0 generation credits. Preserve original text pixels where wording is unchanged; otherwise select installed or verified openly licensed fonts autonomously. Never request font files, names or links from the user. An unavailable exact typeface is a documented visual approximation, not a blocker.

**Proof**

- Partial. Every project drew its text, flashes, frames and doodles in code: the Katana graffiti engine,
  the Yaong typewriter and starburst, the Brazil cards.
- No whole reference of this kind has been run end to end. **UNTESTED as a full project.**

### F7. Product or object swap

**Recognition cues**

- The hero of the cut is an object: a product in hands, a packshot, a car, a bottle.
- The user wants their product in its place.

**Pipeline**

- **Same-class swaps (bottle→bottle, shoe→shoe):** SWAP with `hf_mult_replace_object` and product photos
  as the image. Run a canary first. This is UNTESTED in these projects, and account history shows 7 of
  18 Object Swap jobs failed (refunded).
- **Product inserts that need no new continuous motion:** reuse a suitable image or prepare a
  source-frame + product-reference STILL, preserving the measured scene, light, scale and perspective.
  Use it directly with deterministic timing/compositing. A white isolation background is conditional
  on an exact source-scene restoration plan. Add Seedance 2.5 only if the measured shot actually needs
  new motion; neither a new still nor a video job is automatic. This product route is UNTESTED here.
- **Class changes (car→person, lamp post→person):** never SWAP.
  - Aura G spent 209 cr: "the car stayed, badges leaked".
  - Aura E failed too: the lamp post was not removed.
  - When a performer's camera choreography matters, REPERFORM with a person. Aura G v4 was accepted
    with MT re-performing the car-show camera moves with Alex in a hangar.

**Proof**: only the negative results above. Always canary.

---

## 2. Per-output-shot router

In REMIX, run this router on every output shot in `plan/creative-plan.json`; source cut IDs are
evidence or selected input intervals, not the output EDL. In EXACT, run it on every source cut.
First mark the intended hero and any requested replacement subject across
all appearances using adjacent-shot continuity, including shots with no readable face. Also mark each
cut covered by an explicit full-regeneration request. These cuts cannot take KEEP merely because they
are difficult, small or faceless. Then choose the first faithful technical route below. A lower price
never makes a mismatched route acceptable; every cut records its scope and route reason.

| #   | Test (from output plan and relevant source evidence)                                                                                                          | Route                                                                                                                                                                                                                                                                                                                                                                                                                    |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0   | Is the cut a solid, flash, black, white, negative, title card, pure type or graphic?                                                                          | **CODE**                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 1   | Is this an untargeted source element or unrelated B-roll whose reuse fits the requested scope, outside any required subject replacement or full regeneration? | **KEEP** only with the per-cut scope reason and provenance recorded; never use face visibility as the reason                                                                                                                                                                                                                                                                                                             |
| 2   | The requested replacement subject appears with no readable face: back view, hood, helmet, mask, silhouette, hands/body crop, occlusion or distance.           | Rebuild the subject for continuity (§2.2): source-frame + uploaded-identity **STILL** through a supported image model, then permitted whole-layer **CODE** composition; **GENERATE** with Seedance 2.5 for required new motion; or suitable verified **SWAP/REPERFORM**. Code never changes a face or creates the replacement identity. Preserve source occlusion and untargeted body/wardrobe/props; no automatic KEEP. |
| 3   | Authorized supplied or independently selected licensed footage covers the output role and locks; in EXACT it must cover the reference shot.                   | **USER-FOOTAGE** / **LIBRARY**                                                                                                                                                                                                                                                                                                                                                                                           |
| 4   | **Class-change test.** The target's class differs from the ref subject's (car/object/animal ↔ person).                                                        | Never SWAP. **REPERFORM** only for specifically required source choreography/camera movement; otherwise suitable existing footage, **STILL** or **GENERATE** for the authored shot.                                                                                                                                                                                                                                      |
| 5   | Anime/stylized reference with a supplied replacement character, where a generated keyframe can preserve the measured source framing/look.                     | **STILL/keyframe** from the original reference frame plus uploaded character photo. Use directly with CODE for still-based edits, or feed Seedance 2.5 for new motion. Choose a verified Genjutsu preset only if it better matches the required transformation; anime alone is not a RESTYLE trigger ([genjutsu-routing.md](genjutsu-routing.md)).                                                                       |
| 6   | Same-class person swap, and the plate, grade or baked text must stay.                                                                                         | **SWAP**                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 7   | The ref's body motion or camera choreography must be re-performed by the hero in a new world.                                                                 | **REPERFORM**                                                                                                                                                                                                                                                                                                                                                                                                            |
| 8   | Locked camera, near-static subject, a held frame or a photo-series beat.                                                                                      | **STILL** with permitted whole-layer/camera composition. EXACT uses measured source motion; REMIX uses authored motion consistent with selected visual grammar and locks. No facial deformation or code expression animation.                                                                                                                                                                                            |
| 9   | A required output role needs new footage that suitable existing footage/stills cannot supply.                                                                 | **GENERATE** with `seedance_2_5` only, within the bounded cap; no alternate video-engine fallback or purchase menu                                                                                                                                                                                                                                                                                                       |

Apply the **text rule** (§2.6), the **length rule** (§2.7) and the **resolution rule** (§2.8) as
modifiers to whichever route wins.

### 2.1 Routes, costs and evidence

Today's prices (2026-10-08). Both video families cost 3 cr/s at 480p; Seedance is 7 / 12 and Genjutsu
7 / 11 at 720p / 1080p. Re-probe with the dedicated cost-estimation tool before quoting (see `references/budget.md` §2.2).

| Route        | What it is                                                                                                             | Cost per cut (720p / 1080p)                                                                                                                        | Evidence                                                                                                                                   |
| ------------ | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| KEEP         | Authorized untargeted elements within the requested reuse scope, frame-exact, with provenance and watermarks preserved | 0                                                                                                                                                  | Historical Altman c04/c11/c18/c20 reused source pixels; this is not a precedent for skipping a targeted subject or full-regeneration cut   |
| CODE         | Canvas/ffmpeg: flashes, type, graphics, grade, camera moves                                                            | 0                                                                                                                                                  | Every project; each revision cost 0 cr                                                                                                     |
| USER-FOOTAGE | User clips, cropped and retimed                                                                                        | 0                                                                                                                                                  | ref-match Maddy v5 (accepted)                                                                                                              |
| LIBRARY      | Authorized supplied or independently selected matching licensed footage                                                | 0 generation cr; verify source authorization                                                                                                       | Brazil draft. Stay conservative: footage from the user, never invent archival moments of real people                                       |
| SWAP         | Genjutsu `hf_mult_replace_object`, person→person, keeps the plate                                                      | **28 / 44** per cut on a 96-frame pad = exactly 4.00 s (12 at 480p). A 4.04 s or 4.17 s input bills 5 s = 35 / 55. +1 if a matte is needed         | Altman: 12 used, text kept on 11 of 12, dedicated estimator 44 per 4 s; 28 charged @720p on a real 96-frame pad (VERIFIED live 2026-10-08) |
| REPERFORM    | Genjutsu `hf_mult_motion_control` (MT)                                                                                 | **7 / 11 cr/s of driving video**. Per cut ≈ 2 (G5 2-ref still) + 28 / 44 + 1 (matte) = **31 / 47**. A full-length take bills round(seconds) × rate | Altman (5 MT cuts), Aura D/G/H (main source)                                                                                               |
| GENERATE     | One shot inside a Seedance 2.5 `omni_reference` multi-shot plate                                                       | **7 / 12 cr/s** of plate. A plate is Σ slots of 2–4 s: a 10 s plate (70 / 120) carries 4–5 shots, ≈ 14–30 per shot. Minimum job 4 s = 28 / 48      | Katana, Yaong; one 10 s 720p plate charged 70 and served a whole 10.5 s rebuild (VERIFIED live 2026-10-08)                                 |
| STILL        | An image model, animated in code                                                                                       | 0.12–2.5 per image                                                                                                                                 | Yaong identity stills; Altman MT stills; Katana stickers                                                                                   |

### 2.2 Subject continuity across every shot

In REMIX these checks cover every appearance in the authored output sequence and all retained or
transformed source intervals containing the target. They do not require reusing every source cut or
the source's screen-time allocation. In EXACT they cover the entire required source sequence. The
source-geometry and wardrobe preservation below applies to a selected local replacement or an exact
lock; other REMIX scenes use their authored shot geometry and wardrobe contract.

Face readability controls how identity is verified, never whether the requested replacement happens.
For a replacement or recast, include every appearance of the targeted subject: back views, helmets,
hoods, silhouettes, body/hand crops, partial occlusions and distant figures. Track the subject using
adjacent cuts, action, spatial position and the source's continuity. Do not label these shots "no person"
or exclude them because eyes, nose and mouth cannot be measured.

For each such cut, record the source frame(s), targeted subject, connected continuity shots, requested
identity, chosen reconstruction route and verification evidence in `plan/routes.json`. Use the original
cut frame plus the uploaded replacement photo through G4 where a prepared frame is needed. A still
with source-matched code animation is valid only when it reproduces the actual motion; otherwise use
Seedance 2.5 or an appropriate verified source-anchored Genjutsu operation. Genjutsu remains optional,
and the short-prompt rule still applies.

Preserve the source's camera, pose, occlusion and visibility: a back view stays a back view, a helmet
stays on, and a silhouette stays a silhouette. Never rotate the subject toward the camera or reveal a
face to prove the swap. Keep body proportions, wardrobe and props unchanged unless the requested
change specifically includes them. Apply the replacement to the targeted subject while retaining all
untargeted people and layers. When no identifying detail is visible, verify the processed shot's role
in the same subject sequence and its matching source geometry; do not invent a visible facial change.

KEEP is available for untargeted source elements and unrelated B-roll when reuse fits the request.
It is not a shortcut for a faceless targeted-subject cut or a cut covered by full regeneration. For an
explicit fully regenerated deliverable, each required output cut has a reconstruction route or a declared
unresolved limitation; any reused element has a specific scope reason. A missing face is never that
reason. If an authorized route cannot complete the cut, report the actual gap rather than silently
passing through the original performer or claiming the replacement is complete. Do not ask a question.

Historical Altman c05 (back/beanie), c13 (hood), c15/c16 (silhouettes) and c21 (boxer from behind) are
continuity shots that belong in a requested replacement plan. c11/c18 (helmeted driver) and c20 (hands)
likewise require subject attribution before routing. Their historical credit costs do not justify omission.

### 2.3 Public figures, famous scenes and anime

Use the required operation, not a blanket famous-person/IP label. Preserve authorized reference footage when it serves the output role. A selected local replacement may use Genjutsu SWAP; a shot requiring particular source motion may use Genjutsu REPERFORM. Neither is the default for a REMIX person shot. Anime can use image generation from the original frame plus the uploaded character reference, followed by CODE or Seedance 2.5 as the shot requires. A verified Genjutsu preset is an optional alternative selected by fidelity, not a required anime stage. Exact inputs and availability checks are in [genjutsu-routing.md](genjutsu-routing.md).

Source tagging supports edit provenance. It does not authorize probing every scene to find a permissive model. A real content rejection must not trigger renaming, identity concealment or transfer of the same refused request to another model. A confirmed technical input failure can be corrected within the attempt/cost ceiling. Otherwise keep supported source portions or report the unresolved cut, with no question. Confirm refunds rather than assuming them.

### 2.4 Class-change test

- `hf_mult_replace_object` failed on every class change:
  - Aura G, car→Alex: 3 jobs, 209 cr. The car stayed and VW badges leaked.
  - Aura E, lamp post→Adil: identity was kept but the post was not removed, and the cyclist stack
    failed.
- A class change is never SWAP. Use REPERFORM when the cut's camera or body choreography is the point:
  Aura G v4 was accepted with MT on the car-show camera moves and Alex in a hangar.
- Otherwise GENERATE a new shot, or use CODE.

### 2.5 Two performers in one cut

Preserve the selected shot's planned cast in REMIX and every source performer in EXACT or a local
replacement. An authored REMIX scene can have a different cast only outside explicit identity/cast locks;
matting or tracking must never accidentally remove a planned person.

- Historical MT runs confused which silhouette was the hero.
  - Aura B: the second person became a faceless white mannequin.
  - Aura A: the roles swapped.
  - Aura B used a long description of the other person. That is historical evidence, not the current
    prompt template. Use source-aligned media and a minimal positional cue, within two sentences / 40
    words; preserve other performers through supported references or verified separate layers.
- Replace accepts "Do not change <named other people>" (Altman's prompt structure).
- Prefer supported SWAP for the requested replacement when it best preserves untouched people.
  A real content refusal follows §2.3; it is not permission to switch models.
- **Generated plates (F2): preserve the source cast.** A plate may isolate one subject only when the
  actual source framing already excludes others or verified separate/source layers preserve them in
  the final shot. Do not introduce a crop to discard a performer. Yaong's historical unused friend
  reference illustrates avoiding unused generation, not permission to alter the source framing.

### 2.6 Text handling (baked text in the reference)

The table covers EXACT and source text explicitly retained in REMIX. In REMIX, new wording is authored
in the creative plan and composed with the selected typographic grammar; source wording is not locked
merely because it exists. Preserve credits/watermarks in reused footage. A local SWAP preserves its
input graphics by default. A planned text change uses supported clean layers and safe composition,
never painting over a face or cropping away an untargeted subject to conceal old lettering.

| Route            | What happens to the ref's baked text                                                                                                                                                                                                                                            | What to do                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| KEEP             | Kept exactly                                                                                                                                                                                                                                                                    | Nothing                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| SWAP             | Kept on **11 of 12** cuts (Altman), including letters behind the hero, PIP cards and the watermark. Failures: one word rendered at about 60% opacity, and a glyph painted onto the new hair (c01). Fades come out 1–2 frames off at 60 fps, because Genjutsu re-renders at 24p. | Run the automatic text check (`textlayers.py`) on every SWAP cut. Re-lay only the words that fail. Do not strip and re-composite text pre-emptively: Altman proved it unnecessary.                                                                                                                                                                                                                                                                                                                                                         |
| REPERFORM        | May lose or distort text, graphics and camera tilt. Historical failures include Creator POV "Tf did I creuts" and Signal's redrawn WALK/STOP.                                                                                                                                   | Preserve source geometry and graphics by default, then validate them. Remove a graphic from a clean intermediate only when saved original-pixel layers, their exact timing and a reversible coordinate mapping are already planned. Inpainting must retain the source scene; never crop away a caption band or substitute an empty studio to simplify generation. Restore failed text from source pixels with measured opacity and behind-subject masks. For explicitly changed wording, select and tune an available font without asking. |
| GENERATE / STILL | Model-rendered lettering may deform, including garment text (Aura B).                                                                                                                                                                                                           | Preserve all source lettering, logos and watermarks in the final result. Exclude them from a generation prompt only for a planned clean intermediate with exact source-layer restoration. Repair failing letters in place from original pixels/outlines or the measured text layer; never crop source content away to hide them.                                                                                                                                                                                                           |

### 2.7 Length rules (Genjutsu minimum, driving clips, billing)

**The minimum.** Genjutsu (both models) rejects inputs under about 4 s:

- 0.25 s, 1.4 s and 3 s were rejected; 4 s and 5 s were accepted;
- replace returned HTTP 422 with no body on a 3.57 s input (not charged).

**The driving clip recipe** (`references/budget.md` §4.5):

1. `python3 $RR/frames.py export $W --cut cNN --fps 24 --crop window`. This resamples by time and mutes
   the driving clip; preserve the actual source content window and its restoration coordinates. Keep
   captions and graphics by default; §2.6 governs any conditional clean intermediate.
2. `python3 $RR/frames.py pad $W/cuts/cNN.mp4 $W/gen/cNN_pad.mp4`:
   - `--mode pingpong` for cuts under 4 s of real time: exactly 96 frames;
   - `--mode freeze` for longer parts; add `--for mt` on a motion-transfer part so a fractional second
     ≤ 0.1 s stays unpadded (the default `--for replace` pads to ceil).
3. Check that the probed duration is the intended length: an exact integer, except an unpadded MT part
   whose fractional second is ≤ 0.1 s. Price from the PROBED frame count (`ledger.py params` / `guard` with
   `--frames F`).

**Never pad a native-fps export** of a 25/30/50/60 fps reference: `pad` exits 2 on an fps mismatch
unless `--retime`. It would retime the motion and inflate the bill: a 60 fps 3.9 s cut padded as-is is
240 f = 10 s = 110 instead of 44 @1080p. Altman's accepted pipeline exported cuts at 24p first.

**Billing:**

- **Replace bills ceil(seconds),** so always trim or pad to an exact integer. 96 frames = 4.00 s = 44
  @1080p, 28 @720p.
  - VERIFIED live 2026-10-08: Altman's c12 (60 fps, 35 frames) exported at 24 fps gave 14 frames, the
    ping-pong pad made exactly 96, and the 720p replace was charged exactly 28. An exact 4.00 s pad bills
    4 s.
  - Altman padded to 100 frames (4.17 s). The account's replace jobs on non-integer pads were charged 55
    each: 13 × 11 = 143 extra.
- **MT bills and returns round(seconds):**
  - fractional second ≤ 0.1 s: do not pad, and fill the ≤2 lost tail frames in code. Aura D: 11.08 s →
    11 s = 121, cuts kept within ±1 f;
  - otherwise: freeze-pad (`tpad=stop_mode=clone`) to the next whole second.
  - Unpadded parts with a larger fraction get truncated or extended with invented shots: the Aura D
    halves came back 152→145 f and 114→121 f, and a 2 s input returned 4.04 s of continuation.

**Pad rules:**

- **Cuts under 4 s:** ping-pong pad (f0..fN-1, fN-2..f1, repeat, keep the first N) to exactly 96 frames.
  Map back with `gen_index = round(padded_index × gen_frames / padded_frames)` and keep only the first N.
  The output is not 96 frames: the 2026-10-08 swap of a 96-frame pad came back with 89 frames (3.71 s)
  at 24 fps (VERIFIED), and `assemble.py` mapped it back proportionally.
- **"Hold" padding** (each frame repeated k times) broke the pose and lost the gloves in Altman. Never
  use it.

**Grouping and minimums:**

- The minimum means a 0.3 s cut still pays for 4 s. That is the fixed input price of a Genjutsu line,
  and it has no utilisation target.
- **Never group adjacent cuts into one Genjutsu input** to improve the ratio. It is UNTESTED, and
  Genjutsu merged and re-ordered shots on strobe edits in Aura H.
- Seedance's current minimum job is 4 s; re-price the actual settings. A separate job for a short or
  sub-second source cut is allowed when it preserves the measured composition/motion more faithfully.
  Group shots only when every source requirement remains equally well preserved (§3); never lengthen
  or omit a final cut to improve billing efficiency.

### 2.8 Resolution per job

Measure in the delivery frame (`references/budget.md` §5 is the full rule). Do not ask the user for a
resolution at intake.

**The delivery frame comes from `plan/creative-plan.json.output_target`.** In EXACT it is the
reference's own pixel size and format lock unless explicitly changed. In REMIX choose it for the actual
deliverable and brief before pricing; evaluate the real intended crops, never a fictitious larger
canvas used only to justify an upgrade.

1. **An explicit mandate wins:** only explicit words ("1080p", "4K", "max quality") count; "good
   quality" does not. Explicitly supplied resolution changes govern the output; do not offer a 720p saving
   once in the quote.
2. **720p is a candidate only when reference detail is preserved** when the delivery frame is ≤720 px wide or its short side is ≤720 px, the picture is
   windowed or letterboxed, or the look is heavily stylised (threshold / xerox / heavy grain).
   - The /test-edit letterboxed ref was only 1080×608 visible: 720p clips at 35 cr instead of 60, with
     no visible loss.
   - Katana's 1080p high under a hard threshold was mostly invisible.
3. **Full-frame MT on a deliverable ≥1080 px tall: 1080p by default.** A 4:3 take cover-cropped to
   1920×1080 is 1920 ÷ 1112 = 1.73× at 720p, against 1.15× at 1080p.
4. **Identity-legible shots:**
   - k720 = visible width of the generated picture in the delivery frame × the largest code punch-in ÷
     the 720p output width (Seedance 4:3 = 1112, VERIFIED live 2026-10-08; 16:9 1280; 9:16 720; confirm
     on the canary).
   - The punch-in is the planned output zoom; in EXACT it is the measured reference zoom. Framing comes from the
     prompt's shot size, never from a crop of a wider take.
   - Use 1080p for a job when any of its shots shows a legible face AND k720 ≥ 1.3.
5. **Otherwise check all source detail at delivery scale.** Use 720p only when texture, lettering,
   props, silhouettes, motion and required crops remain faithful; choose the necessary available
   resolution within the cap. An unreadable or hidden face does not justify lost non-face detail.

Worked examples:

- **Yaong, delivered at its own 900×720 → 720p**, the identity-legible close-ups included: short side
  720, and k720 ≈ 900 × 1.5 ÷ 1112 ≈ 1.21 < 1.3. (The real project was delivered at 1440×1080 because
  the user chose it; only that choice made its plates 1080p: 1440 × 1.5 ÷ 1112 ≈ 1.94.)
- **Altman's window → 720p:** windowed, and k720 = 996 ÷ 1054 = 0.94 (1054 px = the real 720p replace
  output, VERIFIED).
- **A full-frame 1080×1920 face close-up → 1080p:** 1080 ÷ 720 = 1.5 ≥ 1.3 with a legible face.

The estimate states each selected resolution and its fidelity reason. Choose autonomously within the
bounded cap, without a resolution-upgrade menu.

**Genjutsu output size** follows the driving clip's aspect, with no aspect parameter:

- landscape (4:3) input gives 1664×1248 at 1080p;
- portrait gives 1248×1664;
- a 16:9 input (a crop made in code) gives 1920×1080;
- a window crop keeps its own aspect: a 994×830 pad came back 1054×880 at 720p (VERIFIED live
  2026-10-08).

**Seedance output size:** 4:3 is 1112×834 H.264 at 720p (VERIFIED live 2026-10-08) and 1664×1248 HEVC
10-bit at 1080p; a draft is 752×560.

**Preserve contracted geometry.** EXACT and selected local source edits preserve measured source
geometry; other REMIX scenes follow their authored output geometry. Never force a driving clip or
returned take into a historical 4:3/16:9 example. Record the actual canvas, content window and crop
trajectory. Any intermediate fit must preserve every required subject/detail and meet the selected
output geometry. A paid reframe needs a documented output requirement within the existing finite cap.

**Genjutsu defaults to 720p,** so always pass `resolution` from the plan line.

---

## 3. Grouping cuts into jobs

### 3.1 Seedance multi-shot plates (GENERATE)

**Group by look or scene family only when equally faithful to the output plan.** A family has the same
identity refs, set, light and wardrobe. Per-output-shot jobs remain valid for any composition a shared
plate cannot preserve, including short cuts; grouping never overrides explicit locks or shot roles.

- Katana grouped shots this way: dance-wide, close-ups, macro, floor/hair-fan, aura wind, katana-prop,
  finale.
- Yaong grouped by look: A selfie, B fur coat plus friend, B&W duet.

**Plate length = Σ slots** (`references/budget.md` §4.3):

- Each shot's slot is clamp(2 × the screen seconds the EDL needs from it, 2, 4). A continuous routine
  is ceil(1.6–2 × its prompted length), with the must-have beats in the first half.
- Round up the total required slots to an allowed live duration (historically 4–30 s). If the
  total exceeds the verified maximum, split into coherent jobs before pricing; never truncate
  required slots to fit a duration limit. Do not multiply again: the ×2 already carries the
  slow-gesture margin.
- Each shot is written as `Shot n (a-bs): …`, and the timecodes are the slots. Timecoded shots inside
  one prompt do land: the Katana hiss landed in its 9–12 s slot, and in the 2026-10-08 run a 10 s plate
  of five 2 s shots changed shot almost exactly on every timecode (VERIFIED). The memory note says cuts
  land within ±0.5 s of the requested time in 3 of 4 blocks, but can slide to a later speech pause.
- Never copy duration 15 from the verbatim Katana prompts. They ran in a project that generated 11× what
  it used; re-time their shot list. Copy their structure only, never their identity items: wardrobe,
  props, hair and make-up come from the current output contract (measured source in EXACT, authored plan in REMIX) (a dry-run eval pasted Katana's wardrobe
  into another user's character).

**Why the margin.** Seedance runs slow:

- Yaong's gesture lists ran 1.5–1.6× slower on A1 and about 2× on B1. B1's finger hearts, prompted at
  2.7–3.6 s, arrived at 8–9.75 s.
- So a beat that must hold 0.8 s on screen gets clamp(1.6, 2, 4) = a 2 s slot.
- Put the beats you cannot lose early in the plate.
- List every needed beat explicitly, once. Do not write "repeats the routine": Yaong A1's 4.5–9 s
  "repeat" half was never used and lacked the second cat-paw the edit needed.

**Preserve the selected shot design.** REMIX slots follow the authored story/visual motif and reference
grammar; EXACT slots retain their reference angle, subject motion, silhouette, lighting, crop and timing. Never
remove a difficult silhouette, glint or low angle, add angle alternation, or replace a wipe just to make
a plate easier to generate. Any temporary isolation background must be recomposited to the actual set.

**Plate count from the shot list:**

- Total generated seconds ≈ 1.5–2.5× the unique screen seconds. This target applies to Seedance plates
  only.
  - Katana generated 270 s for about 24 unique seconds on screen (8.9%, about 120 cr per final second).
  - Yaong generated 25 s for 9.52 s (2.6×).
- Yaong F1 was 5 s for a 0.89 s use; the 4 s minimum would have done.

**One take per plate**, then re-roll only a failed shot (`references/budget.md` §6.2):

- the re-roll is a single-shot job of max(4, ceil(2 × its slot)) s at the same resolution;
- the whole plate is re-run only when it is the canary or when half or more of its shots fail for one
  cause.

**Bounded retries and canaries.** Use the one-take policy and bounded failure re-rolls from
`references/budget.md` §6. Test a planned shot that exercises the family's hardest fidelity requirements;
use price only to break equivalent test choices. Verify any refund rather than assuming it.

**After the plates arrive:**

- Plates come out 24 fps; 1080p 4:3 is 1664×1248 HEVC 10-bit, 720p 4:3 is 1112×834 H.264 (VERIFIED live
  2026-10-08; a 10 s plate gave 241 frames).
- Pick in-points from the real plate's timestamped contact sheet (`frames.py catalog`, 4 fps by
  default), never from the prompt's timecodes.
- `jobs_wait` until every plate of the batch is terminal before cataloguing. Between polls, do
  reference-side work only.
  - Katana f3a (180 cr) arrived after planning started and was never used.
  - A plate that lands after the EDL exists must be catalogued and the EDL reviewed before rendering.

### 3.2 Genjutsu jobs (SWAP / REPERFORM)

**SWAP is per cut,** on 96-frame pads (exactly 4.00 s: 28 @720p, 44 @1080p). A cut of 4 s or more is
trimmed or freeze-padded to an exact whole second, because replace rounds up.

- Never a full-length or grouped replace pass in the default plan. A whole-reel replace is an UNTESTED
  experiment excluded by default (`references/budget.md` §4.7).

**One full-length take applies to REPERFORM (MT) only,** for refs up to about 11 s with no burned-in
graphics or captions:

- Aura D (11.08 s): only the full take kept the ref's cuts within ±1 f; the halves came back retimed.
  Unpadded, it bills round(11.08) = 11 s × 11 = 121.
- Aura H (9.58 s): full takes, cast into a 35-segment plan by content, because Genjutsu re-orders and
  merges shots on strobe edits. Freeze-padded to 10 s = 110 per take, and 2 takes planned (220).

**MT per part** (5–9 s parts cut at the ref's own cuts) when:

- the ref is longer than about 11 s. Aura G was 3 parts of 6 + 5 + 8 s, and all 4 takes were used;
- the ref has burned graphics that the full take redraws. Split on measured source cuts when this preserves them more faithfully; any clean intermediate needs saved source layers and exact restoration. A historical empty-studio experiment is not a default scene replacement;
- the scene or world changes between parts.

Parts pay their own rounding: G is 6 + 5 + 8 = 19 billed seconds = 209 at 1080p, not 16.92 → 17 × 11 = 187. Parts under 4 s pay the 4 s minimum. Splitting never saves credits.

**MT per cut** when that supported motion-transfer operation was selected for the measured cut.
A content refusal does not select MT. Use source-derived timing with the verified model's minimum
input duration (§2.7).

**Rules for every Genjutsu job:**

- The driving clip is the source-aligned 24 fps muted export (§2.7). SWAP keeps baked captions and
  graphics by default. A clean MT intermediate is conditional on the exact restoration plan in §2.6;
  no route requires blanket caption stripping or loss of source framing.
- Dispatch one paid request per guard reservation and immediately add its returned id; no generation batches.
- Canaries per `references/budget.md` §7:
  - select one already required hardest-fidelity cut per actual model/reference/world family;
  - do not add paid exploratory jobs merely because a film or person is recognizable;
  - submit canaries one at a time through guard → submit → add; different submitted jobs may process
    concurrently, but no two dispatches share an unrecorded reservation.

### 3.3 Stills, mattes and audio

**Stills:**

- count 1 per need, submitted serially through guard → submit → add;
- at most 3 attempts per still need within the cap; report any remaining gap;
- preserve the intended identity and explicit subject locks. EXACT permits a new fictional subject only
  for an explicit replacement; REMIX may author unlocked supporting characters required by its story,
  without replacing the user's intended hero or buying unused character variants.

Create a still only when it is needed and no suitable existing image already meets the requirement.
Eligible uses include a finished still/CODE shot, source-anchored anime or stylized identity replacement,
a required REPERFORM image (G5), and a Seedance start/reference frame (G8). Select the necessary route;
do not turn these uses into mandatory sequential paid stages.

SWAP usually takes a suitable supplied replacement-identity image directly. Prepare a source-aligned
reference only when required for measured identity/wardrobe fidelity; it is not an automatic extra stage.

**Mattes:** order them only after the EDL exists, and only for clips the EDL uses with contours,
cut-outs or behind-subject text.

- Katana's mf4b served a single 0.21 s wipe.
- Yaong's still-image matte was never used.
- Run one matte first when the clothing is dark. The /test-edit `video_background_remover` mattes went
  unused on a navy blazer; `sam_3_video` worked.

**Audio:** EXACT preserves the reference stream/timing unless changed. REMIX uses the authored audio
plan and explicit locks, selecting actual available source/user/stock recordings as needed; no code
music/SFX synthesis. TTS requires a supported noninteractive voice route and planned speech need;
choose internally after read-back and timing checks, within the bounded cap. See `creative-quality.md`.

---

## 4. Historical routing evidence

These observations explain the technical routes; they are not casts, creative briefs or user-choice
menus for a new job. Reference content and the current verified tool contract remain authoritative.

| Observed route          | Historical result                                              | Limitation                                                                       |
| ----------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Per-cut SWAP            | 96-frame 24-fps pad charged 28 cr at 720p; 89 output frames    | Map the actual returned frames back to the reference grid                        |
| Full-take MT            | 11.08-second reference preserved cuts within about one frame   | Multi-cut and strobe inputs may merge or reorder shots; strict QA still required |
| Multi-shot plate + CODE | Five 2-second slots supplied a 10.5-second mixed-media rebuild | A similar-looking rebuild does not prove a frame-exact reproduction              |
| User footage + CODE     | 27 cuts assembled from two user files, no generation charge    | Applies only when footage covers the required reference shots                    |
| Photo series            | Proposed still-based route was never run end to end            | Verify a small set inside the cap before relying on the full method              |

## 5. Router output: `plan/routes.json` (logical content)

`ledger.py` and `references/budget.md` own the exact quote and ledger format; if their keys differ,
theirs win. `plan/gen_plan.json` is filled from the `jobs` below. Each paid job's params are then
prepared by `ledger.py params $W --line <id>`, verified against the current callable contract and
exactly priced. Execute guard → one submit → immediate add; generation batches are disabled.
The router must produce at least this content:

This REMIX example uses output IDs in `cuts`, `for_cuts` and the ledger's `serves_cuts` field. The
observed source cut IDs stay in `source_evidence`. EXACT can reuse source IDs because its output grid
matches the source; its format/audio locks still come from the task contract.

```json
{
  "task_contract": "analysis/task-contract.json",
  "creative_plan": "plan/creative-plan.json",
  "creative_mode": "remix",
  "family": "F2",
  "output_target": {
    "size": "<authored delivery size>",
    "fps": "<planned fps>",
    "frames": "<planned frame count>",
    "audio": "<planned actual recording>"
  },
  "cuts": [
    {
      "id": "o01",
      "f0": 0,
      "f1": 23,
      "role": "hook",
      "route": "USER-FOOTAGE",
      "reason": "existing authorized footage fulfills the hook and identity locks",
      "source_evidence": [{ "asset": "<user clip>", "interval": "<verified interval>" }]
    },
    {
      "id": "o02",
      "f0": 24,
      "f1": 71,
      "role": "payoff",
      "route": "GENERATE",
      "job": "plate_A",
      "reason": "missing new action in the authored story, using selected reference texture and light grammar",
      "source_evidence": [{ "source_cut": "c07", "use": "texture/light grammar only" }],
      "text": "<authored wording or none>",
      "matte": false
    }
  ],
  "jobs": [
    {
      "id": "plate_A",
      "route": "GENERATE",
      "model": "seedance_2_5",
      "mode": "<verified API mode>",
      "resolution": "<priced resolution>",
      "res_why": "preserves planned output detail after actual crop",
      "identity": true,
      "generate_audio": false,
      "bitrate_mode": "high",
      "duration": 4,
      "shots": [{ "n": 1, "slot_s": [0, 4], "screen_s": 2, "for_cuts": ["o02"] }],
      "quote_cr": 0,
      "canary": true
    }
  ]
}
```

The sample is structural only: expand it to cover every frame and replace placeholder model/cost fields
with verified contracts and estimates. A zero placeholder is never a valid paid-job estimate.

Rules for the file:

- Every output cut has exactly one route and a concrete role/scope/continuity reason. REMIX can omit
  source cuts or invent unlocked scenes without editing the measured breakdown. EXACT accounts for
  every required source interval. For subject replacement,
  record every appearance of the target, including hidden-face shots, its connected continuity cuts
  and output verification; none may silently become KEEP. Unrelated B-roll remains untargeted.
- For full regeneration, record a reconstruction route for every required cut. Any reused layer needs
  a specific permitted scope reason; face invisibility is never a reuse exemption.
- Every paid job lists the output cuts it serves, including asset jobs through their dependent shots.
  A paid job serving no output cut is waste: delete it before the
  quote. A canary is always one of the planned, cut-serving jobs, never an extra one.
- Every video job carries its resolution and the §2.8 reason, and Seedance plates carry their slots and
  state `"generate_audio": false` and `"bitrate_mode": "high"` (copied into `plan/gen_plan.json`, where
  `ledger.py quote` warns about a Seedance line without them).
- Every job replacing the targeted subject carries `"identity": true`, including hidden-face continuity
  shots. Face readability determines the QA evidence and resolution needs, not replacement scope.
- F1b full MT takes retain `"full_take": true`; strobe references retain `"strobe": true`. Plan extra
  takes only when required and covered by the bounded cap.
- Existing schema supports `"optional": true`, `"take_reason"` and `"take_of"`, but this workflow
  does not create interactive optional lines. Select necessary jobs internally and include their cost.
- IP-suspect SWAP cuts retain source and permitted fallback metadata; associated generation-plan lines
  carry `"ip_suspect": "<source>"`. A refusal never permits filter bypass.
- F3 KEEP/LIBRARY cuts record authorization and provenance; sourcing is autonomous, without a link menu.
