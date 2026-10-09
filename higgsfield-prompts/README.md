# Higgsfield – reverse engineering promptów z MCP (etap 1: inwentaryzacja)

Zrzut **wszystkich instrukcji / promptów / przepisów**, które serwer Higgsfield MCP podaje modelowi,
kiedy korzystasz z niego z Claude. Każdy tekst jest zapisany **verbatim** (bez skracania) w `raw/`,
a ten plik jest mapą: co jest czym, do czego służy i gdzie leży.

Data zrzutu: 2026-10-09. Źródła:

| Źródło | Jak pobrane | Co daje |
|---|---|---|
| Higgsfield MCP (`mcp.higgsfield.ai`) | `get_workflow_instructions`, `get_workflow_bundle_file`, `get_preset_instructions`, `get_presets`, `get_explainer_presets`, `ai_influencer_list_presets`, `shorts_studio_list_presets`, `models_explore`, `apps_search` | właściwe prompty systemowe (SKILL.md), przepisy presetów, master prompty Katany, katalogi |
| GitHub `higgsfield-ai/skills` (oficjalne, MIT, v0.13.0) | `git clone` | 8 skilli do CLI `higgsfield`, w dużej części te same teksty co workflowy MCP + `prompt-engineering.md`, `model-catalog.md` |
| GitHub `OSideMedia/higgsfield-ai-prompt-skill` (społeczność, MIT, v3.40) | `git clone`, okrojone | 36 sub-skilli promptowych pisanych przez twórców zewnętrznych, nie przez Higgsfield |

Strona `higgsfield.ai` (Katana / Genjutsu / docs) jest **zablokowana przez politykę sieciową tego kontenera** (403 na proxy),
więc galerie wziąłem wprost z MCP. MCP zwraca dokładnie to, co widać na stronie (te same slugi i tytuły), plus pełny tekst instrukcji, którego strona nie pokazuje.

---

## Mapa folderów

```
higgsfield-prompts/
├── README.md                  ← ten plik (indeks + grupy)
├── INVENTORY.md               ← auto‑generowana lista wszystkich plików z rozmiarami
└── raw/
    ├── workflows/             ← A. 13 workflowów MCP (SKILL.md + references/ + scripts/)
    ├── presets/               ← B. 63 przepisy produktowe (/hero-shot, /crane-reveal …)
    ├── katana/                ← C. 28 presetów Katana (pełne master prompty autorów)
    ├── katana-refs/           ← I. 20 map montażowych wideo referencyjnych Katany (analiza klatka po klatce)
    ├── katana-kits/           ← I. 8 kitów CDN Katany (skrypty/szablony/timeline'y, bez binariów)
    ├── commands/              ← D/E. komendy: /genjutsu, /katana, /3d-jutsu, /use-after-effects, /use-blender, galerie
    ├── catalogs/              ← F. katalogi (Genjutsu, Katana, Viral, Marketing Studio, Explainer, AI Influencer, modele, apps)
    ├── github-skills/         ← G. oficjalne repo skilli Higgsfield (kopia 1:1 bez binariów)
    └── community-osidemedia/  ← H. annex: skille społeczności (third‑party)
```

---

## A. Workflowy MCP (13) – „duże” prompty systemowe

To są główne SKILL.md, które MCP ładuje, kiedy prosisz o konkretny typ produkcji. Każdy ma frontmatter
(`name`, `version`, `description` = reguła triggerowania), potem procedurę krok po kroku, hard rules,
listę narzędzi i delivery. Większość ma dodatkowo `references/*.md` (sub‑prompty, słowniki, szablony)
i `scripts/` (Python/bash/JS do montażu, walidacji, renderu).

