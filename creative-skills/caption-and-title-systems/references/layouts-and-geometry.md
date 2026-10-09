# Layouts and geometry (9:16)

Contents:
1. Clip fields and transform math
2. Fit modes and the corner-radius rule
3. Layout building blocks
4. 9:16 layout presets (split screens, PIP, talking head plus cards)
5. Shot blueprints (capability to construction)
6. Positioning text relative to layouts

Numbers in sections 4 and 6 are starting geometry derived by arithmetic from a 1080x1920 frame and the safe zones in `subtitle-rules.md`. Tune by eye. Sections 1, 2, 3 and 5 come from the source's geometry contracts.

## 1. Clip fields and transform math

A clip has: transform, intrinsic size, opacity, blend mode, effects, time range, animations, presets, mask, visibility and lock flags. Media clips additionally have an asset, trim, volume, mute, speed, pitch preservation and corner radius.

- `timeRange: { start, duration }` in seconds. Top-level starts are scene-local; nested starts are parent-local.
- `trim: { start, end }` in source seconds.
- Transform x and y place the anchor in scene pixels. Scale x and y multiply the intrinsic size. Rotation and skew are in degrees. Anchor x and y are normalized (0 to 1) inside the clip box.
- Premiere and AE equivalents: Position is the anchor's location in frame pixels; Scale is a percentage of intrinsic size; Anchor Point is in layer pixels (normalize it yourself when you reason about pivots). Scaling about the anchor means a centered anchor scales in place and a corner anchor scales away from that corner.
- Box masks are center-based and clip-local; a composition-node mask may use a different top-left schema. When moving a mask between tools, re-check which origin it uses.
- Animated clip properties use property names such as position, offset, scale, opacity, volume or effect parameter. A dotted path such as `transform.x` is not an animation property name; animate Position, not "x".
- Raw edits that change the document (move, insert, remove, set) address clips by array positions. Read fresh state before deriving positions, and preserve unrelated fields. In an editor, this translates to: change only the clip you mean to change; do not rebuild a human-edited timeline from scratch.

## 2. Fit modes and the corner-radius rule

| Fit | Behavior | Premiere / AE |
|---|---|---|
| Cover | Fills the slot, crops overflow, keeps aspect | Scale up until the slot is filled, then crop with a mask or let the slot clip it |
| Contain | Fits entirely, letterboxes, keeps aspect | Scale to Frame Size / Fit |
| Fill | Stretches to the slot, distorts aspect | Never use for footage |

Automatic media slots in a layout center contain and cover content and preserve aspect. A slot needs a resolvable height. Standalone media needs explicit geometry; do not assume it centers itself.

Corner radius is clip-local and pre-transform. If a clip is scaled to 50%, a radius of 64 px on the clip shows as 32 px on screen. To get an intended on-screen radius, divide it by the scale: target 48 px at 150% scale means set 32 px. The corner radius object holds a uniform value or four corner values (tl, tr, br, bl). In AE, rounded corners on a precomp via a rounded mask scale with the layer in the same way; compensate or round the matte at final size.

## 3. Layout building blocks

A persistent layout frame owns its arrangement:

- Layout modes: column (default), row, equal-column grid, and none (deliberate absolute positioning). Layout mode itself does not animate. Grid has equal columns only: no spans, no min-max.
- Sizing: positive pixels, fill, or hug. Fill needs a resolvable parent axis; absolute frames need explicit dimensions.
- Properties: gap, row gap, padding (single value or per side), wrap, align (start, center, end), justify (start, center, end, space-between), origin (top-left or center).
- Background, radius and clip live on the frame.
- Reveal clips without reflow; animating width, height or gap reflows the children. Use reveal when the layout should stay fixed, animate size when it should reflow.
- Children use local coordinates and local time and cannot outlive the frame.

In Premiere and AE you build the same thing by hand: a precomp or nested sequence per slot, with explicit pixel rectangles for each slot (section 4), and a parent null or adjustment layer for shared motion.

## 4. 9:16 layout presets (frame 1080x1920)

Safe box from `subtitle-rules.md`: x 119-961, y 192-1599.

