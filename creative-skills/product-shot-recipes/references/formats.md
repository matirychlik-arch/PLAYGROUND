# Product photo formats

Use this file when the brief is a deliverable type (banner, pin, carousel, ad pack, model try-on, surreal still, restyle) rather than one of the 63 one-shot recipes. Each format gives purpose, presets, composition rules, a prompt skeleton and quality gates. Fill the {{placeholders}} from the product photo and the brief, then run the identity block from SKILL.md at the end.

Contents:
- 1. Product shot (studio packshot)
- 2. Lifestyle scene
- 3. Closeup product with person
- 4. Pinterest pin
- 5. Hero banner
- 6. Social carousel
- 7. Ad creative pack
- 8. Virtual model try-out
- 9. Conceptual product (surreal, CGI-style)
- 10. Restyle (aesthetic and seasonal)

Conventions in the skeletons: `[SECTION]` headings are optional labels, keep them if the generator follows structured prompts, flatten into prose if not. Lighting should always carry direction, quality and a Kelvin value; lens should carry focal length and aperture (vocabulary lives in the sibling skill photo-prompt-craft). Style references are written as concrete descriptors (palette, light, surface, staging register), never as artist or publication names. Append the identity block and the negatives block (universal, plus anti-text-warp whenever a label is visible, plus anti-uncanny whenever people appear).

## 1. Product shot (studio packshot)

Purpose: catalog images, packshots, e-commerce and Shopify listings on neutral, seamless or controlled backgrounds.

Presets:
| Preset | Use for | Visual signature |
|---|---|---|
| clean-studio | Universal e-commerce, catalog | Seamless white-to-light-grey gradient, soft frontal key, minimal shadow |
| dramatic-studio | Premium, fragrance, electronics | Hard rim light, deep shadows, single light source, moody backdrop |
| minimal-design | Modern DTC, clean aesthetic | Pastel or single-color seamless, geometric simplicity, high negative space |
| etsy-handmade | Handcrafted, artisan, small batch | Warm natural light, linen / wood / stone surfaces, organic shadow |
| luxury-editorial | Jewelry, perfume, high-end fashion | Polished surface reflections, marble or velvet, jewel-tone backdrop |
| vibrant-color | Beauty, food packaging, lifestyle DTC | Saturated solid background, bold color blocking, flat modern composition |
| floating-product | Hero shots, suspended display | Product suspended mid-air, motion blur on accents, surreal staging |
| ingredient-flatlay | Beauty, food, supplements | Top-down with raw ingredients arranged around the product |

Aspect ratio: Shopify or catalog main 1:1; IG e-commerce post 4:5; web product page hero 3:4 or 4:5; Pinterest-friendly 2:3; wide editorial 16:9. Default 1:1.

Composition rules: product recognizable and matching the reference; lighting with clear direction (never flat); physically plausible shadows; label text sharp and unwarped; background intentional, not muddy.

Skeleton:
```text
[SUBJECT] Hero shot of {{exact product description}}, {{material/finish}}, {{label/branding visible}}.
[COMPOSITION] {{camera angle}}, {{framing}}, {{rule-of-thirds placement}}, {{negative space directive}}.
[LIGHTING] {{setup with direction and quality}}. {{Kelvin}}. {{shadow behavior}}.
[LENS & CAMERA] Shot on {{focal length}}, aperture {{f-stop}}, {{depth of field}}, sharp focus on {{specific area}}.
[MATERIALS & TEXTURE] {{surface treatments}}, {{reflections}}, {{micro-details}}.
[COLOR PALETTE] Dominant tones: {{2-3 colors from the product or brand}}. {{contrast directive}}.
[STYLE REFERENCE] {{concrete descriptors}}. Commercial product photography, magazine editorial quality.
[BRAND INTEGRATION] {{brand colors}}, {{brand mood: clean / warm / edgy / refined}}.
[QUALITY MARKERS] Tack-sharp, hyper-detailed, photorealistic, commercial-grade.
[AVOID] {{universal + anti-text-warp}}
```

Style-descriptor families by preset: clean-studio and minimal-design lean on geometric color blocking, witty minimal staging; dramatic-studio and luxury-editorial on classical museum-quality still life with dramatic light; etsy-handmade on warm hand-crafted natural light; vibrant-color on saturated, playful staging; floating-product on surreal, high-concept premium staging; ingredient-flatlay on geometric, color-organized top-down arrangement.

## 2. Lifestyle scene

Purpose: the product inside a real-world environment with atmosphere and human signals; more than "product on a table".

