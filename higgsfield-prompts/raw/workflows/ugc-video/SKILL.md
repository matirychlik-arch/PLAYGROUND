---
name: ugc-video
description: >-
  Produce a finished UGC video: creator review or productless creator story,
  product-only off-screen voiceover, creator-led unboxing, wearable try-on,
  step-by-step tutorial, or creator-led website tour using real screenshots.
  Select one format from the requested deliverable; a product URL alone does
  not imply a website tour. Missing assets or duration are intake gaps only
  after a production request. Exclude scripts, text-only plans, generic ads,
  still images, footage edits, testimonials and impersonation. Silent product-only
  commercials use ordinary generation, not the voiceover product format.
---

# UGC video

One shared execution pipeline, six format profiles. Select exactly one profile
from the user's intent; review is the default for an otherwise unspecified UGC
video. A long video is one stitched deliverable, not an implicit series.

| Format   | Requested result                                                                                          | Read                                       |
| -------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| review   | One consenting/generated adult creator demonstrates a product or tells a supplied story; product optional | [Review](references/formats/review.md)     |
| product  | Product is the hero, off-screen native voiceover; no on-camera speaker                                    | [Product](references/formats/product.md)   |
| unboxing | Visible creator opens packaging and reacts                                                                | [Unboxing](references/formats/unboxing.md) |
| try-on   | Creator wears an item and demonstrates fit/texture                                                        | [Try-on](references/formats/try-on.md)     |
| tutorial | Creator demonstrates actual use with Step N labels                                                        | [Tutorial](references/formats/tutorial.md) |
| website  | Real captured website/app/page appears with a presenter                                                   | [Website](references/formats/website.md)   |

A product URL identifies the product unless its page itself must appear. Do not
change formats because a URL was supplied. Read only the selected profile and
its prompt references. Format is workflow state, never an invented tool argument.

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
- Workflow scripts are preinstalled at `${HF_WORKFLOWS}/ugc-video/scripts/` inside
  the sandbox. Run them from there. Load detailed workflow references with
  `get_workflow_bundle_file` only when the phase names them.
- Use `generate_image_batch` and `generate_video_batch` for headless workflow
  stages. Each request is `{index, params}`, `params.count` is `1`, and one call
  contains at most twelve requests. Keep stable indices across retries.
- Wait on returned `{index, job_id}` pairs with `jobs_wait` in groups of at most
  twelve and `timeout_seconds:15`. If `all_terminal:false`, wait the returned
  `poll_after_seconds` and poll only active or retryable lookup-failed jobs.
  Freeze completed indices. Never poll jobs through a legacy singleton status
  tool.
- Never pass a batch `submission_failed` entry without a `job_id` to
  `jobs_wait`. Retry only rejected or failed indices, never the whole stage.
- `unlim_choice` means no job was submitted. Ask its message and resubmit the
  unchanged request with the user's `use_unlim` choice; never choose for them.
- Do not substitute a different model when a locked model is unavailable.
  Report the incompatible slug and stop that phase.

## Shared execution — before generation

1. Resolve format-specific intake and safety gates before spending. Reuse supplied
   creator/product assets. Review supports productless requests: never invent a
   product or demand one. Product-only skips creator generation. Website uses
   real captures and no boards; retain its caption-style and capture-failure gates.
2. Run [duration planning](references/duration.md); use its exact clip durations.
3. Read the selected profile's actual prompt references before writing prompts.
   Preserve user-authored beats, authorized identity, real product labels and
   geometry. Approved claims are an allowlist, not inspiration for stronger claims.
   Never fabricate personal use, endorsements, results, measurements or reviews.
4. Physical formats follow [board execution](references/boards.md): GPT Image 2
   → Seedream 5 Pro → visual inspection → Seedance 2.5. Cleanup is mandatory;
   inspection alone is not cleanup. Keep raw and cleaned IDs/URLs separately.
   Only the completed inspected cleaned result may seed another board or video.
   Stop dependent generation if cleanup fails; never fall back to the raw board.
5. Compile every clip prompt before submission. Use the selected format's ordered
   reference roles, native audio, `seedance_2_5`, `mode:"omni_reference"`, and
   `generate_audio:true`. Do not add a separate narration/TTS job. Follow batch
   and upload limits in the runtime contract above, not another host's schema.
6. Inspect completed clips for identity/product continuity, actual duration,
   framing, speech and intended text. Tutorial Step N labels are required;
   other generated text is forbidden. Correct only identified failed clips.
7. For assembly and requested captions load video-montage directly, passing ordered
   accepted clip URLs, authored words, language, look and any website hook/card
   clearance. Physical captions/post package are opt-in; website retains its
   upfront selection. Caption scripts belong exclusively to video-montage.

## Failures and delivery

A timeout or unknown outcome is not a failed submission: poll existing IDs first.
Never resubmit a whole batch because one index failed. An explicit technical
failure may be retried once within authorized spending; a bare failed status with
no reason remains unknown. Moderation stops the dependent path; do not switch
providers, regenerate identities, remove references or use text-to-video to bypass it.
Never replace a locked model silently. Retain successful artifacts for recovery.
Return the confirmed finished video and requested chat-only post package. Check
actual output metadata and encoded frames; job completion alone is not quality proof.


---

## Bundled scripts

This bundle's scripts are ALREADY PRESENT in every sandbox, at
`/home/user/.higgsfield/workflows/ugc-video/scripts/`. Run them there with `sandbox_exec`:

```
python3 "$HF_WORKFLOWS/ugc-video/scripts/<script>"
```

`$HF_WORKFLOWS` is set inside the sandbox — pass it through
verbatim rather than substituting it. Never read a script's contents into the
conversation, and never write one into the sandbox yourself. Any bare
`scripts/...` path in these instructions means
`$HF_WORKFLOWS/ugc-video/scripts/...`.

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
