---
name: ugc-video-scripts
description: "Writes complete UGC ad packs in six formats (creator review, product-only voice-over, unboxing, try-on, tutorial, website tour): script skeleton, hook bank, shot list, creator persona and delivery notes, caption style, plus ready-to-paste per-shot prompts (image for the creator frame, video for talking and handling shots) for Nano Banana Pro + KLING / Seedance 2 / Higgsfield, or a shooting plan if Mati films it himself. Use it whenever the request is a short creator-style ad or product video, even if the word UGC is never said. Trigger on: UGC, reklama UGC, scenariusz UGC, skrypt do reklamy, recenzja produktu, unboxing, rozpakowanie, przymiarka, try-on, tutorial krok po kroku, jak używać produktu, film produktowy z lektorem, voiceover do produktu, prezentacja strony, website tour, hook, haczyk, pierwsze 3 sekundy, aktor AI, twórca do reklamy, napisy do reklamy. Not for: a faceless narrated video (use faceless-video-pipeline), a static ad (static-ad-creatives), designing the AI persona itself (ai-influencer-casting), Mati's own build-in-public reels (viral-reel-builder)."
---

# UGC Video Scripts

Turns a product (or a story, or a URL) into a ready-to-produce UGC ad: the words, the shots, the prompts. Most of the craft lives in `references/`; this file is the operating procedure.

## When to use / when not

Use when the deliverable is a short vertical creator-style video: a creator (generated or real) reviews, unboxes, tries on, teaches a product, tours a website, or a product is shown with an off-screen voice-over. Also use it to fix a weak hook, to write only the script, or to turn an existing idea into per-shot prompts.

Route elsewhere:
- Persona design for a channel or a recurring AI creator (traits, casting sheet, consistency): `ai-influencer-casting`, then come back here.
- Stills of a product only (packshot, hero): `product-shot-recipes`. A static ad with copy: `static-ad-creatives`.
- Faceless explainer, history, kids or story video: `faceless-video-pipeline`. Voice-over timing and TTS fitting: `narration-vo`.
- Detailed caption or title design beyond the UGC recipe: `caption-and-title-systems`.
- Concept stage ("which idea?") before any script: `concept-loop`. Mati's own personal-brand reels: `viral-reel-builder`.
- Changing an existing clip with a video-to-video model: `video-edit-prompting`.

Do not produce: testimonials that claim a generated creator really bought or used the product, impersonation of real people, political persuasion, or ads for restricted goods (the gate is in `references/formats.md`, section 0).

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

Ask ONE bundled question, only for real gaps:
1. Product: photo or URL, or "none" (productless story is allowed). Never ask for a product just to fill a field.
2. Format: one of the six (table below). Default review. A product URL alone does not make it a website tour.
3. Duration: offer 10s / 15s / 30s / 45s. Do not silently assume 15s. Minimum 4s.
4. Creator: an authorized photo, an existing persona (from `ai-influencer-casting`), or desired gender for a generated adult. If Mati will film himself, say so and switch to the self-shoot plan.
5. Optional overrides: `approved_claims` (exact allowed claim strings), language and accent, location, outfit register, mood, music, on-video text (subtitles / hook plate / both / none), tools he will use.
Defaults: 9:16, English spoken line with neutral American accent (lip-sync is most reliable in English; for Polish test first, see `references/shot-prompts.md` section 7), NATURAL register, no music, no baked text, neutral daylight, phone-camera look.

Classify specificity: `auto` (1-5 words, no scenario: you choose the whole treatment), `guided` (tone or rough flow: preserve it), `director` (shot list or scenario: map his beats one-to-one, adapt only physically unsafe actions).

## Workflow

1. **Gate.** Run the safety and truth gate (`references/formats.md` section 0). Generated creator = host or demonstrator, never a customer. Claims come only from `approved_claims`; with no list, write claim-free copy about observable mechanics. Product-present output is framed as a brand demo or sponsored creative.
2. **Pick the format.**

