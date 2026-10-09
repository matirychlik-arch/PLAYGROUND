<!-- Wklej do CLAUDE.md projektu. Router dla paczki creative-skills. -->
## Creative skills router

When the request is about making or editing visual content, pick the skill by the deliverable, then by the input:

- Image of a product (packshot, hero, reel cover, catalog) -> `product-shot-recipes`. Any other photo prompt, or fixing a failed generation -> `photo-prompt-craft`.
- YouTube / Reels / TikTok thumbnail or cover with a face and text -> `thumbnail-design`.
- Static ad with copy (Meta/IG/TikTok, marketplace card) -> `static-ad-creatives`. Logo, palette, brandbook, mockups -> `brand-identity-kit`.
- A character that must stay consistent across images/videos -> `character-sheet-builder`. A persona/AI influencer for a channel -> `ai-influencer-casting`.
- A new generated clip: hooks, effects, transitions, product camera moves -> `viral-effects-library` (full cinematic prompts: `cinematic-prompt-builder` / `seedance-director`).
- Changing an existing clip with a video-to-video model (swap person/product/background, 1->N variants, other market) -> `video-edit-prompting`.
- An edit to be built in Premiere/AE from a reference video, or a brief with cuts, strobes, titles and audio hits -> `video-edit-brief`.
- Captions, subtitles, titles, 9:16 layouts, PIP -> `caption-and-title-systems`. Voice-over fitted to timings or presenter mode -> `narration-vo`.
- A UGC ad (creator review, unboxing, try-on, tutorial, website tour) -> `ugc-video-scripts`. A faceless narrated video (explainer, history, kids, story) -> `faceless-video-pipeline`.
- Landing page, web app or mini game design and Figma-to-code -> `web-design-taste`.

Order of operations for a production: concept (`concept-loop` / `viral-reel-builder`) -> script (`ugc-video-scripts` or `faceless-video-pipeline`) -> stills (`product-shot-recipes` / `character-sheet-builder`) -> motion (`viral-effects-library` / `video-edit-prompting`) -> edit (`video-edit-brief`) -> text (`caption-and-title-systems`) -> voice (`narration-vo`).
Polish requests map the same way; the skills' descriptions carry Polish trigger phrases.
