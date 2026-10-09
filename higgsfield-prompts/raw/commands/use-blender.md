# /use-blender

---
name: use-blender
title: Higgsfield use Blender
description: Set up the local Higgsfield use Blender MCP to create, edit and render .blend projects in a background Blender process without an add-on.
---

# Higgsfield use Blender

## Execute the setup request

`higgsfield mcp, /use-blender` is a request to install and connect this integration. In local Codex or Claude Code (including Claude Desktop **Code → Local**), use the host shell to complete the installation, register the server for the current OS user, and verify it. The command itself authorizes these setup steps; use the latest supported published package and do not stop to ask whether to install or which registration scope. Honor any narrower scope or other constraint the user states. Client or OS permission prompts may still require approval. Setup does not authorize editing the user's Blender scenes.

Claude Desktop Chat and Cowork are not supported for this host installation flow. Code Cloud and Higgsfield `sandbox_exec` are not host shells either. If this conversation cannot run a shell on the same computer as Blender, ask the user to switch to **Code → Local** (or a local Codex task) and repeat the same command. Do not present manual setup as completed installation.

Connect a desktop MCP client to a dedicated background Blender process on the same computer:

Desktop client → stdio → fnf-blender-mcp → process pipes → Blender Python / bpy.

Use **Higgsfield use Blender** as the display name and `higgsfield-use-blender` as the server identifier. No add-on, HTTP listener, WebSocket or cloud account is required for local scene operations.

Each MCP session owns its own scene. Commands preserve that scene in memory until the connection closes; save needed work with `bl_save_project`. This integration cannot read unsaved work in an already-open Blender window. To edit that work, first save it in the desktop application, then load the file with `bl_open_project`. To inspect results in the UI, open the saved output file separately.

Use `fnf-blender-mcp@latest`; version 0.1.0 requires an add-on and cannot provide this workflow. This is a setup command, not a media preset. A remote cloud sandbox cannot install software on the user's desktop. First discover available local `bl_*` tools and verify an existing session before reinstalling.

For setup, read [installation](references/installation.md). For diagnosis and edits, read [verification](references/verification.md). When served by get_preset_instructions, load `/use-blender/references/installation` and `/use-blender/references/verification` respectively.


## Available references

Read a reference only when needed by calling get_preset_instructions with the exact preset argument below.
- {"preset":"/use-blender/references/installation"}
- {"preset":"/use-blender/references/verification"}
