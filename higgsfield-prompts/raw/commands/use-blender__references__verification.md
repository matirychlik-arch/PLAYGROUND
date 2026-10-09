# /use-blender/references/verification

(note: instructions_markdown value from {"mode":"instructions",...} response, JSON string unescaped to plain markdown)

# Verify the background session

Use the current conversation's tools from **higgsfield-use-blender**:

1. `bl_health` must return the Blender version, PID, `background: true`, active file and scene. The first call starts a dedicated process with factory startup settings; it does not attach to an open window.
2. `bl_get_scene_summary` reports this session's scene. Load an existing saved `.blend` with `bl_open_project` when requested; preserve current session changes first.
3. Before edits, load `bl_get_skill` with `name: "blender-scene"` and inspect relevant objects. Use a camera and `bl_render` for appearance checks. There is no viewport screenshot tool in background mode.

If tools are absent, inspect the client's MCP registration, persistent paths, `BLENDER_EXECUTABLE`, startup errors and tool restrictions, then refresh the connection. A successful shell `doctor` is not evidence that the conversation can control Blender. Do not reinstall a working runtime merely because tools have not been discovered.

One process belongs to one MCP connection. Changes persist between calls, but reconnecting, stopping MCP or a process crash loses unsaved scene state. Save deliverables explicitly before closing; open the saved output in desktop Blender separately when needed. Python local variables do not persist across calls; scene datablocks do.

A timeout does not cancel or repeat a command. Use its `job_id` with `bl_job_status` on the same MCP session. Other execution tools reject calls while that job is running; status and offline skill tools remain usable. Errors can leave partial scene or file changes. Inspect before retrying; never assume rollback. Job history retains at most 128 jobs and disappears on reconnect. A process failure does not trigger an automatic restart or recovery; inspect output files and explicitly reconnect to start a new session.

`bl_open_project` guards unsaved changes, and save/render refuse existing output files unless `overwrite: true`. Use a new output path when the user has not authorized replacement. Arbitrary Python has the Blender process's filesystem permissions and can bypass those typed-tool guards.

For long renders set the client tool timeout above 300 seconds. If the client times out before a job ID arrives, report uncertain completion and avoid resubmission. Verify only the platforms and Blender versions actually tested; fixtures alone do not prove native scene editing.
