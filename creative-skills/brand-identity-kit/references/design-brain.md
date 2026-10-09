# Design brain: decision rules for options

Contents:
1. Source of truth and Creative DNA
2. Visual axes
3. Action modes (palettes, logo mechanisms, typography, critique, revise)
4. Anti-slop rules, one expressive move, scoring rubric
5. Concept boards: the sequence (palette, logo, typography)

This is the internal art-direction layer between the user's input and production. Never show this analysis as a separate concept or ask the user to approve it. It does not render assets, write generator prompts, or store approvals. It turns the current brief and selected draft elements into strong, coherent creative decisions for the next stage.

## 1. Source of truth

Use only:
- Mandatory intake answers
- Uploaded official assets
- Uploaded inspiration/reference signals
- User feedback from prior review stages
- Already selected draft palette/logo/type

Do not run external design research. Do not copy a supplied reference's logo, layout, artwork, pattern, or distinctive device.

### Compile Creative DNA

Privately extract:

```text
PRODUCT TRUTH
What is materially, functionally, or behaviorally real?

AUDIENCE DESIRE
What does the intended audience want to feel, signal, or achieve?

POSITIONING / VALUES
What promise or value must the identity communicate?

NAME CUES
Meaning, sound, rhythm, initials, and useful letter shapes.

REFERENCE SIGNALS
General palette, form, type, composition, material, and energy preferences.

VISUAL AXES
Restrained-Expressive:
Geometric-Organic:
Familiar-Experimental:

CENTRAL MECHANISM
One specific visual idea that can generate a palette, mark, type relationship,
and applications.

FORBIDDEN CLICHES
Generic devices that would make this identity interchangeable.
```

Every recommendation must trace back to at least one Creative DNA field.

## 2. Visual axes

Treat values as directional constraints, not mathematical style recipes:
- Restrained <-> Expressive controls intensity, contrast, and density.
- Geometric <-> Organic controls construction and shape language.
- Familiar <-> Experimental controls category recognition and novelty risk.

Do not invent a value when the user omitted it; use 50 (balanced).

## 3. Action modes

### `PROPOSE_PALETTES`

Input: Creative DNA.

Privately generate several raw candidates, critique them, then return 2-3 distinct palette options.

Each option defines:
- name
- rationale tied to Creative DNA
- background and text colors
- 2-4 supporting/accent colors
- optional gradient logic only when meaningful
- usage relationships
- what cliche it avoids
- 2-3 rough logo mechanism seeds appropriate to that palette (for a palette-only request, omit them)

Palette options must differ in strategic emphasis, not merely hue.

### `PROPOSE_LOGO_MECHANISMS`

Input: Creative DNA + selected draft palette.

Return exactly three distinct symbol-only mechanisms. Each defines:
- mark_type
- central_idea
- visual_mechanism
- distinctive_element: one concrete silhouette, negative-space device, motif treatment, or unexpected locked color-role pairing
- shape_logic
- treatment
- style_register
- user_style_directive: preserve the user's explicit style wording when supplied
- composition
- palette roles used by the mark (choose one, two, or three as the concept requires; three is a maximum, not a target, unless the user explicitly requested more)
- forbidden elements

No wordmarks, taglines, descriptors, or generator prose. Prompt writing happens afterwards under the enhancer grammar in `logo-and-prompt-enhancer.md`.

Each mechanism contains one concept only. State its single visual idea in one clause. Never fuse two symbolic subjects unless the user explicitly requested that exact fusion. "Simple" mechanisms still need the `distinctive_element`; generic geometry or adjectives do not qualify.

#### Logo type routing

Choose mark types from evidence, not taste alone:
- **lettermark_monogram**: only when initials/name letterforms support an ownable construction tied to the brief.
- **pictorial**: only when a literal product/process/object is central and can be represented without a category cliche.
- **abstract**: when the strongest source is a process, benefit, emotion, or relationship rather than one literal object.
- **mascot**: only for strongly character-led, playful, community, or family-facing positioning.
- **emblem**: only for heritage, certification, membership, ritual, or badge/label-heavy applications.

Normally return three different mark types:
1. one name/letter-derived route when viable
2. one product/meaning-derived route
3. one concept/benefit-derived abstract route

If one route is not viable, replace it with the strongest evidence-based type. Never produce three variations of the same mechanism merely with different shapes.

### `PROPOSE_TYPOGRAPHY`

Input: Creative DNA + selected draft palette + selected draft mark.

Return 2-3 font-pair proposals. Each defines:
- display family/source/weight/style
- body family/source/weight/style
- why their anatomy complements the selected mark
- why the pair fits the audience and positioning
- official font links when applicable
- risks/avoid rules

Do not create type scales, line-height systems, or letter-spacing systems.

Choose pairs by:
- matching display-font anatomy to the selected mark's geometry and stroke character
- keeping body text readable and quieter than the display face
- supporting the audience, positioning, and selected visual axes
- ensuring required language/glyph coverage
- using fonts that are actually available through supplied files or Google Fonts

Every option must use a unique display/body combination. Do not repeat the same pair under different names, swap the same two families, or use identical display/body families unless the input explicitly requests a one-family system.

