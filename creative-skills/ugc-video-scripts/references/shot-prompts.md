# Shot prompts: image frames and video clips for UGC

Contents:
1. Two production modes (shot-by-shot vs multi-cut clip)
2. Shot card and the camera cadence that forces real cuts
3. Image prompt template (the still for one shot)
4. Video prompt templates (single shot, multi-cut clip)
5. Hands, POV and product handling laws
6. Performance menus, hook devices, one-take moves
7. Audio line and performed dialogue
8. Quality tail and negatives, realism pass, troubleshooting

## 1. Two production modes

Pick one per project. Both use the same creator frame (see `creator-persona.md`) as the reference image in every generation.

- **Shot-by-shot (default, works in any tool).** One still per shot (image model), then one short clip per shot (image-to-video with that still as the start frame). You assemble in Premiere/AE. Most control, best for KLING or any single-shot video model. Generate each clip a little longer than the shot needs and trim in the edit.
- **Multi-cut clip (the original recipe, for models that follow written cuts).** First build a contact sheet: one wide image holding N equal vertical 9:16 panels in one row (8 panels for a ~15s talking format, 4 panels for product/unboxing/tutorial). Then feed the sheet plus the creator frame (plus product photo) to a video model, with a prompt that writes `Cut 1 ... Hard cut to. Cut 2 ...`. The model turns the panels into hard cuts inside ONE clip. The sheet is a narrative map, not frames to copy. The original recipe used a 21:9 sheet (2k, high quality) of 9:16 panels and a 9:16 1080p clip with native audio. If the sheet comes back with the wrong number of panels, merged panels or text, use shot-by-shot instead.

Why cadence matters in both modes: a model snaps a boundary into a crisp hard cut only when the two neighbouring beats are visually FAR apart. Two low-delta neighbours (same POV, same distance, same action) MORPH into a blend.

## 2. Shot card and camera cadence

Shot card fields: `#`, duration, role (e.g. PACKED / REVEAL), POV (SELFIE or STATIC), distance (TIGHT / MID / WIDE band plus the exact word), action (one physical action), hands (role of each hand), product state, expression, spoken line or VO, SFX.

Anti-morph rules (hard):
1. POV alternates every shot. Never two consecutive shots in the same POV (walk SELFIE and STATIC down the row).
2. Distance band rotates. Bands: TIGHT (tight close-up, MACRO), MID (medium, medium close-up), WIDE (three-quarter, waist-up, full-body, product-extended). Adjacent shots come from different bands; across 8 shots every band appears at least twice; no run of three in one band.
3. A different physical action every shot. Never the same hand-product configuration twice in a row.
4. Shift angle or micro-location where the story allows (a background change is the strongest cut-forcer).
5. No two adjacent shots share BOTH POV and distance band.

State the framing word in every shot: `TIGHT CLOSE-UP`, `MEDIUM CLOSE-UP`, `MEDIUM`, `MEDIUM-WIDE`, `MACRO`, `THREE-QUARTER`, `WAIST-UP`, `FULL-BODY WIDE`, `PRODUCT-EXTENDED`.

Default 8-shot cadence (talking review): `SELFIE-MID, STATIC-WIDE, STATIC-MACRO, SELFIE-TIGHT, STATIC-MID, STATIC-MACRO, STATIC-WIDE, SELFIE-TIGHT`.
Default cadences for 4-shot formats: unboxing `STATIC, STATIC, STATIC-CLOSE, SELFIE`; tutorial `STATIC, STATIC, STATIC (close-up), SELFIE`; product `STATIC-WIDE, STATIC-MEDIUM, MACRO or FIRST-PERSON-POV, STATIC-WIDE`.

Time slicing: split the clip evenly across the cuts; fast even beats ARE the format.
| clip length | 8 cuts | 4 cuts |
|---|---|---|
| 8s | ~1.0s each | 2.0s |
| 10s | ~1.25s each | 2.5s |
| 12s | ~1.5s each | 3.0s |
| 15s | ~1.9s each (0-1.9, 1.9-3.8, 3.8-5.6, 5.6-7.5, 7.5-9.4, 9.4-11.3, 11.3-13.1, 13.1-15) | ~3.75s |

Long videos: a clip is 4-15s. Plan the minimum number of clips that keeps the total (16s = 12+4, 19s = 15+4, 31s = 15+12+4, 46s = 15+15+12+4). Later clips continue mid-thought (no greeting, no re-introduction).

