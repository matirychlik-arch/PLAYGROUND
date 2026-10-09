---
name: product-shot-recipes
description: Turns a product photo plus an intent into a ready-to-paste image or video prompt from a library of 63 recipes (Visible effect / Preserve / Parameters / Master prompt), with strict identity preservation of label text, logo and proportions. Use whenever the user has a product photo or description and wants a packshot, hero shot, lifestyle scene, splash or floating FX still, social card, benefit or spec card, carousel, banner, pin, ad pack, model try-on, restyle, or a short product video (push-in, spin, whip-pan, light sweep), even if they never say "recipe"; also to write a new recipe. Trigger on - packshot, zdjęcie produktowe, hero shot, sesja produktowa, reklama produktu, prompt do zdjęcia produktu, wideo produktowe, najazd kamery, obrót produktu, karta social media, karuzela, baner, zachowaj etykietę, nie zmieniaj logo. For general lighting, lens and negative-prompt craft use photo-prompt-craft; for multi-shot video scripts use cinematic-prompt-builder.
---

# Product Shot Recipes

Turn one product photo and one intent into a single ready-to-paste prompt (image, or start frame plus video) that keeps the product exactly as photographed. The craft lives in two places: a recipe grammar that says what the picture should show and what must not change, and a set of identity rules that stop the generator from redesigning labels, logos and proportions.

## When to use / when not

Use when:
- There is a product photo (or a precise product description) and the user wants a finished image or short clip around it.
- The user names a look ("na białym tle", "z wodą", "w dłoni", "karta z 3 powodami", "powolny najazd") that matches a recipe.
- The user wants a deliverable type (banner, Pinterest pin, carousel, ad pack, model try-on, restyle) from the formats reference.
- The user wants a new reusable recipe.

Do not use when:
- The request is general photographic prompt writing or a critique of a generated image with no product to preserve: use photo-prompt-craft.
- The request is a multi-shot cinematic video script or a branded key visual with brand system rules: use cinematic-prompt-builder or the brand-specific skill.
- The user needs regulated listing images (marketplace compliance sets, A+ content with legal claims): recipes here deliberately avoid claims, so they will not produce those.
- The product has no reference and no description. Ask for one; do not invent the product.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

1. Product photo or detailed description (shape, material, colors, label text, logo position). Required.
2. Intent: the look or deliverable (recipe id, format, or plain words). If missing, default to `hero-shot` for a still and `push-in` for a clip.
3. Image or video. Default image; a request for motion, "wideo", "ruch kamery" means video.
4. Aspect ratio. Default 3:4 (recipe default). Square 1:1, landscape 16:9, full-screen Reel or Story 9:16, feed post 4:5.
5. Exact on-image text, only if wanted, with the language and spelling. Default: no text beyond what is printed on the product.
6. Target tool (Nano Banana Pro, KLING, Seedance 2, Cinema Studio). Default: tool-neutral output with a note per tool.
7. Brand colors or mood. Default: derive from the packaging.

Ask at most three short questions in one message, and only when a missing item changes the result. Never ask about resolution, model, lens or negatives; those are craft decisions made here.

## Workflow

1. Parse the brief. Resolve image or video, ratio, text, tool. Look at the photo: note label text, logo position, closure, finish, number of units, any tilt or elevated camera angle.
2. Pick the recipe with the table below. Platform or deliverable beats environment (a pin request is a pin, even if it shows a kitchen). If two recipes fit, prefer the more specific one. Offer at most two alternatives in one line.
3. Open `references/recipe-library.md`, find the recipe by id, and copy its master prompt verbatim. For a deliverable type (banner, pin, carousel, ad pack, try-on, conceptual, restyle) use `references/formats.md` skeletons instead.
4. Adapt it with the rules in "Adapting a master prompt". Edit only the allowed slots.
5. Append or confirm the identity block (below). Master prompts already contain a version of it; add the extra sentences that match this product (readable label, people in frame, tilted reference).
6. For video: first output the start-frame prompt (shared, in the library), then the video master prompt. A clip generated from the raw photo drifts; the isolated, centered start frame is what keeps motion on-model.
7. Deliver using the output template. State the one-line reason for the recipe choice and the identity check the user should do on the result.

