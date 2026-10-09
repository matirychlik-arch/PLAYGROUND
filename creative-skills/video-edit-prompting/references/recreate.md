# Recreate an ad for another market, language, cast or product

Contents:
1. Recreate vs edit vs hook/CTA only
2. Intake: what to ask, defaults
3. Writing the recreate request (template)
4. Image roles, voice and language rules
5. Hook or CTA only
6. Manual recreate procedure (KLING, Seedance 2, any generator without a recreate mode)
7. Localization checklist for a new market
8. Failures and delivery report

Source note: sections 1 to 5 and 8 carry the rules of a production "recreate" workflow, generalized from one vendor's backend to any tool; sections 6 and 7 are added procedures for generators that have no recreate mode.

## 1. Recreate vs edit vs hook/CTA only

Recreate re-shoots one source ad as new footage for another market, audience, spoken language, cast, product or setting, while keeping the source's structure: its beats, order, timing, pacing, aspect ratio and capture style. Every output is new footage, so the source performance, motion and audio do not survive by design.

| The user wants | Mode | Go to |
|---|---|---|
| Same footage, motion and audio; only named targets change (person, product, background, one line of text) | Edit | prompt-grammar.md |
| Same ad made again with new footage: local cast and setting, new spoken language, different audience, own product in the source structure, several market versions | Recreate | this file |
| Only a new opening hook, a new closing call to action, or both; the rest of the ad stays | Hook/CTA only | section 5 |
| Dub or translate the existing footage, reframe, or an original ad that merely borrows ideas from a reference ad with a new script | None of these | route elsewhere (dubbing/translation tool, reframing tool, or write a new script) |

If the request fits both edit and recreate, ask one question: keep the original footage and change named targets, or re-shoot the ad as new footage?

## 2. Intake: what to ask, defaults

Ask once, in one message, only for what is missing:

1. the source video (4.0 to 30.0 seconds in the reference workflow; check your tool);
2. what changes: target market or audience, spoken language, a new product, or new people.

Defaults without other instructions: one output, 720p. Do not ask about audio, setting or image roles: those are decided from the request and the images, and the request text should say what the user wants. Never invent product facts, prices, offers or claims. Ordered lists pair by output position (see variant-matrix.md); never build a Cartesian product.

When the user wants a different person and gives no photo, describe that person in the request in words (the reference backend generated one adult likeness itself); for a tool that needs an image, make a stand-in person image first (variant-matrix.md, stand-in people). With a photo, attach it and say in the request whom it replaces.

## 3. Writing the recreate request

In a recreate mode the request carries everything: the backend analyzes the source itself and decides language, cast, image roles, audio and setting from the request and the images. Whatever is not in the request is lost. Keep it to at most 4,000 characters and in the user's words. Include:

- the market or audience;
- the spoken language;
- a replacement product's name and the facts the user gave (nothing else);
- who each image is and what it replaces;
- lines to say exactly, in quotes;
- any explicit audio or setting wish.

Template:

```text
Recreate this ad for [market/audience] in [language].
Cast: [who replaces whom; "@Image1 is [name/description] and replaces the main presenter"].
Product: [name], [facts given by the user only]. [@Image2 is the product pack; show it as the hero product.]
Setting: [wish, or "a typical [market] [location]"].
Lines to say exactly: "[line 1]" ... "[CTA line]".
Audio: [keep source music / new local music / silent / user wish].
Keep the structure, beat order, timing, pacing and vertical 9:16 format of the source.
```

Examples:

```text
Recreate this ad for the German market in German, with the presenter in the image replacing the main presenter.
```

```text
Odtwórz tę reklamę na rynek niemiecki, po niemiecku. Prezenterka z @Image1 zastępuje główną postać. Produkt: krem do rąk "VELA 75 ml", cena nie pojawia się w spocie. Linia na końcu dokładnie: "Jetzt testen".
```
(Write the request itself in English when the tool is English-first; the quoted lines stay in the target language.)

## 4. Image roles, voice and language rules

- Images are classified by what they show: product, person, wardrobe, location, prop, logo or style. The words in the request about an image win over the classification. If you attach a logo, say it is a logo; if a photo is a mood reference, say "style reference only".
- A new performer or a new spoken language gets a new voice. The source voice and music stay only when nobody who speaks changes, unless the request says otherwise.
- Never ask for or invent price, offer, claim, certificate or legal text. If the source contains them and the new market needs different ones, ask the user for the new text and put it in quotes in the request.
- Do not promise captions: recreate renders contain no captions. Subtitles are added in the editor (Premiere/AE) after the render.
- Each output is an independent analysis and render, so two outputs with identical inputs still differ. For several market versions, give each its own request.

