# Recipe library (63 recipes)

Contents:
- Start-frame prompt shared by all video recipes
- A. Studio packshots and hero stills (11)
- B. Lifestyle and in-context stills (8)
- C. Conceptual FX stills (5)
- D. Social cards and hooks (7)
- E. Informational and explainer layouts (14)
- F. Video camera moves (12)
- G. Video reveals and FX (6)

Every master prompt below is verbatim. Each assumes the product photo is attached to the generator as a reference image ("the supplied image"). If your tool has no reference-image input, describe the product in detail inside the prompt instead and expect weaker identity preservation.

Defaults shared by all recipes: aspect ratio 3:4 (override freely: square 1:1, landscape 16:9, full-screen Reel or Story 9:16). Image recipes: 2K, highest quality setting. Video recipes: 6 seconds, 1080p, silent, standard motion mode.

## Start-frame prompt shared by all video recipes

Run this first with the product photo as the reference, at the final aspect ratio, and use the resulting image as the first frame of the video. The video recipes assume the product is already isolated, centered and uncropped; the start frame is what makes motion stay on-model. Pick the background hue from the product itself.

```text
Create a clean, premium product-video start frame from the supplied image, treating the visible product as the authoritative reference. Isolate the product and place it centered, upright, fully visible, and uncropped on a seamless single-color studio background with a matching floor-to-wall transition. Select the background hue directly from a distinctive visible color on the product, packaging, label, logo, or material. Prefer a recognizable brand or accent color over neutral black, white, or gray when one is visible. Use a slightly lighter or darker value of that same sampled hue only when needed to maintain clear edge separation and legibility; do not introduce an unrelated color. Scale the product to occupy approximately 60–70% of the frame while leaving balanced motion-safe space around it. Add soft controlled studio lighting and one physically plausible grounding shadow. Preserve the exact product identity, silhouette, proportions, construction, materials, colors, packaging, logo placement, and all readable label text. Do not redesign, simplify, restyle, relabel, crop, rotate, open, duplicate, or deform the product. Do not add props, people, hands, scenery, patterns, gradients, text, captions, borders, watermarks, or extra products. Deliver a photorealistic, stable, high-detail frame suitable as the first frame of a product animation.
```

## A. Studio packshots and hero stills

Clean product-first frames. Use these when the brief is "make the product look good" with no text on the image.

### hero-shot: Hero Shot

- Visible effect: The product as the hero of the frame.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: The default clean advertising still; start here when nothing else is specified.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Place the product large and dominant, standing on a clean seamless studio surface whose tone and texture complement the product's palette, against a softly graded backdrop with generous negative space. Light it like a premium advertising shoot: one large soft key from the upper front-left, a subtle rim light for edge separation, controlled speculars that follow the product's real materials, and one coherent soft shadow grounding it. Shoot at product eye level with a slight hero low angle and a moderate telephoto perspective, keeping the entire product in crisp focus. Add no props, scenery, or set dressing beyond this surface and backdrop unless they are present in the reference. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text — reproduce every printed element, including stickers, fine print, and secondary marks, exactly as in the reference; never invent, translate, or substitute words or characters, and keep unreadable glyphs as faithful shapes. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### minimalist-white: Minimalist White

- Visible effect: A clean product image for a store.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: E-commerce main image, marketplace or store listing where truthful color matters most.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Create a polished e-commerce product still on a clean neutral background with accurate color, even illumination, crisp edges, and a natural grounding shadow. Prioritize clarity and truthful product representation. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### luxury: Luxury

- Visible effect: Premium lighting with a soft glow.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Premium positioning: fragrance, cosmetics, jewelry, spirits, electronics.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Create a refined luxury still with soft luminous highlights, deep clean shadows, subtle reflections, and rich material rendering. The glow should come from believable lighting rather than covering or altering the product. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### signature-frame: Signature Frame

- Visible effect: A signature brand visual.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: A campaign key visual with an ownable color relationship and room for a headline added later.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Build a distinctive campaign-defining key visual around the product using a confident composition, a memorable color relationship derived from the packaging, and generous negative space. The result should feel ownable and brand-specific. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### power-angle: Power Angle

