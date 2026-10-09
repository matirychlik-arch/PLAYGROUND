# Budget: existing spend authority, sizing and ledger

This file holds the cost-control rules of katana. Follow them literally. Every rule exists because a
real project lost credits without it (§9 has the numbers). Prices are from 2026-10-08 and match
`scripts/prices.json`; they drift, so re-probe them before quoting (§2.2).

**VERIFIED (live 2026-10-08)** marks a fact measured in the paid test run of that day (Higgsfield sandbox

- MCP, 111.12 cr in total, reconciled exactly with `transactions`; §10, "Measured run"). Everything else
  comes from the earlier projects' records or from the dedicated cost-estimation tool, as stated next to it.

Read other reference files locally from the bundle. If the task has no supplied reference, find and inspect one under [creative-quality.md](creative-quality.md) before constructing the paid plan. Scripts run in the sandbox as `python3 $RR/<script>.py`, where
`$RR = $HF_WORKFLOWS/katana/scripts`. Exact script arguments: `python3 $RR/ledger.py <cmd> --help`;
if this page and the script disagree on arguments, the script wins.

## 0. Rules at a glance

Read `analysis/task-contract.json` before sizing. REMIX is the default; its output shots, timing,
format, text and scene design come from `plan/creative-plan.json`, subject to every explicit user lock.
EXACT inherits the reference's duration, frame grid, fps, dimensions, appearance, text and audio except
for requested changes. Historical exact-rebuild examples below do not impose source geometry or
motion transfer on a remix. Preserve the intended hero/product in either mode; new supporting assets
must serve the authored plan, not an unnecessary intake field. Never ask questions, request approval,
present choice menus, request fonts or enter a state waiting for user consent.

An explicit execution request authorizes ordinary necessary use of existing generation credits within
actual account/platform permissions. Derive a finite internal cap for the entire workflow from exact
quotes for ready jobs, verified current upper bounds for dependent deferred jobs (§8.2), and a bounded
retry allowance. Deferred bounds include downstream work but never authorize its submission. The hard
cap is the minimum of that internal cap, any supplied numeric user
limit and any applicable account limit; a numeric user budget is optional. Inform the user of the plan
and continue autonomously. Never request consent or wait for it, buy credits, top up, subscribe or bypass
platform permissions. If a service mandates interactive consent, select an already-authorized supported
alternative. If no alternative exists, continue free work and deliver a truthful partial or declarative
limitation without asking the user to approve, choose or enable anything.

**Complete free analysis before any paid video:** decode and inspect the entire reference with an
accounted-for record for every frame and every elapsed second, including the final partial second.
Use per-frame observations plus a per-second synthesis of motion, cuts, text, audio sync, textures,
lighting and transitions. Detect and preserve subtle overlays, grain, texture changes and one-frame
flashes. A contact sheet or sparse sample alone does not satisfy coverage. Complete any missed ranges
before video costing/submission. Optimize wall-clock time through decoding reuse, batched frame
inspection and parallel independent ranges, never by skipping frames, seconds or difficult details.

Choose the route that best satisfies the selected mode and user locks within the existing allowance;
use cost to break otherwise equal choices. REMIX builds the planned roles and visual language through
usable footage, necessary images and Seedance scenes, with Genjutsu only for justified source
transformations. EXACT minimizes deviation from the reference. Existing authorized assets and code
may be reused when suitable; preserve provenance. Do not omit required beats, change explicit locks
or lower quality to make a cheaper plan appear complete. A revised remix plan can solve the same
creative need economically, but cannot masquerade as an exact recreation or silently drop user needs.

Code savings never authorize local face replacement, face/head patching, facial warping, restoration,
beautification or hand-painted anatomy. Identity/expression corrections require the permitted image,
Genjutsu or Seedance route within the plan. If no such correction remains available, report the
unresolved cut without asking; do not repair the face in code. Whole-plate camera moves, planned
whole-shot effects and separate graphic layers are compositing, not identity corrections; EXACT
matches the source and REMIX follows its authored plan.

**Video-model allowlist, checked before costing every plan and every batch:** every fresh-video
`GENERATE` job must use exactly `seedance_2_5`. Genjutsu transformations, including optional Genjutsu
presets for anime when useful, use only exact currently verified model/workflow identifiers and
contracts. A verified Restyle operation is eligible only when its selected Genjutsu preset route
actually requires it; it is not a mandatory extra stage. Never invent a preset/model id. Inspect every
batch item independently; exclude any other
fresh-video model, including preview and retry jobs. Historical price rows do not authorize an
alternative. If the required allowed capability is unavailable, use authorized existing assets/code or
report the limitation without questions, consent prompts or a user-wait state.

Before each paid submission, the live-priced parameters must match the plan, `ledger.py guard` must
pass, and committed spend plus the new worst-case charge must remain within the existing hard cap.
The guard enforces the explicit `hard_cap` with no percentage margin. Record every submitted job at once,
verify refunds before freeing their allowance, and reconcile unknown submissions before retrying.

Use one take per job, at most one justified video re-roll per job, and at most three attempts per still
need. All attempts must remain within the cap. Test each model/identity/scene family on a planned shot
that exercises its hardest fidelity requirements. Await every submitted job before final asset selection.
When a limit or guard blocks work, continue free or already-authorized work and report any remaining gap.

## 1. Where the money goes

**The bill is video seconds × resolution.** Everything else is noise.

Historical spend evidence only; unselected models below are not executable recommendations.

Account spend history (1,500 transactions, 2026-09-19 → 2026-10-08, 56,899 cr spent, 3,976 refunded):

| Bucket                                                                                     | Jobs | Credits | Share   |
| ------------------------------------------------------------------------------------------ | ---- | ------- | ------- |
| Seedance 2.5 video                                                                         | 454  | 36,252  | **64%** |
| Genjutsu motion transfer                                                                   | 88   | 15,018  | **26%** |
| Wan 3.0 / Prime, Object Swap, Seedance 2.0, other video                                    | ~56  | ~4,600  | ~8%     |
| ALL image models together (GPT Image 2.5 ×584, Soul ×101, Nano Banana ×39, GPT Image 2 ×7) | 731  | ~650    | **~1%** |

Consequences:

- **A still costs about what 0.01–0.2 s of 1080p video costs.** Iterate on stills, never on video.
  - Examples: Soul 2.0 0.12, Seedream 5.0 Flash 0.5, Nano Banana 2 1k 1.5, Seedream 5.0 Pro 2k 2.5.
  - One second of Seedance 1080p is 12.
- **Price is set by the generated seconds, not the seconds on screen.** Katana paid 12 cr per generated
  second but ~120–135 cr per second that reached the final, because 91% of the footage went unused.
  The same 10.5 s reference rebuilt under these rules cost **7.9 cr per final second** (VERIFIED live
  2026-10-08: 83.12 charged for 10.5 s, §10 "Measured run").
- **Code is free.** `sandbox_exec` costs 0 credits (verified via `transactions`). That covers analysis,
  sheets, compositing, text, grade, grain, flashes, transitions, sticker placement, tracking, recorded-SFX mixing,
  renders, QA and every revision. This does not authorize procedural music or SFX; use actual source/stock recordings and the rules in [creative-quality.md](creative-quality.md).
- **Never buy from a video model what code can do:** camera punch-ins and pushes, shakes, whip and zoom
  transitions, speed ramps and slow-mo, B/W or any grade, grain, flash frames, typography, frames and
  windows, watermarks, the audio mix.
- **Never pay for post that code does:**
  - `reframe`: crop or pad in code;
  - `fps_boost` or deflicker: local `minterpolate` / `tmix` only for a measured requested correction; preserve intentional source cadence/flicker;
  - video upscale of footage that ships at its native size;
  - `video_analysis_create` (2.2–2.3 cr per call): `analyze_ref.py` does the job in the sandbox for
    free.
- **Never reframe a driving video.** The one exception to the reframe ban: a portrait (3:4) take that
  must fill a landscape canvas. Its cover-crop is a soft 1.54× upscale (1248 px wide → 1920), so
  reframe is eligible only when needed for fidelity and already covered by the numeric cap (§8).

