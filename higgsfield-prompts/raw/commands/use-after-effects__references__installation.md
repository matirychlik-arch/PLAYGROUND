# /use-after-effects/references/installation

(note: instructions_markdown value from {"mode":"instructions",...} response, JSON string unescaped to plain markdown)

## Install the local runtime

Requirements: Node.js 24+, npm, and Adobe After Effects installed on macOS or Windows. Automated checks cover instruction loading, not a live Windows installation. A reported successful Windows shell test does not establish end-to-end control from the desktop conversation.

Source repository: https://github.com/higgsfield-ai/fnf-local-pluging-bridge-mcp

Check dependencies in the local shell that will perform installation. On Windows, follow the discovery steps below before recommending installation. On macOS, check `node --version` and `npm --version` and inspect their resolved paths if either fails. A missing command, a blocked PowerShell script, and an absent installation are different failures; retain the command and error that establish the diagnosis.

If Node/npm are actually missing, install Node.js 24 LTS with npm from https://nodejs.org/en/download on the user's computer within the requested setup scope. If an older Node is installed, upgrade using the user's existing installation method. Reopen the terminal after installation; an already-running desktop client may also need restarting to inherit a changed PATH. Recheck both versions before installing the bridge. npm/npx cannot bootstrap themselves without Node/npm. If an interactive installer or OS permission requires the user, request only that action and resume afterward.

## Windows: discover Node and npm

Use local PowerShell, including Windows PowerShell 5.1. Before installing into a user directory or registering the client, record `whoami`, `$env:USERPROFILE`, `$env:LOCALAPPDATA` and the client's configured data/config location if available. Compare with the desktop client's and AE's user/session when discoverable. A sandbox account's profile or temporary directory is not the user's persistent installation target, and its default CLI configuration may belong to a different profile. Do not install or register into that profile as a substitute. Use a permitted execution context and persistent paths accessible to the intended desktop client; if access is unavailable, give the manual handoff below. Do not change user identity or sandbox settings to bypass restrictions.

First inspect command resolution:

```powershell
Get-Command node.exe,npm,npm.cmd,npx.cmd -All -ErrorAction SilentlyContinue |
  Select-Object Name,CommandType,Source
where.exe node
where.exe npm
```

Use `where.exe`, not PowerShell's `where` alias. When Node resolves, run `node --version` and `node -p "process.execPath"` to identify the actual executable. A client-bundled Node runtime can exist without npm; finding Node alone is insufficient.

If `npm --version` fails, try `npm.cmd --version` in PowerShell. An error about `npm.ps1` and script execution policy does not mean npm is absent. Use the verified `.cmd` launcher; do not change execution policy to make installation work.

If npm or Node is not on PATH, inspect these existing locations before declaring it missing:

- The directory of the resolved `node.exe`: look for `npm.cmd` and `node_modules/npm/bin/npm-cli.js`.
- `%ProgramFiles%/nodejs`, `%LOCALAPPDATA%/Programs/nodejs`, and `%APPDATA%/npm`.
- Existing version-manager locations indicated by `NVM_HOME`, `NVM_SYMLINK`, `VOLTA_HOME`, or resolved command paths. Reuse the user's existing manager instead of installing a second one.

Check candidate files with `Test-Path -LiteralPath`. Invoke verified absolute paths with PowerShell's call operator, for example `& $nodeExe --version` and `& $npmCmd --version`, where these variables hold discovered paths. If only `npm-cli.js` is present, use `& $nodeExe $npmCli --version` and the same invocation for subsequent npm commands. Verify Node is 24+ and npm actually runs. If its launcher needs Node on PATH, prepend the verified Node directory to this shell's `$env:Path`; do not replace the user's persistent PATH. Prefer a persistent Node installation over a temporary/cache runtime for the registered MCP server.

