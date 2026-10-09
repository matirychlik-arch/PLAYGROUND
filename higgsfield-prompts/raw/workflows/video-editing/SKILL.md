---
name: video-editing
version: 1.0
description: |
  Edit supplied footage or author file-backed motion graphics with Higgsedit.
  Activate only for a requested edit or graphics deliverable: cuts, trims,
  soundtrack changes, native layouts, animated text, shaders, overlays or title
  cards. Do not activate when the user only asks to analyze, summarize, describe,
  critique or review a video or YouTube link. Exclude footage generation,
  generative restyling, transcription, subtitle translation/review and ordinary
  speech-caption burning.
---

# Video editing

Higgsedit runs natively in Node. A project contains `project.json`, imported
`media/`, and `renders/`. This workflow targets native CLI v0.14.0 only. Use the
installed `higgsedit --help` and `types/fable.d.ts` as the command and field
authority. The pinned release is `f39e3bc5882b` in `/opt/fable/VERSION.json`.
If that identity differs or help lacks a required flag, report the runtime
mismatch; do not install, substitute, or omit options.

## MCP runtime and delivery

The dev sandbox alias is `mcp-sandbox-dev`. CLI support in that alias does not
provide browser visual-editor sync or publishing parity. Rebuilding its template
does not deploy these instructions: workflow text is server-owned.

`sandbox_exec` is ephemeral. Before rendering, call `media_upload` to reserve the
output and obtain its presigned upload URL. Put input download, project creation,
render, verification, and `curl -f -X PUT --upload-file ...` in the same `sandbox_exec` call.
Call `media_confirm` only after the PUT returns HTTP 200.
Never pass a sandbox path to an attachment upload tool. Deliver the confirmed URL;
there is no MCP tool that publishes an editable project or hosted editor link.

## Capabilities

| Area     | Features                                                                                                   |
| -------- | ---------------------------------------------------------------------------------------------------------- |
| Media    | Import images/video/audio; source trims, cuts, fitting and audio mixing                                    |
| Layout   | Persistent frames: column, row, equal-column grid, absolute; fill/hug sizing                               |
| Graphics | Text, shaped fonts, rectangles, gradients, paths, Lucide icons, masks and mattes                           |
| Motion   | Raw keyframes, frame choreography, shared counters, token text, transitions, 2.5D camera                   |
| Effects  | Standard filters, shadows, motion blur, custom GLSL, image textures, animated uniforms                     |
| Output   | Native PNGs, contact sheets, MP4/MOV/MKV, H.264, H.265/HEVC Main10, AV1, target bitrate, editable projects |

## Script API

Scripts accept JSX/TSX or supplied node builders; no React, DOM, or HTML scenes.

| Call                                                                              | Result                      |
| --------------------------------------------------------------------------------- | --------------------------- |
| `await project({dir, size, fps, background})`                                     | Create/open project         |
| `await p.add(file)`                                                               | Import asset; return handle |
| `p.cut(handle, {from, dur, at, fit})`                                             | Place footage/audio         |
| `p.compose(nodes, {at, dur, name, camera})`                                       | Place native graphics/media |
| `p.duration()` / `await p.read()`                                                 | Timeline length / document  |
| `await p.frame(time, out)`                                                        | PNG                         |
| `await p.render(out, {draft, depth, codec, bitrate, accel, shards, concurrency})` | Encoded movie               |

`from` is source seconds; composition `at` is timeline seconds. Frame children
and animations use local seconds. `cut` and `compose` record work synchronously.

```jsx
export default async ({ project }) => {
  const p = await project({ size: "640x360", fps: 24 });
  p.compose(
    <frame width={640} height={360} padding={40}>
      <rect
        width={400}
        height={80}
        fill="#32acff"
        animate={[{ property: "scaleX", from: 0, to: 1, duration: 0.6 }]}
      />
    </frame>,
    { dur: 2 }
  );
  await p.frame(1, "renders/frame.png");
  await p.render("renders/video.mp4");
};
```

## Commands