## 2. Price table and the verify-before-quoting procedure

### 2.1 Live prices (probed 2026-10-08, historical cost probes + matched against real charges)

Allowed video routes only (historical rates per second of OUTPUT unless stated; verify current prices):

| Model (MCP id)                                        | 480p | 720p | 1080p | Min / allowed durations        | Notes                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------------------------------------------------- | ---- | ---- | ----- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `seedance_2_5` (t2v, omni_reference, video_extension) | 3    | 7    | 12    | int 4–30 s                     | Audio on/off, bitrate high, aspect, number of refs: **no price change**. 4 s = 12/28/48; 5 s = 15/35/60; 10 s = 30/70/120; 15 s = 45/105/180. 10 s @720p 4:3 omni_reference = 70, output 1112×834 H.264 24 fps (VERIFIED live 2026-10-08). `draft:true`: 4 s = 12, output 752×560 (VERIFIED); the finalize is always 1080p at the full 1080p price (§2.3).                                  |
| `seedance_2_5` video_edit                             | —    | —    | —     | billed by source length (est.) | 4.04 s source = 15/31/49. UNTESTED as a katana route: excluded by default (§4.7)                                                                                                                                                                                                                                                                                                        |
| `hf_mult_motion_control` (Genjutsu MT)                | 3    | 7    | 11    | ~4 s min (shorter is rejected) | **Per second of DRIVING video, rounded to the nearest whole second.** 4 s = 12/28/44; 11.08 s → 11 s = 121 @1080p                                                                                                                                                                                                                                                                           |
| `hf_mult_replace_object` (Genjutsu replace)           | 3    | 7    | 11    | ~4 s min (3 s rejected)        | Same rate but rounds UP: an exact 4.00 s pad (96 f @24) = **28 @720p** (VERIFIED live 2026-10-08, real charge) / 44 @1080p (Altman dedicated estimator); 4.04 s or 4.17 s → 5 s = 15/35/55. Output follows the clip's aspect: a 994×830 window pad came back 1054×880, 24 fps, **89 frames for 96** (VERIFIED), so map back proportionally. 7 of 18 earlier account jobs failed (refunded). |

Post and mattes:

| Tool                                                   | Price                                                             | Notes                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------ | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `remove_background` video (`video_background_remover`) | 1 per job                                                         | 14 observed charges of 1 on 4–5 s sources, and 1 on a 10 s 720p plate (VERIFIED live 2026-10-08); sources over 10 s unmeasured                                                                                                                                                      |
| `sam_3_video`                                          | Historical observations: 1.14 per job; ~2.5 per 266 frames (Aura) | Historical estimator failure and observed charges are not an executable quote. Require an exact current non-submitting estimate or verified account quote in credits; otherwise use supported local masking or declare the missing operation. Never authorize it with `unit_price`. |
| image background remover                               | 1                                                                 |                                                                                                                                                                                                                                                                                     |
| `bytedance_video_upscale`                              | 0.1/0.2/0.4 per 5 s (standard 1080p/2k/4k); pro 1/2/4             | Never for footage that ships at its native size. 720p + upscale instead of 1080p is UNTESTED (§5)                                                                                                                                                                                   |
| `reframe` (workflow)                                   | 5 s: 18 / 25.5 / 48 (480/720/1080p)                               | Never buy it: crop or pad in code. Never on a driving video. Only exception: a fidelity-required portrait-take correction already within the cap (§1)                                                                                                                               |
| `fps_boost`, deflicker                                 | paid per clip                                                     | Prefer measured local correction only when required; never smooth away source cadence or intentional flicker. No automatic `minterpolate` / `tmix` pass.                                                                                                                            |
| `video_analysis_create`                                | 2.2–2.3 per call                                                  | Never buy it: `analyze_ref.py` is free                                                                                                                                                                                                                                              |

Images (per image):

| Model                | Price                                  | Notes                                                                                                                                                                                                                                                                                             |
| -------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `soul_2` (Soul 2.0)  | 0.12                                   | Fictional humans. Use for an explicitly requested new fictional subject or an unlocked supporting character needed by a REMIX story; never replace the intended hero. Select one result autonomously, count 1. 2k 3:4 = 0.12, output 1536×2048, backdrop slightly grey (VERIFIED live 2026-10-08) |
| `seedream_5_0_flash` | 0.5                                    | any res                                                                                                                                                                                                                                                                                           |
| `seedream_v5_pro`    | 1.25 (1k/1.5k), 2.5 (2k)               | identity sheets, i2i look changes; `remove_bg` surcharge unmeasured                                                                                                                                                                                                                               |
| `nano_banana_2`      | 1.5 / 2 / 3 (1k/2k/4k)                 | refs free; 2-ref keyframes and REPERFORM stills                                                                                                                                                                                                                                                   |
| `nano_banana_pro`    | 2 / 2 / 4                              | defaults to 2k                                                                                                                                                                                                                                                                                    |
| `gpt_image_2`        | low 0.5 … high 2k **6.5** … high 4k 11 | MCP default low+1k = 0.5; CLI default high+2k = 6.5 (trap). Drifted colours in Yaong.                                                                                                                                                                                                             |
| `gpt_image_2_5`      | low 1k 0.25 … max 5                    | Sunburst real charges were 2.75 and 15, estimates unreliable                                                                                                                                                                                                                                      |

Audio:

- `seed_audio` 0.3–2 per take (quoted at 2, the upper bound).
- `elevenlabs_v4` ~0.23 per 30 characters.
- Historical SFX model prices are not an active route: source new SFX from actual stock recordings; do not synthesize music or effects.
- Use an existing authorized voice only when narration is requested. Do not open a voice picker or add narration to replace a song.

Free: `sandbox_exec`, dedicated `estimate_image_cost` / `estimate_video_cost` preflights, `media_upload`/`media_confirm`
(never seen as charges), `models_get` / `models_search`, `balance`, `transactions`, `jobs_wait`, and preset-hijack
bounces (no job is created).

**Historical refund observation, not a promise for this run.** The recorded account's `transactions` showed
`nsfw`, `ip_detected` and `failed` job charged at submit and refunded within ~5 s–4 min
(`references/mcp-api.md` §13):

- 6 × replace `ip_detected`: −55 / +55 each;
- 3 × Seedance `nsfw`: −28 / +28 each;
- failed Seedance and MT jobs: refunded too.

After a block, inspect current `transactions` for a matching refund. State only observed charges and
refunds; never promise that a blocked job is free. Mark `refunded` only after the matching credit is
verified, and retain unrefunded charges in committed spend.

What a block does cost:

- **Time and a re-plan; net credits depend on the verified refund.** `nsfw` shows ~2.5 min after submit, and a full job takes
  3–12 min.
- **A balance reduction until a refund is actually verified.** Do not assume it will be temporary.

An HTTP 422 on a too-short replace input is not charged at all. The money at risk is COMPLETED but
unusable footage: wrong identity, wardrobe, background or motion. That is what canaries protect (§7).

### 2.2 Verify before quoting (mandatory, free)

The stored memory note said Seedance 2.5 costs 63 cr per 7 s, about 9 cr/s. The live price is 84
(12 cr/s), so the note was **33% low**. Never quote from memory or from this table alone:

1. **Build the generation plan first:** `plan/gen_plan.json`, filled from the router's
   `plan/routes.json` jobs (see `references/routing.md` §5).
   - Every paid job must list the cuts it serves.
   - An **exact request** includes the actual prompt, input media IDs, model, mode, resolution,
     duration, quality/bitrate settings and every supported operation parameter. For Genjutsu it also
     includes the probed driving-frame count. A changed prompt or media input needs its own current estimate.
   - If an input is the output of an unfinished selected job, declare the dependent line `deferred:true`
     with `depends_on` and `input_bindings` (§8.2). Record its verified current per-job planning upper
     bound; do not invent an input ID, exact quote or provider price to register the workflow.
