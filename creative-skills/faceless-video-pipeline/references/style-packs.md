# Style packs: locked looks for faceless video

Contents
0. How a style lock works (formula, palette lock, motion slot, negatives, accent)
1. Defaults per channel type and the cross-channel rule
2. Stickman Cartoon (generic formula)
3. Editorial Motion Graphics (editorial collage)
4. Paper Diorama
5. Mannequin
6. Cinematic Storybook (Fairy Tale / Myth)
7. Watercolor Chronicle (long-form history)
8. Flat 2D Papercraft (stills default)
9. Kids styles 1 to 5 (Studio 3D, Pastel Flat 2D, Colorful 3D, Hand-drawn Ink, Poster Vector)
10. Style-inherent extras (music, cadence)

Copy a formula BYTE-IDENTICAL into every image and video prompt of the video: that repetition is the whole consistency mechanism. Fill the `{ACCENT}` slot once per video and never change it.

## 0. How a style lock works

A style lock is five things, all pasted verbatim into every prompt:
1. **STYLE FORMULA**: 80 to 100 words, at most 2 sentences: line and surface work, shading, palette, one signature accent, background treatment, motion timing, render discipline, written in positive form. Always non-photorealistic.
2. **PALETTE LOCK line**: "use ONLY the colors and the background treatment of the reference images". It stops the generator from adding new colours or gradient backgrounds.
3. **{MOTION} slot**: how things move in this look. Flat 2D families: `simple limited animation on twos`. Dimensional families: `smooth simple handcrafted motion, subtle stop-motion feel`. Keep `3D render` in the NEGATIVE for flat 2D looks, drop it for dimensional looks; the photorealism ban always stays.
4. **NEGATIVE list**: style drift and realism bans (see the block template in `prompts-and-blocks.md`).
5. **Style key image**: one generated sample image of the look, attached as a reference to every asset and shot. It is a look anchor, not a final frame; tell the user it can look slightly odd or abstract, that is normal. If you have 2 or 3 images that show the look (your own earlier frames, a reference), attach them as STYLE DONORS to the key generation: take the render style, palette and surface treatment, never the subjects or composition. With uploaded donors, prefix: "Take only the visual render style and color grading of the input image(s)... never use the characters, inscriptions, etc."

Style key prompt (pretty and legible, not formless blobs):
"A clean {STYLE} STYLE SAMPLE: one simple recognizable subject (a small friendly object or mini-scene) rendered in the style so its line weight, shading and colours read at a glance. Balanced, attractive, easy to read. No palette strip, no colour chips, no swatch bar, no colour squares, no labels, no text, no watermark, no reference-sheet layout."
Anything drawn into the key (swatches, labels) can propagate into the video, so ban it in the key prompt.

Generic rules:
- Never name a real comic, studio, brand or IP in a prompt; describe the look.
- Banned tokens in video prompts: `child`, `kid`, `childlike` (use `naive`, `small`, `simple`); video-model safety filters trip on them.
- Characters only emote and gesture, they do not talk (the voice is an external narrator), except where a format explicitly says otherwise.

## 1. Defaults per channel type and the cross-channel rule

| Channel type | Default style | Named alternates |
|---|---|---|
| Explainer | Editorial Motion Graphics (recommended) | Stickman Cartoon (second main direction); any style below |
| History | Editorial Motion Graphics | Paper Diorama (geopolitics, money, power, "cinematic"), Mannequin (battles, expeditions, intrigue), Watercolor Chronicle (long-form 10+ min) |
| Kids | Studio 3D | Pastel Flat 2D, Colorful 3D, Hand-drawn Ink, Poster Vector, Fluffy Toy |
| Fairy Tale and Myth | Cinematic Storybook | none (the only style) |
| Picture Story (stills) | Flat 2D Papercraft | Stickman Cartoon, Hand-drawn Ink |

