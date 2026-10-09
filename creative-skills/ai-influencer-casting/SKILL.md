---
name: ai-influencer-casting
description: "Designs an AI persona or AI influencer for a channel, an ad series or a recurring UGC creator: picks traits from a full taxonomy (tier, gender, age, build, hair, eyes, skin, head and face features, style, accessories), writes the two-panel casting-sheet prompt (close-up portrait + full-body standing shot on white) in the proven brief grammar, and gives a consistency procedure (reference set, what to lock, drift audit) so the same face and look survive across images and video. Includes all 39 example casting briefs grouped by tier and style. Use it whenever Mati wants a character that must look the same in many posts, even if he only says 'stwórz influencerkę', 'postać do kanału' or 'twarz marki'. Trigger on: AI influencer, persona, wirtualny influencer, postać AI, awatar, twarz kanału, maskotka, arkusz castingowy, casting postaci, spójna postać, ta sama twarz w każdym ujęciu, bohater serii, kreator do reklam, host kanału. Not for: story or animated characters with turnarounds (character-sheet-builder), the ad scripts themselves (ugc-video-scripts), a one-off portrait (photo-prompt-craft)."
---

# AI Influencer Casting

Designs one believable, reusable persona and freezes it so it can star in a whole channel or ad series. The output is a casting-sheet prompt you can run in Nano Banana Pro (or any image model), plus a persona bible and a drift-proof way to reuse the face in stills and video.

## When to use / when not

Use when: Mati needs a recurring AI host, creator or brand face for TikTok / Reels / YouTube Shorts or a UGC ad series; when he wants a distinctive mascot-like persona; when a UGC pack needs a locked creator (`ugc-video-scripts` calls for one); when faces drift between generations.

Route elsewhere:
- Fictional story characters, anime or 3D characters, turnarounds and expression sheets: `character-sheet-builder` (same slot architecture, more styles).
- The scripts, hooks and per-shot prompts for the ads the persona will star in: `ugc-video-scripts`.
- A single nice portrait with no continuity need: `photo-prompt-craft`. Thumbnails with a face: `thumbnail-design`.
- Editing an existing video to swap the person: `video-edit-prompting`.

Rules that always apply: original characters only (never a real person, celebrity or copyrighted character), adults only (adult, mature or senior reads), photoreal means unretouched, and an AI persona is never presented as a real customer with lived experience.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

Ask one bundled question for gaps:
1. Purpose: channel host, ad creator for a product category, mascot, or brand ambassador; platform and language; niche and audience.
2. Believability dial: believable everyday person (tier `normal`, default) or deliberately odd casting-photo character (tier `freak` or `total`, see the taxonomy).
3. Hard traits he cares about: gender, age band, ethnicity, build, height, hair, one signature feature. Anything he does not specify you choose, and say what you chose.
4. Style and wardrobe vibe: one of Retro, Sporty, Y2K, Theatre, Goth, Suits, Streetstyle, Casual (or a custom line).
5. How it will be used: stills only, or also video; with which tools; how many variants in the series.
6. Reference photos only if they are of an authorized person or his own earlier persona.
Defaults: tier normal, adult age, one signature feature, deadpan neutral expression on the sheet, pure white seamless background, bright soft light, two panels, 16:9 image.

## Workflow

1. **Define the role.** One sentence: who is this persona for, what does it sell or host, what must the audience feel (trust, curiosity, humour). The role picks the tier and the style.
2. **Select traits** from `references/trait-taxonomy.md`: tier first, then the silhouette keys (gender, age, build, height, ethnicity, skin tone, hair style and colour, eye shape and colour, facial hair), then at most 4 features, 2 distinctive features, 3 accessories, 2 proportions. Keep exaggeration low in `normal`; use the freak/total options only for a mascot-like character.
3. **Choose ONE signature.** The single loud feature the face or hair is built around (a towering pompadour, a checkerboard flat-top, a unibrow with ram-horn buns, a mega jaw, a colossal moustache). Everything else stays quiet. Two signatures compete, three is noise.
4. **Write the two-panel casting brief** with the grammar below, borrowing the nearest shape from `references/casting-briefs.md` (6 shapes, 39 examples). Outfit head to toe with materials and colours; background and light fixed; no text or logos.
5. **Generate 3-6 sheets**, pick the one whose face you could draw from memory. Reject sheets with a changed outfit between panels, a cropped body, a second person, text, or plastic skin.
6. **Freeze it** in the persona bible (`references/consistency-procedure.md` section 2): trait labels, face/hair/body lock sentences, wardrobe anchors, persona sentence, seed and tool.
7. **Build the reference set** from the sheet: frontal head, 3/4, profile, full body, plus expression and lighting variations (8-12 images if the tool trains an identity).
8. **Hand off to production.** Give `ugc-video-scripts` (or any shot prompt) the identity block and the persona sentence; every shot attaches the sheet or frontal reference first and describes ACTION only.
9. **Audit drift** after each batch and repair in order (references first, then shorter prompts, then new references), never by adding face adjectives.

