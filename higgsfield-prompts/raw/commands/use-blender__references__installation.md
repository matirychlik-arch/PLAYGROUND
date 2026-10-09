# /use-blender/references/installation

# Install background Blender MCP

Requirements: Node.js 24+ with npm, and Blender 4.2+ on the user's own computer. Target package: `fnf-blender-mcp@latest`. No add-on, source checkout, separate Python installation or open Blender window is required. Blender supplies its own Python runtime.

Check Node/npm and locate the intended Blender executable. Common locations are `/Applications/Blender.app/Contents/MacOS/Blender`, `C:/Program Files/Blender Foundation/Blender <version>/blender.exe`, or `blender` on Linux PATH. A missing default path does not prove Blender is absent. On Windows, use `npm.cmd` if PowerShell blocks `npm.ps1`. Use absolute executable paths when PATH differs between the shell and MCP client. Do not install Blender itself unless requested.

Before changing an existing installation, check `npm view fnf-blender-mcp@latest version --registry=https://registry.npmjs.org/`. Confirm that the latest published version is 0.2.0 or newer before installing. If the registry is unavailable or latest points to an older release, report the blocker; do not install the obsolete 0.1.0 add-on runtime. An authentication error on this public package calls for checking registry configuration, not creating an npm account or exposing tokens.

## Install and configure

Install the latest published package, or rerun the same install command to update an existing installation. Use a persistent directory owned by the user. Do not register paths inside temporary directories, a cloud sandbox or an npx cache.

macOS / Linux (replace the executable path with the discovered path):

```sh
blenderDir="$HOME/.higgsfield/blender-mcp"
npm install --prefix "$blenderDir" --registry=https://registry.npmjs.org/ --no-audit --no-fund fnf-blender-mcp@latest
blenderCli="$blenderDir/node_modules/fnf-blender-mcp/dist/cli.js"
node "$blenderCli" doctor --blender "/absolute/path/to/blender"
node "$blenderCli" config --blender "/absolute/path/to/blender" --format json
```

Windows PowerShell:

```powershell
$blenderDir = Join-Path $env:LOCALAPPDATA 'Higgsfield/blender-mcp'
npm.cmd install --prefix $blenderDir --registry=https://registry.npmjs.org/ --no-audit --no-fund fnf-blender-mcp@latest
$blenderCli = Join-Path $blenderDir 'node_modules/fnf-blender-mcp/dist/cli.js'
node $blenderCli doctor --blender 'C:/absolute/path/to/blender.exe'
node $blenderCli config --blender 'C:/absolute/path/to/blender.exe' --format json
```

The generated entry contains absolute Node/server paths and `BLENDER_EXECUTABLE`. The CLI prints configuration; it does not register the server. Inspect an existing `higgsfield-use-blender` entry in the **client running this conversation**. Reuse a matching enabled entry; do not overwrite a conflict or intentional disablement.

- **Codex local:** run `config --format toml` and inspect `codex mcp get higgsfield-use-blender`. If absent, register the printed Node/server paths with `codex mcp add --env BLENDER_EXECUTABLE=<absolute-blender-path> higgsfield-use-blender -- <absolute-node-command> <absolute-server-arg>`, or merge the complete printed TOML entry including its environment.
- **Claude Code local:** inspect `claude mcp get higgsfield-use-blender`. If absent, register with `claude mcp add --scope user higgsfield-use-blender --env BLENDER_EXECUTABLE=<absolute-blender-path> -- <absolute-node-command> <absolute-server-arg>` using the paths printed by `config --format json`. Keep `--env` after the server name so Claude does not parse the name as another environment value. Do not put the entry in Chat's `claude_desktop_config.json` for a Code session.

Quote the whole `BLENDER_EXECUTABLE=<absolute-blender-path>` argument when the path contains spaces. Preserve other servers and tool policies. Keep the installation and Blender executable at their registered paths. Confirm the entry in the same client, then start a fresh conversation for tool discovery.

Refresh the MCP connection, then follow the verification reference. `doctor` starts and terminates a separate empty background process; it does not inspect the MCP session or prove that the current conversation has tools.

## Upgrade from 0.1.0

Save any needed work before reconnecting. Replace the package and refresh the server entry with `config`; remove obsolete `BLENDER_MCP_PID` and `BLENDER_MCP_RUNTIME_DIR` overrides from this server entry. Version 0.2.0 does not discover or attach to the old bridge. `launch`, `install-addon` and `bl_screenshot` are removed; use `bl_render` with a camera for visual evidence. The old add-on can be disabled in Blender Preferences once no client needs it; do not delete user files or reset preferences during migration.

