# The six UGC formats

Contents:
0. Shared gates, intake, product normalization, duration planning
1. Creator review (or productless creator story)
2. Product-only with off-screen voice-over
3. Unboxing
4. Try-on
5. Tutorial
6. Website tour (creator + real screenshots)

Each format lists: result, hard rules, shot list (roles, POV, distance), script skeleton, creator and delivery notes, caption style, generation notes and self-shoot notes. Prompt grammar for stills and clips is in `shot-prompts.md`; lines, hooks and caption recipes are in `hooks-and-captions.md`; the creator frame is in `creator-persona.md`.

## 0. Shared material

### Format choice
| Format | Requested result |
|---|---|
| review | One consenting or generated adult creator demonstrates a product or tells a supplied story; product optional. Default for an unspecified UGC video. |
| product | Product is the hero, off-screen native voice-over, no on-camera speaker |
| unboxing | Visible creator opens packaging and reacts |
| try-on | Creator wears an item and demonstrates fit/texture |
| tutorial | Creator demonstrates actual use with `Step N` labels |
| website | Real captured website/app/page appears with a presenter |
A product URL identifies the product; it does not by itself make the video a website tour (the page must itself appear on screen). A silent product-only commercial is ordinary video generation, not the voice-over product format. A long video is ONE stitched deliverable (clips of 4-15s), not a series.

### Safety and truth gate (before any generation; if an item fails, stop and do not route around it)
- Creator authorization: a generated adult (look 21+) or a consenting adult non-public person whose image the user is authorized to use. A supplied photo is not permission to impersonate its subject. If third-party consent or adult status is unclear, ask once. Decline public figures, celebrities, minors, non-consenting people, deceptive identity use. Never clone or imitate a supplied person's voice.
- Allowed promotion: decline political persuasion and promotion of prohibited or age-restricted goods or services (adult sexual content, products or services; gambling; illegal or regulated drugs, paraphernalia, prescription medication; tobacco or nicotine; weapons, explosives, harmful materials; counterfeit or illicit goods; extremist goods; deceptive or high-risk financial services; malware or spyware; fraud; covert surveillance).
- Truthful claims: `approved_claims` is the complete allowlist (see `hooks-and-captions.md` section 1). No synthetic testimonials. Product-present output is described as a brand demo, creator concept or sponsored creative.
- Try-on additionally: general-audience fashion only (ordinary garments, footwear, bags, jewelry, wearable accessories). Decline intimate apparel, lingerie, underwear, fetish wear, transparent garments, sexualized styling, nudity, or emphasis on intimate anatomy. Do not adapt a disallowed request into a different outfit.

### Intake (ask only for real gaps, bundled into ONE question)
Collect: product photo or URL (not for productless review), duration (offer 10s / 15s / 30s / 45s; never silently assume 15), creator photo (authorized) or desired gender, approved claims, language and accent, and explicit overrides (location, hair, ethnicity, outfit register, mood, props, music, on-video text). Offer accent/quirk only when the brief already signals an origin or unusual energy. Never ask about tools, aspect ratio, resolution, audio, batching or identity training; default 9:16.
Specificity tiers: `auto` (1-5 words, no scenario: choose the whole treatment), `guided` (1-3 sentences of tone or rough flow: preserve that direction), `director` (4+ sentences, a scenario, shot list or location sequence: map the supplied beats one-to-one onto the shots; adapt only physically unsafe interactions).

### Product normalization (do once, reuse verbatim everywhere)
From a photo: read category, usage mechanic (spray / squeeze + apply / press pump / swipe / brush / press with sponge / drop onto fingertips / scoop / swallow or chew / mix), opening mechanic (uncap, unscrew, pull tab, flip top, press pump; it must be shown BEFORE any contents exit), and key visual details. Never default to "applies cream"; describe the exact mechanic the photo shows. From a URL: read the title, brand, description and the hero image from the page's structured data / social-preview meta; if the page is thin, blocked or image-free, ask once for a photo; never substitute a stock or generated product.
Write ONE `product_description`: shape, material, colour, hand-relative size ("palm-sized, fits entirely in one hand, ~15 cm tall", never object comparisons), mechanism anatomy (which part is where, what moves, where output exits), absent features stated visually ("cordless, smooth body, no buttons"), the label treatment (real photo = the label keeps its real text; description only = "small label, turned slightly away, too small to read"), plus one honest imperfection. If a big readable logo is in the photo, warn once that wordmarks may render as gibberish or as a competitor brand. Also fix: `tier` (luxury / premium / drugstore, from packaging cues only, never a price lookup), `category`, and for VO formats `voice_gender`. Never infer price, claims or an unseen side.

### Duration planning
Integer total of at least 4s. Each clip is 4-15s. Use the minimum number of clips that preserves the total: 16 = 12+4, 19 = 15+4, 31 = 15+12+4, 46 = 15+15+12+4. 4-15s = 1 clip; 16-19s = 2 clips balanced to at least 4s each; 20-30s = 15 + remainder; 31-45s = 15, 15, remainder; 46-60s = 15, 15, 15, remainder; over 60s = ceil(D/15) clips of 15 with the final one at least 4s. Tutorial has 4 step slots per clip (4/8/8/12/16 steps for those bands). Website uses the same planner with no sheets.

