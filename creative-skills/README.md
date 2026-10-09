# creative-skills – uniwersalna paczka skilli (etap 2 reverse‑engineeringu Higgsfield)

15 skilli wyciągniętych z promptów Higgsfield MCP (`../higgsfield-prompts/raw/`) i przerobionych tak, żeby działały
z dowolnym narzędziem: Nano Banana Pro, KLING, Seedance 2, Higgsfield Cinema Studio, Premiere Pro / After Effects,
Figma / Illustrator / Photoshop. Z promptów zostało **rzemiosło** (słowniki, frameworki, przepisy numeryczne, gramatyki promptów,
checklisty QA), wyleciało wszystko, co było „klejem” do narzędzi Higgsfield (wywołania MCP, kredyty, widgety, modele).

Konwencja: `SKILL.md` po angielsku (prompty do generatorów i tak są po angielsku), w `description` są polskie frazy‑triggery,
żeby Claude łapał skill, gdy piszesz po polsku. `references/` = biblioteki (słowniki, master prompty, mapy montażowe).

## Instalacja

```bash
# globalnie (wszystkie projekty)
cp -r creative-skills/<skill> ~/.claude/skills/
# albo tylko w projekcie
cp -r creative-skills/<skill> <projekt>/.claude/skills/
```

Żeby Claude **sam** wiedział, czego użyć, wklej do `CLAUDE.md` projektu zawartość `ROUTING.md` (krótka macierz decyzyjna).
Opisy skilli są już „pushy”, więc trigger działa i bez tego, ale router rozstrzyga przypadki graniczne (np. miniatura vs packshot).

## Macierz: kiedy czego używać