Presets:
| Preset | Setting | Typical products |
|---|---|---|
| morning-kitchen | Sunlit kitchen, breakfast moment | Beverages, food, cookware, supplements |
| bathroom-vanity | Marble or wood vanity, soft window light | Skincare, beauty, fragrance, candles |
| bedroom-nightstand | Cozy nightstand, lamp glow, book and linen | Sleep aids, candles, journals, electronics |
| desk-workspace | Modern desk, natural light, laptop and notebook | Tech, stationery, productivity items |
| cafe-table | Marble or wood cafe table, coffee shop blur | Drinks, snacks, books, accessories |
| outdoor-natural | Forest, beach, mountain, golden hour | Outdoor gear, beverages, sunscreen, fashion |
| living-room-cozy | Couch, throw blanket, side table, warm lamp | Candles, throws, books, drinks |
| gym-active | Gym floor, weights, water bottle | Sportswear, supplements, recovery |
| dinner-table-social | Set table, people implied | Beverages, sauces, glassware |
| pour-shot | Mid-air pour, splash, motion frozen | Beverages, oils, sauces |
| flat-lay-curated | Top-down curated objects | Beauty, food, tools, accessories |
| hand-held-closeup | Hands holding / applying / using | Skincare, food, gadgets |
| gift-unboxing | Wrapped or partially unwrapped product | Premium gifts, beauty, jewelry |

Aspect ratio: Instagram feed 4:5 (default); Story or TikTok 9:16; Pinterest 2:3; web hero 16:9; print 3:4 or 4:5.

Composition rules: product is the focal anchor even when small (use light, color or depth of field to draw the eye); surrounding objects tell a story rather than clutter; negative space is intentional and lived-in; avoid perfect symmetry; if hands appear, specify finger positions and natural skin texture.

Skeleton:
```text
[SCENE] {{scene description in 1-2 sentences, location and time of day}}.
[PRODUCT PLACEMENT] {{exact product description}} placed {{position}}, {{relationship to other objects}}, {{prominence directive}}.
[HUMAN ELEMENT] {{hands / person partially visible / group implied / "no people, traces of presence"}}.
[ENVIRONMENT DETAILS] {{3-5 specific surrounding objects}}, {{texture details}}, {{storytelling cues}}.
[LIGHTING] {{direction, quality, Kelvin}}. {{window / practical / natural source}}. {{shadow and highlight behavior}}.
[LENS & CAMERA] Shot on {{35mm / 50mm / 85mm}}, aperture {{f-stop with shallow depth for separation}}, {{point of focus}}.
[ATMOSPHERE] {{mood: serene / energetic / intimate / indulgent / fresh / nostalgic / refined}}. {{air quality}}.
[COLOR PALETTE] {{2-3 dominant tones}}. {{contrast level}}.
[STYLE REFERENCE] {{concrete descriptors}}. Editorial commercial photography.
[QUALITY MARKERS] Cinematic depth, hyper-realistic textures, natural skin and hand details if humans present.
[AVOID] {{universal + anti-uncanny if humans + anti-stock-feel}}
```

## 3. Closeup product with person

Purpose: tight crop with the product as hero and hands, partial face or skin as context (beauty application, holding, pouring, tasting). Different from lifestyle (wide environment) and try-on (full body). A source product image is required.

Presets:
| Preset | Use for | Visual signature |
|---|---|---|
| serum-application | Skincare, oils, treatments | Hand applying product to face, dropper or spatula visible, glowing skin |
| lipstick-on-lips | Lip products | Tight on lips, product near or applied, sharp catchlight |
| hand-holding-vertical | Bottles, fragrance, skincare | Hand cradling product vertically, wrist visible, soft light on glass |
| pour-into-palm | Cream, lotion, oil, supplement | Product poured into open palm, rich texture |
| eye-makeup-closeup | Mascara, shadow, liner | Eye area tight crop, lash detail |
| texture-on-skin | Cream, balm, scrub, foundation | Swatch on hand or cheek, ingredient texture visible |
| dropper-mid-air | Serums, oils with droppers | Dropper near skin with a single suspended drop, clinical premium feel |
| hands-cradling-jar | Body products, candles, jars | Two hands cradling an open jar, indulgent ritual |
| face-touch-product | Skincare results | Hand on cheek, product nearby |
| mouth-bite-or-sip | Food, beverage, supplements | Lips and teeth interacting with the product, sensory focus |

Lighting by preset: serum-application soft beauty dish from camera front with slight under-fill, 5000K; lipstick and eye makeup beauty dish or ring light frontal, 5500K; hand-holding-vertical window light camera-side with rim separation, 4500K; pour-into-palm top-down softbox with sharp falloff, 5000K; dropper-mid-air hard directional key with grid on a deep shadow background, 5000K; hands-cradling-jar soft warm window light, 3500K; texture-on-skin side raking light, 5000K; face-touch-product soft front fill with key 45 degrees camera-left, 4500K; mouth-bite-or-sip practical warm or window key, 4000K.