```bash
higgsedit build edit.jsx
higgsedit inspect PROJECT --id CLIP_ID --at 1.2
higgsedit frame PROJECT 1.2 --out renders/frame.png
higgsedit sheet PROJECT --times 0.1,1,1.8
higgsedit render PROJECT --depth 10 --codec hevc --bitrate 8M --out renders/master.mp4
higgsedit do PROJECT VERB --help
```

`inspect --at` requires an ID or unambiguous name and reports evaluated parameters,
not execution proof. `doctor` checks native dependencies; `check` validates
supported inputs. `fonts list`, `fonts add` and `icons QUERY` expose asset catalogs.

## Boundaries

- Whole-script builds replace the timeline. Existing or shared edits require fresh
  inspection and bounded `do`/`ops`; canonical connections require host credentials.
- Native HEVC Main10 import needs no compatibility transcode. Ten-bit output can
  report eight-bit compositor fallbacks; GLSL pixels are RGBA8.
- HTML scenes, runtime animation callbacks, native LUTs, and shader adjustment nodes
  are unsupported.
- Browser shader previews are not universally equivalent to native output.
- MCP does not provide hosted editor publishing or sync credentials; CLI sync
  commands require an explicitly supplied connection.

## References

- API: [composition](references/compose.md), [geometry](references/clip-geometry.md),
  [timing](references/animation-contract.md), [motion](references/motion-language.md).
- Text: [captions](references/caption-titling.md), [caption layers](references/caption-systems.md),
  [titles](references/title-animation.md).
- Projects: [assembly](references/assembly.md), [patch/sync](references/workflows.md),
  [inspection](references/editor-measured.md), [asset identity](references/provenance.md).
- Reference: [composition patterns](references/shot-blueprints.md), [limits](references/failure-modes.md).


---

## Unlimited generations (`use_unlim`) — applies to every workflow

Free-trial **unlim** makes `generate_image` / `generate_video` / `generate_audio` calls free.
It is **opt-in and the user's call**: pass `use_unlim: true` only when they explicitly ask to
spend their unlimited / free-trial generations. Never add it on your own initiative to save them
credits, and never quietly drop it once they have asked.

When they ask, **send the flag — do not pre-gate on anything.** Neither `unlim.available` nor a
model's `supports_unlim` is a precondition: a request that cannot be served free comes back as a
typed rejection, never as a silent charge, so the backend is the authority and dropping the flag
"to be safe" is what actually bills the user.

What the models tools give you is not a gate but the values to stay inside — one call per model this
run actually uses:

```
models_explore  action: "get"  model_id: "<model this workflow locks>"
```

- the **`Unlim configs`** text at the end of the response — the configurations the grant actually
  covers, one row per covered configuration, keyed by the backend's `job_set_type` (usually but not
  always the model id — match it yourself). A request is free if it satisfies **any one** row of its
  model; a parameter absent from a row has no cap; `max_duration` is a bound in seconds. No rows for
  a model is not a denial — send the flag and let the rejection, if any, tell you why.
- `supports_unlim` and the top-level `unlim` block are context for what you tell the user, not a
  reason to withhold the flag.

Then add `use_unlim: true` to every generate call of the run, staying inside the covered values.
**If this workflow's locked parameters fall outside them** — a resolution the rows don't list, a
duration above `max_duration` — stop and ask: run the covered value, or keep the workflow's value
and pay credits. Never silently downgrade the output, and never silently charge. Swapping models is
not a fix: a workflow's locked models stay locked.

Anything that is not one of the three generate_* tools takes no `use_unlim` — assembly, upscales,
transcription/subtitles and similar are billed as usual, unlim run or not.

Rejections — never retry the same call; each has its own fix:

- `unlim_trial_available` → eligible but the trial is not started. The error carries
  `recovery_tool: show_plans_and_credits` — call it immediately, then wait for the user.
- `unlim_trial_expired` / `unlim_not_eligible` → the allowance is gone. Stop and ask before
  continuing on credits; this can land mid-run, so do not finish the remaining jobs unasked.
- `unlim_not_supported` → that model has no unlim path at all; no plan or trial change fixes it.
- `unlim_config_not_covered` → the model is covered, these parameters are not. Re-read the
  `Unlim configs` rows and retry inside them.

Retries and re-submitted jobs carry the same flag as their original submission.