| Preset | Slots (x, y, w, h in px) | Notes |
|---|---|---|
| Full-bleed | A: 0, 0, 1080, 1920 (cover) | Captions in the safe box; the default |
| Split screen, top/bottom 50/50 | A: 0, 0, 1080, 960; B: 0, 960, 1080, 960 | Both cover-fit. The seam sits at y 960, mid-frame; captions straddling the seam read badly, so place captions fully in the bottom slot's upper part or at the seam with a plate |
| Split screen, 60/40 | A: 0, 0, 1080, 1152; B: 0, 1152, 1080, 768 | Main content on top, reaction or demo below; keep the bottom 321 px of the lower slot free of text |
| Split screen, left/right | A: 0, 0, 540, 1920; B: 540, 0, 540, 1920 | Each slot is 9:32, a very narrow crop; use only for tall subjects |
| Thirds (stack of 3) | 0, 0 / 0, 640 / 0, 1280, each 1080x640 | Dense; text only in the middle band |
| Footage beside graphics | Footage: 0, 192, 1080, 1100 (contain or cover) ; graphics card below at 60, 1320, 960, 280 | Row/column frame with a centered media slot plus text/card frames |
| PIP, corner | 360x640 window (9:16 inset, one third of frame width) at x 60, y 940 (bottom edge 1580, above the bottom 321 px zone; left side, so it stays clear of the right-edge platform buttons) | Round corners 24 px at final size, 4 px white or accent stroke, soft shadow; captions then use the right two thirds or sit above/below the window |
| PIP, circle face cam | 320 px circle at x 120, y 1180 | Cover-fit, circular mask, 6 px stroke |
| Talking head plus cards | Head full-bleed; card frame 840x220 at x 120, y 1250 (inside safe width) | Spine clip carries picture and audio; cards and titles are composed overlays above it |
| Before / after | Top/bottom 50/50, or one slot with a vertical wipe line at x 540 | Use identical framing in both halves; animate the wipe with a mask |
| Hub-and-spoke diagram | Hub 240 px circle at center (420, 840); spokes as paths to 4 nodes of 160 px | Path connectors, icons, groups and 2D transforms |

PIP safety: the source assigns no fixed PIP size; the geometry above keeps a 9:16 inset at one third of frame width. Do not park a PIP where it hides the main subject's face or where captions need to be.

Platform side buttons: Reels, TikTok and Shorts put action buttons along the right edge of the lower half. The 11% side margin (119 px) already keeps text out of that column; keep PIP windows out of the right column as well unless the window is decorative (the left-side PIP position above does this).

## 5. Shot blueprints (construction primitives)

These are capability mappings, not required templates.

| Need | Primitives |
|---|---|
| Sequential phrases or states | Sequence, child at/duration, text keyframes |
| Cards, lists, or logo walls | Persistent frame with column, row or equal-column grid layout |
| Input-to-result demonstration | Frames for UI regions, cursor paths, explicit state clips |
| Control and target moving together | Shared keyframe data applied to separate nodes or frame motion targets |
| Footage beside graphics | Row/column frame with a centered media slot and text/card frames |
| Talking head with overlays | Spine cut for audio and picture, plus composed frames for titles and cards |
| Metrics and charts | Text, rect, path, effect parameter, width/height, color and draw-progress tracks |
| Hub-and-spoke diagram | Path connectors, icon/media nodes, groups and 2D transforms |
| Before / after comparison | Row or grid frames with synchronized node tracks |
| Zoom or parallax | Top-level z values plus a camera, or group/frame 2D transforms |
| Logo or title build | Path, shaped-text draw progress, masks, reveal, token motion and keyframes |
| Abstract field | Deterministic path/rect states, gradients, effects and explicit tracks |

Frame child clocks are parent-local; keyframes are node-local. A child with explicit timing must fit the parent's half-open lifetime. There are no per-frame callbacks, so state is represented by keyframes, sequence children, text motion, frame choreography or explicit clips. Use contain or cover media in a frame with resolvable dimensions. Animate frame width/height when layout should reflow; use reveal when it should remain fixed.

Two audio facts that bite layouts: composed media is picture-only (an overlay clip's mute and volume do not bring its audio into the mix). Keep required audio on the spine, extract it separately, or mix after render. An audio clip cannot share a track with visual clips.

## 6. Positioning text relative to layouts

- Captions: baseline inside the safe box, normally in the lower part (bottom edge at y 1599 for Reels spec, 1594 for faceless). Center-aligned text, anchor at the text center.
- Split screens: caption belongs to the speaking slot. If both slots talk, use the seam with a plate, or alternate caption position per speaker.
- Cards: card width up to the safe width of 842 px (x 119-961); keep 24 px minimum internal padding on a 1080 frame so strokes and shadows do not clip.
- Do not stack titles and captions in the same 200 px band.
- Keep corner radii on one scale per video (all sharp, all about 16-24 px, or all pill).
- Footage that must show a face: protect the face box first, lay out text around it second.