| Workflow | Wersja | Do czego | Najcenniejsze pliki do „uniwersalizacji” |
|---|---|---|---|
| `ad-multiplier` | 1.5 | 1→N wersji gotowej reklamy wideo (4–30 s): podmiana ludzi/produktów/tła z zachowaniem montażu; tryb Recreate = przestrzelenie reklamy na inny rynek/język/cast | `references/prompt-writer.md` (jak pisać prompt edycji wideo), `references/recreate.md` |
| `ads-studio` | 1.2 | statyczne kreacje reklamowe (Meta/IG) z copy i obrazem: z URL marki, z produktu, z promptu | sam SKILL.md (intake marki → brand kit → produkt → generacja → QA) |
| `brand-asset-creation` | 1.1 | logo, identyfikacja, brand kit, mockupy, merch, packaging, signage, brandbook, social, plakaty, deck | 23 references: `logo.md`, `logo-prompt-enhancer.md`, `palette.md`, `typography.md`, `mockups.md`, `brandkit-design-brain.md`, `qa-and-iteration.md` |
| `character-sheet` | 1.0 | character sheet / model sheet / turnaround; „slot‑based prompt architecture” + silnik „anti‑AI / unretouched realism”; 5 stylów | SKILL.md zawiera gotową architekturę promptu obrazkowego (sloty) – bardzo przenośne |
| `faceless-video` | 2.4 | kompletne wideo narratorskie (faceless YT): 5 typów – Explainer, History, Kids, Picture Story, Fairy Tale; lock stylu, jeden głos, napisy | `references/scriptwriter.md`, `prompts.md`, `channel-styles.md`, `kids-styles.md`, `style-*.md`, `vo_and_captions.md`, `topic-sourcing.md`; 14 skryptów montażowych |
| `katana` | – | montaż z referencji: edycja źródła wg briefu, remiks referencyjnego edita na nowy subject, lub wierna rekonstrukcja 1:1 | `references/analysis.md`, `compositing.md`, `generation.md`, `creative-quality.md`, `qa-delivery.md`; `scripts/comp/engine.js` (silnik kompozycji), `analyze_ref.py`, `assemble.py` |
| `narration` | 1.1 | lektor dopasowany do okien czasowych, długa narracja w zablokowanym głosie, „wstaw mnie jako narratora” (presenter mode) | `references/presenter-mode.md`, `scripts/speech_metrics.sh` |
| `product-photoshoot` | 1.0 | packshoty, lifestyle, product‑with‑person, Pinterest pin, hero banner, carousel, ad pack, virtual try‑on, conceptual, restyle | 15 references, w tym **`photography-vocabulary.md`, `photographer-references.md`, `negative-prompts.md`, `refinement-pass.md`** – gotowy słownik fotograficzny do dowolnego generatora |
| `thumbnail-generation` | 1.3 | miniatury YT/IG: 16 frameworków koncepcyjnych, casting 11 emocji, rig oświetleniowy, identity lock, tekst | **`references/thumbnail-frameworks.md`** (16 frameworków), `text-overlay-bake.md`, `scripts/bake_text_overlay.mjs` |
| `ugc-video` | – | gotowe UGC: review twórcy, product‑only VO, unboxing, try‑on, tutorial, website tour | SKILL.md + references (formaty UGC, skrypt, hooki) |
| `video-editing` | 1.0 | Higgsedit: cięcia, trimy, ścieżka dźwiękowa, layouty, animowany tekst, shadery, title cards | `references/animation-contract.md`, `caption-systems.md`, `assembly.md` + reszta |
| `video-montage` | – | sklejanie klipów, soundtrack, wypalanie/stylizacja napisów; cały pipeline transkrypcja→alignment→burn | `references/` + `scripts/` (ffmpeg, whisper‑alignment) |
| `website-builder-flow` | 2026‑07‑25 | strony / web‑app / gry przeglądarkowe na infrastrukturze Higgsfield; 3 typy: game / website / app | 53 pliki: `design-recipe.md`, `design-taste-frontend.md`, `wow-catalog.md`, `review-rubric.md`, `image-to-code.md`, `game-*.md`, `scroll-scrub*.md` |

