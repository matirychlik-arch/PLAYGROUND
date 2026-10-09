# Generation cookbook for reference-led footage

## Execution contract

Read `analysis/task-contract.json` (`mode`, `mode_reason`, `explicit_locks`, `creative_freedoms`) and
`plan/creative-plan.json` before choosing jobs. REMIX is the default for a new independent deliverable,
including “remake” or “same vibe/style”; EXACT needs an actual request for 1:1, the same edit, only a
subject replacement or equivalent preservation. Negated/quoted phrases do not switch modes. Continue
the chosen mode until newer actual user steering changes it. A REMIX can contain scope-specific exact
locks. This creative `mode` is distinct from a provider API mode such as `omni_reference`.

In REMIX, preserve the intended identity, explicit locks and selected source visual grammar while
authoring a new story/visual motif, scenes, text, framing and duration. Route the authored **output shot
IDs**, using suitable existing footage first, necessary image preparation second and Seedance 2.5 for
missing new scenes. Do not make motion transfer the default for people. Genjutsu is justified by a
selected local transformation or a particular required source movement. In EXACT, preserve the source
shot-by-shot except explicitly changed elements. The recipe's source-lock language applies to EXACT
and local exact-locked edits; a new REMIX scene follows its authored shot specification.

**Mandatory complete-reference gate.** Before finalizing any generation plan or submitting any video generation, complete [reference analysis](analysis.md): decode the entire source on its native frame grid, inspect every native-frame sheet, and finish the per-second log covering the full timeline with no unexamined interval. Sparse keyframes, a few sampled seconds, a scene summary or an uninspected frame export do not satisfy this gate. Read the full source audio too. Any unreadable section remains explicitly unresolved; do not fill it with guessed production defaults or start dependent generation.

Keep exact observed start/end/peak frames, intensity, texture scale/direction, blend/opacity, font
geometry and cadence in `analysis/breakdown.json`. In EXACT, reproduce those mechanisms, including
overlaps, without a cleaner generic substitute. In REMIX, `plan/creative-plan.json` records the selected
grammar, its source evidence and authored output timing; observations are not rewritten as invented
events. Each job serves a necessary output role or exact source requirement. Hidden-face identity
continuity still matters. A QA score never guarantees 1:1 reproduction or closes unexamined details.

**Video model lock.** New video footage, drafts, retries, extensions and newly generated motion use only `seedance_2_5` (Seedance 2.5). Never substitute another Seedance version, Kling, Veo, Wan or an aliased video engine to save time or credits. Before every estimate and submission, including each batch item, verify this allowlist: fresh video = `seedance_2_5`; a selected source-anchored local subject replacement = `hf_mult_replace_object`; a shot requiring particular source motion/re-performance = `hf_mult_motion_control`. Anime and stylized identity replacements do not require Genjutsu presets: prefer the two-reference image route in G4 when it preserves the source more faithfully. Genjutsu presets or Styles are optional fidelity routes only when their verified contract fits the requested change; never force a restyle or an extra paid job. Never invent or interchange a catalog preset ID, Styles model or API parameter. Image models remain available for still images and identity/keyframe preparation; Seedance 2.5 is used only for video. Post-production utilities, `sam_3_video` segmentation, `remove_background` and local masks are allowed; the model lock restricts newly generated creative scene footage, not masking or processing existing footage. Load [Genjutsu routing](genjutsu-routing.md) for celebrity-source edits or anime/Styles transformations before choosing that route.

**Genjutsu prompt limit.** For direct Genjutsu edits and optional Genjutsu presets, write one short sentence, at most two and at most 40 words. State only the operation and a small preservation rule; the supplied media carries identity, appearance, style, scene and choreography. Do not re-describe demographics, wardrobe, camera, effects or every object unless a minimal target distinction is required. A preset may use an empty prompt when its verified contract permits it and selected preset + inputs already specify the result. This limit does not apply to the two-reference image-edit prompt or detailed Seedance 2.5 timing instructions.

**Celebrity and anime references.** A celebrity appearing in supplied source footage is not a categorical reason to refuse or replace the person with a generic lookalike. Preserve the original source when unchanged, and use the appropriate supported source-anchored Genjutsu route for requested edits. For a local anime/stylized character replacement, prefer the source frame plus uploaded user identity in an image model, preserving source style, texture, pose and camera. New REMIX scenes instead use the authored scene geometry and explicitly assigned style/identity ownership. Use the resulting still with code, or Seedance 2.5 only where new motion is required; direct Genjutsu motion transfer is appropriate when exact driving choreography requires it. A Genjutsu preset is optional, and an anime reference alone never authorizes a forced restyle. Do not describe generated celebrity scenes as genuine archival footage. Never disguise identity, remove evidence or switch routes to defeat an actual content refusal; unsupported changes remain a declarative limitation with no question.

In EXACT, the reference owns subject, face, wardrobe, props, composition, text, logos, audio, frame
grid and effects except named changes. In REMIX, explicit locks and the authored shot plan own those
choices; a portrait supplies identity, not automatic clothing, lighting or background. Keep the user's
intended hero across every output appearance, including hidden faces. For a local subject replacement,
all other source details remain locked. Full regeneration covers every required output shot; automatic
KEEP cannot reduce either scope. Reuse actual suitable source pixels/audio where the contract permits.

**Never change a face in code.** Do not use Python, OpenCV, Pillow, Canvas, ffmpeg filters, mesh/landmark
warps or local pixel editing to replace a face, blend identities, repaint or paste facial parts, change
expression/eyes/mouth/nose/jaw, retouch skin, beautify, or apply face-only color/lighting corrections.
Required identity or facial changes and generated-face defects use a verified authorized image-editing
model, the appropriate Genjutsu transformation, or Seedance 2.5 for new footage, within the existing
attempt/cost limits. Missing capability or budget never authorizes a code-based face substitute.
Code may track coordinates, move/rotate/uniformly scale an entire unaltered frame or subject layer,
refine its outer matte edges, and apply whole-shot grades or separate graphic/text overlays: measured
source layers in EXACT, authored layers consistent with the selected grammar in REMIX. These operations must not reshape or reconstruct the face beneath them; a face crop is for
inspection/reference preparation, not a patch to paste onto a different head.

Never ask intake, taste, character, voice, font, budget or approval questions, and never open a consent or selection widget. Infer production choices from the reference and choose the closest matching result internally. No waiting-for-user state is permitted. If a required asset, capability, account authorization or mandatory service consent is unavailable, do not bypass the requirement: use an already authorized faithful supported fallback or report the dependent branch as blocked or partial declaratively. Continue independent work.

Before any paid work, live-price a finite plan of required jobs, one take each, with a bounded retry reserve. Use existing task authorization under account and platform rules; a numeric user budget is optional. Apply any user cap or account spending limit, record the actual authorization, and set the internal ceiling to the required quoted plan plus bounded reserve. Continue automatically within that ceiling without confirmations or option menus. Internal ledger registration is not fabricated user approval. No purchase, top-up, subscription or discretionary experiment is implied. Unknown prices or permissions cannot authorize a paid submit: use an already authorized faithful fallback or report the blocked branch declaratively. At most three still attempts and one corrective video retry are allowed within the plan; never increase its ceiling autonomously.

Price the entire dependent workflow under [budget.md §8.2](budget.md): ready jobs need exact quotes;
jobs waiting for generated inputs use verified current planning upper bounds and remain non-executable.
The first registration fixes the whole-workflow ceiling. Actual-input activation never resets spend or
raises that ceiling; no invented IDs, guessed prices or paid pricing probes are permitted.

The API examples are request shapes. Resolve the current operation and contract from available tools before any call. For image/video costing use the dedicated non-generating estimate operation (`estimate_image_cost` / `estimate_video_cost` where available), never an unverified `params.get_cost` field on a generation call. Audio supports `generate_audio` with `get_cost:true` only when its live contract says so. References below to a cost preflight mean that verified non-generating operation. Current contracts govern roles, batch limits and model IDs; the historical observations are not fresh verification.

This file covers _how_ to generate once `routing.md` has decided _what_ to generate. Every recipe gives
the model id, a params shape, historical price (2026-10-08; re-price through the current estimate operation), the count policy, when
to use it, and the prompt. Where the prompt actually produced accepted or used footage, it is quoted
**VERBATIM**. Anything that has not been run is marked **UNTESTED**. Sibling docs named here
(`routing.md`, `budget.md`, `mcp-api.md`, ...) are `references/<name>.md`, read with
the available skill-resource reader or the local package path. Do not invent an unavailable bundle tool.

Status labels:

- **PROVEN**: used in a shipped or approved film, with the project named.
- **WORKED**: the output was usable, but the film it went into was not accepted, or its acceptance is
  unknown.
- **UNTESTED**: reasoned from the evidence, never run.
- **VERIFIED (live 2026-10-08)**: seen in the paid test run of this workflow on 2026-10-08 (a Katana
  remake with one Seedance plate, and an Altman SWAP cut; 111.12 cr, reconciled exactly with
  `transactions`).

**VERBATIM prompts are someone else's project. Copy the structure, never the identity items.**

- Every VERBATIM block below belongs to a past user's hero: Katana's lime wig, micro shorts, cross
  thigh-highs, green lipstick and katana; Yaong's striped top, bangles and mop-handle backstage; Altman's
  boxer. None of it belongs in a new user's prompt.
- Take from an example: the block order, the sentence types (identity-lock sentence, inventory, style
  line, timecoded shots, closing exclusion), the observed structure and technical lessons.
- Identity and explicit locks come from the current request and its authorized references. EXACT
  wardrobe/props/scene details come from measured source observations; unlocked REMIX details come
  from `plan/creative-plan.json`, with their reference grammar recorded. Never silently import a
  portrait's clothing/background or a historical example's styling.