2. **Price only the selected path: exact quotes for ready requests, bounded planning quotes for deferred
   requests.** For anime, include a
   frame+character image job only when the selected route needs a missing prepared frame; reuse suitable
   existing images or use a justified direct transformation when they suffice. Price only the selected motion route;
   never automatically add an extra preset/Restyle charge. Call `estimate_video_cost` or `estimate_image_cost` with the real parameters after
   reading its current contract. `generate_video` and `generate_image` submit paid jobs; never call them
   as price probes or assume an extra flag makes them free. Use a separately verified audio estimator
   if one exists; otherwise omit paid audio whose upper bound cannot be verified.
   - **Serial paid dispatch only.** This ledger deliberately does not submit generation batches.
     Reserve one job with `guard`, submit that one request with count 1, then `add` its returned id
     before the next guard. Provider batch capacity does not change this accounting rule.
   - For a ready or activated line, prepare `ledger.py params $W --line <id>` (§8.3), verify it against the current callable schema,
     and fill actual media/prompt/format fields in the plan. Unknown contracts fail closed; never
     improvise a generic image call for a preset or change the payload after the exact cost estimate.
   - Pass explicit resolution, duration, aspect and image quality only where the selected verified
     contract supports them. Direct Genjutsu length/aspect follow its actual source video.
     Defaults are traps: Seedance defaults to 720p 5 s 16:9 with audio; the CLI's gpt_image_2
     defaults to high 2k (6.5); a draft finalize with no duration prices 5 s (§2.3).
   - Every Seedance call also carries `generate_audio:false` and `bitrate_mode:"high"`, both free, and
     every Seedance plan line states both fields itself (§8.1, plan fields), so they are visible in the
     plan and the quote, not only injected by `params`.
   - **Genjutsu:** upload the actual driving clip first (upload is free). Obtain an exact preflight
     once every required input exists; a missing generated image keeps the line deferred under §8.2.
     Keep its prompt to 1–2 short sentences, at most 40 words; source video/image carry the look and
     motion. Do not itemize wardrobe, camera moves or a detailed script. Use an empty prompt only if
     the selected verified preset contract supports it. This limit applies only to Genjutsu, not to
     image-generation or Seedance prompts.
     - Price each clip from its PROBED frame count (§4.5), never from the plan's nominal 96.
     - Estimate each actual clip/prompt request; do not reuse a different clip's response because its
       frame count matches. Historical observation only: one actual 96-frame pad was charged 28 @720p
       on 2026-10-08; this is not a current quote or permission to submit another clip.
3. **Inspect current estimator/tool responses.** A recommendation is data, not a paid submission
   instruction. Do not assume the historical preset-decline parameter still exists. Use only a
   currently documented non-submitting estimator; never probe a prompt through a generation call.
4. **Record live prices.** If a live price differs from the table, use the live one and record it with
   `ledger.py price-set $W --line <id> --credits <one-job credits> --source estimate_video_cost
   --evidence "<actual estimator response reference>"` (use `estimate_image_cost` for images).
   The exact configuration, current timestamp, evidence and native credit amount are stored. A changed
   request or an estimate older than 24 hours needs another non-submitting estimate.
   For a deferred line, use `price-set $W --line <id> --planning --basis "<verified upper-bound basis>"
   --credits <per-job upper bound> --source <estimate_video_cost|estimate_image_cost|verified_account_quote>
   --evidence "<actual current evidence>"`. This is a non-executable planning bound, not an exact quote.
   Planning evidence must also be current within 24 hours; historical tables or guessed prices do not qualify.
5. **Mark estimates.** Some supporting operations may lack a dedicated estimator (`sam_3_video`, supported post-processing).
   Use a verified current account quote in native credits as `--source verified_account_quote`,
   with its real evidence and upper bound. A historical observation alone cannot authorize a paid
   submission. A deferred line may register a verified current planning bound, but cannot execute until
   it has an exact actual-input quote. Without either the required planning bound or executable exact
   quote for the relevant stage, use free work or report the limitation. (A Seedance draft finalize can be preflighted: the dedicated cost-estimation tool on it returns the full 1080p price,
   VERIFIED live 2026-10-08; §2.3.)
6. **Check the balance.** Call `balance` once before the quote. If the worst case exceeds the balance,
   say so in the quote. The balance is shared with the user's other chats, so it is never the measure
   of this project's spend (§8.3).

### 2.3 Seedance draft → finalize (excluded by default, quality UNTESTED)

Measured on 2026-10-08 (VERIFIED live):

- `draft:true` bills at the 480p rate: 4 s = 12. The draft comes back 752×560 (4:3), good for judging
  composition and shot order, not for shipping.
- The finalize of a draft is **always 1080p** (a `720p` param is ignored) and costs the **full 1080p
  price**: the dedicated cost-estimation tool on a 4 s finalize returned 48. Without a `duration` it prices 5 s (60), so always
  pass the draft's duration.
- Draft + finalize = 12 + 48 = 60 for 4 s = **1.25×** a direct 1080p job (48).

When it can pay off: it saves credits only when the drafts you reject replace direct jobs you would
have rejected. Per attempt, with r = the share of drafts you expect to reject:

- against a direct **1080p** job: 12 + 48 × (1 − r) < 48 ⇔ r > 25%;
- against a direct **720p** job (most plans here, §5): 12 + 48 × (1 − r) < 28 ⇔ r > 2/3, because the
  finalize forces 1080p.

Rules:

- Never the default. Use only if an existing request explicitly includes this experiment and its full
  cost fits the authorized cap; otherwise select the direct fidelity route without offering a menu.
- Its motion fidelity is unverified: nobody has compared a finalize against its draft. Do not promise
  that the finalize matches the inspected draft.
- Price the line as draft (480p rate × seconds) + finalize (1080p price × the same seconds) per plate.

## 3. The cost ladder (exact rules per rung)

**Rung 1: free (0 cr).** Fetch, deconstruct, contact sheets, cut list, breakdown, routing, prompts,
price preflights, the quote.

- Rank sources by the selected output role and locks. In REMIX use suitable footage, CODE for graphic
  layers, necessary STILL assets and Seedance GENERATE for new action; SWAP / REPERFORM require a
  concrete source-preservation need. In EXACT rank by source fidelity. Price breaks ties; it never
  justifies omitting a required beat or retaining an unwanted source performance in a remix.
- F3 uses real footage for real events and people. Reuse authorized inputs or independently choose
  matching licensed sources; never fabricate archival events or wait for a sourcing-list selection.

**Anime reference route and single accounting path:** use the source frame plus the uploaded character
photo when they serve the selected image operation. EXACT preserves source composition, pose,
lighting and style except the requested change; REMIX assigns identity/style/composition ownership
from its planned new shot. If a still and whole-plate editing satisfy that shot, stop there. Generate
fresh motion with `seedance_2_5` when the output action needs it. Genjutsu presets are optional
alternatives for the required transformation, never a compulsory Styles/Restyle pass. Price each image once
and only the chosen motion/transformation route once. Do not charge for parallel alternative routes or
add both Seedance motion and a preset transformation unless the selected output plan requires both and the
plan documents the distinct need within its cap. No selection questions or consent menus.

**Rung 2: stills (≈ free; 0.12–2.5 each).**

- **Reuse a suitable existing identity anchor per character.** Generate one only when required by the
  actual shot: a supplied photo may need a prepared sheet, and an explicitly requested fictional human
  or unlocked supporting character required by a REMIX story may need one generated still. Preserve the
  intended hero and select internally; no automatic sheet purchase for every character.
