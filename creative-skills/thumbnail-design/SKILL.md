---
name: thumbnail-design
description: "Design YouTube thumbnails, Shorts/Reels/TikTok covers and Instagram covers end to end with any image model (Nano Banana Pro first): pick one of 16 concept frameworks with an information gap, cast one of 11 emotions, write the full image prompt (face identity lock from a reference photo, YouTube lighting rig, composition for 1280x720 and 1080x1920 safe zones) and specify the text overlay (bake it in the image model or add it in Figma/Photoshop). Use this even if the user never says 'skill' whenever a video needs click-worthy packaging. Trigger on - miniatura, miniaturka, thumbnail, okładka filmu, okładka reelsa, cover do shorta, okładka na YouTube, miniaturka z moją twarzą, napis na miniaturce, nagłówek na miniaturce, jak zrobić miniaturę która się klika, wariant miniatury, before/after miniatura. For a consistent recurring character use character-sheet-builder first; for product-only packshots use product-shot-recipes; for the video itself use a video prompt skill instead."
---

# Thumbnail Design

Turn a video topic into a click-worthy thumbnail or cover: concept (framework), casting
(emotion), a ready-to-paste image prompt, and an exact text-overlay spec. The prompt grammar
is tool-agnostic; the adapters at the end say how to run it in Nano Banana Pro or elsewhere.

## When to use / when not

Use when:
- The user wants a YouTube thumbnail, a Shorts / Reels / TikTok cover, an Instagram cover, or "big bold viral-style packaging" for a video.
- The user has a face photo and wants themselves in the thumbnail (identity lock).
- The user wants variants (different emotions or camera takes) or a headline on the image.
- The user has a finished thumbnail and wants a surgical change (expression, background, rim colour).

Do not use when:
- The request is the video itself (use a video prompt skill) or a product packshot with no click-packaging goal (use product-shot-recipes).
- The user needs the same character across many scenes first (build the sheet with character-sheet-builder, then come back here with the sheet as the reference).
- The best thumbnail is a real frame from the video (framework 4): say so, and pick the frame instead of generating.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

| Input | Default if missing |
|---|---|
| Video topic / title and the truthful promise it makes | ask (the one input you cannot invent) |
| Platform and ratio | YouTube 16:9 (delivered 1280x720); Shorts/Reels/TikTok 9:16 (1080x1920); Instagram feed 4:5 (1080x1350) |
| Who appears: 0-3 people, with face photo(s) | if a person is needed and no photo exists, ask once (see gate below) |
| Exact scene content, props, location | derive from topic; default key element = the most concrete depictable noun |
| Reference thumbnail (style example only) | none; if given, ask once: match it or take a unique spin |
| Logo (flat or 3D) | none |
| Headline text and delivery (bake in model / overlay) | clean image, no text |
| Emotions and number of variants | emotion `shock`, 1 variant; offer ~4 (different emotion or camera take); hard cap 16 |
| Brand colour / rim colour | plain white rim; coloured rim only if named |

Gates, run before writing any prompt:
- **Character gate.** Decide WHO is in frame; never silently substitute a stranger. A supplied face photo is always attached and identity-locked. If the concept has a person and there is no photo, ask once: "Do you want yourself or a specific person in the thumbnail? Send a face photo and I will lock the identity, or choose a generated person, or no people." In a batch, ask this once before the whole set.
- **Text gate.** Default is a clean render with no text. Put text in the image only on an explicit ask (a headline is given, "add text", or a text framework is named). A text-carrying framework that you merely brainstormed renders text-free.
- **Variant gate.** If the count is not stated, ask once: one thumbnail or a set of about 4.

## Workflow

1. **Collect inputs** and run the gates above. Write the prompt in English; the baked headline stays in the user's language (usually Polish).
2. **Pick the framework.** Read references/frameworks.md. Brainstorm at least 5 truthful concepts across frameworks, keep the one with the strongest information gap (the image asks a question the title answers), one focal subject, minimal clutter. Combine frameworks only if it still reads in under a second at about 120px wide. Truthfulness law: exaggerate, never misrepresent the video.
3. **Cast the emotion.** Read references/emotions-and-lighting.md. Choose from the 11 presets by the video's promise (shock for reveals, charisma for calm authority, smug for "I was right", awe for scale). Take the parenthetical descriptor as the Expression phrase. For N variants, use the ladder: shock, hype, rage, awe, laugh, fear, smug, charisma, confusion, determination, disgust.
4. **Compose for the ratio.** Subject LARGE (about 40-60% of the frame, chest-up or medium-close, on a power third). 16:9: keep the bottom-right corner free (duration badge) and leave a free quarter for the headline. 9:16: faces in the upper two-thirds, important content inside the centre band, clear of top and bottom UI bands. Details in references/text-overlay.md section 2.
5. **Assemble the prompt** from the 11 blocks in references/prompt-blocks.md, in order, copying the library sentences exactly. Add an identity lock per face photo, the lighting rig on people, and the manifest line when 2+ images are attached.
6. **Specify the text** (only if a headline was asked). Pick a style preset (Beast default), position in a free quarter, 2-4 words. Choose the route: bake in the image model, or typographic layer in Figma/Photoshop. Full rules in references/text-overlay.md.
7. **Render and QA.** One variant per generation, highest resolution available. Check identity against the reference, stray text, the 120px test. Re-render the same prompt up to twice on a hard failure; never ship a drifted face silently.
8. **Tweak surgically** if asked: use the exact tweak prompts in references/prompt-blocks.md section 4 on the picked render (expression only, background only, background recolor, rim recolor).

## Output format

Deliver this brief, with the prompt in a fenced block ready to paste (one block per variant):