## 3. Image prompt template (one still)

```
[Reference line] The same person as the reference image, identical face, hair, body and identity. Same outfit as the reference. [If product] The product is the item in the product reference, exactly one unit in frame, same label, same colour, same visible side, realistic size: [hand-relative size + cm, e.g. "palm-sized, fits entirely in one hand, ~15 cm tall"]. If the label is small in frame, move the camera closer, never enlarge the product.
[POV + distance word]: [one action, MID-EVENT (hands already moving), with the role of EACH hand named, the idle hand parked: "left hand holds the phone off-frame, right hand holds the product"]. [Expression with named mechanics: brows, eyes, mouth]. [Product placement: fully visible in one hand / fully hidden in a closed bag / absent].
Setting and lighting identical to the reference: [room], [light direction], neutral daylight, one motivated light source, consistent white balance.
Shot on iPhone, casual handheld framing, deep focus, mild phone-wide edge distortion, phone-sensor grain, pore-level skin, mild HDR flattening, faint shadow noise. Authentic UGC creator phone photo, NOT editorial photography, NOT studio, NOT magazine commercial.
No on-image text, no watermark, no mirror or reflection, no bokeh, no lens flare, no beauty filter, no cinematic grade, no fisheye, no third arm, no extra hands, no deformed hands, no duplicated limbs.
```
Notes:
- Do not re-describe the creator's face in words when a reference image is attached; re-description fights the reference. Describe action, not appearance.
- Frame one of every shot is MID-EVENT: the hand already at the tape edge, the head mid-turn, the product mid-lift. Never a posed "about to start" frame.
- Label handling: with a real product photo the label keeps its real text (the reference carries it). With no photo, write "small label, turned slightly away, too small to read". No other prop carries legible text or numbers (receipts, screens, price tags render as random characters).
- Product shown only if the shot's action needs it: show / open / apply / react-with-it = visible; transit, setup, problem moment, talking-head hook = hidden (fully inside a closed bag/box/pocket) or absent. Forbidden placements: half-sticking out of a bag, balanced on an open bag, wedged between objects, floating, peeking from a pocket, partially visible inside a box.
- Absent features stated visually in the shot AND the negatives ("hand-pump only, completely cordless, smooth body with no buttons" + "no power cord, no power button, no charging port, no digital display"), otherwise the model re-adds the default affordance.
- Nano Banana Pro: give it the creator frame (and the product photo) as image inputs, and any text as an exact string in quotes. For tutorial step captions, the safer route is to add them in Premiere/AE/Figma instead of baking them.

## 4. Video prompt templates

### 4a. Single shot (shot-by-shot mode; KLING, Seedance, Cinema Studio)
```
Start frame: the attached still. [Motion in plain action verbs: what the hands and body do during the shot, 2-3 concrete micro-behaviours, one within-shot change]. [Expression evolution]. Camera: [SELFIE: handheld front-facing, intimate, slight natural micro-shake from her grip | STATIC: locked-off, completely static, no shake, no drift]. [Optional ONE baked camera move, see below].
Audio: [She/He speaks to camera, iPhone microphone with natural room tone: "line"] OR [off-screen voiceover only, mouth closed].
Facial features clear and undistorted, consistent clothing throughout. Shot on iPhone, natural lighting, social media vertical 9:16. No on-screen text, no subtitles, no watermarks, no cinematic grade, no film grain, no bokeh, no lens flare, no slow motion, no beauty filter, no third arm, no extra hands, no duplicated limbs, no deformed hands.
```
Rules: one subject, one action, camera in its own sentence. A SELFIE shot never shows the phone: the camera IS the phone; only her free hand or forearm may touch the frame edge. Forbidden words in a SELFIE description: `mirror selfie`, `looking at her phone`, `phone in her hand`, `holding phone up to face`, `over-the-shoulder`, `phone screen visible`, `reflection`, `mirror`. Forbidden words in a STATIC description: `handheld`, `shake`, `drift`, `wobble`, `sway`, `slight movement`, `micro-shake`, `intimate handheld`, `natural movement`, `subtle movement` (they leak motion).