- Leak check before every non-generating estimate (§5 check #10): read the prompt against the example you
  started from; any garment, prop, colour or place that came from the example and not from this user is
  a leak. Evidence: a dry-run eval copied Katana's micro shorts, green lipstick and cross thigh-highs
  into a different user's brief.

**Every params block below is a SHAPE, not settings.**

- `model`, `mode`, `resolution`, `duration` (for Genjutsu: the driving clip's length) and `aspect_ratio`
  come from the job's line in `plan/gen_plan.json`. They are written `"<from plan line>"`, or
  `"<from plan line: seedance_2_5>"` where the recipe fixes the value and the plan line must say the
  same. Never copy a value from this cookbook or from a VERBATIM project: Katana's 1080p and 15 s were
  that project's choices, not defaults.
- The plan line gets its resolution from `budget.md` §5, measured in the **delivery frame from
  `plan/creative-plan.json.output_target`**. EXACT retains source size unless explicitly changed;
  REMIX selects the output size for the brief before pricing. Test 720p coverage and fidelity
  against all visible source detail, including texture, lettering, silhouettes and props. Face readability
  and a 1.3× upscale are useful risk signals, not the sole criteria. Windowing, letterboxing or a stylized
  grade does not automatically justify lower resolution. Use the required supported resolution within
  the cap; never hide a loss of detail behind the absence of a visible face. Historical examples:
  - Yaong, a 900×720 reference delivered at its own size → 720p (the eval that measured it in a
    1440×1080 frame bought 1080p plates for +109 cr nobody would see);
  - Altman's 996 px window → 720p (996 ÷ 1112 < 1; windowed anyway);
  - a full-frame 1080×1920 face close-up → 1080p (1080 ÷ 720 = 1.5);
  - Katana remake, 1440×1080 delivery: the 720p 4:3 plate is 1112×834 (VERIFIED live), a 1.29× upscale
    at full frame under a xerox look → 720p; it shipped that way.
- The plan line gets its duration from `budget.md` §4: plate slots, or the driving clip's seconds.
- `python3 $RR/ledger.py params $W --line <ID>` prints the exact request for a ready or activated line.
  Its prompt and real media IDs must already be in the plan. `--check '<params json>'` compares what
  you are about to send with the line (exit 1 = mismatch). Deferred lines are rejected, not executable
  skeletons to fill with invented upstream IDs.
- Every Seedance call carries `"generate_audio": false` and `"bitrate_mode": "high"`. High bitrate is
  free. **They are plan fields too:** every Seedance line in `plan/gen_plan.json` states
  `"generate_audio": false` and `"bitrate_mode": "high"` (and `"draft": true` only on a draft line), so
  the quote, `params` and `--check` all see them. `ledger.py quote` warns when a Seedance line lacks
  them; fix the line, do not rely on defaults (the model default is audio ON). Plan line shape:
  ```json
  {
    "id": "plate_A",
    "stage": "canary",
    "tool": "generate_video",
    "model": "seedance_2_5",
    "mode": "omni_reference",
    "resolution": "<budget.md §5>",
    "duration": "<Σ slot_s>",
    "aspect_ratio": "<output target or exact format lock>",
    "count": 1,
    "generate_audio": false,
    "bitrate_mode": "high",
    "identity": true,
    "refs": ["@image1 source-aligned frame", "@image2 identity-only reference if needed"],
    "prompt_file": "plan/prompts/plate_A.txt",
    "serves_cuts": ["o03", "o05"],
    "screen_seconds": 4.6
  }
  ```
  `serves_cuts` retains the ledger's field name but contains output shot IDs in REMIX. Store observed
  source cut IDs separately in route evidence; in EXACT output IDs may match source cut IDs.
- Pre-submit check #9 (§5): the params equal the plan line. A mismatch is unplanned spend: stop.

MCP mechanics are in `mcp-api.md` and prices in `budget.md`. The short version:

- **Count.** Use `count: 1` for every image, video and audio request. Select results internally; never open a character or voice selection gate.
- **Attempts.** At most three attempts per still need and one corrective retry per video job, within the finite priced plan and remaining authorized spend. Stop the paid branch when either bound is reached. Reuse matching source material or report the unresolved mismatch without a question.
- **Price check.** Use the live non-generating image/video estimate tools. Ready/activated requests need exact quotes for their real inputs and settings; dependent stages need verified current per-job planning bounds before initial registration, then exact actual-input quotes before execution. A planning bound is never permission to submit. A quote is not a generation-readiness or moderation pass. Do not use paid generation as a pricing probe.
- **Preset hijack.** A call (or its preflight) can return `Preset "IN THE DARK" was recommended…` and no
  job. The bounce costs nothing.
  - Resubmit ONLY the bounced items, with identical params plus the `declined_preset_id` read from the
    response. So far it has always been `24bae836-2c4a-48e0-89b6-49fcc0b21612` (IN THE DARK).
  - It hit 10/18 Katana requests, 5/5 Yaong, and recurring Altman and Aura MT batches.
  - VERIFIED live 2026-10-08: the verified non-generating estimate on the Altman swap prompt returned the IN THE DARK
    `preset_recommendation` for free, and the bounce reproduces on the real submit unless that item
    carries `declined_preset_id`. So the preflight result decides the submit params: a prompt that
    bounced in preflight is always submitted with the id read from that preflight.
  - Passing it pre-emptively on items that did not bounce is UNTESTED (mcp-api §11).
- **Serialized submissions and job polling.** The platform supports up to 6 batch items (or its smaller live limit), but this workflow submits exactly one paid request per ledger reservation. Reserve, submit that exact request, then immediately register its returned job ID before reserving another. Linked atomic batch reservation is not supported; do not run several guards and then send a multi-item batch.
  - Multiple jobs may remain pending after their individual submissions are registered. Between `jobs_wait` polls, do reference-side work: text layers, `fx.js`, the audio map and QA preparation.
  - Do not finalize the footage catalogue, in-points or EDL until every submitted paid job in the planned group is terminal and accounted for. A late job must be catalogued before rendering.
- **Refunds require verification.** `nsfw`, `ip_detected` and `failed` jobs are charged at submit and were
  refunded automatically within ~5 s–4 min on this account (VERIFIED from its records, mcp-api §13).
  These are historical observations, not a refund guarantee. Keep each debit charged against the plan
  until its refund is verified; completed unusable footage also consumes the budget.
  - Report a current refund only after verifying it in current `transactions`. If unresolved, report the debit and unknown refund status; never repeat a historical account claim as a current result.
- **Canaries** (`budget.md` §7). The canary is the planned job that covers the family's hardest fidelity constraints, submitted alone
  at the final settings, so a pass is usable footage.
  - A family is model + identity image set + set or world. A new style line or new shot content is not a
    new family.
  - Submit each family's canary through its own reservation → single request → immediate ledger registration. Each family's other jobs wait for that canary to pass; never submit a multi-item canary batch.
  - Never add a canary job that serves no cut.
- **Timeouts.** After a transport timeout, never resubmit until you have checked the jobs: a resubmit can
  charge twice.
- **Allowance selection.** When the live contract defines `use_unlim:false` as ordinary existing-credit
  billing, set it from already-established task/account credit authority to avoid an unnecessary picker;
  this creates no new authority. Set `use_unlim:true` or `use_free_gens:true` only from an applicable
  existing explicit allowance choice verified against live entitlements. Never start a trial or bypass
  genuinely required fresh consent; use an authorized fallback or state the limitation.
- **Media.** `medias[].value` must be a media_id or job_id, never a URL.
  - Roles: Seedance and image models take `image` (Seedance also `start_image`).
  - Genjutsu takes `image` (at least 1) plus exactly one `video`. Send these current schema keys (mcp-api §6.2).
  - Confirm roles with `models_get` once per session.
- **Generated-input dependencies.** In the initial plan, mark a waiting line `deferred:true`, name
  `depends_on:["still_line"]`, and bind its explicit `<...>` input placeholder using
  `input_bindings:{"medias.0.value":"still_line"}`. Supported paths are only `medias.N.value`,
  `media_id` and `draft_job_id`; bindings and dependencies name the same selected upstream lines and
  form no cycles. All other prompt/settings/roles/count fields stay concrete and registered. Store a
  verified current upper bound with `price-set --planning --basis "<basis>" --credits <C>
  --source <estimate_video_cost|estimate_image_cost|verified_account_quote> --evidence "<actual evidence>"`.
  `quote` includes this non-executable stage in the fixed maximum; `params` and `guard` reject it.
  When all named upstream ledger jobs complete, replace each declared placeholder with its actual job ID,
  set `deferred:false`, obtain a fresh exact actual-input quote no higher than the original planning
  bound, and repeat `approve` with the unchanged `--hard-cap`. Then use normal params → guard → submit
  → immediate add. Unavailable bound/quote/capability selects a declarative gap, never a consent gate.
- **Where tech specs go.** Aspect ratio, duration, fps and resolution go in params, never in the prompt
  body (user memory rule).
- **Showing prompts.** When you show a prompt to the user, put it in one fenced code block.

---

## 0. Index

| #   | Purpose                                                                                                       | Model                                                              | Price today                            | Status                                                                                                          |
| --- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| G1  | Identity sheet from the user's photo                                                                          | `seedream_v5_pro`                                                  | 2.5 (2k)                               | PROVEN-ish: Katana. All 18 plates used it                                                                       |
| G2  | Fictional hero (UGC-real or fashion identity still)                                                           | `soul_2`                                                           | 0.12 / image                           | PROVEN-ish: Yaong; VERIFIED live 2026-10-08 (Katana remake identity, 2k 3:4 = 1536×2048)                        |
| G3  | Look or outfit change that keeps the face                                                                     | `seedream_v5_pro` i2i                                              | 2.5 (2k)                               | PROVEN-ish: Yaong look B                                                                                        |
| G4  | Source-frame + uploaded-identity image edit: stylized/anime replacement, finished still, keyframe or MT input | `gpt_image_2_5` or a verified selected multi-reference image model | Live estimate                          | Two-ref ownership required; runtime output unverified                                                           |
| G5  | REPERFORM still: the hero inside the cut's frame, as the MT image                                             | G4 selected multi-reference image model                            | Live estimate                          | In-scene still PROVEN (Altman, 3/5 won, text-described form); the default 2-ref form is UNTESTED as an MT input |
| G6  | Die-cut stickers                                                                                              | `seedream_v5_pro` + `remove_bg`                                    | 1.25 (1k) + unprobed surcharge         | PROVEN-ish: Katana, 30/30 clean                                                                                 |
| G7  | Multi-shot plate (new footage)                                                                                | `seedance_2_5` `omni_reference`                                    | 12 / 7 / 3 cr/s                        | PROVEN-ish: Katana, Yaong; VERIFIED live 2026-10-08 (10 s 720p 4:3 = 70 cr, 1112×834)                           |
| G8  | Per-cut clip when most faithful, including sub-second source cuts                                             | `seedance_2_5` start image                                         | 12 / 7 / 3 cr/s, min 4 s               | WORKED (/test-edit, 720p)                                                                                       |
| G9  | Person→person swap that keeps the plate                                                                       | `hf_mult_replace_object`                                           | 28 / 44 per 4.00 s pad at 720p / 1080p | PROVEN: Altman, 12 cuts; 720p charge of 28 on a 96-frame pad VERIFIED live 2026-10-08                           |
| G10 | Re-performance (motion transfer)                                                                              | `hf_mult_motion_control`                                           | 11 / 7 / 3 cr/s of driving video       | PROVEN: Aura D/G/H, Altman 5 cuts                                                                               |
| G11 | Mattes                                                                                                        | `remove_background` / `sam_3_video` / local masks                  | 1 / ≈1.14                              | PROVEN: Katana, Yaong, Altman, Aura D; remove_background 1 cr VERIFIED live 2026-10-08                          |
| G12 | Chant or VO                                                                                                   | `seed_audio` / `elevenlabs_v4`                                     | 0.3–2 / ≈0.23 per 30 chars             | PROVEN-ish: Yaong chant                                                                                         |
| G13 | Texture plates                                                                                                | prefer CODE; `gpt_image_2_5`                                       | 2.75 observed                          | PROVEN: Aura H paper                                                                                            |
| G14 | Seedance 2.5 motion previews                                                                                  | `seedance_2_5` with `draft:true` only                              | Historical draft rate: 3 cr/s          | Draft and finalize prices VERIFIED live 2026-10-08; preview fidelity UNTESTED                                   |

"PROVEN-ish" means the film shipped with no explicit approval recorded: Katana v2 has no verdict;
Yaong v2 got no revision request; Katana v1 was built upon.

---

## Asset ownership and optional prompt structure

Use role-based output slots from `plan/creative-plan.json`: for example hook, context, hero, action,
detail, contrast, payoff or release. Choose only the roles needed by the story/visual motif. Each
slot records its output ID, purpose, start/end state where relevant, screen duration, source evidence,
explicit locks and required assets. A visual montage need not invent a literal character goal.

Prepare a reusable hero, location or prop asset only when a real consistency/composition need cannot
be met by existing inputs. One suitable asset may serve several named output slots. No mandatory
character sheet, neutral studio, location count, draft purchase or extra image before every video.
Never erase, paint over or reshape a face/head with code to create a sheet; a needed model-generated body reference is a separate permitted image operation. Asset preparation uses supported image models;
Seedance 2.5 is reserved for video.

Assign **one explicit ownership per reference** rather than letting every image control everything:

| Input                                      | Ownership when selected                                                                                                          |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| User portrait/character                    | Intended identity and distinguishing traits; wardrobe, background and lighting only if explicitly assigned                       |
| Source frame in an exact/local replacement | Composition, pose, framing, source wardrobe, location, light, texture and untouched details                                      |
| Source style frame in a new REMIX scene    | Selected palette, texture, rendering or typography grammar; it need not dictate cast, pose or composition                        |
| Location reference/plate                   | Specified architecture, material and spatial landmarks; shot lighting/camera are separate unless explicitly locked to this plate |
| Prop reference                             | Design, proportions, material and actual markings; scene context only if assigned                                                |
| Accepted shot keyframe                     | Planned shot composition/start state; it does not replace the original identity check                                            |

Use the smallest sufficient set within the current tool's limits. G4's source-frame + identity baseline
uses two images; broader REMIX scene/asset preparation may use other verified reference combinations
only when their ownership and need are recorded. Never drop an exact structural reference to make room
for an unnecessary sheet, blend two people into one identity, or copy the portrait background by accident.

For image and Seedance prompts, include only fields that clarify the selected shot:

1. **Reference ownership and locks:** which image supplies identity, space, prop or selected style.
2. **Optional causal context:** what happened before and its visible trace; want/obstacle if there is a
   story; start state → meaningful end state. Omit irrelevant narrative fields for graphics or pure texture.
3. **Spatial map:** subject count, foreground/midground/background, screen positions, landmarks and
   motion direction when continuity needs them. Specify who acts and who remains unchanged.
4. **One legible action:** a concrete beat or state change. Multi-shot jobs give each slot its own
   action and time interval; do not cram an unrelated routine into one shot.
5. **Camera:** framing/angle and, only if needed, one move + dose + limit (for example, a short lateral
   move ending before the subject leaves the frame). A locked camera is valid; no compulsory movement.
6. **Light and texture:** selected source grammar and shot-specific motivated light/material response.
   Avoid contradictory ownership between a location plate and a separate light instruction.
7. **End constraints:** identity, intended cast, prop design, required text/graphics and continuity.
   Generated clean layers have a concrete later text/compositing plan; they do not silently remove locks.

EXACT fills these fields from observed frames instead of inventing new events. REMIX fills unlocked
fields from the creative plan and retains the selected visual grammar. Image prompts describe the
chosen still state, not a motion sequence. Technical duration/aspect/resolution stay in API params.
This structure is optional guidance, not a sentence-preservation template. It does not apply to
Genjutsu, whose operation prompt remains at most two sentences / 40 words.

## G1. Optional identity sheet (historical Seedream 5.0 Pro example)

- **When to use:** only when a measured identity-consistency problem requires an additional prepared
  anchor and a suitable supplied image or source-frame + identity edit (G4) does not already solve it.
  A small face or an F2 classification alone does not require a paid sheet. Never create one per cut.
- Preserve the assigned reference ownership. For EXACT/local replacements the source frame controls
  wardrobe, makeup, props, pose, light and setting; the uploaded portrait supplies identity only.
  REMIX sheets preserve the intended hero and planned wardrobe, without locking all future shots to
  one pose/background. A sheet does not replace a required source frame or original identity reference.
- **Params shape** (verify multi-reference support and actual settings for the selected image model):
  ```json
  {
    "model": "<verified image model from plan>",
    "aspect_ratio": "<planned sheet layout>",
    "resolution": "<from plan line>",
    "count": 1,
    "medias": [
      { "role": "image", "value": "<source frame media_id>" },
      { "role": "image", "value": "<authorized identity-only photo media_id>" }
    ],
    "prompt": "Prepare only the planned identity reference views. Image 1 supplies <assigned wardrobe/material/style ownership>; image 2 supplies identity only. Preserve <explicit locks> without importing the portrait background."
  }
  ```
- Record the necessary views. Do not claim unseen facial details or an outfit were observed in a
  cropped photograph; unlocked REMIX wardrobe must instead be explicitly authored in the plan. Compare the sheet to both inputs before reuse. Keep the original photo available for
  identity checks: historical sheets sometimes widened the face.
- Use a neutral isolation background only for a needed intermediate, never as the automatic final
  setting. Its background/light must not overwrite the exact source scene or authored REMIX scene.
- Reuse the sheet only where needed and supported. Source-aligned frames retain their reference role;
  any extra identity input must fit the verified model limits and the priced plan. Never drop the source
  frame to make room for a redundant sheet. The G7 wardrobe inventory follows the contract, not an accidental portrait import.
- **Historical price:** Seedream 5.0 Pro was 2.5 cr. Re-price the actual selected model/settings. Use
  count 1, at most three planned attempts, no character picker or approval gate.

## G2. Fictional UGC-real hero: Soul 2.0 selfie (Yaong)

- **When to use**
  - The user wants an invented hero ("a girl generated in Soul 2.0").
  - The reference is phone or UGC footage.
  - Soul gives a realistic selfie look.
  - It also made the identity still of the 2026-10-08 Katana remake (a full-length fashion portrait on a
    white studio backdrop, the only identity ref of its Seedance plate): VERIFIED live, 0.12 cr, 2k 3:4
    output = **1536×2048** PNG. The "seamless white" backdrop came back slightly grey: harmless for a
    Seedance ref, but lift levels in code before thresholding or keying the still itself.
- **Params**. These are the param names as recorded. Verify the names with `models_get`.
  ```json
  {
    "model": "<from plan line: soul_2>",
    "aspect_ratio": "<from plan line: 4:3>",
    "quality": "<from plan line: 2k>",
    "count": 1,
    "style_id": "3db34ab5-3439-4317-9e03-08dc30852e69",
    "enhance_prompt": false,
    "prompt": "<below>"
  }
  ```
  - The style id is "General".
  - Soul takes at most 1 image ref.
  - Use `soul_id` only for a trained Soul.
- **Price**: 0.12 cr per image. the verified non-generating estimate ignores `count`, so multiply it yourself (mcp-api §4).
- **Count**: 1. Use this branch for an explicitly requested fictional hero or an unlocked supporting
  character required by a REMIX story; never replace the user's intended hero. Select internally; no
  character picker. At most three attempts within the plan.
- **Prompt (VERBATIM, Yaong heroine, chosen #4).** **EXAMPLE ONLY: copy the structure, never these identity
  items** (header rule): hair, makeup, top, bangles, nails,
  gesture and backstage props are Yaong's; take them from your reference and brief.
  ```
  Phone front-camera selfie photo at arm's length of a fictional 21-year-old Korean K-pop idol girl in a bright white backstage waiting room. Long straight glossy jet-black hair past the shoulders with soft wispy face-framing side bangs, a small silver rhinestone hair clip above one temple. Pale luminous glass skin, rosy pink blush across the cheeks and nose bridge, sparkly aegyo-sal under the eyes, soft brown eyeliner with a small wing, glossy pink gradient lips. She wears a black halter top with thin white horizontal stripes, layered chunky silver chain necklaces, a chunky glossy brown tortoiseshell bangle on one wrist and a translucent pink bangle on the other, silver rings, long almond nails with white chrome nail art. She makes cute cat-paw hands under her chin, head tilted, sweet closed-mouth smile, looking straight into the lens. Background: plain white walls, a pale lime-green shelf near the ceiling, two mop handles leaning in the corner. Soft overexposed daylight, lifted creamy whites, pinkish skin glow, slight phone-camera softness, candid vlog snapshot.
  ```
- **Historical structure**, adapt to the selected output role and ownership; do not invent age or ethnicity unnecessarily:
  1. Capture device and framing.
  2. The permitted fictional character and story role; age/ethnicity only if necessary to the actual brief.
  3. The planned location (source location in EXACT).
  4. Hair.
  5. Skin and makeup.
  6. Contracted outfit/accessories (source-derived in EXACT).
  7. The planned gesture or still pose.
  8. Planned background props and explicit prop locks.
  9. Selected light/texture grammar and planned scene lighting.
- Describe the actual permitted subject plainly. Do not relabel a subject or remove reference evidence to evade a rejection; see §2.
- Do not use `soul_cast` for creatures, quadrupeds or stylised media. It forces photoreal humanoids and
  drifts the background to grey (memory note). Use `nano_banana_2` or `gpt_image_2_5` instead.

## G3. Look or outfit change that keeps the face: Seedream i2i (Yaong look B)

- **When to use**: the planned output requires another look/outfit, or a prepared identity image
  conflicts with its wardrobe contract. EXACT follows the source or explicit change; REMIX follows its
  authored wardrobe and locks.
- **Params**
  ```json
  {
    "model": "<from plan line: seedream_v5_pro>",
    "aspect_ratio": "<from plan line: 4:3>",
    "resolution": "<from plan line: 2k>",
    "count": 1,
    "medias": [{ "role": "image", "value": "<chosen identity still job_id>" }],
    "prompt": "<below>"
  }
  ```
- **Price**: 2.5 cr.
- **Count**: 1.
  - Yaong ran a 4-image shootout with 2 × `gpt_image_2` 2k high (6.5 each) and 2 × Seedream.
  - Seedream #3 was used. Seedream #4 was also fine.
  - Both `gpt_image_2` outputs gave a beige coat instead of caramel-brown.
- **Prompt (VERBATIM, Yaong look B, used as @image1 of plate B1).** **EXAMPLE ONLY: copy the structure,
  never these identity items** (header rule): the coat, tank
  top and jewellery are Yaong's look B.
  ```
  Keep the exact same girl from the reference photo: identical face, eyes, makeup, rosy blush, long straight jet-black hair with side bangs and the silver hair clip. Change only her outfit and pose: she now wears a big fluffy caramel-brown faux-fur coat worn open and slipping off her shoulders over a white ribbed tank top, a thin silver chain necklace, long silver threader drop earrings, silver rings, white chrome almond nails. Pose: both hands raised near her cheeks making small finger hearts, playful open-mouth smile, looking straight into the lens. Same bright white backstage waiting room with plain white walls and two mop handles leaning in the corner, soft overexposed daylight, lifted creamy whites, phone front-camera selfie at arm's length, slight phone-camera softness. No text, no logos.
  ```
- **Structure**, in this order:
  1. "Keep the exact same <person>" + the identity features to preserve.
  2. "Change only <outfit/pose>: …", with every new item's colour and material.
  3. The same location, light and camera.
  4. Exclusions.
- "slipping off her shoulders" passed here, on an image. It was removed from the Seedance prompt
  (see §3).

## G4. Local reference-frame identity edit: exactly two image references

This recipe preserves the source shot for EXACT or a selected local replacement in REMIX. For a new
REMIX scene, use the optional asset/prompt structure above: a source frame may own selected style only,
while composition, pose and setting follow the creative plan. Do not apply G4's exact composition lock
to every new scene or force a two-image limit onto another supported, explicitly mapped asset need.

Use this route for a faithful anime, stylized or photographic identity replacement, a finished still/code-composited cut, a Seedance 2.5 start frame, or a motion-transfer input. It is not limited to video keyframe preparation. The baseline is exactly two current user-authorized images: the original cut frame first, the uploaded character/person image second. Never add a third identity or reconstruct the original composition from text alone.

The first image owns composition, existing art style, textures, pose, camera angle, lighting, setting, garments, props, other people and typography. The second image owns only the requested identity intended to replace the selected source subject. This applies to all of that subject's cuts, including back views, silhouettes, helmets, body/hand crops, occlusions and distant shots; facial visibility is never a prerequisite. Do not average the new face with the original person's face, preserve the original person's identity by accident, or import the uploaded photo's background, outfit or lighting unless explicitly requested. Preserve all untargeted details. Preserve source body proportions, wardrobe and props unless explicitly included in the requested change. Keep a hidden face hidden: do not turn a back view toward camera, remove a helmet or brighten a silhouette merely to display the replacement's face. Track the same subject through neighboring shots and record the relationship; unrelated B-roll and other people are not replacement targets.

Default to `gpt_image_2_5` for image editing, or use an already selected verified multi-reference image model such as `nano_banana_2` or `seedream_v5_pro` when its live contract fits. Resolve the actual supported image parameters and price; image models remain distinct from the Seedance 2.5 video restriction.

```json
{
  "model": "<from plan: gpt_image_2_5 or verified selected multi-reference image model>",
  "aspect_ratio": "<measured source-frame ratio supported by the model>",
  "count": 1,
  "medias": [
    { "role": "image", "value": "<original cut frame media_id>" },
    { "role": "image", "value": "<uploaded user character/person image media_id>" }
  ],
  "prompt": "The first reference owns the exact composition, visual style, texture, pose, camera angle, framing, light, wardrobe and environment. Replace only <the intended source subject> with the identity from the second reference, rendered in the first reference's existing style. Preserve the replacement identity; do not blend it with the original person's face. Do not copy the second reference's background or clothes. Preserve the source's body proportions, face visibility and occlusions unless the requested change explicitly includes them; a hidden face stays hidden. Keep every untargeted person, prop, text and graphic unchanged."
}
```

Extract each relevant cut frame at full source resolution after complete reference analysis, including the targeted subject's hidden-face continuity shots. Do not substitute a frontal close-up for a back view or crop just to simplify identity verification. Retain source text and graphics in the image unless an explicit clean-intermediate layer plan will restore those exact original pixels afterward. Describe first/second input roles in prose as well as any image tags supported by the actual model. One result per request; at most three bounded attempts within the finite plan, selected internally without questions.

Choose the least generative faithful continuation. A still plus measured whole-frame/layer camera motion may be sufficient; never animate facial landmarks, reshape the face or simulate expressions in code. If new motion is needed, use the accepted frame as a supported Seedance 2.5 start/reference image. If exact source choreography requires direct motion transfer, use G5/G10 with the existing driving video. A direct Genjutsu subject swap may use the uploaded identity image without creating this intermediate still when it already preserves the source better. Do not buy both routes as automatic alternatives.

Genjutsu catalog presets are an optional route, not the default for every anime reference. Read [Genjutsu routing](genjutsu-routing.md) before selecting one. A catalog `genjutsu:<id>` and a public Restyle API preset identifier belong to different contracts and are never interchangeable. Any real content refusal still forbids identity disguise, removal of evidence or model switching to evade the restriction; use a supported faithful fallback or declare the affected branch unresolved.

## G5. REPERFORM still: the hero inside the cut's frame, as the Motion Transfer image (Altman)

- **When to use**: a supported REPERFORM cut whose existing supplied or prepared image does not already preserve the required subject, source framing and appearance (`routing.md` §2.3). Reuse a suitable existing image; do not generate a new still for every cut automatically.
- **Why**: with the bare user photo, MT rebuilt the background from the photo. Altman's c03 came back
  as a TED-like stage with giant letters.
- **Evidence**
  - A still of the hero already inside the cut's set won on 3 of 5 cuts and tied on the other 2
    (Altman). Those stills were text-described (hero photo + a description of the set), because the
    user's 2-ref rule did not exist yet.
  - Aura G used a frame of the hero already in the hangar.
  - Aura H used 2 real photos with plain backgrounds.
- **When a new image is needed: the 2-ref still (G4's shape).**
  - `@image1` = the reference cut frame (`frames.py keyframes`), with original graphics preserved unless a separate exact restoration layer is planned;
    `@image2` = the hero photo. Exactly two refs. This is the user's rule (memory
    `ref-frames-as-composition-refs`, brief rule 5).
  - As an MT input the 2-ref form is UNTESTED. A moderation or IP rejection does not authorize transferring the same blocked request to this model.
  - Reuse one suitable image across cuts only while it preserves their measured composition and appearance. For a take or part needing a new image, use its relevant source frame. Do not purchase comparison images or extra MT jobs merely to compare routes.
- **Params**: G4's block with the measured source-frame aspect and geometry. Never force historical 4:3 or 3:4 examples onto another source. If the verified model requires a supported input shape, use a documented reversible pad/coordinate mapping that preserves the intended composition; inspect actual output dimensions before mapping it back.
- **Prompt**: G4's template. When the user wants a different world from the reference (Aura-style),
  keep both refs and name the world changes after the swap sentence: place, materials, light, plain
  wardrobe changes only when requested. The source video and identity images anchor the actual subject; do not replace a celebrity with a generic identity or conceal who is depicted.
- **Price**: live-price the selected multi-reference image model; the historical 2 cr example is not a fixed price. At most three attempts per cut within the plan; then source reuse or a declarative limitation.
- **Fallback.** Prefer the original reference pixels. A text-only scene approximation is not a 1:1 replacement and must not be used to evade moderation or an IP restriction. If source reuse cannot fulfill an explicitly requested change, record the blocked cut and report it without a question.

## G6. Die-cut stickers: Seedream remove_bg (Katana)

- **When to use**: an output role needs graphic stickers whose required pixels cannot be reused.
  EXACT preserves the reference inventory; REMIX authors an appropriate set from the selected graphic
  grammar. Prefer suitable existing assets and generate only missing planned items.
- **Params**: one sticker per `generate_image` request, `count:1`, through its own reservation and immediate ledger registration. The platform batch limit does not enable multi-item submissions in this workflow.
  ```json
  {
    "model": "<from plan line: seedream_v5_pro>",
    "aspect_ratio": "<from plan line: 1:1>",
    "resolution": "<from plan line: 1k>",
    "remove_bg": true,
    "prompt": "<below with {ITEM}>"
  }
  ```
- **Output**: 1024×1024 RGBA PNG. Visible art covers 50–85% of the canvas. Crop to the alpha bbox
  (+6 px) before sizing, or the stickers look too small.
- **Price**: 1.25 cr each at 1k. The `remove_bg` surcharge was never probed. Run the verified non-generating estimate first.
- **Count**: match the planned output inventory/timing; EXACT matches the analyzed source exactly.
  Reuse suitable assets before buying missing ones. Katana's historical 30-sticker set is not a default.
- **Prompt (VERBATIM, Katana).** **EXAMPLE ONLY: copy the structure, never these identity items** (header
  rule): the black/white/acid-lime palette is Katana's grade;
  use your reference's palette and item list.
  ```
  A single die-cut vinyl sticker of {ITEM}. Bold flat graphic illustration, thick clean white die-cut border around the whole shape, colors only black, white and acid lime green, slight screen-print grain. Centered on a plain light grey background. No text, no letters, no logo, no watermark.
  ```
- **Historical recipe details, not defaults:** Katana used three colours, a white die-cut border and a grey removable background. Follow the current source's palette, edge treatment and lettering instead; do not copy the example's text exclusions when the source sticker has letters or logos.
- **Building the item list**
  - EXACT uses the exact reference inventory except explicit changes. REMIX derives its planned items
    from the story and selected shape/texture/palette/border/lettering grammar; preserve explicit locks.
  - Katana's 30 items (gothic cross with a lime gem, skull in lime flames, fanged heart, sheathed katana,
    barbed-wire heart, padlock heart, chain links, lightning bolt, sparkle star, black rose, spider, bat,
    skull-wing butterfly, cherry bomb, crying eye, fanged lips, crown, angel wings, snake, chrome Y2K star,
    X-eyed smiley, safety pin, broken heart, skull 8-ball, spiked choker, flame burst, tribal swirl, ink
    splatter, cute ghost, devil horns) are an example only.
  - The historical "cute ghost" was pulled for a past project's taste decision. Do not remove or replace any current source item on that basis.
- **Sticker-sheet alternative (UNTESTED)**
  - One 2k image of about 12 stickers, evenly spaced on plain light grey and not touching, with
    `remove_bg`.
  - Slice it in code by alpha connected components.
  - Historical price comparison: one 2k image (2.5) instead of 12 × 1.25 (15). Use only when faithful and within the verified finite plan; the first required sheet can be its canary. Do not buy duplicate comparison jobs.

## G7. Seedance 2.5 `omni_reference` multi-shot plate (Katana, Yaong)

- **When to use**: required new output footage that existing usable footage cannot supply, grouped
  only where the authored roles and locks remain intact (`routing.md` §3.1). EXACT matches measured
  source shots; REMIX authors scenes using selected reference grammar. A clean set is appropriate
  when planned for the actual scene or a documented compositing intermediate, never by generic default.
- **Params**
  ```json
  {
    "model": "<from plan line: seedance_2_5>",
    "mode": "<from plan line: omni_reference>",
    "duration": "<from plan line: sum of the shot slots>",
    "resolution": "<from plan line>",
    "aspect_ratio": "<from plan line>",
    "bitrate_mode": "high",
    "generate_audio": false,
    "medias": [
      { "role": "image", "value": "<source frame or accepted source-aligned keyframe id>" },
      { "role": "image", "value": "<identity-only reference id, omit this entry if unnecessary>" }
    ],
    "prompt": "<below>"
  }
  ```
  - `@image1` / `@image2` follow the order of `medias`.
  - Use explicitly assigned image ownership: exact/local source frame for structure, REMIX style frame
    only for selected visual grammar, intended identity or necessary reusable location/prop references.
    Use a supported `start_image` where the first frame must be pinned. Omit unnecessary references
    rather than generating an extra sheet; the JSON is a minimal two-reference example, not a mandatory asset chain.
  - Set `generate_audio: false` every time. The model default is TRUE.
  - Never use audio refs. Audio refs with `generate_audio:true` gave nsfw 4/4 in Yaong. Seedance also
    re-speaks an audio ref instead of passing it through.
  - Set mode, resolution, duration and aspect explicitly, from the plan line. The model default is t2v
    at 720p, 5 s, 16:9 with audio on. `t2v` rejects all reference media.
  - Duration is an integer from 4 to 30.
  - The plan line itself states `"generate_audio": false` and `"bitrate_mode": "high"` (header), so
    `ledger.py params` and `--check` carry them; `ledger.py quote` warns on a Seedance line without them.
  - Output is 24 fps. 1080p 4:3 = 1664×1248 HEVC Main10. **720p 4:3 = 1112×834 H.264, 24 fps**: a
    10 s plate came back as 241 frames (VERIFIED live 2026-10-08). Size the k720 arithmetic
    (`budget.md` §5) on 1112 / 834, not on 960 / 720.
- **Duration** (the plan line's, from `budget.md` §4.3; one formula, no extra multiplier):
  - Multi-shot plate: duration = Σ slot_s, where slot_s = clamp(2 × the screen seconds the EDL needs
    from that shot, 2, 4).
  - Continuous-routine plate (the Yaong A1 kind): duration = ceil(1.6–2 × the prompted routine
    length), with the must-have beats in the first half.
  - Round up to the required integer duration, respecting the verified model minimum. Use that full
    duration within the live supported maximum (historically 30 s), or split into sufficient jobs before
    pricing. Never clamp a longer sum to 15 s, truncate the routine or drop a planned slot. The prompt's
    `Shot n (a-bs)` timecodes are these slots.
- **Price**: 12 / 7 / 3 cr per second at 1080p / 720p / 480p.
  - The rate is the same for t2v, omni_reference and extension.
  - Audio on or off, bitrate high, aspect ratio and ref count do not change the price. So bitrate high
    is free.
  - Examples at 1080p: 4 s = 48, 10 s = 120, 12 s = 144, 15 s = 180.
  - The memory note's 63/135 cr figure is stale; the price is now 33% higher.
  - VERIFIED live 2026-10-08: one 10 s 720p 4:3 plate (five 2 s shots) was charged exactly 70. That
    single plate, plus a 0.12 cr Soul identity still and a 1 cr matte, carried a whole Katana-style
    remake at 7.9 cr per final second (the original Katana project spent ~120 per final second).
- **Composition and evidence.** Record each output shot and its input ownership in `plan/routes.json`.
  EXACT/local edits retain the relevant source frame and measured geometry. New REMIX scenes use
  authored geometry with selected style/location/identity evidence; an existing matching keyframe or
  a necessary prepared scene image may anchor them. Do not replace a required available structural
  reference with text alone merely because a clean studio plate is convenient.
  - Use the accepted frame as a supported Seedance reference or `start_image`. A start image anchors only its own initial frame; validate each later shot. Split into the necessary source-aligned jobs if one multi-shot plate cannot retain all required compositions, rather than discarding source detail.
  - An exact clean layer preserves source lighting, colours, texture and perspective and restores
    removed original layers. A new REMIX scene follows its planned set/light and selected grammar.
    Never recolour an identity-locked prop merely for easier keying.
  - A per-cut G8 clip is justified whenever it is the faithful authorized route, including a short but important shot. Model minimum duration is a billing constraint, not permission to change final cut timing.
- **Preserve the planned full cast.** EXACT/local edits retain every untargeted source person. REMIX
  scenes retain their authored cast and explicit identity locks. A separately isolated plate may contain
  one person only if all other required people remain in verified layers. Never accidentally drop a
  planned person to simplify face tracking or background removal.
- **Count**: 1 take.
  - **Canary**: the planned plate covering the family's hardest fidelity constraints, alone, at final settings (header and
    `budget.md` §7).
  - **Second take**: no discretionary alternative. A corrective retry needs an observable failure of
    the selected shot contract, within the plan reserve and retry limit.
  - **Re-roll** (`budget.md` §3 rung 5). Log every re-roll with its reason; "a better take" is not a
    failure.
    - Shot failure: a planned shot fails a check from the fail list: identity, wardrobe, garbled text
      or logo, anatomy, a matte-hostile background, or a missing beat the EDL needs that no other plate
      second supplies. Re-roll that shot alone as a single-shot job of max(4, ceil(2 × its slot)) s at
      the same resolution.
    - Job failure: the canary fails, or half or more of a job's planned shots fail for one cause. Fix
      the cause and re-run the whole job once (that is the job's re-roll).
    - Re-roll spend per job stays ≤ that job's own cost, within the pre-priced reserve, and only while
      `ledger.py guard $W --line <ID> --reroll-of <job> --reason <fail-list item>` passes. For a
      single-shot re-roll add `--slot <the shot's slot seconds>`; `ledger.py params $W --line <ID> --slot
      <s>` prints that job's skeleton.
- **Prompt shape**: use the optional ownership/causal/spatial structure above, then the required shot
  slots. Leave technical specs in params; keep separately composed effects in the layer plan.
  1. **Header**: what each `@image` is, plus an exhaustive inventory of identity items to keep "in
     every shot". Use HEADER-FULL for body shots and HEADER-CU for close-ups.
  2. **Prop line** (when needed): preserve the source material, colour and shape; solve keying in compositing without changing the prop.
  3. **Style and scene line**: planned set, light, camera behaviour and selected reference grammar.
  4. **`Shot n (a-bs): …`**: only the necessary shots, each with its role, framing and action. The timecodes are the slots
     above.
  5. **Closing line**: preserve explicit locks and planned details. EXACT restores source graphics;
     REMIX composes its authored wording/graphics. Never exclude required final content without its
     documented later layer.
- **Prompt (VERBATIM, Katana)**. Below are the two headers, then the four used scenes.
  - **EXAMPLE ONLY: copy the structure, never these identity items** (header rule). The headers'
    inventory (lime wig, camouflage bomber, chains and crosses, denim micro shorts, cross-print
    thigh-highs, gloves, platform boots, smoky eyes, green lipstick) and the scenes' katana, hair flicks
    and fur hood are Katana's hero. A dry-run eval pasted them into another user's plates. Keep the
    shot-list structure only; derive subject, scene, camera, light, expression, wardrobe, text and motion from the current mode contract: measured source in EXACT, authored creative plan and selected grammar in REMIX. These historical studio scenes are not default prompts.
  - **Do not copy their durations.** These prompts ran as 15 s plates (`Shot 5 (12-15s)`) in a project
    that generated 11× what it used: 270 s for about 24 s on screen, 180 cr per plate at 1080p. Copy the
    timing grammar only, author source-specific shot text, then re-time it to the measured slots and set the plan line's
    duration to their sum. Never set duration 15 because the timecodes end at 15. A worked re-timing
    follows the scenes.
  - HEADER-FULL:
    ```
    @image1 is the woman and her complete outfit, @image2 shows the same woman full-length and her face up close. Keep her exact face, makeup, knee-length lime-green wig with blunt bangs, camouflage bomber with fur hood, chains and crosses, studded belt, denim micro shorts, white thigh-highs with black cross print, black gloves and black platform boots in every shot.
    ```
  - HEADER-CU:
    ```
    @image1 is the woman and her complete outfit, @image2 shows the same woman full-length and her face up close. Keep her exact face, dark smoky eye makeup, dark green lipstick, lime-green wig with blunt bangs, cross choker, chains and camouflage bomber with fur hood in every shot.
    ```
  - Scene b, dance. HEADER-FULL, then:
    ```
    Fashion film on a seamless pure white studio cyclorama, bright high-key on-camera flash look, crisp detail, handheld camera with a light natural drift. She dances loosely and confidently with a cool, understated attitude.

    Shot 1 (0-3s): full-length wide, head to platform boots, she sways her hips side to side and flicks the long lime-green hair over one shoulder.
    Shot 2 (3-6s): medium shot from the waist up, both gloved arms rise above her head, hands slide into her hair, eyes half closed.
    Shot 3 (6-9s): low angle from floor level, the black platform boots stomp twice on the white floor, the long hair swings behind her legs.
    Shot 4 (9-12s): full-length, she turns her back to the camera, the hair hangs down to her knees, then she looks back over her shoulder into the lens.
    Shot 5 (12-15s): waist-level crop of the studded belt and shorts as she sways, one gloved hand resting on her hip.

    No text, no logos, no watermark.
    ```
  - Scene c, close-ups with the hiss. HEADER-CU, then:
    ```
    Fashion film close-ups on a seamless pure white studio background, bright high-key on-camera flash look, crisp skin and hair detail, handheld camera with a light natural drift. Cool, confident, understated attitude.

    Shot 1 (0-3s): close-up of her face, she looks straight into the lens, slowly tilts her head, a strand of lime-green hair falls across one eye.
    Shot 2 (3-6s): medium close-up, both black-gloved hands push the bangs up and back into her hair, eyes closed, then she opens her eyes to the camera.
    Shot 3 (6-9s): extreme close-up of her eyes and bangs only, smoky makeup, her eyes glance to the side, then back into the lens.
    Shot 4 (9-12s): close-up, she lifts both gloved hands beside her face with fingers curled like claws and bares her teeth in a short playful hiss, then relaxes.
    Shot 5 (12-15s): medium shot, she gives a small smirk, tilts her head and pulls the fur hood edge closer to her cheek.

    No text, no logos, no watermark.
    ```
  - Scene f1, the **aura recipe**: slow motion + side wind + "calm, unbothered … no smiling".
    HEADER-FULL, then:
    ```
    Slow-motion fashion film on a seamless pure white studio cyclorama, bright high-key flash look, crisp detail. A strong studio wind fan blows from the side the whole time. She is calm, unbothered and completely confident, a cool understated stare, no smiling.

    Shot 1 (0-4s): full-length, she stands perfectly still with her hands in her jacket pockets while the wind blows her very long lime-green hair sideways like a flag; she slowly lifts her chin and looks straight into the lens.
    Shot 2 (4-8s): low angle from floor level, hero shot looking up at her, she looks down into the lens, fur hood and hair fluttering in the wind.
    Shot 3 (8-11s): medium shot, she slowly turns her head from profile to face the camera, hair whipping across her face in slow motion.
    Shot 4 (11-15s): full-length slow-motion walk straight toward the camera, hands in pockets, wind streaming her hair behind her.

    No text, no logos, no watermark.
    ```
    - This scene gave the opening shot and many of the best beats.
    - Katana's aura plates (f1–f5) use 4 shots of 3–4 s, not 5 × 3 s.
  - Scene f3, Prop line. HEADER-FULL, then:
    ```
    Prop: a katana sheathed in a glossy black lacquered scabbard with an acid lime-green cord-wrapped handle. It stays sheathed except in shot 3.

    Slow-motion fashion film on a seamless pure white studio cyclorama, bright high-key flash look, crisp detail, a studio wind fan blowing her hair. She is calm and completely confident, a cool understated stare.

    Shot 1 (0-4s): full-length low angle, she stands with the sheathed katana resting on her right shoulder, the wind blows her long hair sideways, she stares into the lens.
    Shot 2 (4-8s): medium shot, she swings the sheathed katana down from her shoulder and plants the scabbard tip on the floor in front of her, both gloved hands resting on the handle, eyes on the camera.
    Shot 3 (8-11s): close-up of her gloved hand on the lime-green handle, her thumb pushes the guard and the blade slides two inches out of the scabbard with a bright glint of light, then clicks back in.
    Shot 4 (11-15s): close-up, she holds the sheathed katana horizontally at eye level, her eyes look over it straight into the lens, hair moving in the wind.

    No text, no logos, no watermark.
    ```
    - Lessons from this scene, under a hard threshold look:
      - Shot 1 came out as a backlit silhouette, a black blob.
      - Shot 3's glint became an unreadable white bar. A lime star was drawn in code instead.
    - Those were historical failures, not reasons to omit a source shot. Preserve the observed silhouette
      and glint; fix the local tonal treatment or exact compositing layer instead.
    - VERIFIED live 2026-10-08: on identity-legible medium close-ups the xerox threshold crushed the
      face to near-black, while the reference keeps facial detail there. If the compositor introduced
      this error, correct the whole-shot grade against the source (`compositing.md`), not a face mask
      or face-only retouch. A defect already present in the generated face requires a supported
      generation correction within the plan. Preserve the measured source light.
  - **Re-timing example** (the `budget.md` §4.3 arithmetic; this re-timed prompt has not been run).
    Suppose the EDL needs 1.0, 0.75, 1.5, 1.0 and 0.5 s from scene b's five shots.
    - Slots: clamp(2 × need, 2, 4) = 2, 2, 3, 2, 2 s. The plate is 11 s: 132 cr at 1080p or 77 at 720p,
      against 180 / 105 for the 15 s original.
    - Keep the shot texts and change only the timecodes: `Shot 1 (0-2s)`, `Shot 2 (2-4s)`,
      `Shot 3 (4-7s)`, `Shot 4 (7-9s)`, `Shot 5 (9-11s)`. The plan line says duration 11.
    - Scene f1's four shots with needs of 1.5, 1.0, 1.0 and 2.0 s re-time to 3 + 2 + 2 + 4 = 11 s.
- **Yaong selfie gesture-pool plate (VERBATIM, A1, 10 s, @image1 = Soul heroine)**. This is the skeleton
  for UGC and jump-cut refs. **EXAMPLE ONLY: copy the structure, never these identity items** (header
  rule): the role, outfit recap, room, chant words and hand routine are Yaong's; your beats come from
  your output shot list.
  ```
  Realistic phone front-camera selfie video at arm's length of the adult woman from @image1, a K-pop idol in her twenties: same face, long straight jet-black hair with side bangs, silver hair clip, black-and-white striped top, chunky silver chain necklace, brown tortoiseshell bangle, pink bangle, white almond nails. Bright white backstage waiting room: plain white walls, a pale lime-green shelf high on the wall, mop handles leaning in the corner. Soft overexposed daylight, lifted creamy whites. Handheld micro-wobble, chest-up framing, her hands always visible near her face. She does a cheerful counting hand routine for a fan video, mouthing 'yaong, hana, dul, set, yaong, saranghae' to an upbeat rhythm.
  0.0-0.4s: cat-paw hands under her chin, head tilt.
  0.45-0.85s: one finger raised beside her cheek.
  0.9-1.3s: two fingers.
  1.35-2.2s: three fingers, then both open hands raised beside her head, waving side to side.
  2.25-2.65s: cat-paw hands again with a small nose scrunch.
  2.7-3.6s: finger heart toward the lens, then a cheerful wave.
  3.6-4.5s: laughs, leans closer to the lens, tucks hair behind her ear.
  4.5-9.0s: repeats the same routine with a little more energy and ends with a wink and a finger heart.
  Natural, friendly, understated expressions. One continuous take, no cuts, no on-screen text.
  ```
  - Skeleton, in this order:
    1. Capture device.
    2. Actual source subject and explicitly requested identity change, with source-derived wardrobe.
    3. Location.
    4. Light.
    5. Measured source camera, framing and subject placement.
    6. Action routine.
    7. Timestamped beat list.
    8. Observed expression and cut structure; text exclusion only for an exact-restoration intermediate.
  - **Timing reality: timecodes are ordering hints, not a schedule.** The gestures arrived 1.5–1.6×
    slower on A1 and about 2× slower on B1. In the 2026-10-08 Katana run the five 2 s shot slots of a
    10 s plate landed almost exactly on their timecodes (VERIFIED live). Both happen, so never plan an
    in-point from a timecode: put the beats you cannot lose early and choose in-points from the sheet.
  - Do not ask for "repeats the same routine". That half was never used, and it lacked the second
    cat-paw the edit needed.
  - List each needed beat once and put the beats you cannot lose early.
  - A1 ran 10 s. Under the continuous-routine rule its 4.5 s routine sizes to ceil(1.6–2 × 4.5) = 8–9 s,
    with no "repeat" half: nothing after 4.89 s of A1 was used.
  - With a second person (Yaong B1 and F1), add one sentence for the friend from `@image2` with their
    position in frame. It passed in both plates.
  - A hard face-lock can crop other people. Preserve every planned performer; EXACT/local edits also retain untargeted source people. Use an appropriate uncropped plate or separate verified layers rather than dropping a person to simplify matting.
- **Do not**
  - Do not write `SAME FRAME` (Katana handoff).
  - EXACT matches observed expression; REMIX matches planned acting and identity. Do not inherit a
    stare or smile merely because a historical example preferred one.
  - Preserve backlit silhouettes, specular glints, props pointed into the lens or low-angle faces when present in the reference. Otherwise avoid adding them
    under a threshold look.
  - EXACT describes observed camera movement and preserves repeated angles. REMIX describes the
    authored move, dose and limit, or a locked camera, consistent with selected grammar and continuity.
    Whole-frame zooms and separate particles may use code within the face boundary.
- **Choosing in-points**: from the real plate's timestamped contact sheet (`frames.py catalog`, 4 fps by
  default), never from the prompt's timecodes, even when a plate happens to follow them (2026-10-08). Catalogue only after every submitted paid job in the planned group is
  terminal (header, "Serialized submissions and job polling").

## G8. Per-cut clip from a keyframe: Seedance start image + face ref (/test-edit). WORKED

- **When to use**: an output role needs new motion and a dedicated Seedance clip fulfills its shot
  specification better than a shared plate, existing footage or whole-layer animation. EXACT uses
  measured source geometry/motion; REMIX may use a newly authored scene/keyframe. This includes brief
  or sub-second shots. G10 is reserved for specific desired source choreography, not every performer.
  - Satisfy the live model's minimum job duration while retaining the authored output interval;
    EXACT keeps the source cut's measured length. Do not change required timing for billing efficiency.
  - Reuse a shared plate only when it preserves every required output composition and beat equally
    well. Price and latency break fidelity ties; they do not authorize dropping explicit locks or
    required source detail in EXACT.
- **Start frame**: reuse a suitable image, prepare G4 for a local source identity edit, or prepare the
  authored REMIX scene under the asset-ownership rules. G4 is not mandatory for every new scene.
- **Params** (role names unverified, so check `models_get`; start and end images only work in
  `omni_reference`):
  ```json
  {
    "model": "<from plan line: seedance_2_5>",
    "mode": "<from plan line: omni_reference>",
    "duration": "<from plan line: >= 4>",
    "resolution": "<from plan line>",
    "aspect_ratio": "<from plan line>",
    "bitrate_mode": "high",
    "generate_audio": false,
    "medias": [
      {
        "role": "start_image",
        "value": "<suitable existing source-aligned image id, or G4 keyframe only if needed>"
      },
      { "role": "image", "value": "<identity-only face photo id; omit this entry if unnecessary>" }
    ],
    "prompt": "<below>"
  }
  ```
- **Price**: 28 cr per 4 s at 720p (48 at 1080p). /test-edit ran 6 × 5 s at 720p (35 each); all 6
  passed and were used.
- **Prompt (VERBATIM shape, /test-edit `clips.sh`, CLI tag format).** **EXAMPLE ONLY: copy the structure,
  never these identity items** (header rule): the gargoyle
  ledge, blazer and stubble are that user's.
  ```
  Slow dramatic push-in from a low angle while he crouches on the gargoyle ledge; wind moves his hair and blazer, he slowly tilts his head down and locks eyes with the camera, a slight confident smirk. The man keeps exactly the face from <<<image_1>>> in every frame: same eyes, nose, jaw, stubble and short light-brown hair. He wears his dark navy blazer and open-collar white shirt throughout. Cinematic action-film look, anamorphic, photoreal, no text. <<<image_1>>>
  ```
  - Describe the selected shot's camera/action, identity, wardrobe and look. EXACT measures these
    from source; REMIX uses the authored plan. The historical “no text” ending needs a later planned
    graphic layer when final text is required; it is never a blanket final-content exclusion.
  - In MCP calls, use `@image1`-style references, as Katana did.
- **Caveats**
  - For exact/local reconstruction, the keyframes in that run were inadequate text re-descriptions:
    use actual source frames/G4. New REMIX scenes can use the authored prompt structure and relevant
    reference ownership; they need not pretend to duplicate a source composition.
  - The film itself (v1) was rejected for compositing reasons; the clips were fine.
  - A Spider-suit costume round ended nsfw on 5 of 6 clips.

## G9. Genjutsu replace: `hf_mult_replace_object` (Altman)

- **When to use**
  - A SWAP route: a person→person swap that keeps the reference's plate, grade, motion blur, PIP cards
    and baked text.
  - It kept text on 11 of 12 cuts.
- **Never use it for**
  - a class change: car→person failed, and so did lamp post→person;
  - an unpadded input under about 4 s (rejected, or HTTP 422): pad it (below);
  - a whole reel in one job. SWAP is per cut, on 96-frame pads. A whole-reel replace is an UNTESTED
    historical experiment, excluded from the normal plan (mcp-api §15.1).
- **Rejected content.** `ip_detected` or `nsfw` does not authorize a model-switch workaround. Confirm any refund, retain the debit until verified, and use a faithful supported source-reuse route if allowed. Otherwise record the unresolved cut and continue independent work. No re-ask, extra credit ceiling or approval gate.
- **The driving clip: two commands, then a check** (the same recipe feeds G10):
  ```bash
  python3 $RR/frames.py export $W --cut c07 --fps 24 --crop window        # -> $W/cuts/c07.mp4, muted, 24 fps
  python3 $RR/frames.py pad $W/cuts/c07.mp4 $W/gen/c07_pad.mp4 --mode pingpong   # < 4 s -> exactly 96 f
  ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames \
    -show_entries format=duration -of compact=p=0 $W/gen/c07_pad.mp4      # 96 frames, 4.000 s
  ```
  - **Export at 24 fps first** (re-timed by time). Never pad a native-fps export of a 25/30/50/60 fps
    reference. `pad` writes its input frames as-is at 24 fps, so the motion slows and the billed seconds
    grow 1.25–2.5×: a 3.9 s cut of a 60 fps reference became 10 s, 110 cr instead of 44 at 1080p. `pad`
    exits 2 on an fps mismatch unless you pass `--retime`.
  - **Captions and graphics.** Preserve original lettering and framing by default. Remove them from an intermediate only when a saved original-pixel layer and exact timing/geometry restoration are already planned. Never crop the final picture to hide or remove source text. Validate stylized text, subtitles, cards and watermarks after the swap.
  - **Pad.** A cut shorter than 4 s of real time is ping-pong padded to exactly 96 frames @24 = 4.00 s.
    Never pad to 100 frames: 4.17 s bills 5 s, 55 instead of 44 at 1080p. Never hold-pad: repeating
    frames broke the pose and lost the gloves (Altman).
  - **Check.** The probed frame count ÷ 24 must be the integer you intend to pay for (96 → 4.000 s, ±0.01
    s on `format=duration`). Price the plan line from the PROBED frame count, not from a nominal 96:
    verify the current estimate for those prepared frames, register it with `price-set`, then reserve with `ledger.py guard $W --line <ID> --frames <probed count>` before submission. The guard does not fetch a live price.
  - VERIFIED live 2026-10-08 (Altman c12): `frames.py export` of a 35-frame cut of a 60p reference gave
    14 frames @24; `pad --mode pingpong` made exactly 96 frames (4.000 s); the verified non-generating estimate on that pad and the
    swap prompt returned the IN THE DARK preset notice (free), the resubmit with `declined_preset_id`
    priced and ran. Run `assemble.py $W --control --dry` on the real pads before the quote: it proves the
    cuts map back.
- **Params**
  ```json
  {
    "model": "<from plan line: hf_mult_replace_object>",
    "resolution": "<from plan line>",
    "medias": [
      { "role": "image", "value": "<suitable supplied or prepared replacement-identity media_id>" },
      { "role": "video", "value": "<96-frame pad media_id>" }
    ],
    "prompt": "<below>"
  }
  ```
  - Roles are the current schema keys: at least 1 `image`, exactly 1 `video` (mcp-api §6.2).
  - Genjutsu defaults to 720p, so always pass the plan line's `resolution`.
  - Add a tight face crop as a second `image` when the face is under about 20% of the
    photo's height (genjutsu-ref-edit skill). A second image adds no charge.
  - Prefer a suitable supplied replacement-identity photo. A necessary source-aligned prepared image
    may be used when it better preserves the requested identity and source wardrobe under the current
    reference contract. Do not generate an extra G4 image automatically or import its scene as a new world.
- **Price**
  - Replace bills ceil(seconds) of the driving clip, so always trim or pad to an exact integer.
  - 44 cr per 4.00 s at 1080p (Altman's get_cost on an exactly 4 s probe clip); 28 at 720p, 12 at 480p.
  - **VERIFIED live 2026-10-08: a real 720p replace job on an exact 96-frame (4.00 s) pad was charged
    exactly 28.** Exact 4.00 s pads bill 4 s; the 1080p 44 is still a get_cost figure.
  - A 4.04 s input bills 5 s: 35 at 720p (today's get_cost) or 55 at 1080p. This account's replace jobs
    on Altman's 100-frame (4.17 s) pads were charged 55 each (mcp-api §13).
  - Account history shows 7 of 18 Object Swap jobs refunded as failed.
  - The quote shows Genjutsu lines as "fixed input (min-billed)", with no utilisation target. Never group
    several cuts into one input to improve the ratio: UNTESTED, and Genjutsu merged and re-ordered shots
    on strobe edits (Aura H).
- **Count**: 1 per cut.
  - The planned representative quality canary is still required before the remaining family jobs. No additional padding experiment is needed once the current input preparation is verified; a prior padding test does not replace the canary.
  - A cut that fails a fail-list check (identity, wardrobe, garbled baked text that code cannot re-lay)
    is re-run once as the same 4.00 s job; that is its re-roll (`budget.md` §3 rung 5).
- **Prompt**: one short operation/preservation sentence; at most 40 words across one or two sentences. Use a brief position cue only if needed to identify the target.
  ```
  Replace <brief target-position cue> with @Image1. Keep the source wardrobe, motion and all other details unchanged.
  ```
- **Historical drafts** used long scene descriptions; they are not operative templates. The input image/video carries those details.
- **Wardrobe warning**
  - Every Altman replace output wore the reference _photo's_ grey crewneck. That included the shirtless
    boxers and the F1 driver, even though the drafts said "same … trunks" or "keep clothes".
  - The server's prompt enhancer defaults to the complete look from `@Image1`. On this account it kept a
    source garment when the user prompt named it ("Keep the grey tracksuit"; mcp-api §6.2, job records).
  - Keep the short clause "preserve source wardrobe" when applicable. Validate the output against the
    source; prepare a better identity image with a supported image model or correct non-facial
    compositing within the plan. Never repair identity or facial appearance with local code, pixel
    painting or a pasted face. Do not request another photo or expand the prompt into a garment inventory.
  - Holding the reference's wardrobe across a film is still UNTESTED: the SWAP canary checks it.
  - VERIFIED again live 2026-10-08: the c12 replace dressed the hero in the photo's wardrobe.
- **After generation**
  - **The output is not the input's size or length.** VERIFIED live 2026-10-08: a 994×830, 96-frame
    pad came back at 720p as **1054×880, 24 fps, 89 frames (3.71 s)**. Never assume 96 out for 96 in,
    or a 720-px-tall output.
  - Map frames back with `gen_index = round(padded_index × gen_frames / padded_frames)` and keep the
    first N (`assemble.py` does this; the c12 rebuild passed `assemble --control` on all 21 cuts, with
    the baked words and the watermark preserved and the audio MD5-equal).
  - Run the text check (`textlayers.py`) and re-lay only the words that fail. c01 rendered a word at
    about 60% opacity and painted a blackletter glyph onto the hair.
  - Fades can come back 24p-stepped, 1–2 frames off at 60 fps. Re-time them with a source-fps text pass to match the original frame boundaries.

## G10. Genjutsu motion transfer: `hf_mult_motion_control` (Aura, Altman)

- **When to use**: REPERFORM routes.
  - Select only when the output shot specifically needs the source's body/camera choreography.
    A new world, anime styling or a person in frame alone does not justify MT; default REMIX scene
    coverage comes from usable footage, necessary image preparation and Seedance 2.5.
  - Historical: the hero re-performs the reference's body and camera choreography in a new world, the main source
    of all three accepted Aura films.
  - Historical evidence only: a past project accepted 5 motion-transfer cuts after replace returned `ip_detected`. This is not an operative fallback rule and does not authorize bypassing a current refusal.
- **Not useful** when nothing in the reference performs: static photos, or peopleless refs (City
  Rhythm).
- **Driving video prep.** Muting, splitting at measured source cuts and padding have historical
  evidence (Aura, Altman); the commands are G9's. Preserve captions by default. A supported clean
  intermediate is conditional on saved source layers and exact geometry/timing restoration.
  - **Split** (`routing.md` §3.2). One full-length take only for a reference of about 11 s or less with
    no burned graphics; otherwise 5–9 s parts cut at the reference's own cuts. A per-cut REPERFORM
    (Altman) is one 96-frame clip per cut.
  - **Export at 24 fps with the window crop, muted.** For one cut use G9's
    `frames.py export $W --cut <id> --fps 24 --crop window`. `export` works per cut, so for a multi-cut
    part or a full take run the same frame-exact trim, crop and 24 fps re-time in one ffmpeg pass (even
    w and h; `end_frame` is exclusive):
    ```bash
    ffmpeg -v error -i $W/ref/ref.mp4 -an \
      -vf "trim=start_frame=<f0>:end_frame=<f1+1>,setpts=PTS-STARTPTS,crop=<w>:<h>:<x>:<y>,fps=24" \
      -c:v libx264 -crf 12 -pix_fmt yuv420p $W/cuts/partA.mp4
    ```
    Never pad a native-fps clip of a 25/30/50/60 fps reference: an 11 s 30 fps full take padded as-is
    bills 14 s (154 cr at 1080p) instead of 11 s (121).
  - **Preserve text and graphics in final delivery.** If the supported MT route needs a clean intermediate, save the original source-pixel layers and plan their exact restoration before removing anything. Do not crop away original image geometry or replace the scene with a generic empty studio.
  - **Pad.** MT bills and returns round(seconds).
    - A cut shorter than 4 s of real time: ping-pong to exactly 96 frames (`frames.py pad … --mode
      pingpong`).
    - A part whose fractional second is 0.1 s or less: do not pad. Inspect the actual missing tail and
      fill it only with verified transformed footage or a hold satisfying timing/motion and identity
      locks; otherwise use a bounded permitted correction or report the gap. Original pixels are
      eligible only when verified to contain no targeted change and to satisfy every applicable lock;
      never reintroduce the original target. Aura D's unpadded 11.08 s full take billed 11 s (121) and
      kept the cuts within ±1 f.
    - Any other part: freeze-pad the tail to ceil(seconds) (`frames.py pad … --mode freeze --for mt`). Unpadded,
      such parts came back truncated or extended with invented shots (Aura D halves: 152→145 f,
      114→121 f).
  - **Check** as in G9: the probed frame count ÷ 24 is the intended number of seconds, and the line is
    priced from the probed count.
  - Upscaling the input does NOT raise the output resolution. Never `reframe` a driving video.
- **Params**
  ```json
  {
    "model": "<from plan line: hf_mult_motion_control>",
    "resolution": "<from plan line>",
    "medias": [
      {
        "role": "image",
        "value": "<suitable existing image id, or G5 two-ref still only if needed>"
      },
      {
        "role": "image",
        "value": "<optional extra identity reference; omit this entry if unnecessary>"
      },
      {
        "role": "video",
        "value": "<prepared source-aligned driving clip; text removed only with exact restoration>"
      }
    ],
    "prompt": "<below>"
  }
  ```
  - Roles are the schema keys, as in G9.
- **Price**
  - **11 / 7 / 3 cr per second of driving video** at 1080p / 720p / 480p.
  - MT bills round(seconds): 4 s = 44, 10 s = 110, 11 s = 121.
  - Parts pay their own rounding: Aura G was 6 + 5 + 8 = 19 billed seconds = 209 at 1080p, not
    17 × 11 = 187.
  - A second image is free. Genjutsu defaults to 720p, so always pass the plan line's `resolution`.
  - Like G9, the quote shows MT lines as "fixed input (min-billed)" with no utilisation target. Never
    group cuts into one input to improve the ratio (UNTESTED).
- **Output**
  - Real time at 24 fps.
  - Historical 1080p outputs included 1664×1248 and 1248×1664; probe the actual result rather than assume either geometry.
  - Inspect source text, watermarks and camera motion; restore only elements that differ using their measured original layers and timing.
  - **Map output to the source frame.** Preserve the source aspect, intended subject scale, positions and visible borders. Use the recorded reversible input mapping and measured per-shot geometry. Never apply a fixed crop centre such as 0.35 or discard source content merely to fill the canvas; choose a better-supported source-aligned route or report an unresolved geometry difference if faithful mapping is impossible.
  - A portrait take going to a landscape canvas is a soft 1.54× upscale. Prefer correctly framed source material and measured code composition; never offer a paid-reframe choice or introduce a new approval gate (`budget.md` §1).
- **Count**: the planned take(s), at final settings.
  - The internal plan contains the necessary initial take and bounded corrective retry reserve. Price a possible retry at the full affected job length; never present optional-take menus.
  - For strobe or 1–3-frame-cut references, preserve short cuts through measured per-cut processing and composition. Historical two-take projects are not a reason to generate duplicate full videos automatically.
  - Re-roll a part only when it fails a fail-list check, once, as the same job (`budget.md` §3 rung 5).
    "A better take" is not a failure. Aura's blanket 2-takes-per-part rule doubled spend.
- **Prompt**: let the prepared image carry the intended appearance and scene; let the driving video carry motion and timing. Use one short sentence, at most two and at most 40 words.
  ```
  Animate @Image1 with the source video's motion and camera movement, preserving the image's identity and appearance.
  ```
- **Historical observation, not a prompt rule:** earlier weak input images produced texture/colour drift and long prose was tried. Do not repeat that workflow. Improve the prepared two-reference image within the existing plan and verify the output instead of describing every object, costume, texture or camera beat in the Genjutsu prompt.
- For a verified preset with sufficient selected style and media, omit the prompt or pass an empty string only when its actual contract permits it. Otherwise name the desired operation and one preservation clause briefly. Do not append generic negative lists or a full scene reconstruction.
- **QA every take**
  - Identity on the wrong person, or a role swap.
  - Invented logos. A Nike-like swoosh appeared despite "no logos".
  - A hallucinated reference object in the first ~0.5 s (a plaster car wheel).
  - Wardrobe drift.
  - Duplicate-frame judder.
  - Shots re-ordered or merged on strobe edits: cast them by content.
  - ±1–2 f cut drift: nudge the in-point by 1 frame.

## G11. Mattes: `remove_background`, `sam_3_video` and local masks

Order mattes only after the EDL exists, and only for clips the EDL uses with contour, cut-outs,
behind-subject text or matte-limited grades.

| Model                                          | Call                                                                                                                                       | Output                                                                                                                        | Price                                                           | Use when                                                              |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| `remove_background` (video_background_remover) | MCP `remove_background` `{"params": {"media_id": "<job or media id>", "media_type": "video"}}` (mcp-api §9.1)                              | H.264 **person on black, no alpha**, same size and fps as the source. Keeps only the main subject: Yaong's friend was dropped | 1 cr flat (VERIFIED live 2026-10-08 on a 10 s 720p plate)       | High-key or white-cyc plates (Katana, Yaong)                          |
| `sam_3_video`                                  | Segmentation through `generate_video` with `model: sam_3_video`, `apply_mask: false`, one `video` (mcp-api §9.2); verify the live contract | Binary source-aligned mask; not newly generated creative footage                                                              | Live-price before use; historical ~1.14 cr is not authorization | Dark clothing, hair, multiple subjects or held props                  |
| Local mask / existing mask asset               | Existing compositor or authorized local segmentation                                                                                       | Binary mask aligned to the source frame grid                                                                                  | No new video-generation call                                    | Dark clothing, multiple subjects or held props needing a precise mask |

- **Alpha recipes** (`matte.py`):
  - Division, white-cyc tuned (Katana/Yaong):
    `blend=all_expr='if(lt(B,34),if(gt(A,10),255,0),clip((A*255/B-70)*1.9,0,255))'` with matte as A and
    original as B, both gray.
  - Threshold: `clip((max(RGB)-8)/10)` (Altman).
  - Close holes with dilate/erode ×8 and a slight blur.
- **Gotchas**
  - `color=…:r=<plate fps>` must match the plate fps (the default is 25).
  - Use `alphamerge=shortest=1`.
  - SAM grabs rails and mics: clamp it to an x-range around the hero. It misses held props: union with a
    difference key.
  - Check matte edges at 100% on white backdrops.
  - One `remove_background` call failed (Katana c0) and the retry worked. Check the jobs before retrying.

## G12. Chant, vocal and VO

- **No sung-vocal model exists.** `sonilo_music` and `mirelo_text_to_audio` are "game pipeline only"
  and must not be used for standalone audio.
- **Default soundtrack**
  - EXACT reuses source audio/timing or an explicitly requested replacement. REMIX follows the authored
    audio plan and locks, using actual source/user/stock recordings (`creative-quality.md`). Preserve
    a locked track; no fixed house music, code-synthesized music/SFX or invented delivered stock file.
  - If a required source/stock operation is unavailable, use accessible suitable authorized audio or
    report the actual limitation. Never claim a replacement matches locked source audio when it does not.
- **Chant, `seed_audio`** for planned REMIX speech or an explicitly changed EXACT vocal, using an
  existing noninteractive permitted voice selection; otherwise preserve suitable source vocals
  (a SHAPE like every params block here; mcp-api §10):
  ```json
  {
    "model": "<from plan line: seed_audio>",
    "prompt": "<the whole chant, one take>",
    "voice_type": "preset",
    "voice_id": "<existing user-selected voice_id>",
    "format": "wav",
    "sample_rate": 48000,
    "pitch_rate": 2
  }
  ```
  - Use the authored REMIX words or source-derived EXACT words and the already selected voice pair; never import historical voice IDs or example lyrics.
  - Match planned prosody (measured source prosody in EXACT); punctuation is a conditional tool, never a default cute delivery.
  - Put the whole chant in one take so it can be sliced per word.
- **Price and count**
  - 0.3–2 cr per take.
  - Use one existing user-selected voice pair. Never invoke `list_voices` when it opens a human picker, invent an ID or copy an example voice. If no selected pair is available, preserve source audio or report that replacement speech cannot be produced without the required selection.
- **Slicing**
  - Cut words by energy envelope or spectrogram, **not by Whisper**: its word starts were about 0.27 s
    late on TTS.
  - Historical +2-semitone chain, only when the requested source-matched vocal correction actually needs
    this measured shift; never pitch-shift the reference soundtrack by default:
    `atrim,asetpts=N/SR/TB,pan=mono|c0=0.5*c0+0.5*c1,asetrate=48000*1.12246,aresample=48000,atempo=0.89090,highpass=f=140`
  - Place each word on the beat in code.
- **VO with ElevenLabs v4**
  - When the user says "v4", the model is exactly `elevenlabs_v4` (`dialogue` + `stability` +
    `similarity_boost`; `prompt` is required and duplicates the text). It costs about 0.23 cr per 30
    characters.
  - Put audio tags after the first sentence. A leading tag made v4 repeat it.
  - Aura's generated epic VO direction was rejected by the client in favour of the reference's own
    audio.

## G13. Texture plates

- EXACT reproduces grain, paper, dust, halation or glitch only where measured in source, with matching
  scale, trajectory, blend, intensity and intervals. REMIX uses the selected reference texture grammar
  with authored intervals and intensity recorded in its layer plan (`compositing.md`).
  Do not use canned noise, RGB split, random jitter or generic flashes as a substitute for source texture
  and transitions. Existing source texture may be retained when the requested scope permits it.
- Aura H used `gpt_image_2_5` for a paper texture: 2 jobs, 1 used, 2.75 cr each as observed (Sunburst
  estimates are unreliable).
- If you use `gpt_image_2` instead, pass `quality` explicitly. The CLI default is high + 2k at 6.5 cr;
  the MCP default is low + 1k at 0.5 cr.

## G14. Cheap motion previews (prices VERIFIED live; preview fidelity UNTESTED)

- **Seedance draft** (VERIFIED live 2026-10-08 unless marked)
  - Seedance 2.5 `draft: true` always bills at the 480p rate, 3 cr/s: a 4 s draft was charged 12. Its
    output is **752×560** for 4:3, 24 fps: a blocking preview, never footage.
  - It can be finalized within 7 days via `draft_job_id`. the verified non-generating estimate on the finalize returns the **full
    1080p price** (4 s → 48). The finalize is **always 1080p**: a `720p` resolution param is ignored.
    Without `duration` it prices 5 s (60), so always pass the draft's own duration.
  - So draft + finalize = 12 + 48 = 60 for a 4 s clip, **1.25× a direct 1080p job** (48) and 2.1× a
    direct 720p job (28). It never pays on a 720p plan.
  - It pays on a 1080p plan only when more than about 20–25% of direct takes would be rejected
    (break-even: 12 ÷ (1 − r) + 48 = 48 ÷ (1 − r) gives r = 25%; 20% if the rejected drafts' own 12 cr
    are ignored). Use it only if already explicitly requested and included in the finite plan: whether the finalized clip keeps
    the draft's motion and framing is unverified (no finalize job has run).
- Drafts use only `seedance_2_5`; no cheaper alternate video model is allowed. Use a draft only for an already justified planned composition check, never as final footage.

---

## 1. Prompt ownership and clean layers

The task contract and explicit locks govern creative ownership. EXACT preserves source identities,
wardrobe, props, expressions, lens style, logos, text and measured texture. REMIX preserves intended
identity and selected visual grammar while deriving new scenes and wording from the creative plan.
Historical examples never supply missing content. Do not add a generic cinematic style, remove locked
glasses or change a planned gesture merely because a prior project preferred it.

Put format, duration and resolution in verified parameters. Every clean intermediate has a concrete
final-layer plan: EXACT restores original graphics at their measured frames/positions; REMIX composes
its authored text/graphics and preserves locked/reused source layers. Never erase a requested element
from delivery. Prompt timecodes are approximate guidance; inspect actual returned footage and align
to the output timeline, which equals the source frame grid in EXACT unless explicitly changed.

## 2. Rejections and permitted recovery

Follow provider restrictions. Do not disguise a restricted identity or costume, remove input evidence, rename prohibited content, or route the same refused request through another model to defeat moderation. Correct a genuine technical input error or use a clearly supported alternative that fulfills the actual request. If exact reproduction is unavailable, retain allowed reference material where possible and report the specific unresolved difference without a question or false 1:1 claim.

Historical refunds are not a guarantee. Reconcile each job debit and refund against transactions. The debit remains part of spend until its refund is verified. A failed request with unknown billing never authorizes a replacement charge automatically.

## 3. Fidelity gate

Compare every candidate against its output role, ownership and explicit locks. EXACT also compares
corresponding reference frames/audio for pose, framing, wardrobe, text, light and timing. REMIX checks
story/visual-motif continuity and selected reference grammar rather than penalizing planned new scenes.
Reject identity/anatomy errors and unintended drift, not deliberate source traits or permitted authored
changes. Choose internally, log defects and use only bounded corrections in the priced plan. No taste
question or external creative approval gate.

## 4. Known failure modes and fixes

The source-preservation fixes below apply to EXACT/local transformations or the corresponding explicit
lock. For new REMIX scenes, compare against the authored shot contract instead. Historical incidents do
not introduce a fixed cast, soundtrack, pose or style, nor make Genjutsu the default generation route.

| Symptom                                                             | Model                                      | Cause or trigger                                                                  | Fix                                                                                                                                                                                                                                                                                                                                   | Source                                                           |
| ------------------------------------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `Preset "IN THE DARK" was recommended`, no job                      | Seedance, MT, replace (long prompts)       | The MCP preset recommender                                                        | Find bounces free with the verified non-generating estimate on every distinct prompt; the bounce reproduces on the real submit unless the item carries `declined_preset_id` (VERIFIED live 2026-10-08); resubmit ONLY the bounced items with the id read from the response (so far `24bae836-2c4a-48e0-89b6-49fcc0b21612`); no charge | Katana, Yaong, Altman, Aura G, 2026-10-08 run                    |
| `nsfw` on 4/4 jobs                                                  | Seedance                                   | Audio ref + `generate_audio:true`, plus suggestive wording                        | Preserve source audio; comply with the rejection and use §2 recovery                                                                                                                                                                                                                                                                  | Yaong                                                            |
| `nsfw` on 5/6 clips                                                 | Seedance, NB still                         | Copyrighted costume (Spider-suit)                                                 | Preserve permitted source material or report the unresolved change; do not disguise the refused costume                                                                                                                                                                                                                               | /test-edit                                                       |
| `ip_detected` (refunded)                                            | replace                                    | Recognisable film scene, per scene                                                | Use supported source reuse or report the unresolved cut; do not transfer the same rejected content to another model; verify refund                                                                                                                                                                                                    | Altman                                                           |
| HTTP 422, no body, or input rejected                                | replace, MT                                | Input under ~4 s                                                                  | Export at 24 fps, then ping-pong pad to 96 f (G9)                                                                                                                                                                                                                                                                                     | Altman, Aura G                                                   |
| 89 frames back for a 96-frame pad, a different frame size           | replace                                    | Output length and size follow the model, not the input                            | Map frames proportionally (`assemble.py`; G9 "After generation")                                                                                                                                                                                                                                                                      | 2026-10-08 Altman c12 (VERIFIED live)                            |
| Output truncated, or extended with invented shots                   | Genjutsu                                   | Input not a whole number of seconds                                               | Freeze-pad to ceil(seconds); an MT part with a fractional second ≤ 0.1 s may stay unpadded (G10); map frames proportionally                                                                                                                                                                                                           | Aura D/CUR                                                       |
| Driving clip bills 1.25–2.5× more; motion slowed                    | Genjutsu                                   | A 25/30/50/60 fps cut padded at 24 fps as-is                                      | `frames.py export --fps 24` before `pad`; price from the probed frame count                                                                                                                                                                                                                                                           | Local frames.py test (cost review); Altman exported at 24p first |
| Pose broken, gloves lost                                            | replace                                    | Hold padding                                                                      | Ping-pong padding                                                                                                                                                                                                                                                                                                                     | Altman                                                           |
| Hero wears the photo's clothes                                      | replace                                    | The prompt enhancer defaults to the complete look from @Image1                    | Use the short source-wardrobe preservation clause and a suitable prepared image; verify the SWAP output                                                                                                                                                                                                                               | Altman; mcp-api §6.2                                             |
| Car stays, badges leak                                              | replace                                    | Class change                                                                      | MT or GENERATE                                                                                                                                                                                                                                                                                                                        | Aura G, E                                                        |
| A word at ~60% opacity, a glyph on the hair, fades 1–2 f off        | replace                                    | 24p re-render of baked text                                                       | Text check + re-lay from reference pixels                                                                                                                                                                                                                                                                                             | Altman c01                                                       |
| Background pulled from the photo (stage, giant letters)             | MT                                         | Bare photo as the image                                                           | Reuse a suitable source-aligned image, or prepare G5 only when needed                                                                                                                                                                                                                                                                 | Altman c03                                                       |
| Dark, textureless objects; colours lost                             | MT                                         | Depth-mask driven; thin prompt                                                    | Improve the prepared reference image and verify colours; keep the Genjutsu prompt short (G10)                                                                                                                                                                                                                                         | Aura (Nurbek), Signal                                            |
| Garbled copies of reference captions or graphics                    | MT                                         | Burned text in the driving video; long parts                                      | Preserve source scene and lettering; use a clean intermediate only with saved exact text/graphics restoration and measured source cut boundaries                                                                                                                                                                                      | Creator POV, Signal                                              |
| Invented swoosh or stripes                                          | MT                                         | — ("no logos" does not stop it)                                                   | Remove only newly invented marks; use a bounded retry only for a measured unresolved defect                                                                                                                                                                                                                                           | Aura H t3                                                        |
| Second performer becomes a faceless mannequin, or roles swap        | MT                                         | Two performers                                                                    | Use a minimal target-position cue; prefer replace when other source people must stay                                                                                                                                                                                                                                                  | Aura B, A                                                        |
| A plaster car wheel in the first ~0.5 s                             | MT                                         | Reference object hallucinated at the take start                                   | Use a later in-point only if all required source motion still aligns; otherwise correct within the bounded plan                                                                                                                                                                                                                       | Aura G                                                           |
| Shots re-ordered or merged                                          | MT                                         | Strobe or 1-frame cuts                                                            | Restore source shot order and exact intervals with verified matching footage; report any missing beat                                                                                                                                                                                                                                 | Aura H                                                           |
| Wardrobe drift (boots for sneakers)                                 | MT                                         | Wardrobe not spelled out                                                          | Prepare the correct wardrobe in the input image; use one short preservation clause                                                                                                                                                                                                                                                    | Aura G v4→v5                                                     |
| Gestures arrive 1.5–2.7× late (or, in another plate, right on time) | Seedance                                   | Timecodes are ordering hints; adherence varies per plate                          | Slots of 2× the needed seconds (G7 duration rule); critical beats early; in-points from the sheet, never from timecodes                                                                                                                                                                                                               | Yaong (late); 2026-10-08 Katana run (on time)                    |
| Coy grin instead of a cool stare                                    | Seedance                                   | "barely visible smirk"                                                            | Correct the generated expression through the permitted generation route within the reserve; never warp or repaint the face in code                                                                                                                                                                                                    | Katana f2b                                                       |
| Black blob or white bar under a threshold                           | Seedance                                   | Backlit silhouette, specular glint, prop into the lens, worm's-eye                | Preserve source backlight, glints and angles; repair only introduced defects using source-matched compositing                                                                                                                                                                                                                         | Katana f3b, f4, f1                                               |
| Face crushed to near-black on identity-legible medium close-ups     | Seedance + code xerox                      | The full-strength threshold, where the reference keeps facial detail              | If the compositor caused it, correct the whole-shot grade; no face-only mask, retouch or repaint. A generated facial defect needs a permitted generation correction                                                                                                                                                                   | 2026-10-08 Katana run (VERIFIED live)                            |
| A past project's wardrobe or props in a new user's plate            | any prompt                                 | VERBATIM example copied with its identity items                                   | Copy the structure only; leak check (§5 #10)                                                                                                                                                                                                                                                                                          | Dry-run eval, 2026-10-08                                         |
| A second person cropped away or dropped by the matte                | Seedance + face-lock / `remove_background` | Extra identity in a face-locked plate                                             | Restore every source performer via an appropriate full-cast plate or separate preserved layers (G7)                                                                                                                                                                                                                                   | Yaong friend                                                     |
| Garbled lettering on waistbands                                     | Seedance                                   | —                                                                                 | Restore original lettering pixels/geometry; remove only invented marks and never crop away source content                                                                                                                                                                                                                             | Aura B                                                           |
| A different man across shots                                        | Seedance                                   | Sheet only (face widens); glasses; mixing a real close-up with generated identity | Sheet + real face frame; preserve reference glasses; one identity source per sequence                                                                                                                                                                                                                                                 | Aura G v1/v3                                                     |
| Wrong coat colour                                                   | gpt_image_2                                | —                                                                                 | Seedream i2i (G3)                                                                                                                                                                                                                                                                                                                     | Yaong                                                            |
| Phone camera-UI overlay                                             | Soul 2.0                                   | —                                                                                 | Reject; pick another variant                                                                                                                                                                                                                                                                                                          | Yaong friend #8                                                  |
| Bipedal "wolf", photoreal "anime", grey background                  | soul_cast                                  | Photoreal-humanoid prior                                                          | nano_banana_2 or gpt_image_2_5                                                                                                                                                                                                                                                                                                        | Memory note                                                      |
| Stickers look small                                                 | Seedream remove_bg                         | Large transparent margins                                                         | Crop to the alpha bbox +6 px                                                                                                                                                                                                                                                                                                          | Katana                                                           |
| Holes in dark clothing or hair                                      | remove_background                          | Person-on-black alpha is ambiguous on dark                                        | Use `sam_3_video` or a local/existing binary mask; validate one clip first                                                                                                                                                                                                                                                            | /test-edit, Altman                                               |
| Matte grabs rails or mics; misses held props                        | sam_3_video                                | —                                                                                 | Clamp the x-range; union with a difference key                                                                                                                                                                                                                                                                                        | Aura D, Signal                                                   |
| Whisper word times ~0.27 s late                                     | faster_whisper on TTS                      | —                                                                                 | Slice by energy envelope                                                                                                                                                                                                                                                                                                              | Yaong                                                            |
| v4 repeats the opening audio tag                                    | elevenlabs_v4                              | Leading tag                                                                       | Tags after the first sentence                                                                                                                                                                                                                                                                                                         | Aura journal                                                     |
| A plate arrives after planning started and is never used (180 cr)   | any                                        | Cataloguing and EDL work before `jobs_wait` finished                              | Between polls only reference-side work; no catalogue, in-points or EDL until every paid job is terminal; a late job is catalogued and the EDL reviewed before rendering                                                                                                                                                               | Katana f3a                                                       |
| Double charge risk                                                  | any                                        | Resubmitting after a transport timeout                                            | Check jobs first; never auto-resubmit                                                                                                                                                                                                                                                                                                 | MCP tool doc                                                     |

## 5. Pre-submit checklist (every paid call)

1. Complete the native-frame inspection and per-second log required by `analysis.md`. The task
   contract selects REMIX/EXACT and the creative plan supplies output target/roles/evidence. The job
   traces to an output shot and relevant source evidence; EXACT retains source interval mapping.
   Its route is in `plan/routes.json` and fits the finite priced plan authorized by task/account rules:
   it is ready or properly activated, never still deferred. Every declared dependency is a completed
   ledger job and the exact quote fits its original planning bound and unchanged workflow ceiling.
   `ledger.py guard $W --line <ID>` passes (a re-roll adds `--reroll-of <job> --reason
   <fail-list item>`).
2. For direct Genjutsu or a Genjutsu preset, keep the prompt to one short sentence (at most two, at most 40 words), or empty only where the preset contract permits it. Check the execution-contract model allowlist on this exact request or batch item: fresh video is `seedance_2_5`; only justified selected source-anchored Genjutsu transformations or a verified preset/Styles route are exceptions. Segmentation and post-production utilities are allowed exceptions, not creative video engines. Image preparation remains on image models. Supply only fields supported by that exact live operation: applicable model, mode, resolution, duration and aspect values come from the plan. Direct Genjutsu follows the source input and does not receive unsupported mode/duration/aspect fields. Every Seedance call
   has `generate_audio:false` and `bitrate_mode:"high"`, stated on its plan line too (header). None of
   them appear in the prompt.
3. Media are media_ids or job_ids. Roles are the schema keys (Genjutsu: `image` +
   exactly one `video`). G4/G5 use the two-reference source-frame/identity baseline. Other necessary
   REMIX scene/asset combinations use the smallest sufficient set within verified limits, with each
   input's ownership recorded. SWAP uses a suitable supplied replacement image, or a necessary verified
   source-aligned prepared image; MT/Seedance preparation is likewise conditional, never an automatic extra job.
4. The prompt fulfills the selected task mode, output role, explicit locks and assigned reference
   ownership. EXACT preserves source details except requested changes; REMIX implements the authored
   scene and selected visual grammar. Intermediate clean layers have a final compositing plan and §2
   restrictions are followed. Its verified non-generating estimate returned a price; if a literal-retry recommendation appeared, the item carries
   the `declined_preset_id` read from that notice.
5. Genjutsu input: prepared according to the verified live contract and G9/G10, with original geometry retained. Captions/graphics are removed only from a planned intermediate with saved exact restoration. For the historical 24 fps padding route, input is retimed before padding
   (exactly 96 f for cuts under 4 s). Its probed duration is the intended whole number of seconds, and
   the line was priced from the probed frame count.
6. `count: 1`; no character or voice picker.
7. This is its family's canary (a planned job covering the family's hardest fidelity constraints, submitted individually), or its family's canary has passed. Never collect separate reservations into one batch submit.
8. Log the job id, params, quoted credits and purpose in `plan/ledger.json` at submit time
   (`ledger.py add $W --line <ID> --job <job_id>`).
9. Every supported request field equals the plan line, including model and any applicable mode, resolution and billed seconds. Do not inject unsupported fields into Genjutsu. `ledger.py params $W
   --line <ID>` prints the skeleton, and `--check '<params json>'` compares (exit 1 = mismatch). A
   mismatch is unplanned spend: stop and fix the params or the plan, and re-quote if the plan changes.
10. Leak check: no garment, prop, colour, place or gesture in the prompt comes from a cookbook example
    instead of the current source evidence, explicit request or authored creative plan (header rule; Katana's micro shorts, green lipstick
    and cross thigh-highs leaked into another user's plates in a dry-run eval).
11. Every planned performer and layer survives tracking/cropping/matting. EXACT/local replacements
    retain untargeted source people and layers. Intended identity is checked across all output
    appearances, including back views, silhouettes, helmets, hands, crops and occlusions. A locally
    replaced hidden-face subject cannot silently become KEEP or reveal a face solely to prove identity.
    Full regeneration covers every required output shot. Reuse suitable images; G4/G8 and reusable
    assets are conditional, never a mandatory paid chain. Clean intermediates have an explicit final
    layer plan; generic studio/crop defaults cannot overwrite exact locks or the REMIX scene design.
12. No face was generated, replaced, deformed, retouched, repainted or locally relit by code. Identity
    changes and facial corrections trace to the authorized model job; tracking and whole-layer
    composition preserve that result's facial geometry and appearance.