````
## Thumbnail brief
- Platform / ratio: YouTube 16:9 (deliver 1280x720)
- Framework: <number + name> (+ combined with <number + name>)
- Information gap: <the question the image raises; the title that answers it>
- Truthfulness check: <what in the video backs the image>
- Cast: <who> | Emotion: <preset> (<parenthetical descriptor>) | Take: <1-4>
- Text: none | headline "<TEXT>" | style <preset> | position <where> | route <bake / Figma>

## Prompt (variant 1: <emotion / take>)
```
IMAGE REFERENCES: image 1 = CHARACTER 1 face reference; image 2 = brand logo.   (only with 2+ images)
<block 1 frame contract> <block 2 scene brief> <block 3 text contract> <block 4 subject + identity lock + Expression>
<block 5 key elements> <block 6 logo> <block 7 location> <block 8 composition> <block 9 background>
<block 10 lighting rig> <block 11 grade>
```

## Text overlay spec   (only when a headline is requested)
Headline / Style / Font / Position / Size / Colors  (template in references/text-overlay.md section 5)

## Variant list
| # | Emotion | Take | Extra line appended |
|---|---|---|---|

## QA to run on the render
<the checklist items that matter for this brief>
````

Example of a filled prompt body (photoreal Posed Portrait, 16:9, one face photo, shock):

```
Bold, punchy YouTube-thumbnail composite — poster-grade, photoreal and high-impact, NOT a muted cinematic movie still, 16:9 aspect ratio, single unified frame — no split-screen, no diagonal divide, everything blends smoothly and organically across the same continuous shot. SCENE BRIEF (must be depicted exactly): a man holding a burnt pizza box at arm's length. No text, no readable UI labels, no watermark. CHARACTER 1: the person from attached face reference #1 — IDENTITY LOCK: reproduce this exact person with a photographic identity match — same bone structure, eye shape, nose, lips, jawline, skin tone, hairline and hair texture as the reference photo. Do NOT beautify, do NOT average with other faces, do NOT restyle the face; it must be recognizably the same person at a glance. Expression: mouth open gasp, wide eyes. Render the subject LARGE and dominant — the clear hero, filling roughly 40–60% of the frame, chest-up, pushed to the foreground and cleanly separated from the background. All faces crisply sharp as the anchors of the shot. KEY ELEMENTS: the charred pizza box oversized, thrust toward the camera, smoke curling up. COMPOSITION: the subject rendered LARGE and dominant — chest-up / medium-close, filling ~40–60% of the frame, pushed to the foreground on a power third, camera at eye level, strong separation from the background so the subject pops, shallow depth with a foreground accent element. BACKGROUND: bold, vivid saturated color-field gradient with punchy high-contrast tones matching the subject's palette, soft vignette, edge falloff. LIGHTING: signature YouTube thumbnail lighting rig on the subject — a strong KEY LIGHT sculpting the face with crisp highlights and controlled falloff, a soft dreamy DREAM LIGHT fill lifting the shadows with a subtle cinematic glow, and a defined BACK LIGHT + HAIR LIGHT tracing a clean bright rim along the hair, shoulders and silhouette, separating the subject sharply from the background. GRADE: vivid high-impact color grade, punchy high contrast, bright clean exposure, rich saturated colors that pop off the screen, deep blacks and bright highlights, crisp and glossy, poster-punchy, cohesive as one image. 16:9.
```

## Tool adapters

- **Nano Banana Pro:** the best fit. Render the prompt at the highest resolution and the exact ratio; attach the face photo(s) first, then the logo, with the manifest line. It renders text reliably: give the exact headline in double quotes with style words and position, then verify every character (Polish diacritics). It can also do the surgical tweaks: attach the finished render and paste a tweak prompt.
- **Higgsfield (Soul / image models):** same prompt works; use its image models for the render and an edit-capable model for tweaks. Use a Soul character or the sheet from character-sheet-builder as the face reference when the user has one.
- **KLING / Seedance 2:** poor fit for stills. Use them only to generate the video; pick a strong frame as a framework-4 thumbnail, or use the first frame of the clip as the face/scene reference for the image model.
- **Premiere Pro / After Effects:** export a still frame (framework 4) or build an animated text layer; they are the route for a cover that must match the first frame of the video.
- **Figma / Photoshop / Illustrator:** the deterministic route for the headline: clean render as background, text layer with outside stroke and shadows from references/text-overlay.md, export 1280x720 under 2 MB for YouTube.

## QA checklist

- [ ] Concept opens an information gap and is truthful to the video.
- [ ] One focal subject; reads in under a second at about 120px wide.
- [ ] Emotion is clear on the face and matches the promise.
- [ ] Identity matches the reference photo (compare side by side); no invented person.
- [ ] Lighting rig present on people; the grade is vivid unless a calm look was requested.
- [ ] No stray text or watermark unless text was ordered; ordered text matches the string exactly.
- [ ] Headline 2-4 words, off the face, inside the safe zone, high contrast.
- [ ] Ratio and delivery size correct (1280x720 / 1080x1920 / 1080x1350); YouTube file under 2 MB.
- [ ] Reference thumbnail was used for style only, not as a face source.

## References

- references/frameworks.md: read at step 2 to choose among the 16 frameworks, with when-to-use hints and the quick chooser.
- references/emotions-and-lighting.md: read at step 3 and 5 for the 11 emotions, camera takes, the lighting rig, the identity-lock sentence and subject-size/grade lines.
- references/prompt-blocks.md: read at step 5 and 8 for the 11 prompt blocks, defaults, split-frame contracts, surgical tweak prompts, the 3D logo prompt and the reference-analysis fields.
- references/text-overlay.md: read at step 6 for text hierarchy, safe zones, the 5 style presets, the font menu and the bake-vs-overlay routes.