Aspect ratio: Instagram 4:5 (default); e-commerce closeup 1:1; Pinterest 2:3; Story 9:16; wide editorial 3:2 or 16:9.

Composition rules: product first, person second (if the person dominates, recompose); product fills 40 to 60 percent of visible area (never below 30 or above 70); product on a third, not dead center, unless dramatic; specify finger position (relaxed natural grip); face partial only (nose-to-chin, eye area, lips or cheek); background blur supports the product; skin has pores and fine hairs, never airbrushed.

Skeleton:
```text
[FRAMING] Tight closeup. Product is the hero, {{40-60%}} of visible area. {{specific crop}}.
[PRODUCT] {{exact product description}}, {{material/finish}}, {{label visible}}, sharp focus on product.
[PERSON CONTEXT] {{body part visible with natural skin texture}}. Person is partial context, not the focal subject. {{skin tone}}.
[INTERACTION] {{applying / holding / pouring / touching}}. Natural, unstaged, ritualistic feel.
[LIGHTING] {{setup}}. {{direction, quality, Kelvin}}. Sharp catchlight on product surface. Realistic skin highlight without plasticity.
[LENS & CAMERA] Shot on {{100mm macro / 85mm portrait}}, aperture {{f/2.8 to f/4}}, shallow depth, sharp focus on product surface, gentle bokeh on skin.
[SKIN & DETAIL] Realistic skin texture with natural pores and micro-imperfections, no smoothing. Hands and fingers anatomically correct.
[COLOR PALETTE] {{2-3 tones}}. Product colors faithful to reference.
[STYLE REFERENCE] {{beauty-editorial descriptors}}. Premium DTC standard.
[PRODUCT FIDELITY] Product identical to reference: same color, material, design, branding. Person is supporting context.
[AVOID] {{universal + anti-uncanny + anti-text-warp}} no full face dominating, no person taking focus from product, no plastic skin, no warped fingers.
```

## 4. Pinterest pin

Purpose: vertical 2:3 visuals tuned to Pinterest: moodboard quality, warmth, layered storytelling. Pins win on a vertical format, a hook in the top portion (mobile crop), a hand-crafted organic look, aspirational save-worthy utility and muted earthy palettes (not saturated Instagram color).

Presets:
| Preset | Use for | Visual signature |
|---|---|---|
| lifestyle-aspirational | Home, travel, fashion, wellness | Soft natural light, curated environment |
| product-feature-vertical | Affiliate or DTC spotlight | Product on textured surface with warm context |
| recipe-cover | Food blog | Top-down or 45 degrees dish, ingredients around, warm light |
| editorial-flat-lay | Style and gift guides | Flat-lay with multiple objects, generous spacing |
| before-after-stacked | DIY, makeover | Two stacked panels, clearly divided |
| mood-board-grid | Brand inspiration | 3-4 image collage feeling within one image |
| quote-on-photo | Inspirational, educational | Atmospheric photo with mood-led composition |
| tutorial-step-pin | How-to | Single-frame summary with implied steps |

Palettes: earthy neutral (cream, oat, soft sage, warm terracotta); coastal soft (dusty blue, sand, white, weathered wood); cottagecore (sage, rose, cream, dried flax); quiet luxury (warm grey, soft camel, muted navy, parchment); scandinavian (cool white, pale grey, raw wood, black accent); autumn warm (ochre, rust, deep green, butter cream); dark academia (deep brown, oxblood, parchment, ivy green); clean girl (vanilla, blush, taupe, soft gold).

Aspect ratio: always 2:3 (alternatives: 1:2.1 long pin for storytelling or infographics; 1:1 rarely).

Composition rules: subject on a third with clear top-to-bottom hierarchy; strong entry point at the top; group multiple objects with spacing, not overlap; background texture (linen, wood grain, paper, plaster) carries warmth; avoid sterile studio polish.

Skeleton:
```text
[FORMAT] Vertical 2:3 Pinterest pin composition.
[SUBJECT] {{product / scene / flat-lay arrangement}}.
[COMPOSITION] {{vertical framing}}, {{focal placement on thirds}}, strong top-to-bottom hierarchy, hand-crafted not stock feel.
[AESTHETIC] Pinterest-native: warm, hand-crafted, lived-in. {{cottagecore / clean girl / scandinavian / dark academia / coastal grandmother / quiet luxury}}.
[LIGHTING] {{soft natural window light / golden hour glow / soft overcast / candlelit warmth}}. {{warm 3200-4500K typical}}. Gentle highlight rolloff.
[SURFACE & TEXTURE] {{linen, raw wood, marble, ceramic, woven texture}}. Tactile, lived-in, never sterile.
[COLOR PALETTE] Muted: {{2-3 tones: sage, cream, terracotta, dusty rose, oat, ochre, muted navy, warm grey}}.
[STYLE REFERENCE] {{concrete descriptors}}. Editorial Pinterest aesthetic.
[QUALITY MARKERS] Save-worthy, scroll-stopping, magazine-quality, photorealistic textures.
[AVOID] {{universal + anti-stock-feel}} no oversaturated colors, no neon, no square Instagram-grid framing, no horizontal-leaning compositions, no sterile feel.
```