### Rules shared by the physical formats
- One creator identity locked for every shot; never regenerate or replace it with a description mid-project.
- Never bake text into generated frames; optional text is added in the edit (tutorial Step labels are the only required text).
- Default spoken language English with a neutral American accent unless changed (the source recipe's reliable lip-sync language).
- Hide mechanics from the viewer: no model names or technical chatter in the deliverable.
- Inspect every generated frame before it feeds the next step; fix only the failed shot. Raw contact sheets must be checked for panel count, panel size, identity, stray text and hands before use.

---

## 1. Creator review (or productless creator story)

Result: one 9:16 video, one creator, product optional. Per 15s clip: 8 beats with 7 hard cuts. Productless mode is fully supported: never invent a product, brand, package, label or claim; the topic, routine or story carries the arc and ends on the human resolution.

Hard rules: one creator reference for all shots; later clips never greet or re-introduce the product (continue mid-thought); product enters as a supporting actor at 40-60% of runtime; no text baked in; default English with an American accent; first word of every segment is hook content.

Arc roles (what the 8 beats do, by position in the video):
| Role | 8-beat flow (shot 1 to 8) |
|---|---|
| HOOK (first clip of a multi-clip video) | attention-grab, context, life beat, life beat, curiosity toward the product/moment, first touch, lead-in, hand-off to the next clip |
| HOOK+SETUP (clip 1 of 2) | attention-grab, setup, context, life beat, first product touch, develop, reaction, lead-in |
| MAIN (middle clip) | pick up from previous, build, core demo A, core demo B, reaction, develop, transition, hand-off |
| REVEAL (clip 2 of 4) | open packaging, reveal product, key detail, macro detail, first impression, reaction, develop, settle |
| APPLY (clip 3 of 4) | begin application, mid-application, macro of the moment, effect starting, effect visible, reaction, develop, settle |
| APPLY+CLOSER (clip 2 of 2) | application, effect visible, macro, reaction, result, recommendation, settle, final look |
| CLOSER (last clip) | result visible, proof, recommendation, settle, warm beat, aside, final look, loop-ready beat |
| FULL_ARC (single clip, N=1) | HOOK (attention-grab / setup), context, life beat, first product touch (or story turn), core action, reaction, result, recommendation-settle |
Slot 1 is the setup of the moment, NOT necessarily "show the product": the product may be hidden, partial or absent there. In a multi-clip video the story is about the PERSON first; the product is incidental or absent in hook clips. Visual beats cost zero words: every plot event that CAN be shown IS shown (the wince, the package on the counter, the held-up product). Each shot carries introduce, develop, land. Frame one is MID-EVENT.

Shot list (FULL_ARC, 15s, ~1.9s per shot): cadence `SELFIE-MID, STATIC-WIDE, STATIC-MACRO, SELFIE-TIGHT, STATIC-MID, STATIC-MACRO, STATIC-WIDE, SELFIE-TIGHT`. Typical mapping: 1 hook (SELFIE, mid-event, the hook pattern staged), 2 context wide (STATIC, creator in the setting), 3 detail macro (the thing the story is about), 4 selfie-tight life beat/reaction, 5 first product touch (STATIC mid), 6 macro of the core action, 7 wide result / show, 8 selfie-tight recommendation settle, ending mid-motion. Adapt to the story; keep the no-two-adjacent-same rule. Hook staging for shot 1 and the body event for the peak shot: `shot-prompts.md` section 6.

Script skeleton (words per `hooks-and-captions.md` section 1): one story shape with ONE "but then" twist; hook line (<= 8 words when ad-style, or the H-pattern opener), 1-2 body lines each anchored to a beat, ONE peak line with the performed-dialogue markup, a closer that carries the CTA inside the resolution (no outro beat). Plain review mode only on explicit request, as a demonstration (PAS / BAB / Hook-Story-Offer / Us-vs-Them / Demonstration).

Creator and delivery: NATURAL register, ONE persona sentence, creator frame from `creator-persona.md` with the category gate (the look leaves room for the product), neutral cool daylight, wardrobe fixed unless the story changes context. Phone-mic audio with room tone; no music unless asked.

Captions: off by default; opt-in UGC-natural subtitles (sentence case, single line, <= 4 words) and/or a hook plate.

Self-shoot notes: phone at arm's length for SELFIE beats, phone propped and locked for STATIC beats; record a longer take than needed and cut into 1.5-2s beats; one hand always free in selfie beats; window light from one side.

---

## 2. Product-only with off-screen voice-over

Result: product is the hero in EVERY shot; any visible person stays auxiliary and silent (hands-only, cropped, partial body, first-person POV, or wide context; mouth closed, no lip-sync, no greeting, never the focal subject, identity not locked, gender matches the voice). 4 beats per clip (4 cuts). A real product reference is required; never invent or substitute one. Voice-over is native/off-screen; a silent commercial is not this format.

Shot list (clip 1; later clips: 4 NEW demo beats, never repeating earlier ones, conditioned on the previous final shot):
| # | Role | Content | POV / distance |
|---|---|---|---|
| 1 | PRODUCT-INTRO | Product in its native context on a surface or in the environment, clean establishing frame, product readable, NOT yet in active use; person absent or only a hand at the frame edge presenting it gently. First clause is motion (the environment kinetically alive). | STATIC-WIDE, MEDIUM-WIDE |
| 2 | PRODUCT-DEMO-A | Product in active use, first demonstration angle; the product is doing what it does | STATIC-MEDIUM, MEDIUM (product + demo target both visible) |
| 3 | PRODUCT-DEMO-B | SECOND demonstration, visibly different from shot 2: different action, scale, context or target (not just a closer version of the same shot) | MACRO or FIRST-PERSON-POV, TIGHT |
| 4 | PRODUCT-RESULT | Outcome of the demo with the result visible, OR a hero shot visually distinct from shot 1 (different angle, scale, surface); settled conclusive frame | STATIC-WIDE or STATIC-MEDIUM, MEDIUM-WIDE or THREE-QUARTER |
Framings must span at least one TIGHT, one MID, one WIDE band. Small cosmetics may lean macro in all four; large appliances lean wide.

DEMO-A vs DEMO-B pairings (template; if a category is missing derive two visibly different actions/targets):
| Category | Shot 2 | Shot 3 |
|---|---|---|
| Gaming mouse | hand on the mouse, glides across the pad while the monitor shows in-game movement | macro on the scroll wheel rolling under the index finger, or thumb pressing a side button |
| Mechanical keyboard | both hands typing, keys depressed in sequence | macro on a single keycap depressing with tactile snap |
| Headphones | worn, hand adjusts the headband | macro on the ear-cup cushion compressing as it settles |
| Controller | both hands grip, thumbs on sticks during gameplay | macro on a shoulder trigger squeezed by the index finger |
| Smartphone | one hand cradles, other swipes | macro of a finger tapping a specific UI element |
| Vacuum | wide shot gliding across living-room carpet | different surface (head on ceiling/wall corner via wand) or macro on the nozzle picking up a cobweb/dust |
| Drill | standard pose driving a screw into wood | macro on the bit rotating with chips emerging |
| Blender | button pressed, contents spinning through the jug | pour shot into a glass or bowl |
| Perfume | mist arcing from the nozzle onto the wrist | macro on droplets settling on skin texture, bottle resting nearby |
| Serum dropper | dropper held up, drops falling onto a fingertip | macro of serum pressed into the cheek with two fingertips |
| Cream jar | lid twisted off, fingertip scoops | macro of fingertip pressing cream into the back of the hand or face |
| Lipstick | cap off, base twisted up | macro of the lipstick gliding across the lips |
| Spray / mist | trigger pressed, mist toward face/hair | macro of mist droplets settling on skin/hair |
| Food / drink | pour from container into a glass/bowl | hand brings glass/utensil to the mouth for a sip/bite |
| Clothing | garment held up front by both hands | worn on body (cropped torso, hands smoothing fabric) |
| Fitness gear | lift/press motion in use | set down on rack, hand pats it or wipes it with a towel |
| Cars | wide shot parked or driving by | macro on a feature (badge, wheel, door handle pulled) |
| Sunglasses / outdoor gear | worn (medium close) | removed and held up against the sky |
| Mop / steamer | wide shot gliding across the floor | different surface (tile bathroom vs hardwood hall) or macro of the head touching debris |
| Pet products | the pet using it | macro on a detail (chew mark on the toy, tag on the collar) |
| Tools | tool in use on the material | macro on the result (clean cut, driven screw, tightened bolt) |

Native use accessories (include 2-3 category-appropriate items across the four shots, distributed: shot 1 shows 2-3 as establishing context, shots 2-3 one or two at the edge, shot 4 returns wider with the result). A product alone reads as a stock photo.
| Category | Accessories |
|---|---|
| Gaming peripherals | mousepad/desk mat, partial keyboard at the edge, monitor with gameplay/desktop visible, notebook or mug, soft ambient light (not RGB-only) |
| Cosmetics | vanity tabletop with brushes, partial mirror, jewelry tray, cotton pads, neighbouring open bottles |
| Skincare / haircare / body | vanity counter, neighbouring bottles, partial towel, plant, water glass, sink edge |
| Perfume | dressing-room vanity, perfume tray with another bottle, dried flowers / glass dish, jewelry tray |
| Food / beverage | counter with ingredients (fruit, herbs, glass), serving plate or glass, partial cutting board/utensil |
| Protein / supplements | shaker, sports towel, water bottle, gym mat or kitchen counter |
| Clothing / jewelry | closet rack, hanger, partial mirror, lifestyle pieces on a flat surface |
| Fitness gear | yoga mat, partial dumbbells, water bottle, gym towel, training shoes |
| Cars | road/driveway/garage floor, building or street, second car partial |
| Outdoor / sunglasses / sunscreen | beach towel, sand or grass, sunhat, cafe table, drink |
| Tech (non-peripheral) | desk with notebook/pen, plant, ambient room, second device partial |
| Home / decor / candles | sofa partial, throw, plant, book stack, side table |
| Cleaning appliances | floor texture clearly visible, visible dust/dirt BEFORE the pass, clean stripe AFTER, dustpan/bucket/cloth |
| Pet products | bowl, bed, leash hook, toy, the pet itself partial |
| Tools | workbench surface, screws/nails, lumber, safety glasses, tape measure |
Settings by category follow the same logic as `creator-persona.md` (cosmetics = bathroom/bedroom vanity, kitchen products = kitchen, tech = desk, cleaning = wherever it is used, pets = pet zone).

Script: off-screen voice-over only, benefit-driven (`hooks-and-captions.md` section 6), opens mid-thought straight into a benefit, no greeting, no bracketed reaction sounds. 4 beat-sized phrases per clip. The 0.1s hook law applies: first VO phrase lands within 0.0-0.4s and shot 1's first clause is motion. Voice gender locked for the whole video; any visible person matches it.

Look: iPhone aesthetic is the defining feature, because static locked shots and macros drift toward product-ad polish. Mandatory phrases: `Shot on iPhone, casual handheld framing`; `Phone-sensor grain and realistic surface texture preserved, no retouch, no smooth-skin filter, no professional gloss`; `Natural ambient light typical of a phone photo, even, slightly imperfect, not dramatically lit`; `Authentic UGC creator phone photo of the product in real-life context, NOT editorial product photography, NOT studio shoot, NOT magazine commercial`. Micro-beats focus on product mechanics and the environment (5+ per shot: glint, label catching light, a click, suction picking up a particle, mist dispersing, surface clearing, ambient air shifting a curtain), and the product state evolves across the four shots (still, actuating one way, actuating another way, post-demo).

Captions: opt-in subtitles; hook plate; no Step labels.

Self-shoot notes: tripod/static for shots 1, 2, 4; hand-held or phone-on-hand POV for shot 3; record the VO afterwards in Polish or English (see `narration-vo`); this format is the easiest to shoot yourself because nobody has to speak on camera.

---

## 3. Unboxing

Format gate: the brief must request a creator-led reveal, not simply a product leaving its packaging. Do not add a visible creator or reaction arc to make a product-only video fit. One creator identity. Per clip: 4 beats, 3 cuts.

Hard rules: shot 1 of clip 1 ALWAYS shows a sealed, taped box and NO product; the reveal is shot 2; the box is at the frame edge or gone in shot 2 and absent forever in shots 3-4 and later clips (never re-closed, re-taped, carried, set back). A real package photo is optional; without one use one generic plain brown delivery box and never invent branding. Every shot opens MID-EVENT (fingers already at the tape edge, not walking toward the box). Product analysis once, reused verbatim. No greeting or reintroduction after clip 1.

Canonical arc (clip 1):
| # | Role | Content | POV | Distance |
|---|---|---|---|---|
| 1 | PACKED | Creator with the sealed delivery box in front of them on a flat surface, hands on the box mid-event, genuine anticipation (eyes bright, grin breaking). Product NOT visible. The box is not lifted. | STATIC | MEDIUM, waist-up with room context |
| 2 | REVEAL | Product just out of the box, held by the creator or placed next to them; box at the frame edge or gone. The ONE genuine peak: a real jaw-drop / audible gasp breaking into a wide delighted grin, paired with one body event. | STATIC | MEDIUM CLOSE-UP, chest-up |
| 3 | PRODUCT-FOCUS | Product extended toward the lens, on palms or held up close; creator partially visible or absent; box gone; product dominates | STATIC close-up | MACRO or TIGHT CLOSE-UP |
| 4 | SATISFACTION | Creator settled into ownership: confident pose, grin, product in hand or beside; box gone; energy resolves from the peak into warm recommendation | SELFIE | THREE-QUARTER or FULL-BODY WIDE |
POV cadence `STATIC, STATIC, STATIC-CLOSE, SELFIE`. The four framings must span TIGHT, MID and WIDE; four different physical actions; same hand holding the same object in all four = rewrite. Director input may remap beats (e.g. open box, smell perfume, apply to wrist, smile) but frame one and the box rules stand.

Later clips (post-reveal, the box never appears): shot 1 picks up mid-action from the previous clip's final shot; slots 2-3 develop ONE new idea; slot 4 lands it. Pick ONE shape per clip, never the same on two consecutive clips: FIRST-USE (product in position, exact hand mechanic begins, visible result such as mist landing / swatch / fabric settling, verdict beat mid-laugh with the result still in frame); WRONG-TURN (product in its expected context, carried to an unexpected-but-plausible spot, the twist staged large and legible, deadpan or grin punchline to the lens); CLOSE-STUDY (product at arm's length, macro on one distinctive detail, second detail or texture from a new distance, reaction to what they studied); SHOW-OFF (conspiratorial lean toward the lens with the product half-raised, product presented like a secret, tight detail beat, wide ownership beat caught mid-settle). Exactly ONE visual twist per clip (zero = flat, two = unreadable); the twist is a plot event, never an energy drop; cause before effect (a mist on the wrist appears only in or after the shot showing the spray); no loop-back beats; every beat legible from the frame alone.