### 4b. Multi-cut clip (Seedance-style, EN or ZH)
```
Style & Mood: UGC iPhone aesthetic, [light matching the sheet], [SELFIE: front-facing camera, intimate handheld feel | STATIC: locked-off static camera, completely static, frozen frame | MIXED: starts SELFIE handheld, hard-cuts to STATIC locked-off, hard-cuts back to SELFIE handheld, POV alternates per cut], social media vertical format.

Narrative Summary: [1 sentence: what happens in this clip and the throughline of the cuts]. Performed by a natural, engaged creator, genuine reactions, lively but human, never staged screaming energy.

Dynamic Description:
Cut 1 (0-1.9s) [framing word] [POV]: [action from panel 1 as MOTION, hand allocation, 2+ micro-behaviours, expression, product placement if any]. Hard cut to.
Cut 2 (1.9-3.8s) [different framing/POV]: [...]. Hard cut to.
...
Cut 8 (13.1-15s) [...]: [...].

Static Description: [1-2 sentences: setting, ambient details, props, light direction, matching the sheet].

Audio: She speaks to camera, iPhone microphone audio with natural room tone: "[line distributed across the cuts at phrase boundaries]"

Facial features clear and undistorted, consistent clothing throughout. Shot on iPhone, natural lighting, social media aesthetic, [SELFIE: slight natural handheld micro-shake from her grip | STATIC: locked-off static camera, absolutely static, zero camera movement of any kind, no shake, no drift, no breathing wobble | MIXED: handheld micro-shake during selfie cuts, locked-off frozen frame during static cuts]. No on-screen text, no subtitles, no captions, no watermarks, no legible text on any object except [the product's own label and] the garment's own large fictional print, no real brand logos anywhere, no cinematic grade, no film grain, no bokeh, no lens flare, no fisheye lens, no ultra-wide distortion, no slow motion, no beauty filter, no third arm, no extra hands, no duplicated limbs, no deformed hands.
```
Rules:
- `Hard cut to.` appears verbatim between every pair of cuts (7 markers for 8 cuts, 3 for 4). Without it cuts collapse into smooth motion. Only the one-take move (section 6) may replace exactly one marker.
- The sheet is fed in as a reference AND your prompt is the primary signal: keep it dense or the model copies panels frame for frame and the result looks stiff. If a sentence in a cut could be a caption for the panel, you are transcribing: rewrite it as motion, change, breath, weight transfer.
- Do not contradict the sheet (POV, which hand holds what), but go beyond it.
- 4-cut formats: same structure with four cuts and the roles of the format (PACKED / REVEAL / PRODUCT-FOCUS / SATISFACTION, PRODUCT-INTRO / DEMO-A / DEMO-B / RESULT, Step 1-4).
- For male creators use "He speaks", third person throughout, never mix genders.
- Time spans must sum to the clip duration exactly.
- Optional music: only if asked; ONE line directly after Audio: `Music: [genre/mood], low in the mix under the voice, swells at [the peak beat], returns under the closer.` Music always ducks under the voice, no lyrics (lyrics fight lip-sync), never per-cut music.

### Baked camera moves (opt-in, at most ONE per cut, never on every cut)
- Slow push-in / gentle ease-back: `the camera slowly PUSHES IN across the cut (a gentle dolly-in)` on a reveal or reaction beat, or `eases back and PULLS OUT` to open a wider beat. On a locked cut one deliberate push-in is the sole exception to the freeze (`locked framing with one deliberate slow push-in, otherwise static`).
- Candid handheld zoom-in opener (Cut 1, SELFIE): `candid HANDHELD iPhone ZOOM-IN toward the face, the frame pushes in fast and a little unsteady, a tiny overshoot-and-correct, like a real hand pinch-zooming, never a smooth professional dolly`; the first word lands during the zoom.
- UGC camera realism for Style & Mood: deep focus (background sharp), 23mm-wide look, mild edge distortion (phone-wide only, never fisheye), one AE/AF adjustment mid-clip (SELFIE cuts only), mild HDR flattening, faint shadow noise, pore-level skin, real weight and contact shadows, hair and fabric react.

## 5. Hands, POV and product handling laws

