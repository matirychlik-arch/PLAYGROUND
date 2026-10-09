# App and game surfaces

Contents:
1. Web-app screens: surface selection, layout, templates
2. Cross-template acceptance outcomes (generation-style apps)
3. UX craft rules for app UI
4. Small games: design laws and feel
5. Game performance and delivery

Use this for tool-like screens (generators, galleries, editors) and for small browser games Mati ships as viral-app projects. For marketing pages use `taste-rules.md`; for the concept of the app itself use viral-app-lab.

## 1. Web-app screens

The product surface itself is screen one: never a splash, never a marketing hero.

| Product type | Surface shape | Base layout |
|---|---|---|
| Generator / console (image, video, audio) | Prompt box in the center of the main page, settings pane in or beside the prompt box, results screen after the first generation with a gallery | Studio layout: sidebar plus prompt dock plus feed |
| Pick-a-style-then-generate | Gallery of presets or styles, creation rail, History tab; also the base for upload-configure-iterate workspaces (try-on, restyle, character) | Preset layout: creation rail plus preset grid plus history |
| Single quick tool with a public landing page | Generator hero plus a how-it-works explainer around ONE quick action | Simple app detail page |
| Feed / gallery / history | Filterable grid or list, item overlay or inspector | App shell plus grid section |
| Editor / notes / project tool | List sidebar, work canvas, optional inspector | Split editor/tool |
| Board / pipeline | Horizontal scroll columns inside a fixed shell | App shell with an `overflow-x-auto` region |
| Settings / profile / billing | Single constrained column of grouped sections | Form panel |
| Dashboard / stats | Bands of metric groups, one chart per question | App shell plus sections |

An unusual request maps to the nearest template (a before/after enhance tool maps to the simple detail page; a step-by-step wizard or upload-configure-iterate workspace maps to the preset layout). Do not plan to swap layouts mid-build; rework the closest one.

Density: consoles and tables run tight (`gap-3`, `p-4`); content-first surfaces (feed, gallery, forms) run spacious (`gap-4 md:gap-6`, `p-4 md:p-6 xl:p-8`). One density per region, not per element.

Premium app layout rules: stable shell with meaningful regions (`min-h-dvh`, scroll regions `min-h-0 overflow-auto`; most tools need sidebar or list plus main work area plus optional inspector); space and constraints (`min-w-0`, `truncate`, `max-w-*`, `minmax(0,1fr)` so content never overlaps); every state (selected, hover, focus, empty, loading, error) is a designed surface not bare text; avoid card soup; one icon family; balanced palette from the system with no one-note gradients or blur blobs; no floating loose text or actions without a shell or region.

## 2. Cross-template acceptance outcomes (generation-style apps)

- **Accepted generation becomes visible immediately.** Once a submit returns queued or running items, add them to the visible result set and move focus there. A preset gallery switches to History/Results; an inline-feed layout scrolls or focuses the new card. Show the pending state at once and poll it in place. Validation errors stay on the form; a post-submit failure remains on Results as a failed card with retry. Preserve the chosen preset and composer state.
- **Generated-media galleries are responsive and uncropped.** Use responsive `auto-fit` columns; derive each card's aspect ratio from result dimensions or the submitted aspect ratio; preserve the full image or video (contain or natural sizing). Never force 1:1, 4:3, 16:9 and 9:16 outputs into one crop. Fixed crops only for curated preset or marketing thumbnails.
- **Settings stay usable at every viewport.** Primary controls visible, secondary behind progressive disclosure. A tall settings panel is a real `min-h-0 overflow-y-auto overscroll-contain` region with a visible scrollbar or an edge-fade or "more settings" cue; hidden scrolling is a bug. A pinned Generate action must not cover the last field and must respect mobile safe areas. Below desktop, stack settings above the result or move them into a bottom sheet. Verify expanded settings at 375 px, tablet and desktop with keyboard and touch.
- **History stays inspectable in place.** Every ready card opens a detail view without leaving History, with Previous/Next and Left/Right arrow keys over the current filtered and sorted results. Closing returns to the same tab, filters, sort and scroll position.

## 3. UX craft rules for app UI

Ranked: CRITICAL rules are never skipped; HIGH and MEDIUM only with a concrete reason.

CRITICAL, interaction:
- Touch targets at least 44x44 px, at least 8 px apart; small icons get padding, not bigger glyphs.
- Every clickable element has `cursor-pointer` and visible hover and pressed feedback within about 100 ms. Hover is an enhancement, never the only signal.
- Async actions disable the trigger and show progress; never leave a button clickable while its request is in flight; show skeletons, not a lone spinner, for loads beyond about 300 ms.
- Disabled means the semantic `disabled` attribute plus disabled styling, not faded opacity that still accepts clicks.
- Destructive actions are visually distinct, spatially separated from the primary action and confirmed; for reversible bulk actions prefer an Undo toast over a confirm dialog.
- Drag interactions need a movement threshold (about 6 px) so clicks do not become accidental drags, plus real-time tracking.