## The two-panel casting brief grammar

Slots in this order (every source brief follows them; shape names refer to `references/casting-briefs.md`):

```
[GENRE LINE] [PANEL LAYOUT] [BACKGROUND AND LIGHT] [BUILD LINE] Signature: [ONE LOUD FEATURE]. [HAIR / CONTRAST CLAUSE.] [FEATURE CLAUSE: brows, nose, teeth, ears.] Outfit: [head to toe]. [TAIL]
```

Verbatim building blocks from the briefs:
- Genre line, believable variant (shape B with the odd wording removed; derived, check it reads as an ordinary person): `Fashion-editorial casting photo of a believable, photoreal person, contemporary [styling].`
- Genre line, odd variants (verbatim): `Classic eccentric 'freak' character, deadpan art-house casting photo; a believable real odd-looking person, understated, not a cartoon.` / `Fashion-editorial freak casting photo of an odd-looking but photoreal person, contemporary [goth/streetwear | y2k streetwear | club/streetwear | workwear/streetwear | motocross/streetwear | trendy 2026 runway] styling.` / `EXTREME hypertrophied 'freak' character, surreal but photoreal fashion-editorial casting photo, the signature feature is wildly exaggerated.` / `Extreme exaggerated anatomy, surreal but photoreal fashion portrait.`
- Panel layout (verbatim, fashion-editorial): `Two-panel sheet: left a tight frontal close-up portrait with the entire head and hair in frame, right a full-body standing shot; arms down, blank deadpan expression.` Classic version: `Two-panel character sheet: left half a tight head-and-shoulders portrait, right half a full-body standing shot, both front-facing, symmetrical, arms hanging straight down, blank deadpan expression.` Grey-studio version: `A two-panel photorealistic character sheet: LEFT panel, deadpan chest-up studio portrait; RIGHT panel, the exact same person full body, standing straight, arms at sides, head to toe.` ... `identical person and outfit in both panels.`
- Background and light (verbatim): `PURE WHITE seamless studio background (#FFFFFF) in both panels, no grey, no gradient, no vignette, soft even light, faint contact shadow under the feet.` / `PURE WHITE seamless background, bright soft light.` / `PURE WHITE seamless background (#FFFFFF), bright high-key soft light, soft floor shadow.` / `Both panels on a light grey seamless studio background, flat even lighting, fine film grain.`
- Build line (verbatim): `Slim, not overweight.` / `Not overweight.` / `Lanky slim build, not overweight.` / `Lean athletic build, not overweight.`
- Signature line: `Signature: [thick glossy black mushroom bowl cut, heavy black horseshoe moustache, metal braces on the teeth, hyper-muscular body].` Variant for characters: `THE CHARACTER: a short, round man around 60 with an impossibly TALL copper POMPADOUR rising thirty centimeters straight up like a loaf of bread, perfectly groomed...`
- Hair and contrast clause: `Hair: [colour, cut, finish].` / `Contrast: sleek long jet-black hair with a perfect center part.`
- Outfit (verbatim style): `Outfit: black leather vest over a black shirt with rolled sleeves, wide black leather belt, emerald-green velvet flared trousers, black leather gloves, black heeled boots.` Name materials, cut and colour for each piece; one detail per item.
- Restrictions: `No tattoos, no piercings.` (when unwanted) / `No text, no logos, no watermarks.`
- Tail (verbatim): `Hyper-realistic, natural uniform skin tone, crisp texture, sharp focus.` / `Hyper-realistic editorial photography, visible skin texture and fabric weave, 85mm lens, sharp focus.` / `Hyper-realistic high-end fashion photography, crisp skin texture, sharp focus.` / `Hyper-realistic, natural uniform skin tone across face and jaw, crisp texture, sharp focus.` For extreme jaws or heads, "natural uniform skin tone across face and jaw" prevents patchy colouring.

Why the grammar works: the sheet is a casting photo, not a mood shot, so expression is blank, light is flat, background is white and the body is standing with arms down; that removes everything that is not identity. The same two panels then become the reference for all later work.

Template to fill (believable persona, tier normal):