| Format | Use when | Persona on camera | Shots per ~15s clip |
|---|---|---|---|
| review | creator demonstrates a product or tells a story (default) | yes, talking | 8 |
| product | the product is the hero, no one talks to camera | optional, silent, hands-only | 4 |
| unboxing | a visible reveal and reaction is the point | yes | 4 |
| try-on | a wearable fit/texture demo | yes (6 talking, 2 macro VO) | 8 |
| tutorial | real usage steps with `Step N` labels | yes | 4 |
| website | the page itself must appear on screen | yes, continuous | 1 take per clip, cards composited |

3. **Normalize the product once** (`references/formats.md` section 0): category, usage and opening mechanic, hand-relative size in cm, mechanism anatomy, absent features, label treatment, one imperfection, tier, voice gender. Reuse this text verbatim in every prompt. Plan clip durations (minimum number of 4-15s clips).
4. **Lock the creator.** Write the creator frame prompt (`references/creator-persona.md`): clean person, no product, phone-selfie look, category gate, one bold anchor. Add ONE persona sentence (NATURAL tier by default) that you repeat verbatim in every shot prompt. For a recurring character use `ai-influencer-casting` and reuse its sheet as the reference. Generate once, inspect, then never regenerate mid-project.
5. **Write the script.** Word budget by clip length, one story shape with ONE "but then" twist, one hook pattern (H1-H8) or a tokenized hook (<= 8 words) for ad-style, product entering at 40-60% of runtime, CTA inside the closer. Run the anti-slop pass and the first-word rule (`references/hooks-and-captions.md`). Give each clip its own segment; later clips open mid-thought.
6. **Build the shot list** from the format skeleton (`references/formats.md`). Enforce the anti-morph rules: POV alternates, distance band rotates, a different action every shot, hands counted, frame one mid-event, 0.1s hook law.
7. **Write the prompts** (`references/shot-prompts.md`): one image prompt per shot (or one contact-sheet prompt per clip) and one video prompt per shot (or one multi-cut prompt per clip). Use exact hand roles, mechanism names, the quality tail and the negatives. Image first; inspect; only then video.
8. **Plan text.** Off by default. If opted in: caption look, hook plate (<= 6 words), safe zones, timing from the final audio. Tutorial: Step labels are mandatory (set them as editable layers in the edit).
9. **Assemble the pack** in the output format below and run the QA checklist. Include the post package (caption, 3-5 hashtags, pinned comment, loop note, ad disclosure) only when asked.

If Mati is filming himself, skip step 7's video prompts and give the shot list as a shooting plan using the "Self-shoot notes" of the format; keep the script, hooks and caption plan.

## Output format

Deliver one markdown pack with these fixed headings. Prompts go in fenced code blocks, never described.

````markdown
# UGC pack: [product or story] | [format] | [total s] | [language]

## 1. Brief
- Format / specificity tier / register (NATURAL | HYPED | CALM) / story shape / hook pattern
- Product block: [canonical product_description] | approved_claims: [exact strings or "none, claim-free"]
- Disclosure line: [brand demo / sponsored creative]

## 2. Creator
- Persona sentence (verbatim in every prompt): [...]
- Creator frame prompt:
```
[prompt from creator-persona.md structure]
```

