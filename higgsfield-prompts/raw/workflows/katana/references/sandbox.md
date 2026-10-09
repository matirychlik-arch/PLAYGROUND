# Sandbox mechanics (katana)

All compute for this workflow runs in the Higgsfield sandbox through `sandbox_exec`: ffmpeg,
Python and headless Chromium. Never use the user's machine, local Bash or local ffmpeg. A
`sandbox_exec` call costs 0 credits. This page covers how the skill lives inside the sandbox:
bootstrap, workspace, state, background jobs, viewing images, and moving media in and out.
Read `references/mcp-api.md` and verify actual available tool schemas. Read other Markdown references with `get_workflow_bundle_file({workflow: "katana", path: "references/<file>.md"})`; reference files need not reside in the remote sandbox. Reference research and supported viewing/listening may use available browser/search/media tools; video/audio processing remains in the sandbox. Read [creative-quality.md](creative-quality.md) for autonomous discovery, reference roles and the three motion reviews.

The sandbox is an assembly and measurement environment, not a local face-edit route. Do not install or invoke face-swap libraries, landmark/mesh warps, head pastes, facial inpainting, manual facial-feature drawing or skin/hair retouching. Detection and tracking may output coordinates; camera alignment transforms the whole plate, and masks composite the complete generated subject. Identity/face corrections require supported authorized model output. Background cleanup requires a full aligned exclusion mask for every visible person, including extras and head/hair silhouettes. Generic pixel-edit utilities and project hooks do not override this boundary.

## 1. Facts that shape everything

| Fact                                                                                                                                                                                                                                                | Consequence                                                                                                                                                                                                                                                                                                                                                                                                         |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Files are discarded ~10 s after a call finishes. Back-to-back calls see the same files.                                                                                                                                                             | Chain work with `&&` in one command. End a stage with `rr_save`, or start the next call immediately. Always save before you hand the turn back to the user.                                                                                                                                                                                                                                                         |
| Foreground timeout is 60 s by default and 120 s max (`timeout_seconds`). But the MCP connector itself gives up sooner: a foreground call that waited ~100 s (`rr_wait <log> 100`) failed with "server isn't responding" (VERIFIED live 2026-10-08). | Keep every foreground call under **~45 s** of work or waiting, with `timeout_seconds` about twice its expected time (≤ 120). Anything that could run longer goes to `background: true`, polled with short calls (`rr_wait <log> 25`).                                                                                                                                                                               |
| `background: true` returns at once with `pid`, `log_path` and `status_path`, and gets a **15-minute lease**. Poll calls do not shorten the lease.                                                                                                   | Renders, matting and long decodes run in the background. Poll every 20–30 s with short calls. Split anything over ~14 min into parts with an `rr_save` between them.                                                                                                                                                                                                                                                |
| `rr_ws`, `rr_restore` and `rr_load` set `$W` and `cd` in the calling shell.                                                                                                                                                                         | **Never pipe them** (`rr_restore … \| tail`): a pipe runs the function in a subshell, so `$W` and the `cd` are lost and every later step of the command runs without a workspace (VERIFIED live 2026-10-08). Chain with `&&` and let them print (`rr_restore` also lists the frame folders still to rebuild, section 9); to quieten one, redirect instead of piping: `rr_restore <slug> '<STATE_URL>' > /dev/null`. |
| There is **one sandbox per account**, shared by every chat of that user (8 vCPU, ~7 GB RAM, ~21 GB disk). A foreground call that hits its timeout, or a `restart: true`, wipes it for everyone, including other chats' background jobs.             | Use a unique slug, run one heavy job at a time, and keep polls under 10 s. Never use `restart: true` mid-project (section 10).                                                                                                                                                                                                                                                                                      |
| `image_paths`: at most 4 PNG/JPEG files, ≤ 512 KiB in total, on a **foreground** command that exits 0.                                                                                                                                              | This is how Claude looks at frames and sheets. rrio sheets are sized for it (section 6).                                                                                                                                                                                                                                                                                                                            |
| The command string is at most 16,000 characters.                                                                                                                                                                                                    | Put the logic in `$RR/*.py` scripts. A command should be the bootstrap plus a few script calls.                                                                                                                                                                                                                                                                                                                     |
| The sandbox runs Debian with Python 3.11, numpy, Pillow, faster_whisper, onnxruntime, ffmpeg 5.1, ImageMagick, sox, jq, node 20 and Playwright Chromium. It has **no** cv2, scipy, librosa, soundfile, torch, vidstab, `bc` or `/usr/bin/time`.     | Use stdlib + numpy + ffmpeg only, and do arithmetic in Python or `$((…))`. Verify the current runtime; dependency installs use the Socket firewall and the deployment lock (§11), never a public package registry.                                                                                                                                                                                                  |