## 5. Hero banner

Purpose: wide banners for website headers, landing pages, email and section dividers. Needs a strong focal anchor, a clear hierarchy, survival under cropping and brand mood within one second.

Presets:
| Preset | Use for | Visual signature |
|---|---|---|
| cinematic-product-hero | Premium launches, DTC homepages | Wide, dramatic atmosphere, product as focal anchor |
| lifestyle-environmental | Brand heroes, lookbook covers | Wide lifestyle scene with a story cue |
| editorial-portrait | Personal brand, founder stories | Subject in cinematic editorial context |
| abstract-brand-mood | Color-led banners, no product | Atmospheric texture, gradient, light play |
| studio-product-wide | Category banners, sale headers | Product centered or grouped, premium studio backdrop |
| seasonal-campaign | Holiday, seasonal launches | Themed environment with a narrative cue |
| panoramic-landscape | Travel, outdoor brands | Wide landscape with focal element, atmospheric depth |
| split-composition | Comparison, dual-message | Left and right halves visually distinct |

Lighting by brand tier: premium or luxury = hard rim against deep shadow, one dominant source; approachable DTC = soft window light, warm ambient, low contrast; energetic = strong directional, saturated color, dramatic shadows; calm or wellness = diffused overcast, even tones, atmospheric haze; editorial = golden hour, anamorphic flare, cinematic depth.

Aspect ratio: web hero 16:9 (default); wide cinematic 21:9; email header 3:1 or 2:1; LinkedIn cover 4:1; YouTube channel art 16:9; X header 3:1; section divider 21:9 or 3:1.

Composition rules: focal anchor on one of the vertical thirds, not dead center; lines and light lead the eye; a foreground depth element (out-of-focus leaf, fabric edge); keep critical subject inside the central safe zone so mobile crops survive; rich tonal range.

Skeleton:
```text
[FORMAT] Wide {{aspect ratio}} cinematic banner composition.
[FOCAL SUBJECT] {{product / scene / portrait}} positioned at {{left third / right third / centered offset}}, occupying {{rough percentage}} of frame width.
[COMPOSITION] {{horizontal flow, eye-leading lines, clear hierarchy}}. {{foreground / midground / background separation}}.
[ATMOSPHERE] {{refined / energetic / calm / indulgent / fresh / dramatic}}. {{air quality and depth cues}}.
[LIGHTING] {{dramatic key / soft cinematic ambient / golden hour / studio with rim}}. {{Kelvin}}. {{shadow behavior}}.
[LENS & CAMERA] Shot on {{24mm / 35mm / 50mm}}, aperture {{f-stop}}, {{deep depth for environment / shallow for separation}}, anamorphic feel.
[COLOR PALETTE] {{2-3 brand-aligned tones}}. {{warm or cool dominance}}. Rich tonal range.
[STYLE REFERENCE] {{concrete descriptors}}. Cinematic editorial photography.
[QUALITY MARKERS] Magazine-cover quality, ultra-sharp, wide cinematic depth, hyper-realistic.
[AVOID] {{universal + anti-stock-feel}} no flat lighting.
```

## 6. Social carousel

Purpose: 3 to 10 connected slides (Instagram, LinkedIn, Facebook, TikTok photo mode) that read as one narrative. Needs one identical visual system on every slide and a hook, body, payoff arc.

Presets and slide structure:
| Preset | Use for | Slide structure |
|---|---|---|
| product-launch | New product reveal | Hook, reveal, benefit 1, benefit 2, social proof, CTA |
| educational-tips | "5 mistakes", "7 tips" | Hook, tip 1, tip 2, ..., summary or CTA |
| before-during-after | Transformation, process | Before, step 1, step 2, step 3, after, CTA |
| list-roundup | Gift guides, roundups | Cover, item 1, item 2, ..., CTA |
| storytelling-narrative | Brand or founder story | Hook, setup, conflict or insight, resolution, CTA |
| comparison | This vs that | Hook, option A, option B, comparison, recommendation |
| feature-deep-dive | One product, many features | Hero, feature 1, feature 2, in-use, CTA |
| process-walkthrough | How it is made or works | Hook, step 1 to 4, final |

