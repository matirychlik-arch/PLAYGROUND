# /3d-jutsu

---
name: 3d-jutsu
title: Higgsfield 3D Jutsu
description: Build, edit, render and export hosted 3D scenes with the scene_builder_3d tools. Use for 3D scene, room, set, prop layout, camera, lighting or animation work in a 3D Jutsu project.
---

# Higgsfield 3D Jutsu

3D Jutsu is a hosted, revision-controlled 3D scene. You build and edit it by running Python (`bpy`) through the `scene_builder_3d_*` tools; nothing is installed on the user's computer. Talk to the user about their scene, project, render and export, not about containers or the runner.

If no `scene_builder_3d_*` tools are available on this connector, say that hosted 3D Jutsu is not available here. `/scene-builder` is a different workflow for the user's own local Blender; offer it only as an alternative, never silently. To turn one image into a standalone 3D mesh, use image-to-3D generation instead of a scene.

## Reconstruct a location from an image

For new views of the same supplied location, load
`/3d-jutsu/references/location-new-angles` with `get_preset_instructions` before
construction or appearance generation. It owns source-camera calibration, hidden
layout, shot acceptance, generation approval and bounded corrections. Image critique
alone does not authorize scene work. Keep the scene workflow below for other 3D tasks.

## Choose the project

Every project-scoped tool takes an explicit `projectId`; no call sets an active project.

- An existing scene: `scene_builder_3d_list_projects`, match the user's named project, and ask when the match is ambiguous.
- A new scene: `scene_builder_3d_create_project` once. If its response is uncertain, list projects before retrying; another create can make a duplicate.
- An authorized project with `exists: false` is a valid empty scene at revision 0, not an error.

## The loop

Two numbers guard every write: `revision` (the committed version) and `sceneSequence` (the settled scene state your code was written against).

1. `scene_builder_3d_get_project` for the current revision, scene sequence and any active operation.
2. `scene_builder_3d_query_python` to inspect names, dimensions, transforms, materials, cameras, lights and RNA before editing. Queries commit nothing; use them freely. Never guess a name, unit or API.
3. Pick a stable, descriptive `operationId` such as `add-key-light-01`. It is an idempotency key: reuse it only to retry the identical code against identical guards.
4. `scene_builder_3d_run_python` with the query's `revisionBefore` as `revision` and `sceneSequenceAfter` as `expectedSceneSequence`.
5. One mutation at a time per project, imports included. If an operation is still active, poll `scene_builder_3d_get_operation` with the same IDs. Only `succeeded`, `failed`, `timed_out` and `expired` are terminal.
6. On success, `revisionAfter` is the new head.
7. On a stale-state conflict, do not replay the code. Re-query, work out what changed, and regenerate the edit with fresh guards and a new operation ID.

Read the operation's `error.code`, `error.retryable` and any `error.retryAdvice` before retrying:

- Python exception: read the message and `output.stderrTail`, fix the code.
- `EXECUTION_TIMEOUT`: nothing was committed. Retry only with cheaper or split work.
- `CONTAINER_UNAVAILABLE` or another retryable transient error: the runtime was not free and nothing was committed. Resubmit the same code under a new operation ID against the same unchanged guards; do not rewrite working code or report it as a scene failure.

## The runtime

- `bpy` API 5.2, headless. `scene.render.engine` accepts only `BLENDER_EEVEE`, `BLENDER_WORKBENCH` and `CYCLES`; there is no `BLENDER_EEVEE_NEXT`.
- Removed APIs that raise: `SceneEEVEE.use_bloom`, `Mesh.use_auto_smooth` (use `shade_smooth()` or a Smooth by Angle modifier), `RenderSettings.tile_x`/`tile_y`, pre-AgX looks. `view_settings.look` takes values such as `'AgX - High Contrast'`. When unsure, query the RNA enum or `dir()` the struct first.
- Execution has a service-configured deadline (currently about five minutes per operation) and code is capped at 256 KiB. Renders are the expensive part: keep resolution and samples small and split large builds into coherent mutations.
- The runtime has no network access. Do not fetch URLs, read files from elsewhere, or embed model or image bytes in Python.
- Each operation starts from the settled scene, not from your previous operation's selection. Look objects up by name, such as `bpy.data.objects["HERO_robot"]`.
- Assign a concise JSON-serializable value to `result`: the names, counts and dimensions you need next, not a dump of scene state.

## Publish renders