### Hand-count law
The creator has exactly TWO hands. Simultaneous hand roles per shot total at most 2, and each hand's role is named.
- SELFIE: one hand holds the phone (off-frame or forearm at the edge), so only ONE hand is free, holding ONE object total. If the action needs two free hands or two objects, switch to STATIC (phone not in frame).
- STATIC: both hands free. Two-hand actions are legal when the action needs both ("left hand steadies the jar on the counter, right hand twists the lid"), with no other simultaneous job.
- An action load that implies a third holder ("holds the box while unwrapping the ribbon while waving") renders a phantom arm: rewrite. A product floating unheld next to busy hands does the same: it is held or it is resting on a surface.
- Sequence multi-step actions across the cuts (show, cut, open). Count the roles before finalizing.
- Decision tree: walking/outdoor + nothing in hand = SELFIE; + ONE bag = SELFIE; bag + visible product = invalid (hide the product in the bag, drop the bag, or go STATIC); indoor holding product alone talking = SELFIE or STATIC; opening cap / twisting dropper / pumping = STATIC; applying while holding the bottle = STATIC; product in palm close-up = STATIC close-up; reaction/CTA with product in one hand = either.

### Safe interaction verbs
| Material | Safe | Forbidden |
|---|---|---|
| Glass / hard plastic / metal | rests on palm, holds lightly, cradles, presents, taps gently, points at | squeeze, crush, clench, twist body, deform |
| Soft tube | holds, gently squeezes, presses lightly | crushes, wrings, twists violently |
| Fabric / clothing | wears, adjusts, smooths, drapes, holds up | stretches unnaturally, yanks, wrings |
| Cardboard box | holds from sides, presents front face, opens flap if visible | crushes, bends, folds unnaturally, tears |
| Food | bites, pours, scoops, stirs, serves | throws, juggles, morphs, multiplies |
| Tech / electronics | holds, presents, points to screen/detail | opens compartments, plugs cables |
| Any product | holds, shows, lifts, presents, points at | throws, catches, juggles, spins, drops |
When unsure: hold-and-present only.

### Product interaction sequences (name exact mechanics, never "opens it / applies it")
| Product | Sequence |
|---|---|
| Perfume / cologne | hold base, lift cap straight up, cap disappears, press nozzle, mist on wrist or neck |
| Serum dropper | hold bottle, unscrew dropper counterclockwise, lift pipette, squeeze bulb, drops on fingertips |
| Cream jar | hold base, twist lid off counterclockwise, lid disappears, fingertip scoop |
| Soft tube | hold middle, flip or unscrew cap, squeeze, product on fingertip |
| Pump bottle | hold base, press pump head with two fingers, product on palm |
| Lipstick / balm | hold base, pull cap straight off, cap disappears, twist base, swipe lips |
| Mascara / gloss wand | hold tube, unscrew wand, pull out slowly, apply |
| Compact / powder | hold compact, flip hinged lid open (lid stays attached), tap brush/sponge, apply |
| Spray bottle / mist | hold bottle, remove cap if visible, press trigger, mist target |
| Food / drink | show package, open if plausible, pour/scoop/bite/drink naturally |
| Clothing / shoes | hold up, wear, adjust fit, smooth fabric, point to detail |
| Cordless vacuum / appliance | grip handle, press power/trigger, glide over surface, release |
| Blender | place on counter, secure lid, press button, contents move inside, pour result |
| Drill | grip handle, align bit on target, squeeze trigger, controlled drive |
| Tech (generic) | hold-and-present, point to screen or exterior detail, no cable/button mechanics |

Rules: cap removed BEFORE contents exit; after removal never describe where the cap goes (it ceases to exist) and never re-close; max one opening + one usage action per cut; one state change per cut; one press, one mist, one swipe, one sip, one scoop. Forbidden action phrases (read as loops): `sprays again`, `another spray`, `sprays multiple times`, `keeps spraying`, `presses repeatedly`, `presses again`, `taps the lid twice`, `back and forth`, `unscrews and screws back`, `opens and closes`, `applies multiple coats`, `swipes again`.

Body-part target lock (override a wrong user target silently, physics beats wording):
| Product | Apply to | Never |
|---|---|---|
| Perfume / cologne / mist | wrist or neck | palm, face, eyes, hair, lips |
| Cream / serum / lotion | fingertip first, then face or hands | straight to face from container, eyes |
| Lipstick / balm / gloss | lips only | cheek, neck, forehead, eyelids |
| Drink | bottle or glass to mouth | wrist, palm, face |
| Powder / blush / bronzer | cheek with brush or sponge | lips, eyelids, neck |
| Mascara | eyelashes only | brows, lips |
| Eyeliner | eyelid lash line | cheek, lips |
| Foundation / concealer | fingertip or sponge to face | directly from bottle, eyes |
| Hair product | hair only (mid-length to ends) | face, neck, lips |
| Food | mouth | other body parts |