Write the slide outline first (one line per slide) and get it confirmed; then lock the visual system and paste it verbatim into every slide prompt:
```text
[VISUAL SYSTEM - applies to all slides]
Palette: {{2-3 dominant tones}}
Surface/backdrop: {{one texture or color across slides}}
Lighting: {{exact setup repeated on every slide: direction, quality, Kelvin}}
Camera height/angle: {{45 degrees / top-down / eye-level, pick one}}
Composition rule: {{rule of thirds / centered / asymmetric, pick one}}
Style reference: {{same concrete descriptors on every slide}}
```

Per-slide skeleton:
```text
[VISUAL SYSTEM] {{locked block, copied verbatim}}
[SLIDE {{N}} of {{TOTAL}}: {{title from outline}}]
[CONTENT] {{what is shown, framed, emphasized}}.
[COMPOSITION VARIATION] {{how this slide's framing differs inside the locked composition rule}}.
[QUALITY MARKERS] Magazine quality, hyper-detailed, photorealistic, slide {{N}} of a connected carousel, must match slides 1 to {{N-1}}.
[AVOID] {{universal + anti-stock-feel}} no inconsistent palette, lighting, surface or continuity between slides.
```

Aspect ratio: Instagram 4:5 (default), legacy 1:1; LinkedIn 1:1; Facebook 1:1 or 4:5; TikTok carousel 9:16.

Set-level QA: lay slides side by side and check palette, lighting direction, surface carry-through and narrative order. If one slide breaks the system, regenerate only that slide, with the locked block as the preservation directive. Keep the same style-descriptor set across the carousel; never mix sets.

## 7. Ad creative pack

Purpose: coordinated static ads from one brief for paid testing: different hooks, offers and ratios on one brand identity. The first frame must stop the scroll in half a second; saturation and contrast run higher than organic.

Hook angles (use as variant generators):
| Angle | Visual approach |
|---|---|
| problem-solution | Visualize the pain point or problem state |
| transformation | Show the desirable end state |
| social-proof | Product with trust cues, many users implied |
| curiosity-gap | Intriguing visual that demands explanation |
| lifestyle-aspiration | The aspirational life the product enables |
| feature-zoom | Closeup on one differentiating feature |
| comparison | Side-by-side or before-after style |
| urgency-scarcity | Time-limited or limited-availability cue |
| founder-story | Personal, founder-led visual |
| bold-statement | Strong dramatic visual |
| unboxing-reveal | Anticipation and reveal |
| behind-scenes | Process, manufacturing, raw authenticity |

Platform ratios: Instagram Feed 4:5; Instagram Story or Reels cover 9:16; Facebook Feed 1:1; TikTok 9:16; Pinterest promoted pin 2:3; Google Performance Max square 1:1 and landscape 16:9; LinkedIn sponsored 1:1.

Default 5-variant pack (confirm with the user first, one line per variant "Hook, what is shown, ratio"):
1. lifestyle-aspiration, IG Feed 4:5
2. feature-zoom, IG Feed 4:5
3. transformation, IG Story 9:16
4. social-proof, FB Feed 1:1
5. curiosity-gap, IG Story 9:16

Locked visual system for the pack: palette (2-3 brand tones plus one high-saturation accent), surface or backdrop, lighting baseline, composition rule (thirds with a strong focal hierarchy), style descriptors, brand colors.

Per-variant skeleton:
```text
[VISUAL SYSTEM] {{locked block verbatim}}
[VARIANT {{N}}: {{hook angle}} - {{aspect ratio}}]
[HOOK VISUAL] {{specific visual that delivers the hook}}.
[COMPOSITION] {{variant framing}}, {{focal anchor on thirds}}, strong eye-leading hierarchy.
[LIGHTING] {{tuned to the hook: dramatic for problem-solution, warm aspirational for lifestyle, clean clinical for feature-zoom}}.
[CONTRAST & SATURATION] Higher saturation and contrast than organic. Bold tonal range, deep shadows, bright highlights.
[STYLE REFERENCE] {{locked descriptors}}.
[QUALITY MARKERS] Scroll-stopping, magazine-quality, hyper-detailed, performance-ad ready.
[AVOID] {{universal + anti-stock-feel}} no inconsistent palette across variants, no flat lighting, no synthetic stock look.
```

Saturation guidance: loud but not cheap. Phrases that work: "high saturation, vivid color, strong contrast, scroll-stopping in a busy feed", "bold tonal range, deep shadows and bright highlights", "clean clear focal hierarchy, eye lands on subject in 0.5 seconds". Avoid neon-tinted oversaturation, HDR halos, synthetic stock look.

## 8. Virtual model try-out

Purpose: a product worn or used by a generated adult model in a fashion-shoot context (clothing, accessories, jewelry, eyewear, watches, bags, hats, footwear). The identity of the model is not preserved between generations, only the "type" described in the prompt. A source product image is required.