Uwaga: ten sam workflow bywa w dwóch miejscach: MCP (`raw/workflows/`) i GitHub (`raw/github-skills/`).
Pary: `brand-asset-creation` ≈ `higgsfield-brandkit`, `website-builder-flow` ≈ `higgsfield-websites`,
`product-photoshoot` ≈ `higgsfield-product-photoshoot`, `thumbnail-generation` ≈ `higgsfield-youtube-thumbnail`,
`faceless-video` ≈ `higgsfield-video-explainer`. Wersje GitHub są pisane pod CLI (`higgsfield …`), wersje MCP pod narzędzia `generate_*`.

---

## B. Przepisy produktowe (63) – `raw/presets/<id>.md`

Krótkie, jednoplikowe „recipes” wywoływane slashem (`/hero-shot`, `/crane-reveal`, …). Każdy ma identyczną
strukturę, która sama w sobie jest świetnym szablonem skilla:

1. **Visible effect** – jedno zdanie, co widać.
2. **Preserve** – co ma zostać nienaruszone (kształt produktu, logo, etykiety).
3. Procedura pobrania referencji (upload / media ID / URL).
4. **Generation parameters** (JSON: model, aspect ratio, rozdzielczość, jakość, wariant).
5. **Master prompt** – pełny prompt generacyjny (to jest to, co chcesz uniwersalizować).
6. Reguły wykonania (bez planowania, bez pytań, bez ujawniania master promptu).

Wideo‑przepisy (`crane-reveal`, `product-spin`, …) mają dwa master prompty: **preprocessing** (klatka startowa
w `nano_banana_pro`) i **video** (ruch kamery).

| Typ | Id |
|---|---|
| **image – hero / studio** | hero-shot, luxury, minimalist-white, pedestal-shot, power-angle, symmetry, signature-frame, color-pop, fabric-wave, ice-capsule, powder-cloud, water-splash, paint-wave* |
| **image – kontekst / lifestyle** | in-hand, on-desk, kitchen-scene, gym-bag, travel-pack, weekend-carry, shelf-ready, retail-stack, flatlay, unboxing, inside-pack, bundle, angles, moodboard |
| **image – edukacyjne / social karty** | benefits, main-benefit, three-reasons, before-after, how-it-works, feature-zoom, specs, whats-inside, care-guide, usage-guide, quick-steps, product-match, myth-fact, saveable-tip, share-card, swipe-opener, vertical-hook, reel-cover, new-drop |
| **video – ruch kamery** | crane-reveal, push-in, pull-back, whip-pan, half-turn, product-spin, floating-roll, macro-glide, texture-track, label-trace, detail-scan, topdown-dive |
| **video – efekt / światło** | light-sweep, sunrise-pass, shadow-motion, liquid-wrap, impact, paint-wave* |

(*paint-wave jest w katalogu jako video.) Pełna lista z opisami: `raw/catalogs/recipes-catalog.json`.

---

## C. Katana (28 presetów) – `raw/katana/<slug>.md`

To „nowy element do montowania filmików z Claude”. Presety występują w dwóch odmianach:

**1. Z pełnym master promptem autora** (`grunge-aura`, `the-boys`, `kawaii-pop` i inne duże pliki, 20–46 KB):

- stała część wspólna (kontrakt wykonania: inputs `MEDIA:`/`INPUTS:`, formularz, delivery przez `show_katana_result`),
- **Inputs** (schemat formularza),
- **Original author master prompt**: CLAUDE EXECUTION CONTRACT → INPUT CONTRACT → FIXED REFERENCE (link do oryginalnego reela + autor) → PRESET LOCK (rozdzielczość, fps, liczba klatek) → VISUAL LANGUAGE → SUBJECT ADAPTATION → NUMERICAL COMPOSITING RECIPE → TITLE CHOREOGRAPHY → **EMBEDDED EDIT MAP** (mapa montażu klatka po klatce) → AUDIO → EXECUTION → DELIVERY,
- **Preset data** (JSON: input_schema, reference_media).

To są najbardziej „inżynierskie” prompty w całym zbiorze – dokładny przepis, jak Claude ma zmontować wideo w Pythonie/ffmpeg.