## 2. Bootstrap: the first line of every command

katana runs through the Higgsfield MCP server as a bundled workflow. The server preinstalls
`scripts/` in every sandbox at `$HF_WORKFLOWS/katana/scripts/` (`$HF_WORKFLOWS` is
`/home/user/.higgsfield/workflows`), and the copy survives `restart`. Every `sandbox_exec` command
therefore starts with:

```bash
source "$HF_WORKFLOWS/katana/scripts/rr.sh"
```

Below, `<BOOT>` stands for this line. Scripts run as `python3 $RR/<script>.py`. Never paste a script
into a command and never rebuild one from the chat. If the `source` fails with "No such file or
directory", the workflow is not deployed on this server yet: use the pre-deploy fallback in §2.1
(SKILL.md, "Environment"). If no deployed bundle or accessible attached bundle URL exists, state that capability limitation
without a question; do not request an upload or invent a bundle URL. First inspect documented
package/deployment locations and available authorized equivalent processing capabilities. Use a
verified supported fallback when possible; never execute unknown code or invent a helper path.

### 2.1 Pre-deploy fallback (bundle not deployed yet)

Use this only while the bundle is not deployed on the server yet. `RR_BUNDLE_URL` is the permanent URL
of the trusted authored bundle **`.zip`**. The install ZIP has a `katana/` wrapper; the runtime ZIP
has `scripts/` and `references/` at its root. The fallback supports both known layouts. Upload it with `media_upload` as a
general file named `*.zip`: the general-file store refuses `.tgz` (verified live 2026-10-08), and the
snippet unpacks with `unzip`, not `tar`. Once the bundle is deployed, the plain line above is enough.

```bash
RR_BUNDLE_URL='<trusted bundle .zip url>'; source "${HF_WORKFLOWS:-/nonexistent}/katana/scripts/rr.sh" 2>/dev/null || { if [ ! -f /home/user/.rr/katana/scripts/rr.sh ] && [ ! -f /home/user/.rr/scripts/rr.sh ]; then mkdir -p /home/user/.rr && curl -sfL --retry 3 -o /home/user/.rr/b.zip "$RR_BUNDLE_URL" && unzip -q -o /home/user/.rr/b.zip -d /home/user/.rr; fi; if [ -f /home/user/.rr/katana/scripts/rr.sh ]; then source /home/user/.rr/katana/scripts/rr.sh; else source /home/user/.rr/scripts/rr.sh; fi; }
```

The snippet tries three sources in order:

1. **The deployed bundle** at `$HF_WORKFLOWS/katana/scripts`, so it does no harm once the bundle
   is deployed.
2. **A cached bootstrap** at `/home/user/.rr/katana/scripts` or `/home/user/.rr/scripts`, left by an earlier call.
3. **A download** of the `.zip` to `/home/user/.rr/b.zip`, unzipped into `/home/user/.rr`.

To force a fresh copy, for example after the bundle changes mid-session, prefix the snippet with
`rm -rf /home/user/.rr/scripts /home/user/.rr/katana/scripts;`. Only bootstrap a verified workflow
package; this snippet is not a loader for arbitrary uploaded code or archives.

Sourcing `rr.sh` exports these variables:

| Variable     | Value                                                                            |
| ------------ | -------------------------------------------------------------------------------- |
| `RR`         | The scripts directory.                                                           |
| `RR_HOME`    | `/home/user` (falls back to `$HOME` off-sandbox).                                |
| `RR_ROOT`    | `$RR_HOME/rr`, the parent of all workspaces.                                     |
| `RR_PYLIB`   | `$RR_HOME/pylib`, for pip `--target` installs.                                   |
| `RR_CACHE`   | `$RR_HOME/.rr/cache`, for models such as YuNet.                                  |
| `PY`         | `python3`.                                                                       |
| `CHROME`     | A working Chromium or Chrome binary (see `rr_chrome`).                           |
| `PYTHONPATH` | Prefixed with `$RR_PYLIB`; `$RR` is appended so `import rrio` works anywhere.    |
| `PATH`       | Prefixed with `$RR_PYLIB/bin`, so pip-installed CLIs such as `yt-dlp` are found. |