### Choosing a recipe

| User wants | Recipe ids |
|---|---|
| Clean advertising still, default | hero-shot |
| Store or marketplace image, truthful color | minimalist-white |
| Premium, glow, soft reflections | luxury |
| Campaign key visual with room for headline | signature-frame |
| Powerful low angle | power-angle |
| Monumental scale | pedestal-shot |
| Centered mirrored composition | symmetry |
| Several angles in one sheet | angles |
| Stack, set, shelf | retail-stack, bundle, shelf-ready |
| In a hand, on a desk, kitchen, gym, travel, weekend | in-hand, on-desk, kitchen-scene, gym-bag, travel-pack, weekend-carry |
| Overhead arrangement, opening a box | flatlay, unboxing |
| Colored shapes, fabric, ice, water, powder FX | color-pop, fabric-wave, ice-capsule, water-splash, powder-cloud |
| Carousel opener, Reel cover, vertical hook, shareable, tip, launch, moodboard | swipe-opener, reel-cover, vertical-hook, share-card, saveable-tip, new-drop, moodboard |
| Benefits, specs, reasons, steps, usage, care, contents, myth, problem-solution | benefits, main-benefit, three-reasons, specs, feature-zoom, how-it-works, quick-steps, usage-guide, care-guide, product-match, whats-inside, inside-pack, myth-fact, before-after |
| Camera move video | push-in, pull-back, crane-reveal, topdown-dive, whip-pan, macro-glide, texture-track, detail-scan, label-trace |
| Product rotation video | half-turn, product-spin, floating-roll |
| FX video | light-sweep, sunrise-pass, shadow-motion, impact, liquid-wrap, paint-wave |
| Banner, pin, carousel, ad pack, model try-on, surreal, restyle | formats.md sections 5, 4, 6, 7, 8, 9, 10 |

Text-heavy recipes (groups D and E in the library) are the riskiest for invented claims. If the user needs exact copy, prefer generating the visual without words and setting the type yourself in Figma, Photoshop or After Effects; see Tool adapters.

## Adapting a master prompt

Think of a master prompt as three layers: an opening that declares the supplied image the authoritative reference, a middle that describes the effect, and a tail that preserves identity and forbids additions. Edit the middle; leave the opening and tail intact.

Allowed edits (write them as short additions or word swaps):
- Surface, backdrop tone, palette: "whose tone complements the product's palette" can become "warm sand seamless paper", or colors taken from the packaging.
- Setting detail inside the recipe's concept: which kitchen counter, which desk, what time of day.
- Count and arrangement where the recipe allows it: how many views in `angles`, how many labels in `benefits` (the recipe caps it at four).
- Camera direction and speed in video: left-to-right, slower, hold at the end for one second.
- Aspect ratio and the safe zones that follow from it (9:16 leaves top and bottom clear for interface).
- Exact on-image strings, only if the user supplied them, in quotes, in the original language, in a recipe that has room for text.

Forbidden edits (these are what keep the product on-model):
- Deleting or softening any sentence that begins "Preserve the exact product identity..." or "Do not ...".
- Replacing "the supplied image as the authoritative product reference" with a text description when a photo exists.
- Adding words, claims, prices, certifications, QR codes or URLs the user did not supply.
- Asking the effect to cover, wrap, tilt or crop the label face or logo.
- Merging two recipes in one prompt. One recipe, one effect; chain outputs instead (a still from `hero-shot` can be the reference for a video).

If the photo was taken from a tilted or elevated angle, keep the master prompt's sentence that tells the generator to straighten the product; many recipes already carry it. If a recipe lacks it and the photo is tilted, add: "If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot."