- Visible effect: A striking low-angle view.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Make a product feel strong or important: sneakers, bottles, tools, gadgets.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Show the product from a dramatic low angle that makes it feel powerful and important. Preserve realistic perspective and proportions, add controlled directional light, and keep the background minimal. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### symmetry: Symmetry

- Visible effect: A perfectly symmetrical composition.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Editorial, architectural look; works best for products with symmetric packaging.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Create a rigorously centered, perfectly balanced composition with mirrored spatial rhythm, precise alignment, and clean lighting. Keep the product itself physically accurate and avoid artificial mirroring of asymmetric label details. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### pedestal-shot: Pedestal Shot

- Visible effect: The product at a monumental scale.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Monumental, larger-than-life product with a low horizon; hero banners and posters.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Transform the product into a monumental, larger-than-life presence while keeping its real geometry and branding exact. Use a believable architectural sense of scale, a low horizon, atmospheric depth, and restrained surroundings. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### angles: Angles

- Visible effect: Multiple product angles in one frame.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Catalog sheet with front, three-quarter, profile and optional top view in one frame.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Photograph the same single product from several camera positions and present the views side by side as one clean catalog sheet: a straight-on front view, a three-quarter view, a profile view, and optionally a top-down view, arranged on one seamless studio surface against a softly graded backdrop. Keep spacing even and scale consistent across views, under even, soft studio lighting so every view reads with the same clarity, each view grounded by its own coherent soft shadow. Add no props, scenery, set dressing, captions, or labels beyond this surface and backdrop. For angles the reference does not show, extend the visible design language consistently and keep those surfaces clean — never fabricate regulatory text, barcodes, or claims. Keep design, branding, and color consistent across every view. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text — reproduce every printed element, including stickers, fine print, and secondary marks, exactly as in the reference; never invent, translate, or substitute words or characters, and keep unreadable glyphs as faithful shapes. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### retail-stack: Retail Stack

- Visible effect: Multiple product packages grouped together.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Identical packages stacked, one dominant front unit; boxes, tins, bags.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Build a retail-ready stacked arrangement of identical supplied packages with consistent printing, scale, and perspective. Use stable physical stacking, clean light, and one clearly dominant front-facing unit. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### bundle: Bundle

- Visible effect: Multiple products presented as a set.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: A set or kit of the supplied product presented as a believable group.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Create a coordinated bundle composition using the supplied product as the exact reference for every included unit. Arrange a believable set with clear hierarchy and consistent scale; do not invent unrelated SKUs. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### shelf-ready: Shelf Ready

- Visible effect: A product presentation on a shelf.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Product on a premium retail shelf, facing forward; pitch decks and retail previews.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Place the product in a believable premium retail shelf environment, facing forward and easy to identify. Use realistic shelf depth, neighboring shapes kept secondary, and clean merchandising light. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

## B. Lifestyle and in-context stills

The product placed in a believable setting. Scale, contact shadows and unobstructed labels are the quality bar.

### in-hand: In Hand

- Visible effect: The product held in a hand.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Scale and human context; hand holding the product with the label unobstructed.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Place the product naturally in a realistic human hand, with correct grip, finger anatomy, contact shadows, and believable scale. Keep the product label unobstructed whenever possible. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### on-desk: On Desk

- Visible effect: The product on a work desk.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Workspace context for tech, stationery, drinks, supplements.
- Master prompt:

```text
Create a polished lifestyle still using the supplied image as the authoritative product reference. Place the product naturally in a contemporary workspace with a believable desk surface, restrained supporting objects, and soft directional daylight. The arrangement should feel used but intentionally composed. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### kitchen-scene: Kitchen Scene

- Visible effect: The product in a kitchen setting.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Household context for food, drinks, cookware, cleaning, supplements.
- Master prompt:

```text
Create a polished lifestyle still using the supplied image as the authoritative product reference. Integrate the product naturally on a clean kitchen counter with believable household context, daylight, and accurate contact shadows. Avoid adding ingredients or uses not supported by the product category. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### gym-bag: Gym Bag

- Visible effect: The product as part of a gym kit.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Fitness context: bottles, shakers, supplements, apparel, accessories.
- Master prompt:

```text
Create a polished lifestyle still using the supplied image as the authoritative product reference. Place the product in or beside an open gym bag with a few relevant fitness essentials. Maintain realistic scale, fabric folds, contact shadows, and an organized but lived-in look. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### travel-pack: Travel Pack

- Visible effect: The product in a travel setting.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Open suitcase, carry-on tray or hotel surface; travel-size items, skincare, accessories.
- Master prompt:

```text
Create a polished lifestyle still using the supplied image as the authoritative product reference. Place the product in a believable travel context such as an open suitcase, carry-on tray, or hotel surface. Keep packaging intact, scale correct, and supporting objects secondary. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### weekend-carry: Weekend Carry

- Visible effect: A collection of weekend essentials.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Editorial arrangement with a few weekend essentials; fashion and lifestyle accessories.
- Master prompt:

```text
Create a polished lifestyle still using the supplied image as the authoritative product reference. Create an editorial arrangement of the product with a small weekend carry selection. Use relaxed styling, coherent materials, and a clear hierarchy without inventing duplicate product variants. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### flatlay: Flatlay

- Visible effect: A neatly arranged overhead composition.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Precise top-down grid with a few supporting objects; beauty, food, accessories.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Build a precise top-down flat lay with the product as the anchor and a small number of relevant supporting objects. Use clean spacing, natural contact shadows, and an editorial grid. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

### unboxing: Unboxing

- Visible effect: An open box revealing its contents.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Open box revealing the product; gifting, premium packaging, launch content.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Show a premium package-opening still with the product revealed inside or beside its box. Preserve the supplied packaging design, make inserts and folds physically plausible, and avoid inventing accessories not implied by the source. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

## C. Conceptual FX stills

Stylized high-speed or sculptural stills. The staging is unreal, the product stays exact and upright.

### color-pop: Color Pop

- Visible effect: Bold colorful shapes surrounding the product.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Bold colored forms (paper, pigment, sculptural shapes) in the package palette; beauty, snacks, drinks.
- Master prompt:

```text
Create a high-end conceptual product still using the supplied image as the authoritative product reference. Surround the product with a controlled burst of bold color forms derived from its packaging palette. Use layered paper, pigment, or sculptural shapes with clear depth while keeping every important product detail unobstructed. Keep the product standing perfectly upright and level, never tilted or leaning; the color forms flow around the product, not under its footing. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. Make all effects physically coherent with consistent perspective, reflections, contact shadows, and lighting. Do not morph the product, duplicate it unintentionally, add unsupported claims, introduce unrelated logos, or add watermarks.
```

### fabric-wave: Fabric Wave

- Visible effect: Fabric flowing around the product.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Flowing fabric around the product; cosmetics, fragrance, jewelry.
- Master prompt:

```text
Create a high-end conceptual product still using the supplied image as the authoritative product reference. Shape a luxurious fabric wave around the product with believable folds, tension, and motion. Choose material and color that complement the source while avoiding any overlap that hides essential branding. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. Make all effects physically coherent with consistent perspective, reflections, contact shadows, and lighting. Do not morph the product, duplicate it unintentionally, add unsupported claims, introduce unrelated logos, or add watermarks.
```

### ice-capsule: Ice Capsule

- Visible effect: The product encased in transparent ice.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Product frozen in a clear ice block; drinks, skincare, anything cooling or fresh.
- Master prompt:

```text
Create a high-end conceptual product still using the supplied image as the authoritative product reference. Encapsulate the product in a clear sculptural block of ice with realistic frost, bubbles, cracks, and condensation. Keep the product visible, intact, and optically coherent through the ice. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. Make all effects physically coherent with consistent perspective, reflections, contact shadows, and lighting. Do not morph the product, duplicate it unintentionally, add unsupported claims, introduce unrelated logos, or add watermarks.
```

### water-splash: Water Splash

- Visible effect: Water forming a crown around the product.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: High-speed water crown; beverages, cleansers, hydration products.
- Master prompt:

```text
Create a high-end conceptual product still using the supplied image as the authoritative product reference. Create a high-speed studio moment where clear water rises into an elegant crown around the product. Make the fluid physically believable, preserve label readability, and keep water from deforming or obscuring the product. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. Make all effects physically coherent with consistent perspective, reflections, contact shadows, and lighting. Do not morph the product, duplicate it unintentionally, add unsupported claims, introduce unrelated logos, or add watermarks.
```

### powder-cloud: Powder Cloud

- Visible effect: A cloud of colored powder.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Frozen cloud of colored powder; sports, supplements, cosmetics, snacks.
- Master prompt:

```text
Create a high-end conceptual product still using the supplied image as the authoritative product reference. Freeze a cloud of fine colored powder around the product in a high-speed studio image. Derive the pigment palette from the package, maintain realistic particle density, and keep the front label readable. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. Make all effects physically coherent with consistent perspective, reflections, contact shadows, and lighting. Do not morph the product, duplicate it unintentionally, add unsupported claims, introduce unrelated logos, or add watermarks.
```

## D. Social cards and hooks

Layouts made for feeds, Stories and carousels. Text is minimal and must be limited to words visible on the product.

### swipe-opener: Swipe Opener

- Visible effect: The opening slide of a carousel.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: First slide of a swipeable carousel with a product-led hook and a short title area.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Create an opening card for a swipeable image series with a compelling product-led hook, clear directional flow toward the next slide, and clean space for a short title. Keep the visual understandable without additional context. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### reel-cover: Reel Cover

- Visible effect: A static cover image for a Reel.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Static cover that stays legible at thumbnail size, with interface-safe zones.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Create a bold static cover designed to remain legible at small mobile size. Use a strong central product crop, high contrast, safe space for interface overlays, and at most a short generic hook without unsupported claims. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### vertical-hook: Vertical Hook

- Visible effect: A vertical visual with a strong hook.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Vertical-first attention image with an unusual crop; Stories and Reels frames.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Create a vertical-first attention hook with an unusual crop, immediate contrast, and the product readable within the first glance. Keep the upper and lower interface-safe zones uncluttered. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### share-card: Share Card

- Visible effect: A visual designed for sharing.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Branded, shareable image with negative space for repost interfaces.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Create a highly shareable branded image with a clear visual idea, concise neutral wording, and enough negative space for repost interfaces. Preserve the product as the source of the color and visual identity. Never write taste, quality, comparative, emotional, or health claims, slogans, or taglines; the only product wording allowed is text visibly present in the reference. Never fabricate contact details, phone numbers, addresses, QR codes, or URLs. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### saveable-tip: Saveable Tip

- Visible effect: A useful tip card designed to be saved.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Tip card: one actionable idea about the product category, product as supporting proof.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Create a useful social tip card related to the visible product category, with one concise actionable idea, a clean layout, and the product integrated as supporting proof. Avoid unverified health, financial, or performance advice. Never write taste, quality, comparative, emotional, or health claims, slogans, or taglines; the only product wording allowed is text visibly present in the reference. Never fabricate contact details, phone numbers, addresses, QR codes, or URLs. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### new-drop: New Drop

- Visible effect: A new product announcement.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Launch or restock announcement with an energetic sense of arrival.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Create an energetic new-release visual with the product entering a fresh, contemporary scene. Use packaging-derived colors, crisp contrast, and a clear sense of arrival; include only the product name when it is legible in the source. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### moodboard: Moodboard

- Visible effect: A branded moodboard built around the product.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Editorial grid of material swatches, palette chips and details around the whole product.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Create a curated moodboard around the product using material swatches, palette chips, contextual fragments, and close details derived from the source. Keep the product whole and central, with a cohesive editorial grid. Swatch and chip captions may name only materials, colors, and textures. Never write taste, quality, comparative, emotional, or health claims, slogans, or taglines; the only product wording allowed is text visibly present in the reference. Never fabricate contact details, phone numbers, addresses, QR codes, or URLs. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

## E. Informational and explainer layouts

Icon, label and diagram layouts. Every claim must be visible or physically evident on the product; invented facts are the failure mode.

### before-after: Before After

- Visible effect: The product as a solution to a specific problem.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Problem-to-solution in one frame via a simple environmental contrast; no medical or numeric claims.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Build a clear visual problem-to-solution concept in one frame: the product is the decisive solution, while the problem is represented through a simple environmental contrast. Avoid medical, performance, or numerical claims not visible in the source. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### myth-fact: Myth Fact

- Visible effect: A myth paired with the actual fact.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Two-part myth versus fact card about one safe, generic misconception.
- Master prompt:

```text
Create a polished informational still using the supplied image as the authoritative product reference. Create a two-part myth-versus-fact card about one safe, generic misconception related to the visible product category. Avoid health, legal, financial, or performance claims unless they are explicitly readable on the source. Never write taste, quality, comparative, emotional, or health claims, slogans, or taglines; the only product wording allowed is text visibly present in the reference. Never fabricate contact details, phone numbers, addresses, QR codes, or URLs. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### three-reasons: Three Reasons