Presets:
| Preset | Use for | Visual signature |
|---|---|---|
| studio-clean | E-commerce on-model main image | Seamless backdrop, soft frontal light, neutral pose |
| editorial-fashion | Lookbook, campaign | Atmospheric environment, dramatic pose and light |
| street-style | Casual, urban DTC | Real city, candid pose, natural daylight |
| outdoor-natural | Outdoor, athleisure | Forest, beach, mountain, golden hour |
| home-lifestyle | Loungewear, sleepwear | Cozy interior, relaxed pose, warm lamp light |
| closeup-detail | Jewelry, watches, eyewear | Tight crop on product area, shallow depth |
| runway-style | Fashion-forward editorial | Studio runway feel, dramatic lighting |
| flat-lay-on-body | Aerial view of body with product | Top-down on a flat surface |

Lighting by preset: studio-clean large softbox 45 degrees camera-left, fill bounce camera-right, hair light, 5500K; editorial-fashion single hard key with gel or grid, deep shadow, 4500-5500K; street-style available daylight with reflector fill, 5000K; outdoor-natural golden hour backlight with reflector fill, 4500K mixed warm, atmospheric haze; home-lifestyle window light with practical lamp fill, 3500K; closeup-detail beauty dish or soft directional, narrow depth, sharp catchlight, 5500K; runway-style strong key with rim, slight haze, dramatic falloff, 5000K; flat-lay-on-body even soft top-down, minimal shadow, 5000K.

Anatomy rules (the main way this format fails): hands need explicit finger positions ("relaxed fingers loosely curled at side", "hand on hip with thumb out", "hand holding strap with natural grip"); feet need shoe and ground contact ("feet planted shoulder-width, weight on back leg"); face needs eye direction and expression (wrong eye direction is the most common tell); posture needs spine curve and shoulder placement; ask for "natural human proportions, anatomically correct".

Aspect ratio: e-commerce on-model 4:5 (default); lookbook 3:4 or 2:3; Instagram 4:5; Pinterest 2:3; Story 9:16; wide editorial 16:9.

Skeleton:
```text
[PRODUCT] {{exact product description}}, worn / displayed on the model's {{body area}}.
[MODEL] {{gender presentation, age range, ethnicity if specified, hair, build, skin tone}}. Natural realistic features, anatomically correct, professional model proportions.
[POSE] {{standing three-quarter / walking / leaning / sitting / candid}}. {{hand positions}}, {{eye direction}}, {{expression}}.
[FRAMING] {{full body / three-quarter / waist-up / closeup on product area}}, {{thirds placement}}.
[ENVIRONMENT] {{backdrop or location per preset}}.
[WARDROBE / STYLING] {{what else is worn}}, complementing the featured product without competing.
[LIGHTING] {{setup}}. {{direction, quality, Kelvin}}. {{skin highlight behavior}}.
[LENS & CAMERA] Shot on {{50mm / 85mm / 35mm}}, aperture {{f/2.8 to f/5.6}}, sharp focus on {{product area}}.
[SKIN & DETAIL] Realistic skin with natural pores, no smoothing. Individual hair strands. Hands and fingers anatomically correct.
[PRODUCT FIDELITY] The product remains identical to the reference: same color, material, design details, proportions, branding placement. The model wears it without altering it.
[AVOID] {{universal + anti-uncanny + anti-text-warp}} no clothing that fights the featured product, no warped product geometry, no altered product color.
```

## 9. Conceptual product (surreal, CGI-style)

Purpose: deliberately unreal, premium product imagery: levitation, frozen splashes, sculptural arrangements. Signals "expensive product". Strong fit: premium fragrance and beauty, luxury watches and jewelry, premium tech, fashion accessories, high-end DTC. Weak fit: casual CPG, budget brands, bohemian or rustic positioning (suggest lifestyle or product-shot instead).

Presets:
| Preset | Use for | Visual signature |
|---|---|---|
| levitating-suspended | Fragrance, skincare, tech | Product floating mid-air, soft shadow below, clean background |
| splash-frozen-motion | Beverages, cleansers, oils | Liquid frozen in a mid-air burst around the product |
| abstract-cgi-render | Premium DTC, jewelry | Hyper-clean studio CGI look, marble, chrome, liquid metal |
| sculptural-arrangement | Beauty, supplements, food | Products stacked as geometric sculpture |
| liquid-pour-suspension | Oils, fragrances, sauces | Liquid ribbon pouring, frozen mid-air |
| broken-deconstructed | Beauty, food, supplements | Exploded view with components floating around |
| floating-elements | Beauty, food, beverages | Petals, leaves, crystals, fabric, citrus suspended around product |
| surreal-environment | Fragrance, fashion | Impossible environment: clouds, water surface, mirrored room, infinity space |
| geometric-pedestal | Fragrance, jewelry, watches | Minimal geometric pedestal with dramatic single-source light |
| chrome-liquid-metal | Tech, fashion accessories | Chrome, liquid metal, mirror surfaces with reflection play |