CRITICAL, keyboard and focus:
- `:focus-visible` ring on every interactive element; tab order matches visual order.
- `Esc` closes the topmost overlay, one layer at a time; every overlay also has a visible close affordance. Modals trap focus and restore it to the trigger.
- Icon-only controls carry an accessible label; meaningful images have alt text, decorative ones `alt=""`.
- Toasts do not steal focus; 3-5 s; include an action when there is something to act on.
- Do not convey state by color alone.

CRITICAL, overlays: popup content (selects, dropdowns, popovers) must escape scrolling or `overflow` clipping ancestors (portal them); do not render a selector menu as an inline absolutely positioned child of a rail, sticky footer or modal. Use a documented z-layer scale; never patch a collision with `z-[9999]`; avoid accidental stacking contexts (`transform`, `filter`, `opacity`, `isolation`) on wrappers around selector triggers. In nested overlays Esc closes the selector first, then the parent. Test pointer, keyboard, focus trap and click-outside with the selector open near every viewport edge.

HIGH, forms and feedback: visible labels (never placeholder-only), persistent helper text for complex fields, validate on blur or submit not per keystroke, error under the field stating cause and fix, focus the first invalid field, semantic input types and autocomplete, submit ends in a visible outcome (success or error with retry; a timeout is an error with retry), multi-step flows show progress and allow going back, confirm before dismissing unsaved input.

HIGH, layout and responsive: mobile-first; `min-h-dvh` never `100vh`; no page-level horizontal scroll; constrain flexible text; fixed bars reserve space and respect safe areas; one primary CTA per screen with subordinate secondary actions; collapse overflowing toolbar actions into a dropdown instead of shrinking buttons; current location always visible; back navigation preserves scroll and filter state; sidebars collapse behind tabs or a drawer below desktop; verify at 375 px, tablet and desktop.

MEDIUM, motion: micro-interactions 150-300 ms; complex transitions up to 400 ms; exits 60-70% of enter; ease-out in, ease-in out; transform and opacity only; 1-2 animated elements per view; stagger lists 30-50 ms per item; motion expresses cause and effect (a panel slides from its trigger side, a modal scales from center), never decoration; respect reduced motion globally; never block input while animating.

LOW, charts: trend line, comparison bar, proportion donut (5 slices max, else bar); visible legends, tooltips on hover or tap, low-contrast gridlines, `tabular-nums` and locale-formatted numbers; skeleton, designed empty state and error with retry; never a bare axis frame.

Buttons: default size medium on app surfaces (small only in dense toolbars); one accent main action per screen; busy state shows a small loader inside the button; icon-only buttons have fixed dimensions and a label.

State rules: loading (skeleton surfaces or disabled controls), empty (title, supporting text, relevant action), error (styled message with retry, never a raw stack trace), disabled with a short explanation, selected state visible independent of hover, mutations feel instant (optimistic with Undo).

Anti-patterns: raw hex in class names when a token system exists; arbitrary text sizes (`text-[13px]`); mixed icon families or stroke widths; emoji as icons; hover-only selected states; empty, loading or error states as bare text; removing focus outlines; positive `tabindex`; errors only in a toast or page top; restyling a component library's components with overrides.

## 4. Small games: design laws and feel

Plan before code: no game code until the plan is thought through. Profile, laws, concept and system come first, then build, then deliver.

**Game profile.** Place the game on each axis: time (real-time, turn-based, pause-at-will, none), space (continuous 2D/3D, discrete, abstract, absent), agency (one hero, squad, disembodied hand), conflict (vs system, vs players, vs self, none), content (authored, procedural, emergent, player-created), outcome (win/lose, endless, player-set, none), players (solo, co-op, versus, massive), session (minutes, hours, once a day), engagement source (execution, calculation, discovery, expression, story, social, accumulation; pick 1-2). Delivery context: default desktop plus mobile plus gamepad; every verb performable by every declared input method; no hover-only interactions when touch is declared; keyboard bound to physical key codes, never typed letters; all player-visible strings external from day one; performance budgets for the weakest platform.