```
Fashion-editorial casting photo of a believable, photoreal [age band] [gender], contemporary [style] styling. Two-panel sheet: left a tight frontal close-up portrait with the entire head and hair in frame, right a full-body standing shot; both front-facing, arms down, calm neutral expression. PURE WHITE seamless background, bright soft light. [Build line.] [Height impression.] Signature: [one loud feature]. Hair: [colour, length, cut, finish]. [Skin tone and undertone; eye shape and colour; brows; facial hair; marks with positions.] Outfit: [top], [layer], [bottom], [shoes], [one metal family of jewelry], [one deliberate imperfection]. Hyper-realistic, natural uniform skin tone, visible skin texture with natural pores and subtle asymmetries, no beauty filter, no AI-airbrushed look, crisp texture, 85mm, sharp focus. Identical original person in both panels, exactly one person, no props, no text, no logos, no watermark; left panel close-up not full body, right panel standing full-body head-to-toe not cropped. Not resembling any real celebrity or existing character.
```
Odd-casting variant: swap the genre line and add the exaggerated features from the taxonomy, e.g. `Signature: extremely long thin neck, tall bleached-blonde flat-top haircut like a box.`

## Output format

````markdown
# Persona: [fictional name] | tier [normal|freak|total] | style [..] | role [..]

## 1. Trait selection
| Key | Choice (label) |
|---|---|
(gender, age, build, height, ethnicity, skin tone, hair style, hair colour, eye shape, eye colour, facial hair, features (<=4), distinctive (<=2), accessories (<=3), proportions (<=2), signature)

## 2. Casting sheet prompt (copy-paste)
```
[full two-panel brief]
```
Generation notes: ratio 16:9 (or 3:2), 3-6 candidates, selection criteria, reject list.

## 3. Persona bible
[template from references/consistency-procedure.md section 2, filled]

## 4. Identity kit for production
- Reference set to produce (names, angles)
- Identity block (paste at the top of every still prompt):
```
The same person as the reference image, identical face, hair, body and identity. Same outfit as the reference unless stated.
```
- Persona sentence (paste in every video prompt): [...]
- Negative tail: [...]

## 5. Wardrobe and episode variants (optional)
| Episode | Only change | Locked |
|---|---|---|

## 6. Drift audit checklist (filled with the 7 checks)
````

## Tool adapters

- **Nano Banana Pro:** generates the sheet (give the whole brief; exact words in quotes work, there is no text on the sheet so keep "no text"). Use the sheet as the first image input for all later stills; multiple reference inputs are supported. Good for identity-preserving edits; check hands and teeth.
- **KLING:** image-to-video from a still of the persona; prompt action and camera only; one subject; do not re-describe the face. Use the frontal head still as the start frame for talking shots.
- **Seedance 2:** accepts multiple reference images and EN/ZH prompts; attach the sheet or frontal reference plus the shot still; restate the persona sentence for voice/mannerisms.
- **Higgsfield (Soul ID-type training, Cinema Studio):** an identity-training tool takes 8-12 varied images and returns a reusable reference; Cinema Studio is fine for cinematic persona shots but the phone-UGC look is better served by flat iPhone-style prompts (see `ugc-video-scripts`).
- **Photoshop / Figma:** persona card (turnaround images, palette, wardrobe anchors), face crops, cleanup of a stray artifact on the reference image. Poor fit for creating the face itself.
- **Premiere + After Effects:** none for casting; use them only to check consistency across a cut (stack frames of the face and compare).

## QA checklist

- Original character: no resemblance to a real celebrity or existing property; adult read; no minors implied.
- Trait picks respect tier availability and maxima (features 4, accessories 3, proportions 2, distinctive 2); one signature only.
- Prompt order follows the grammar; the build line, background, light and "no text, no logos, no watermark" are present.
- Sheet check: two panels, same person and outfit in both, close-up not full body on the left, full standing body with both feet on the right, arms down, one person, white seamless background, no props, no text.
- Realism: visible pores, asymmetry, no glossy plastic skin, no beauty filter, natural uniform skin tone; no babyface on adults.
- Persona bible filled; seed and tool saved; reference set produced and shortlisted by face match.
- Production handoff: identity block + sheet reference in every still, action-only video prompts, persona sentence in every clip, disclosure of AI persona where the platform requires.
- Drift audit run on the first batch and fixed with references, not adjectives.

## References

- `references/trait-taxonomy.md`: read when selecting traits. Tiers, all 18 selection keys with the values observed in the 39 presets, full option catalog with tier availability, patterns.
- `references/casting-briefs.md`: read when writing the brief or looking for a style precedent. All 39 presets with selection and verbatim briefs, grouped by tier and style, plus the six brief shapes (13 presets have empty briefs in the source).
- `references/consistency-procedure.md`: read when freezing and reusing the persona. What to lock, bible template, reference set rules, still and video usage, realism module, drift audit, identity training.
