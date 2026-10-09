# /use-after-effects/references/verification

(note: instructions_markdown value from {"mode":"instructions",...} response, JSON string unescaped to plain markdown)

## Verify the actual connection

Track four separate results: dependencies installed, MCP initialized and tools listed, AE returned a live response, and the current conversation can call those tools. Record the execution context for each result. `doctor`, offline skills/catalog, an enabled toggle and a startup log prove only their respective checks. A successful external PowerShell test does not establish that this conversation can control AE.

First inspect the current conversation's callable tools and use available tool discovery/search before declaring local tools absent. If `ae_get_skill` or `ae_project_info` cannot be discovered, use the missing-tools procedure below instead of attempting nonexistent calls or reinstalling working dependencies.

Use tools from the **local `higgsfield-use-after-effects` server**, not similarly named tools from a cloud bridge:

1. Call `ae_get_skill` with `{}` for the bundled index.
2. Call `ae_get_skill` with `{"name":"ae-clean-rig"}` for the shared editing rules. Load individual modules only when relevant, for example `{"name":"ae-clean-rig","reference":"references/07-sliders.md"}`.
3. Call `ae_project_info` with `{}` to verify live communication and inspect existing work. AE may start on this first live call. On macOS, allow the host application's Automation request when shown. If AE reports file access disabled, enable **Allow Scripts to Write Files and Access Network** in its scripting preferences as part of the requested setup.
4. Call `ae_catalog` with `{}`, then with a needed category, to discover the exact supported operations. Use `ae_do` for requested edits. The cloud FNF server does not acquire these local tools merely because this instruction was loaded; they must be connected in the desktop client.

Preserve unsaved projects. Do not reset the project or run a mutating demo just to test connectivity. A timeout after a mutation can mean execution completed: inspect state before retrying. Only report control from this conversation after a successful live response through its local MCP tool. Distinguish an installed MCP with unreachable AE, an externally verified bridge, and tools verified in this conversation.

## Server enabled but tools missing in this conversation

Inspect the registration on the same host and profile as this conversation: server name, absolute Node/server paths, environment, startup result and advertised tools. Where the installed Codex CLI supports them, use `codex mcp list` and `codex mcp get higgsfield-use-after-effects`; inspect applicable tool allow/deny lists as described in the [MCP configuration reference](https://developers.openai.com/codex/mcp/). Do not remove intentional restrictions. A server's own `tools/list` result and the agent's callable tool list are separate evidence.

Use refresh/reconnect controls actually available in the installed client. Do not assume a `/mcp` slash command or a particular settings/status screen exists. After one supported refresh or restart, rediscover the tools. If they remain absent, stop repeating restarts and collect the registration, client version, current host/profile, advertised versus available tool names, and relevant startup errors. Suggest testing a fresh conversation only as a diagnostic, not a guaranteed fix.

Locate logs through the installed client's diagnostics or discovered configuration/data paths. Do not invent `%LOCALAPPDATA%/Codex/logs` or copy another user's absolute path. If a logs SQLite database is discovered, inspect its schema and query only relevant records read-only; do not assume a fixed filename or table layout. Permission denied does not establish whether a path exists. A startup success from a different time, host or server is not proof for this conversation.

A direct local stdio test can isolate server and AE behavior when permitted, but label it as an external diagnostic. Do not silently replace requested chat control with generated `.cmd` files or manual scripts. If chat tools remain unavailable, report that exact limitation and the evidence needed to investigate it.

If only some tools are missing, compare the advertised list and installed bridge policy before treating this as a connection failure. For example, a successful `ae_project_info` with no `ae_do` can mean inspection is available while editing is restricted. Report the available capability without relaxing policy automatically. Keep logs/config excerpts limited to the relevant entries and redact secrets before sharing them.

## Windows: live call times out

After the first completed live-call timeout, diagnose before retrying. The bridge can already relaunch the dispatcher within one call; another unchanged call may just repeat the same failed launches. Preserve the exact error, including whether the request was never picked up or was consumed without a response.

Before a shell-based diagnostic, record `whoami`, the shell/working directory, the resolved Node executable, and the relevant `TEMP`, `TMP`, `AE_MCP_EXE` and `AE_MCP_RUNTIME_DIR` values. Inspect the running `AfterFX.exe` process owner and session when permitted. Do not assume the agent's shell, the desktop client's MCP process and AE run as the same Windows user or on the same desktop. The [Windows sandbox documentation](https://developers.openai.com/codex/windows/) describes execution-context restrictions, but a username or timeout alone does not prove their role in this failure.

Compare the bridge's resolved mailbox/pointer paths with AE's expected location using the installed bridge's logs and code. The bridge uses Node's OS temp directory while the dispatcher uses AE's `Folder.temp`; different user contexts can resolve different locations. Inspect path agreement and access without deleting pending requests or changing ACLs. Do not share a writable mailbox between unrelated users or change sandbox/protection settings automatically.

If allowed, compare the same non-mutating `ae_project_info` test from the user's ordinary local PowerShell using the same Node, server, AE path and relevant environment. For a test outside the agent's permitted context, use the supported approval path or an explicit user-run diagnostic; do not bypass a tool denial. Success there and failure in the agent shell narrows the issue to execution context, but does not identify the exact cause or prove MCP tools are available in chat. Do not repeat successful dependency installation or claim that switching to full access fixes it.

After a relevant path, registration or user-authorized permission change, rerun one non-mutating live test and report the observed result. If still blocked, give a concise handoff: which of the four checks passed, which context failed, the exact error and the next supported action. Preserve the project; inspect state before retrying any timed-out mutation.

When the user requests an actual edit, follow the retrieved AE skills, inspect before editing, render representative frames with `ae_render_frame`, review them, and save only to the intended destination. This integration currently controls After Effects; Blender and Premiere require separate adapters.