**2. „Reference remake”** (większość community, ~7 KB): ten sam kontrakt wykonania + link do wideo referencyjnego (600×450) + formularz
(zwykle `media.images` 1–5, czasem pole „Wishes”) + ogólne reguły Katany. Tu „prompt” to samo wideo: Claude ma je przeanalizować
workflowem `raw/workflows/katana/` i odtworzyć z subjectem użytkownika. Rozmiar pliku mówi, który to rodzaj (patrz `INVENTORY.md`).

Presety z pełnym promptem (rozmiar 32–46 KB): `grunge-aura`, `the-boys`, `kawaii-pop` (+`.part-2`), `let-me-show-you` (+`.part-2`),
`last-katana`, `pink-collage`, `launch-cut` (+`.part-2`), `lights-out`, `living-lab`, `many-lies`, `physical-body`, `travel-edit`.
Serwer dzieli najdłuższe na części (`/katana/<slug>/part-2-<hash>`); zapisane jako `<slug>.part-2.md`. `chrome-orbit` to jednozdaniowy
opis ruchu kamery + wideo referencyjne. Kilka z nich to w praktyce **osobne produkty z własnym kitem** (skrypt renderujący na CDN
Higgsfield, sha256, fonty): `launch-cut` (30‑sekundowa reklama produktu z klonem UI), `lights-out` (17 s kinetic typography),
`living-lab` (30 s launch film), `many-lies` i `physical-body` (strobe/overlay edity z jednego klipu, zero kredytów), `travel-edit` (28 s mood edit).

| Kategoria | Slugi |
|---|---|
| **aura_farming** (20) | dreamy-streetwear, power-suit, outfit-check, tiger-eyes, frame-dance, tokyo-bloom, star, blue-eyes, dark-and-moody, painting-flow, dark-aura, nocturne, car-edit, xerox-3, xerox-2, the-boys, kawaii-pop, let-me-show-you, last-katana, pink-collage |
| **motion** (4) | launch-cut, lights-out, living-lab, chrome-orbit |
| **clipping** (3) | travel-edit, many-lies, physical-body |
| **higgsfield (oficjalny)** (1) | grunge-aura |

Ogólna komenda `/katana` bez presetu: `raw/commands/katana.md`. Workflow nadrzędny: `raw/workflows/katana/`.

---

## D. Genjutsu – `raw/commands/genjutsu.md` + `raw/catalogs/genjutsu*.json`

`/genjutsu` to instrukcja routingu: przeglądanie galerii, animacja AI Influencera, motion transfer
(`hf_mult_motion_control`) albo podmiana subjectu (`hf_mult_replace_object`). Galerie zawierają
**tylko nazwy + wideo napędowe + jeden szablonowy opis** (nie ma per‑preset promptu tekstowego):

- `genjutsu.json` – 34 presety „Higgsfield” (np. Countryside Duo, Umbrella Transformation, Infinite Zoom, Parkour Flow),
- `genjutsu-trending.json` – 50 trending (Urban Style Rotation, Night Fuel Drive, …),
- `genjutsu-new.json` – 50 nowych (Tunnel Portrait Swap, Samurai Night Walk, …).

---

## E. Komendy setupowe i galeryjne – `raw/commands/`

| Komenda | Plik | Treść |
|---|---|---|
| `/3d-jutsu` | `3d-jutsu.md` + `3d-jutsu__references__location-new-angles.md` | hostowany Blender (`bpy` przez `scene_builder_3d_*`); nowe ujęcia tej samej lokacji |
| `/use-after-effects` | `use-after-effects.md` + `__references__installation.md`, `__references__verification.md` | instalacja i weryfikacja lokalnego MCP do After Effects |
| `/use-blender` | `use-blender.md` + references | lokalny Blender MCP (bez add‑onu) |
| `/katana` | `katana.md` | ogólna Katana bez presetu |
| `/genjutsu` | `genjutsu.md` | patrz D |
| `/effects`, `/product`, `/motion`, `/marketing-studio` | `effects.md`, `product.md`, `motion.md`, `marketing-studio.md` | jednolinijkowe komendy otwierające galerie (`get_presets`) |