- **Keyframe and reusable asset stills only for necessary output roles:**
  - For REMIX, a reusable location, prop, hero anchor or composition image is eligible when existing
    media do not cover a planned need. Associate it with the output shots served; no mandatory
    character sheet or location image for every shot. Do not import fixed asset counts from a preset.
  - (a) **The REPERFORM image** (`references/generation.md` G5): reuse an existing frame when it
    preserves the required subject, composition and look. Prepare a new G4 two-reference image only
    when needed, using the exact source cut frame and uploaded identity. Preserve captions/graphics
    unless an explicit source-layer restoration pass is planned. A content refusal never authorizes
    a text-only reconstruction of the same blocked request; correct only a permitted technical error
    or use a genuinely supported fallback and declare any remaining gap.
  - (b) **Start frames for Seedance shots or plates** (G8). Use a dedicated clip whenever it preserves
    required motion more faithfully, including sub-second shots. Satisfy the live model's job minimum
    while keeping the final interval as short as the output plan requires (the source interval in
    EXACT); do not drop a required short shot for cost.
  - (c) **Anime keyframe:** the source frame + uploaded character photo generate the planned still,
    matching source composition in EXACT or its declared role in REMIX; finish with whole-plate code
    when sufficient, or use it for necessary Seedance 2.5 motion. A Genjutsu
    preset is an optional alternative, not an additional mandatory purchase.
  - **SWAP uses the intended supplied identity image.** Prepare another frame only when a verified
    supported operation actually needs it for fidelity; never buy an automatic extra keyframe.
- **At most 3 attempts per still need within the existing cap.** Still needs are the identity anchor,
  a requested look change and each keyframe. After three failures, use the best valid asset or report the gap.
- **One proven model per still type.** No model shoot-outs: Yaong's 4-way look-B test wasted ~15 cr,
  and gpt_image_2 got the colour wrong.
- **Check identity-critical stills against the intended identity internally** before video; choose
  a suitable asset and continue without a review gate.
- **Use ~10% of the plan as a still-iteration warning.** Above it, stop redundant iterations and
  preserve the required fidelity within the cap. This heuristic does not apply to photo-series plans (F5).
- **Photo-series references:** first live-price the required series and bounded reserve, counting unique
  frames after faithful reuse. Register the finite cap, then submit one planned representative still at
  final settings as the canary; do not add exploratory stills (§10, photo series).

**Rung 3: canary (a representative fidelity-critical planned job of each family).** See §7. Submit
one planned canary at final settings through guard → single submit → add, then the next. A passing
canary is usable footage, not an extra unplanned test.

**Rung 4: remaining planned jobs, serialized submissions.**

- A family's remaining jobs go out once their own canary has passed. They do not wait for other
  families.
- One take and one submitted request at a time. Do not use generation batch tools.
- Resolution per §5, durations per §4.
- Before the single request, run `ledger.py params --check` and `ledger.py guard`. The guard reserves
  its full quoted exposure. Immediately record its one returned id with `ledger.py add` (§8.2).
- `jobs_wait` (groups of ≤6) until ALL paid jobs of the batch are terminal.
  - Between polls, prepare plan-based text layers, effects, the audio map and QA material; do not
    assume unfinished video jobs have succeeded.
  - Do not catalogue plates, choose in-points or write the EDL before that.
  - A job that turns terminal after the EDL exists must be catalogued, and the EDL reviewed, before
    rendering. Katana's f3a (180 cr) arrived 3 min after planning began and was never used.

**Rung 5: targeted re-roll.** Only for a failure that code cannot rescue, and only from the fail list
(§6.2): identity, wardrobe, garbled text or logo, anatomy, a matte-hostile background, a missing beat
the EDL needs, or a job failure. Look at the failure on its `frames.py catalog` sheet (4 fps by
default). One re-roll per job, no more than that job's own cost and only within the existing hard cap.

**Rung 6: code-only revisions (0 cr).** Text, timing, colour, density, stickers, transitions, tracking
and recorded-SFX mix changes never trigger video generation:

- Katana applied 65 QA fixes at 0 cr (re-render 7–11 s each);
- Yaong's v1→v2 cost 0 cr in 11 min;
- Altman's v2→v3 only re-matted one clip.

## 4. Sizing: how many seconds to generate

### 4.1 Unique screen seconds

Compute **U = the unique screen seconds** needed by output shots routed to GENERATE / SWAP /
REPERFORM. In REMIX use the authored output intervals and intended asset reuse, not the number or
duration of reference cuts. In EXACT those output intervals follow the source. Frozen, repeated and
stuttered material counts once. Bill Genjutsu from the actual driving input separately.

### 4.2 Utilisation target (Seedance plates only)

- **Seedance plates:** generated seconds ≈ 1.5–2.5 × the U they serve.
  - Katana generated 11× (270 s for ~24 s used).
  - Yaong generated 2.6× (25 s for 9.52 s).
- **Genjutsu lines have no target.** Report them as "fixed input (min-billed)": the driving clip and the
  4 s minimum set their length. A 0.4 s cut on a 96-frame pad is 10× by construction, and that is
  correct.
- **Never group cuts into one Genjutsu input to improve the ratio.** It is UNTESTED: Genjutsu merged and
  re-ordered shots on strobe edits (Aura H), so a grouped take can come back unusable and still be paid.

### 4.3 Seedance plate length (one formula, no extra multiplier)

- **Multi-shot plate:** duration = Σ slot_s.
  - slot_s = clamp(2 × the screen seconds the EDL needs from that shot, 2, 4).
  - The ×2 is the whole margin for gestures that run 1.5–2× slow. Do not multiply again.
- **Continuous-routine plate** (one take, a list of beats):
  - duration = ceil(1.6–2 × the prompted routine length);
  - put the must-have beats in its first half.
- Round up to the required integer duration, respecting the verified model minimum. Use the full required
  duration within the live supported maximum (historically 30 s), or split into sufficient jobs before
  pricing. Never clamp a longer sum to 15 s, truncate a routine or discard planned slots to fit a job.
- **The prompt's timecodes `Shot n (a-bs)` are these slots.**
- **Never copy duration 15 from the verbatim Katana prompts** (`references/generation.md` G7). They ran
  as 15 s plates in a project that generated 11× what it used. Re-time their shot list to your slots.

Examples:

| Plate                                                                  | Needed on screen     | Slots                             | Duration                                                                                                                                                                                       |
| ---------------------------------------------------------------------- | -------------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Katana-like dance plate, 5 shots                                       | ≤1 s each            | 5 × 2 s                           | 10 s (70 @720p, 120 @1080p). VERIFIED live 2026-10-08: the five 2 s shots changed almost exactly on their timecodes (241 frames at 24 fps), and this one plate served the whole 10.5 s rebuild |
| 4 shots                                                                | 0.8, 1.2, 1.5, 0.5 s | 2 + 2.4 + 3 + 2 = 9.4             | 10 s                                                                                                                                                                                           |
| Aura G-like climax insert, 1 shot                                      | 1.04 s               | clamp(2.08, 2, 4) = 2.08 → ceil 3 | 4 s (the minimum): 48 @1080p                                                                                                                                                                   |
| Yaong B-like routine prompted in 5 s, hearts moved into the first half | —                    | ceil(2 × 5)                       | 10 s                                                                                                                                                                                           |
| Yaong F1-like duo                                                      | 0.89 s               | clamp(1.78, 2, 4) = 2             | 4 s (the minimum)                                                                                                                                                                              |

Write repeated choreography once. Seedance ignored "repeat the routine 4.5–9 s" in Yaong A1, and nothing
after 4.89 s was used.

Shot changes land on the slot timecodes (VERIFIED above); gestures inside a shot still run 1.5–2× slow,
which is what the ×2 in the slot formula covers.

### 4.4 Minimum billable durations

Minimum billed duration does not prohibit a dedicated job for a short output cut:

- Seedance 2.5: 4 s (int 4–30);
- Genjutsu transformations: ~4 s historically; verify the actual supported contract.
- Optional Genjutsu preset transformation: derive duration limits from the verified chosen workflow
  contract. Use Restyle parameters only if that actual preset route requires Restyle; never infer an
  undocumented model or use another fresh-video generator.

A 1.2 s cut on its own pays for at least the verified minimum. Group it into a plate only when the
required composition, motion, timing and locks remain equally faithful; otherwise price a dedicated
job and keep the planned short interval in the final edit. Do not group Genjutsu cuts for efficiency.

### 4.5 Genjutsu driving clips (billed by the probed driving-video seconds)

**Recipe** (all in the sandbox):

