# /3d-jutsu/references/location-new-angles

(note: instructions_markdown value from {"mode":"instructions",...} response, JSON string unescaped to plain markdown)

# Location new angles

Reconstruct a supplied location image as one editable scene, compose selected new
cameras, and restore appearance only when requested. Produce recognizable views
of the same place. Use this for interiors, streets, landscapes, industrial spaces
and fictional environments; image critique alone does not authorize construction
or generation. Continue requested edits to an existing scene without restarting
intake. Reply, label plans and describe shots in the user's language.

## Inspect and establish the shot specification

Inspect the source pixels and actual dimensions. Record observed silhouettes,
colors, patterns, counts, facing, connections, openings, contacts, depth order,
lighting and edge objects separately from inferred depth and approved additions.
One image does not establish exact metric dimensions or hidden geometry.

Ask only about important unresolved hidden areas, particularly behind the source
camera. Offer a reverse wide, optional side medium and optional detail, naming
subjects and connecting landmarks; the user chooses the actual shots. Preparing
three options does not authorize three generations. Infer relative scale unless
physical accuracy or an important ambiguity requires dimensions.

Prepare the visible scene while awaiting required hidden-layout answers, but do
not build dependent content before the answer. If the user authorizes proceeding
without questions, infer ordinary continuation conservatively and label it as
inferred. Preserve this mode across tool calls until the user changes it.

Maintain a per-shot specification: camera side and direction anchored to named
landmarks, near-to-far object order, facing and visible sides, visible counts,
whole-object coverage or intended crop, symmetry/alignment and approved changes.
Update it from user corrections and annotations. Do not ask again about a clear
correction or a decision already supplied.

For first construction or major layout changes, establish a compact top-down plan
with observed/inferred areas, objects, openings, source and proposed cameras.
Use camera numbers, viewing rays and center directions, and explain approximate
scale and the left/right frame. Show an annotatable plan when it resolves ambiguity
or is requested. For a clear autonomous brief, it can accompany the first source
and top previews; do not make a separate diagram approval cycle. Wait only for an
explicitly requested plan approval or a required unresolved layout choice.

## Match the source before making new views

Build the visible location under a saved source-control camera. Fit camera and
geometry together: perspective, projected positions, sizes, silhouettes,
orientations, overlaps, openings and distinctive medium-scale structure. Use
simple colors and materials; spend geometry on identity and spatial relations.
Dense rooms may use colored proxies, but large opaque boxes must not erase holes,
passages, thin objects or foreground context. Streets need coherent kerbs, fences,
paths, vegetation boundaries and structural rhythm.

Keep semantic parts editable with stable names and centered origins. Reuse shared
mesh/material data and parameterized components for repeated geometry; avoid
thousands of operator calls and model only detail visible at delivery scale.
Example dimensions from another location are hypotheses, never measurements of
this source. Blender is Z-up; editor/glTF coordinates are Y-up. Update the correct
scene/view layer before reading world matrices or bounds.

Acquire a small sharp material-color source-control preview and a full technical
top view, together when the current worker budget permits. Collect one correction
list for camera, layout, scale, facing, contacts and occlusion. Workbench verifies
geometry only; use a separate small appropriate-engine preview for lighting,
transparency, reflection or depth of field. A top view cannot prove unseen layout
from one perspective image. Fix meaningful mismatches before calling new cameras
ready. Exact textures and unknown real-world measurements are not prerequisites.

Extend approved hidden surroundings in the same scene without disturbing verified
geometry, and recheck the source camera when additions could affect it. Include a
neutral inferred ceiling for an indoor scene even if the master does not show it.
Never move objects independently per shot to rescue a composition; preserve the
main scene when the user requests an experimental branch.

For a reverse, start near a familiar anchor, move only far enough past or beside
it to reveal the opposite context, then turn back. Adjust lateral position and aim
independently. Determine its visible side from actual orientation. Reversal is
not mirroring, and no fixed camera travel distance fits every location. Default
new wide views to three-quarter composition; honor explicit camera requests.
Medium/detail views need depth but not a mandatory three-quarter angle.

