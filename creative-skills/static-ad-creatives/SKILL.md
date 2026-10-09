---
name: static-ad-creatives
description: >-
  Produces a set of static ad creatives for Meta (Facebook/Instagram), TikTok and marketplace listings from a brand + product + offer: for each creative a ready-to-paste image prompt, headline / primary text / CTA copy, and a layout spec with sizes and safe zones. Three entry paths: from a brand website URL, from a product (page link, photo, description), or from a plain prompt. Also builds marketplace product cards (main image, secondary images, A+ style modules). Use whenever the user asks for ads, kreacje reklamowe, ad creatives, banery, grafiki na Meta/Instagram/TikTok, A/B variants of an ad, or listing images for Allegro/Amazon/Etsy, even if they never say "skill". Trigger on: kreacja reklamowa, reklama na Facebooku, reklama na Instagramie, kreacje statyczne, hook, nagłówek, tekst główny, CTA, zestaw reklam, warianty do testów, karta produktowa, zdjęcia do oferty, Allegro, infografika produktowa, stwórz reklamę dla. Not for a brand/logo/identity (use brand-identity-kit), not for video or UGC ads, not for plain product photography without ad copy.
---

# Static Ad Creatives

Make a coordinated set of static ads, the kind that run as Meta ads on Facebook and Instagram or as TikTok image ads, plus marketplace product cards. Each creative is a package: image prompt + copy + layout spec. The set is engineered for testing: different hooks, one brand look.

The order matters. Give the product its facts first, then write copy from those facts, then render. Ads written from an unread product come out generic, so do not draft copy until the product facts exist.

## When to use / when not

Use for:
- Meta/IG/TikTok static ads for a product, a brand, or an offer
- A/B test packs: several hook angles across several formats
- Marketplace cards: main image, secondary images, infographic, lifestyle, what's in the box, A+ style modules

Do not use for:
- creating a logo, palette or identity: use `brand-identity-kit`
- a picture with no ad copy (a product shot, a catalog photo, a scene): a product photography skill or a plain image prompt
- video ads, UGC or creator videos
- copy alone: write it in chat using `references/copy-frameworks.md`; no layout or image prompt needed

"Brand kit" is ambiguous. Here it means the brand facts the ad needs (logo, palette, fonts, tagline, audience, tone). If the user wants a full identity created or extended, route to `brand-identity-kit`.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

Parse what the user already gave. Ask one compact message with only the blockers.

1. **Entry path** (see Workflow step 1): brand website URL, product (page link / photo + description), or a prompt alone
2. **Product facts**: name, what it is, 3-5 true benefits, proof the user actually has, price and offer, destination URL
3. **Brand kit**: logo file, exact hex colors, fonts, tagline, tone, audience. If a website is given, extract these from it instead of asking
4. **Objective**: `sales`, `leads` (sign-ups, demos, quotes), `traffic` (visits, clicks), `awareness` (a launch, being known), `engagement` (comments, shares). Leave it unset unless the user made the goal clear; the product profile then decides
5. **Placements / formats**: default IG Feed 4:5, IG Story 9:16, FB Feed 1:1 (see `references/formats-and-layouts.md`)
6. **Count**: the number the user named, or 1 for a singular request; default pack is 5 variants
7. **Language and market**: copy language (Polish by default for a Polish brand), formal or informal address
8. **Text mode**: exact words on the image generated in one pass ("baked"), or text added afterwards in Figma ("overlay")

Defaults: 1:1 if nothing is stated (square feed), objective unset, text mode = overlay in Figma for final exactness, baked only if the user wants it or for fast concepts.

Never invent selling points, prices, discounts, deadlines, reviews, statistics, certifications or guarantees. Use the user's own words for copy fields. If a needed fact is missing, ask or leave a visible `[TO CONFIRM: ...]` slot.

## Workflow

1. **Pick the entry path.**
   - *From a brand:* the user names a brand or gives a bare domain/homepage. Fetch the site and extract a brand kit card (logo, palette, fonts, tagline, audience, tone) and the products found. Only research a domain the user named; if only a brand name is given, ask "Is that example.com?" before touching anything.
   - *From a product:* a link to one item (path like `/products/...`), a product photo with a description, or a description. File the product facts; a product needs no brand and no brand is invented to hold it. If the link's domain also looks like the user's brand and it is unclear, ask one line whether to also read the brand.
   - *From a prompt alone:* an offer, an idea, a service with no page and no photo. Go straight to the outline; the result is only as specific as the prompt, so say what you assumed.
   A link is a brand if it is a homepage or the user says brand/store/site/company; it is a product if it points to one item.
