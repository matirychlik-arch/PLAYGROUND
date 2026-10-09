# Emotions, lighting rig, identity lock

Contents:
1. Emotion casting (11 presets, ladder, custom phrases)
2. Takes per emotion (camera variations) and variant math
3. The YouTube lighting rig (plain and colored-rim variants)
4. Identity lock (anti face-drift) and reference manifest
5. Subject size and grade
6. Drift handling and the 120px test

All prompt sentences below are meant to be pasted into the image prompt as written.

## 1. Emotion casting (11 presets)

**shock** (mouth open gasp, wide eyes), **hype** (ecstatic grin, blazing eyes), **fear** (terrified stare, frozen breath), **confusion** (one brow raised, puzzled), **determination** (locked jaw, laser focus), **smug** (knowing smirk), **charisma** (calm magnetic gaze, relaxed brows, faintest composed half-smile, charismatic leading-man poise, confident but never aggressive; the calm positive option, because "determination" alone reads too harsh), **disgust** (recoiling grimace), **awe** (jaw dropped, glittering wonder), **rage** (bared teeth fury), **laugh** (head back).

The emotion phrase used in Expression slots = the preset's PARENTHETICAL descriptor (shock
becomes `mouth open gasp, wide eyes`). A custom user phrase replaces the preset phrase
verbatim (`Expression: <custom>`).

When the user gives an emotion COUNT without naming them, take the first N of this ladder:

shock, hype, rage, awe, laugh, fear, smug, charisma, confusion, determination, disgust

The default emotion is `shock` when a person is in frame. With no person in frame the Expression
axis is empty and variants = takes. When offering emotion choices interactively, always include
an Other/custom option.

If a reference thumbnail is analysed, its own emotion can add one vivid `emotion_detail`
sentence (eyes, brows, mouth, head angle) on the variant that uses the reference's emotion only.
Variants with a different emotion use the preset parenthetical alone.

Expression slot grammar, one per subject, always last in the subject's prose:

```
Expression: <emotion phrase>.
```

## 2. Takes per emotion (camera variations)

Take 1 = designed framing (no modifier). Takes 2-4 append one line each:

- `ALTERNATE TAKE: reframe as a low-angle hero shot — camera below eye level looking up, the subject towering with extra dominance, background perspective stretching upward, same scene and lighting.`
- `ALTERNATE TAKE: extreme close-up punch-in — the face and expression dominate more than half the frame, background compressed into soft bokeh context, same scene and lighting.`
- `ALTERNATE TAKE: wider dynamic shot with a subtle dutch tilt — more of the environment visible, subject anchored off-center on a power third, stronger motion energy sweeping the frame, same scene and lighting.`

Total variants = emotions x takes, hard cap 16. Variants differ ONLY by the Expression phrase
and/or one ALTERNATE TAKE line, so each needs its own prompt (render one variant per
generation, never a batch count that shares one prompt).

## 3. The YouTube lighting rig (mandatory on people)

Plain rig (the default):

> signature YouTube thumbnail lighting rig on the subject — a strong KEY LIGHT sculpting the face with crisp highlights and controlled falloff, a soft dreamy DREAM LIGHT fill lifting the shadows with a subtle cinematic glow, and a defined BACK LIGHT + HAIR LIGHT tracing a clean bright rim along the hair, shoulders and silhouette, separating the subject sharply from the background.

Colored rim variant (use ONLY when the user names a rim color): replace the last clause with

> a defined <color> BACK LIGHT + HAIR LIGHT tracing a vivid colored rim ... with a subtle matching glow.

Rim palette:

| Name | Hex | Words to use in the prompt |
|---|---|---|
| Ice Blue | `#4DA6FF` | "electric ice-blue" |
| Neon Magenta | `#FF3DBE` | "hot neon magenta" |
| Toxic Lime | `#C8FF2E` | "toxic neon lime" |
| Amber Gold | `#FFB63D` | "warm amber-gold" |
| Pure White | `#FFFFFF` | "pure white" |

Key and fill NEVER change color; only the back light and hair light do. Keeping the face
light neutral protects skin tone and identity.

Drop the rig for non-photoreal concepts (Graphical Representation, illustrated or collage
mediums) and make it optional for Landscape where the subject is tiny.

## 4. Identity lock (anti face-drift, required per photo-referenced person)

Soft phrasing ("keep face and identity exact") is NOT enough; models drift. For every
character with a face photo, emit this block:

> CHARACTER N: the person from attached face reference #K — IDENTITY LOCK: reproduce this exact person with a photographic identity match — same bone structure, eye shape, nose, lips, jawline, skin tone, hairline and hair texture as the reference photo. Do NOT beautify, do NOT average with other faces, do NOT restyle the face; it must be recognizably the same person at a glance. Expression: `<emotion phrase>`.

Rules around it:
- Up to 3 characters; photo characters map positionally onto the attached face references (image 1 = CHARACTER 1, image 2 = CHARACTER 2, and so on).
- A supplied face photo or character image is ALWAYS attached and locked. Never invent or substitute a new person when one was supplied.
- If the concept contains a person and no face photo exists, ask once: yourself / a specific person (send a photo) / a generated person / people-free. A generated person is an explicit choice, never a silent default. Never invent a specific identity.
- Text-described people or creatures (no photo) are described in prose in the subject block and their prose ALSO ends with `Expression: <emotion phrase>`.
- A style-reference thumbnail is analysed by eye only. It is never attached as an image to the generator and never a face source; it shapes the prompt through extracted fields.
- With 2 or more attached images, the FIRST prompt line is the manifest:

```
IMAGE REFERENCES: image 1 = CHARACTER 1 face reference; image 2 = brand logo.
```

  Order: faces first in CHARACTER order, then the logo.
- For a non-photoreal medium, translate recurring characters into that medium while preserving exact design, silhouette, wardrobe, colors and facial identifiers. Do not turn illustrated references into photoreal faces.

## 5. Subject size and grade

Subject block rule: **Render the subject LARGE and dominant — the clear hero, filling roughly 40-60% of the frame, chest-up or medium-close, pushed to the foreground and cleanly separated from the background; NEVER a small subject stuck in the lower third, never a distant video-frame look.** End the subject block with `All faces crisply sharp as the anchors of the shot.`

Default composition line: `the subject rendered LARGE and dominant — chest-up / medium-close, filling ~40–60% of the frame, pushed to the foreground on a power third, camera at eye level, strong separation from the background so the subject pops, shallow depth with a foreground accent element`

Grade line (always last in the prompt on photoreal people shots):

> vivid high-impact color grade, punchy high contrast, bright clean exposure, rich saturated colors that pop off the screen, deep blacks and bright highlights, crisp and glossy, poster-punchy, cohesive as one image. <ratio>.

Dial back to a restrained / soft / low-contrast grade ONLY on an explicit calm / premium / muted / aesthetic request.

## 6. Drift handling and the 120px test

- Faces drift occasionally even with the identity lock (stochastic). Inspect every render against the face reference before showing it. The fix is a re-render of the same prompt (max 2 retries per variant), not an apology; if it still fails, say so honestly.
- Final readability test: a thumbnail competes at about 120px wide in a sidebar. The emotion and the hero element must still read at that size. If they do not, the composition (not the resolution) is wrong: enlarge the subject, simplify the background, push the expression.