Lighting by preset: levitating single soft key from above-front 45 degrees, deep shadow background, soft contact shadow under the floating product, 5000K; splash hard strobe with high-speed freeze, multiple flashes for separation, 5500K; abstract-cgi multi-source with controlled bounce, even key with rim, mirror-like reflections, 5500K; sculptural single dramatic key with grid, deep architectural shadow, 5000K; liquid-pour hard backlight to define the liquid, rim separation, freeze every droplet, 5000K; broken-deconstructed even soft top-down, minimal shadow, 5500K; floating-elements soft directional key with subtle fills, 4500K; surreal-environment light from an impossible motivated source (glow from inside, from below, refracted through liquid), 5000K cool; geometric-pedestal single hard key with strong shadow, museum precision, 5000K; chrome soft dome lighting for reflection control, sharp speculars, 5500K.

Aspect ratio: editorial or catalog premium 1:1 (default for standalone); magazine portrait 3:4 (editorial default); Instagram 4:5; Pinterest 2:3; Story 9:16; banner 16:9.

Composition principles: commit to the surreal (half-surreal looks worse than realistic); negative space is intentional isolation; the product stays photorealistic and crisp while only the staging is unreal; one main surreal element plus 2 to 4 supporting elements, more is clutter; reward geometry (triangles, golden ratio, symmetry, repetition).

Skeleton:
```text
[CONCEPT] {{preset description in 1-2 sentences}}. State that the composition is surreal / impossible / CGI-rendered photorealism, not documentary photography.
[PRODUCT] {{exact product description}}, {{material/finish}}, {{label}}, sharp realistic detail despite the surreal context.
[COMPOSITION] {{geometric / sculptural / floating / suspended}}, {{specific surreal element}}, dramatic hierarchy.
[PHYSICS DEFIANCE] {{what defies physics: floats with no support / liquid suspended with no fall / impossible arrangement}}.
[LIGHTING] {{dramatic stylized setup}}. {{hard direction, controlled shadow}}. {{usually 5000-5500K}}. Sharp catchlights on glass, metal, liquid.
[BACKGROUND & ENVIRONMENT] {{clean gradient / surreal environment / geometric backdrop / infinity space}}, supporting not competing.
[MATERIALS & TEXTURES] {{marble, chrome, liquid metal, polished glass, water, smoke, satin, velvet}}. Hyper-realistic surface detail.
[LENS & CAMERA] Shot on {{50mm / 85mm / 100mm macro}}, aperture {{f/8 to f/11 for sculptural, f/2.8 for selective focus}}, sharp focus throughout the product.
[COLOR PALETTE] {{2-3 tones}}. {{high contrast / monochromatic / single accent against neutral}}.
[STYLE REFERENCE] {{concrete descriptors}}. Premium conceptual product photography, CGI-render aesthetic.
[AVOID] {{universal + anti-text-warp}} no cartoonish render, no plastic look on product, no half-committed surreal, no cluttered composition, no random floating objects, no text other than the product's own branding, no melted product details.
```

## 10. Restyle (aesthetic and seasonal)

Purpose: transform the aesthetic, mood or season of an existing image while the subject, composition and product identity stay recognizable. Two axes, usable alone or combined ("Christmas version in cottagecore style"). A source image is mandatory; keep its aspect ratio unless told otherwise.

Axis 1, aesthetic (visual signature / palette / surfaces):
| Aesthetic | Signature | Palette | Surfaces |
|---|---|---|---|
| clean-girl | Minimal, dewy, fresh, neutral | Vanilla, blush, taupe, soft gold | Smooth glass, brushed gold, fresh linen |
| cottagecore | Rustic, hand-crafted, romantic | Sage, cream, dried rose, wheat | Linen, raw wood, dried flowers, vintage paper |
| Y2K | Glossy, futuristic, playful | Hot pink, lime, chrome, baby blue | Chrome, glossy plastic, holographic, glitter |
| minimal | Stripped back, geometric, pure | White, grey, single accent | Concrete, brushed metal, matte paper |
| dark-academia | Moody, scholarly, romantic | Oxblood, deep brown, parchment, ivy | Worn leather, aged paper, dark wood, candlelight |
| quiet-luxury | Refined, restrained, expensive | Warm grey, camel, muted navy, parchment | Cashmere, polished marble, brushed metal |
| scandinavian | Cool, clean, functional | White, pale grey, raw wood, black | Pale wood, linen, ceramic |
| coastal-grandmother | Soft, weathered, breezy | Dusty blue, sand, white, weathered wood | Linen, driftwood, ceramic, woven texture |
| maximalist | Layered, saturated, bold | Multi-color clash with intent | Velvet, brass, patterned wallpaper |
| brutalist | Raw, monolithic, modernist | Concrete grey, black, white | Raw concrete, brushed steel |
| art-deco | Geometric, gold, glamorous | Black, gold, emerald, ivory | Polished marble, brass, lacquered wood, mirror |
| retro-90s | Saturated, grainy, nostalgic | Magenta, teal, mustard | Film grain, faded color, soft vintage glow |
| futurist | Sleek, glowing, neon | Neon cyan, magenta, deep black | Glossy black, glowing edges, holographic |
| japandi | Calm, minimal, organic-modern | Warm beige, charcoal, soft white | Pale wood, linen, ceramic, soft shadows |
| bohemian | Eclectic, warm, layered | Terracotta, mustard, deep teal, cream | Macrame, woven rugs, brass, plants |
| mid-century-modern | Clean lines, warm woods, retro | Mustard, teal, walnut, cream | Walnut, leather, geometric patterns |
| gothic-romance | Dark, dramatic, ornate | Black, deep red, gold, deep purple | Velvet, lace, candlelight, antique frames |
| pastel-dream | Soft, ethereal, whimsical | Lavender, peach, mint, baby blue | Soft tulle, pastel paper, dreamy light |