`artifacts` is the only way a file leaves an operation:

```python
target = artifacts.file(name="preview.png", media_type="image/png")
scene.render.filepath = str(target.path)
scene.render.image_settings.media_type = "IMAGE"  # set before file_format
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
target.publish()  # unpublished files are discarded
```

At most eight `image/png`, `image/jpeg` or `video/mp4` files per operation. Names are 1-64 characters of letters, digits, `.`, `_` or `-`, starting with a letter or digit. A mismatched media type, missing file or oversize file fails the whole operation. For video set `media_type = "VIDEO"`, then `file_format = "FFMPEG"`, `ffmpeg.format = "MPEG4"`, `ffmpeg.codec = "H264"`.

Retrieve published files with `scene_builder_3d_get_artifact`, passing the operation ID for a query artifact or the revision for a committed one. Inspect the image with this client's image capability. If you cannot view it, say which visual checks remain unverified.

## Bring in models

Models enter only through `scene_builder_3d_search_assets` then `scene_builder_3d_import_asset`, copying the search result's `importArguments` (including `catalogSearch`). This version imports curated catalog assets only; it cannot import a user's own file. Each import is one tracked object. Adjust it afterwards with a mutation rather than importing again. If `settled` is false, poll `scene_builder_3d_get_project` until `appliedSceneSequence` reaches `targetSceneSequence`. If an import fails, report it; never fall back to Python downloads or base64.

## Build a scene, not a script

A scene is an editable visual system at metre scale, judged from its delivery camera. For anything beyond one object, decide the deliverable, the hero, midground and background roles and their fidelity, the camera, and the light motivation before building. Name objects by role (`HERO_robot`, `ENV_floor`, `CAM_main`, `LGT_key`) and keep semantic parts, modifiers and materials editable.

The first blockout mutation places the delivery camera and a working light rig: modest world ambient, one motivated key (`LGT_key`), one soft fill. Use Sun, Spot or Point lights: the scene view and GLB export drop Area lights. Then work coarse to fine and do not polish past a failed gate: silhouette, proportion (verify dimensions with a query), depth, contact (nothing floats or interpenetrates), camera read (a small low-sample `BLENDER_EEVEE` render from the delivery camera), detail. `BLENDER_WORKBENCH` ignores scene lights, so it proves form only.

A succeeded mutation proves the code ran, not that the scene is right. Render from the delivery camera, retrieve the artifact, look at it, fix the largest visible defect and re-render before calling the work done.

Load the reference the task calls for before that stage:

- `/3d-jutsu/references/scene-building` before any multi-object or whole-scene build.
- `/3d-jutsu/references/composition-modeling` before detailed geometry, hard-surface work or GLB export.
- `/3d-jutsu/references/lookdev-lighting` before materials, textures or lighting beyond the working rig.
- `/3d-jutsu/references/animation-audit` before keyframes, camera motion, loops or turntables.

## Deliver

- Files: `scene_builder_3d_get_glb` for a portable model and `scene_builder_3d_get_blend` for the editable source, only when the user wants them. Procedural shaders and world lighting do not reliably carry into GLB.
- AI image or video from a render: `scene_builder_3d_generate_angles` (image) and `scene_builder_3d_generate_video` (Seedance 2.5 video with the render as its start frame) spend credits and leave the scene unchanged. Use them only when the user asks for an AI image or video from the scene, with an inspected PNG/JPEG render's `operationId` and `artifactId`, then poll `scene_builder_3d_get_generation`. On an uncertain response, reuse the same `requestId` and arguments; never allocate a new one just to retry.
- At each completed scene review or delivery, call `scene_builder_3d_show_scene` once with the exact final `revisionAfter` (or settled `revision` after import), after settlement and visual verification. Do not repeat an unchanged revision. This ends that phase's scene inspection/edit calls; authorized generation and status calls may follow. Later feedback or a verified mismatch may reopen editing; verify and show the corrected revision at its next review boundary. If widgets are unavailable, give the returned `projectUrl`.


## Available references

Read a reference only when needed by calling get_preset_instructions with the exact preset argument below.
- {"preset":"/3d-jutsu/references/animation-audit"}
- {"preset":"/3d-jutsu/references/composition-modeling"}
- {"preset":"/3d-jutsu/references/location-new-angles"}
- {"preset":"/3d-jutsu/references/lookdev-lighting"}
- {"preset":"/3d-jutsu/references/scene-building"}