**Laws.**
- L1 Experience first. Design the experience, not the artifact. Write the experience formula in one sentence: "The player feels ___ because the game constantly ___." No genre labels.
- L2 Meaningful interaction. Every action is discernible (visible effect now) and integrated (echoes later). Test per mechanic: action, visible effect, where it resurfaces. An empty slot is a dead mechanic.
- L3 Mastery. Interest is pattern mastery: one new pattern at a time, the next after the previous one's exam; design the sequence of mastery, not the volume of content.
- L4 Undecided outcome on every horizon (turn, fight, session). Pick 2-3 uncertainty sources tied to real mechanics; randomness lands before decisions, not after; when a source runs dry another must already be active.

**System.**
- Few strong verbs beat many weak ones (strong means several object types respond differently).
- Sign every feedback loop: positive loops snowball, negative loops dampen skill. A comeback from a deficit must exist, and good play must still win.
- Decide visibility per fact; a hidden fact that affects the outcome needs a discoverable trail, or it reads as cheating.
- Interest curve: hook in the first moments, alternating peaks and breathers, maximum near the end.

**Ten subsystems, each a decision or a justified absence:** representation (camera/screen layout never hides information needed for the current decision); input (platform conventions, axes not inverted by default, most frequent actions on the cheapest gestures, conflicting simultaneous inputs resolve predictably); agency metrics (jump length, move range, options on screen, frozen before mass content); resistance by verb matrix (every source of resistance is a question some verb answers); peaks (each period ends in a combined exam of what it taught); rewards (feed the declared engagement source; the strongest reward is a new verb); interface (every element serves a decision, otherwise remove it); economy (every resource has sources and sinks); delivery of mechanics (one pattern at a time); game entry (a short counted path from launch to the first meaningful action; on return the first screen shows the current goal and next step; controls learnable on demand; accessibility options reachable before play).

**Feel (response).** Every action gets an immediate acknowledgment (long operations: instant receipt plus progress). Every significant action has an immediate reaction and a later echo in the world. Polish parameters (shake, hit-pauses, easing) are config data, tunable live. Input is forgiving: generous tolerance windows so honest near-misses count; the player's hitbox smaller than its sprite, the enemy's honest. Stable frame pacing matters more than a high average.

**Balance.** Priced options live on one cost curve (above it dominant, below it junk); keep at least one non-transitive structure (A beats B beats C beats A); perceived difficulty is the gap between the player-power curve and the challenge curve; inflation means sources outrun sinks, so fix sinks not prices; tune expected value and variance separately; soften streaks (pity counters, draw from a deck) and re-count odds; all balance numbers live in data, tuned one change at a time.

**The player's head.** Perception is subjective (critical signals use several channels and never collide, including under colorblindness); attention is a bottleneck (nothing instructional under load, one message at its moment of need); memory decays (the game remembers for the player: current goal and next step visible at any return). Every system state is observable; every refusal explains why and how to lift it; what looks interactive is interactive. Accessibility and localization are data from day one: remappable bindings, options that actually apply (text scale, shake and flash toggles, contrast), strings external.

**Narrative (if any).** The hero's goal is the player's goal; build on state variables not scene-branching trees; every significant choice observably fires later; deliver up the hierarchy: the player did it, saw it in the world, overheard it, read it.

**Visual style.** Derive one style formula (a byte-identical style line reused across every generated asset: art direction, palette, lighting, line weight, perspective) and write an asset manifest (id, role, type, description, size or ratio, style-line reference, source) before generating assets, so sprites, backgrounds and UI look like one game.

## 5. Game performance and delivery

- Performance is a frame budget set before code, for the weakest platform; exceeding it is a crash-grade bug.
- Swarms of same-type entities render as one draw call (instancing or batching), never one each. The hidden is neither drawn nor created. Zero allocations in the frame loop.
- Diagnose in fixed order: draw calls, GPU-bound, CPU-bound, spikes/GC. Measure on a dev overlay (fps, frame time, entity and draw counts) toggled by a query flag before saying "slow".
- Anti-patterns: a mesh or material per instance, default-on shadows and post-processing, full-scene scans every frame, rendering the invisible.
- Architecture by symptom: frame-rate-dependent behavior means a fixed-timestep simulation with separate rendering; class explosion means entity components; replay, undo or multiple input sources mean input as command objects; boolean-flag forests mean a state machine; gameplay poking audio or UI directly means events; object churn proven by a profiler means pools, spatial indexes or dirty flags (never pre-emptively).
- Determinism: fixed timestep plus seeded RNG, logic and visual generators split, so any bug reproduces from its inputs. Debug by observation: reproduce stably, hypothesize then observe (never patch and see), bisect, fix the cause and leave a guard.
- Numbers before code: any numeric criterion (budget, window, limit) is fixed before building the thing it judges and never softened in the iteration that failed against it. Freeze agency metrics before mass content and features once content is complete.
- Limits: perceived quality (composition, animation feel, music) and real player delight need human hands and eyes. Say so at delivery instead of overclaiming.