Mechanism anatomy: name the parts, positions and flow once and repeat verbatim ("pump head on TOP, pressed DOWN; product exits the nozzle"). Cause before effect (press, mist, reaction). One vessel (the cup she poured).

Tech peripheral grips (ergonomic, never a fingertip pinch): gaming mouse = full palm cup, fingers over the buttons, thumb on the side, palm base on the pad; keyboard = both hands in typing position on the home row, or one index finger on a specific key for a macro; over-ear headphones = held by the headband or worn; earbuds = pinched by the stem or worn; controller = both hands on the grips, thumbs on sticks, index on triggers; smartphone = vertical hold by the side edges, or cradled with the other hand swiping; smartwatch = worn; tablet = cradled under the bottom edge; laptop = on a surface, both hands typing; stylus = pencil grip.

Weight and grip: Heavy (appliance, bottle >= 1L, kettlebell, dumbbell >= 3 kg) = BOTH hands, lean forward, visible strain (jaw set, brow furrow, controlled exhale) combined with the reaction. Bulky but light (large pillow, empty big box) = both hands, NO strain. Light (cosmetics, phone, small bottle, jewelry case) = ONE hand, relaxed. Tiny (earring, pill, lens) = pinched between thumb and index, close to the lens. One-handed lifting of heavy items and two-handed strain on light items both read as AI. Paired products (dumbbells, gloves, earrings): never both on one palm; one in each hand, or one displayed and one set down, or both side by side on a surface. If ambiguous, assume the heavier class.

Realistic scale (hand-relative plus cm, never object comparisons, they drift oversized): perfume 50-100 ml ~10-12 cm; cologne 100-200 ml ~13-16 cm; serum dropper 30 ml ~8-10 cm; cream jar 30-50 ml ~6-8 cm wide; soft tube 12-18 cm; lipstick 7-9 cm; mascara/gloss 10-12 cm; pump bottle 250 ml 18-22 cm (two-hand grip); compact 7-10 cm wide; spray bottle 15-20 cm; energy drink can ~12 cm (slim ~16); single-serve snack bag 15-20 cm; phone-sized device ~15 cm (state in cm, not "phone-sized").