- Visible effect: Three reasons to choose the product.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Product plus three short icon-led reasons based on visible attributes only.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Create a structured image with the product and three concise visual reasons based only on visible or physically evident attributes. Use simple icons or short labels, keep hierarchy clear, and do not invent statistics or regulated claims. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### benefits: Benefits

- Visible effect: The product's key benefits.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Up to four short verb-led benefit labels with icons around an upright product.
- Master prompt:

```text
Create a polished informational still using the supplied image as the authoritative product reference. Create a clean benefit overview around the product using only visible, category-safe, or physically evident qualities. Use at most four short, neutral, verb-led benefit labels with simple visual icons; never write taste, quality, comparative, or health claims, slogans, prices, or invented headlines — a short neutral title is acceptable only if it copies text visible in the reference. Keep the product upright and dominant on a clean studio ground; add no props or scenery beyond the icons and labels. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### main-benefit: Main Benefit

- Visible effect: The product's single most important benefit.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: One benefit as a single strong visual metaphor; physical attributes when no claim is readable.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Highlight one visually defensible benefit inferred from the product category or visible packaging, using a single strong visual metaphor. If no claim is readable, focus on a physical attribute such as portability, organization, protection, texture, or ease of use. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### specs: Specs

- Visible effect: The product's key specifications.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Specification card limited to attributes visible in the photo; no invented measurements.
- Master prompt:

```text
Create a polished informational still using the supplied image as the authoritative product reference. Create a precise specification-style card based only on attributes visible in the supplied image, such as form, finish, closure, included pieces, or packaging type. Do not invent measurements, capacity, materials, or performance data. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### feature-zoom: Feature Zoom