No reference image available (text-only product): replace "the supplied image" with a "Product description" paragraph (shape, material, colors, closure, exact label wording, logo position) and warn the user that identity will be weaker. Do not claim the label will be exact.

## Identity preservation rules

This is the core craft. Generators redraw products from memory unless told, in plain words, what must not move. Treat every item below as part of the prompt.

Identity block (paste or confirm in every prompt, image or video):

```text
Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text; reproduce every printed element, including stickers, fine print, and secondary marks, exactly as in the reference; never invent, translate, or substitute words or characters, and keep unreadable glyphs as faithful shapes. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products.
```

Video addition (every frame, not only the first):

```text
Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product.
```

Rules and why:
- Label text: copy, never translate. Polish diacritics (ą ć ę ł ń ó ś ź ż) and non-Latin glyphs are the first thing generators damage; call them out in your message to the user as the check to do at 100% zoom.
- Small print: if a line is unreadable in the photo, say "keep unreadable glyphs as faithful shapes". Otherwise the generator invents plausible words, which is worse than blur.
- Logo: fix its position and size relative to the pack ("logo placement"), and keep it on a face that stays visible to camera. Effects (splash, powder, paint, fabric, liquid) must flow around the label, never over it.
- Proportions and silhouette: never stretch to fit the ratio. Change the canvas, not the product. Keep height-to-width, cap size, handle shape, corner radii.
- Materials and colors: name the material in the effect ("matte", "glass", "foil") so reflections follow real geometry; take FX colors from the packaging so the product does not clash with its own scene.
- Unit count: one product stays one product; a set stays the same number of units. Say "identical units" for stacks.
- Unseen sides: generators must infer back and side faces in angles, spins and half-turns. Tell them to infer conservatively and keep design continuity; never fabricate barcodes or regulatory text.
- Claims: no health, performance, comparative or numeric claims unless printed on the product. This is why the text recipes cap labels and forbid slogans.
- People and hands: natural anatomy, unobstructed label, believable scale.
- Straight, level product: reference photos are often taken from above or tilted; do not inherit that viewpoint.

Verify every result before delivering (see QA checklist). When a label still comes out wrong after two attempts, stop re-rolling: generate the scene with the label face turned slightly away or small in frame, then composite the real label or the untouched original packshot onto it in Photoshop or After Effects.

## Writing a new recipe in the same grammar

Use this when no existing recipe fits and the effect will be reused. A recipe has four fields and nothing else.

```text
id: kebab-case-name
Visible effect: one sentence a client could say out loud ("Water forming a crown around the product.")
Preserve: image  -> Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
          video  -> Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
Output type: image | video     Aspect ratio: 3:4 default     Parameters: image 2K high quality; video 6 s, 1080p, silent
Master prompt: opening + effect + tail
```

Master prompt anatomy, in order:
1. Opening: "Create a [polished commercial | production-ready marketing | polished informational | high-end conceptual | polished lifestyle] still using the supplied image as the authoritative product reference." Video: "Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference."
2. Effect: two to four sentences, concrete and physical. Name what moves, where the product stays, what the camera does, and how it ends. One effect per recipe.
3. Safety clause for the effect: what must not touch the product ("keep water from deforming or obscuring the product", "the impact must never move or damage the product").
4. Viewpoint sentence (images): straighten a tilted reference.
5. Identity block (above).
6. Closing: image "Deliver a photorealistic, production-ready image with clean edges and coherent shadows." Video: "End on a clean, stable product frame suitable for social media."

Quality bar for a new recipe: a stranger can picture the frame from the effect sentence alone; there is no brand-specific word in it; it contains no claim; every moving thing has a stated start, path and end; the preserve line is untouched. Test it on three different products (a flat pouch, a glass bottle, a boxed item) before adding it to the library. Save new recipes by appending an entry to `references/recipe-library.md` in the same entry format.

## Output format

Deliver exactly this, filled in. The prompt goes in a fenced block so it can be pasted without edits.