Cross-channel rule: any style is legal on any channel type. A style brings ONLY its look (formula, palette lock, motion slot, negatives, style-inherent laws such as Mannequin's cast rules). Everything narrative stays with the channel type: cut pattern (the Kids 4-cut pattern belongs to the Kids channel; a History run in Studio 3D still uses 5 cuts), beat grammar, script rules, voice tone. Kids-catalog looks carry one extra: a wordless music bed. Cinematic Storybook carries two: on-twos cadence and a mysterious-calm bed.

Do not silently replace a style the user named with the channel default. A style named by the user is locked.

Legacy looks without a pinned formula (Fluffy Toy, 3D Papercraft, Mixed Media, Whiteboard Doodle, Pixel Art, Claymotion, Low Poly, Isometric Flat Vector, 3D Mix, 2D Illustrator): attach a reference image of the look, and WRITE the formula yourself from its visible traits (line and surface work, shading, palette, background, motion) in 80 to 100 words, then lock it. See `explainer-presets.md`.

## 2. Stickman Cartoon (generic formula)

Explainer's second main direction. Crude paint-program webcomic: thin wobbly black outlines, flat solid fills, egg-head dot-eye stick figures, plain flat-color backgrounds. Never name a real comic.

> flat 2D webcomic cartoon, extremely minimal - uniform thin even-weight black outlines, egg-shaped heads with tiny dot eyes and a single line mouth, plain noodle limbs, solid flat color fills with NO shading, NO gradients, NO texture, deadpan minimalist design, plain flat solid-color backgrounds.

{MOTION}: flat, `simple limited animation on twos`; keep `3D render` in the NEGATIVE.
PALETTE LOCK: the flat off-white / clean webcomic background of the references; no new colours.

## 3. Editorial Motion Graphics (editorial collage)

Flagship house style, default for History AND Explainer. A motion-designed editorial documentary collage: warm cream-paper stage, monochrome halftone archival cutouts, ONE accent color doing all the talking; a magazine spread that moves like a news documentary, never filmed footage. Strongest on data stories, economics, history, "the real reason X" topics.

One-liner (use verbatim as the option description): "Editorial documentary collage - cream paper, monochrome archival cutouts, one bold accent color (the big disc, the one colored hero); the voiceover carries all words (no on-screen text)." Never describe it as "kinetic text" or "data on screen": in-clip words are banned in it.

STYLE FORMULA:

> flat editorial documentary collage on a warm cream paper stage with subtle fiber grain: monochrome halftone archival photo cutouts with rough white keylines and a slightly offset {ACCENT} stroke behind each cutout, one single {ACCENT} accent color per video - a large flat {ACCENT} disc behind the main subject and exactly one color-popped hero element among the monochrome - torn paper edges and tape strips, soft paper drop shadows, hand-drawn {ACCENT} marker circles, arrows and underline strokes (abstract strokes only, never letters), abstract unlabeled data shapes and flat stylized maps, subtle print misregistration on inked elements, snappy staggered spring motion with slight overshoot, non-photorealistic illustrated collage, never live-action.

**{ACCENT}: lock ONE accent color per VIDEO** (write it into the formula and the PALETTE LOCK verbatim; never mix accents across blocks). Burnt orange is the classic, not the law: burnt orange, coral red, mustard gold, petrol blue, deep crimson, forest green. Within a shot the disc + ONE color-popped element + strokes is plenty; let some shots breathe with monochrome only.

The layer model (name the layers in shot beats):
- BACKGROUND, the locked stage: warm cream paper field with fiber grain. Within a block the stage NEVER changes; cuts re-compose the elements, not the world. Between blocks a location is its own stage plate. Optionally one large flat {ACCENT} disc or half-disc anchors the composition behind the subject.
- MIDGROUND, the subjects: monochrome halftone cutouts (people, cars, buildings, objects) with rough white keylines and the offset {ACCENT} stroke; paper puppets that enter, act, leave.
- FOREGROUND, the devices: props, charts, maps, annotation strokes, where the {ACCENT} lives. The through-line object sits here.

Signature composition devices (rotate them; each shot uses 1 to 2):
- The disc: a big flat {ACCENT} circle or half-circle behind the monochrome subject, the style's poster shot.
- The color pop: exactly ONE element rendered in {ACCENT} (or full color) among the monochrome, the hero of the beat (the one figure in an orange suit in a grey lineup). Never two.
- The giant hand: an oversized monochrome photographic hand entering from off-frame to place, hold, tilt or flick a cutout prop.
- The timeline ribbon: a thin baseline ribbon with tick marks and a sliding marker along the bottom, measuring progress or eras WITHOUT numerals (the VO names the years).
- The on-photo callout: an {ACCENT} marker circle or arrow drawing itself DIRECTLY ON a photo cutout, isolating one detail; pairs with a slow push-in.
- Dot-matrix data: charts built from halftone DOTS (a semicircle gauge filling dot by dot, a bar of dots stacking, a share of dots flipping to {ACCENT}); reads as print, not as UI; still no axis text or numerals.
- Pinned cards: photo cards with white borders and tape strips or a push pin, planted onto the stage (the giant hand loves planting these); a card can flip over or slide a torn edge.
- Working set: marker circles, arrows, underlines drawing themselves; abstract data graphics (bars grow, lines draw, slices separate, no axis text); flat maps with routes and pulsing pins; redaction/highlight bars; scale comparisons (one cutout multiplying into rows, the through-line's natural home).

{MOTION}: flat family, `snappy motion-graphics collage animation, staggered spring entrances with slight overshoot`; keep `3D render` in the NEGATIVE.

PALETTE LOCK: `warm cream paper base, monochrome halftone cutouts, ONE {ACCENT} accent (disc, strokes, one popped element) - no other colors, no gradients, no full-color scenes`.

Asset roster guidance:
- Characters (2:3): monochrome halftone cutout figures with white keyline + offset {ACCENT} stroke, readable era-true silhouette, deadpan neutral poses (annotation marks do the emoting). A protagonist may be the recurring color-pop.
- Locations (chosen aspect): FLAT stage plates are the style's treatment: a cream field with a taped flat map and pins; a soft graph-grid notebook field with an unlabeled dot-matrix chart zone; a newsprint strip with torn-edge photo frames; a plate with the big {ACCENT} disc and a standing arrangement of cutouts; and, sparingly (at most 2 blocks per video), a DARK evidence board with pinned photo cards, taped notes and {ACCENT} connection strokes. One named anchor device each. A coverage angle = a RE-COMPOSITION of the same plate (elements re-arranged, different crop), never a camera orbit.
- Props (1:1): individual cutouts: the {ACCENT} through-line object, a building, an arrow set, a redaction bar pack, the giant hand. Give the through-line its own prop asset so it never morphs.

Shot language (write each SHOT as pure choreography, layers named: stage / cutouts / devices):
- The cuts vary composition scale on the SAME stage: FULL-SPREAD (whole plate), DETAIL (one cutout + its annotation), RE-COMPOSITION (payoff arrangement).
- Stagger everything: elements never arrive simultaneously; "A, then B, then C, staggered" is the highest-value phrase; spring pop-ups with slight overshoot.
- Land the motion: arrival verbs (snaps into place, stamps down, drops with a bounce, tapes down, settles). Floaty = badly directed.
- ONE camera behavior per shot, stated once: slow push-in, static, gentle drift, whip to the right. Never two moves in one cut; the stage's calm IS the style.
- Settle beat: the FINAL shot eases into a stable final frame (clean cut point), still micro-moving (settled is not frozen).
- Every block lands at least ONE impact beat: a cutout SLAMS in, a redaction bar STAMPS down, the giant hand PLANTS a prop; name it in the SHOT text and echo it in AUDIO (reference-grade explainers hit an accent about every 3 s).

AUDIO line (SFX follows choreography 1:1): every motion verb gets at most ONE sound cue; nothing sounds that did not move. 2 to 4 cues per block + one bed: paper pops and thwips on entrances, a stamp hit on the impact beat, soft tick-tick on data steps, low newsroom-air bed underneath. Percussive, never musical; the bed is room tone, not a track.

In-clip text: NONE. Every typography beat is an abstract device (highlight bar, redaction block, circle, the timeline ribbon). Symbols allowed (warning sign, $, check, cross); words and numerals never; the VO carries them. Append to NEGATIVE: `readable text, letters, words, numbers, live-action footage, photographic realism, full-color scene, foreign accent colors`.

## 4. Paper Diorama

History's named alternate; reach for it whenever the topic is geopolitics, money, power, institutions, investigation, or the user asks for "cinematic". Cinematic vintage paper-diorama documentary: miniature table-top worlds built from aged sepia newsprint and cardboard, anonymous halftone cutout figures, ONE accent color locked per video, tungsten light, macro tilt-shift.

One-liner (verbatim): "Cinematic paper-diorama documentary - miniature sepia newsprint worlds, tactile cutout figures, one accent color, moody tungsten light."

STYLE FORMULA:

> cinematic vintage paper-diorama documentary: miniature table-top worlds built from aged sepia newsprint and cardboard, torn layered paper edges, monochrome halftone print texture, anonymous halftone cutout figures with obscured faces, one single {ACCENT} paper accent, distressed letterpress texture on props, warm tungsten documentary lighting with deep shadows, macro tilt-shift shallow depth of field, film grain and floating paper dust, smooth handcrafted stop-motion motion, non-photorealistic handcrafted paper materials only.

**{ACCENT}: lock ONE per VIDEO** (formula + PALETTE LOCK verbatim; never mix across blocks): burnt orange, deep crimson, petrol blue, mustard gold, forest green, faded teal. Within scenes 1 to 2 accent objects max, and let some shots breathe with NO accent at all; an all-accent video reads as a gimmick.

Anonymity: vary the device, do not stamp censor bars on everyone. Faces are obscured, but rotate HOW: blank unprinted paper face; face turned away / back view; deep tungsten shadow or hat brim; figure too small to read; torn-away face patch; black censor bar. Keep censor bars for at most about 1/3 of blocks (they are the signature, not the uniform; they stay the PREFERRED device for real-politician archetypes since they defuse likeness issues). The protagonist stays recognizable by SILHOUETTE across all devices.

{MOTION}: DIMENSIONAL style, `smooth simple handcrafted motion, subtle stop-motion feel`; DROP `3D render` from the NEGATIVE (photorealism ban stays).

PALETTE LOCK: `sepia newsprint monochrome with ONE {ACCENT} paper accent - no other colors, no colored/gradient backgrounds`.

Asset roster guidance:
- Characters (2:3): monochrome halftone cutout figures, faces obscured by ONE of the anonymity devices (vary across the roster). The only color in this world is the {ACCENT}, so make figures distinct by SILHOUETTE (era clothing shape, a hat, posture, a prop in hand), never by color. Groups read as institutions; a single figure reads as the protagonist.
- Locations (chosen aspect): dressed miniature diorama sets (a newsprint canyon, a cardboard parliament, a paper harbor, a market of folded-news stalls), each with ONE named anchor object, no people.
- Props (1:1): the {ACCENT}-colored objects that carry meaning (a stamp, a coiled fuse, a treaty seal, a banknote stack). Give the script's through-line object a prop asset so it stays identical across every block.

The letterpress exception (the ONLY in-clip text allowed in any style): ONE short letterpress label per scene on a prop, 1 to 2 words or a number ("EXPIRED", "1848"), described as `distressed letterpress on a torn {ACCENT} paper element`. On a labeled block, replace the NEGATIVE's `on-screen text, captions` pair with `no text anywhere except "<LABEL>", no gibberish letters, no captions`; unlabeled blocks keep the full ban. Max one label per block; if the render misspells it, one retry, then drop the label and keep the prop. Every other style keeps the symbols-not-text rule.

Shot language: macro push along a paper canyon; top-down tilt from figures onto a document; detail crop of the accent prop, HARD CUT, wide of the whole miniature; dust drifting through a tungsten beam; a scale shock from letterpress texture to the full diorama landscape. Reverse, lateral and detail crops of the same set count as distinct locations for pacing purposes. Every block lands at least ONE impact beat (a stamp PUNCHES the letterpress, a paper structure COLLAPSES, dust WHUMPS off a slammed document), named in the SHOT text and echoed in AUDIO.

Moderation notes: real people's names belong to the NARRATION only; in video prompts describe archetypes by silhouette and build (never named politicians or celebrities), rendered as a censor-bar cutout; mid-shot or wider on faces. "Mushroom cloud" trips safety filters: swap the silhouette (hourglass, cracking dam, fuse reaching a keg), keep the idea.

## 5. Mannequin

History's third named style. A clean 3D CGI clay-render world where every character is a smooth featureless matte mannequin in a solid role color, acting out real history in simple period environments under a flat light-grey sky. Reads instantly as "reenactment diagram": great for battles, expeditions, political intrigue.

One-liner (verbatim): "Clay-render mannequin reenactment - smooth featureless figures in solid role colors acting out history in clean period environments."

STYLE FORMULA:

> clean 3D CGI clay-render historical reenactment: smooth featureless matte clay mannequin figures with no face, no clothing detail and no seams, one solid color per character, crisp sharp viewport-style render with solid flat matte colors and smooth surfaces, flat even neutral lighting with soft ambient global illumination and no hard directional shadows, uniform very light grey sky with no clouds and no gradient, simple uncluttered period-accurate environments, smooth fluid weighty CGI animation with real momentum and follow-through, non-photorealistic, no film grain, no camera shake.

{MOTION}: dimensional, `smooth fluid weighty CGI animation with real momentum and follow-through`; DROP `3D render` from the NEGATIVE (this style IS a render; the photorealism ban stays). ADD to the NEGATIVE: `stiff stop-motion, doll-like jitter, laggy or teleporting motion, plastic-toy look, physical claymation texture, film grain, camera shake`.

PALETTE LOCK: `solid matte role colors of the reference figures on period environments under a uniform very light grey sky - no time-of-day light, no sunset, no night, no blue sky`.

The LOCKED CAST (identity chain, mandatory). Role colors ARE identity. Generate each cast member ONCE, then reuse the same asset on every block it appears in:
- Male white: protagonist / crew
- Male black: leader / antagonist
- Female white: female lead
- Female teal: queen / secondary female lead
- Extra roles: red / yellow / blue / green / purple, generated once, locked, reused everywhere.

Consistency chain: the FIRST mannequin generated becomes the body reference; every subsequent cast member is generated WITH that first mannequin attached ("the SAME mannequin body type and render as the reference, now in {color}, {female base}") so proportions and material never drift.

Female base (mandatory for women): feminine silhouette, slim waist, gently rounded hips, soft shoulders, a plain smooth ankle-length clay gown. Never the male base for a woman.

Creatures / non-humans: creature-SHAPED mannequins, never recolored humans (emu = smooth bird form, pig = smooth pig form, sea serpent = smooth serpent form). Giants or monsters that risk reading as a nude body: stage as a SHADOW plus one glowing feature, not a bare figure.

Aging and era variants, simplified (no detail to age): at most TWO variants per character, child and adult. A child mannequin = smaller scale with a slightly larger head proportion, same role color. Passage of time is carried by the NARRATION and the environments (a ruined wall, a new palace), not by the figures. The role color NEVER changes across a character's lifetime.

Environments and crowds: environments are per-event and free to change (outback, Roman walls, sea and islands, palace interiors), simple and uncluttered; ONLY the figures, render look, lighting and grey sky stay constant. Crowd scenes render MANY distinct figures ("dozens", "many rows", every figure fully modeled), never three mannequins pretending to be an army.

Moderation notes: "muscular / ripped / chiseled" body descriptors on mannequins trip filters; never describe musculature; build is conveyed by SCALE and posture ("a head taller", "broad frame"). Bare-body readings (giants, swimmers) use the shadow + glowing-feature staging. Real people: names in NARRATION only; on screen they are role-color mannequins.

Suggested defaults: 16:9, a first run of about 90 s (9 blocks), VO tone dry British narrator, subtitles off.

## 6. Cinematic Storybook (Fairy Tale / Myth)

The Fairy Tale and Myth channel's default style: a lush hand-painted 2D-animation feature look with richly detailed semi-realistic characters, expressive faces and ornate costumes, gothic and natural fairytale settings, warm volumetric light against deep atmospheric shadow. Reads as "a beautiful animated legend"; for retellings of myths and fairy tales (Greek, Slavic, European, world folklore).

One-liner (verbatim): "Cinematic hand-painted storybook - lush 2D-animation fairytale look, painterly light and deep shadow, ornate characters and enchanted settings, told on twos like a classic cartoon."

STYLE FORMULA:

> cinematic hand-painted 2D animation, storybook fairytale look: soft painterly rendering with warm volumetric light and deep atmospheric shadows, richly detailed semi-realistic characters with expressive faces and ornate period costumes, gothic and natural enchanted settings, muted jewel-tone palette (deep burgundy, obsidian, forest green, dusk blue, candle gold), delicate linework under soft gradient shading, dramatic chiaroscuro lighting, dreamy enchanted mood, high-production 2D feature-film look, non-photorealistic, no film grain.

PALETTE LOCK: `muted jewel-tone palette of the reference images - deep burgundy, obsidian, forest green, dusk blue, candle gold; warm key light against deep shadow. No neon, no flat bright cartoon primaries.`

{MOTION} slot, ANIMATE ON TWOS (this style's signature): about 12 drawings per second, stepped, like a classic hand-drawn cartoon. It sells the 2D-animation feel and hides AI over-smoothness and morphing. Two layers, use BOTH:
1. In every block prompt: `TRADITIONAL HAND-DRAWN 2D ANIMATION, animated ON TWOS (~12 drawings per second) - deliberate STEPPED / staggered motion with tiny holds between poses, snappy pose-to-pose keyframe animation, NOT smooth, NOT fluid interpolation, NOT slow-motion`; slow graceful dreamlike camera moves are fine. ADD to the NEGATIVE: `smooth motion, fluid interpolation, slow-motion, motion blur, 60fps look`. KEEP `3D render` in the NEGATIVE (this is 2D).
2. In the edit: step the final footage to 12 updates per second (Premiere Pro or After Effects: Posterize Time effect set to 12 fps on the adjustment layer over the whole sequence; keep the container frame rate and the audio untouched). The prompt sets the character of motion, the effect guarantees the cadence; both together give the cleanest cartoon look.

Tone and voice: enchanting STORYTELLER, hushed, warm, mysterious, unhurried and mythic; not History's witty/sarcastic register, NO jokes. Cold open still at most 8 words. Voice: a deep male storyteller or a warm female for gentler tales; one voice locked as everywhere.

Music, mandatory, mysterious and calm (default ON): dark-enchanted ambient: mysterious, calm, hushed, dreamlike; soft sustained strings, distant harp, faint music-box, low choir pad, a far-off bell; instrumental, no drums, no vocals. Ducked under the voice (bed at about 0.09 of voice level with sidechain ducking). Never bright or bouncy. A user-supplied file always wins; if no bed is available ship without and say so.

Storybook-spread inserts (optional atmospheric blocks): a block MAY be an illustrated BOOK SPREAD instead of a staged scene: an open antique storybook whose two pages hold one continuous painted illustration in gold vine borders. Use sparingly (an opener, a chapter turn, the closing moral). Faint illegible decorative script only, never readable text.

Moderation notes: video-model safety filters trip on grim death imagery even in painterly fairytale. AVOID in prompts: `hooded figure / cloaked ferryman`, `souls of the dead`, `corpses`, `river of the dead`, tight menacing shadow-claws, anything reading as violence toward a person. Convey dark or underworld mood through ARCHITECTURE, LIGHT and NATURE instead: gateways, torches, mist, asphodel flowers, ruins, moonlight. Keep characters clearly adult. If a grim beat keeps failing, re-stage it as an empty atmospheric location.

Everything else = the History channel mechanics: 10 s blocks of FIVE hard cuts, a 2 to 3 min default (12 to 18 blocks), asset roster + style key, one continuous through-image.

## 7. Watercolor Chronicle (long-form history, 10+ min)

Intake one-liner (verbatim): "Watercolor Chronicle - hand-painted watercolor washes with fine ink sketch lines, muted period palette, soft paper texture; a storybook documentary look."

STYLE FORMULA:

> hand-painted watercolor and ink documentary illustration: loose expressive watercolor washes over fine confident ink sketch linework with visible pen strokes, muted restrained period palette with sepia-leaning warmth, soft cotton-paper texture with washes bleeding at the edges, unfinished sketch edges fading into blank paper at the frame borders, period-accurate costume and architecture, painterly directional light with soft shadows, subtle paper grain, gentle painterly motion - washes breathing, lines alive, never mechanical - non-photorealistic, illustrated, no live-action.

{MOTION}: painterly-flat, `gentle painterly motion, washes breathing and lines alive, subtle parallax between painted planes`; keep `3D render` in the NEGATIVE.

PALETTE LOCK: `muted period watercolor palette of the reference images with sepia-leaning warmth - no saturated modern colors, no neon, no gradients outside the washes`.

In-clip text: NONE (era titles and dates are carried by the VO and the captions).

## 8. Flat 2D Papercraft (stills default)

Default for Picture Story (narrated stills) when nothing else is picked: "Layered cut-paper collage - flat colored paper shapes with crisp cut edges, subtle drop shadows between layers, textured construction paper."

STYLE FORMULA:

> flat 2D papercraft collage: characters and scenery cut from colored construction paper with crisp scissor-cut edges, layered flat shapes with subtle soft drop shadows between paper layers, visible paper grain and fiber texture, slightly imperfect hand-cut silhouettes, matte saturated paper palette, simple readable compositions on a plain paper backdrop, handcrafted collage feel, non-photorealistic, no gradients outside paper shadows, no outlines - shapes are defined by paper edges.

PALETTE LOCK: `matte construction-paper palette of the reference images - no neon, no gradients, colors read as physical paper`.

Alternates for stills: Stickman Cartoon (section 2) and Hand-drawn Ink (section 9, style 4). Something adjacent the user asks for ("crayon", "flat vector") maps to the closest of the three; confirm in one line.

## 9. Kids styles

Kids runs use this baked-in set (Studio 3D recommended, first). For each, attach 2 to 3 style-donor images to the key generation if you have them; refs are donors only, never frames, and their subjects are never copied. Without donors, generate the key from the formula alone.

### 9.1 Studio 3D (recommended default)

> Studio 3D preschool style - chunky rounded cartoon 3D characters with a soft glossy toy finish, big adorable googly cartoon eyes and tiny friendly smiles, smooth matte-and-glossy plastic-clay surfaces with no sharp edges, clear readable silhouettes, bright saturated candy colors (red, yellow, blue, orange, green), gentle soft studio lighting with soft rounded shadows, pure clean seamless white background with generous negative space, playful preschool CGI look - non-photorealistic, no live-action, no on-screen text.

{MOTION}: dimensional, `springy bouncy friendly motion (hops, wobbles, blinks), smooth gentle camera moves`; drop `3D render` from the NEGATIVE.
PALETTE LOCK: `bright candy palette of the reference images on a pure seamless white background - no new colors, no gradients in the backdrop`.

### 9.2 Pastel Flat 2D

> flat 2D vector cartoon in a soft pastel preschool style: soft pink, baby blue, mint green, sandy yellow and lavender palette, colored outlines one shade darker than each fill (never black), large round circle eyes with white sclera, large black pupils and small white glints, simplified rounded shapes with organic curves, cell shading with distinct flat shadow shapes, friendly warm expressions, clean uncluttered backgrounds with a soft gentle gradient, no sharp angles, no textures.

{MOTION}: flat, `simple limited animation on twos, soft bouncy easing`; keep `3D render` in the NEGATIVE.
PALETTE LOCK: `pastel palette of the reference images (pink / baby blue / mint / sandy yellow / lavender) - no new colors, outlines darker-shade never black`.

### 9.3 Colorful 3D

> colorful stylized 3D cartoon: deliberately rounded chunky character proportions with oversized sparkling expressive eyes, wide warm smiles and clear readable silhouettes, glossy toy-like clean surfaces, soft near-shadowless studio lighting, cartoonish high-gloss CGI never photoreal, ULTRA-VIVID high-saturation candy palette turned up bold and punchy (cherry red, sky blue, sunny yellow, lime green, orange at full intensity - never muted, never pastel), cozy storybook environments with rounded friendly shapes under a bright blue sky with fluffy clouds, safe friendly upbeat mood with adventure but no real danger, lively springy comedic motion accents (sweat drops, surprise marks, whoosh effects).

The cast, its size and any team roles come from the SCRIPT, not the style: one hero, two friends or a crowd all work.
{MOTION}: dimensional, `lively springy motion with comedic accents, dynamic but gentle camera (push-ins, orbits, crane pull-backs)`; drop `3D render`.
PALETTE LOCK: `vivid high-saturation candy primaries of the reference images, turned up bold - no muted or pastel drift, no new colors; if the script has recurring heroes, each keeps one consistent signature color`.

### 9.4 Hand-drawn Ink

> hand-drawn thin-line ink illustration, uniform thin slightly wobbly black ink outlines on a PURE WHITE background, objects and figures left uncolored, simple rounded figures with dot eyes, tiny line mouths and hugely expressive eyebrows, soft flat light-grey shadow shapes under objects and figures with soft edges and no hatching, flat 2D, no gradients, no texture, STRICTLY NEUTRAL BLACK-AND-WHITE greyscale - no color cast, no bluish or cool tint, no colors beyond pure white, neutral grey and black, deadpan understated humor, clean disciplined linework, never photorealistic.

{MOTION}: flat, `simple limited animation on twos`; keep `3D render`.
PALETTE LOCK: `pure white / neutral grey / black ONLY - any color is a defect`.

### 9.5 Poster Vector

> flat 2D vector cartoon in a cheerful minimal poster look - bold rounded geometric shapes with no outlines, solid flat color fills, NO gradients, NO texture, friendly blob characters with tiny curved-line closed eyes or dot eyes and small simple smile mouths, one subtle flat darker-tone offset shadow per shape, vivid saturated palette of sunny yellow, tangerine orange, cobalt blue, bubblegum pink, grass green, deep navy plus black and white accents, single plain flat solid-color background, a white sparkle diamond as the signature accent.

{MOTION}: flat, `snappy poster-style motion, shapes popping with slight overshoot`; keep `3D render`.
PALETTE LOCK: `the poster palette of the reference images, one flat backdrop color per scene - no gradients, no new colors`.

Fluffy Toy: a legacy look with no pinned formula; derive it from a reference image (plush fabric texture, soft stitched toys) per section 1.

## 10. Style-inherent extras

- Kids looks (any channel): a wordless music bed on by default, mood matched to the channel's tone (playful-light for the look, not babyish). Level about 0.05 of the voice level, ducked under speech by sidechain. Prompt for a generated bed: the topic's mood in tempo, instruments and feel, instrumental, no lyrics, no vocals, 1 sentence: calm topics = soft lo-fi or warm marimba + airy pads at a light mid tempo; adventure = brighter bouncy small-combo groove. Acoustic, jazz, lo-fi and small-combo genres pass moderation reliably; avoid big orchestral scores and EDM/bass-drop wording. Duration of the bed = the video's exact length.
- Cinematic Storybook: on-twos cadence (12 fps stepped) + the mysterious-calm bed above.
- Editorial and Diorama: no bed required; a quiet room-tone bed is welcome on long-form.
- Level law for every mix: voice 1.0, clip SFX about 0.12, music bed 0.10 generic or 0.05 Kids/Storybook, bed ducked under speech, final loudness about -16 LUFS integrated.