| # | Skill | Użyj, gdy… | NIE używaj, gdy… (→ zamiast) | Wejście | Wyjście | Narzędzia docelowe |
|---|---|---|---|---|---|---|
| 1 | `product-shot-recipes` | packshot, hero shot, zdjęcie produktu, reel cover z produktem, 63 gotowe przepisy (również krótkie ruchy kamery wideo) | ogólna fotografia bez produktu (→ photo-prompt-craft); miniatura YT (→ thumbnail-design) | zdjęcie produktu + intencja | prompt obrazu/wideo z regułą „preserve” | Nano Banana Pro, Higgsfield, KLING (ruchy kamery) |
| 2 | `photo-prompt-craft` | dowolny prompt fotograficzny: światło, obiektyw, look, negatywy, poprawka po nieudanej generacji | gotowe przepisy produktowe (→ 1); postać do serii (→ 4) | brief lub nieudany obraz | ustrukturyzowany prompt + negatywy + pass poprawkowy | każdy generator obrazu |
| 3 | `thumbnail-design` | miniatura YouTube / okładka Reela / TikToka, 16 frameworków, emocja twarzy, tekst na obrazie | packshot (→ 1); statyczna reklama z copy (→ 6) | temat filmu, zdjęcie twarzy, hasło | prompt obrazu + spec tekstu (do wypalenia w Nano Banana Pro lub Photoshopie) | Nano Banana Pro, Photoshop/Figma |
| 4 | `character-sheet-builder` | spójna postać do serii obrazów/wideo, model sheet, turnaround, „anty‑AI” realizm | persona influencera do kanału (→ 12); pojedynczy portret (→ 2) | opis postaci lub referencja | prompt arkusza postaci w architekturze slotów + kit spójności | Nano Banana Pro → KLING/Seedance/Higgsfield |
| 5 | `brand-identity-kit` | logo, paleta, typografia, brandbook, mockupy, merch, packaging, social templates | pojedyncza kreacja reklamowa (→ 6); strona www (→ 15) | wywiad o marce | brief marki + prompty logo/mockupów + outline brandbooka | Figma/Illustrator + Nano Banana Pro (mockupy) |
| 6 | `static-ad-creatives` | statyczne reklamy Meta/IG/TikTok z copy, karty marketplace, warianty | wideo UGC (→ 10); identyfikacja marki (→ 5) | marka + produkt + oferta | zestaw: prompt obrazu + headline/primary/CTA + layout | Nano Banana Pro + Figma |
| 7 | `video-edit-brief` | montaż „pod referencję”: mapa cięć, przepis kompozycji w liczbach, choreografia tytułów, QA; remiks edita na nowy subject; 28 stylów Katany + 20 map | pisanie promptu do generatora wideo (→ 8/9); same napisy (→ 13) | wideo referencyjne lub brief + materiał | brief montażowy 1:1 na keyframe’y Premiere/AE | Premiere Pro, After Effects, Higgsfield Katana |
| 8 | `video-edit-prompting` | edycja istniejącego wideo modelem V2V: podmiana osób/produktów/tła z zachowaniem cięcia, 1→N wariantów, wersja na inny rynek, motion transfer vs object replacement | nowy klip od zera (→ 9 / cinematic-prompt-builder); montaż ręczny (→ 7) | gotowy klip + co zmienić | prompt „replace/preserve” + macierz wariantów | KLING, Seedance 2 (ref video), Higgsfield Genjutsu |
| 9 | `viral-effects-library` | hook/efekt/przejście do klipu, 87 opisów efektów, ruchy kamery produktowej, ruchy Genjutsu | pełny scenariusz reela (→ viral-reel-builder); edycja istniejącego klipu (→ 8) | subject + cel | prompt efektu (subject lock, akcja, kamera, czas) | KLING, Seedance 2, Higgsfield |
| 10 | `ugc-video-scripts` | reklama UGC: review twórcy, product‑only VO, unboxing, try‑on, tutorial, website tour | faceless narracja (→ 11); copy do statycznej reklamy (→ 6) | produkt + format | skrypt + hooki + shot list + prompty per ujęcie + styl napisów | Nano Banana Pro + KLING/Seedance/Higgsfield lub nagranie własne |
| 11 | `faceless-video-pipeline` | film narratorski bez twarzy: explainer, historia, kids, picture story, bajka; lock stylu, jeden głos, napisy | reklama (→ 10); sam lektor (→ 14) | temat / kanał | skrypt + shot list z promptami w zablokowanym stylu + spec VO + napisy + brief montażu | Nano Banana Pro, KLING, ElevenLabs, Premiere |
| 12 | `ai-influencer-casting` | persona/AI influencer do kanału lub serii reklam, arkusz castingowy, taksonomia cech, 39 briefów | postać fabularna/animowana (→ 4) | założenia kanału | brief castingowy dwupanelowy + lock spójności | Nano Banana Pro → wideo |
| 13 | `caption-and-title-systems` | napisy, subtitles, tytuły, animowany tekst, layouty 9:16, PIP/split, strefy bezpieczne | cała mapa montażu (→ 7) | gatunek klipu + platforma | spec napisów/tytułów do Essential Graphics / AE (+ SRT) | Premiere Pro, After Effects |
| 14 | `narration-vo` | lektor dopasowany do okien czasowych, budżet słów/s (PL/EN), jeden głos w długiej narracji, presenter mode | pisanie całego skryptu (→ 11) | tekst + czasy | dopasowany tekst VO + znaczniki pauz + brief prezentera; `scripts/fit_narration.py` | ElevenLabs / dowolny TTS, Premiere |
| 15 | `web-design-taste` | landing / web‑app / mini‑gra do viralowych projektów: recipe, zasady „smaku”, katalog wow‑efektów, rubryka review, image‑to‑code z Figmy | identyfikacja marki (→ 5) | brief lub makieta Figma | plan designu + checklista + implementacja | Figma → kod (Claude Code) |

## Workflow: jak Claude ma wybierać

1. **Co jest wynikiem?** obraz → 1/2/3/5/6/12 · klip z generatora → 8/9 · montaż/edycja w NLE → 7/13/14 · produkcja wieloetapowa → 10/11 · strona → 15.
2. **Czy jest materiał wejściowy?** zdjęcie produktu → 1 · gotowy klip do zmiany → 8 · wideo referencyjne do odtworzenia → 7 · zdjęcie twarzy + temat → 3 · makieta → 15.
3. **Czy chodzi o spójność w serii?** postać → 4 · persona influencera → 12 · marka → 5 · styl kanału → 11.
4. **Skill nie pasuje w 100 %?** Weź najbliższy, a słownik z `photo-prompt-craft` (obraz) i `viral-effects-library` (wideo) jako dopalacz.
5. **Łańcuchy typowe:** `concept-loop` → `ugc-video-scripts` → `product-shot-recipes` (klatki) → `viral-effects-library` (ruch) → `caption-and-title-systems` (napisy) → `narration-vo`.
   Dla edita „pod referencję”: `video-edit-brief` → `caption-and-title-systems` → (opcjonalnie) `video-edit-prompting` na warianty.

## Jak to współgra z Twoimi istniejącymi skillami