Box logic:
- Real package photo given (Case B): that exact package is the only packaging anywhere; no packing tape, no tissue paper, no knife unless visible in the reference. In clip video, build "the package just arrived" excitement through shot 1 (finger-drumming on the lid in 3-4 taps, an excited shoulder wiggle, wide-eyed grin with brow-pump suspense, a quick mock head-shake, a tiny "ooooh" mouth peek), a playful few-cm slide of the box on the surface (never lifted, tossed or dropped), then ONE clean opening motion that matches the visible mechanism (lift-off lid pulled straight up, hinged lid tilted back, slide-out drawer pulled forward, magnetic flap flipped, wraparound sleeve slid off).
- No package photo (Case A): plain brown cardboard delivery box sealed with packing tape, no logos, no labels or stickers, slightly larger than the product, never a white gift box or branded retail box. At the end of shot 1 she picks up a small utility knife, slices the tape in one decisive motion (no lingering on the blade), sets it aside (never mentioned again); color-matched tissue paper is briefly visible inside the open flaps in shot 2 only (atmospheric backdrop, crumpled not flat, never focal). Tissue colour by product: pink/red/rose = soft pink or blush; blue/aqua = light blue; black/dark = cream, beige or warm grey; white/light/pastel = soft pastel (lavender, peach, mint); multicolour / brand-led = dominant brand colour; unsure = cream or beige.
- Surface: tiny/small products (cosmetics, phone, jewelry, supplements) on a TABLE only, never the floor; medium on a table; large (<= ~50 cm) table or floor; oversized (bicycle, furniture, big appliance) floor only, creator kneels or stands beside. Style the surface to the room: living room = marble/light-wood coffee table, sideboard or console (white lacquer, oak, ash); bedroom = vanity/bedside/dresser top; kitchen = marble/quartz counter or island; bathroom = marble/stone vanity; hallway = console table; unknown = light wood, white lacquer or marble. Forbidden surfaces: workbench, scratched dark wood, garage/industrial surfaces, plastic folding or camping tables, anything with tools or hardware around, distressed dark "barn" wood, clutter (mail, papers, tools, food). Hardwood/parquet/light-tile floor if the floor is used.
- Weight and grip logic is mandatory before shot 2 (see `shot-prompts.md` section 5): heavy = both hands, forward lean, strain plus the gasp; light = one relaxed hand; tiny = pinched, close to the lens; pairs never on one palm.