Axis 2, seasonal (cues / palette / atmosphere):
| Season | Cues | Palette | Atmosphere |
|---|---|---|---|
| christmas | Pine, holly, ornaments, candle, ribbon, snow window | Deep red, evergreen, gold, cream | Warm tungsten glow |
| black-friday | Bold sale aesthetic, type-friendly | Black, red, white, stark contrast | High-contrast cinematic |
| cyber-monday | Tech-modern, neon, digital | Electric blue, magenta, black | Glowing edges, futuristic |
| valentines-day | Roses, soft hearts, candlelight, ribbon | Dusty rose, deep red, blush, gold | Romantic warm glow |
| mothers-day | Spring flowers, pastels, brunch | Blush, sage, cream, soft yellow | Soft natural morning light |
| fathers-day | Wood, leather, masculine textures | Warm brown, navy, olive | Warm afternoon light |
| easter | Pastel eggs, spring flowers, greenery | Mint, lavender, peach | Bright spring morning light |
| halloween | Pumpkins, candles, autumn leaves, gothic accent | Orange, deep purple, black, amber | Moody candlelight, twilight |
| thanksgiving | Harvest, dried wheat, gourds, warm spice | Burnt orange, ochre, deep red, cream | Warm afternoon golden light |
| back-to-school | Notebooks, pencils, apples, denim | Navy, mustard, red, denim blue | Crisp morning light |
| pride | Rainbow accents, joyful | Saturated rainbow | Vibrant celebratory light |
| new-years | Champagne, gold confetti, midnight glow | Gold, black, deep navy, white | Sparkling night light |
| summer | Sun, water, fresh fruit, light fabric | Saturated blue, yellow, white, coral | Bright midday or golden hour |
| spring | Cherry blossoms, fresh greens | Soft pink, green, cream, butter yellow | Soft morning sun |
| fall | Foliage, sweaters, warm spice | Burnt orange, mustard, deep red, brown | Warm afternoon, low sun |
| winter | Snow, frost, cozy textures | Deep blue, white, silver, deep green | Cool soft daylight or warm interior |
| lunar-new-year | Red lanterns, gold accents, blossoms | Deep red, gold, black | Festive warm glow |
| 4th-of-july | Picnic, flag colors, fireworks | Red, white, blue with warmth | Bright summer outdoor light |

Skeleton:
```text
[SOURCE] Restyle the referenced image. PRESERVE: {{subject identity, composition, framing, focal anchor, product details}}.
[TRANSFORMATION] TRANSFORM into {{aesthetic}} {{+ seasonal preset}} aesthetic.
[AESTHETIC SHIFT] {{visual cues}}. {{surface and texture changes}}. {{mood shift}}.
[SEASONAL SHIFT] {{seasonal cues}}. {{palette shift toward seasonal tones}}.
[PALETTE] Shift the dominant palette to {{exact palette from preset}}. Keep the product's intrinsic colors recognizable.
[LIGHTING] {{new lighting matching the aesthetic}}. Different from the source lighting if needed.
[TEXTURE & SURFACE] {{surface treatments from the aesthetic}}.
[STYLE REFERENCE] {{concrete descriptors}}.
[PRESERVATION DIRECTIVE] The subject and composition must remain recognizable as the same image; only aesthetic and atmosphere change.
[AVOID] no aesthetic mixing, no half-applied transformation, no source style bleeding through, no change to subject identity, composition or product appearance.
```

QA for restyle: subject and composition preserved, shift strong and committed, palette matches the preset, seasonal cues read clearly, no kitsch (editorial, not gimmicky).