Tokeny `/ugc-video`, `/faceless-video`, `/ad-multiplier`, `/explainer`, `/thumbnail`, `/character-sheet`, `/narration`,
`/website`, `/brand`, `/soul` **nie mają własnych instrukcji** – serwer zwraca `not_found` i odsyła do workflowów (A). Zapis w `commands/_FAILED.txt`.

---

## F. Katalogi bez pełnych promptów – `raw/catalogs/`

| Plik | Co | Prompt? |
|---|---|---|
| `recipes-catalog.json` | 63 przepisy z B (id, tytuł, opis, typ) | tak → B |
| `katana-catalog.json` | 28 slugów Katany wg kategorii | tak → C |
| `genjutsu*.json` | 134 presety Genjutsu | tylko szablon |
| `viral.json` | **87 efektów Viral** (`/effects`), każdy z 1–2 zdaniowym opisem efektu („Vanish: ciało znika, ubranie opada…”) | opisy = dobre seedy |
| `marketing-studio-product-shot.txt` | 418 szablonów product‑shot (nazwy + typ) | nie |
| `marketing-studio-motion.txt` | 231 szablonów motion (2d_motion / saas_motion / hypermotion / mixed_media) | nie |
| `explainer-presets.json` | 22 style explainera (Editorial Motion Graphics, Stickman, Watercolor, Claymotion, Pixel Art, …) | szablon |
| `ai-influencer-presets.json` | **39 presetów AI Influencer z pełnymi briefami** („Fashion‑editorial freak casting photo… two‑panel sheet… PURE WHITE seamless…”) + selekcja cech + seed | **tak** – gotowe prompty portretowe |
| `shorts-studio-presets.json` | 16 stylów Shorts Studio (nazwy) | nie |
| `models.json` | 127 modeli z parametrami, aspect ratio, tagami | metadane |
| `apps.json` | 1 app marketplace („Match Cut + Tracelab”, 28 akcji) | metadane |

---

## G. Oficjalne skille GitHub – `raw/github-skills/`

Repo `higgsfield-ai/skills` v0.13.0 (MIT). 8 skilli pod CLI `higgsfield`:

| Skill | Co nowego względem MCP |
|---|---|
| `higgsfield-generate` | **`references/prompt-engineering.md`** (ogólne zasady promptowania obrazu/wideo), `model-catalog.md`, `workflows.md`, `marketing-*.md` (Marketing Studio: avatary, brand kits, DTC ads, hooki) |
| `higgsfield-soul-id` | trening postaci Soul (`photo-guide.md` – jak dobrać zdjęcia referencyjne) |
| `higgsfield-product-photoshoot` | 10 trybów, enhancer promptów |
| `higgsfield-brandkit` | = `brand-asset-creation` (+ `prerequisites.md`) |
| `higgsfield-marketplace-cards` | karty produktowe Amazon‑style (main image, secondary, A+) |
| `higgsfield-websites` | = `website-builder-flow` |
| `higgsfield-video-explainer` | = podzbiór `faceless-video` (`references/prompts.md`) |
| `higgsfield-youtube-thumbnail` | = `thumbnail-generation` |

Dodatkowo `COOKBOOK.md`, `evals/scenarios.md` (scenariusze testowe) i `CLAUDE.md` repo.

---

## H. Annex: skille społeczności (OSideMedia) – `raw/community-osidemedia/`

Nie są to prompty Higgsfield, tylko zewnętrzny pakiet (MIT) zbudowany nad ich MCP/CLI. Warte uwagi przy etapie 2:
`skills/higgsfield-prompt`, `higgsfield-cinema`, `higgsfield-camera`, `higgsfield-shotlist-director`,
`higgsfield-seedance*`, `higgsfield-character-design`, `rules/prompt-formula.md`, `rules/cinematic-vocab.md`,
`templates/*` (10 gatunkowych szablonów promptów wideo + text‑overlays + character‑design).

---

## I. Katana – mapy montażowe referencji (20) i kity CDN (8) – `raw/katana-refs/`, `raw/katana-kits/`