Script: caved-in confession or other specific reveal-compatible hook; a body-event reaction at the reveal; one turn; a natural resolution. Later clips mid-thought. Bracketed sounds only on clip 1. ~12-20 / 20-28 / 28-35 words per <=10 / 11-12 / 13-15s clip. No CTA tail unless asked.

Captions: opt-in; keep the bottom safe zone clear; hook plate allowed.

Self-shoot notes: tape the box shut before filming; shoot shot 1 and 2 as one continuous take and cut at the lid-lift; film shot 3 as a locked close-up on a table; shot 4 as a selfie. The reveal reaction must be real, so do not rehearse it too often.

---

## 4. Try-on

Result: one creator, one wearable product (general-audience fashion only). Per clip: 8 beats, 7 cuts: six lip-sync beats (1, 2, 3, 5, 7, 8) and two silent macro voice-over beats (4, 6).

Hard rules: the muted pre-wear outfit with one plain kraft bag appears ONLY in shot 1 of clip 1; from shot 2 on the product is worn and the bag never returns. Never depict a costume change, opening the bag or lifting the product from it; the hard cut performs the change. Shots 4 and 6 are hand-free garment macros (no hand touches the fabric, no "operator hand"). No mirrors or reflections (including puddles and glass). Lock hair, face, product silhouette, colour, print and design across the video. No CTA tail; end on the final spoken beat. Default English, American accent.

