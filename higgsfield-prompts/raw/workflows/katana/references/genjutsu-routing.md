# Reference-image reconstruction and optional Genjutsu presets

Load this reference when a remake contains a public figure, requires an identity transformation, or needs an anime look. It does not introduce questions, galleries requiring user selection, consent steps or new spending authority. All existing fidelity, font and finite-budget rules still apply.

Read the creative mode from `analysis/task-contract.json`, separately from any provider API mode.
REMIX is the default for a new deliverable; EXACT follows an actual request for 1:1, the same edit,
only replacing a subject or equivalent preservation. A continuation retains its mode until actual
user steering changes it; quoted/negated examples do not toggle it. Both modes preserve explicit locks
and the intended user identity. REMIX may author new story, scenes, text, framing and length using
selected reference visual grammar, with scope-specific exact locks recorded in the contract.

## Engine selection

Fresh scene footage, missing motion plates, previews, extensions and corrective generation use `seedance_2_5` only. Do not substitute another video-generation engine for price, speed, availability or a rejection. Image/keyframe models and segmentation/compositing utilities are separate operations and remain available.

Genjutsu exceptions transform an existing source: a selected local object/subject replacement,
particular desired source choreography, or a suitable verified preset. Record why that output role
needs the operation; a REMIX, new world, public figure or anime look alone is not a motion-transfer
trigger. Prefer usable existing footage, conditional image preparation and Seedance 2.5 for new REMIX
scenes. Choose one necessary path, not every model in sequence. EXACT preserves all required source
shots; REMIX retains suitable source intervals only where they serve the authored output plan.

Identity and facial changes are model operations, never local pixel repairs. Do not paste or warp a
photo's face/head onto the source, recolor facial/hair pixels, draw anatomy, run a local swap/restoration
model or animate eyes/mouth with code. After image-first reconstruction, deterministic animation means
timing and movement of the complete finished plate plus separate source graphics. A wrong face needs
a permitted bounded generative correction, not a cheaper code fallback. Follow SKILL.md's face boundary.

## Public figures without a blanket stop

A known face or name alone does not make this workflow unavailable. Preserve the intended subject
and identity locks. EXACT keeps the source subject except requested replacement; REMIX follows the
authored cast rather than automatically recasting the user's hero as a reference celebrity. If a public
figure's existing footage serves a selected slot, reuse authorized pixels and edit in code. Do not
wastefully regenerate the person from a name-only prompt.

For a selected local identity replacement, `hf_mult_replace_object` may use the confirmed source video
and intended supplied image references. Use `hf_mult_motion_control` only when the shot requires that
existing movement/camera choreography. New REMIX scenes normally use image preparation and Seedance
instead. Source media, approved identity references and the intended edit determine inputs; do not
invent a face reference, scrape private likeness data or reinterpret a style thumbnail as a person.
A compatible authorized image step may prepare a necessary reference within the same finite plan.

Apply a subject change to every appearance in the selected replacement scope, including back views,
silhouettes, helmets, body crops and occlusion. No clear face is not a KEEP criterion. A local source
replacement preserves hidden-face pose, untouched people, camera, background, timing and graphics.
Other REMIX shots preserve their authored cast/identity and explicit locks without requiring every
source cut to reappear. These supported routes do not promise to defeat provider restrictions. Never
obfuscate names, disguise identity or move refused content between models to evade a restriction.
Correct confirmed technical input errors; for substantive rejection use allowed source material or
disclose the affected slot without questions. Never call synthetic performance genuine archival
footage or a real endorsement.

## Reference frame plus uploaded character

The exact two-reference recipe below applies to source-anchored character replacement in either mode.
For a new REMIX scene, a reference frame may supply only selected style/texture grammar while the
creative plan supplies new pose, space, camera and story. Record those separate ownership assignments;
use conditional existing/prepared hero, location or prop references as necessary within the live tool
limits. No mandatory character/location sheets or code-based head/face changes. `generation.md` gives
the optional image/Seedance causal and spatial prompt structure.

Anime and stylized source images do not require Genjutsu presets. When the requested change is a character replacement, first consider a multi-reference image-generation operation using two actual inputs: the original reference frame and the user's uploaded character/photo. Use the selected shot's clean native-resolution frame, not a contact sheet or a text-only scene description. Reuse already uploaded media identifiers.

The original frame controls framing, camera angle, pose, subject placement, background, lighting, palette, linework, texture and reference wardrobe. The uploaded image supplies the intended character identity and distinguishing traits. Transfer only explicitly requested clothing or props from that image; its portrait background, lighting or photo-real style must not overwrite the source scene. Replace the intended source character rather than blending the original and replacement identities. Preserve exact source text/graphics as separate compositing layers when image generation cannot keep them exact.

Use the already selected compatible image model or the connected image-editing default after verifying two-image reference support. Inspect the result internally against both inputs: source structure and visual treatment must match independently of replacement-identity fidelity. Keep the bounded still-attempt limit; no user choice or approval. This applies to anime, illustration and other stylized references as well as realistic frames.