````markdown
## Recipe: <id> (<title>) | <image or video> | <aspect ratio>
Why this one: <one sentence tying the user's intent to the recipe>
Attach: <the product photo as the reference image; for video, the generated start frame>

### Start frame prompt (video only; generate this first)
```text
<shared start-frame prompt, aspect ratio set to the final one>
```

### Prompt
```text
<master prompt, adapted: allowed slots changed, identity block intact>
```

Settings: <aspect ratio, 2K for stills / 6 s 1080p silent for video, one output unless more were requested>
Changed from the master prompt: <bullet list of the slots you edited, or "nothing">
Check on the result: <label text incl. diacritics at 100% zoom, logo position, silhouette against the photo, and any recipe-specific risk>
Next: <one-line follow-up, e.g. "if the label drifts, I will give you the compositing fallback">
````

For a new recipe, output the four-field entry and a line saying where it was appended.

## Tool adapters

- Nano Banana Pro: attach the product photo as a reference image and paste the prompt. It renders text well, so for any text you want, give the exact strings in straight quotes inside the recipe's text slot and keep the "never invent" clause. Strongest for the image groups A to E. Add a second reference (a previous output) to hold a look across a set.
- KLING: image-to-video from the generated start frame. Describe motion in plain action verbs, one subject, and put the camera move in its own sentence; shorten the video master prompt to that pattern if the tool ignores long text. Pick the nearest clip length it offers to 6 seconds. Weak fit for `product-spin` and `impact` if it morphs labels; check frame 1 against the last frame.
- Seedance 2: accepts English and Chinese prompts; image-to-video with the start frame as first frame. The video recipes were written for this style of model, so paste the video master prompt as is. Keep the clip silent and let the edit add sound.
- Higgsfield Cinema Studio: use the start frame as the first frame and put the recipe's camera sentence in the prompt; if it offers a matching camera preset (push, pull, crane, whip, orbit), use the preset and keep the identity sentences in the text.
- Premiere Pro and After Effects: use for the last mile. Set exact copy, prices and Polish diacritics as live type over a text-free render; composite the real label or the original packshot over a warped label (track and mask); speed-ramp or time-remap 6-second clips; add sound. Do this instead of fighting the generator for exact text.
- Figma, Illustrator, Photoshop: for cards in groups D and E, generate the visual without words ("no text") and build the layout and copy as vector type; export at the ratio you planned. This is the only reliable route for long or legally sensitive text.

## QA checklist

- [ ] Recipe fits the intent; only one effect in the prompt.
- [ ] Master prompt copied verbatim; only allowed slots edited; identity block present.
- [ ] Photo attached as reference (or text-only fallback disclosed).
- [ ] Video: start frame generated first, at the final aspect ratio, product isolated and 60 to 70 percent of frame.
- [ ] No claims, prices, URLs, QR codes or extra logos added that the user did not supply.
- [ ] Result check: label text matches letter by letter (diacritics too), logo in the same place, silhouette and proportions match the photo, material and color unchanged, product count unchanged.
- [ ] Hands and people (if any) have correct anatomy; effects do not cover the label.
- [ ] Video: first and last frames show the same product; edges stable; ends on a clean hold.
- [ ] If two attempts fail on the label, switch to the compositing fallback instead of re-rolling.

## References

- `references/recipe-library.md`: read when picking or adapting a recipe; it holds all 63 recipes grouped by type with the full verbatim master prompts and the shared video start-frame prompt.
- `references/formats.md`: read when the request is a deliverable type (hero banner, Pinterest pin, carousel, ad pack, model try-on, conceptual CGI still, restyle, lifestyle scene, studio shot, closeup with person) rather than a single recipe; it has purpose, presets, composition rules and prompt skeletons.
- Sibling skill `photo-prompt-craft`: read when you need lighting, lens, surface and negative-prompt vocabulary to extend a recipe, or to critique and refine a generated image.