## 3. Script
| Clip | Seconds | Words | Segment (verbatim) |
|---|---|---|---|
Hook: [line] | Pattern: [H#] | First word check: [ok]
Delivery notes: [pace, peak word, unguarded beat, closed-mouth beat]

## 4. Shot list
| # | Time | Role | POV | Distance (band) | Action (one) | Hands (each role) | Product state | Line / VO |
|---|---|---|---|---|---|---|---|---|

## 5. Prompts per shot
### Shot 1 (image)
```
[image prompt]
```
### Shot 1 (video)
```
[video prompt]
```
(repeat for every shot, or one contact-sheet prompt + one multi-cut prompt per clip)

## 6. Captions and text
- Look / safe zones / hook plate text / Step labels / timing source

## 7. Edit notes
- Assembly order, trims, card timings (website), audio, loop ending

## 8. Post package (only if requested)
````

## Tool adapters

- **Nano Banana Pro:** the creator frame and every shot still. Attach the creator frame (and the product photo) as image inputs and describe action, not appearance. Give any wanted text as exact strings in quotes, but keep step labels and captions for the edit unless a baked look is required. Good at text and at holding a product label from a reference photo; still check counts of hands and fingers.
- **KLING:** shot-by-shot image-to-video from the shot still. One subject, motion in plain action verbs, the camera move in its own sentence, no `Hard cut to.` (one shot per generation, you cut in the edit). Generate a little longer than the shot and trim.
- **Seedance 2:** accepts EN and ZH prompts and multiple reference images; the original recipe fed it a contact sheet + creator frame (+ product photo) and a multi-cut prompt with native speech. Use the multi-cut template for an 8- or 4-cut clip, or single shots. Check lip-sync zones.
- **Higgsfield Cinema Studio:** a poor fit for the phone-UGC look, which wants flat deep-focus iPhone realism; use it only if the brief explicitly asks for a cinematic UGC. Its general video models are fine for single shots with the same templates.
- **Premiere Pro + After Effects:** assembly, speed ramps, trims, hard cuts, Step labels, website cards (contain-fit 0.78W x 0.60H, shifted up 0.04H), subtitles from a transcript fixed against the script, hook plate, safe zones (top 10%, bottom ~17%, sides ~11%).
- **Figma / Photoshop / Illustrator:** label templates, card frames, text plates, covers. Not for the live shots.
- **Filming it yourself:** phone at arm's length for SELFIE beats, propped and locked for STATIC beats, window light from one side, record longer and cut to 1.5-2s beats, record voice-over separately for product-only.

## QA checklist

- Safety gate passed; creator is a generated or consenting adult; no testimonial or invented use, results, reviews or ratings; claims are exact allowlisted strings or absent.
- One format, one creator reference, one persona sentence repeated verbatim; creator image contains no product.
- Word counts inside budget (~2.4-2.7 words/s); the first word of every segment is hook content; no banned phrases; no greeting after clip 1; no phrase repeated across cuts.
- Frame one is mid-event; first word or sound lands within 0.4s; one peak with a body event; one unguarded beat; one closed-mouth beat per dense cut.
- Anti-morph holds: no two adjacent shots share both POV and distance band; every band appears at least twice in 8 shots; every shot has a different action.
- Hands: at most 2 roles per shot, each named; SELFIE shots have one free hand and one object; two-handed actions are STATIC; no phone visible; no mirrors or reflections.
- Product: exactly one instance, correct size in cm, one visible side, mechanism named, cap removed before use and never re-closed, body-part target correct, absent features stated and negated.
- Format-specific locks hold (box gone after the reveal; bag only in shot 1 and no costume change on screen; macros hand-free; Step numbering global; CTA only on the last clip; site cards real, contain-fit, no card on hook or closer).
- No baked text in generated frames; tail has the full negatives; look is iPhone UGC, neutral daylight, no golden hour.
- Captions: timing from the final audio, <= 5 words per cue, diacritics render, safe zones respected, face and labels clear.

## References

- `references/formats.md`: read first. Shared gates and intake, then per format: hard rules, shot lists with POV and distance, arcs, box/bag/macro/step/card logic, script skeleton, self-shoot notes.
- `references/hooks-and-captions.md`: read at the script stage and the caption stage. Word budgets, truth contract, persona archetypes, story shapes, hook patterns and bank (EN + PL adaptations), anti-slop lists, line banks, series mode, caption looks, hook plate, post package.
- `references/shot-prompts.md`: read at the prompt stage. Shot-by-shot vs multi-cut modes, anti-morph cadence, image and video templates, hand-count law, product mechanics and body-part tables, performance menus, hook devices, one-take moves, audio markup, negatives, troubleshooting.
- `references/creator-persona.md`: read when writing the creator frame. Rules, variety pools, wardrobe recipes, location matrix, lighting, camera phrasing and bans, closing block, worked examples.
