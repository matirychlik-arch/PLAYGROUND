# Variant matrix: one source ad to N versions

Contents:
1. Counting rules (N = final videos)
2. The variant table
3. Shared vs per-output content
4. Matrix patterns (product, cast, market, background, text)
5. Stand-in people when no reference photo exists
6. Run order, retries, QC and report

Source note: sections 1, 3, 5 and 6 come from a production multi-variant ad workflow (counting, zipping, retry and ordering rules, and the stand-in person image procedure), generalized to any video-to-video tool. Sections 2 and 4 are templates added for planning.

## 1. Counting rules

- Upload and analyze the source once. Reuse that analysis for every output.
- `N` always counts final videos. It never counts people, assets, operations or takes.
- Ordered lists pair by output position: output 1 gets item 1 of every list, output 2 gets item 2, and so on (zip). Never build a Cartesian product (3 products x 4 backgrounds = 12) unless the user lists the 12 pairs explicitly. If the user describes a product of lists, restate it as a numbered pair list and ask for one confirmation.
- Shared assets and instructions may repeat across outputs (the same background in every version, the same preserve block).
- Output order is the order of the user's list, from planning through prompts, generation, QC and delivery.
- If each of N outputs replaces two people and neither has a reference, you need 2N distinct replacement people, two per output.
- One output may contain several simultaneous edits; that is still one video.
- Do not create a persistent registry of variants beyond the table below; the table is the plan.
- Resolve every user-dependent choice during planning. A finished prompt states one resolved edit and contains no alternatives.

## 2. The variant table

Fill one row per final video before writing any prompt. Ask one bundled question for every empty cell.

| # | Operation(s) | Target in source (anchor + range) | Replacement (reference or words) | Clothing override | Text edit | Output name |
|---|---|---|---|---|---|---|
| 1 | Replace product | the can in the woman's hand, 0-12 s | @Image1 olive-oil bottle | none | none | pl_oil_v1 |
| 2 | Replace product | the can in the woman's hand, 0-12 s | @Image2 balsamic bottle | none | none | pl_balsamic_v2 |
| 3 | Replace product + modify text | the can in the woman's hand, 0-12 s; price tag at 8-12 s | @Image3 vinegar bottle | none | "9,99 zl" | pl_vinegar_v3 |

Rules for the table:
- Target = analysis description plus one unique plain-language anchor plus the visible range. An `add` uses a caption-grounded placement and timing instead.
- A person identity replacement is global across that person's appearances. If the user asks for a partial person replacement, offer two choices: a full identity replacement, or a non-identity attribute edit (hair, clothing, expression).
- Resolve appearance authority per person: default complete look; record a clothing override only for a separately mapped garment or outfit image, or an explicit user clothing instruction. Source wardrobe inferred from the video is never an override.

## 3. Shared vs per-output content

| Shared (write once, paste into every prompt) | Per output |
|---|---|
| The source-text preservation block | Replacement reference and alias |
| The "keep shots, camera, lighting, timing" sentence | The operation sentence(s) and the timing ranges |
| The lock/avoid wording | The person exclusion sentence (names the target and alias) |
| Resolution, aspect, duration (= ceil of source seconds) | The output name |

## 4. Matrix patterns

| Pattern | What varies | What is locked | Typical risk |
|---|---|---|---|
| Product versions (flavors, colors, SKUs) | The product image | Hand pose, framing, label position, text overlays | Label text drifts; keep one close-up frame in the source and verify it |
| Cast versions | The person image (complete look) | Choreography, blocking, camera, lines | Source person leaking in cuts and reflections; use the exclusion sentence |
| Background / location versions | Location image per segment | People, product, timing | Lighting mismatch; name the light direction in the operation |
| Text versions (offer, price, headline) | The quoted new text | Typography, placement, animation, timing | Neighboring captions changing; keep the preserve block |
| Market versions (language + cast + setting) | Everything | Beat order, timing, pacing | This is a recreate job, not an edit: see recreate.md |
| Seasonal / audience versions | Clothing, background, props | People, motion | Over-editing; list exactly which props change |

Hook/CTA variants: keep the body; change only the hook or CTA (recreate.md section 5), then generate N hooks and join each to the same body.

## 5. Stand-in people when no reference photo exists

Use only for a requested adult human replacement that has no user image. Not for animals, creatures, robots, products, objects, backgrounds, removals, attributes, text edits, children or teens. For a source person under 20, require a user reference or explicit consent to recast the role as an adult.

Use an image model that follows long prompts and renders realistic people (Nano Banana Pro works). One image per missing person, one at a time, vertical 3:4 at 2K, no reference image.

