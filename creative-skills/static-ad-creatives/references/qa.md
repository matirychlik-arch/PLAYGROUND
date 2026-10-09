# QA for static ad creatives

Contents:
1. Readiness gates (before any copy or image)
2. Quality gates for a pack
3. Hard rules (never)
4. Copy checks
5. Layout and image checks
6. Marketplace card checks
7. Repair strategy and revisions
8. Delivery

Provenance: the quality gates (section 2), the readiness rules and the "never" list come from the source ad workflows and ad-pack mode. The copy, layout and marketplace checks add standard practice.

## 1. Readiness gates

Nothing is written or rendered before it is ready.
- The product has a Product Fact Sheet: name, what it is, at least 3 true benefits, an offer or reason to act. Ads generated from an unread product come out generic.
- If the product came from a page: at least one real product image is available, or an exact visual description exists. A page that could not be read is reported, not guessed; ask for the product page, a public image link, or the user's own description and photo.
- If a brand is involved: the Brand Card is complete (logo file, hex colors, fonts, tone). A failed or partial brand read still leaves a usable pack from the product alone; say what is missing.
- The user has seen the one-line outline per variant when the pack is larger than three creatives or the brief was loose.
- The objective, placements and ratios are stated for each creative. A request like "make ten ads, go" while the product is still unread gets the wait explained, not a pack of generic ads.

## 2. Quality gates for a pack

- [ ] All variants share the visual system (palette, surface, style references)
- [ ] Each variant delivers its assigned hook angle visually
- [ ] Saturation and contrast are ad-appropriate
- [ ] Brand colors integrated consistently
- [ ] Aspect ratios match the assigned platforms
- [ ] No AI artifacts or warped baked-in text
- [ ] Pack feels coordinated, not random
- [ ] Typography (if any) renders correctly per the three-case rule
- [ ] Prompt asks for 2K output where the tool supports it

## 3. Hard rules (never)

- Never invent selling points, prices, discounts, deadlines, ratings, review counts, certifications or guarantees. Use the user's own words for copy fields.
- Never invent a brand to hold a product, and never start research on a domain nobody named. Confirm a guessed domain in one line first.
- Never treat a homepage as a product, or a product page as a brand. When the link's domain is new and the words do not settle it, ask.
- Never send an unsupported ratio. If the generator has no exact 4:5, use the 3:4 compose-and-crop route, not an unlisted value.
- Never name an objective the user did not imply; leave it unset.
- Never put one brand's look on another brand's product, and never promise a brand look on a product the kit does not cover.
- Never reuse a Product Fact Sheet from another product.
- Never claim an ad is ready when pictures are still rendering or when the layout check has not been run on the real strings.
- Never mix several creatives' fixes: repair only the failing one.

## 4. Copy checks

- Every claim traces to a line of the Product Fact Sheet
- Headline states one promise; on-image headline is 2-6 words
- Primary text hook sits in the first ~125 characters
- CTA matches the objective and is a label the platform offers
- Headline, primary text and image say the same thing
- Address form (ty/Państwo) is consistent across the pack
- No policy-sensitive implications (personal attributes, guaranteed outcomes, unsubstantiated health or finance claims)
- No competitor names unless the user asked and can substantiate
- Polish: diacritics correct, no single-letter line endings, currency format "99 zł"
- `[TO CONFIRM: ...]` slots are resolved or flagged to the user

## 5. Layout and image checks

- Canvas size and ratio match the placement table
- Text and logo inside the safe zones for the placement (stories/TikTok: not in top 14% or bottom 20%; feed: at least 6% from every edge)
- Headline at least 64 px, other text at least 32 px (at 1080 px wide); CTA text at least 40 px
- Contrast sampled on the actual pixels under the text: at least 4.5:1 (3:1 for large display text)
- Hierarchy reads in the order: product/hero, headline, CTA, logo
- One display and one body font from the Brand Card; at most two families
- Logo file is the exact brand asset, correct colorway for the background
- Product shape, color, label and packaging match the reference photo; label text unwarped
- Baked text: every string spelled exactly as in the quotes, Polish diacritics intact; one headline and one short CTA at most
- Overlay mode: the calm area is a natural part of the scene, not a flat band; the final text is set in the real font
- Faces and hands free of uncanny artifacts; no extra fingers, no melted geometry
- No fake logos, watermarks or invented microcopy
- Not neon, not HDR-haloed, not stock-photo synthetic
- If a 4:5 was cropped from 3:4, nothing important crosses the crop boundary

## 6. Marketplace card checks

- Main image: pure white background, product about 85% of the frame, no text/badges/watermark/props, correct label, minimum 1000 px longest side (2000 px recommended), sRGB. Verify the target marketplace's current rule.
- Secondary and A+ images use the accepted main image as the product reference; the product is identical across all assets
- Infographic callouts are 3-5 short strings, legible at thumbnail size, and contain only supplied facts
- No efficacy numbers, certifications or endorsements unless the user supplied them; skip those modules otherwise
- Lifestyle shots show plausible scale and a believable setting; the product is the hero
- All text in the user's language, spelled exactly, diacritics intact
- Consistent palette and typography across the whole set

## 7. Repair strategy and revisions

When a creative fails:
1. Name the failed gate.
2. Decide whether it is a copy, layout, or image problem.
3. Keep the visual system and all passing creatives unchanged.
4. Fix the smallest thing: re-type the headline in Figma, move the logo, recrop, swap a background; regenerate only if the image itself fails.
5. Re-run the checks on that creative and re-check the pack for consistency.

Do not retry the same failing prompt more than once; change the prompt (stronger preservation language, simpler composition, text moved to overlay) or switch the text mode to overlay. A request for edits, variations or a different look changes only that creative.

## 8. Delivery

Return the pack table, then each creative card in order. Name files predictably so a single creative can be revised:

```text
<brand>-<product>-<angle>-<ratio>-v1.png      e.g. oxy-bottle-feature-zoom-4x5-v1.png
<brand>-<product>-<angle>-<ratio>-v1-bg.png   (text-free background, overlay mode)
```

State for each: text mode (baked or overlay), fonts required for the Figma file, and anything marked `[TO CONFIRM]`.
