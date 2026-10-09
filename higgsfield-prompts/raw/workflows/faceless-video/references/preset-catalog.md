# The faceless channel preset catalog, offline

**You normally never need this file.** Round 2 calls `get_explainer_presets` and
`resolve_explainer_preset`, and the resolver returns the card's `name` together with
its style image — that closes the round. Open this file ONLY when:

- a brief or an old picker handed you a bare `preset_id` and no resolver is available, or
- the resolver errored twice and you must map the id yourself, or
- you need to know which pinned style FILE a card's title belongs to.

Ids are verified live against the CMS on 2026-07-29: 25 rows, 21 live + 4 archived.

    CMS catalog itself, so a pick maps with no network at all. **"I cannot map the preset
    id, so I will use the default style" is a BUG**: silently swapping the user's Hand
    Drawn pick for the channel default is exactly the failure this rule exists to stop.
    An id outside this table means the catalog gained a row — fetch the two views, and
    only if that also fails say in one line that the card could not be identified and ask
    ONCE, as named options from the table, never as a raw uuid.

    **HOUSE cards** — each has a pinned style file in `references/`, and `images[]` in the
    house view are its real style donors:
    - Editorial Motion Graphics — `56fc6472-33b7-45dc-83ff-80c71d40aec6`
    - Stickman Cartoon — `237dd06c-3729-4895-9672-1c623c4266e0`
    - Watercolor Chronicle — `0029f935-be9e-46c7-a5d8-a4e0f81d49c8`
    - Fairy Tale & Myth — `de5b38ca-9134-4987-9d7a-d5e9085f0480`
    - Paper Diorama — `83d276f6-e3aa-49b8-82f2-1a0bb7d0a370`
    - Pastel Flat 2D — `d0708b4f-a134-40f7-9884-9ad830904e71`
    - Colorful 3D — `30948d66-76b1-4c8e-884a-1854e08e91df`
    - Hand Drawn (= Hand-drawn Ink) — `402635b8-7363-4172-ac78-7ffa9b999c94`
    - Poster Vector — `8014a730-3092-4f3a-b880-0321ae1d207d`
    - Mannequin — `32356614-40f8-42b2-8a57-2f7b30cfb473`
    - Studio 3D — `ab43dacd-6bee-4f8e-98b7-c4ff678bfdbd`

    **LEGACY explainer cards — same catalog, same rules, no pinned style file.** An id from
    here is a valid pick, not a mystery:
    - Whiteboard Doodle — `b347d852-98fc-4013-92b7-6b0219fb21be`
    - 3D Papercraft — `bb90786e-fa06-4911-884b-c576dcd20bef`
    - Mixed Media — `80e4dd7b-cd65-42d4-b191-b58d62558602`
    - Low Poly — `3e4bfd81-fbd8-4587-886d-296cbe48d152`
    - 2D Illustrator — `5a1ae304-c541-4f11-9784-595e0f2c3d2b`
    - Pixel Art — `730d436b-c0d2-4346-a7e9-3d9a80065f30`
    - Claymotion — `1de0f39e-c602-4b00-b54a-38440c7f63f7`
    - Isometric Flat Vector — `c109eddb-1a79-478a-afd5-273bd0b205e5`
    - 3D Mix — `daa250fe-c353-4d26-8ab2-fc1c4ec777a4`
    - Fluffy Toy — `1fde6c92-721b-4824-b490-4ea75ad0665f`
    For any of these the look anchor is the card's COVER (or the resolver's `media_id`
    where that tool exists) and the FORMULA is written from the card art's visible traits —
    there is no style file to quote, exactly as the CROSS-CHANNEL PRESET RULE says.

    **ARCHIVED — 4 rows flagged `is_hidden`. They cannot be picked and must never be
    offered:** Frame by frame `bc3c6f53-762e-4806-84f0-37a85e278835` (replaced by the
    stills MODE of Round 1b), Dynamic Motion Design `de3bd354-69d3-4311-8f4e-6cd1e945bbc1`,
    Vintage Documentary `23df630a-c4f4-4f2f-b774-6ae1cd972614`, Custom Template
    `4edac834-6ec0-4b0a-9bfc-d2cafbe0c8f6`. The listing does not filter them yet — ignore those rows. Never name one as a default or an
    alternate. If such an id somehow arrives, say so in one line and take the channel
    default.
  Skip the gallery when the style is already
  decided: a style/preset NAMED in the prompt resolves by name (below), uploaded
  style images (≤3) take the custom path, and a long-form-locked run offers its own
  LONG-FORM style set instead (below). HOW a style was picked never changes its
  mechanics: house styles have no preset id and generate the key from their pinned
  FORMULA (stickman uses the generic webcomic formula in `references/prompts.md §0`);
  Kids styles pin 2–3 canonical ref images (kids-styles.md: `media_import_url` each →
  ALL media_ids as `image_references` into ONE `seedream_v5_pro` style-key call with
  the FORMULA — the user gets their OWN unique key, look-locked to the canon; refs
  are style donors only, never frames).
