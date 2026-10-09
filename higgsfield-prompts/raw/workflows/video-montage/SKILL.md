---
name: video-montage
description: >-
  Assemble existing clips into a finished video, add or change a soundtrack, or burn/restyle speech captions. Owns all subtitle transcription, authored-word alignment, placement, burning and final caption checks. Use for a requested rendered video; exclude text-only subtitle translation/correction, transcription, SRT/VTT delivery, analysis, native Higgsedit project authoring and generative edits.
---

# Video montage

Own the finished-file edit and all caption production. Preserve the original clean
master. Re-evaluate each follow-up: a request to translate words is a text task,
not another render. Missing video is an intake gap only for a requested video edit.
Native editable Higgsedit projects and motion graphics use video-editing and
motion-craft; do not turn an ordinary assembly into a native composition.

## Runtime contract

- Use only tools exposed by the current full MCP host.
- Use native client elicitation when it is available; otherwise ask one concise
  normal-chat question. Never invent an elicitation tool name.
- For a local user attachment in an Apps UI-capable client, call
  `media_upload_widget`. When the client can provide bytes directly, use
  `media_upload`, PUT the bytes to its `upload_url`, then call `media_confirm`.
  Keep the returned `media_id`.
- Import an authorized HTTPS image URL with `media_import_url` before generation
  and reuse the returned `media_id`; full-profile generation inputs never receive
  raw URLs.
- Run ffmpeg, Python, downloads, probes, transcription, assembly, and uploads
  only through `sandbox_exec`, never a client-local shell.
- For a sandbox-created output, call `media_upload` before the producing
  `sandbox_exec`, PUT the file to its `upload_url` in that same sandbox command,
  and call `media_confirm` only after HTTP 200. Never pass a sandbox path to
  any attachment-only helper.
- Workflow scripts are preinstalled at `${HF_WORKFLOWS}/video-montage/scripts/` inside
  the sandbox. Run them from there. Load detailed workflow references with
  `get_workflow_bundle_file` only when the phase names them.

## Select the requested edit

- Standalone speech captions or Faceless clean masters: read [subtitles](references/subtitles.md).
- UGC optional hook/captions: read [UGC captions](references/ugc-captions.md).
- Website UGC screenshot composite: read [website captions](references/website-captions.md).
- For standalone and UGC captions also read [caption clearance](references/caption-clearance.md).
  Its measured placement and final-frame inspection override fixed-size examples.
  Faceless preserves its supplied fixed-bottom style and orientation-aware sizing.

The calling workflow supplies the finished master, authored script, language,
requested look and any per-block voice files/assembler sidecar. Do not re-ask
resolved choices. Caption an already assembled master without rearranging clips
or remixing its audio. Transcribe actual audio, verify authored wording, burn,
then inspect the encoded result. A transcript is not proof of a correct burn.

## Assembly and soundtrack

Probe each source with ffprobe. Preserve the requested ordering, source resolution,
aspect ratio and timing. Default to hard cuts; do not add transitions unasked.
For matching codecs, dimensions, fps and audio layouts, use an explicit ordered
concat manifest and ffmpeg concat demuxer with stream copy. If inputs differ,
normalize only what the requested output needs before concatenation; retain audio
sync and inspect cut boundaries. Never claim successful assembly from a command
exit alone: verify duration, streams, first/last frames and every join.

For a requested music change preserve speech, mix/duck to keep it intelligible,
and trim music to the measured edit. Do not add music when it was not requested.
Perform requested captions after the clean edit is complete. Reserve output upload
slots before the producing sandbox command, upload there, then confirm successful
outputs. Return one confirmed finished video and disclose any unverified stage.


---

## Bundled scripts

This bundle's scripts are ALREADY PRESENT in every sandbox, at
`/home/user/.higgsfield/workflows/video-montage/scripts/`. Run them there with `sandbox_exec`:

```
python3 "$HF_WORKFLOWS/video-montage/scripts/<script>"
```

`$HF_WORKFLOWS` is set inside the sandbox — pass it through
verbatim rather than substituting it. Never read a script's contents into the
conversation, and never write one into the sandbox yourself. Any bare
`scripts/...` path in these instructions means
`$HF_WORKFLOWS/video-montage/scripts/...`.

The directory ships with the sandbox image, so it survives `restart: true`. Write
your own outputs to the working directory, not next to the scripts.

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