## 5. Hook or CTA only

Use when the user wants a new opening hook, a new closing call to action, or both, with the rest of the ad kept.

Rules of the reference behavior (copy them when you do it by hand):

- Find each section in the source: the first hook, the last CTA.
- Cut at the end of the shot that finishes the section, never inside a spoken word.
- Render each new section in the source's setting. Reference lengths: a hook 4 to 15 seconds, a CTA 4 to 5 seconds.
- Stitch the new sections in with hard cuts. Resulting length = source length minus removed sections plus new sections.
- If the source has no clear hook or CTA, add the new one before (hook) or after (CTA) the whole ad and remove nothing.
- The request says what the new hook or CTA should do or say. Leave out changes to the rest of the ad; a hook/CTA-only run cannot make them.
- With both sections requested, if one part fails, keep the source in place of that part and say which part failed.

Request example:

```text
New hook: open on a close-up of the product with the question "Still tired at 3 pm?"
```

By hand (Premiere/AE): mark the hook end at the last frame of its shot, generate or shoot the new hook, join with a hard cut, and check that audio does not cut a word in half.

## 6. Manual recreate procedure (any generator)

Use when the tool has no recreate mode (KLING, Seedance 2 or another image/video generator). The goal is the same: new footage, same structure.

1. **Break the source into a shot list.** Note for every shot: start and end time, framing, camera move, action, spoken line or on-screen text, and what it is for (hook, problem, product, proof, CTA). Use a scene-analysis tool or watch it twice. This list is the timed caption that every later step refers to.
2. **Write the localization brief**: market, language, cast description, setting, props, product facts given by the user (section 7).
3. **Make the references**: product pack shot (Nano Banana Pro or the real photo), a cast portrait or character sheet for each recurring person, a location plate if the setting must match across shots. Reuse the same references for every shot so identity stays stable.
4. **Rewrite each shot as a generator prompt**: same duration, same framing and camera move as the source shot, new cast, setting, props and language. Use the 7-slot structure from the viral-effects-library skill (subject lock, start state, action, camera, end state, format, avoid) or a Seedance prompt. Keep the beat order identical.
5. **Generate shot by shot** at the source aspect ratio, 5 to 10 seconds per shot at most, silent. Where a shot is mostly a product or label, use image-to-video from the product pack shot.
6. **Voice and music**: record or generate the new-language voice-over from the translated lines; keep the source music only if licensing and market allow.
7. **Assemble in Premiere/AE**: cut to the source timing (shot durations from the shot list), add captions and legal text yourself, lay in voice and music, match loudness.
8. **Check against the source structure**: same number of beats, same order, same total length within one second.

Poor fit: lip-synced dialogue across many shots in a generator that cannot hold a face; split such an ad into voice-over plus B-roll shots.

## 7. Localization checklist for a new market

Added checklist, not from the source workflow. Run it before writing the request.

- Language: spoken lines, on-screen text, product naming, number and date format, currency symbol and position.
- Cast: apparent age and look plausible for the market; clothing for the climate and season; no copy of a real person.
- Setting: architecture, street, interior style, packaging shelf context, license plates and signage language.
- Props and product: pack variant sold in that market, units (ml/oz), local retailer logos only if the user supplied them.
- Claims and legal: replace every claim, price, offer and disclaimer with user-supplied text for that market; never keep a source claim unchecked.
- Culture: gestures, colors, holidays, humor and food that mean something else locally; ask the user when unsure.
- CTA: local call to action wording and channel (app, site, store).

## 8. Failures and delivery report

| Failure | Response |
|---|---|
| Source length outside the tool's range | Report the measured length and the accepted range, stop or fix the input; never resubmit unchanged |
| Parameter or format error | Correct the mapping once and resubmit that output only |
| The tool reports a missing fact (product, price, name) | Report the missing fact, ask the user, put the answer in the request, resubmit once |
| Content or rights filter triggered | Report it and do not resubmit the same request |
| Other terminal failure | Retry that output once with the same request |
| Some outputs still pending | Report them as pending, never duplicate them |

Delivery: list results in output order labeled `Output 1`, `Output 2`, and so on. For each, state the change it was asked for and the resolution. Report completed/total, failures and pending. A job can sit in a queue for several minutes while the tool analyzes and plans; that is not a stall. For a hook or CTA output, say which part was replaced and that the rest of the source is unchanged.