All of these can be overridden by setting them before sourcing, which is how local tests run.

## 3. Workspace layout

`rr_ws <slug>` creates and enters `W=/home/user/rr/<slug>`. Make the slug unique per project,
for example `katana-1008-x7`, because other chats share the sandbox.

| Path                                             | Contents                                                                                                                                                                                                                                                 |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ref/`                                           | `ref.mp4` (the reference as fetched), the probe JSON `ref.json`, `meta.json` for page links.                                                                                                                                                             |
| `analysis/`                                      | `analysis.json`, `breakdown.json`, `frames.json`, `window_mask.png`, `events.txt`, permitted `words.json`, `coverage.json`, `seconds.json`, `references.json` (source/viewing/asset evidence), `motion-reviews.json` (three review passes at each gate). |
| `audio/`                                         | `audio.py` measurement output: `ref.wav`, `ref_orig.<ext>`, `beats.json`, `cutsync.json`, `align.json`; authorized existing music and stock SFX assets with their manifest references. No synthesized music/beat/SFX outputs.                            |
| `cuts/`, `keyframes/`                            | `frames.py export` cut clips (+ `<cut>.json`) and `frames.py keyframes` frames.                                                                                                                                                                          |
| `sheets/`                                        | Contact sheets and QA crops: JPEGs sized for `image_paths`.                                                                                                                                                                                              |
| `plan/`                                          | `gen_plan.json` (the generation plan), `ledger.json` (quoted/charged/used), `renders.json` (`assemble.py`), `prompts/`, `urls.json` (every remote URL: state, generations, uploads).                                                                     |
| `gen/`                                           | Downloaded generation results, as returned; Genjutsu driving pads `<cut>_pad.mp4` + `.json` (`frames.py pad`).                                                                                                                                           |
| `plates/`                                        | Explicitly prepared plates used by the EDL; `render.py prep` frame folders.                                                                                                                                                                              |
| `mattes/`                                        | Matte videos and alpha PNG sequences.                                                                                                                                                                                                                    |
| `faces/`                                         | Face boxes and landmarks JSON, identity crops.                                                                                                                                                                                                           |
| `comp/`                                          | Compositor project: `edl.json`, `fx.js`, assets, and `comp/frames/` (rendered frame dump, not saved).                                                                                                                                                    |
| `out/`                                           | Deliverables: final mp4, side-by-side, triptych.                                                                                                                                                                                                         |
| `qa/`                                            | QA sheets, frame-count and audio reports.                                                                                                                                                                                                                |
| `logs/`                                          | `rr_bg` logs with `<log>.status` and `<log>.pid`.                                                                                                                                                                                                        |
| `.rr_slug`, `.rr_state.json`, `.rr_excluded.txt` | State manifest files, written by `rr_save`.                                                                                                                                                                                                              |

Scripts take `$W` as their first positional argument (after the subcommand, e.g. `frames.py export $W`) and
write only inside it. Never touch another
workspace under `$RR_ROOT`.

## 4. Ephemeral files: the stage pattern

A **stage** is one `sandbox_exec` command:

```bash
<BOOT> && rr_restore <slug> '<STATE_URL>' && python3 $RR/<step>.py $W ... && rr_save '<UPLOAD_URL>' '<CONTENT_TYPE>'
```

- `rr_restore` is a no-op when the workspace is still warm, meaning `.rr_state.json` is present.
  Otherwise it downloads the last saved state. On the very first stage use `rr_ws <slug>` instead.
  Never put `rr_ws` / `rr_restore` / `rr_load` before a `|` (section 1): the workspace is lost.
- States are lean (section 9): after `rr_restore` / `rr_load` prints "REBUILD before rendering", run
  `rr_rebuild` before any render (it re-runs the left-out `render.py prep` lines; a 241-frame plate plus
  its matte took ~9 s in the sandbox, VERIFIED live 2026-10-08). Many clips: inside `rr_bg` with
  `background: true`.
- Calls that follow back-to-back may skip `rr_save`. The next call will see the files.
- **Always** `rr_save` before ending a turn; a later continuation may arrive after the files are gone.
  Do not end a turn to wait for questions, credit confirmation or consent. If unavailable service
  permission prevents work, save completed work and state the blocked/partial result, using an
  authorized fallback when available. Never bypass permissions or enter a user-waiting state.
- Also save right after anything slow to redo: renders, mattes, and many downloads. Generation
  results themselves can always be re-fetched from their URLs, so record those in `plan/urls.json`.
- Each `rr_save` needs a **fresh** upload slot (section 9), because slots are single-use, and the
  `content_type` from that slot's `media_upload` reply as its 2nd argument.

## 5. Background jobs

Run anything that may take longer than ~45 s with `background: true` (section 1: longer foreground
calls can drop the MCP connector). Wrap the work in `rr_bg` so the job's state lives in the workspace:

```bash
# background: true
<BOOT> && rr_restore <slug> '<STATE_URL>' && rr_bg logs/render.log python3 $RR/comp/render.py $W ... && rr_put out/<slug>_v1.mp4 '<UPLOAD_URL_MP4>' && rr_save '<UPLOAD_URL_STATE>' '<STATE_CONTENT_TYPE>'
```

- `rr_bg <log> <cmd...>` behaves like nohup. It sends stdout and stderr to the log, ignores SIGHUP,
  writes `<log>.status` (`state=running`, then `state=done|failed rc= secs=`) and **waits**, so its
  exit code is the command's. A single string argument runs as a bash script:
  `rr_bg logs/x.log "python3 a.py && python3 b.py"`.
- Reserve every upload slot the job needs (deliverable plus state) **before** starting it, and put
  the PUTs at the end of the same command.
- Poll with short foreground calls (`timeout_seconds` about 40) every 20–30 s:
  `<BOOT> && rr_ws <slug> && rr_wait logs/render.log 25`.
  `rr_wait` checks every 3 s for up to 25 s, then prints `STATUS …` and the log tail.
  Use `rr_status logs/render.log 15` for a single look. Never wait longer in one call: a 100 s wait
  dropped the MCP connector (section 1), so `rr_wait` caps at 45 s. Many short polls are safe.
- `rr_status` return codes: `0` done, `1` failed, `3` running, `4` missing (sandbox was reset:
  restore and rerun), `5` died (killed or lease expired).
- `rr_kill logs/render.log` stops the job and all of its children. A plain `kill <pid>` of the
  wrapper orphans the real process. The background reply's own `pid` can also be killed (per the
  tool docs); whether that reaps the children is unverified, so prefer `rr_kill`.
- To look at results (`image_paths`), wait until the job is done, then make a foreground call that
  lists the files.
- Do **not** background things inside a foreground call. `nohup … &` in a foreground call still
  blocks, and `a && b & c` backgrounds the whole `a && b` chain. Use `background: true` instead.
- Run one heavy job at a time. Before starting one, `rr_info` lists workspaces and running
  `rr_bg` jobs, including other chats' jobs on the same sandbox.

## 6. Looking at images (`image_paths`)

- Pass up to 4 PNG/JPEG paths, ≤ 512 KiB **in total**, on a foreground command that succeeds.
  Relative paths start at `/home/user`, so use `rr/<slug>/sheets/x.jpg`.
- `rrio.tile_sheet` / `rrio.video_sheet` / `python3 $RR/rrio.py sheet` write JPEGs ≤ `max_bytes`
  and ≤ 1600 px wide. They lower JPEG quality first, then downscale. Labels use a built-in bitmap
  font, so no system fonts are needed. Budget `max_bytes` by how many images go in one call:

| Images per call | `max_bytes` each      |
| --------------- | --------------------- |
| 1               | 500_000 (the default) |
| 2               | 250_000               |
| 3               | 165_000               |
| 4               | 120_000               |

- Quick looks: `python3 $RR/rrio.py sheet ref/ref.mp4 sheets/ov.jpg --max-tiles 48` gives an
  overview. For a frame range, use `--start 120 --end 180 --every 1`. For single frames, use
  `python3 $RR/rrio.py frame ref/ref.mp4 0,120 sheets/f{f}.jpg --scale-w 720`.
- A full-resolution PNG of a 1080p frame is about 2–3 MB, too big for `image_paths`. Look at
  JPEG crops instead, for example `rrio.write_image(path, crop, 85)`.

### Actual viewing and review evidence

When no reference was supplied, research current relevant TikTok/YouTube Shorts through an available search/browser operation, then actually view the complete eligible clips before choosing one primary. Search responses, metadata, thumbnails and partial previews are discovery evidence only. A supported full-clip viewer or complete inspected frame coverage of the actual media can establish visual inspection; preserve exact viewed ranges and tool/media evidence in `analysis/references.json`. Use a supported listening operation for audible music judgments and record measured-only limitations honestly. Continue to another accessible candidate rather than ask the user for a link. Do not silently replace an inaccessible user-designated reference.

Keep the primary separate from supplemental montage, music and font references. Inspect all three
roles, using the primary when sufficient. In REMIX supplemental evidence informs the authored plan;
in EXACT it fills missing detail without overriding source locks. Follow `analysis.md` for every
decoded source frame and actual presentation second. Preserve the source master and VFR PTS during
analysis. Output timing follows `plan/creative-plan.json` -> `output_target`; equal source/output
timing is mandatory only in EXACT or a scoped user lock. CFR-only helpers reject unsupported VFR
preservation: use a verified PTS-aware route where needed. A separately rendered remix may have a
planned CFR timeline without modifying the source master or claiming source timestamps survived.
Save actual temporal, spatial and detail reviews in `analysis/motion-reviews.json` before generation
and refresh against the composition. No helper or successful render certifies unperformed reviews.

## 7. Getting media in

| Source                                                 | How                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Generation results (Seedance, Genjutsu, images, audio) | `rr_get '<result_url>' gen/<name>.mp4`. CloudFront result URLs are directly readable, with no re-upload.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Reel or page link (Instagram, TikTok, YouTube)         | `fetch_ref.py` uses existing `yt-dlp` when available. Missing packages may be installed only through the pinned, hashed deployment lock and Socket firewall (§11); no automatic bare install is permitted. A direct-media importer cannot ingest HTML pages. Historical downloads do not guarantee current access or dependency availability. The fetch helper preserves downloaded bytes at the legacy `ref/ref.mp4` path; probe the actual container. No automatic crop, HDR conversion, frame normalization or original deletion. Keep any SDR/resized preview separate from that source. |
| Direct HTTPS media URL                                 | `rr_get` it directly. When a confirmed media ID is needed, use a verified supported import operation or reserve a standard media upload and PUT the fetched bytes before confirmation. Do not assume a legacy URL-import tool exists.                                                                                                                                                                                                                                                                                                                                                        |
| Already attached file (photo, footage, reel)           | Use its existing accessible media URL or an available authorized file-upload capability, then `rr_get` the result. Do not open an upload widget or request a file selection. If no transfer capability exists, state the limitation without a question.                                                                                                                                                                                                                                                                                                                                      |
| Required new/replacement music and SFX                 | Select actually inspected authorized TikTok or stock music and stock SFX. Use an existing authorized retrieval operation or actual downloadable asset URL; preserve its source, asset ID, audition evidence and supported use conditions in `analysis/references.json`. Download stock assets only through an available permitted operation. If inaccessible, retain actual source audio where it fits and report the missing change without pretending delivery. Do not synthesize audio in code, scrape full lyrics or invent a download URL.                                              |
| Earlier project state                                  | `rr_restore <slug> '<STATE_URL>'` or `rr_load '<STATE_URL>' [slug]`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |

`rr_get <url> [dest]` downloads with 4 retries, writes atomically (`.part`, then rename), and
returns non-zero on HTTP errors. A trailing `/` or an existing directory as `dest` keeps the URL's
basename.

## 8. Getting media out (deliverables, generation inputs, state)

1. Call **`media_upload` before** the command that produces the file. Its filename extension sets
   the type: image, video or audio become generation inputs; `.tar.gz`, `.tar`, `.zip`, `.json` and
   other whitelisted general files get a permanent URL (`.tgz` is refused). Keep the `upload_url`,
   `media_id` and `content_type`.
2. In the **same** `sandbox_exec` command that produces the file, append
   `rr_put <file> '<upload_url>' [content_type]`. It prints `HTTP <code> …`.
   - `rr_put` sends `If-None-Match: *` and the `Content-Type`; the signature covers both.
     Pass `media_upload`'s `content_type` when it differs from the extension default (`rr_mime`).
     A 403 almost always means a Content-Type mismatch or an expired URL.
   - A slot is **single-use** (FROM-EVIDENCE). `rr_put` refuses missing or empty files so they don't
     burn the slot. A second PUT is refused; the exact code is UNVERIFIED (expect 412,
     `references/mcp-api.md` §2.1 and §14). Request a new slot.
   - On 000, 408, 429 or 5xx, `rr_put` retries 4 times. A 412 right after such a failure is
     reported as "probably uploaded"; `media_confirm` decides.
   - Always single-quote the URL; presigned URLs contain `&`.
3. Call **`media_confirm`** only after `HTTP 200`, with `type` set to `video`, `image`, `audio` or
   `file`. Generation inputs then have a `media_id`; general files get their permanent URL.

Notes:

- **One `media_upload` call per stage.** Reserve every slot the stage's command will PUT to (its
  state archive, Genjutsu driving clips, deliverables, an image to show the user) in ONE
  `media_upload` call with `files[]`. Slots are single-use and every `rr_save` needs a fresh one, so
  a stage without its own state slot cannot save (VERIFIED live 2026-10-08).
- Each `media_upload` reply costs about 4k tokens per file. Reserve only slots you will use in the
  next command, at most 20 per call.
- Upload audio as `.m4a` or `.mp3`. A `.wav` gets typed `audio/mpeg` and stored as `.mp3`.
- A frame that must condition a generation (an identity still, the ref's cut frame) is uploaded
  as an image: `.png`/`.jpg`, typed `image`.

## 9. Project state (`rr_save` / `rr_load`)

The project state is a gzip tarball of `$W`, uploaded as a **general file**, which gives a
permanent URL. One name everywhere: **`<slug>_vN_state.tar.gz`**, where N is the version being
worked on (`v0` before the first render, `v1` while building and delivering v1, and so on).

1. Reserve a slot with `media_upload` for the general file `<slug>_vN_state.tar.gz`. Keep the
   `upload_url` and the `content_type` from the reply.
2. Run `rr_save '<upload_url>' '<content_type>'` and **always pass the reply's content type**. The
   presigned URL signs it, and a different type is rejected with 403. Verified live 2026-10-08: the
   reply's `content_type` for a `.tar.gz`, `.tar` or `.zip` general file is `application/octet-stream`
   (whatever type was requested), which is also `rr_save`'s default without the 2nd argument.
   - It writes the manifest files `.rr_slug`, `.rr_state.json` and `.rr_excluded.txt`.
   - It tars everything except `*/frames_cache/`, `comp/frames*` (every `render.py` dump: the render and
     its `preview/`, `stills/` and `unused/` subfolders), `comp/stills/`, `tmp/`, `__pycache__/`,
     `node_modules/`, `*.part|*.raw|*.y4m|*.yuv`, files larger than `RR_SAVE_MAX_MB` (default 150),
     and any `RR_SAVE_EXCLUDE` patterns (find `-path` patterns relative to `$W`, e.g.
     `RR_SAVE_EXCLUDE='./gen/raw ./plates/*.mov'`). By default it is also **lean**: `ref/src.*` and the
     rebuildable frame folders stay out (below).
   - It then PUTs the tarball with `rr_put`.
   - `.tar.gz` is accepted as a general file (verified live 2026-10-08; stored as `.gz`, and `rr_load`
     unpacks it whatever the stored name). Never name the slot `.tgz`: that extension is refused
     ("Upload URL generation failed"). A full round trip (`rr_save` → HTTP 200 → `media_confirm` →
     `restart: true` → `rr_restore`) was verified the same day.
3. `media_confirm(type='file')` returns the permanent URL. Record it as the **current STATE_URL**
   in the conversation, and in `plan/urls.json` on the next stage.
4. Restore with `rr_restore <slug> '<STATE_URL>'`, which loads only when the workspace is
   cold, or `rr_load '<STATE_URL>' [slug]`, which always unpacks over `$W`. With no slug and no
   `$W`, `rr_load` reads the slug from the tarball. It lists what was excluded so you know what
   to re-fetch or re-render.

Before saving, ensure `analysis/references.json`, `analysis/motion-reviews.json`, frame-coverage logs and selected audio/font source records are included. Keep unavailable-asset and unviewed-candidate states explicit; restoring state does not make them inspected. Every save is a new permanent URL, and older ones stay valid, so rollback is possible. The state
contains the user's photos and footage. Treat the URL as private: keep it in the conversation and the
project files only, never in public posts or prompts.

**Lean by default.** The Katana test run's states were 78–184 MB (VERIFIED live 2026-10-08), almost
all of it rebuildable: `ref/src.*` (the original yt-dlp download kept next to `ref.mp4`) and the
`render.py prep` JPEG / PNG frame folders in `plates/<id>/` and `mattes/<id>/`. `rr_save` now leaves those
out by itself:

- Left out: `ref/src.*`; the images of every `plates/<id>/` and `mattes/<id>/` folder whose `clip.json`
  names a source that is itself in the state (`gen/*.mp4`) and records exact `prep_args`; `cuts/<id>/`
  image dumps. A folder that cannot be rebuilt (no exact prep metadata, source/mask outside `$W`
  or not saved) is kept whole. Legacy metadata without `prep_args` retains its images; re-run
  preparation with the intended settings to make it eligible for a lean save.
- Kept: `ref/ref.mp4`, every `.mp4`, `.json` and `.md` (generations in `gen/`, matte videos,
  `mattes/fit/` from `assemble.py`, all plans).
- `.rr_excluded.txt` lists what was left out, with a `REBUILD:` command per folder. After a cold
  restore, `rr_restore` / `rr_load` print the pending ones; run `rr_rebuild` (or `rr_rebuild --dry` to
  see them) before any render. Rebuild uses the stored source, size, frame range, JPEG quality,
  filter, matte mode/width, threshold and morphology settings. It parses the listed arguments
  and runs only the trusted `render.py prep` helper, never shell code from the state file.
  A 241-frame plate plus its matte rebuilt in ~9 s (VERIFIED live
  2026-10-08).
- `RR_SAVE_FULL=1 rr_save '<upload_url>' '<content_type>'` keeps everything (the old fat archives); only
  for a handoff where the next session must not re-run `render.py prep`.
- Re-fetch excluded generation results only while their actual result URLs remain accessible; a saved URL is not a permanence guarantee. Preserve irreplaceable source/audio/font assets in the state. Rebuild frame dumps from retained source assets.

## 10. Shared-sandbox rules

- Other chats of the same user may be working in `/home/user/rr/*` right now. Use a unique slug.
  Never delete or modify other workspaces, `/home/user/.rr`, or `/home/user/pylib` wholesale.
- **Never `restart: true` mid-project** unless the state is saved and the sandbox is genuinely
  broken (disk full, wedged processes). It also kills every other chat's files and jobs. Check
  `rr_info` first, and tell the user.
- A foreground call that hits its timeout wipes the sandbox for everyone. Size foreground work
  conservatively, and background anything uncertain.
- Run one heavy job (render, matte, full decode at 1080p) at a time per chat. RAM is ~7 GB shared,
  so prefer streaming (`rrio.read_frames`) over `read_all` for long or large videos.
- Keep stdout short. Scripts print summaries, and logs go to files; read them with `rr_status`
  or `tail`.
- Never `pkill -f <pattern>` inside a command: the pattern also matches the command's own
  `bash -c` line, so the call kills itself (exit -1, no output). Stop jobs with `rr_kill <log>`
  or by pid.
- Never run `chrome --dump-dom` (or any browser call that waits for the page) in a foreground
  call without `timeout 20`: with `--headless=new` it can hang until the call times out.
  `render.py` does not use it.

## 11. Python, pip and Chrome

- Scripts: `python3 $RR/<script>.py [<subcommand>] $W …`. They `import rrio` from their own directory.
  `rrio` provides frame-exact readers, image IO, sheets, a bitmap font, numpy filters and JSON
  helpers. Do not use Pillow, cv2 or ImageMagick for labels.
- `rr_pip <pkg…>` reuses already installed packages. A missing package is installed only from
  the deployment-provided `RR_REQUIREMENTS_LOCK`, with exact `==` versions and SHA-256 hashes,
  using `https://socket-firewall.higgsfield.xyz/pypi/simple`. No bare unpinned install or public
  registry fallback is permitted. A missing/invalid lock or Socket rejection means no install;
  use an already available authorized capability or state the dependency limitation without
  asking the user. Never fabricate lock hashes, bypass a block or promise a cold install will work.
- `rr_chrome` (and `$CHROME`) resolves in this order: `$CHROME`, then
  `/ms-playwright/chromium-*/chrome-linux64/chrome`, then the Playwright headless shell, then
  macOS Google Chrome, then `chromium`/`google-chrome` on PATH. Flags that work in the sandbox:
  `--headless=new --no-sandbox --disable-gpu`. There is no FaceDetector API on Linux; `faces.py`
  uses YuNet via onnxruntime. Verified 2026-10-08: the binary is Chrome for Testing 153; a cold
  start that loads a page, draws a blurred Canvas2D frame and POSTs it to a local server takes
  about 5 s.
- Fonts: Montserrat, Metropolis, DejaVu, Liberation, Noto Color Emoji and CJK fonts are installed.
  Montserrat and Metropolis exist **only in the ExtraBold weight**, so every weight requested
  from them renders ExtraBold; load a font file through the EDL `fonts[]` when the look needs
  another weight.
  The test-edit bundle's League Gothic, UnifrakturMaguntia, Cormorant and Inter are at
  `$HF_WORKFLOWS/test-edit/scripts/fonts/`.

## 12. `rr.sh` reference

| Function                        | Does                                                                                                                                                                                                                   | Returns                                                          |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `rr_ws <slug>`                  | mkdir the standard subdirs, `cd`, export `W` (no arg: `cd $W`); never in a pipe (section 1)                                                                                                                            | 2 on a bad slug                                                  |
| `rr_get <url> [dest]`           | curl `-fL` with 4 retries, atomic rename                                                                                                                                                                               | non-zero on failure                                              |
| `rr_put <file> <url> [mime]`    | presigned PUT: Content-Type + `If-None-Match: *`, prints `HTTP <code>`                                                                                                                                                 | 0 only on 200/201/204                                            |
| `rr_save <upload_url> [mime]`   | lean tar.gz of `$W` (section 9: no caches, dumps, `ref/src.*` or rebuildable frame folders; `RR_SAVE_FULL=1` keeps them), then `rr_put`; pass the slot's `content_type` as `mime` (default `application/octet-stream`) | `rr_put`'s code                                                  |
| `rr_load <state_url> [slug]`    | download + untar into `$W`; prints excluded paths                                                                                                                                                                      | non-zero on failure                                              |
| `rr_restore <slug> <state_url>` | `rr_ws` + `rr_load` only when cold; never in a pipe (section 1)                                                                                                                                                        | —                                                                |
| `rr_bg <log> <cmd…>`            | nohup-style run with log + `.status` + `.pid`, waits (`RR_BG_DETACH=1`: return at once, local use only)                                                                                                                | the command's rc                                                 |
| `rr_status <log> [n]`           | `STATUS …` line + last n log lines                                                                                                                                                                                     | 0 done, 1 failed, 3 running, 4 missing, 5 died                   |
| `rr_wait <log> [secs≤45]`       | poll every 3 s until not running or secs elapse (capped at 45 s: a 100 s wait dropped the MCP connector), then `rr_status`; 20–30 s is the norm                                                                        | as `rr_status`                                                   |
| `rr_rebuild [--dry]`            | run the pending `REBUILD:` lines of `.rr_excluded.txt` (lean state, section 9) from `$W`                                                                                                                               | non-zero if one fails                                            |
| `rr_kill <log>`                 | stop the job's process tree (STOP → TERM → CONT)                                                                                                                                                                       | —                                                                |
| `rr_chrome`                     | print the browser path                                                                                                                                                                                                 | 1 if none                                                        |
| `rr_pip <pkg…>`                 | reuse installed package; otherwise exact pinned/hashed `RR_REQUIREMENTS_LOCK` through Socket only                                                                                                                      | nonzero on missing lock, invalid requirements or blocked install |
| `rr_mime <file>`                | MIME type by extension                                                                                                                                                                                                 | —                                                                |
| `rr_info` / `rr_du`             | environment, workspaces, running jobs / workspace sizes                                                                                                                                                                | —                                                                |

`rr.sh` is portable to bash 3.2 (macOS) and bash 5 (Debian). Local test:
`bash tests/test_core.sh`, which uses a localhost mock of the presigned-PUT semantics.

## Noninteractive font fallback

Inspect and save primary-source glyph crops plus any necessary supplementary font specimens under the typography role in `analysis/references.json`; a font name alone is not visual verification. Match the actual source and do not import another reference's typography as a redesign.

Discover the actually installed font files instead of assuming this inventory is current. A missing face must never trigger a request for the user to provide a font, name or link. Preserve unchanged reference text as pixels or outlines; for changed words, use the closest installed font or autonomously retrieve a verified openly licensed font through an authorized available operation. If retrieval fails, continue with the installed match, tune its geometry and disclose the remaining difference. Save used font assets with project state when possible.

## Bundled Katana fonts

The existing Katana bundle includes League Gothic, UnifrakturMaguntia, Cormorant and Inter at `$HF_WORKFLOWS/katana/scripts/fonts/`, with font source and license records beside them. The compositor serves these assets as `/_hf/katana/scripts/fonts/<file>`. Select them only when their letterforms fit the task; otherwise use a suitable accessible face or preserved source lettering. Load the chosen font explicitly and inspect required glyphs without asking for font files.