2. **Readiness gate.** Write a Product Fact Sheet and a Brand Card (templates under Output format). Do not proceed until the product has: a name, what it is, at least 3 true benefits, and an offer or reason to act. For a page-sourced product, also have at least one real product image or an exact visual description.
3. **Choose objective and formats.** Map objective to CTA and to hook angles (`references/copy-frameworks.md`). Pick placements from `references/formats-and-layouts.md`. Meta feeds want 4:5 or 1:1; Stories/Reels/TikTok want 9:16.
4. **Outline first, generate second.** Draft a one-line summary per variant (`Variant N: hook angle, what is shown, format`) and confirm with the user when the pack is more than three creatives or the brief was loose. Default pack: lifestyle-aspiration 4:5, feature-zoom 4:5, transformation 9:16, social-proof 1:1, curiosity-gap 9:16.
5. **Lock the visual system** once for the whole pack (palette with one high-saturation accent, surface, lighting baseline, composition rule, brand colors). Copy it verbatim into every prompt.
6. **Write the copy** per variant with a framework (AIDA, PAS, BAB, FAB, 4U): headline, primary text, CTA, optional description. Check length limits and the claims rules in `references/copy-frameworks.md`.
7. **Write the layout spec** per format: canvas size, safe zones, text zones as percentages, logo position, CTA button position, min text sizes (`references/formats-and-layouts.md`).
8. **Write the image prompt** per variant. Follow the typography rule: exact words in the image (quoted strings) or a tonally calm area in the scene for overlay, never a vague "empty space".
9. **QA** with `references/qa.md`, fix only the failing creative, deliver the pack table plus per-creative cards.
10. **Marketplace branch.** If the request is listing images, use the marketplace section of `references/formats-and-layouts.md`: choose a scope (main, product-images, aplus, full-set), build the main image first, then secondary images and A+ modules that reference the accepted main image.

Revisions: if a user wants a different look for one creative, change only that creative and keep the locked visual system and the other creatives.

## Output format

Deliver a pack summary table, then one card per creative. Everything paste-ready.

**Product Fact Sheet**
```text
Product:
What it is (one line):
True benefits (3-5, user's own words):
Proof the user has (reviews count, certificates, numbers they supplied):
Price / offer / deadline:
Destination URL:
Product images available:
Unknowns to confirm:
```

**Brand Card**
```text
Brand:
Logo file:
Palette (hex + role):
Fonts:
Tagline:
Audience:
Tone:
Never (2+ rules):
```

**Pack table**
```text
# | Hook angle | Format | Headline | CTA | Text mode | Status
```

**Creative card**
````text
CREATIVE <N>: <hook angle> | <placement> <ratio> <WxH px> | objective: <objective>

COPY (language: <pl/en>)
Headline (on image or ad headline field): "<...>"   [<n> chars]
Primary text: "<...>"                                 [<n> chars]
CTA button: "<...>"
Description (optional): "<...>"
Destination URL: <...>

LAYOUT SPEC
Canvas: <WxH>, safe margins <...>
Zones (percent of canvas): headline <x,y,w,h>; product focal <...>; logo <...>; CTA <...>
Type: <display font + size min>, <body font + size min>, contrast <ratio>

IMAGE PROMPT
```
[VISUAL SYSTEM] ... [VARIANT N: hook angle - ratio] ... [AVOID] ...
```
````

## Tool adapters

- **Nano Banana Pro:** primary image generator. Renders text well: put exact strings in quotes, one headline and one short CTA at most. Attach the real product photo as a reference image and say "preserve the product, label and packaging exactly". Ask for 2K if available. Request the ratio you need (9:16, 1:1, 4:5 or the nearest and crop).
- **Figma:** the exact-layout path. Build a frame per format at the pixel size, place the generated text-free background, set copy in the real brand font, add the logo file and CTA button, export PNG/JPG. Use components for CTA and logo so a pack of 10 stays consistent.
- **Photoshop / Illustrator:** product cutouts, label retouching when a generator warps a label; vector logo placement.
- **Premiere Pro + After Effects:** only to animate a finished static into a short motion ad (push-in, text build). Out of scope for this skill; hand over the text-free background and the layer list.
- **KLING / Seedance 2 / Higgsfield Cinema Studio:** poor fit for exact-text statics. If the user wants a motion version, animate the text-free image (one subject, camera move in a separate sentence; Seedance 2 accepts EN+ZH prompts) and add the copy in After Effects.
- **Meta Ads Manager / TikTok Ads Manager:** the headline, primary text and CTA fields from the cards paste directly; the image carries only the short on-image text.

## QA checklist

Full list in `references/qa.md`. Minimum before delivery:
- [ ] Every claim, price and deadline traces to the Product Fact Sheet; none invented
- [ ] Headline, primary text and CTA fit the length limits; CTA matches the objective
- [ ] Exact strings and Polish diacritics render correctly; no garbled or fake text
- [ ] Text and logo sit inside safe zones for the placement; contrast at least 4.5:1
- [ ] Product and label are unaltered and match the reference photo
- [ ] All creatives share one visual system, brand colors, one accent
- [ ] Each creative delivers its assigned hook angle visually
- [ ] Ratios and pixel sizes match the placements
- [ ] Saturation is louder than organic but not neon or HDR-haloed

## References

- `references/copy-frameworks.md`: read when writing headline, primary text and CTA: hook angles, objective-to-CTA mapping, AIDA/PAS/BAB/FAB/4U templates, length limits, claims rules, Polish copy notes.
- `references/formats-and-layouts.md`: read when specifying sizes, aspect ratios, safe zones, layout zones, the image prompt template and text-mode rules, and the marketplace card system (main, secondary, A+ modules).
- `references/qa.md`: read before delivering and when a creative looks off: quality gates, hard "never" rules, copy and layout checks, repair strategy, marketplace checks.