Continue with resolved absolute paths when available; a stale PATH alone is not a reason to stop or reinstall Node. [PowerShell command resolution](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_command_precedence) and [npm installation folders](https://docs.npmjs.com/cli/v11/configuring-npm/folders/) describe these launcher and prefix conventions.

### Recover a failed Node download or inaccessible installation folder

When Node/npm must be installed, separate download failure from filesystem failure. Capture the exact downloader, official URL, destination and error. `SEC_E_NO_CREDENTIALS` during an HTTPS download is a Windows security-context failure, not evidence that an npm account is required. It alone does not identify a proxy, certificate, sandbox or filesystem root cause.

1. Check that the intended destination is writable before downloading. Prefer a persistent user-owned directory such as `$env:LOCALAPPDATA/Higgsfield/node`; create it within the allowed setup scope and verify a uniquely named temporary file can be written and removed there. Directory existence and an approval message do not prove write access. If ordinary filesystem permissions prevent that location, use another permitted user-owned location. If the tool reports a sandbox or policy denial, use its supported permission mechanism if available; do not change paths or tools to evade a denial. If permission is granted but the operation still fails, retain the new error and report the unresolved execution restriction.
2. If `curl.exe` fails with a TLS/Schannel error and the tool did not deny network access, try one available alternative downloader against the same official HTTPS URL. For Windows PowerShell 5.1, use `Invoke-WebRequest -UseBasicParsing -Uri $nodeDownloadUrl -OutFile $nodeArchive -ErrorAction Stop` with verified URL and destination variables. This can behave differently from curl but is not guaranteed to fix the security context. Do not disable certificate validation, switch to HTTP, or change machine-wide TLS/proxy settings. Do not repeat an unchanged failing command.
3. If an MSI requires unavailable elevation, use the Windows ZIP distribution from the [official Node 24 release directory](https://nodejs.org/dist/latest-v24.x/) when portable installation is permitted. Resolve the exact release and OS architecture first, download that release's `win-x64.zip` or `win-arm64.zip` and its `SHASUMS256.txt` from the versioned official directory, and compare the archive's SHA-256 with its exact manifest entry before extraction. Download the complete distribution with npm, not only `node.exe`. Extract to the verified persistent directory without overwriting an existing runtime. Verify its absolute `node.exe` and `npm.cmd` paths and versions, then continue bridge installation with those paths. Never register a runtime in a temporary download/extraction directory.
4. If permitted shell download methods still fail, offer downloading the official installer or ZIP in the user's browser. If browser tooling is available and authorized, perform that download; otherwise use the user handoff below with the exact official release link. Resume using the verified installed paths. A browser download may succeed, but do not promise it fixes TLS or access restrictions. If filesystem access remains denied, downloading alone is insufficient; report that restriction separately.

Keep the discovered AE path and completed checks while recovering Node setup. Refresh the MCP connection after registration; request a desktop-client restart only when needed to pick up changed environment or connections. A restart alone is not a remedy for a failed download or inaccessible folder.

### When the user needs to install Node manually

Give a complete, short walkthrough in the user's language, not just "install Node and restart". State the actual blocker in one sentence, retain any discovered AE version/path, and adapt this handoff to the user's desktop client:

1. Open [the official Node.js download page](https://nodejs.org/en/download) in the browser on this Windows computer. Choose **Node.js 24 LTS**, **Windows**, and **Windows Installer (.msi)**. Specify the architecture already detected on this computer; use x64 for x64 Windows and ARM64 for ARM64 Windows. Prefer a verified direct official installer link when available.
2. Open the downloaded `.msi` file from the browser's downloads or the Downloads folder. Follow **Next**, accept the license, and keep the default **npm package manager** and **Add to PATH** features enabled. Finish with **Install → Finish**. Optional tools for compiling native modules are not required for this bridge.
3. If installation fails or asks for an administrator password the user cannot provide, ask them to return with the error text. Offer the permitted ZIP installation described above; do not send them back through the same failing installer.
4. After successful installation, if the desktop client needs to inherit the new PATH, ask the user to finish active tasks, fully quit the client, and reopen it. Return to this conversation.
5. Give a ready-to-send continuation message: **"Node.js is installed. Continue connecting Higgsfield use After Effects: check Node and npm, install the bridge, register it, and verify the connection to After Effects."** Translate it into the user's language. Mention the AE version only if it was actually found.

Tell the user what happens next: the agent will check `node --version` and `npm.cmd --version`, reuse the known AE path, install/register the bridge and run the live verification. Do not require the user to run terminal diagnostics or configure MCP manually when the agent can do those steps. When the user returns, verify the installation before proceeding; their completion message alone does not establish that Node/npm work. If execution remains restricted, report the precise remaining action instead of claiming the connection is complete.

## Windows: locate After Effects

The bridge's built-in discovery probes only AE 2026, 2025, and 2024 under `C:/Program Files/Adobe/Adobe After Effects <year>/Support Files/AfterFX.exe`, plus the `AE_MCP_EXE` or legacy `AE_EXE` override. It does not search the registry. A failed default-path check is not evidence that AE is uninstalled.

Discover an existing installation in this order:

1. Validate any existing `AE_MCP_EXE` / `AE_EXE` value as a file with `Test-Path -LiteralPath`.
2. Inspect a running AE process and installed Adobe directories:

   ```powershell
   Get-Process AfterFX -ErrorAction SilentlyContinue | Select-Object Id,Path
   Get-ChildItem -Path "$env:ProgramFiles/Adobe/Adobe After Effects*/Support Files/AfterFX.exe" -File -ErrorAction SilentlyContinue |
     Select-Object -ExpandProperty FullName
   ```

3. If unresolved, inspect Windows App Paths for `AfterFX.exe` and uninstall entries whose `DisplayName` matches After Effects. Check `HKLM` and `HKCU`, including `SOFTWARE/WOW6432Node/Microsoft/Windows/CurrentVersion/Uninstall` as well as `SOFTWARE/Microsoft/Windows/CurrentVersion/Uninstall`. Treat `InstallLocation` and `DisplayIcon` as path hints, not commands to execute; validate the actual `Support Files/AfterFX.exe`. Missing registry entries do not prove absence.
4. Inspect After Effects shortcuts in the user/common Start Menu and Desktop, and follow their target paths. Check custom Adobe installation directories discovered there, including other drives. Avoid a recursive whole-drive search. An inaccessible process path or registry key is an inconclusive check, not a negative result.

Use the user's specified version, or the running installation when unambiguous. If multiple installations remain and the choice matters, ask which to connect. If these checks find nothing, ask for the installed AE executable path or for the user to open AE so its process path can be inspected. Summarize the locations checked; say "not found in the checked locations", not "not installed". Do not install Adobe software automatically.

Store the verified absolute executable path in `$aeExe`, then set it for this setup shell before running `doctor`:

```powershell
if (-not (Test-Path -LiteralPath $aeExe -PathType Leaf)) { throw 'AfterFX.exe path is invalid' }
$env:AE_MCP_EXE = $aeExe
```

Also persist `AE_MCP_EXE` in this MCP server's client configuration during registration below. A shell-only environment variable will not configure an already-running desktop client. Discovering a version outside 2024–2026 does not establish compatibility; report the version and verify live communication.

## Install the package

Install the latest published, prebuilt package. To update an existing installation, rerun the same install command:

```sh
npm install --global --ignore-scripts fnf-after-effects-mcp@latest
fnf-after-effects doctor
```

This includes the MCP server, JSX and offline skills. No Git clone, manual build, Python or separate AE plugin is required. If the registry confirms the package/version is unavailable, report that and stop; do not install a similarly named package. Keep DNS, TLS, proxy and registry-access failures separate from a missing release. Reuse a working installed version; this pinned command is not an instruction to downgrade another installation.

On Windows, use the verified npm invocation from discovery and `.cmd` launchers. For npm available as `npm.cmd`:

```powershell
npm.cmd install --global --ignore-scripts fnf-after-effects-mcp@latest
```

Check the install exit code before continuing. Find the global prefix with that same npm invocation (`npm.cmd prefix --global`), then invoke `<prefix>/fnf-after-effects.cmd` by absolute path with `&`. Windows global launchers live directly in the prefix, not in `<prefix>/bin`. Use this helper path for `doctor`, `config`, and `install-codex`. If the prefix is not writable, use a user-owned prefix such as `$env:LOCALAPPDATA/Higgsfield/ae-mcp` via `--prefix` and retain that prefix for discovery. Do not require administrator access for the bridge package.

If the helper shim fails despite a successful installation, use the verified persistent Node executable to run `<prefix>/node_modules/fnf-after-effects-mcp/dist/cli.js` directly, for example `& $nodeExe $bridgeCli doctor`, after checking that file exists. This avoids launcher/PATH failures without reinstalling a working package.

If a global installation fails with `EACCES` on macOS, use a user-owned prefix instead of `sudo`:

```sh
npm install --global --ignore-scripts --prefix "$HOME/.local" fnf-after-effects-mcp@latest
"$HOME/.local/bin/fnf-after-effects" doctor
"$HOME/.local/bin/fnf-after-effects" install-codex
```

Use that same explicit executable path for subsequent commands when using this prefix.

Inspect `doctor`'s JSON checks and exit code. Fix the named failure before continuing: an `after-effects` failure calls for locating AE/setting its path, while missing server/dispatcher files or a skill-integrity failure calls for repairing the package. A nonzero result does not by itself mean AE or Node must be reinstalled. `doctor` checks the installation and bundled skills without contacting AE, and does not test npm or conversation tool availability. Passing it does not yet prove live connectivity. For an AE installation outside the default paths, set `AE_MCP_EXE` to the `.app` bundle on macOS or `AfterFX.exe` on Windows in the local MCP client's server environment.

## Register the MCP client

Register on the **same local host and user profile as this conversation**. Claude Desktop Chat and Cowork are not supported for this setup flow; switch to **Code → Local** or a local Codex task. Do not install into a Cowork VM or Higgsfield cloud sandbox and mistake that for host registration. The `/use-after-effects` request authorizes package installation and registration; continue through verification without asking for a separate generic installation decision.

For Codex, with its CLI available locally:

```sh
fnf-after-effects install-codex
```

Run registration only against the same host and configuration profile used by the intended desktop conversation. This registers `higgsfield-use-after-effects` using absolute Node and server paths. It leaves a matching enabled registration in place and refuses to overwrite a conflicting entry. Keep the installed package and Node at the registered paths; do not run this helper from a temporary npx cache.

For an existing `fnf-after-effects` registration, inspect it with `codex mcp get fnf-after-effects` where supported. Before removing anything, save the existing entry privately and prepare its replacement, preserving command, arguments, environment, enabled state and tool policy. The helper refuses a duplicate legacy connection and does not migrate these settings. For an intentional rename, replace the entry through the client's supported configuration mechanism; if using CLI removal, remove only the legacy entry after the replacement is prepared, restore the preserved settings under `higgsfield-use-after-effects`, and verify the result. Do not delete a conflicting entry merely to make the helper succeed or silently enable an intentionally disabled server.

For Claude Code running locally, inspect `claude mcp get higgsfield-use-after-effects` first. Reuse a matching enabled entry. If absent, obtain the persistent absolute Node and server paths from:

```sh
fnf-after-effects config
```

Register the printed paths with `claude mcp add --scope user higgsfield-use-after-effects -- <absolute-node-command> <absolute-server-arg>`. If an explicit AE path is needed, pass `--env AE_MCP_EXE=<absolute-AE-path>` after the server name and before `--`; quote the whole `KEY=value` argument when the path contains spaces. On Windows use the working `claude` launcher and verified Node path. Preserve a conflicting or intentionally disabled entry and report the conflict instead of overwriting it. Confirm with `claude mcp get higgsfield-use-after-effects` and start a fresh Code conversation for tool discovery. Claude Code user scope is separate from Chat's `claude_desktop_config.json`.

For another supported local stdio client, merge only the printed `mcpServers` entry into its own configuration. A remote ChatGPT connector URL is not interchangeable with this local stdio configuration. Do not invent a cloud endpoint for the local server.

All companion skills are available through `ae_get_skill`; a separate global skill installation is optional and not needed for this setup. If the Codex CLI is unavailable (including a Windows command-shim failure), use the printed configuration in Codex's supported local MCP settings.

The integration's display name is **Higgsfield use After Effects**. If an existing client still shows "Fnf After Effects", inspect its saved registration and installed server metadata and use the migration procedure above when appropriate. Changing these instructions alone cannot rename a saved registration, update an installed package, or relabel historical activity.

On Windows, `install-codex` can fail even when `codex.cmd` works in PowerShell: the package invokes `codex` through Node `spawnSync` without a shell, and Windows `.cmd` launchers require a command interpreter. Do not interpret that failure as a missing bridge or AE installation. Use `config` through the verified helper or direct Node invocation, then configure the client with its printed absolute Node `command` and server `args`. See [Node's Windows launcher behavior](https://nodejs.org/api/child_process.html#spawning-bat-and-cmd-files-on-windows).

When using an explicit AE path, add `env.AE_MCP_EXE` to this server entry in a JSON MCP client configuration. For Codex's TOML configuration, merge the printed `command` and `args` into `[mcp_servers.higgsfield-use-after-effects]` and the override into `[mcp_servers.higgsfield-use-after-effects.env]` as `AE_MCP_EXE`; use the discovered configuration file for the intended host/profile. The helper's `config` output and `install-codex` registration do not include this override automatically. Preserve other servers and existing settings; do not paste the `mcpServers` JSON document into TOML. Use valid escaping for Windows paths, or forward slashes. Verify the saved entry contains the persistent Node/server paths and the AE override before refreshing the MCP connection.

Finish by loading `/use-after-effects/references/verification` and running its live checks. If blocked, report the failing command/error, discovered Node/npm/AE paths and the specific remaining action. Do not stop at a generic request to reinstall dependencies when a verified path or launcher fallback works.