| Istniejący skill | Relacja |
|---|---|
| `cinematic-prompt-builder`, `seedance-director` | piszą prompt **nowego** klipu od zera. Ta paczka dokłada: efekty/hooki (9), edycję istniejącego klipu (8), spójne postaci (4/12). |
| `prompt-master` | ogólny; `photo-prompt-craft` (2) jest jego fotograficzną specjalizacją z gotowym słownikiem i negatywami. |
| `concept-loop`, `viral-reel-builder`, `storytelling-viral-journal` | koncepcja i scenariusz **przed** produkcją. Paczka startuje po nich (10/11/7). |
| `creative-director` | Big Idea kampanii → potem 5/6 (identyfikacja, kreacje). |
| `mobile-vikings-kv` | własny system marki; 6 i 2 są ogólne i nie nadpisują zasad MV. |
| `task-estimator` | wycena; niezależny. |

## Zawartość paczki (pliki)

| Skill | Rozmiar | Pliki poza SKILL.md |
|---|---|---|
| `ai-influencer-casting` | 76 KB | `references/casting-briefs.md`, `references/consistency-procedure.md`, `references/trait-taxonomy.md` |
| `brand-identity-kit` | 95 KB | `references/applications.md`, `references/design-brain.md`, `references/intake-and-brand-lock.md`, `references/logo-and-prompt-enhancer.md`, `references/palette-typography.md`, `references/qa.md` |
| `caption-and-title-systems` | 67 KB | `references/caption-systems.md`, `references/failure-modes.md`, `references/layouts-and-geometry.md`, `references/subtitle-rules.md`, `references/title-animation-and-motion.md`, `scripts/words_to_srt.py` |
| `character-sheet-builder` | 41 KB | `references/consistency-kit.md`, `references/realism-engine.md`, `references/slot-architecture.md`, `references/styles.md` |
| `faceless-video-pipeline` | 119 KB | `references/assembly-brief.md`, `references/explainer-presets.md`, `references/format-variants.md`, `references/prompts-and-blocks.md`, `references/scriptwriter.md`, `references/style-packs.md`, `references/topic-sourcing.md`, `references/vo-and-captions.md` |
| `narration-vo` | 46 KB | `references/presenter-mode.md`, `references/timing-budgets.md`, `scripts/fit_narration.py` |
| `photo-prompt-craft` | 54 KB | `references/negatives.md`, `references/photographers.md`, `references/refinement-pass.md`, `references/typography.md`, `references/vocabulary.md` |
| `product-shot-recipes` | 141 KB | `references/formats.md`, `references/recipe-library.md` |
| `static-ad-creatives` | 44 KB | `references/copy-frameworks.md`, `references/formats-and-layouts.md`, `references/qa.md` |
| `thumbnail-design` | 48 KB | `references/emotions-and-lighting.md`, `references/frameworks.md`, `references/prompt-blocks.md`, `references/text-overlay.md` |
| `ugc-video-scripts` | 146 KB | `references/creator-persona.md`, `references/formats.md`, `references/hooks-and-captions.md`, `references/shot-prompts.md` |
| `video-edit-brief` | 220 KB | `references/compositing-recipe.md`, `references/creative-quality.md`, `references/edit-map-grammar.md`, `references/master-prompt-template.md`, `references/premiere-ae-mapping.md`, `references/qa-checklist.md`, `references/style-library.md` |
| `video-edit-prompting` | 72 KB | `references/finishing-and-qc.md`, `references/prompt-grammar.md`, `references/recreate.md`, `references/variant-matrix.md` |
| `viral-effects-library` | 82 KB | `references/camera-moves.md`, `references/effect-to-prompt-examples.md`, `references/effects-catalog.md`, `references/genjutsu-motions.md`, `references/marketing-templates.md` |
| `web-design-taste` | 108 KB | `references/app-and-game-surfaces.md`, `references/design-recipe.md`, `references/image-to-code.md`, `references/review-rubric.md`, `references/taste-rules.md`, `references/wow-catalog.md` |

Ścieżki `<PLAYGROUND>/...` w skillach oznaczają root tego repo (tam leżą surowe źródła w `higgsfield-prompts/raw/`).

## Weryfikacja paczki

```bash
python3 creative-skills/_tools/lint_pack.py
```
Sprawdza frontmatter, wymagane sekcje, istnienie plików z `references/`, i czy nie zostały Higgsfield‑izmy (nazwy narzędzi MCP, kredyty).

## Pochodzenie

Każdy skill ma w sekcji „References” ślad do źródła w `../higgsfield-prompts/raw/`. Źródła: workflowy MCP (A), 63 przepisy (B),
Katana (C + I: mapy montażowe i kity), katalogi (F), oficjalne skille GitHub (G).
