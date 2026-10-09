# Creator persona prompt (the clean-person frame for UGC)

Contents:
1. Rules that decide the frame (no products, beauty floor, override rule, category gate)
2. Variety pools (how to avoid the same creator every time)
3. Wardrobe, location and lighting matrices
4. Camera language, bans, expressions, closing block
5. Prompt structure and worked examples

Use this when you need ONE clean image of a UGC creator that every later shot references. For a persona that must live across a whole channel or series, build it with `ai-influencer-casting` (two-panel sheet, trait taxonomy) and use this file only for the UGC look of the frame. Write the prompt as one plain string. The creator frame is made once and reused as the reference image for every shot. Never regenerate it mid-project.

## 1. Rules that decide the frame

### No products in the creator image
The frame is a CLEAN PERSON. The product is added in the later shots.
- Describe only the person: appearance, face, expression, clothing, pose, style.
- Never include products, objects, props or anything the person holds. Location/background is fine, hands stay empty.
- Bad: "a young woman holding a skincare bottle in a bathroom, smiling" (the model bakes the bottle into the image and the later composite fails).
- Good: "a young woman, mid-20s, natural beauty, friendly smile, casual style, modern bathroom background".

### Beauty floor (every prompt, every tier)
The persona reads as conventionally attractive: model-tier face, symmetrical features, well-proportioned figure. Tier changes wardrobe, room and register, it does not lower the bar. Include these four anchors (or close paraphrases):
- `with high model facial features`
- `symmetrical features`
- `well-proportioned figure`
- `natural skin texture`