1. **Export at 24 fps:** `python3 $RR/frames.py export $W --cut cNN --fps 24 --crop window`.
   - This resamples by time.
   - Mute the clip and preserve burned captions, graphics and source geometry by default. A clean
     intermediate is allowed only with saved original layers, measured timing and a reversible geometry
     mapping for exact restoration; never crop away scene content or alter faces/heads to remove text.
2. **Pad:**
   - cuts shorter than 4 s of real time: `python3 $RR/frames.py pad $W/cuts/cNN.mp4
     $W/gen/cNN_pad.mp4 --mode pingpong`, which gives exactly 96 frames;
   - longer parts: `--mode freeze`, applied only when the rounding rule below says so (`--for mt` on an MT
     part applies the ≤ 0.1 s rule; the default `--for replace` always pads to ceil).
3. **Verify before upload:**
   - the probed duration is the intended integer seconds (±0.01 s). The one exception is an unpadded MT
     part whose fractional second is ≤ 0.1 s (see the billing rules below);
   - there is no audio stream (an audio stream can make the container longer).
   - Price the clip from its PROBED frame count.

**Never pad a native-fps export of a 25/30/50/60 fps reference.** `pad` exits 2 on an fps mismatch
unless `--retime` is given, because the frames would be re-timed and the bill inflated:

- a 30 fps cut of 3.5 s (105 f) padded as-is → 120 f = 5.000 s → 55 instead of 44 @1080p;
- a 60 fps cut of 3.9 s (234 f) → 240 f = 10.000 s → 110 instead of 44.

**Billing rounds differently per model:**

- **Replace bills ceil(seconds),** so always trim or pad to an exact integer. 96 frames = 4.00 s = 44
  @1080p. 100 frames = 4.17 s → 5 s = 55; never pad to 100.
  - VERIFIED live 2026-10-08 (Altman c12): the 60 fps cut (35 frames) exported at 24 fps gave 14
    frames, the ping-pong pad made exactly 96, and the 720p replace was charged exactly 28. An exact
    4.00 s pad bills 4 s.
  - The output is not 96 frames: that job returned 89 frames (3.71 s) at 24 fps. `assemble.py` maps it
    back proportionally (`gen_index = round(padded_index × gen_frames / padded_frames)`); never assume
    the output length equals the pad.
- **MT bills round(seconds):**
  - fractional second ≤ 0.1 s: do not pad. Fill any missing tail only with verified transformed footage
    or a hold that satisfies the shot's timing/motion and identity locks; otherwise report the gap or
    use a bounded permitted correction. Original pixels are eligible only when verified to contain no
    targeted change and to satisfy every applicable lock; never reintroduce the original target.
    Aura D: 266 f = 11.08 s → 11 s = 121, accepted with the cuts within ±1 f.
  - otherwise: freeze-pad to ceil (Aura H: 9.58 s → 10 s = 110).
- **Do not hold-pad** by repeating frames: it broke the pose in Altman.

**One clip per cut, or one take per film:**

- **SWAP is per cut,** on 96-frame pads. A cut of 4 s or more is trimmed or freeze-padded to an exact
  whole second.
- **One full-length take applies to REPERFORM (MT) only,** for references up to ~11 s without burned
  graphics. Aura D's full take kept the cut grid; its halves came back retimed.
- **Otherwise per part,** at the reference's own cuts. Parts pay their own rounding: Aura G was
  6 + 5 + 8 = 19 s = 209 at 1080p, not 16.92 s → 17 × 11 = 187.

### 4.6 Mattes

- Order mattes only after the EDL exists, and only for clips used with cut-outs, contours or
  behind-subject text.
- Run one matte on one clip before ordering the rest.

### 4.7 Whole-reference passes (UNTESTED experiments, excluded by default)

A whole-reference `seedance_2_5` video_edit or whole-reel Genjutsu replace remains
unverified for frame-exact reproduction. Do not add experiments or preview purchases to a faithful
remake by default. Use one only when already explicitly requested, with a verified compatible tool
contract and all costs inside the existing cap. Otherwise continue the proven per-cut reconstruction.
The historical 480p experiment estimate was 3 cr/s × ceil(reference seconds), not a current quote.

## 5. Resolution policy (per job, measured in the delivery frame)

**First fix the delivery frame.** Use `plan/creative-plan.json` -> `output_target`. EXACT defaults to
the reference's pixel size unless the user changes it. REMIX derives the target from explicit format
instructions, intended presentation and reference evidence before pricing; source dimensions are
evidence, not a mandatory output size. Do not inflate the canvas or add needless cropping just to
justify a more expensive generation. Once selected, measure every job against the real planned output.

Then decide per plate or Genjutsu job, in this order. Do NOT ask for a resolution at intake.

1. **An explicit mandate wins.** Only explicit words are a mandate: "1080p", "4K", "max quality".
   "Good quality" is not one.
   - Katana mandated "1080p high" even though its threshold look hid it. Altman's "1080 гоу" was
     explicit too.
2. **720p is a candidate, subject to visual fidelity checks,** in these cases:
   - the delivery frame is ≤720 px wide, or its short side is ≤720 px (900×720, 960×720, 1280×720,
     720×1280): the 720p output already covers it at about 1× or more;
   - the picture is windowed or letterboxed;
   - the look is heavily stylised: threshold / xerox, posterise, halftone, pixelate, heavy blur or glow,
     VHS / datamosh, crushed B/W, heavy grain.

   Evidence: /test-edit's letterboxed 1080×608 picture used 720p and saved 150 cr (−42%) with no
   visible loss. Katana's 1080p was invisible under its xerox threshold (270 s × 5 cr/s = 1,350 cr
   premium).

3. **Full-frame MT on a deliverable ≥1080 px tall → 1080p by default.** A 4:3 MT take cover-cropped to a
   1920×1080 canvas gives k720 = 1920 ÷ 1112 = 1.73, while at 1080p it is 1920 ÷ 1664 = 1.15.
4. **Every visible detail: the k rule plus actual fidelity checks.**
   - Measure in the DELIVERY frame (`output_target`; source size by default only in EXACT).
   - k720 = the generated picture's visible width in that frame × the largest code punch-in on the shot ÷
     the 720p output width.
   - **The punch-in is the actual planned zoom**, observed in the reference for EXACT or deliberately
     authored for REMIX. Count its real pixel demand. Framing comes from source media for Genjutsu;
     image/Seedance generation may describe a new required shot size without a needless rescue crop.
     Fix an incorrect source/frame selection before compensating with a larger resolution; do not add
     camera scripting to the Genjutsu prompt.
   - 720p output widths: Seedance 4:3 = 1112 (1112×834, VERIFIED live 2026-10-08), 16:9 1280, 9:16 720.
     Genjutsu follows the driving clip's aspect: a 994×830 window pad came back 1054×880 at 720p
     (VERIFIED). Confirm the size on the canary.
   - Treat k720 ≥ 1.3 as a signal to inspect a higher-resolution supported output. Compare every
     visible requirement: faces, hair, hands, fabric, props, small text/logos, linework, grain structure,
     silhouettes, glints and transition texture. A readable face is one cue, never the only cue.
   - Select **1080p** or another actually supported setting whenever lower resolution loses required
     detail, including shots with no visible face. Use 720p only when required output detail
     survives the final crop and motion. Absence of a face never justifies a downgrade.
5. **Otherwise test 720p coverage and detail; choose the required available resolution within the cap.**
6. **480p** is not a substitute for higher-resolution reference footage. Do not buy extra previews. A
   Seedance draft bills at the 480p rate, but its finalize is always 1080p (§2.3).
7. **720p + `bytedance_video_upscale`** is UNTESTED for quality and excluded by default.
8. **Genjutsu:** the same rules apply (7 vs 11 cr/s).

Worked examples, each measured in its delivery frame:

| Case                                                                           | Delivery frame                                     | Arithmetic                                                                                                                                | Result                                                            |
| ------------------------------------------------------------------------------ | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Yaong: identity-legible selfie close-ups, the reference's own zoom punch ≤1.5× | the reference's own 900×720                        | short side 720 (rule 2). Cross-check: k720 ≈ 900 × 1.5 ÷ 1112 ≈ 1.21 (≈ 1.29 counting the 4:3 cover-fit overhang, 960 × 1.5 ÷ 1112) < 1.3 | **720p** for every plate, the identity-legible close-ups included |
| Altman: 996×836 window                                                         | 1080×1920 canvas, picture in a window              | windowed (rule 2). Cross-check: k720 = 996 ÷ 1054 (the real 720p replace output) = 0.94                                                   | **720p**                                                          |
| Full-frame 9:16 face close-up                                                  | 1080×1920, the reference's own size                | 1080 × 1.0 ÷ 720 = 1.5 ≥ 1.3, face legible                                                                                                | **1080p**                                                         |
| Katana real run: xerox threshold                                               | rendered at 1440×1080 (1.5× the 960×720 reference) | threshold (rule 2); k720 = 1440 ÷ 1112 = 1.29 < 1.3 anyway                                                                                | **720p** (VERIFIED live 2026-10-08, §10 "Measured run")           |
| Yaong delivered at 1440×1080 because the user asked for that size              | 1440×1080                                          | 1440 × 1.5 ÷ 1112 ≈ 1.94                                                                                                                  | 1080p, only because of the user's choice                          |

The estimate states the selected resolution and fidelity reason for every video line. Choose it
autonomously; do not add a resolution-upgrade menu. A low-cost route that visibly loses detail fails QA.

## 6. Takes and re-rolls

### 6.1 Takes

- **Default: 1 take per job.** It held up in Altman (every correctly padded, non-IP-blocked replace
  take was used: 12/12), Yaong (3/3 completed plates used), Aura Genjutsu (10/13 used) and the
  2026-10-08 run (1/1 plate and 1/1 swap used, VERIFIED). It is still
  UNTESTED as a controlled comparison for Seedance.
- Additional full takes are excluded by default. Include a second full take only when planned output
  coverage requires it, the need is documented, and existing spend authority covers it. Otherwise use
  the single planned take plus a bounded failure re-roll; never present a take-selection menu.
- **"To choose from" and "just in case" are not reasons.** Katana's identical second takes cost
  1,620 cr.
- **Never run parallel spare takes.** Aura's spares cost 297 cr. One H take finished after the render
  and was never used.
- **Variants after completion** require a new user instruction; never propose them as an approval gate.

### 6.2 Re-roll scope

**The fail list** (the only reasons to re-roll):

- identity;
- wardrobe;
- garbled text or logo;
- anatomy;
- a matte-hostile background;
- a missing beat the EDL needs that no other plate second supplies.

"A better take" is not a failure.

**Code rescues come first.** Try soft levels, recasting to other source seconds of the same or another
plate, a drawn overlay, or reusing a black wipe.

**(a) Shot failure:** a planned shot fails a check from the fail list.

- Re-roll that shot alone as a single-shot job of max(4, ceil(2 × its slot)) s, at the same resolution.
- A 2 s slot → 4 s (28 @720p, 48 @1080p).
- Yaong B1's hearts in a 3 s slot → 6 s (72 @1080p). A fixed 4 s re-roll of a gesture that runs 2× slow
  would fail again.

**(b) Job failure:** the canary, or any job where half or more of its planned shots fail for one cause.

- Fix the cause and re-run the whole job once. That uses the job's re-roll.
- For a Genjutsu cut job the job is the shot, so (a) and (b) are the same re-run.

Limits:

- **Re-roll spend per job** is at most that job's own cost, and only while both `guard` and the hard-cap check pass.
  - `ledger.py guard $W --line <id> --reroll-of <job> --reason "<fail-list item>"` allows one re-roll
    per job.
  - Add `--slot <slot seconds>` for a shot re-roll (a), so it is priced at max(4, ceil(2 × slot)) s. For
    a job failure (b), use `--reason "job failure"`.
  - If a plate has two failed shots that are fewer than half of its shots, re-roll the one the EDL needs
    most and rescue the other faithfully in code; report any unresolved beat.
- **Log every re-roll with its reason:** `ledger.py add $W --line <id> --job <new id> --reroll-of <job>
  --reason "<item>" [--slot S]`.
- **No second re-roll of the same job in this execution.** Continue with valid assets and state any gap.

## 7. Canary policy

- **Family = model + identity image set + set/world.** A new style line or new shot content is not a new
  family.
  - Seedance: one identity anchor on one white cyc is one family, however many plates it has. A new
    look made from a different identity image (Yaong look B) is a new family.
  - Genjutsu SWAP: one family per compatible source world/identity (replace, hero photo, the source). One SWAP canary covers
    identity and wardrobe.
  - IP-suspect films: one cut per suspected source film also goes into the canary call.
  - REPERFORM (MT): one family per world or source film.
- **Canary = a representative fidelity-critical planned job of each family,** at final settings.
  Prefer the lower-cost job only when it exercises the same identity, motion, wardrobe and text risks.
- **Submit canaries individually through guard → submit → add.** A reservation blocks the next
  submission until the actual job is recorded or provider evidence proves no job and no charge.
  Separate submitted jobs may process concurrently; each family's remaining jobs await its own canary.
- **Never add a canary job that serves no cut.** No extra 4 s "moderation canary": it is an additional
  paid submission, and a refusal does not guarantee a refund.
- **Subject replacement follows the selected per-output-shot route.** Image-first, STILL/CODE,
  Seedance and justified Genjutsu remain conditional alternatives; an identity change alone does not
  mandate SWAP. Apply these SWAP checks only to selected SWAP jobs. Preserve the intended subject
  otherwise; do not treat an IP concern as a reason to invent a replacement.
  - Put one cut per suspected source film into the canary call.
  - On `ip_detected`, do not route the same refused content to REPERFORM, another model, or altered
    wording to bypass the restriction. Retain an already-permitted source element when allowed, or
    mark the affected cut blocked. Retry only a genuine, permitted technical correction; otherwise
    continue unaffected work and state the limitation without a question. Verify any refund separately.
- **Look at the canary's `frames.py catalog` sheet,** never only at its status:

| Check                         | Fail sign                                                       | Fix (once)                                                                                                                                                                                                       |
| ----------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Preset recommendation         | provider returns a recommendation rather than a job             | Treat it as data; use only an already verified noninteractive contract. No hardcoded preset IDs, invented decline fields or user picker.                                                                         |
| nsfw                          | status nsfw                                                     | Respect the refusal; no wording/model changes to obtain the same refused content. Correct only an actual permitted technical issue, retain allowed source content, or mark the cut blocked. Verify any refund.   |
| ip_detected                   | status ip_detected                                              | No model/route switch to bypass refusal. Keep an allowed source element or mark the cut blocked; only genuine permitted technical corrections may retry. Verify any refund.                                      |
| Identity                      | face or hair or build drifts from the anchor                    | stronger anchor (two-panel sheet, in-world still), fewer competing refs                                                                                                                                          |
| Wardrobe                      | clothes copied from the photo (replace) or drifted              | Choose a supplied matching image/frame; reference media carry the look. For Genjutsu, use only a brief change instruction, never an itemized wardrobe script.                                                    |
| Background isolation          | an intermediate matte plate cannot be cleanly isolated          | use a clean temporary extraction plate only where necessary, then compose the planned world; EXACT restores required source backgrounds, props and graphics                                                      |
| Motion                        | gestures missing, too slow or too fast; retimed cuts (Genjutsu) | fewer shots per plate, a longer slot for the slow beat (§4.3); one full-length MT take (REPERFORM, §4.5)                                                                                                         |
| Baked text (Genjutsu replace) | the ref's text garbled or lost                                  | Restore only failed text from saved original pixels/layers at measured timing. A clean retry input is conditional on exact layer/geometry restoration; preserve source framing and never paint over a face/head. |

- **The same failure twice → stop.** Do not try a third time on that route. Reroute only within the
  video-model allowlist: fresh footage stays on `seedance_2_5`; verified Genjutsu transformations or optional presets may transform
  existing footage where appropriate. Otherwise use existing assets/code or a truthful partial.
  Recompute the estimate; do not remove required content or issue a question.