Verify every requested camera's modeled surroundings, anchors, counts, facing,
openings, foreground occlusion and coverage. Source matching alone is insufficient.
For requested whole objects check all frame edges; equal world dimensions do not
prove equal projected lengths or centering. Choose tolerances appropriate to the
request rather than claiming approximate alignment is exact. Keep a sharp control
for any defocused shot; focus and look-at targets are separate, and blur cannot
repair bad blocking.

## Prepare clean references and prompts

Render at the source's actual aspect ratio unless the user selects another. Do
not silently stretch, crop, add bars or substitute a widescreen preset. A technical
plan can use a different format. Check the generation tool's supported formats
and actual output dimensions before promising exact final-format preservation.

Angle references contain no UI, grids, labels or camera icons. Update the separate
plan from settled transforms and optics, linking camera numbers to thumbnails and
descriptions. For high cameras show a frame footprint on an explicit reference
surface when useful; viewing rays alone do not show occlusion or focus distance.

Immediately before each prompt, inspect the master, source-control preview and
current angle again. Fix contradictory geometry before prompting. Default to two
references: master supplies identity, materials, palette, imperfections, visual
character and lighting evidence; current angle supplies camera, placement,
footprints, facing, overlaps, openings and structural silhouette. Keep the
source-control preview for internal QA. Only add it as a correspondence key for a
specific unresolved mapping if the selected tool permits another reference. An
approved same-direction sibling can identify revealed items, but must not compete
for camera/layout. Avoid chains of generated masters.

Number images by actual submission order, not by the default order described
above. Map proxies to real items explicitly without treating boxes as literal
anatomy. Describe only this shot's visible foreground, subject and background:
camera position/direction, height/tilt, horizon, frame bands, visible sides and
counts, crop and occlusion. Name critical items behind the camera or outside the
crop only when omission could cause hallucination. Total scene counts and visible
counts may differ. A reverse does not mechanically reverse every object's order.

Preserve distinctive types, silhouettes, local hues, directional patterns and
imperfections. Describe thin props, continuous drapery, open passages, door wall
relations and connected structures explicitly. For stairs/ramps identify endpoints,
ascent direction, landings and separate rails/supports. Newly revealed areas need
approved content and the master's architectural/dressing density, not arbitrary
decoration of established parts.

Translate lighting from its world source into the new camera frame; do not copy
the master's screen-left/right light placement. Cover source location and type,
soft/hard and broad/directional quality, lit surfaces, ambient foundation and
plausible falloff. Preserve material palette and white balance rather than equal
pixels on differently lit surfaces. State primary illumination before decorative
lamps. Avoid repeated darkening language or unrelated negative lists. People,
text and signs follow the source and user intent; there is no universal ban.

Write a concrete per-view prompt in this order: input roles/proxy mapping, verbal
camera lock, layout and visible sides/counts, approved revealed content, identity
and directional patterns, lighting/palette, focus and a short reminder of risky
invariants. Omit inapplicable clauses, replace every placeholder, and trim duplicate
adjectives before spatial constraints. Prompt length is not a quality guarantee.

## Generation and review boundaries

Use Seedream 5.0 Pro for appearance reconstruction. Flash is only an explicitly
selected budget experiment; never silently substitute a model or claim a measured
quality advantage. Inspect current model/tool settings, reference capacity, format
support and cost. Do not hardcode historical prices or claim scene work is free.

Default mode: finish geometry, camera checks, clean previews, reference preparation,
per-view prompts and a current cost estimate before requesting approval. Show the
settled scene and selected camera previews, then end the turn with a direct request
to generate the named shots, image count, model and estimated total cost. A general
request for new angles alone is not approval of that paid batch. This gate applies
to appearance generation, not the scene preview renders needed to prepare it.