Choose the next step from the measured shot: use the image directly with deterministic timing/layers for still-based edits; animate it with Seedance 2.5 when new continuous motion is necessary; use direct Genjutsu motion transfer only when the actual source choreography is better preserved that way. Do not add all routes in sequence. Price the selected still and motion path once, without automatically buying an extra style pass.

## Optional Genjutsu presets

Use the user's term Genjutsu presets for the optional catalog route. The connected preset operation supports the Genjutsu catalog through `get_presets` with `source:"genjutsu"`; exact categories, preset IDs and execution contracts come from actual responses. The generic Genjutsu preset catalog includes workflows beyond restyling. Do not assume every preset is a visual style, or substitute a preset's example subject or driving clip for the user's intended source.

Choose a compatible preset autonomously only when it serves the planned transformation better than
image-first reconstruction and runs noninteractively. EXACT preserves measured timing/source context;
REMIX preserves its selected output role and locks. A preset never replaces the intended media with
its demo choreography. A missing preset/picker is not an anime blocker: use a suitable authorized
image-first route. Never open a picker or ask the user to choose.

Genjutsu Styles/Restyle is one possible style-transfer capability, not a required anime stage and not another name for every Genjutsu preset. The public Restyle style IDs and connected Genjutsu catalog IDs are different namespaces; never interchange them without a verified mapping. Load the conditional API details below only when that precise Restyle operation is selected.

## Short Genjutsu prompts

For direct Genjutsu calls and preset text fields, default to one sentence and allow at most two sentences / 40 words. State the transformation and a minimal preservation rule. Appearance, source action, camera and composition already come from the media. Do not restate every visual trait, scene beat, texture, effect or clothing detail. Preserve the full analysis and compositing plan outside the generation prompt.

A replacement prompt can be: "Replace the main subject with the character in the reference image. Preserve the source motion, camera, background and timing." A motion-transfer prompt can be: "Apply the source video's motion to the character in the reference image, preserving framing and timing." For a fully specified preset, omit the prompt or use an empty string only when its actual contract permits it. An extra phrase is justified only to resolve a concrete ambiguity, such as which of two subjects changes. This rule does not limit the image-editing prompt or Seedance shot instructions.

## Conditional Restyle API

The [official API reference](https://open.higgsfield.ai/models/higgsfield/genjutsu/restyle/v1.0/api-reference) identifies `higgsfield/genjutsu/restyle/v1.0`. Discover styles with `GET /models/higgsfield/genjutsu/restyle/v1.0/presets`; submit through `POST /higgsfield/genjutsu/restyle/v1.0` on `https://api.higgsfield.ai`. Use a current returned style UUID, never a documentation sample.

The inputs are `video_url`, `preset_id`, optional `image_urls`, `prompt` and `resolution`. Keeping source subjects needs no character images. Character references allow at most five. Resolution is 480p, 720p or 1080p. Supply downloadable media, including valid signed URLs. Source clips must be at least four seconds and at most 200 MiB; longer-than-30-second inputs are truncated, so prepare the intended segment first. Framing follows the source; no duration, aspect-ratio or fps parameter exists. Audio is retained, but output cadence and exact frame counts may differ. Await the returned asynchronous request until completion and retrieve its video URL.

## Capability and accounting boundary

The public API and the connected MCP catalog are different contracts. During this review the public Restyle endpoint was documented, but the connected video-model catalog exposed only the two direct Genjutsu models, with no Styles parameter. Do not assume that a public API model path works as an MCP model ID or inject `preset_id` into motion-control parameters without a verified contract.

At execution, use a verified connected Restyle operation if one is available. Otherwise an already configured authorized API integration may use the documented endpoint. Do not ask for credentials, inspect unrelated secret files, put secrets in prompts or logs, invent tooling, or install a new integration to conceal unavailability. If neither route exists, continue through image-first reconstruction when it can fulfill the request. Only an explicitly required, indispensable Restyle-only operation remains a reported capability limitation. Never claim Styles ran when another route produced the result.

Verify actual account pricing and the finite ceiling before any selected stage. Dollar-denominated API prices are not Higgsfield credit amounts; do not reuse motion-transfer prices for Restyle or fabricate a currency conversion. Keep exact native operation/model identifiers in accounting. If a bundled ledger cannot represent a new operation accurately, do not mislabel it as Seedance or bypass a guard.

## Reconstruction check

Complete the full native-frame inspection and every-second event/texture log from [analysis.md](analysis.md) before choosing generated clips or paying for transformations. Image-first reconstruction, a preset or motion transfer does not replace this analysis.

In EXACT, map transformed shots to the locked source timeline, restore original text/audio as required
and inspect source/result frame pairs. In REMIX, map them to authored output shot IDs and inspect
their specified action, selected grammar and explicit locks; retained exact motion still needs source
comparison. In both modes check identity, pose, camera, linework and temporal flicker, then validate
the planned output frame count/fps. A Styles result never proves exactness by broad action alone.
