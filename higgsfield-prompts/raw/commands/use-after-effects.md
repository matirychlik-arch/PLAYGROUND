# /use-after-effects

---
name: use-after-effects
title: Higgsfield use After Effects
description: Install and connect the local Higgsfield use After Effects integration on your computer.
---

# Higgsfield use After Effects

## Execute the setup request

`higgsfield mcp, /use-after-effects` is a request to install and connect this integration. In local Codex or Claude Code (including Claude Desktop **Code → Local**), use the host shell to complete the installation, register the server for the current OS user, and verify it. The command itself authorizes these setup steps; use the latest published package and do not stop to ask whether to install, which version, or which registration scope. Honor any narrower scope or other constraint the user states. Client or OS permission prompts may still require approval. Setup does not authorize editing the user's After Effects projects.

Claude Desktop Chat and Cowork are not supported for this host installation flow. Code Cloud and Higgsfield `sandbox_exec` are not host shells either. If this conversation cannot run a shell on the same computer as After Effects, ask the user to switch to **Code → Local** (or a local Codex task) and repeat the same command. Do not present manual setup as completed installation.

Use Higgsfield use After Effects to connect a desktop MCP client to Adobe After Effects on the user's computer. The connection is:

Desktop MCP client → local Node MCP server → OS scripting / ExtendScript → After Effects.

Use **Higgsfield use After Effects** as the user-facing integration name in progress updates and results. `fnf-after-effects-mcp` and `fnf-after-effects` are package/CLI identifiers, not display names. Register the local MCP server as `higgsfield-use-after-effects`; if the client offers a display-name setting, use the exact integration name above.

This command directs the local coding client to perform setup. It is not a media preset: do not open a preset gallery, request a reference image, submit generation, or fall back to ordinary generation. Follow the user's requested setup or editing scope.

## Where installation runs

Use a shell on the user's own Mac or Windows computer. The Higgsfield `sandbox_exec` tool and a cloud coding sandbox cannot install software into the user's desktop AE or register its local MCP client. If only a remote/web environment is available, give these local steps and explain that a desktop client is required; do not claim to have connected AE from the cloud.

No Higgsfield AE panel, cloud bridge account, or bridge OAuth login is needed. Adobe licensing and OS permissions are separate requirements. Installing the public npm package requires no npm account or GitHub login.

## Load instructions as needed

First inspect the tools available in the current conversation, using the client's tool discovery/search when provided. If local After Effects tools are available, load the verification reference and check the existing connection before reinstalling anything. If tools are absent but an existing registration or successful setup is reported, load that reference's missing-tools procedure first. Use installation instructions for a fresh setup or a specific missing/broken dependency found during diagnosis. A configured server and an enabled toggle do not establish tool availability in this conversation.

Before checking dependencies, installing or registering the bridge, call `get_preset_instructions` with `{"preset":"/use-after-effects/references/installation"}` and follow the returned instructions. On Windows, complete its Node/npm and After Effects discovery steps before concluding that a dependency is missing or asking the user where AE is installed.

Before verifying connectivity or performing edits, call `get_preset_instructions` with `{"preset":"/use-after-effects/references/verification"}` and follow the returned instructions. It covers missing conversation tools and Windows execution-context timeouts. Only report control from this conversation after a successful live call through its local MCP tools.


## Available references

Read a reference only when needed by calling get_preset_instructions with the exact preset argument below.
- {"preset":"/use-after-effects/references/installation"}
- {"preset":"/use-after-effects/references/verification"}