### `CRITIQUE_ESSENTIAL_KIT`

Input: Creative DNA + selected palette + selected logo + selected typography.

Check:
- Is every element traceable to the brief?
- Do logo, palette, and typography express one central mechanism?
- Could the identity be renamed for another brand without meaningful changes?
- Is there one primary expressive move rather than several competing moves?
- Is the mark scalable and producible?
- Does typography complete rather than fight the mark?
- Does the palette support contrast and real applications?
- Does anything copy a supplied reference?
- Does anything rely on generic AI-branding cliches?

Return specific revision instructions for failing elements. Return `PASS` only when the combined kit is coherent enough to show for final approval.

### `REVISE_FROM_FEEDBACK`

Input: Creative DNA + current selected drafts + latest user comment.

Change only the element the feedback targets, then re-run downstream coherence:
- Palette change: recheck mark and typography.
- Logo change: recheck typography.
- Typography change: rebuild wordmark/lockup.

Never restart unrelated stages without a concrete dependency reason.

## 4. Rules

### Anti-slop rules

Reject:
- leaves used as an automatic synonym for organic
- sparkles used as an automatic synonym for premium
- shields used as an automatic synonym for trust
- random gradients used as an automatic synonym for modern
- generic globe/orbit/network marks without product-specific meaning
- arbitrary initials with no construction idea
- gold + serif as an automatic luxury solution
- excessive decorative devices
- several unrelated metaphors combined in one mark
- two metaphors physically fused without an explicit user request
- concepts described only with adjectives
- generic minimal symbols with no described silhouette, negative-space device, motif treatment, or unexpected color-role relationship

### One expressive move

Each direction gets one distinctive expressive mechanism. Supporting elements must be quieter.
- Expressive mark: restrained palette/type.
- Expressive palette: simpler mark/layout.
- Expressive typography: minimal supporting graphics.

### Internal selection rubric

Score raw candidates privately:
- relevance to brief
- distinctiveness
- ownability
- coherence
- category suitability
- scalability
- production feasibility
- application potential
- cliche risk
- reference-copy risk

Discard weak candidates before producing user-facing options. Never expose scores, rejected drafts, or internal reasoning.

## 5. Concept boards: the sequence

The visual concept is not a separate abstract direction. It is the combined result of the user's selected palette, logo mark, and typography. Each generated element remains draft until the user selects it. Approved palette, logo, and typography slots persist independently.

Build options from: the brand/product brief, audience, positioning and tone supplied by the user, user preferences and comments, uploaded references/logos/fonts/colors. Invite uploads before starting. Ask what the user specifically likes about each reference (palette, typography, composition, shape language, material, overall aesthetic); if they give no explanation, use the overall character as inspiration without copying distinctive elements.

### Step 1: palette options

For every interactive new-identity flow that needs a logo, start here and complete this review before Step 2. Phrases such as "pastel", "blue", or "warm neutrals" are preferences used to build the options, not a selected palette. Skip this review only when the user supplied an authoritative palette or explicitly selected exact colors, or asked you to choose for them (then build one exact palette from the brief and record it before Step 2).

Create 2-3 considered palette options. Each includes: named flat colors with exact hex values; background and text colors; optional gradients only when relevant; a one-sentence rationale; small usage examples; 2-3 rough logo mechanism seeds (for a palette-only request, none). Do not display a typography specimen, placeholder font pairing, or wordmark on the palette board.

After showing: "Take your time reviewing the palettes. Reply with the option you prefer and any colors you want changed, added, or removed." Wait for the user's ordinary next message.

### Step 2: logo mark options

Enter only after Step 1 produced a user-selected palette (or an authoritative/explicitly selected palette was already available).

Using the selected draft palette plus the rules above:
1. Return exactly three original logo mechanisms.
2. Apply the enhancer grammar once per mechanism to produce its prompt.
3. Generate the three prompts as three separate requests with identical parameters, using the one, two, or three logo colors the concept needs; never pad to three; exceed three only when the user explicitly requested more.
4. Show all three together. This review is mandatory in every mode.

When interaction is allowed, ask the user to review and comment. Do not self-select or start typography before the user responds. In auto mode (the user asked you to choose), choose the strongest candidate and continue only the requested deliverables.

A logo-only request is complete once the user picks a logo; typography is not mandatory.

### Step 3: typography options

Using the selected draft palette and selected mark:
- Propose 2-3 suitable font pairs.
- Use user-supplied licensed fonts when given; otherwise use verified Google Fonts with official download links.
- Render the real brand name and short sample copy.
- Show the selected mark next to each wordmark treatment so type/mark cohesion is visible.
- Use one contrasting text color for both display and body samples; it must not equal the background color.

Ask for feedback in a normal message and wait.

### Optional combined board

Render a combined board (logo + palette + type) only when all three slots are approved and the user requested a full identity/brand kit or asks to see them together. It is a presentation view (a Figma frame), not another approval gate. Do not ask the user to approve the system again.

### Continue the original request

Once the slots required by the first-message deliverables are approved, load the output modules and continue. Never force missing unrelated slots or ask the user to choose scope again.
