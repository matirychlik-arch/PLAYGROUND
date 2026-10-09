Read the ugc-video entrypoint and shared execution references first. This file
contains only the selected format; shared duration, cleanup, transport and failure
contracts apply to every stage.

# UGC website video

Produce one hosted 9:16 MP4. A single talking-head creator remains on camera and
speaks continuously. Real mobile screenshots from the supplied URL appear as
large static overlay cards. There are no storyboards and no generated UI.

## Hard rules

- Screen content is always real captured pixels from the supplied site or
  screenshots the user supplied. Never generate, restyle, animate, or invent UI.
- Never ask the user to record their screen. Never use web search or an
  unrelated source to fill missing page content.
- Creator stays on camera and supplies the continuous audio spine. Screenshot
  cards overlay the creator; they are never full-screen or scrolling.
- Body clips are visually product-free. A physical product may appear only in
  the closer and only from a real image on the supplied page.
- Use the same `character_media_id` in every clip and never regenerate it.
- Captions are on by default. Only an explicit “no captions” request skips them.
- Capture failure on the first attempt triggers one user choice immediately:
  send screenshots or make a talking-head-only version. Do not silently retry.
- Hide models, job IDs, internal phases, and intermediate files.

## Phase 0 — Intake and routing

Parse required URL, duration, attached creator photo or desired gender,
appearance/location overrides, site type/audience/surface, language, approved
claims, and `caption_mode`: `Both` default, `Subtitles`, or `Hook`.

Stay in this skill when the user names SaaS UGC/site tour or wants the supplied
page visible. A product-page URL stays here when its page appears onscreen.
Hand off to product-side UGC only when the page will not appear.

Ask once for missing URL, duration (offer 10s/15s/30s/45s), creator input, and
caption mode when unspecified. Do not offer generated UI, scrolling, full-screen
screens, model choices, aspect ratios, audio choices, or clip-count forks.

## Phase 1 — Capture the site

Read `references/website-capture.md`. Reserve image upload slots before capture.
Run the preinstalled mobile Chromium capture in one self-contained
`sandbox_exec`, producing and uploading:

- one full-page mobile capture for the section map;
- 6–10 useful dedicated stills when available: hero/product, features,
  dashboard/search/editor, reviews, specs, pricing, or plans.

Confirm successful uploads and keep their hosted URLs. Skip nav/footer/logo
filler. Build an ordered section map; the same order drives monologue beats and
overlay cards.

On error, bot wall, login gate, blank result, or fewer than three usable cards,
ask immediately: `I'll send screenshots` or `Make it without the site`. If real
screenshots do not arrive, continue talking-head-only and disclose that in the
final report.

## Phase 2 — Lock the creator

If the user attached a creator photo, import it and use it unchanged. Skip the
generated-seed de-slop pass.

Otherwise read `references/unboxing-ugc-character.md` and
`references/saas-ugc-character.md`, settle fresh variety rolls, write a clean
product-free creator prompt, and submit:

```json
{
  "requests": [
    {
      "index": 0,
      "params": {
        "model": "soul_2",
        "prompt": "<creator prompt>",
        "count": 1,
        "aspect_ratio": "3:4",
        "quality": "2k"
      }
    }
  ]
}
```

Wait until terminal, then take the completed creator `result_url` returned by
`jobs_wait` and de-slop the generated seed with one `generate_image_batch`
request: `seedream_v5_pro`, its confirmed media ID after media_import_url with canonical role `image`,
3:4, 2k, and this exact prompt:

> KEEP EXACTLY the framing, composition, pose, subject and identity of this
> vertical portrait — no reframe, no zoom, no crop, no change to the person's
> face / hair / body / clothing. CHANGE ONLY micro-realism: true-to-life
> pore-level skin with natural texture and fine vellus hair, real material
> detail, even natural daytime light with gentle highlight roll-off and faint
> true sensor noise, a flat authentic iPhone selfie, deep focus. PRESERVE the
> face's exact shape / width / proportions 1:1 — do NOT squeeze / narrow / slim /
> stretch the face. AVOID AI-slop: waxy plastic skin, airbrushed poreless skin,
> beauty-filter smoothing, over-saturation, HDR glow / bloom / halos,
> oversharpening, teal-orange grade, shallow depth of field, bokeh, cinematic /
> DSLR look. No added text, no watermark.

Import an authorized HTTPS input once with media_import_url and use its confirmed ID in generation.
Never pass the raw creator job ID to this i2i call.

On moderation rejection stop the dependent path. A missing cleaned creator cannot seed video.

## Phase 3 — Write monologue and card plan

Read `references/saas-monologue.md`. Write in English unless explicitly changed.
Use hook → site solves it → result/action. The first body beat names the site;
later body beats follow captured card order; the closer contains no card.

Target 22–26 words for ≤10s, 28–33 for 11–12s, and 35–40 for 13–15s, with
varied 2.4–2.7 words/second delivery. Save exact `output/script.txt`, a ≤6-word
`output/hook.txt`, and ordered `{section_label, words}` beats.

## Phase 4 — Generate talking-head clips

Read `references/saas-clip-prompt.md`. Write every clip prompt before submission.
Each is one continuous shot: no board, slot, cut, site/UI visual, or product in
body clips. Restate locked identity, medium 9:16 framing, centered head, US
accent, varied lively pace, phone-mic audio, matching ambience, and no music.

For a physical-product closer, extract one real product image only from the
supplied page, convert it to a confirmed Higgsfield image UUID, and add it as the
second media. If no usable product image exists, use a neutral closer gesture.

Submit all N requests through `generate_video_batch`, at most six per call:

```json
{
  "requests": [
    {
      "index": 1,
      "params": {
        "model": "seedance_2_5",
        "prompt": "<one-shot prompt>",
        "count": 1,
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "duration": 15,
        "mode": "omni_reference",
        "generate_audio": true,
        "medias": [{ "value": "<character_media_id>", "role": "image" }]
      }
    }
  ]
}
```

The physical closer adds `product_closer_reference` with role `image`. If that
closer is moderated, retry only it without product media, with the same creator.
Never regenerate the creator.

Before submission reject any body prompt containing `Hard cut`, `Cut 1`,
`slot`, `board`, a product visual, or a rendered website/UI/screen/browser.

## Phase 6 — Composite

Read `references/screen-broll-and-composite.md`. Reserve the final video upload,
then run one self-contained sandbox command that downloads clips and confirmed
card images, concatenates clips in stable order, and overlays cards at authored
word-time anchors:

- no card during first ~1–2s hook or closer;
- each card ~1.2–1.5s with ~0.3–0.5s clean-face gap;
- contain-fit inside ~0.78W × ≤0.60H, centered and shifted slightly up;
- keep the bottom ~15% clear for captions;
- copy audio and encode video once.

With no site cards, concatenate the talking-head clips only. The phase is not
complete until `output/final.mp4` exists and was PUT successfully.

## Phase 7 — Captions

Read video-montage (website-captions for website; ugc-captions otherwise). Captions are on by default. Use word-level
Whisper timing from final audio and burn the selected `Both`, `Subtitles`, or
`Hook` layers in one pass. Never infer timings. If no speech is found, burn
nothing and deliver the clean final. PUT and confirm the chosen final video.

## Phase 8 — Deliver and optionally publish

Return one confirmed hosted video URL and duration. State when site capture was
unavailable and the output is talking-head-only.

Then ask once whether to publish to TikTok. On yes, use the current sequence:
`tiktok_accounts` → `tiktok_connect` if needed → `tiktok_prepare_publish` →
user reviews and submits the publish-form widget →
`tiktok_publish_status`. Do not call `tiktok_publish` yourself; publication requires the widget. Clients without MCP Apps cannot publish.