- Visible effect: A demonstration of the product's key feature.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Full product plus one magnified functional detail in an inset or cutaway.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Show the full product together with one magnified functional detail in a clean inset or cutaway. Choose a feature that is visible in the source, preserve its construction accurately, and avoid fictional internal technology. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### how-it-works: How It Works

- Visible effect: An explanation of how the product works.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Small sequence, arrows or cutaway for a mechanism that is visually inferable.
- Master prompt:

```text
Create a production-ready marketing still from the supplied image, treating it as the authoritative product reference. Create a clean visual explanation of how the product is used or assembled, using a small sequence, arrows, or cutaway only when the mechanism is visually inferable. Do not invent hidden components or unsupported performance claims. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. Keep typography concise, correctly spelled, and visually subordinate to the product. Do not invent prices, statistics, endorsements, ingredients, certifications, or product claims. Do not add unrelated logos, watermarks, or extra products.
```

### quick-steps: Quick Steps

- Visible effect: A short step-by-step guide.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Concise three-step visual guide for the most obvious safe use.
- Master prompt:

```text
Create a polished informational still using the supplied image as the authoritative product reference. Create a concise three-step visual guide for the most obvious safe use of the product. Use simple numbered stages, consistent product rendering, and no steps that require assumptions about hidden functions. Never write taste, quality, comparative, emotional, or health claims, slogans, or taglines; the only product wording allowed is text visibly present in the reference. Never fabricate contact details, phone numbers, addresses, QR codes, or URLs. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### usage-guide: Usage Guide

- Visible effect: Ways to use the product.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Several plausible ways to use or present the product.
- Master prompt:

```text
Create a polished informational still using the supplied image as the authoritative product reference. Create an organized guide showing several visually plausible ways to use or present the product. Keep every use consistent with the visible category and avoid medical, technical, or safety-sensitive assumptions. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### care-guide: Care Guide

- Visible effect: Product care instructions.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Conservative icon-led care points around an upright hero-shot product.
- Master prompt:

```text
Create a polished informational still using the supplied image as the authoritative product reference. Create a clean care guide using conservative, category-appropriate handling instructions that cannot damage the product. Prefer visual actions such as store dry, keep clean, close securely, or handle gently when applicable. Present the product standing upright and dominant, staged like a hero shot on a clean seamless studio surface, with concise icon-led care points arranged around it. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### product-match: Product Match

- Visible effect: A guide to choosing the right product.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Selection guide matching the product to plausible needs or contexts.
- Master prompt:

```text
Create a polished informational still using the supplied image as the authoritative product reference. Create a simple selection guide that matches the product to several plausible user needs or contexts. Use neutral labels and visible product attributes only; do not fabricate variants that are not shown. Never write taste, quality, comparative, emotional, or health claims, slogans, or taglines; the only product wording allowed is text visibly present in the reference. Never fabricate contact details, phone numbers, addresses, QR codes, or URLs. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### whats-inside: Whats Inside

- Visible effect: The product's contents or ingredients.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Breakdown of contents clearly visible inside or listed legibly on the package.
- Master prompt:

```text
Create a polished informational still using the supplied image as the authoritative product reference. Create an organized visual breakdown of what is clearly visible inside the package or listed legibly on it. If contents are not verifiable, focus on package components rather than inventing ingredients or accessories. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable source text. If people or hands appear, keep anatomy, grip, and scale natural. Use coherent lighting and physically plausible contact shadows. Do not invent factual claims, measurements, ingredients, prices, certifications, extra logos, watermarks, or unrelated products.
```

### inside-pack: Inside Pack

- Visible effect: The internal structure of the packaging.
- Preserve: Exact product shape, proportions, packaging, colors, logo, and readable label details from the supplied image.
- Output type: image | Aspect ratio: 3:4 | Parameters: 2K, high quality
- Use for: Cutaway or opened package showing how the product sits inside.
- Master prompt:

```text
Create a polished commercial still using the supplied image as the authoritative product reference. Create a neat cutaway or opened-package presentation showing how the product sits inside. Keep the exterior design accurate and make internal trays, folds, and compartments mechanically plausible. If the reference photo was taken from a tilted or elevated angle, do not inherit that viewpoint: straighten the product and compose it cleanly and level within the frame, in the natural orientation for this shot. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text. If people or hands appear, keep anatomy natural and product scale believable. Do not add unsupported claims, prices, extra logos, watermarks, or unrelated products. Deliver a photorealistic, production-ready image with clean edges and coherent shadows.
```

## F. Video camera moves

One camera or product move per clip, 6 seconds, silent. Needs the start frame described in the next section.

### push-in: Push In

- Visible effect: A smooth camera push-in.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: The default video move: slow dolly toward the product, ending on a close hero framing.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Perform one slow, steady camera push toward the product, beginning with environmental context and ending on a strong close hero framing. Preserve perspective, focus behavior, and product geometry. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### pull-back: Pull Back

- Visible effect: A camera pullback revealing the scene.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Start on a detail, pull back to reveal the full product and environment.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Begin on a close product detail, then pull the camera smoothly backward to reveal the complete product and its environment. Keep the product anchored and sharp throughout the move. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### crane-reveal: Crane Reveal

- Visible effect: A vertical camera move revealing the product.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Camera rises vertically from behind a foreground element to reveal the product.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Begin below or behind a simple foreground element and raise the camera vertically to reveal the full product. End with a balanced hero composition and a short stable hold. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### topdown-dive: Topdown Dive

- Visible effect: A transition from an overhead view to a close-up.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Overhead view descending and tilting into a close three-quarter angle.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Start from a clean top-down view, then descend and tilt into a close three-quarter product angle in one continuous move. Keep horizon changes smooth and spatial geometry coherent. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### whip-pan: Whip Pan

- Visible effect: A fast whip-pan to the product.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Fast motion-blurred whip pan landing sharp on the product; energetic openers.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Start on a neutral adjacent area, execute one fast motion-blurred whip pan, and land precisely on the product in sharp focus. The transition should feel energetic but not distort the product. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### half-turn: Half Turn