1. Build a positive two-axis contrast plan against that slot's source person. Every generated replacement must have both: a clearly different apparent racial/ethnic casting presentation (a fictional visual casting descriptor, not a claim about a real person) and a different hairstyle, including length, texture and shape. The reason: identity-carrying cues from the source person must not survive into the replacement. Do not force a different body type, body proportions, face shape or facial geometry; those come naturally from the image. Stature or build is carried only if the user supplied it or the analysis states it unambiguously, and it never gates anything. Generated people in the same request set must also look visibly distinct from one another. Words such as "different" or "contrasting" without explicit positive traits do not satisfy the plan.
2. Write each image prompt as one cohesive 140 to 190 word natural-language paragraph, not a tag list or a semicolon checklist. Resolve every field before writing; never leave bracketed placeholders or slash-separated alternatives. The replacement must be strikingly beautiful, handsome or otherwise conventionally attractive. Use the matching phrase for the requested presentation: `strikingly beautiful`, `strikingly handsome` or `conventionally attractive`. Include these four anchors or close positive paraphrases in fluent prose: `with high model facial features`, `symmetrical features`, `well-proportioned figure`, `natural skin texture`. Never default an unspecified presentation to the example's woman; resolve it from the request and the source mapping or ask. Beauty and realism are quality floors, not extra contrast axes.
3. Paragraph order:
   1. Subject and pose: a straight-on, eye-level, full-body portrait of exactly one adult age 20+; the positive casting traits, skin tone, hairstyle length/texture/shape, facial quality, posture, expression and direct camera gaze. Describe the casting presentation through concrete visible traits. Never mention the source person's traits in this prompt.
   2. Wardrobe: a complete stylish, period-appropriate outfit from top through footwear, in opaque, well-structured fabrics with at most two restrained accessories. The whole outfit and both feet visible.
   3. Studio and composition: the subject alone against a seamless matte-white studio backdrop whose white floor blends into the wall; the figure centered in balanced vertical framing with generous negative space; no props, furniture, text, logos or clutter.
   4. Lighting and palette: soft, evenly diffused high-key natural studio lighting, gentle grounded shadows, controlled highlights, no harsh contrast or overexposure; a restrained outfit-led palette.
   5. Capture and finish: a professional high-resolution digital camera, deep depth of field, ample dynamic range, minimal noise, razor-sharp head-to-toe focus; close with authentic skin detail, realistic human anatomy, natural hands and limbs, no plastic retouching, distortion or exaggerated traits, and a crisp modern editorial mood.
4. For several missing people, vary the concrete pose, outfit silhouette, accessories, palette accents and both casting axes while keeping the same studio and camera quality standard.
5. Worked example (prose form only; rebuild every subject detail from the slot's own plan, do not copy this woman, age, casting, hair, skin tone or wardrobe):

```text
A straight-on, eye-level full-body portrait features a strikingly beautiful 24-year-old Afro-Caribbean woman with supermodel facial features, symmetrical features, a well-proportioned figure, warm deep-brown skin with natural texture, and long dark softly waved hair. She stands poised with shoulders back, one foot angled outward, arms relaxed, and a direct camera gaze. She wears a structured matte-black blazer, opaque high-neck top, tailored wide-leg trousers, pointed-toe heels, thin gold chain, and small stud earrings. Her complete outfit and both feet are visible. A seamless matte-white studio backdrop and matching floor contain no props, furniture, text, logos, or clutter, leaving generous negative space around her centered figure. Soft, evenly diffused high-key natural studio lighting creates gentle grounded shadows, authentic skin detail, and controlled highlights without harsh contrast or overexposure. A crisp black, white, and subtle gold palette supports the modern fashion-editorial mood. Captured on a professional high-resolution digital camera with balanced vertical framing, deep depth of field, ample dynamic range, minimal noise, and razor-sharp focus from face to footwear, the image preserves realistic anatomy, natural hands and limbs, and a photogenic unretouched editorial finish without distortion or exaggerated traits.
```

6. Inspect each result against its source profile, the contrast plan and the quality gate. Regenerate a named position once if either required axis is unchanged, vague or missing, or if the person is not attractive, photogenic, natural-looking and anatomically realistic. Never offer a failed candidate for approval.
7. Show the candidates to the user and continue only after approval; regenerate named people or stop as asked.
8. After approval, keep the image and the approved two-axis profile. The image becomes a normal positional reference (`@Image(K+1)` after the user's K own images). The profile is copied into the manifest as `replacement_casting_profile` and into both the reference declaration and the render instruction of the DETAILED prompt.

## 6. Run order, retries, QC and report

- Submit outputs one at a time in order. Send the source video first, then every image reference in the same order as the manifest and the prompt.
- Retry only a rejected or terminally failed position, once, with the same approved identity and scope. Never retry a pending position or duplicate it.
- Continue with independent successes; report every failure with its output number.
- After each render, run finishing-and-qc.md (audio restoration, exact duration, aspect, resolution) before calling an output done.
- Report: completed/total, selected resolution, exact source duration, whether source audio was restored or the source was silent, concise failure and pending counts. Deliver outputs in the original order labeled `Output 1`, `Output 2`, and so on. Do not hand over prompts, manifests, intermediate stand-in images or raw silent renders as deliverables unless asked.

Failure boundaries:

| Failure | Response |
|---|---|
| Source outside the tool's length range | Stop; report measured length and range |
| Analysis unusable twice | Stop before generating |
| Ambiguous mapping (target, range, reference, list assignment) | Ask one bundled mapping question |
| A stand-in person image fails twice | Fail each dependent output or stop |
| User rejects a stand-in person | Regenerate the named person or stop |
| Prompt fails validation twice | Fail only that output |
| One position fails after its retry | Report it; keep the others |
| Source is silent | Produce a silent verified final |
| Audible source but audio extraction fails | Do not deliver a silent substitute |