An explicit instruction to generate without further confirmation, including casual
wording, authorizes proceeding through generation and bounded correction within
the user's count, settings and budget. Retain that instruction; do not stop for a
redundant plan or generation approval. Service-required payment choices and missing
mandatory authorization remain blockers. Silence never supplies permission.

Start with one image per selected view. Track proposed/submitted counts and total
estimated spending, including retries. Approval covers the presented scene revision,
shots and settings across calls. In default mode, show updated previews after
requested 3D edits and obtain approval for the updated batch unless already covered.
Extra generations need approval unless already authorized, including by the user's
no-confirmation mode. Respect the runtime's approval controls in either mode.

For this MCP, prefer `scene_builder_3d_generate_angles` when its contract fits:
provide the inspected angle's `operationId`/`artifactId` and the confirmed master
as `referenceMediaId`, then poll `scene_builder_3d_get_generation`. Inspect the
actual reference ordering; do not assume the master is image 1. This path supports
one optional uploaded reference and enumerated `aspectRatio`, not arbitrary extra
images or width/height. If the required format or conditioning is unsupported,
resolve that limitation before submission. Generic `generate_image` may be used
when its current model contract supports the required inputs; inspect metadata and
estimate the actual settings first. Upload according to the connector profile,
never assume a local desktop file exists in the remote sandbox. Refresh expiring
authorized artifact URLs just before use; never bypass access controls.

For an uncertain submission, reconcile the known request/job before retrying.
With the hosted generation tool, reuse exactly the same `requestId` and arguments;
do not allocate a new ID to recover an unknown outcome. Retry only failed shots.

At each actual scene review or delivery boundary, call
`scene_builder_3d_show_scene` once with the exact settled revision after visual
verification. It ends that phase's scene inspection/edit calls; generation and
status calls may follow in an already authorized batch. Do not repeatedly show an
unchanged revision or use the widget as the agent's visual evidence. Displaying a
scene does not prevent later corrections.

## Check, recover and deliver

Compare each output to its angle for camera, layout, facing, visible counts,
openings, anchor direction, crop and occlusion; compare to the master for identity,
silhouette, materials, imperfections, palette and spatial lighting logic. Check the
latest explicit shot specification and approved hidden content. Attractiveness
does not establish correctness.

User feedback or a concrete QA failure can trigger correction. If the blockout's
geometry/layout/camera is wrong, repair the affected scene parts and settle a new
revision. Re-render affected views and the source control when relevant; replace
stale plans, previews, prompts and references. If the blockout is correct and only
appearance/projection drifts in generation, correct prompts/conditioning instead.
Do not redesign an approved scene on taste or distort correct geometry to offset
generation drift.

Allow at most one targeted generation retry per failing angle within authorized
spending. Returning to 3D or changing a prompt does not reset that count. Default
mode requires approval for the concrete correction batch unless already covered;
no-confirmation mode preserves the same bounded recovery without another pause.
If the same major failure remains, stop that angle, state the limitation and
deliver successful views. Further attempts require explicit scope/budget.

When color matching is requested or already in scope, perform it only after
geometry/identity acceptance, using the supplied or approved master as a fixed
reference. Preserve original images and dimensions; compare changed patches and
unrelated materials. A grade cannot repair geometry or physically relight a scene.

Deliver requested finished images, clean blockout references, updated camera plan
and short shot descriptions: camera position/direction, subjects, foreground,
focus and observed versus revealed content. Keep the editable scene and cameras;
download scene files only when useful/requested. For multi-location packages use
one flat folder per location, master first, then render/texture pairs per shot,
technical checks afterwards and intermediate attempts separately, unless directed
otherwise. Report material unresolved failures and unverified visual checks.

Historical examples and measured case dimensions are evidence, not universal
rules. This instruction does not bundle the archive's optional Python helpers or
BLEND templates; do not invent resource paths or import catalog IDs for them.