### Override rule
Anything the user specifies (setting, clothing, mood, hair colour, ethnicity, time of day) wins over every default below. Defaults only fill gaps. Skip the matching variety pick when the user gave a value, and use their value verbatim. Tone words in the brief (goth, noir, deadpan, clinical, refined, minimal, Y2K, streetwear, preppy, coastal, boho, editorial, leather-grit, quiet-luxury) select the matching register and expression. Voice, accent and speech style never enter the image prompt, only what a still can show (a deadpan persona gets `natural unguarded face, soft neutral expression, not smiling at the camera`; a physical quirk's worn prop, such as stacked rings or reading glasses, must be visible and worn, never held).

### Product-logic casting (category gate, runs before the variety picks)
The look must leave room for the product to work. If the "before" already looks like the "after", the pitch is dead. General law: identify what the product changes, then undo that change in the creator's default look.

| Product category | Appearance lock |
|---|---|
| Skincare / cosmetics / beauty devices | Makeup register forced to `bare-skin no-makeup`. If the product IS makeup, the face still starts bare; application happens in the video. |
| Haircare | Hair worn DOWN with natural texture: shoulder-length wavy, long sleek straight, long with soft waves, medium with curtain bangs, sleek bob (chin-length), wolf cut, half-up half-down. No slicked-back, buns, braids, ponytails, updos. |
| Teeth / smile products | Natural real teeth visible, a smiling or mid-laugh expression, never a veneer-perfect smile. |
| Sleep / energy products | Slight under-eye shadows: an honest "before", tired-but-attractive, never haggard. |
| Fitness / supplements | Believable body from the rolled build; a slight post-workout flush beats gym-model polish. |
| Fashion / accessories / jewelry | Opposite: full styling allowed and expected. |

Bare face is not bad skin: it renders as visible pores and natural unevenness on a model-tier face.

## 2. Variety pools

To defeat the model's bias toward "familiar" options, pick from each pool with a random number (`pool[roll % size]`) instead of choosing by feel. Never reuse the same set of picks for two creators in one project. A user value skips that pool.

- Age band (4): early 20s; mid 20s; late 20s; early 30s
- Hair colour (14): warm honey blonde; cool ash blonde; chestnut; espresso; soft brown; jet black; deep auburn; copper; platinum; honey balayage; money-piece highlights; vivid green; vivid pink; pastel lavender
- Hair length and style (14): shoulder-length wavy; long sleek straight; long with soft waves; medium with curtain bangs; sleek bob (chin-length); pixie cut; wolf cut; claw-clip slicked back; messy low bun; half-up half-down; boxer braids; high ponytail; dreadlocks (locs); shaved buzz cut
- Build / vibe (5): athletic toned; soft natural; average proportional; petite; tall everyday
- Distinctive feature (6): clean (none); natural freckles across cheekbones; delicate nose stud; dimples; gap teeth; subtle beauty mole on cheek
- Makeup register (9): bare-skin no-makeup; casual natural; glowy with mascara only; soft brown smoky eye; playful winged liner; bold colored eyeliner accent; brushed-up feathered brows, bare lids; graphic blush draped across cheekbones; glossy lip with neutral face
- Face read (8): fair European; warm Mediterranean; East Asian; South Asian; Latina; mixed; Middle Eastern; Slavic. Render the face by FEATURES, not by writing the ethnicity word (a user-supplied ethnicity is the only exception).
- Outfit aesthetic register (10): streetwear-oversized; preppy / equestrian; Y2K-coded; quiet-luxury; coastal-minimal; sporty-jersey; editorial-blazer-cool; boho-soft; leather-grit; clean-minimalist

Glitter ban: never write glitter, shimmer, sparkle or "inner-corner highlight" in any makeup register. It is a known render-slop signature.

### One bold visual anchor
Exactly ONE loud element per creator, derived from the picks, never added on top. Scan in priority order and take the first hit: (1) vivid or unusual hair colour (vivid green, vivid pink, pastel lavender, platinum, copper); (2) statement hair style (buzz cut, boxer braids, wolf cut, locs); (3) loud distinctive feature (gap teeth); (4) otherwise one statement accessory (chunky chain choker, statement cap, layered pendants). Give the anchor the richest description ("vivid bubblegum-pink hair with blunt bangs and a glassy sheen") and keep everything else quiet. Two anchors compete, three is noise.

### Feminine legibility guard (women only)
If two or more are true, add the clause `soft feminine facial features, a delicate jawline, smooth cheekbones, naturally full lips, and defined natural lashes` next to the beauty-floor anchors and do not use the hair as the anchor: (A) hair is pixie cut / wolf cut / boxer braids / locs / buzz cut; (B) bare face; (C) figure-hiding top (oversized tee, hoodie, jersey, boxy cut with no waist).

### Anti-clone
Compare with the previous creator on age band, hair colour, hair style, build. The new one must differ on at least two. If three or more match, shift the conflicting picks to the next option in the pool.

### Casting for the offer (the one-degree bend)
When the pick lines up too perfectly with the product stereotype (skincare = glowy polished, fitness = sporty jersey), bend by ONE small against-type detail: the fitness creator wears delicate reading glasses, the finance-app minimalist has the pink hair in a claw clip, the snack-food creator keeps a deadpan face. One detail, never two, never a second anchor.

## 3. Wardrobe, location, lighting

### Register vocabulary
- streetwear-oversized: oversized graphic tee or hoodie + baggy / wide-leg trousers or denim + chunky sneakers + layered chain necklaces
- preppy / equestrian: blazer + silk neck-tie or cream silk blouse + leather accents (gloves / belt) + structured bag
- Y2K-coded: mini skirt or slip dress + butterfly hair clips + chunky choker + small bag
- quiet-luxury: cashmere or merino knit + tailored trousers + delicate gold jewelry + minimal leather accessories
- coastal-minimal: linen shirt + cream wide-leg trousers + simple gold hoops + woven / leather sandals
- sporty-jersey: oversized sports jersey or polo + baggy trousers or shorts + bandana or hair clip + sneakers
- editorial-blazer-cool: pinstripe or tailored blazer over tank / camisole + chunky chain choker + statement sunglasses
- boho-soft: slip dress or silk camisole + open cardigan + layered pendants + soft sandals
- leather-grit: leather jacket layer over knit or tee + dark denim or trousers + statement cap + boots
- clean-minimalist: fitted white shirt or knit + denim or trousers + delicate jewelry (the most stock register, pick others more often)

Tier calibrates materials: luxury reads silk / cashmere / designer / fine gold; premium reads quality cotton / branded / considered finishing; drugstore reads everyday cotton / thrift-tier / plastic clips / basic chains. Register gives the SHAPE, tier gives the REFINEMENT. If the rolled register is physically wrong for the product you may shift it by one, once.

Accessories are ONE system of 2-3 related pieces in ONE metal family (silver OR gold, never both), worn only, never held.

### Style DNA laws (every outfit)
1. Silhouette contrast is the engine: fitted top + voluminous bottom OR oversized top + slim/short bottom. Never fitted + fitted, never baggy + baggy.
2. Monochrome base + ONE metal: black / white / cream dominates; silver default, gold for warm retro looks.
3. White ribbed socks are a signature (with flats, loafers, platform boots).
4. Eyewear as anchor: Y2K shield, slim rectangular tinted, chrome sport frames, oversized nerd glasses; counts as the one bold anchor when used.
5. Headphones are jewelry: chunky over-ear or wired earbuds with visible cord, WORN, never held.
6. Texture over print: ribbed cotton, crinkled crepe, parachute nylon, mohair fuzz, patent leather, washed denim. Print size law: any print or lettering is BIG (a bold graphic or wordmark filling the chest, `large varsity-style wordmark across the full chest`). Small logos and tiny lettering render as gibberish. All lettering fictional.
7. One deliberate imperfection: sleeves shoved to elbows, one strap slipping, shirt untucked on one side, cuffs unbuttoned, loose hair strands.

### Recipes (women W1-W18, men M1-M4). Hair always comes from the hair pick, never from the recipe.
- W1 Balloon Noir: black sleeveless mock-neck fitted top + black parachute-nylon balloon trousers cinched at the ankles + black platform-heel sandals + thin silver chain belt.
- W2 Airy Gallery: white crinkled-crepe boxy sleeveless top + black wide knee-length culotte shorts + white ribbed socks + black leather ballet flats + wide silver cuff.
- W3 London Errand: oversized navy-white breton stripe long-sleeve tee + black capri leggings with side slits + black ballet flats + oxblood leather shoulder bag.
- W4 Seoul Soft-Office: oversized powder-blue cotton shirt, sleeves rolled once + navy A-line midi skirt + grey retro running sneakers + caramel croc-texture shoulder bag.
- W5 Sydney Minimal: oversized white heavyweight tee tucked loosely front-only + black pleated wide bermuda shorts + white ribbed socks + black penny loafers + tiny gold hoops.
- W6 Slick Capri: black fitted sleeveless boat-neck top + black kick-flare capri trousers + black puffy platform slides + narrow black oval sunglasses + cream canvas tote.
- W7 Dark-Street Otaku: washed-black oversized graphic tee (big faded fictional print filling the chest) + black wide shorts + black crew socks + chunky lug-sole boots + chunky black over-ear headphones.
- W8 Milan Prep Noir: oversized double-breasted black blazer + white shirt + black pleated skirt + sheer black tights + white ribbed socks + black chunky loafers.
- W9 90s Sitcom It-Girl: white cap-sleeve baby tee under black fitted tank + black velvet mini skirt + knee-high black leather boots.
- W10 Y2K Chrome Maximal: washed denim corset top + super-wide dark carpenter jeans with embroidered fictional patches + sculptural chrome rings + mirrored wrap sunglasses.
- W11 Newsprint Bodycon: newsprint-pattern fitted mini dress (oversized fictional newsprint graphic).
- W12 Y2K Dancer: cropped boxy leather jacket over a black bralette + low-rise super-wide charcoal jeans with double studded belts + platform boots.
- W13 Blur-Flash Grunge: cream ribbed tank with a big faded fictional college arc across the chest + slim rimless tinted sunglasses + layered silver chains.
- W14 Chrome Baby-Tee: grey-navy raglan baby tee with a bold fictional varsity print filling the chest + chrome wraparound sport glasses low on the nose.
- W15 Fuzzy Y2K Cafe: pink-red striped fuzzy mohair crop sweater + washed denim mini skirt + wired earbuds around the neck + fuzzy pink wrist warmers.
- W16 Mesh Rave Prep: acid-green printed mesh long-sleeve over a black bralette + black-white plaid pleated wide culottes + gunmetal moto-hardware shoulder bag.
- W17 Cyber Sport Tank: black fitted cropped tank + grey camo baggy cargos + black studded star belt + chunky black headphones around the neck + silver star pendant.
- W18 Studio Wolf-Cut: black fitted halter tank + slim silver pendant + yellow-tinted rimless shield glasses.
- M1 Desert Cowboy Sport: cream straw cowboy hat + white retro soccer jersey with green trim (big fictional crest) + black super-wide side-stripe trousers + black-stripe retro sneakers + narrow black sunglasses.
- M2 Nerd-Prep Denim: oversized washed-denim chore jacket + white shirt buttoned to the collar + navy-red striped tie + oversized black nerd glasses.
- M3 Knit Maximalist: oversized varsity-pattern knit cardigan in burgundy-cream (large fictional lettering) + light-wash balloon jeans cuffed high + black western boots + stacked silver rings.
- M4 Paris Street: navy fitted tank over a grey baby tee + light-grey parachute pants + silver wraparound sport sunglasses + silver chain + chunky headphones around the neck + cross-body strap bag.

Coverage adaptation: recipes built on a bralette, crop top, halter, corset or standalone tank get a closed layer over them (W12's jacket zipped to the chest; W16 gets an opaque black top beneath and a jacket over; tanks and corsets go under an overshirt or jacket), so the frame passes any generator's filters.

Register to recipe subset (women / men): streetwear-oversized W7, W17 / M4; preppy W3, W8 / M2; Y2K W9, W10, W12, W15, W16 / M3; quiet-luxury W1, W4 / M2; coastal-minimal W3, W5 / M1; sporty-jersey W14, W18 / M1; editorial-blazer-cool W6, W8, W11 / M2; boho-soft W11, W15 / M3; leather-grit W12, W13 / M3; clean-minimalist W2, W5 / M2. Pick inside the subset with `(hair colour roll + hair style roll) % subset size`. Invent an outfit only when no recipe covers the brief, and then still obey the Style DNA laws.

Hair and face phrasing bank: name bangs precisely (curtain bangs, full blunt bangs, wispy micro-bangs, face-framing pieces); the bob family reads French bob / chin-length bob / shag bob; buns read slick OR messy-curly; blowouts read layered; loose strands are the deliberate imperfection.

### Location x tier x wardrobe matrix (when no location override)
| Category | Tier | Default location | Wardrobe |
|---|---|---|---|
| Cosmetics / makeup / fragrance | luxury | stylish modern bedroom or vanity nook, paneled walls, statement mirror | silk or satin robe tightly tied at the waist with closed modest neckline and lapels overlapping fully, OR designer pajama set, OR already dressed for going out with a curated outfit |
| same | premium | bright clean modern bathroom or bedroom | premium cotton robe tightly tied, casual chic top, or lounge-luxe set in neutrals |
| same | drugstore | everyday bright bathroom or bedroom, lived-in | cozy oversized cotton robe tightly tied / soft hoodie / casual fitted top |
| Skincare / haircare / body care | luxury | spa-like bathroom, marble, brass fixtures, plants | silk robe or premium bathrobe in muted tones, tightly tied, lapels overlapping |
| same | premium | bright modern bathroom, clean tile, matte fixtures | cream / oatmeal cotton robe tightly tied, casual lounge wear |
| same | drugstore | standard bright bathroom, friendly and lived-in | cozy oversized robe tightly tied, casual t-shirt |
| Food / beverages / kitchen | any | modern kitchen, finish by tier (luxury marble + brass; premium white cabinetry + stainless; mass bright friendly) | casual chic: fitted blouse + jeans, knit top, or athleisure if health-coded |
| Protein / supplements | any | home gym (dumbbells, mat, mirror, plants) OR bright kitchen (powder/shaker = kitchen) | athleisure fitted top, joggers or leggings, fresh-from-workout vibe |
| Clothing / accessories / jewelry / watches | luxury | stylish bedroom or dressing room, wardrobe rack | curated outfit, already styled: silk camisole + tailored trousers, or refined knit + slip skirt |
| same | premium | bedroom / living room with elevated styling | casual chic: relaxed fitted top, high-waisted trousers, layered minimal jewelry |
| same | drugstore | bedroom / living room, everyday cozy | casual relaxed outfit, comfortable layers |
| Fitness equipment | any | home gym, living-room mat area or yoga corner with plants and natural light | athletic wear matching the discipline |
| Cars | any | outdoors next to the car: driveway, sunlit street, garage with the door open | stylish casual outerwear, tier elevates (luxury: tailored coat, designer shades) |
| Outdoor gear / sunglasses / sunscreen | any | outdoor cafe terrace, park, sunlit street | outfit for season + tier |
| Tech / electronics / audio | any | home desk, living room or studio nook | smart casual: fitted knit, button-down, relaxed athleisure |
| Home / decor / candles | any | living room or bedroom with the relevant ambiance | lounge-elevated: soft knit, relaxed trousers, cozy set |
| Everything else | any | cozy home: bedroom or living room | casual everyday outfit |

Outdoor is used only when the product belongs there. Rotate through the wardrobe options in a row, never default to a button-down for everyone, and do not add a camisole base layer to every outfit.

### Location detail
A named location alone ("kitchen") produces a plain wall. Always add: what is in the background (furniture, cabinetry, shelving, plants), materials (marble, wood, tile, linen, brass), and the palette in one line (one dominant field, one secondary tone, at most ONE loud accent; if the creator has a bold anchor, the anchor IS the accent). Wardrobe colour must share at least one tone with the room palette. World-logic chain: the product's world is in the room (a whisk lives in a kitchen with flour on the counter, the product itself still absent), the outfit fits the room (no heels on a trail), and practitioner spaces show practitioner details (worn equipment, tools racked properly).

### Lighting
Always give direction and quality ("soft natural daylight streaming in from the left window", "cool diffused daylight from the right"). Default: neutral cool daylight only: "cool neutral daylight", "soft diffused white light", "clean midday light", "overcast diffusion". Hard ban: golden hour, warm sunset, orange/amber/honey cast, late-afternoon warm wash, magic hour, even outdoors (they make the persona look like a stock ad). Never studio strobes, never a pure white seamless background unless asked. Let the light interact with surfaces in the room.

## 4. Camera language

The frame must read as a real creator's phone photo. This is the single most important rule.

Mandatory phrasing (include all, verbatim or close):
- `Self-portrait selfie shot on iPhone front-facing camera held by the subject at arm's length, head and shoulders fill the frame`
- `Selfie geometry: subject's own arm extended toward the lens, hand or wrist may faintly appear at the edge of frame holding the phone`
- `Slightly off-center, slightly imperfect framing, not posed, not studio-centered`
- `Spontaneous angle with a slight casual tilt, intuitive composition, not symmetric, not centered`
- `Captured mid-moment, NOT a formal pose for the camera`
- `Subject minimally aware of the lens, relaxed, natural, like she just turned the camera on`
- `Phone-sensor grain and realistic skin pores and texture preserved, no retouch, no smooth-skin filter, no professional gloss`
- `Subject in clear focus with the background falling out naturally as in any phone photo`
- `Authentic UGC creator phone selfie, taken by herself with her own front camera at arm's length, NOT editorial fashion photography, NOT studio portrait, NOT magazine retouch`

Hard ban list (each flips the render to editorial or studio): `centered composition at eye-level`, `straight-on`, `mid-length portrait` / `editorial portrait` / `fashion portrait`, `minimal depth of field, soft subtle separation`, `editorial mood` / `editorial atmosphere` / `crisp editorial`, `aspirational lifestyle atmosphere`, `flattering and even illumination`, `glowing skin` / `flawless skin` / `radiant complexion`, `poised` / `refined expression` / `dignified pose` / `elegant stance` / `graceful posture`, `warm smile at the camera` / `looking at the camera with a smile` / `direct eye contact with the camera and a confident smile`, any pose verb (`poses`, `is posing`, `striking a pose`, `stands gracefully`), anything implying a static camera, studio strobe, ring light, beauty dish or professional camera body, and fisheye / ultra-wide / GoPro-warp (the front camera reads as standard lens language, at most mild phone wideness).

Approved mid-action expressions (pick ONE per prompt, never `warm smile`):
- mid-thought, slight half-smile, eyes glancing slightly off-lens
- caught mid-laugh, soft natural laugh, head slightly tilted
- casually glancing toward the lens with a relaxed, neutral expression
- looking up from her phone with a relaxed, unguarded face
- mid-action expression, in the middle of saying something, not posing
- natural unguarded face, soft neutral expression, not smiling at the camera
- wide-eyed mid-gasp, lips parted, brows lifted, caught at the start of a reaction
- mid-laugh with mouth open, head thrown slightly back, shoulders shifted
- playful mock-shock: round eyes, slight grin breaking under the surprise
- mid-react squint: one eye scrunching, half-grin pulling sideways
- eyebrows lifted mid-thought, lips pressed in a "wait, no" line, head tilted slightly

Body pose: neutral only (relaxed standing, weight slightly on one hip, one hand resting naturally, head level). Interest lives in face, wardrobe and the one bold anchor. Never a hand thrust at the lens, jumps, low-angle looming, limbs toward the camera, framing the face with the hands, biting glasses (extended limbs warp, foreshortened hands grow fingers).

Coverage language (apply to every outfit, generators otherwise default to plunging cuts that trip filters): append `top fully closed at the front, fabric meeting at the collarbone, classic high-coverage fit`. Per garment: shirt `fully buttoned to at least the second-from-top button`; knit `modest crew or scoop neckline, no V-cut`; blouse `modest closed neckline, no plunging V, no deep decolletage`; robe `tightly tied at the waist with sash visible, both lapels overlapping fully across the chest`; t-shirt `fitted but with a modest crew neckline`; tank/camisole never standalone, only layered under a shirt/cardigan/blazer; athletic top `high crew or modest scoop neckline, fully covering chest`. Prefer positive phrasing (`fully buttoned to the collar`) over negations, because text encoders prime on the negated words.

Closing block (append verbatim to every creator prompt):
```
Self-portrait selfie shot on iPhone front-facing camera held by the subject at arm's length, head and shoulders fill the frame, casual handheld framing, slight natural tilt, slightly off-center, slightly imperfect, not posed. Phone-sensor grain and realistic skin texture preserved, no retouch, no smooth-skin filter. No fisheye lens, no ultra-wide distortion. Authentic UGC creator phone selfie, NOT editorial portrait, NOT fashion magazine.
```

Safety: adult, 21+ look only; never a recognizable public figure, celebrity, minor or non-consenting real person; a text description must produce an original fictional adult. If a detailed brief asks for bare skin or intimate anatomy, adapt by weaving in clothing that covers sensitive areas rather than discarding the prompt.

## 5. Prompt structure

Gender follows the brief; never mix genders in one prompt.

```
A [age band] [man/woman], [mid-action expression], [hair colour + length/style], [build vibe], with high model facial features, symmetrical features, well-proportioned figure, natural skin texture, standing in a [specific location with architectural details].
[Light direction and quality, cool/neutral daylight] falls across [her/his] face, neutral, clean, no warm cast, no retouched glow. Skin texture is real, with visible pores and natural unevenness.
[He/She] wears [outfit from the matrix or a recipe, with the coverage language]. Body in a calm neutral pose, relaxed standing, one hand resting naturally.
The background features [materials, colours, furniture].
Color palette dominated by [space colours, neutrals, no amber/orange dominance].
Casual handheld iPhone selfie taken by [her/him] at arm's length, head and shoulders fill the frame, slight natural tilt, slightly off-center, intuitive composition, captured mid-moment. Subject in clear focus with the background naturally falling out as in any phone photo.
[closing block]
```
The bold anchor lives in line 1, with the richest clause.

### Worked example (kitchen, premium food/beverage, recipe W4)
```
A spontaneous iPhone snap of a young woman in her early 20s, mid-thought with a slight half-smile, eyes glancing slightly off-lens, with high model facial features, symmetrical features, well-proportioned figure, natural skin texture, standing in a modern, bright kitchen. Soft natural window light streams in from the left across her face, clean, neutral, no warm cast, no retouched glow. Skin texture is real, with visible pores and natural unevenness. She wears a casual chic outfit: an oversized powder-blue cotton shirt with the sleeves rolled once, fully buttoned to at least the second-from-top button, top fully closed at the front, fabric meeting at the collarbone, classic high-coverage fit, tucked loosely into a navy A-line midi skirt, with grey retro running sneakers and a caramel croc-texture shoulder bag worn on one shoulder. Body in a calm neutral pose, relaxed standing, one hand resting naturally. The kitchen background is defined by pristine white cabinetry, stainless steel hardware, and subtle recessed lighting. Casual handheld iPhone selfie taken by her at arm's length, head and shoulders fill the frame, slight natural tilt, slightly off-center, intuitive composition, captured mid-moment. Subject in clear focus with the background naturally falling out as in any phone photo. The color palette is bright, dominated by whites, beiges, and subtle tan accents. Self-portrait selfie shot on iPhone front-facing camera held by her at arm's length. Phone-sensor grain and realistic skin texture preserved, no retouch, no smooth-skin filter. No fisheye lens, no ultra-wide distortion. Authentic UGC creator phone selfie, NOT editorial portrait, NOT fashion magazine.
```

### Worked example (bathroom, skincare, premium, bare face)
```
A spontaneous iPhone snap of a young woman in her mid-20s, casually glancing toward the lens with a relaxed, neutral expression, with high model facial features, symmetrical features, well-proportioned figure, natural skin texture, standing in a bright modern bathroom. Soft diffused daylight from the left falls across her face, neutral cool, no warm cast, no retouched glow. Skin texture is real, with visible pores and natural unevenness. She wears a cozy oversized cream-colored robe tightly tied at the waist with a closed modest neckline and lapels overlapping fully, casual and relaxed. Body in a calm neutral pose, relaxed standing, one hand resting naturally. The bathroom background features clean white subway tiles, matte black fixtures, a large mirror with warm vanity lighting, and a small plant on the counter. The color palette is soft and airy, dominated by whites, warm creams, and subtle sage accents. Casual handheld iPhone selfie taken by her at arm's length, head and shoulders fill the frame, slight natural tilt, slightly off-center, intuitive composition, captured mid-moment. Subject in clear focus with the background naturally falling out as in any phone photo. Self-portrait selfie shot on iPhone front-facing camera held by her at arm's length. Phone-sensor grain and realistic skin texture preserved, no retouch, no smooth-skin filter. No fisheye lens, no ultra-wide distortion. Authentic UGC creator phone selfie, NOT editorial portrait, NOT fashion magazine.
```

### Worked example (home gym, supplement, athletic set)
```
A spontaneous iPhone snap of a young woman in her early 20s, mid-action, in the middle of saying something, not posing, with high model facial features, symmetrical features, well-proportioned figure, natural skin texture, standing in a bright home gym corner. Soft natural daylight streams in from a tall window on the right, falling cleanly across her face and the matte rubber flooring, neutral, clean, no warm cast, no retouched glow. Skin texture is real, with visible pores and natural unevenness. She wears a fitted athletic set: a sage compression top with a high crew neckline, fully covering chest, paired with high-waisted leggings, with a slight post-workout flush and a few loose strands of hair framing her face. Body in a calm neutral pose, relaxed standing, one hand resting naturally. The background features a stack of clean dumbbells on a wooden rack, a rolled yoga mat, a tall potted plant, and a wall-mounted mirror reflecting soft light. The color palette is fresh and grounded, dominated by warm whites, muted sage greens, and natural wood tones. Casual handheld iPhone selfie taken by her at arm's length, head and shoulders fill the frame, slight natural tilt, slightly off-center, intuitive composition, captured mid-moment. Subject in clear focus with the background naturally falling out as in any phone photo. Self-portrait selfie shot on iPhone front-facing camera held by her at arm's length. Phone-sensor grain and realistic skin texture preserved, no retouch, no smooth-skin filter. No fisheye lens, no ultra-wide distortion. Authentic UGC creator phone selfie, NOT editorial portrait, NOT fashion magazine.
```