- A failed canary does not unlock its own family's batch. Other families continue.

## 8. Informative estimate and spending ledger

### 8.1 Estimate and plan schema

Complete the entire per-frame and per-second reference analysis, with no coverage gaps, then shot
routing, prompts and live pricing before submission. Show a concise
informative estimate with selected jobs, planned credits and the finite maximum including bounded
retries; continue without questions, approval requests, menus or waiting for a reply. Apply an existing
numeric limit if supplied, but do not require one.

Use only capabilities allowed by existing task/account authority. A mandatory interactive service gate
is a blocked route, never an instruction to request consent or start a picker. Use a supported authorized
alternative; otherwise deliver free work and a truthful declarative limitation. `ledger.py quote $W` is
an accounting report; it reports selected work and never requests consent or presents a menu.

Preserve the required `plan/gen_plan.json` fields supported by the bundled script:

- Check the video-model allowlist before estimation and submission for every job and batch item.
- Every job has a stable `id`, the output shots it serves, its verified operation/model, count/takes,
  and an exact live quote when ready or a verified current planning upper bound when deferred. Include
  mode, resolution, duration and aspect only where the actual
  operation accepts them. Source frame count/fps remain billing metadata for Genjutsu when those
  fields are not accepted provider parameters; price the actual probed driving frames, not nominal padding.
  Link observed source-cut IDs separately when relevant. Output and source IDs need not be one-to-one
  in REMIX; the ledger's existing cut-list field records served output shots, not a forced source mapping.
- A dependent line uses `deferred:true`, `depends_on:["<upstream line id>"]` and
  `input_bindings:{"medias.0.value":"<upstream line id>"}`. Only `medias.N.value`, `media_id` and
  `draft_job_id` are supported binding paths; their unresolved values must be explicit `<...>`
  placeholders. Bindings and `depends_on` cover the same selected upstream line IDs, with no cycles.
  All other request fields, prompts, settings, roles and count/takes must already be concrete.
- Identity-legible jobs retain `"identity": true`; this is metadata, not an upgrade request.
- Full-length MT jobs retain `"full_take": true`.
- A planned strobe job retains `"strobe": true` (source-derived in EXACT); select only necessary takes
  covered by the finite plan. A strobing reference does not force every REMIX job to strobe, and this
  metadata never adds takes automatically.
- Every Seedance line explicitly includes `"generate_audio": false` and `"bitrate_mode": "high"`.
- Suspected source-scene restrictions retain `"ip_suspect": "<source>"`; estimate any permitted fallback
  before committing it. Never bypass a refusal.
- The script understands `"optional": true`, `"take_reason"`, `"take_of"`, `"draft": true` and
  `"finalize": true`. Do not create optional user-choice lines in this workflow. Preserve inherited
  metadata if reading an existing plan; excluded optional lines remain excluded unless existing
  explicit authorization already selects them.

### 8.2 Finite plan registration and serialized submission

Read the task and existing account permissions. Compute an explicit finite `hard_cap` for all selected
workflow stages: exact ready-job quotes, verified current deferred-job upper bounds, and bounded retries,
capped by any existing `user_limit` or `account_limit`.
A numeric user budget is optional; no question or approval gate is created. Register with
`ledger.py approve $W --total <selected subtotal> --hard-cap <finite maximum> --note "<existing task/account authority>"`.
The legacy command name `approve` means internal plan registration, never human consent. The first
registration freezes the entire `workflow_ceiling`; activating a later stage cannot raise it or reset
prior spend. Do not forge authority or hand-edit registration/guard state. A plan containing only ready
jobs follows the existing exact-quote process unchanged.

**Dependent stages, such as image → video → matte:**

1. Include every necessary stage in the original plan. Mark only input-dependent lines deferred with
   the schema in §8.1. For example, a video's `medias[0].value` may be `"<result of hero_still>"`, with
   `"depends_on":["hero_still"]` and `"input_bindings":{"medias.0.value":"hero_still"}`.
   Verify the actual operation contract and all non-input fields now; never submit these placeholders.
2. Record each deferred job's verified current per-job upper bound using `price-set --planning --basis`
   and real estimator/account evidence (§2.2). The bound must cover the registered configuration without
   fabricated prices or paid probes. `quote` includes these non-executable jobs and their bounded reserve
   in the whole-workflow maximum. `params` and `guard` reject deferred lines.
3. Execute ready upstream jobs normally. After every named upstream line has a completed ledger job,
   replace each declared binding placeholder with its actual returned job ID, then set `deferred:false`.
   Each bound value must match a completed ledger job of its named upstream line. Keep the registered
   operation, prompt, settings, roles and count/takes unchanged; ordinary newly supplied media is not a
   substitute for the declared dependency. Activate a matte only when the EDL actually uses its clip.
4. Obtain a fresh exact quote for the actual completed input IDs and store it without `--planning`.
   Each exact per-job price must fit its original planning upper bound. Run `quote` and repeat `approve`
   with the updated subtotal and the unchanged `--hard-cap` before that line's normal guard/submission.
   Activation cannot expand the workflow ceiling. If the bound or a required capability fails, continue
   supported work or report the gap; never invent an estimate, buy a pricing probe or request consent.

A live returned `higgsfield_preset` wrapper is supported only when the recorded Genjutsu mapping is
exact: line model `genjutsu:<returned preset_id>` matches the actual request's `preset_id`, and the
fresh `verified_request` records the returned tool contract and its source. Never invent a mapping.

The exact maximum reserves at most one retry per required image/video job, capped at that job's price.
All actual image attempts, including failed attempts and retries, are limited to three per planned item;
one root job receives at most one retry. Refunded failures still count as attempts. Content refusals are
terminal for that content; no wording or model switch circumvents them.

For each ready or activated paid job, in this order:

1. Verify current tool/model schema and real input media, then run `ledger.py params $W --line <id>`.
   Use its exact request with the dedicated non-submitting estimator. Store the result using
   `ledger.py price-set $W --line <id> --credits <C> --source estimate_video_cost --evidence "<response reference>"`
   (images use `estimate_image_cost`; a supported account quote uses `verified_account_quote`).
   Exact quotes expire after 24 hours and are bound to the whole planned request, including prompt-file
   contents and any actual returned `declined_preset_id`. Native dollar prices must never be relabeled as credits.
   Quote JSON keeps full estimator precision for subtotal and maximum; use those exact values for
   registration, never a rounded manual subtotal.
2. Run `ledger.py params $W --line <id> --check '<actual request JSON>'`; the check includes model,
   media IDs/roles, prompt, aspect, quality and all parameters. Unknown contracts fail closed.
3. Run `ledger.py guard $W --line <id>`. It verifies the current exact estimate, registered settings,
   remaining attempts and explicit hard cap, then atomically reserves **one** job. `--jobs` can only be 1.
   No generation batches and no `guard --next` bypass are supported. Pending reservations prevent a
   second guard from reusing the same uncommitted allowance.
4. Submit that one request with count 1. Immediately run `ledger.py add $W --line <id> --job <returned id>`.
   This converts the reservation to recorded exposure before the next guard. Persist the workspace.

A bounded retry uses `--reroll-of <original job> --reason "<fail-list item>"` on guard and add. A changed
slot/duration needs its own exact non-submitting estimate with matching `--slot`, `--duration` or
`--frames` fields on `price-set`, guard and add. Retry cost cannot exceed the original job's price.
A retry keeps the registered operation/model, mode, resolution and quality; it cannot be used to switch
routes or increase registered image count/takes. A legitimate route change is a separately registered
plan within the existing hard cap, never a way to bypass a content refusal. Failed/refunded image
attempts still count against the original registered item count.
A cap/contract/attempt failure selects supported authorized alternatives, free work or a truthful partial;
it never starts a question, consent flow or user-wait state.

### 8.3 Accounting, supported commands and preset contracts

The generation plan is `plan/gen_plan.json`; exact quotes are in `plan/prices_override.json`; all
submitted jobs and any outstanding reservation are in `plan/ledger.json`. Preserve these with `rr_save`.

