# Channel styles — defaults, alternates, the long-form set and the card map

Read this when you need the DEFAULT look for a channel (the Round-2 gallery came back
empty, or a brief named no style), when the user asks what else is available, when the run
is long-form, or when you must map a card TITLE to the pinned style FILE that carries its
formula. A resolved pick from Round 2 outranks every default here (CROSS-CHANNEL PRESET
RULE): apply the picked look, keep the channel's mechanics.

  - **Per-type DEFAULTS + long-form:** when nothing is picked (hands-off, briefs):
    Explainer → **Editorial Motion Graphics** (Stickman Cartoon = the second house
    direction); History → **Editorial Motion Graphics** (named alternates **Paper
    Diorama**, **Mannequin** — `references/style-mannequin.md`, clay-render
    reenactment figures); Kids → **Studio 3D** (then Pastel Flat 2D / Colorful 3D /
    Hand-drawn Ink / Poster Vector — `references/kids-styles.md`; Fluffy Toy is a
    legacy card in the same catalog); **STILL PICTURES mode with no pick → Flat 2D
    Papercraft** (then Stickman / Hand-drawn Ink — one-liners verbatim from
    `references/picture-flow.md`; adjacent asks map to the closest and confirm in one
    line), overriding the channel default because that is the look the stills pipeline
    is tuned for; Fairy Tale & Myth → **Cinematic Storybook** (the only style;
    `references/style-cinematic-storybook.md`, canon-refs → unique seedream key like
    the Kids flow). **LONG-FORM AUTO-LOCK: if the request already says ≥10 minutes and/or
    "documentary", the LONG-FORM direction is LOCKED from the prompt** — never
    offered as an option (offering what the user already chose is a re-ask). A locked
    long-form run: duration options become 10/15/20 min (+ Other) if not already
    stated; the style round offers the LONG-FORM set — **Watercolor Chronicle
    (recommended, first)** / Paper Diorama / Editorial Motion Graphics / Upload —
    with descriptions VERBATIM from the style files (`history-longform.md` carries
    Watercolor's one-liner); and the mandatory time/cost warning + ERA-MAP flow from
    `references/history-longform.md` apply.
  - **ONE catalog — "Faceless channel presets"** (backend consolidation 2026-07-27: the
    channel cards were moved into the explainer catalog and it was renamed): **25 rows,
    21 live + 4 archived**, house and legacy cards side by side, mapped id→title by the
    Round-2 table. There is no separate faceless catalog and no separate resolver any more.
    - **The 11 house cards, mapped to their style files** (CMS title on the left —
      titles differ slightly from the file names, so fuzzy-map, same rules as
      user-typed names): Editorial Motion Graphics · Stickman Cartoon (generic §0
      formula) · Paper Diorama · Mannequin · Watercolor Chronicle · Studio 3D · Pastel
      Flat 2D · Colorful 3D · **Hand Drawn** = Hand-drawn Ink · Poster Vector ·
      **Fairy Tale & Myth** = the Cinematic Storybook look
      (`references/style-cinematic-storybook.md`). **"Frame by frame" is ARCHIVED** — the
      stills format moved to the Round-1b MOTION MODE question, so never offer that card
      and never present stills as a "style"; an inherited id for it reads as mode = Still
      pictures + Flat 2D Papercraft.
      **This mapping is also what Phase 1 RULE 0 uses:** every one of these titles
      resolves to its `images[]` in the house CMS view (and to a `media_id` where the
      resolver exists), and those images MUST be attached to the style-key call —
      including on hands-off runs where the style came from a channel default rather than
      a card pick.
    - **ONE card is still a DIRECTION card.** "Fairy Tale & Myth" locks
      channel type = Fairy Tale & Myth (on-twos `--stepped 12` + mysterious-calm bed) —
      and it obeys the MOTION MODE like every other style: picked with Still pictures it
      becomes a narrated storybook in the Cinematic Storybook look.
    - **The 10 legacy explainer cards live in the same catalog** (Fluffy Toy, 3D
      Papercraft, Mixed Media, Whiteboard Doodle, Pixel Art, Claymotion, Low Poly,
      Isometric Flat Vector, 3D Mix, 2D Illustrator). They are valid on any channel
      (CROSS-CHANNEL PRESET RULE) but have NO pinned style file and no published
      `images[]`: anchor on the card's cover (or a resolver `media_id` where that exists)
      and write the locked formula from the card art's visible traits.
    - Where a card DOES have a style file, that file wins: the pinned FORMULA +
      canonical static.higgsfield.ai refs ARE the preset (self-sufficient — a
      `media_id` is optional extra anchoring). Kids styles always keep the
      canonical-refs → unique seedream key flow; the FORMULA goes byte-identical into
      every prompt regardless of anchor source.
  - **CROSS-CHANNEL PRESET RULE — any catalog preset is valid on ANY channel type.**
    A preset named on input (user message, brief `preset`, or a card pick) is the
    LOCKED style for the run even when it is not among that channel's defaults —
    History in Colorful 3D, Kids in Editorial, Explainer in Watercolor Chronicle are
    all legal. Never re-ask, never "correct" the choice, never silently substitute the
    channel's default. **A style brings ONLY its look, never its home channel's
    mechanics:** the style file contributes the FORMULA, canonical refs / anchor
    mechanism (Kids styles keep their unique-key flow anywhere), palette lock,
    {MOTION} + negatives, and style-inherent laws (e.g. Mannequin's cast/identity
    rules). Everything narrative stays with the CHOSEN channel type: cut pattern
    (Kids' 4-cut belongs to the Kids CHANNEL — a History run in Studio 3D cuts the
    standard 5), narrator↔character interplay, beat grammar, documentary skeleton,
    script rules. **Kids-catalog styles carry ONE style-inherent extra: the default
    wordless music bed** (`references/kids-styles.md §Kids music bed`) — a history or
    explainer run in a Kids look still gets the bed, with the MOOD matched to the
    channel's tone (playful-light for the look, not babyish). **"Fairy Tale & Myth"
    (Cinematic Storybook) carries TWO style-inherent extras anywhere it is used: the
    on-twos cadence (`--stepped 12`) and a mysterious-calm music bed**
    (`references/style-cinematic-storybook.md`).
    **Stills are no longer a style exception:** whether a run is animated or stills comes
    from the Round-1b MOTION MODE, so every preset here is legal in BOTH modes and no
    card can flip the format on its own.
    Watercolor Chronicle outside long-form is just the watercolor look — no
    long-form skeleton, no ERA MAP unless the run is long-form.
  - **Pick another preset** → if the user has ALREADY NAMED a preset (in their message
    or by choosing a named option), resolve it BY NAME against the Round-2 table (and the
    CMS views for its art): exact match, else FUZZY match (case/word-order/partial —
    "fluffy toy" hits "Fluffy Toy", "3d paper" hits "3D Papercraft"), confirm in one line.
    If nothing plausibly matches, offer the 1–2 closest names in the SAME breath and only
    then fall back to the gallery — never jump straight to it over a typo (asking twice for
    the same choice is a bug). Browsing = the Round-2 gallery, which serves the same single
    catalog the resolver does. (Never enumerate presets as a plain text
    question.)
  - **Upload ≤3 style images** → collect them with `media_upload_widget` (style donors
    only; local files reach this server no other way), then pass the returned media ids as
    `image_references`.
