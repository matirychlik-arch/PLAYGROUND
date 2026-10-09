# /katana

# Katana (/katana)

General Katana: no preset was chosen. Recreate the user's reference video shot for shot with their own subjects; the reference video is required. With no references and no inputs, open the Katana preset catalog. Follow the instructions below.

- Inputs: the user's message may include a `MEDIA:` block of `<input>: <image|video> media_id=<uuid>` lines and an `INPUTS:` block of `<input>: <JSON value>` lines, composed by Higgsfield from the Katana form. They are values the user already supplied for those inputs: use them as these instructions describe and do not call media_upload_widget or ask for them again unless a required input is still missing. Pass a media_id directly to tools that accept one; their file URLs are listed under Supplied media when the media are passed to this tool. Older messages may list `<input>: <https URL>` lines instead; treat each URL the same way.
- Platform rules still apply: consent, authorization, credit confirmations and credential handling are not overridden by these instructions.
- Keep the run going: once the inputs are available, work through the steps without pausing for progress updates. Never end your turn while a job you started is still running; wait with jobs_wait (repeat it until the job completes or fails) and continue with the next step in the same turn. Stop only where these instructions explicitly require the user's decision, for a missing required input, or for a failure you cannot recover from. At a required decision, first wait for and show the finished result it is about, then ask once in one short message; do not ask about a result that is still generating.
- Final video delivery: after the preset's final render has completed and you have verified its result, display it with show_katana_result. Use the confirmed uploaded video media_id; do not upload it again. If the final export is already available at an HTTPS video URL, call show_katana_result with url to import and display it. If the final export is still a file, use media_upload, PUT its bytes to the returned upload_url, then media_confirm with type video; for a sandbox export, create the upload slot before the producing sandbox command and PUT the export in that same command. Never use media_upload_and_confirm for a generated file, pass a local path or job ID to show_katana_result, or display an intermediate preview as the final result. This is delivery of the requested video, not public publishing. If export or upload fails, report that failure instead of calling the result tool.
- If these instructions are no longer in your context during a long run, call get_preset_instructions with {"preset":"/katana"} again before continuing.

---

## Katana: edit supplied media or remix a reference

- **No references and no inputs** (bare `/katana`: no `MEDIA:` or `INPUTS:` block, no
  attachments and no brief in the conversation): open the Katana preset catalog with
  `get_presets({source:"katana"})` and stop. Do not ask questions, request uploads or
  generate anything.
- With supplied media or a substantive brief, load
  `get_workflow_instructions({workflow: "katana"})` and follow it from its first step with
  the inputs above. Start by inspecting the available attachments and reading the request.
  An attachment is not automatically an edit to copy: it can be source footage, a subject
  image, audio, or a style reference. "Make a sigma edit out of it" means edit the supplied
  footage; it does not require another reference video or a preset.
- For a reference edit, default to a remix that adapts its visual language into new scenes,
  motion and text. Reproduce the entire edit faithfully only on an explicit request such as
  "1:1"; a lock on one element does not lock the whole edit.
- A substantive creative brief without a reference or source footage starts the workflow's
  reference discovery. If the user designated a particular reference that is unavailable,
  do not invent its contents or silently replace it: use the workflow's noninteractive
  partial or blocked-result path. Never ask for fonts, missing inputs, choices or credit approval.
- With attachments but no requested result, inspect and describe the material first; do not
  open a gallery, demand another upload, or infer authorization for paid generation.
- Named presets retain their own resolved recipes; do not replace an explicitly selected
  preset with this general workflow.