| Command                                                                                | Purpose                                                                                                                                              |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `quote $W`                                                                             | Informative whole-workflow estimate, including non-executable deferred bounds and bounded maximum; no menus or refusal reroute recipe                |
| `price-set $W --line ID --credits C --source estimate_video_cost --evidence E`         | Store a current exact one-job credit estimate; use the appropriate image/account source                                                              |
| `price-set $W --line ID --planning --basis B --credits C --source SOURCE --evidence E` | Store a verified current per-job upper bound for a deferred line; SOURCE is an image/video estimator or verified_account_quote, never a guessed rate |
| `approve $W --total N --hard-cap H --note S`                                           | Register the whole-workflow ceiling; repeat with the same H to activate exactly quoted dependent jobs within their original bounds                   |
| `params $W --line ID [--frames F / --duration S / --slot S] [--check JSON]`            | Prepare and strictly compare the current exact request; real inputs required                                                                         |
| `guard $W --line ID [--reroll-of JOB --reason R]`                                      | Reserve one job inside the hard cap; no percentage slack or generation batches                                                                       |
| `add $W --line ID --job JOB [--reroll-of JOB --reason R]`                              | Immediately record the one submitted job against its reservation                                                                                     |
| `release $W --evidence E`                                                              | Clear an unresolved reservation only after real provider evidence of no job and no charge                                                            |
| `status $W --job JOB --state S [--charged C] [--evidence E]`                           | Update actual status/charges; `refunded` and `bounced` require transaction/provider evidence                                                         |
| `use $W --job JOB (--screen-seconds S / --ref-only / --unused) [--reason R]`           | Record actual source use after the EDL exists                                                                                                        |
| `jobs $W` / `summary $W`                                                               | Show exposure, charges, refunds, use and waste                                                                                                       |

`--unplanned --reason R --quoted C` on add is emergency reconciliation of a job already submitted
outside this process, never permission to submit it. Such exposure still reduces the hard cap.
Failed/nsfw/ip_detected jobs retain their quoted or higher actual exposure until a matching refund is
verified; a failure status or later state rewrite alone never releases money. For a partial refund,
`status --state refunded --charged <remaining net debit> --evidence <matching refund>` retains that
remaining debit against the hard cap. Omit `--charged` only for a verified full refund. Unfinished jobs retain at least their quote even
if a partial zero charge was observed. Match transactions by model, timestamp and amount; never treat
account balance differences or unrelated-chat transactions as this project's spending.

Known call templates use canonical media roles. Ready background-removal lines bind their real `media_id`
and matching `params.media_type` to the documented utility request. Only declared input placeholders on deferred
lines may reach planning registration; no placeholder may reach executable params, a guard or a paid call.
Free work never needs or receives a paid submission reservation. The video callable also enforces its
engine allowlist independently of the price table's `kind`; classifying an engine as post-processing
never grants permission to use it. For supported audio, store the actual existing selected `voice_id`
and `voice_type` (Seed audio), or actual `dialogue` turns (ElevenLabs), on the plan line. These values
and supported voice settings are part of the exact quote fingerprint; unavailable selected voices
lead to source-audio reuse or a declared limitation, never a picker. An optional Genjutsu preset absent from those templates
requires a line's `verified_request` accounting record: exact `tool`, exact `params`, `operation:
"genjutsu_preset"`, actual contract `source`, fresh UTC `checked_at`, and `allows_empty_prompt:true`
only if that actual preset supports it. Its model identifier must be a real returned `genjutsu:<id>` or
the verified public `higgsfield/genjutsu/restyle/v1.0` contract, never an invented alias. The ledger uses
the exact supplied contract; it does not fabricate `generate_image` from a flat price. The operation also
needs a verified native-credit quote. If an API only supplies another currency, the credit-only ledger
cannot represent it and execution uses an available supported route or states the limitation.

### 8.4 Transport timeouts (double-charge trap)

If a `generate_*` call times out or returns no job ids, the submission outcome is UNKNOWN.
**Never resubmit blindly.** Do this instead:

1. Call `transactions` (size 10) and look for a charge for that model in the last minutes.
2. Call `show_generations` with `only_completed:false`, the right `type` and size ~10, and look for
   jobs with that model and prompt. It is the only job listing; it renders a gallery widget, which is
   acceptable for this recovery.
3. If a job exists: `ledger.py add` it and `jobs_wait` it.
4. Keep the reservation while the outcome is unknown. Only real provider evidence of no job and no
   charge permits `ledger.py release $W --evidence "<evidence>"`, followed by a new guard. A missing
   gallery entry alone does not prove that no job was created. Never retry the entire group.

## 9. Historical waste evidence

Historical projects show why redundant video purchases, native-fps driving pads, premature EDLs and
untested full-reference passes are costly. One project generated 270 seconds for about 24 usable
seconds; another billed a 4.17-second replace pad as 5 seconds. Exact 96-frame, 24-fps pads billed as
4 seconds in the 2026-10-08 test. These observations support sizing and accounting rules, not copying
those projects' cast, wardrobe, prompts, optional purchases or approval flow.

## 10. Historical budgets and measured run

Prices below are historical evidence only. The operative estimate always uses current the dedicated cost-estimation tool.

| Family / historical run         | Measured result                                                                                         | Practical limit                                                               |
| ------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| F1a per-cut replacement         | 96-frame pad at 720p charged 28 cr; returned 89 frames                                                  | Map real output duration back to the reference grid                           |
| F1b motion transfer             | 11.08-second driving take billed 11 seconds at 11 cr/s = 121                                            | Reference-sized finishing and caption reconstruction still required           |
| F2 measured 10.5-second rebuild | Identity still 0.12 + 10-second 720p plate 70 + matte 1 = 71.12 used; draft probe 12 made 83.12 charged | A previous useful test is not proof of exact reproduction for a new reference |
| F3 real-footage montage         | 0 generation credits; only a draft delivered                                                            | Zero credits does not establish completeness or fidelity                      |
| F4 user-footage edit            | 0 generation credits                                                                                    | Available shots must actually cover the reference                             |
| F5 photo series                 | 250 unique stills at historical 0.5 / 1.5 cr = 125 / 375 cr                                             | Count unique frames after legitimate reuse and respect the existing cap       |

The 2026-10-08 paid test ledger reconciled 83.12 + 28 = **111.12 cr** with transactions. Do not reuse
this historical total as authorization for another job.

## 11. Account allowance without consent requests

When the live contract defines `use_unlim:false` as ordinary existing-credit billing, set false from
already-established task/account credit authority to avoid an unnecessary allowance picker. This does
not create new spending authority. Set `use_unlim:true` or `use_free_gens:true` only from an applicable
existing explicit allowance choice verified against live entitlements. Never start a trial or switch
to an uncovered payment source. If the server still requires genuinely fresh interactive consent or
returns a choice that existing authority cannot resolve, do not bypass it, open a picker, relay its
question, request approval or wait for the user. Use an already-authorized supported alternative within
the finite cap; otherwise continue free work and deliver a declarative limitation. A rejected allowance
is not permission to buy credits or change subscriptions.

## 12. Token and agent cost (not credits, still real)

- Katana's edit design + two QA Workflow runs used **5.56 M subagent tokens**, ~1,300 tool calls and
  ~100 min. Round 1's strict sticker planner introduced a regression (~27 of 54 stickers placed) that
  round 2 had to undo. Every one of the 65 fixes was code.
- Brazil used >4.5 M agent tokens and ~3 h 10 min for a draft. A 67-agent shootout launched before v1
  was delivered, and nothing from it reached the draft.
- Rules:
  1. **One QA round** (parallel reviewers allowed), then a **regression check against the previous
     render** (same frames side by side). No second review round unless the first found blocking
     issues.
  2. Spend extra agents on the breakdown (>~25 cuts) and the plate catalog, not on repeated review.
  3. Use at most five parallel agents for this workflow, within the runtime limit; do not add a fan-out approval gate.
  4. Lock format, timing, music and grade before spawning editors or collectors. Give collectors a
     per-slot list with counts and a stop condition.