Pogłębienie grupy C. Większość presetów Katany to „reference remake” – prompt jest w wideo, nie w tekście. Żeby się do tego dobrać,
w sandboxie Higgsfield (`sandbox_exec`) pobrano wszystkie 20 wideo referencyjnych z `static-public-media.higgsfield.ai/katana-presets`
i przepuszczono je przez oficjalny analizator workflowu Katany (`$HF_WORKFLOWS/katana/scripts/analyze_ref.py --review-size`), czyli ten sam
krok, który Claude wykonuje przy montażu. Wynikowy `analysis.json` skompresowano do czytelnej mapy montażowej (`_tools/summ2.py`).

**`raw/katana-refs/<slug>.md`** (20 plików) – dla każdej referencji: totals (liczba cięć, flashe, solidy, inwersje, wzorce kadencji),
global look (bw / luma / kontrast / saturacja / dominujący hue / letterbox), a potem **lista cięć** (klatki, czas, długość, rodzaj,
kadencja, wektor ruchu, look, flashe/inwersje/tekst), osobno flashe, solidy, inwersje, strefy aktywności i „maybe-cuts”.
To są propozycje detektora, nie potwierdzone cięcia – ale razem z master promptem z `raw/katana/` dają kompletny brief montażowy,
który da się odtworzyć w Premiere/AE bez Higgsfield. Slugi: blue-eyes, car-edit, chrome-orbit, dark-and-moody, dark-aura,
dreamy-streetwear, frame-dance, grunge-aura, kawaii-pop, last-katana, many-lies, nocturne, outfit-check, painting-flow, power-suit,
star, tiger-eyes, tokyo-bloom, xerox-2, xerox-3.