- Visible effect: A smooth 180-degree product rotation.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Fixed camera, product rotates 180 degrees with ease-in and ease-out.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Keep the camera fixed while the product rotates smoothly through 180 degrees, beginning from the supplied view and ending on a clean complementary angle. Use gentle ease-in and ease-out with stable light. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### product-spin: Product Spin

- Visible effect: A clean 360-degree product rotation.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Full 360 turntable turn at constant speed; the product must have plausible unseen sides.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Keep the camera locked while the product completes one smooth 360-degree turn on a clean turntable. Use constant angular speed, stable studio lighting, and a subtle grounded shadow. Infer unseen surfaces conservatively and preserve design continuity. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### floating-roll: Floating Roll

- Visible effect: Slow product rotation in zero gravity.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Zero-gravity slow roll in place with soft reflections; premium, tech, cosmetics.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Make the product float weightlessly and perform a slow, graceful roll in place. Add minimal vertical drift, soft studio reflections, and physically coherent motion without changing the product shape. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### macro-glide: Macro Glide

- Visible effect: A smooth camera move across the product's surface.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Macro lens glides across the surface to show material, edges and print detail.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Use a macro lens to glide slowly across the product surface, revealing material, edges, and print detail with shallow depth of field. Keep macro scale believable and focus transitions controlled. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### texture-track: Texture Track

- Visible effect: A camera move along the material's texture.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Raking light tracks along one visible material texture, then widens to the full product.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Track closely along one visible material texture with raking light that reveals its depth, then widen slightly to reconnect the texture to the full product. Do not replace or exaggerate the material. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### detail-scan: Detail Scan

- Visible effect: Product details revealed in sequence.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Continuous scan through two or three real details ending on the complete product.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Move through two or three important visible product details in a continuous cinematic scan. Use precise focus pulls and finish on the complete product without inventing hidden features. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### label-trace: Label Trace

- Visible effect: A camera move across the logo and label text.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Camera traces across the real label and logo; legibility is the point.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Trace the camera smoothly across the real label, logo, and visible typography, keeping letters stable and legible. Finish by pulling focus to the full front of the product. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

## G. Video reveals and FX

Light, shadow, liquid, paint and particle effects around a product that stays still and intact.

### light-sweep: Light Sweep

- Visible effect: A band of light sweeping across the product.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: One band of light sweeps over a locked product to reveal contours and materials.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Keep the camera and product locked while one controlled band of light sweeps across the surface, revealing contours and materials. Reflections must follow the real geometry and settle into a clean final light. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### sunrise-pass: Sunrise Pass

- Visible effect: A transition from darkness to warm light.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Cool darkness to warm directional light; product emerges into a bright hero state.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Animate a gradual sunrise-like lighting transition from cool darkness to warm directional light. Let the product emerge naturally with moving shadows and finish in a bright premium hero state. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### shadow-motion: Shadow Motion

- Visible effect: Moving graphic shadows.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Graphic architectural shadows glide across background while the product stays fixed.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Keep the product fixed while clean graphic shadows move slowly across the background and surface, as if cast by architectural shapes. Maintain one coherent light source and full brand readability. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### impact: Impact

- Visible effect: A burst of particles frozen around the product.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Radial burst of neutral particles frozen mid-air while the camera arcs.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Begin with the product still, release a controlled radial burst of neutral particles, then freeze them mid-air while the camera makes a short arc. The impact must never move or damage the product. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### liquid-wrap: Liquid Wrap

- Visible effect: Liquid flowing around the product.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: A ribbon of liquid wraps around the product and peels away.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Animate a smooth ribbon of liquid wrapping around the product and peeling away again. The fluid should follow believable momentum and surface interaction without staining, bending, or hiding the product. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### paint-wave: Paint Wave

- Visible effect: A wave of colorful paint.
- Preserve: Exact product identity, shape, proportions, packaging, colors, logo placement, and readable label details throughout every frame.
- Output type: video | Aspect ratio: 3:4 | Parameters: 6 s, 1080p, silent (no audio), start frame required
- Use for: Sculptural wave of packaging-colored paint passes around a stationary product.
- Master prompt:

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Send a sculptural wave of colored paint past and around the product, using colors derived from the packaging. Keep the product clean and stationary, and make the paint motion thick, coherent, and premium. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```
