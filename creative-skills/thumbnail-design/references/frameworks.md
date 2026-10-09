# Thumbnail frameworks: the concept layer

Contents:
1. Principles (information gap, combining, truthfulness law)
2. The 16 frameworks, each with when to use it and how to realize it
3. Quick chooser (topic type to framework)
4. The 10 rules cheat-sheet

This is the "what to depict" layer; prompt-blocks.md is "how to render it".
Pick the framework(s) first, then assemble the prompt.

## 1. Principles

Every thumbnail must open an **information gap**: the image raises a question the title /
video answers. Before writing any prompt, brainstorm **at least 5 concept options** across the
frameworks below and carry the strongest into the prompt blocks; a concept often **combines 2+
frameworks** (e.g. Posed Portrait + Map + Landscape) when it deepens the gap without clutter.

**Truthfulness law:** the image may exaggerate but must honestly represent the video. A
Social-UI / News-Clip / amplification that misrepresents the video breaks viewer trust;
keep any baked text short and true.

Most frameworks map straight onto the prompt blocks (see prompt-blocks.md); the ones needing
readable in-image text use the **BAKED UI** clause in the Text contract (block 3) and stay
brand-generic (no real logos / networks).

## 2. The 16 frameworks

Each entry: **Realize it with** is the original wording, kept verbatim. **When to use** is a
selection hint added for choosing quickly.

### 1. Before/After Transformation
- When to use: the video is about change over time (fitness, glow-up, renovation, learning a skill, a rebuilt project).
- Realize it with: Split frames `before/after` mode, with maximum contrast between the two states of one subject.

### 2. Social UI (tweet / DM / review)
- When to use: the video reacts to, answers, or is triggered by something someone said online (a comment, a hate DM, a review).
- Realize it with: KEY ELEMENTS = a **generic** chat bubble / DM row / star-review card beside the subject; short message via BAKED UI; NO real platform brand.

### 3. Three-Step Progression
- When to use: a journey with a clear start, middle and end (day 1 / day 30 / day 100, rough sketch / draft / final).
- Realize it with: Split frames plain/custom, 3 vertical panels: start, then mid story-beat, then end; optional per-panel number/Day badge.

### 4. Compelling Screenshot
- When to use: the video already contains a striking frame (a reveal, a reaction, a stunt) and you have the source clip.
- Realize it with: NOT a generation. Use a real frame from the source video, or a Posed Action Shot that matches the video's first frame. Flag when the user has a source clip.

### 5. Posed Portrait
- When to use: the default for personality-led channels, reactions, opinions, any face-first video; the safe starting point when nothing else fits.
- Realize it with: SUBJECT rendered LARGE (fills much of the frame) + Identity Lock + YouTube rig + Emotion; very little or nothing in the background. The subject IS the focus.

### 6. Posed Action Shot
- When to use: the video has one intriguing physical moment (about to jump, holding a strange object, mid-experiment).
- Realize it with: Scene brief = one intriguing action mid-moment; COMPOSITION uncrowded, single hero action.

### 7. Highlighting a Specific Day
- When to use: challenge / time-based series ("Day 87") where the chosen day is the hook.
- Realize it with: Any framework + a big `DAY N` badge (BAKED UI); pick a day in the last ~20% of the arc.

### 8. Graphical Representation
- When to use: abstract or data topics (statistics, curves, concepts, money, algorithms) that a photo cannot show.
- Realize it with: Non-photoreal: REPLACE the Frame contract with a clean diagram/graphic brief (bell curve, simple familiar chart); drop the photoreal + lighting-rig blocks.

### 9. Landscape
- When to use: travel, places, nature, survival, a destination is the star.
- Realize it with: Environment is the hero; keep ONE small subject on a power third; lighting rig optional.

### 10. Map/Aerial
- When to use: geography, routes, distance, "I walked/drove from A to B", location mysteries.
- Realize it with: Frame = a map or aerial photo; KEY ELEMENTS = a highlighted route / point (circle, arrow, label via BAKED UI).

### 11. Product
- When to use: reviews, unboxings, comparisons, "is it worth it" videos about a physical or digital product.
- Realize it with: Product is the SUBJECT (hero, sharp, its own label exempt from the no-text rule); open the gap by making the product the answer to the title's question.

### 12. Adding Text
- When to use: the image alone does not raise the question; a short word or phrase must complete the gap.
- Realize it with: Text policy overlay (default) or baked TEXT; use it as a callout (arrow + word) or as the continuation / answer to the title's question.

### 13. Repetition of Objects
- When to use: quantity is the story ("1000 pencils", "100 layers", "50 phones").
- Realize it with: KEY ELEMENTS = a large quantity of ONE object filling the frame, still legible; add one context element + a subject for scale.

### 14. Size Difference
- When to use: giant vs tiny is the hook (world's biggest, tiny house, massive vs minimal).
- Realize it with: COMPOSITION = extreme scale contrast between two elements central to the story (giant vs tiny).

### 15. News Clip
- When to use: a "breaking", "exposed", "it happened" tone, current-events or drama framing.
- Realize it with: Generic "breaking news" lower-third / chyron over the image (BAKED UI, short truthful line); generic broadcaster styling, NO real network.

### 16. Amplified Reality
- When to use: a real element of the story is already dramatic and can be pushed one notch further.
- Realize it with: Posed Action Shot + exaggerate ONE real element from the story (KEY ELEMENTS oversized); keep it plausible, because over-amplification kills trust.

Frameworks 1, 5, 12 are already the skill's defaults; the rest are selected here and realized
through the existing prompt blocks. Do not invent a parallel renderer.

## 3. Quick chooser

| Video is about | Start with | Often combine with |
|---|---|---|
| A person's reaction or opinion | 5 Posed Portrait | 12 Adding Text |
| A challenge or time-based series | 7 Highlighting a Specific Day | 3 Three-Step Progression, 1 Before/After |
| A transformation | 1 Before/After | 3 Three-Step Progression |
| A product or gear | 11 Product | 14 Size Difference, 13 Repetition |
| A place, trip or route | 9 Landscape | 10 Map/Aerial, 5 Posed Portrait |
| Money, stats, concepts | 8 Graphical Representation | 12 Adding Text |
| Drama, exposure, callout | 15 News Clip | 2 Social UI, 16 Amplified Reality |
| A stunt or experiment | 6 Posed Action Shot | 16 Amplified Reality |
| "Biggest / most / how many" | 14 Size Difference | 13 Repetition of Objects |

## 4. The 10 rules cheat-sheet (why these work)

The frameworks are vehicles for the underlying rules. Apply them regardless of framework:
one clear focal subject, a strong information gap, high contrast and readability at ~120px,
emotion or intrigue on any face, no clutter, truthful to the video, and a concept that reads
in under a second in a crowded feed.