**`raw/katana-kits/<slug>/`** (8 kitów, 79 plików tekstowych, wszystkie zweryfikowane sha256) – presety, które wymagają kitu z CDN
(`d2ol7oe51mr4n9.cloudfront.net`, URL + sha256 przypięte w master promptach). Pobrano i rozpakowano w sandboxie; do repo trafiły
wszystkie pliki tekstowe (kod, szablony, timeline'y, licencje), **bez binariów** (modele `.onnx`, fonty `.ttf/.woff2`, muzyka, obrazy):

| Kit | Co zawiera |
|---|---|
| `lights-out` | `render_template.py` (27 KB, 17 s kinetic typography, silhouette przez u2netp), `SHA256SUMS`, licencje OFL fontów |
| `travel-edit` | `edit28.py` (28 s mood edit), licencje OFL (Montserrat, Pinyon Script) |
| `living-lab` | silnik kompozycji w JS (`comp/engine.js`, `living_lab.js`, `deco.js`, `film.js`), `audio/score.html`, narzędzia Playwright (`tools/cap.js`, `render.sh`, `review.sh`, `keysheet.sh`, `music_window.py`) |
| `many-lies` | `KIT.json`, `assets.json`, silnik HTML/JS (`engine/fx.js`, `ana.html`), `scripts/{ana,edit,ml,serve}.py`, `template/timeline.json`, `reference/{template,fixes}.md` |
| `physical-body` | ta sama architektura co many-lies + `track.py` (śledzenie twarzy, YuNet/SFace) i `sandbox.sh` |
| `let-me-show-you` | `aura_kit/aura.py` (36 KB), `compose.py`, `plan_template.json`, `clean_specs/{B,G,H}.json` |
| `the-boys` | `build.py`, `timeline.json`, `LICENSES.txt` |
| `pink-collage` | pakiet `glow/` (engine, media, seg, y2k), `scripts/{analyze,cast,edit,pc,qa}.py`, `template/template.json`, `assets.json`, `requirements.txt` |

`_tools/job.sh` = skrypt, który to wszystko pobrał (pełne URL‑e kitów i referencji + sha256), `_tools/summ2.py` = kompresor map,
`kits_listing.txt` = pełna lista plików kitów z rozmiarami (razem z pominiętymi binariami). `launch-cut` nie ma kitu na CDN – cała
procedura (narzędzie `higgsedit`, timeline, stems) jest inline w `raw/katana/launch-cut*.md`.

---

## Jak zweryfikowano wierność kopii

Każdy plik w `raw/workflows`, `raw/presets`, `raw/katana` i `raw/commands` został **wyciągnięty programowo** z surowych
wyników narzędzi MCP (transkrypty sesji + wyniki zapisane przez harness na dysku) i porównany bajt w bajt z tym, co zapisali
agenci; różnice nadpisano dokładną kopią. Pliki w `raw/katana-kits` i `raw/katana-refs` przeszły z sandboxu Higgsfield przez
transkrypt sesji w porcjach ≤15 KB z nagłówkiem `sha256 + rozmiar`; po złożeniu każdy z 79 plików kitów zgadza się z sumą sha256
policzoną w sandboxie (0 błędów, 0 niekompletnych). Pliki bundle mają zgodność z `size_bytes` raportowanym przez serwer. Dwie wersje
SKILL.md: `SKILL.md` = to, co serwuje `get_workflow_instructions` (z doklejoną sekcją o unlimited generations i meta),
`SKILL.bundle.md` = surowy plik z bundle, zapisany tylko tam, gdzie się różni (`ugc-video`, `video-editing`, `video-montage`, `website-builder-flow`).
`_META.json` / `_MANIFEST.txt` obok SKILL.md = metadane odpowiedzi (wersja, lista plików).

## Co się NIE udało / ograniczenia

- Strona `higgsfield.ai` niedostępna z kontenera (policy sieci). Galerie wzięte z MCP; brak wglądu w ewentualne opisy marketingowe ze strony.
- Marketing Studio (418 + 231) i Shorts Studio: serwer nie zwraca tekstu promptu, tylko nazwy/typ/podgląd. Prompty są po stronie backendu.
- Genjutsu trending/new: pobrana pierwsza strona (50) każdej listy.
- Kity Katany: binaria (modele ONNX 4–180 MB, fonty, muzyka, obrazy) nie zostały przeniesione – `media_upload` i transfer base64
  z sandboxu blokuje klasyfikator uprawnień, a CDN Higgsfield jest poza policy sieci kontenera. Pełne kity (z binariami) zostają
  w sandboxie Higgsfield (`/home/user/kat/kits`) ok. 24 h; `_tools/job.sh` pobiera je ponownie w dowolnym środowisku z dostępem do CDN.
- Mapy w `katana-refs` są wynikiem detektora (`analyze_ref.py`), nie ręczną weryfikacją cięć.
- Zrzut jest stanem na 2026‑10‑09; Higgsfield wersjonuje workflowy (np. `faceless-video 2.4`), więc warto go odświeżać.

---

## Etap 2 (następny krok) – kandydaci na uniwersalne skille

Z tego materiału najłatwiej wyciągnąć „tool‑agnostic” skille:

1. **Product recipe skill** – struktura z B (effect / preserve / params / master prompt) + 63 master prompty jako biblioteka stylów. Działa 1:1 w Nano Banana Pro, GPT Image, Seedream.
2. **Photography vocabulary + negative prompts + refinement pass** (`product-photoshoot/references/`) – uniwersalny słownik dla każdego generatora obrazu.
3. **Thumbnail frameworks (16)** – koncepcje miniatur niezależne od narzędzia.
4. **Character sheet slot architecture** – prompt‑builder postaci z „anti‑AI realism”.
5. **Katana edit maps** – kontrakt „reference → edit map → compositing recipe → QA”; przenośny na Premiere/AE jako brief montażowy, nie tylko na Pythona. Materiał: 28 master promptów (C) + 20 map montażowych referencji i 8 kitów (I).
6. **Faceless scriptwriter + VO/captions** – pipeline narracyjny niezależny od Higgsfield (ElevenLabs, Kling, Seedance).
7. **Brandkit design brain + logo prompt enhancer** – briefy identyfikacyjne.
8. **Ad multiplier prompt‑writer** – gramatyka promptu „edycji istniejącego wideo” (podmiana/zachowanie).
9. **AI Influencer briefs (39)** – wzorzec „two‑panel casting sheet”.
10. **Viral effects (87 opisów)** – seedy efektów do Kling/Seedance.