Product lock: Angle Lock (the product shows only the visible side from the reference, never rotates, spins or reveals unseen sides; camera moves, the product's visible side does not; with several reference photos switch angle only by hard cut). Exactly ONE unit in frame wherever it appears (write "exactly one bottle", or "the only bottle-shaped object in frame is the product"; models multiply products on words like "shopping" or "lots of"). One state per prop per shot (cap on OR off). Across clips an opened product stays open.

Other universal rules: no mirrors or reflections anywhere (they spawn extra limbs; GRWM/vanity scenes keep the mirror out of frame; if unavoidable, a partial shoulder-up sliver matching the subject exactly plus `no extra limbs, no duplicated person`); no phone visible in any frame; a character who exits the frame is gone for the rest of the clip; at most 3 characters per shot (duets: second character gets ONE fixed description repeated verbatim every cut, archetype contrast, lock left/right); at most 4 visual beats per shot; never describe the creator's age with words like boy/girl/kid/young/teen inside video prompts.

## 6. Performance menus, hook devices, one-take moves

Default register is NATURAL: lively, engaged, ONE honest human-scale peak (a real jaw-drop, a breaking grin, a delighted laugh), never staged screaming. A flat-neutral prompt renders a wooden presenter because video models under-render energy, so keep micro-behaviours concrete in every shot. Switch to HYPED only when the brief carries an explicit energy signal (hyped, energetic, explosive, high-energy, viral energy); switch to CALM only on goth, noir, cold, deadpan, clinical, refined, luxury-passive, minimal, somber, serious, dark, quiet, GRWM, routine, process-led. The user's word always wins.

NATURAL menu: raised brows with a genuine grin, small bright laugh, lean-in toward the lens, head tilt with narrowed appraising eyes, surprised blink, satisfied slow nod, half-laugh through the nose, breaking grin she doesn't fight, delighted eyebrow flash, quick glance down at the product then back up with a warmer smile, honest jaw-drop that relaxes into a smile, hand-to-cheek small disbelief, weight rock back with a pleased exhale, quiet appreciative head shake; image-side extras: slight lean toward camera, glance down then back to lens, hair tuck, small nod, pointing at product, holding product closer to camera, tapping label, posture shift, pause before reveal, mock-confused squint, chin tuck with raised brow, eye-roll then quick grin back to lens, mid-bite face (food/drink), thumb-wipe at corner of mouth.

HYPED menu (explicit signal only): WILD open-mouth scream-gasp (jaw dropped wide, eyes blown wide, neck tendons visible), mouth blown open in full scream of excitement, victorious mouth-open shout, dramatic head jerk back recoil with explosive joy, cheek puff then deflate, mid-bite then explosive react-scream, lip wipe with thumb at corner of mouth, eyebrows shoot skyward, knuckles white grip-tighten, mock-confused squint then break-into-laugh, slow head shake with massive grin, full-body satisfaction shudder, tongue-press inside cheek, eye-roll then explosive grin back to lens, head thrown back with burst of laughter. Under hype signals keep peak energy in every shot, never de-escalate, never `half-smile`, and vary the body event per shot.

CALM menu: weight shift, hair touch, glance break, head tilt, eyebrow flash, hand gesture, posture shift, lip movement, shoulder shrug, breath (inhale / exhale / sigh / sharp inhale), jaw set, neck tendon definition, knuckle tightening, foot pivot, brow furrow, chin tuck, lean forward/back, micro-grin, half-blink, slight off-center handheld tilt. Calm beats on stills: dramatic deadpan stare into lens, settled gaze, slow controlled gesture, quiet half-smile, satisfied exhale, small nod, deliberate stillness.

Expression patterns across the cuts (never the same expression twice):
- Pattern N (default): opener = genuine curiosity or a grin already breaking, brows raised, lean-in; middle = animated focus, a DIFFERENT small live beat per shot; peak = ONE genuine human-scale reaction on the reveal/result shot; close = warm confident recommendation.
- Pattern A (warm-but-restrained): curious casual opener, animated middle, warm satisfied close.
- Pattern C (deadpan-then-crack): deadpan stare at the lens, hold it, then break-character grin as the key action lands, relaxed wrap.
- Pattern D (sustained passive): low-key neutral half-lidded opener, minimal reaction, slow controlled gestures, quiet half-smile close, never high energy.

Peak = body event. The peak shot pairs its expression with ONE body reaction (a peak read only in the face is weak): sharp gasp with a free hand flying to chest or mouth; leans back out of frame wide-eyed; jaw drops and STAYS dropped, eyes to the lens; double-take frozen mid-whip back to the product; covers mouth, muffled-squeal face, eyes crescent with laughter; open palm slapped flat on the surface; presses the product against the cheek, eyes closed (satisfaction shots only); shakes the product at the lens mid-grip; hand flying to the chest mid-gasp (selfie-safe); both hands framing the face in disbelief (static only); head thrown back mid-laugh; full-body lift onto toes (static only). The body event replaces one micro-behaviour; it obeys the hand-count law (in SELFIE it uses the one free hand).

Unguarded beat (every clip): at least one recovered eye-flick, mid-thought stumble, post-laugh settle, quick self-correction or re-found composure; wooden, posed-throughout performances read as AI. Playful improv (one small goofy moment per clip, skip in calm registers): tongue-out flash, blep face, crossed-eyes mock, mock-zen closed eyes, eyebrow waggle, exaggerated mock-thinking face with finger on chin, double thumbs-up with cartoon grin, mid-gesture cartoon shrug, mock-disappointment slow head shake. Sound intrusion (optional, max one per clip, never during a peak or the CTA): name a precise off-frame sound that belongs to the location (`a kettle starting to whistle off-frame`, `muffled neighbor's drill, two bursts`), add a physical glance beat (eyes flick off-frame, half-turn of the head, one beat of stillness), return to the lens within ~1.5s, no spoken acknowledgement.

Quirk beat (residue products: foam drinks, lip cosmetics, chocolate/cream, powdered snacks, sticky/drippy food): one brief unguarded aftermath AFTER the main action (thumb-wipe at the corner of the mouth, soft tongue-press inside the cheek, thumb-rub of fingertips, a self-aware grin), staged large for ~1.5-2s, sound named as a single loud event ("one loud crisp lip-smack"). Never the main beat, never repeated, never in the same beat as the peak. A physical signature behaviour named in the brief becomes THE quirk: stage it LARGE (the acting body part fills its zone of the frame, mechanics ~30% bigger than natural), one shot only, never in a macro shot, never stacked on the peak, charming not mocking.

Hook devices for frame one (0.1-second hook law: the first clause is motion and the first word or sound lands within 0.0-0.4s of frame one; no silent lead-in, no breath-before-speaking). Patterns H1-H8 are in `hooks-and-captions.md`. Optional camera-arrival devices (SELFIE shot 1 only, hook roles only, at most one per clip, written as FRAME physics, never "drops her phone", resolves into shot 1's composition within ~1.5s, with an audio twin in the room-tone clause):
- Drop-Catch: the frame is already tumbling, world spinning, then caught and righted; first word lands during the catch.
- Lens Wipe: smeared half-blurred image; a sleeve wipes across the lens; the frame clears onto shot 1.
- Pocket Start: darkness, muffled audio, fabric sounds; the frame pulls free, light floods in, her face appears mid-rant.
- Walk-and-Slam: violent handheld motion, breath audible, background streaking; she drops into a seat and the frame settles on her already talking.
- Zoom-Out Reveal: extreme digital zoom on an unexplained detail; quick zoom-out reveals what it is; the first line refers to the detail.
- Light Switch: near-black, only her voice; a lamp clicks on and the scene appears already mid-moment, sound leading picture by half a second.
- Focus Hunt: autofocus breathes, hunting between face and product, snaps sharp on the product exactly as the key word lands.

One-take moves (replace exactly ONE `Hard cut to.` per clip; default on the closing clip's final boundary when legal; elsewhere only on a one-take/honest-take brief):
- Set-Down (SELFIE to STATIC, still mid-sentence): frame physics only ("the frame swings down, tilts, and settles") at a slightly low, slightly crooked angle; she steps back into full view, both hands free, and keeps talking. After it, STATIC language applies.
- Pick-Up (STATIC to SELFIE, strongest right before the closer): "she walks toward the camera and reaches past the lens, the frame lifts, shakes for a beat, and becomes handheld again, her face close and slightly wide-angled". Never "grabs the phone".
- The voice runs THROUGH the move. Never across a state jump (cap on to off, packed to revealed, outfit change): that hard cut hides the jump and must stay. The move costs ~1.5s inside the neighbouring cut spans.

Loop ending (final clip only): the last shot ends mid-motion (unresolved action) or frame-matched to the opening framing (single-clip videos). Visual only, never repeat a spoken line; the CTA rides inside the resolution, never as an outro beat. A mid-phrase timing cut (final phrase still in her mouth when the clip ends) is the loop device for multi-clip videos.

## 7. Audio line and performed dialogue

```
Audio: She speaks to camera, iPhone microphone audio with natural room tone: "<line, verbatim, split at phrase boundaries across the cuts>"
```
- First clip may open with 1-3 bracketed non-verbal sounds (not counted as the first word). NATURAL pool: `[*small bright laugh*]`, `[*soft gasp*]`, `[*delighted 'oh!'*]`, `[*ooooh*]`, `[*open-mouthed exhale*]`, `[*choke-laugh*]`, `[*incredulous scoff*]`, `[*sharp inhale*]`, `[*mock gasp* "wait"]`. HYPED pool (explicit energy signal only): `[*explosive gasp*]`, `[*barely-contained scream*]`, `[*hyped yelp*]`, `[*excited shriek*]`, `[*explosive shocked inhale*]`. Rotate; never repeat the combo on consecutive clips; skip entirely in calm registers; none on later clips; for tutorials skip them when the tone is instructional.
- Later clips open mid-thought. Forbidden openers: hey, hi, hi guys, hey everyone, what's up, today I'm showing you, I want to share, I just got, I wanted to tell you about, let me show you, so this is the [product], as I was saying, going back to, anyway, okay so / alright so as a fresh start.
- Each cut owns a different chunk of the line: no sentence or near-identical phrase in two cuts.
- Performed delivery markup (words stay as written, never add or reorder): vowel stretch on at most 2 emotional words per clip (`soooo`, each eats ~1.5s), CAPS spike on at most 1-2 words per line, ONE broken sentence at the peak (`it's... okay wait. LOOK.`), at most ONE whisper-to-spike switch per clip written as delivery direction. Breath events are timed physical actions in the cut text ("a sharp audible gasp, hand flying to her chest"). Never engineered or dramatic pauses.
- Protect the mouth: lip-sync is the weakest render zone (doubled lip edges, smeared corners, waxy texture). Give every dense cut one closed-mouth beat (lips together, no voice) and shed words toward voiceover shots. The fix for a dense script is fewer words, never faster speech. Natural pace is ~2.4-2.7 words/second, never crammed.
- Persona and accent: only on an explicit request. Open the Narrative Summary with ONE vivid persona sentence (`[origin/identity] + [attitude] + "speaks and moves exactly like that"`), restated verbatim in every clip (clips generated apart drift). Echo it in the Audio line ("She speaks to camera with a strong [origin] accent, [1-2 described qualities], iPhone microphone audio..."). Describe qualities, never phonetic spelling (it breaks lip-sync); write the accent two levels stronger than asked and never `slight/subtle/light`; add `no neutral accent, no generic American voice, no flat monotone delivery` to the tail. If you can supply a 5-10 s voice sample as an audio reference, label it "accent and vocal delivery reference only, do not copy words". Text-only accent lands roughly one render in three.
- Language: the source recipe wrote the spoken line in English because lip-sync renders English most cleanly. For Polish, test one short line first; if the mouth smears, move the line to a voiceover shot (mouth closed) and record the VO separately (see `narration-vo`).
- Voice-over shots: `Audio: Off-screen voiceover, [she | he] describes the product in an emotional UGC tone, NOT on-camera dialogue, NO lip-sync, no on-camera mouth movement, iPhone microphone audio with natural room tone: "<line>"`. Voice gender is locked for the whole video; any visible auxiliary person matches it.

## 8. Quality tail, realism pass, troubleshooting

Quality tail (end of every clip prompt): see the templates above. Add `deep focus, background sharp` and, for product shots, `Shot on iPhone, casual phone framing, phone-sensor grain and realistic textures preserved, no retouch, no professional gloss. Authentic UGC creator phone photo of the product in real-life context, NOT editorial product photography, NOT studio shoot, NOT magazine commercial.`

Banned in any UGC prompt (they produce the ad look): `dramatic side-lighting`, `cinematic lighting`, `moody atmospheric lighting`, `mood lighting`, `shallow depth of field`, `aggressive bokeh`, `creamy bokeh`, `professional DSLR lens`, `lens flare aesthetic`, `editorial product photography`, `product shoot`, `commercial product still`, `studio strobes`, `softbox`, `ring light`, `magazine retouch`, `glossy professional finish`, `polished commercial look`, `flawless surface`, `golden hour`, `warm sunset`, `magic hour`. UGC that looks like cinema reads as an ad; use a cinematic look only if the brief explicitly asks.

Realism pass (run on a generated creator still when it looks slick; an image-edit model, image in, image out):
```
KEEP EXACTLY the framing, composition, pose, subject and identity of this vertical portrait. No reframe, no zoom, no crop, no change to the person's face / hair / body / clothing. CHANGE ONLY micro-realism: true-to-life pore-level skin with natural texture and fine vellus hair, real material detail, even natural daytime light with gentle highlight roll-off and faint true sensor noise, a flat authentic iPhone selfie, deep focus. PRESERVE the face's exact shape / width / proportions 1:1: do NOT squeeze / narrow / slim / stretch the face. AVOID AI-slop: waxy plastic skin, airbrushed poreless skin, beauty-filter smoothing, over-saturation, HDR glow / bloom / halos, oversharpening, teal-orange grade, shallow depth of field, bokeh, cinematic / DSLR look. No added text, no watermark.
```

Troubleshooting:
| Symptom | Fix |
|---|---|
| Cuts blend into a morph | make adjacent shots differ in POV AND distance band AND action; keep `Hard cut to.` |
| Third arm / extra hand | hand-count law; park the idle hand; sequence the action across cuts; add the negatives |
| Product duplicates | "exactly one", remove look-alike shapes, avoid words like shopping/lots of |
| Product label garbled | use the real photo as reference, closer camera, angled-away label for invented products |
| Waxy lip-sync | fewer words, closed-mouth beat, voiceover shot for the dense part |
| Wooden presenter | concrete micro-behaviours per cut, one peak with a body event, one unguarded beat |
| Ad look instead of UGC | remove banned phrases, add the iPhone phrasing and the closing block |
| Face drifts between shots | same reference every shot, do not re-describe the face, restate the persona sentence, see `ai-influencer-casting` |
| Text baked into the frame | add "no on-screen text" to the tail; add all text in post |
| Warm orange cast | neutral cool daylight only; ban golden hour words |