Canonical arc (clip 1):
| # | Role | Content |
|---|---|---|
| 1 | PRE_WEAR | Boring neutral home outfit (basic tee + lounge pants / oversized hoodie + cotton shorts / plain knit + sweatpants / simple robe; muted, never competing with the product). One kraft bag (plain brown craft paper, no logo, optional handles tinted to the product's primary colour) held by one handle at her side or standing on a surface beside her; never opened, peeked into, unwrapped or addressed. Product NOT visible. Genuine anticipation, lip-syncing the opener. SELFIE |
| 2 | WEARING | Now wearing the product, full-body or three-quarter, locked-off static, alive stance with a visible pose shift (weight transfer, hip-pop swap, small rotation), one hand may smooth the front of the garment. The ONE genuine peak (jaw-drop into a warm grin) with mouth open mid-word. Bag gone. Embed ONE brief twirl: roughly mid-cut a slow exhale, weight shifts onto the right foot, she rolls her body in one smooth turn revealing the back of the outfit (hold half a beat), turns back and settles; the fabric type catches a slight breath of motion; ONE turn, not a spin; lip-sync pauses while her back is to camera |
| 3 | FRONT_POSE | Front-facing, full-body or three-quarter at a DIFFERENT distance/POV from shot 2, reading the whole silhouette head to toe in an alive stance |
| 4 | TEXTURE_CLOSEUP | Hand-free macro on fabric / cut / texture via framing, drape and light only. Voice-over beat: she is silent on camera |
| 5 | TURN | Mid-turn showing the side or back (over-the-shoulder glance or back-to-camera), body already rotating |
| 6 | DETAIL | SECOND hand-free macro on a DIFFERENT detail (hem / sleeve / collar / hardware / print / seam). Voice-over beat |
| 7 | STYLE_POSE | A DIFFERENT room of the same home, ONE styled pose per clip (accent armchair with a casually crossed leg, window-seat in soft daylight, leaning on a doorframe, mid-step in a hallway, kitchen island, stairs, balcony with soft city light); shoes visible if full-body; up to one paired accessory. Confident victory wrap, mouth open mid-word |
| 8 | FINAL_LOOK | Settled alive final wrap in that room, a last confident look to the lens, warm grin or small delighted laugh, loop-ready mid-motion |
Cadence: POV anchors: shot 1 SELFIE; macros 4 and 6 STATIC close-up with no phone in frame; 2, 3, 7, 8 STATIC (SELFIE acceptable for a naturally one-handed pose); alternate SELFIE/STATIC in between. Distance anchors: macros TIGHT/MACRO; wearing / front / style lean WIDE; openers MID; each band at least twice.

Later clips (picks up where the last clip's shot 8 ended; no bag, no pre-wear, no reintroductions):
- Clip 2 HOME TOUR: bridge from the prior final room, then pose variations across DIFFERENT home rooms not yet shown, two hand-free detail macros (voice-over). No twirl.
- Clip 3 OUTDOOR: all outdoor, tier-matched (luxury: upscale street / cafe terrace / promenade / gallery district; premium: modern urban walk / stylish cafe / plaza; drugstore: neighbourhood walk / suburban street / local cafe terrace / park bench), overcast cool daylight. Shot 1 dry establishing; light rain from shot 2 with droplets on shoulders, arms, hem; 3 front read in drizzle; 4 hand-free wet macro; 5 turn mid-walk; 6 second wet macro on another detail; 7 post-rain or sheltered styled pose (awning, covered terrace, doorway); 8 settled outdoor wrap. Hair stays DRY in every shot (light drizzle only, partial shelter, just-out-of-rain, or an umbrella if requested), never wet or dripping. Allowed: droplets beading, sheen, slight darkening where droplets gather (without shifting the colour), wind-caught drape. Not allowed: soaked-through colour shift, see-through fabric, smeared print, water-weight shape change. No reflections in puddles or storefront glass. Wet macro cue by fabric: silk/satin = beads roll off, sheen intensifies; linen/cotton = droplets soak slightly without darkening the colour; leather = beads on top like glass; denim = droplets bead, wash gradient unchanged; knit = droplets nestle in the weave; synthetic/waterproof = beads like on a windshield; outerwear = beads on the shell, water rolls off seams.
- Clip 4 HOME REFLECT: back indoors, creator settled (sofa, armchair, window-seat, bed-edge, kitchen island), "now that I've worn this, honest verdict". Shot 1 seated SELFIE talking-head opener; 2 different seated angle; 3 seated front read; 4 settled hand-free detail macro; 5 settled turn or shift; 6 second settled macro; 7 styled settled pose in the second room; 8 final wrap at home. Energy: settled-glow (warm grin, soft laugh, calm body), never explosive.
- Clips 5+: alternate established and new compatible places; the two macros stay hand-free voice-over.
Hand-free macro cue by garment type (pick ONE per macro, a different one for shot 6): top = light catches the chest as she breathes / shoulder seam as the body settles / fabric falls over the chest with slight sway; dress = skirt drapes as the body settles / waist seam as she breathes / bodice catches light; skirt = drape settles in the locked frame / side seam / pleats read as light shifts; pants/shorts = fabric falls along the leg as she shifts weight / cuff sits naturally / seam line visible; outerwear = lapel sits open with collar settled / shoulder seam reads / texture catches light; knitwear = knit catches light as the body breathes / weave reads in macro; denim = wash gradient / seam / grain; leather = grain catches light / sheen reads; accessories = catches light / sits naturally.

Garment lock: identical silhouette, primary and secondary colour or print, and recognizable details (collar, hem, sleeve, neckline, hardware, stitching) in every worn shot; the creator may turn freely and the garment rotates with her body; render at realistic proportions with natural drape per fabric weight, not exaggerated; the creator's body proportions from the reference stay consistent; no invented buttons, pockets or hems. Accessories: classify weight (heavy bag = two hands; oversized hat/scarf = two hands, no strain; sunglasses/clutch/watch = one hand; earrings/ring = pinched), size them hand-relative in cm, and never balance a pair on one palm.

Audio model: lip-sync on shots 1, 2, 3, 5, 7, 8 (also on a STATIC locked camera; she speaks to the phone propped across the room); voice-over layered on macros 4 and 6 with her silent on camera (a lip-syncing macro is a rewrite; a silent talking shot is a rewrite unless a calm aesthetic was requested). Put the wordiest chunks on the macro shots. Personal-want mini-story for the opener (bank in `hooks-and-captions.md`), concrete fit/fabric/location observations in the body. At least one closed-mouth recovery beat in the densest lip-sync cut. Loop ending on the last clip: mid-phrase timing cut (final phrase still in her mouth when the clip ends) or, for a single clip, a final settle frame-matched to shot 1's framing WITHOUT the bag or pre-wear outfit.

Captions: opt-in; keep captions off the macro garment details; hook plate allowed.

Self-shoot notes: film shot 1 in the pre-wear outfit, change, then film the rest; keep hair identical; for macros lock the phone and breathe, no hands on the garment; do not use a mirror.

---

## 5. Tutorial

Result: one creator, 4 physical steps per clip, each shot shows exactly ONE step and carries exactly one `Step N – Heading` label. Step numbering is global: clip J holds steps 4*(J-1)+1 to 4*J (4/8/8/12/16 steps by duration band). The last ~0.5-1s of the final cut of the final clip is a brief talking-head CTA, not a fifth step and never a label.

Hard rules: product usage analysis is mandatory (never invent a capability or an impossible action); build `total_steps = 4*N` chronological, physically realistic steps (if the natural sequence is shorter, add real preparation and finishing steps; if longer, merge adjacent micro-actions; preserve a user-supplied step list one-to-one); step labels exactly `Step N – 1-4 Word Heading`, English Title Case; no other generated text; English by default for labels, dialogue and CTA; clip J+1 continues the sequence mid-thought.

Default 4-slot arc (overridden by the product's real sequence, e.g. coffee maker = place cup, load pod, press button, drink; jump rope = pick up, first jump, mid-set, finish):
| # | Role | Content | POV | Distance |
|---|---|---|---|---|
| 1 | Setup / first contact | Creator ON CAMERA (face AND torso visible, locks identity and outfit) with the product clearly held or presented, performing Step 1. Never hands-only or product-only. Calm anticipation. | STATIC | MEDIUM |
| 2 | Core action 1 | Open / dispense / activate / measure / pour / press; typically two-handed | STATIC | MEDIUM CLOSE-UP |
| 3 | Core action 2 | Apply / use on the target (skin, hair, food, surface), mid-action; shows the mechanic clearly | STATIC | MACRO or TIGHT CLOSE-UP |
| 4 | Wrap-up | Result, settled with the product, optional talking-head transition; face visible again to re-anchor identity | SELFIE | THREE-QUARTER or MEDIUM CLOSE-UP |
Cadence `STATIC, STATIC, STATIC (close-up), SELFIE`; a naturally one-handed step (spray bottle, lipstick) may be SELFIE. Expression arc: focused setup, concentrated/instructive, focused application, settled satisfaction. The four framings span TIGHT, MID, WIDE.

Script: tutorial steps, not a generic story arc, are the spine. Explain what the creator is physically doing in concise conversational English, four step beats per clip, measured and calm, no trailer-style gasps (sounds only sparingly, or none). Friction beats enthusiasm ("I almost returned this.") or no verbal opener at all with the first words landing mid-action on Step 1. One closed-mouth beat per cut. Reserve the CTA (`Link in bio.` / `Follow me.` / `Subscribe!`, ONE, picked by available time) as audio plus a decisive downward hand gesture toward the bottom edge (as if pointing at the description), eyes flicked to the lens with a confident half-smile, in the final ~0.5-1s of the final cut; never extend the clip, shorten the narration earlier instead. CTA wording in the video prompt: "In the final ~0.5-1 second of this cut, the camera angle resolves into a tight talking-head selfie POV: the creator pulls in close to the lens, makes a quick decisive downward hand gesture toward the bottom edge of the frame, eyes flicked briefly to the lens with a confident half-smile, and briefly says '[CTA phrase]'."

Labels: see typography rules in `hooks-and-captions.md` section 8. If the labels are baked into stills, tell the video prompt that each label "stays visible in its baked position throughout this cut, sharp and legible", never animating in/out; the safer route is to add them as editable layers in the edit. The CTA is never a caption.

Generation notes: the Step 1 still must show the creator's face, torso and the product (a hands-only opener drifts the face, outfit and product across the later shots). Keep the product identical to the reference in every shot. Dense scripts: fewer words, never faster speech.

Self-shoot notes: shoot the steps in order on a tripod at three distances (medium, medium close-up, macro) and one selfie wrap; speak while doing; record the CTA as a separate 1-second insert.

---

## 6. Website tour (creator + real screenshots)

Result: ONE talking-head creator on camera speaking continuously; real mobile screenshots of the supplied page appear as large static overlay cards. There is no sheet and no generated UI; screen content is always real captured pixels (never generated, restyled, animated or invented) and cards are never full-screen or scrolling. Stay in this format when the page itself must appear (site tour, SaaS UGC, a product page shown on screen); otherwise use the product formats.

Hard rules: body clips are visually product-free (a physical product may appear only in the closer, only from a real image on the supplied page, and the body prompt must not mention the product at all or the model invents a fake one); the same creator reference in every clip; captions ON by default (`Both` hook plate + subtitles, `Subtitles`, or `Hook`; only an explicit "no captions" skips them); never ask the user to record their screen; never use unrelated sources to fill missing page content; never render a website, app UI, screen, monitor or browser inside a clip (add to EVERY clip: "No website, no web interface, no app UI, no screen / monitor / browser / rendered content on any phone or device screen anywhere in the shot"; video models render UI text as gibberish).

Capture: get 6-10 useful mobile stills of the page (hero with logo and navbar, features, dashboard/search/editor screens, a couple of reviews, pricing plus a specific plan, specs, distinct product views) plus one full-page capture to build the section map. Browser devtools mobile emulation or a real phone screenshot work. Be granular and skip nav, footer and logo strips. Reviews, pricing and specs are often behind tabs and not in the full-page shot, so capture them separately; capture one still at the top of the page with the logo and navbar in frame (the hero card). Do not upscale, restyle or edit captures; cookie banners must not be in a card. Crop by absolute pixel rect, never by a fraction of the page height (repeat captures of one URL vary in height by ~14%), and beware image tools that cap large pixel counts on very tall full-page screenshots. If capture fails (bot wall, login gate, blank page, unreachable, fewer than 3 usable cards): ask once, "I'll send screenshots" (use them as-is, usually desktop frames, no cropping to 3:4, contain-fit) or "make it without the site" (talking-head only; say so in the report). Never retry on your own or search the web for images.

Section map: record sections top to bottom with a key/filler flag; the same order drives the script beats and the card order. The first card is the hero, anchored to the beat that names the site; then details/product, reviews, price/warranty.

Script: hook (first 1-2s, ~8-12% of runtime, <= 8 words with a token, no greeting, no pointing intro) then body (~70%: the first body beat names the site, then one concrete line per section while its card is up, beats follow the card order, many beats ideally one per still) then closer (~15%: the result, concrete, CTA riding inside it, while the creator acts: pick up / hold up a physical product from a real page image, or for SaaS/app/service act on a phone with the screen turned away or blank). Delivery ~2.4-2.7 words/second with varied pace (quicker on connectives, slower to land the number/price/CTA), contractions, one live imperfect beat, performed dialogue, ONE engineered pause at most. Save: the full script, the hook line (<= 6 words for the plate), and the ordered `{section_label, words}` beats. Write in English unless the video is explicitly in another language.

Clip prompt (one continuous shot per clip, NO sheet, NO cuts): subject = the creator (same reference every clip, never re-described); framing vertical 9:16, medium shot, creator about 2/3 of the frame, head CENTERED horizontally and vertically (no top headroom), eyeline into the lens, hands kept out of the bottom ~15% (caption zone); setting = the locked self-film scene (phone propped, real home, couch/desk, natural light), the same in every clip; action = talking to camera with natural hand gestures, American accent (never British), ~2.4-2.7 wps with varying speed; the beat's line verbatim; audio = iPhone front-camera mic, ambient = the natural sound of what the scene shows, low under the voice, no music; the website ban line; the closer adds the real product image as a second reference. Pre-submit check: reject any prompt containing `Hard cut`, `Cut 1`, `slot`, `board`, a product name in a body clip, or `website` / `UI` / `screen` / `browser` outside the ban line. Keep the realism pass handy for the creator still.

Composite (Premiere Pro or After Effects; all numbers are fractions of the frame, 1080x1920):
1. Concatenate the talking-head clips; keep the audio untouched; export once.
2. Cards float OVER the live face with no blurred copy, no solid backing, no pad.
3. Timeline: `t(cum) = T * cum_words / total_words` over the continuous voice. The hook gets NO card (`t_hook = min(2.0, t(hook_words))`). Each body still is its own card anchored at its beat: start `s_k = t(cum words before the beat)`, end `e_k = s_k + 1.4` (~1.2-1.5s), `s_k >= t_hook`, a ~0.3-0.5s clean-face gap between cards (push a later anchor back if it collides). The first card is ALWAYS the hero at the site-naming beat. The closer gets NO card (drop any window that would spill past `t_closer = t(total - closer_words)`). More cards come from more captures and more narrated beats, never from longer windows.
4. Geometry: contain-fit inside a box of 0.78W x at most 0.60H, centered horizontally and shifted up 0.04H (about 1080x1152 box, offset about 77 px up), so the bottom lands near 0.80H, clear of the bottom ~15% caption band. A tall card shrinks until it fits, which also normalizes card sizes. Never cover-crop a card; a wide desktop screenshot simply lands shorter.
5. If the anchors drift off the spoken words, re-time each card from a real word-level transcript of the finished audio.
6. Captions on top (see `hooks-and-captions.md` section 8), protecting the cards, the face and the hook plate. Fewer than 3 cards = talking-head-only fallback.

Self-shoot notes: this format is nearly free to shoot yourself: phone propped on a desk, one continuous take per beat group, screenshots from your own phone, composite in Premiere.
