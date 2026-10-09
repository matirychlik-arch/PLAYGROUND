# Katana preset: Kawaii Pop (/katana/kawaii-pop)

The instructions below are the selected preset's own instructions for this request. Follow them from their first step: they define the inputs, tools, workflow and deliverable. Do not substitute another preset, workflow or generation path.

- If a tool the preset requires is unavailable in this connection, stop and tell the user the preset cannot run here; do not substitute other tools.
- Inputs: the user's message may include a `MEDIA:` block of `<input>: <image|video> media_id=<uuid>` lines and an `INPUTS:` block of `<input>: <JSON value>` lines, composed by Higgsfield from the Katana form. They are values the user already supplied for those inputs: use them as these instructions describe and do not call media_upload_widget or ask for them again unless a required input is still missing. Pass a media_id directly to tools that accept one; their file URLs are listed under Supplied media when the media are passed to this tool. Older messages may list `<input>: <https URL>` lines instead; treat each URL the same way.
- Collecting inputs: the user may start the preset with the bare command and no `MEDIA:` or `INPUTS:` block; that is a normal start, not an error. Before the first step that uses an input, compare the Inputs list with what the user already supplied (MEDIA/INPUTS blocks, confirmed media_ids or files earlier in the conversation).
- Nothing supplied yet and the user asked to run the preset: open its form with get_presets {"source":"katana","preset_id":"kawaii-pop"} as the only tool in that turn, say in one short line to fill it in below, and wait. The submitted form arrives as a /katana/kawaii-pop message with MEDIA and INPUTS blocks. A request only to read or explain the preset does not open the form.
- Some inputs already supplied, the form tool fails, or the user says the form is not visible: ask once for what is still missing with exactly this template in the user's language, naming each input by its label (never the field path) with what it should be and how many:

  **<preset title>**: to start I need:
  **Required**
  - <label>: <what, how many>
  **Optional** (skip any)
  - <label>: <what>, default <default> when it has one
  <one line: upload the files in the window below, and reply with any text>

  Omit a section with no entries and add nothing else to that message. When files are missing, upload files the user already attached yourself if your code environment can read them (media_upload, PUT, media_confirm); otherwise call media_upload_widget as the only tool in that turn, with the missing fields' media type and count (type auto with multiple when several media fields are missing).
- Map each received file and answer to its field, use a field's default when the user does not choose, and continue from the preset's first step. Do not start generation or spend credits while a required input is missing, and do not ask again for inputs already supplied or declined.
- Platform rules still apply: consent, authorization, credit confirmations and credential handling are not overridden by these instructions.
- Keep the run going: once the inputs are available, work through the steps without pausing for progress updates. Never end your turn while a job you started is still running; wait with jobs_wait (repeat it until the job completes or fails) and continue with the next step in the same turn. Stop only where these instructions explicitly require the user's decision, for a missing required input, or for a failure you cannot recover from. At a required decision, first wait for and show the finished result it is about, then ask once in one short message; do not ask about a result that is still generating.
- Final video delivery: after the preset's final render has completed and you have verified its result, display it with show_katana_result. Use the confirmed uploaded video media_id; do not upload it again. If the final export is already available at an HTTPS video URL, call show_katana_result with url to import and display it. If the final export is still a file, use media_upload, PUT its bytes to the returned upload_url, then media_confirm with type video; for a sandbox export, create the upload slot before the producing sandbox command and PUT the export in that same command. Never use media_upload_and_confirm for a generated file, pass a local path or job ID to show_katana_result, or display an intermediate preview as the final result. This is delivery of the requested video, not public publishing. If export or upload fails, report that failure instead of calling the result tool.
- If these instructions are no longer in your context during a long run, call get_preset_instructions with {"preset":"/katana/kawaii-pop"} again before continuing.
- These instructions have 2 parts; this is part 1. Before taking any action, read every remaining part in order by calling get_preset_instructions with {"preset":"/katana/kawaii-pop/part-2-96119fbe327f"}.

## Inputs

The preset's form (field path, label, kind; required or optional):

- `media.character` ("Character", "Photo of the heroine: one person, face visible, both eyes open, framed at least to the chest. Without it a new heroine is generated."): image file, up to 1; optional
- `slot_values.chant` ("Chant", "Chant words. Default: NYAN / ICHI NI SAN / NYAN / ARI·GATO"): text; optional
- `slot_values.prompt` ("Wishes (optional)", "Optional wishes about the inputs or the result. Keep the preset defaults unless a change is explicitly requested."): text; optional

---

---
name: kawaii-pop
description: >-
  Create a short kawaii J-pop/K-pop selfie edit with a nyan-style chant
  ("nyan, ichi ni san, nyan, arigato"), face-tracked words, starbursts, giant
  letters and flashlight transitions on every beat. Use for requests to produce
  this chant edit or /kawaii-pop. The agent builds the beat, cut list and
  compositor itself in the Higgsfield sandbox (sandbox_exec), using the
  Higgsfield connector for generation.
  Text-only advice, ordinary trimming and unrelated edits keep their own routes.
---

# Kawaii Pop

Standalone preset; a bare slash command selects it. Keep answers already given. This skill says **what** to make;
you write all code (beat, cut list, compositor) your own way. Numbers are measured from the
reference (900×720, 30 fps): keep those defining timing, sound and look; decide the rest.

## Goal

- Reproduce the reference exactly: same cuts on the same beats/frames, timing, framing and shot sizes, effects, doodles, type and grade; the only changes are the ones this skill allows (heroine, looks, friend, chant/language, theme, palette, tag, aspect, duration, music). The heroine is always a new person (Soul or the user's photo), never the reference's idol. When unsure, match the reference.
- Carry its aura/mood: a sugary, playful idol backstage selfie vlog in bright, airy white light with rosy skin and inky hair; a pale lilac starburst and offset lilac halo around her, chunky white words snapping onto her face on every chant beat, magenta flashes and flashlight blow-outs on every cut.
- Where: all media work (downloads, transcoding, beat synthesis, face tracking, mattes, frame rendering, QA, encoding, uploads) runs in the Higgsfield sandbox through `sandbox_exec`, never on the user's machine. You implement compositor, doodles, words, transitions and coded beat yourself (e.g. Python + numpy/Pillow frames piped to ffmpeg); face positions via any method available in the sandbox, fallback in §8. Sandbox: ffmpeg/ffprobe, python3, numpy, Pillow, faster_whisper; no cv2/scipy/soundfile/pedalboard unless it shows otherwise; media in via `curl` from the CDN. Commands cap at ~16k chars → write code to files. Files vanish ~10 s after a call unless a background command holds the 15-minute lease → keep steps reproducible, run long jobs with `background: true` and poll. No base64/text relay of bytes; upload = `media_upload` → PUT with `Content-Type` and `If-None-Match: *` (both required) → after HTTP 200 `media_confirm`; never print signed URLs. No `sandbox_exec` → say so before spending credits.

**Reference** (Higgsfield CDN, public). Download it into the sandbox at the start of every
run and study it: the text describes it, the video shows it.

- Japanese idol edit "nyan, ichi ni san, nyan, arigato": 9.52 s (audio; video 283 frames = 9.43 s), 900×720 (5:4), 30 fps:
  `https://d30d7anzgyxsrg.cloudfront.net/user_3ByefnwR6sEVy13pzdD2kizfNIn/83058cc9-6072-42c5-a0f4-80326b859a83.mp4` (media_id `83058cc9-6072-42c5-a0f4-80326b859a83`)

Defaults = the reference. Change only what the user asks; derive the rest. YAONG (Korean cat
chant) appears below only as a worked example of a variant, never as the look to match.
Out-of-scope requests (end of file): say so before generating.

## 0. Parameters

Ask only where the request is ambiguous and the answer changes the result.

| Parameter | Default (reference) | Can change to |
| --- | --- | --- |
| Heroine | Soul 2.0, fictional idol (a new person, not the reference's idol) | user's photo (§1) |
| Looks | 2: A black halter with thin white stripes (phrase 1), B brown fur coat (phrase 2) | 1–3, any outfits |
| Friend | yes: B&W duet in the bridge, at the right edge in phrase 2 | none |
| Chant | NYAN / ICHI NI SAN / NYAN / ARI·GATO | any words, 4–8 per phrase (example: YAONG / HANA DUL SET / YAONG / SARANG·HAE) |
| Language | Japanese | Korean, English, any Seed Audio language |
| Animal theme | cat: "NYAN" call, cat-paw hands under the chin on the call, hands raised beside the head on the counts, "*" on the nose on the call repeat | bunny, puppy, bear, fox, none |
| Music | coded beat, 102 BPM (B ≈ 0.5875 s), 8-beat phrases | 90–150 BPM; user's own track |
| Duration | 9.52 s (2 phrases) | ~6–20 s |
| Aspect | 5:4 900×720 | 4:3 1440×1080, 9:16 1080×1920, 1:1 1080×1080 |
| Palette | lilac-pink `#f7cbfd` (halo, stairs), giant fill `#f8d8fc`, burst `#f5e7fb`, magenta wash peak `#c34ca7` | any 2–3 pastels (white stays the word/doodle fill) |
| Tag | an invented short handle with "*" (replaces the reference's caption) | any short handle with "*" |
| Final grade | matched to the reference (§10) | lighter, darker, none |
| Output fps | 30, with the reference's 18 fps hold cadence (§9) | 24, 60 |

## 1. Inputs and checks

All inputs optional: no photo → Soul heroine; no other reference video → the reference's
structure; no chant → NYAN / ICHI NI SAN / NYAN / ARI·GATO; no track → coded beat.

**Heroine photo** (must work for Seedance and face tracking):

- **One person**, frontal or 3/4, **both eyes visible** (no sunglasses or bangs over the eyes): no eyes = no face tracking, no face words.
- Short side ≥ 1024 px, face sharp, visible to the chest at least (tight crops make Seedance invent the body; the outfit drifts).
- **Not a celebrity or recognizable public figure** (IP-blocked, no rights).
- Not a bright front-camera selfie, wrong room or aspect? Normalize with `seedream_v5_pro` i2i first (§4). Dark or colored backgrounds ruin the vibe and the cutout.
- The photo's outfit = **look A**; other looks come from the normalized photo.
- Several people: ask which is the heroine. A real friend photo gets the same checks.

**Another reference video**: analyze it (§3). Same scheme (chant, face words, starburst,
blow-outs)? Map its words to roles, use its BPM and duration. Other edit kinds (dance,
story, lip-sync) are out of scope.

## 2. Models, tools, sandbox facts

| Task | Model / tool | Parameters |
| --- | --- | --- |
| Reference / track analysis | `sandbox_exec` + faster_whisper `small` | `word_timestamps=True` |
| Heroine, friend | `soul_2` | output aspect (4:3 for the 5:4 default, cropped later), quality 2k, count 4 |
| Extra looks / photo normalization | `seedream_v5_pro` (i2i) | output aspect (4:3 for 5:4), `resolution: 2k`, count 4, `medias:[{role:image_references, value:<id>}]`. **Not** `gpt_image_2` (worse face hold, color drift) |
| Chant voice | `seed_audio` | `voice_type: preset`, wav, 48 kHz, `pitch_rate: 2`, 4 takes, different voices (`list_voices`); pick the take closest to the reference's bright, high female chant. YAONG example used **Pixie** `0178ef57-ada4-43d9-992b-8d9221045bb4`; a user-picked voice overrides |
| Video | `seedance_2_5`, `mode: omni_reference` | output aspect (4:3 for 5:4, cropped in compositing), 1080p, `bitrate_mode: high`, `generate_audio: false`, `declined_preset_id: 24bae836-2c4a-48e0-89b6-49fcc0b21612`, **no `audio_references`**. Allowed durations: `models_explore get seedance_2_5` |
| Cutout | `remove_background` | `media_type: video`, every phrase clip (halo, starburst, arc letters and giant letters sit behind her) |
| Beat, face tracking, compositing | your own code in the sandbox (`sandbox_exec`) | §5, §8–§9 |

**Higgsfield.** One `ToolSearch` for `models_explore`, `generate_image`,
`generate_audio_batch`, `generate_video_batch`, `list_voices`, `jobs_wait`,
`show_generation_by_ids`, `remove_background`, `media_upload`, `media_confirm`,
`sandbox_exec`, `balance`. Uploads as in Goal. Photos and tracks: if a file already has a `media_id` (uploaded earlier in this chat, a Katana input, a generation ID), use it and never ask again. If you can read the file yourself (a local path), upload it with `media_upload` + PUT. Only when the photo exists solely as a chat attachment you cannot read as bytes, call `media_upload_widget` (image or audio) once, saying in one line that the attachment has to go into Higgsfield first; never ask for it again after that. Keep working while jobs render.

**Sandbox facts.**

- Seedance returns **HEVC 10-bit** (4:3 = 1664×1248, 24 fps); `remove_background` fails on it silently: transcode to H.264 8-bit yuv420p, upload, then cut out. Do it at once for every clip.
- Sandbox Whisper: `WhisperModel('small', download_root='/opt/whisper-models', local_files_only=True)`.
- Seedance plays the timed routine ~1.5–2× slower than prompted: gesture log from the clip, never the prompt.
- Matte fallback if `remove_background` fails or bleeds: your own person matte from the original against the white room; last resort, keep giant letters and starburst clear of the body and tell the user.
- Fonts: face words and closer = a black italic grotesk ("Helvetica Neue" Black/Heavy Italic or "Arial Black" italic), closer second part = light 300 upright; arc letters = an upright bold grotesk ("Arial Black"/"Helvetica Neue" Bold); tag = bold sans. If the sandbox lacks them, use the closest. Render all text yourself.

**Generations.** Don't show credit estimates or ask for budget approval; run the batches:
(1) heroine `soul_2` ×4 (or `seedream_v5_pro` ×4 normalization), friend `soul_2` ×4, voice
`seed_audio` ×4 · (2) `seedream_v5_pro` ×4 per extra look · (3) `seedance_2_5` A1 10 s, B1
10 s (+ C1 10 s for 3 looks, A2 10 s for 1 look with 2 phrases), F1 5 s with a friend ·
(4) `remove_background` per phrase clip. Regenerate failed clips one by one; never loop: if a
clip keeps failing, stop and tell the user.

## 3. Reference, chant, plan (gate 1)

1. Study the reference frame by frame (contact sheets per shot, §9 cut list). User reference: upload it, get duration and fps, study it the same way, run Whisper + onset detection in the sandbox (words, timestamps, BPM).
2. Give each chant word a **role** (meaning over shape):

| Role | Reference (default) | YAONG example | On screen (reference) |
| --- | --- | --- | --- |
| **call** (opens, repeats) | NYAN | YAONG | pale lilac starburst behind her, letters arced around the head behind her; music-note doodles on the first call; "*" on the nose on the repeat |
| **count** words | ICHI, NI, SAN | HANA, DUL, SET | 1st: face word typed on; middle (index N//2, the reference's NI): **giant letters behind her**, no face word; last: face word pops in whole |
| **closer** | ARI·GATO | SARANG·HAE | lightning slashes + typewriter, first part bold italic, second thin |

Limits: call 3–6 letters; giant ≤ 3 letters (5:4/4:3), ≤ 2 (9:16); face words ≤ ~7; closer
split at a syllable (ARI + GATO, SARANG + HAE, LOVE + YOU). Over a limit: propose a
shorter variant, don't shrink fonts. Ready-made: ja NYAN / ICHI NI SAN / NYAN / ARI·GATO
(default) · ko cat YAONG / HANA DUL SET / YAONG / SARANG·HAE · ko bunny KKANG / HANA DUL SET /
KKANG / JOA·HAE · en MEOW / ONE TWO THREE / MEOW / LOVE·YOU.

3. Theme matches the call word (cat: nyan/yaong/meow, bunny: kkang-chong, puppy: wang/woof…; §9).
4. Invent a tag replacing the reference caption (never reuse the reference's handle; the YAONG example used `nabi.cam*`, Nabi being a typical Korean cat name).
5. Compute the grid (§9); one-paragraph plan: words → roles → beats, looks, friend, aspect, duration.
6. Use the defaults (2 looks, friend in the B&W bridge and at the phrase-2 edge, Japanese chant, 5:4 900×720 unless the platform needs 9:16) for anything the user didn't specify; ask only if the request can't be done without an answer.

✅ Gate: every word has a role within its limit; grid adds up to the duration.

## 4. Heroine, friend, voice (in parallel)

Launch together: heroine, friend (if any), voice (`generate_audio_batch`, 4 presets,
unless the user brought a track). Keep the reference's **frame** (fictional new person, phone
front-camera selfie at arm's length, white backstage room with a pale lime-green shelf high on
the wall and mop handles in the corner, bright airy light, candid vlog); swap person, outfit,
pose. 9:16: "vertical phone selfie, chest-up framing with headroom". Opening pose = the theme's
**call gesture** (§9).

The prompt templates below are kept verbatim from the YAONG worked example. Where they say
"overexposed daylight, lifted creamy whites", the reference's whites are bright but cool-neutral
(≈ `#f7fafc`), not creamy: the §10 grade match takes care of it.

**Heroine (Soul):**

```
Phone front-camera selfie photo at arm's length of a fictional 21-year-old Korean K-pop idol girl in a bright white backstage waiting room. Long straight glossy jet-black hair past the shoulders with soft wispy face-framing side bangs, a small silver rhinestone hair clip above one temple. Pale luminous glass skin, rosy pink blush across the cheeks and nose bridge, sparkly aegyo-sal under the eyes, soft brown eyeliner with a small wing, glossy pink gradient lips. She wears a black halter top with thin white horizontal stripes, layered chunky silver chain necklaces, a chunky glossy brown tortoiseshell bangle on one wrist and a translucent pink bangle on the other, silver rings, long almond nails with white chrome nail art. She makes cute cat-paw hands under her chin, head tilted, sweet closed-mouth smile, looking straight into the lens. Background: plain white walls, a pale lime-green shelf near the ceiling, two mop handles leaning in the corner. Soft overexposed daylight, lifted creamy whites, pinkish skin glow, slight phone-camera softness, candid vlog snapshot.
```

**User photo normalization (seedream_v5_pro i2i, instead of Soul):**

```
Keep the exact same person from the reference photo: identical face, facial features, eyes, hair color and hairstyle. Recreate the shot as a phone front-camera selfie at arm's length, chest-up framing, looking straight into the lens, cute cat-paw hands under her chin, head slightly tilted, sweet smile. Keep her outfit from the photo. Setting: a bright white backstage waiting room with plain white walls, a pale lime-green shelf near the ceiling, two mop handles leaning in the corner. Soft overexposed daylight, lifted creamy whites, rosy pink blush, pinkish skin glow, slight phone-camera softness, candid vlog snapshot. No text, no logos.
```

**Friend (Soul).** Hair and outfit must contrast with the heroine's, or they blur together in
B&W. (The reference's friend wears a black-and-white striped top in the bridge and a pink
graphic top at the phrase-2 edge; the template's lilac cardigan is the remake's contrast choice.)

```
Phone front-camera selfie photo at arm's length of a fictional 20-year-old Korean girl with an idol-trainee look in a bright white backstage waiting room. Long layered ash-brown hair with see-through bangs and two thin front braids, a small pink star hair pin. Fair dewy skin, peach blush, puppy eyeliner, glossy coral lips, small silver hoop earrings. She wears a white baby tee with thin pink horizontal stripes under an open lilac fuzzy knit cardigan, a delicate silver necklace. Playful peace sign near her cheek, cheeky grin with teeth, looking straight into the lens. Background: plain white walls, soft overexposed daylight, lifted creamy whites, slight phone-camera softness, candid vlog snapshot.
```

**Voice (seed_audio).** Chant in the language's own script, "!" and "~" between words so the
TTS pauses and words cut cleanly. Default (reference, Japanese):
`にゃん~! いち! に! さん! にゃん~! ありがとう~!`. English: `Meow~! One! Two! Three! Meow~! Love you~!`.
YAONG example (Korean):

```
야옹~! 하나! 둘! 셋! 야옹~! 사랑해~!
```

✅ Before showing: check every variant; drop those with camera UI, text, extra people,
mutant hands, or (user photo) a drifted face; listen to every take (all words present).
Pick the heroine, friend and voice yourself (closest to the reference) and go on; mention
the picks in one line.

**Extra looks** once the heroine is picked: `seedream_v5_pro` i2i from her, ×4 per look. Look B
(YAONG example template; the reference's look B is likewise a brown fur coat):

```
Keep the exact same girl from the reference photo: identical face, eyes, makeup, rosy blush, long straight jet-black hair with side bangs and the silver hair clip. Change only her outfit and pose: she now wears a big fluffy caramel-brown faux-fur coat worn open over a white ribbed tank top, a thin silver chain necklace, long silver threader drop earrings, silver rings, white chrome almond nails. Pose: both hands raised near her cheeks making small finger hearts, playful open-mouth smile, looking straight into the lens. Same bright white backstage waiting room with plain white walls and two mop handles leaning in the corner, soft overexposed daylight, lifted creamy whites, phone front-camera selfie at arm's length, slight phone-camera softness. No text, no logos.
```

Describe the heroine's real hair and accessories. Pick the variant yourself (face and
bangs match, planned outfit color) and tell the user. Looks must differ clearly in color
and texture: phrase 2 must read as a new outfit at a glance (reference: monochrome striped
halter → brown fur).

## 5. Track

No Higgsfield song model with vocals (`sonilo_music` is games-only), so the reference song is
replaced by a coded beat on the reference's grid. `B = 60/BPM`; beats count inside each phrase;
`L = N + 5` beats per phrase (§9).

**Reference audio, measured** (onsets + Whisper): 102 BPM, B ≈ 0.5875 s, 2 phrases of 8 beats.
Chant onsets: phrase 1 NYAN 0.05 · ICHI 0.60 · NI 1.20 · SAN 1.80 · NYAN 2.39 · A-RI 2.84 → GA
2.99 s; phrase 2 NYAN 4.74 · ICHI 5.34 · NI 5.94 · SAN 6.49 · NYAN 7.08 · A-RI 7.53 → GA 7.68 s;
beats 5–7 of each phrase carry no chant. The music drops to near silence for ~0.1 s just
before most chant words (≈0.40, 2.29, 2.74, 4.64, 5.09, 5.54, 6.98, 7.43 s), so each word
punches in. Bright flash hits on the blow-out cuts (≈0.65, 1.80, 2.99, 5.34, 6.49, 7.68 s), one
in the bridge (≈4.14 s) and one before the outro blur (≈8.88 s). Audio ends 9.52 s.

**A. Coded beat (default)**, 48 kHz stereo, on the §9 grid.

- **Chant words**: boundaries from the **chosen take** itself (e.g. its spectrogram), never another take's. Slots `call1`, `call2` (two call takes alternating: phrase 1 call1→call2, phrase 2 call2→call1; one take = both), `c1…cN`, `closer`. Each: trim, **+2 semitones, same length**, high-pass 140 Hz, mono, gain 0.95, 2 ms in / 30 ms out fades, reverb send 0.16 (phrase 1) / 0.22 (later). Beats: call 0, counts 1…N, call N+1, closer's stressed syllable on N+2 (its first syllables start ~0.25·B earlier, like A-RI before GA); phrase 1 starts 0.05 s into the file. Start each word a **pre-roll** early so the attack hits the beat (call1 0.02, call2 0.03, closer 0.07, others 0.02 s). Mute the music for ~0.1 s before the call repeat, the closer and every phrase start (reference dropouts). A missing word is a blocker.
- **Harmony**: 102 BPM; chord per 2 beats cycling Fmaj7 `[65,69,72,76]` → Em7 `[64,67,71,74]` → Dm7 `[62,65,69,72]` → Cadd9 `[60,64,67,74]` → B♭maj7 `[58,62,65,69]`; bass roots MIDI `41 40 38 36 34`.
- **Toy-piano melody** doubling the chant, `[beat, MIDI, len s]` (len 0.32): `[0,81] [0.5,77]`, count k on beat k at MIDI `84 86 88 89 91 93 95 96`[k−1] (0.8 s on the last), then `[N+1,84] [N+1.5,81] [N+1.75,81] [N+2,79] [N+2.5,77,0.8]`. YAONG example (134.4 BPM, its own 10-beat grid with a jump-repeat beat): `[0,81] [0.5,77] [1,84] [1.5,81] [2,86] [3,88,0.8] [5,84] [5.5,81] [6,81] [6.5,79] [7,77,0.8]`.

```
Kick   sine 48+120e^(-30t) Hz 0.24 s + click; every beat 0.9 (first break beat 0.7)
Clap   band-passed noise ~1.3 kHz, triple burst; backbeats 0.45
Hats   noise >7.5 kHz; eighths 0.07 on / 0.13 off; open hat off-beat of beat L-3; break: 16th roll 0.03->0.06
Bass   square LP 700 Hz + sine sub 0.12 s; eighths root / root+12; 0.30 (break 0.18)
Plucks chord tones, triangle+square LP 3.2 kHz; eighths weighted [1,0,0.7,0.85] x 0.085
Bells  chord +12, 16th arps, 0.6 s, pan +-0.45; 0.035; not on last break beat
ToyPn  sine + 2nd/3rd harmonics, light vibrato; melody 0.07
Pop    sweep 260+1300e^(-60t) Hz 70 ms; 0.10 on every chant word but beat 0; 0.14 outro
Sparkl bells MIDI 96 98 100 103 105 108 110, 18 ms apart; 0.05 each phrase start, 0.06 outro
Whoosh noise BP 300<->7500 Hz; up L-2.5..L-2 (0.12); up 1.2 beats into later phrases (0.14); down outro->end (0.10)
Break  last 2 beats of each phrase: kick on first only, no claps/plucks, quiet bass, hat roll
Outro  kick 0.85, bass F 0.3 s, pluck [65,69,72,77] 0.1, sparkle, pop, down-whoosh
Bus    room reverb send; music ducks 0.35e^(-14 t_since_kick) (not vocals/SFX/reverb); 0.12 s end fade,
       soft clip tanh(1.1x)/1.1; master loudnorm=I=-13:TP=-1:LRA=7, 48 kHz 16-bit
```

**Transition SFX** (cue per cut from §9, 5–10 ms early): `flash` = high-passed noise +
1.8→7 kHz sweep, 0.16 s, 0.17 (face blow-outs) · `flashBig` = same 0.5 s, 0.22, more reverb +
up-whoosh over the 0.18 s before (closer) · `white` = flash + bells MIDI 100, 107 (20 ms apart)
(white frames) · `mosaic` = glitch (square jumping 0.9–4.4 kHz every 12 ms, 90 ms, 0.045) (magenta
mosaic) · `shutter` = two clicks 55 ms apart (bridge cut and bridge blur) · `mag` = sparkle 0.03.

**B. User's track**: upload, Whisper (word timestamps) + onset/beat detection in the
sandbox; every shot starts on a detected onset or beat (§9); no voice generation; only
the SFX at gain 0.35 over the excerpt (no normalization, 0.15 s fade-out, limiter 0.95).
Never cut or time-stretch the user's track without asking.

✅ ≈ −13 LUFS (A); every word on its beat ±30 ms (check against the grid and the dry take: Whisper over the mix merges words); no clicks at word boundaries.

## 6. Video, Seedance 2.5 (all clips in one `generate_video_batch`)

Parameters in §2; aspect = output aspect (4:3 for the 5:4 default); keep whatever size comes back.

| Clip | When | Length | References | Content |
| --- | --- | --- | --- | --- |
| A1 | always | 10 s | @image1 = look A | counting routine, twice |
| B1 | 2+ looks | 10 s | @image1 = look B (+ @image2 = friend at the edge) | same in look B |
| C1 | 3 looks | 10 s | @image1 = look C | same |
| F1 | friend | 5 s | @image1 = heroine look A, @image2 = friend | duet for the B&W bridge |
| A2 | 1 look, 2 phrases | 10 s | @image1 = look A | second take, other framing/energy (phrase 2 mustn't reuse phrase 1 frames) |

**Gesture routine** (reference): one timed line per word, ~0.4 s each: call = theme call
gesture (§9; cat-paw hands under the chin, head tilt); count words = both hands raised beside
or above the head with open palms, changing each count (1st: palms up by the head; giant
count: hands on top of the head like ears; last: hands waving beside the head); closer =
pointing at / finger heart to the lens; then "repeats the same routine with a little more
energy and ends with a wink and a finger heart". Too many words: two clips per look.

**A1 (YAONG example template, verbatim):**

```
Realistic phone front-camera selfie video at arm's length of the adult woman from @image1, a K-pop idol in her twenties: same face, long straight jet-black hair with side bangs, silver hair clip, black-and-white striped top, chunky silver chain necklace, brown tortoiseshell bangle, pink bangle, white almond nails. Bright white backstage waiting room: plain white walls, a pale lime-green shelf high on the wall, mop handles leaning in the corner. Soft overexposed daylight, lifted creamy whites. Handheld micro-wobble, chest-up framing, her hands always visible near her face. She does a cheerful counting hand routine for a fan video, mouthing 'yaong, hana, dul, set, yaong, saranghae' to an upbeat rhythm.
0.0-0.4s: cat-paw hands under her chin, head tilt.
0.45-0.85s: one finger raised beside her cheek.
0.9-1.3s: two fingers.
1.35-2.2s: three fingers, then both open hands raised beside her head, waving side to side.
2.25-2.65s: cat-paw hands again with a small nose scrunch.
2.7-3.6s: finger heart toward the lens, then a cheerful wave.
3.6-4.5s: laughs, leans closer to the lens, tucks hair behind her ear.
4.5-9.0s: repeats the same routine with a little more energy and ends with a wink and a finger heart.
Natural, friendly, understated expressions. One continuous take, no cuts, no on-screen text.
```

Where the reference differs from this template: the mouthed words are the chant in use
(default 'nyan, ichi, ni, san, nyan, arigato'), and the count lines (0.45–2.2s) are the
reference's raised-hands gestures above, not finger counts. Swap those lines; keep the rest.

**B1 with a friend**, add:

- "Her friend from @image2 (…) stands just behind her at the right edge of the frame, half cropped by the frame edge, swaying along";
- "laughs and glances at her friend" in the 3.6–4.5s line.

No friend: drop these. Friend always on the **right** (tracking picks the left face), as in the
reference's phrase 2.

**F1 (YAONG example template, verbatim):**

```
Realistic phone front-camera selfie video at arm's length in a bright white backstage waiting room with plain white walls and mop handles leaning in the corner. The girl from @image1 (same face, long straight jet-black hair with side bangs, silver hair clip, black halter top with thin white stripes, chunky silver chain necklace, brown tortoiseshell bangle) is on the left of the frame. Her friend from @image2 (same face, ash-brown hair with thin braids, lilac fuzzy cardigan over a pink-striped white tee) leans in from the right side into the selfie, cheek close to the girl's shoulder. Both giggle at the lens; the girl points at her friend and laughs, the friend makes a peace sign, then both put their hands together into one shared heart toward the lens. Handheld wobble, soft overexposed daylight, lifted whites. Natural, warm, understated laughter. One continuous take, no cuts, no on-screen text.
```

Always fill in the real appearance (hair, outfit) from the chosen images.

**Moderation, what reliably breaks Seedance**: any song as `audio_references` +
`generate_audio: true` (all 4 such jobs returned "nsfw"); "girl" without "adult woman in
her twenties"; "blows a kiss"; "slipping off her shoulders"; "glowing pink-flushed skin".
Keep actions wholesome. Without `declined_preset_id` the first submit returns an "IN THE
DARK" preset recommendation instead of a job. Lip sync is loose (face words hide it):
tell the user up front.

While Seedance renders: cut the voice, build the beat and the renderer skeleton.

✅ Per clip: face matches, hands intact, gestures readable, no text, no cuts, an edge friend
doesn't cover the heroine, F1 heroine on the left. Regenerate only a failing clip.

## 7. Gesture log and in-points

Watch each clip closely and log what she does when (source s). In-points
come **only from the log**: gesture must match word. Per phrase N + 3 in-points (call,
each count, call again, closer); a non-last phrase also 2 bridge in-points (heroine alone, then
the F1 duet, or the heroine alone laughing); the last phrase's closer runs on to the end
(pick a closer in-point with ≥ 1.7 s of usable, still-cute footage after it).

YAONG example log (its A1/B1 clips): A1 paws 0–0.6 · one finger 0.75–1.0 · "two" 1.5–1.75 ·
three 2.0–2.25 · open palms 2.75–3.25 · cheek heart + wink 3.5–3.75 · heart 4.0–4.5 · waving
4.75–5.75 · laugh, hair 6.0–6.5 · heart 7.0–7.5 · heart + wink 8.5–9.75. B1 paws 0–1.75 · one
finger 1.75–2.75 · one + "two" 2.75–3.25 · hands up 3.5–4.25 · paws 4.75–5.5 · heart 5.75–6.25 ·
points at camera 6.5–7.0 · turns to friend 7.25–7.5 · finger hearts 8.0–9.75.

Missing gesture? Take the closest cute moment (laugh, head tilt), let graphics carry the
word; don't regenerate for one shot.

✅ `in + shot length` within the clip; no two consecutive shots start on nearly the same frame (a jump cut needs a visible pose change).

## 8. Cutout, mattes, face tracking

1. `remove_background {media_type: "video"}` on every transcoded phrase clip (not the bridge). Result: person on **black, no alpha**.
2. Work from source frames at **native resolution** (the framing crops in). Build a clean alpha matte per frame from cutout and original (e.g. ratio of cutout to original luminance, thresholded, with closing for dark-hair holes); mattes stay frame-aligned at native fps (24; an ffmpeg color source defaults to 25 and drifts).
3. Track per source frame: eye centers (→ midpoint, distance d, roll a), mouth, nose, by any method the sandbox offers. Face box only: center x, center y − 0.08·H, d = 0.42 × box width, a = 0. Fill gaps and smooth so framing and words never jerk. Friend in frame: track the left, larger face. **No detector**: hand-estimate eyes every ~0.25 s and interpolate; if unreliable, static centered crop with fixed words and tell the user the face tracking is off.

✅ Matte on 2–3 frames: no holes in hair, friend not in the heroine's matte. Face found
on **≥ 95 %** of frames; a long gap (hands over the face) jerks the framing: pick another
in-point.

## 9. Assembly

Render at output size, 30 fps, with the reference's **18 fps cadence**: every 5 output
frames show 3 distinct images (hold pattern 2, 2, 1), graphics included. Pixels for 900 wide
(scale W/900). `D` = on-screen eye distance (reference ≈ 80–100 px at 900 wide); `(x, y)` in D
from the eye center, rotating with the head (+y down); `u` = s into the shot; easeOut =
1 − (1 − t)³.

**Reference cut list** (30 fps frame → s): 0 call · 19 (0.633) ICHI · 37 (1.233) NI giant ·
55 (1.833) SAN · 72 (2.400) white → call again · 90 (3.000) closer · 117 (3.900) B&W bridge ·
147 (4.900) white → phrase-2 call · 164 (5.467) ICHI · 179 (5.967) NI giant · 197 (6.567) SAN ·
214 (7.133) white → call again · 232 (7.733) closer · 270 (9.000) blur-out · 282 (9.400) one
white frame, end. Cuts land 1–2 frames after the chant onset (phrase-2 call and ICHI 4–5).

**Grid.** Phrase = call (beat 0) · counts (1…N) · call again (N+1) · closer (N+2, cut on its
stressed syllable) · tail; `L = N + 5` beats (reference 8 beats = 4.70 s). No jump-repeat
shot. Non-last tail: closer holds 1.5·B, then the B&W bridge to the next phrase (reference
3.90–4.90 s). Last phrase: the closer runs on, blur-out over the last ~0.4 s, one white
frame. `dur ≈ phrases × L × B + 0.12 s` (reference 2 phrases = 9.52 s). One clip per phrase
(A, B, C…; one look: A2 or A1's 2nd half). User track: N + 3 starts per phrase on
onsets/beats, closer and bridge proportions as above, B from detected BPM.

**Framing** (from the reference): medium close-up, chest up with raised hands in frame; eye
distance `ld·W` with ld 0.09–0.11; eye line at `ly·H`, ly ≈ 0.33 (call) · 0.35–0.42 (counts) ·
0.46 (closer); eye center x ≈ 0.42–0.50·W. Head tilt stays natural (no leveling, lockRot 0);
keep the source's handheld motion, smoothed. Gentle push-in through each shot (≈ 1 → 1.06).
Never show the source edge (scale up, shift inward). 9:16: `ld × 900/W`, ly −0.08.

**Phrase template** (reference times phrase 1 / phrase 2):

| Shot | Effects | Layers | SFX |
| --- | --- | --- | --- |
| Call (0) · 0.000–0.633 / 4.900–5.467 | phrase 1 opens straight into magenta (no white); later phrases: 2 white frames, then magenta. Magenta: mosaic ~30 → 4 px over the first 0.1 s, magenta tint fading over ~0.35 s | starburst + arc letters behind her · halo · 3 doodles: beamed note, "ɜ" squiggle, note, in a diagonal from her chin down-right · tag (phrase 2+) | mosaic / white |
| Count 1, face word typed · 0.633–1.233 / 5.467–5.967 | blow-out in with pixel blocks, decays over ~0.35 s · word typed letter by letter (~2 frames/letter: I, IC, ICH heavy) · last ~0.27 s: blur pulse + thin dark frame; the finished word turns bold first letter + thin rest (I + CHI); vertical smear on the last 2 frames | stairs · halo · tag (phrase 2+) | flash |
| Count, giant (index N//2) · 1.233–1.833 / 5.967–6.567 | blur-in ~0.1 s continuing the pulse | giant letters behind her, background washed mostly white · stairs · halo · no face word | — |
| Last count, face word whole · 1.833–2.400 / 6.567–7.133 | blow-out in with pixel blocks, decays over ~0.33 s · word pops in whole, heavy italic | giant letters stay behind her · stairs · halo | flash |
| Call again (N+1) · 2.400–3.000 / 7.133–7.733 | 2 white frames (phrase 2: 1), then magenta as above, ~0.3 s | starburst + arc letters · halo · "*" on the nose (phrase 1) · no doodles | white |
| Closer (N+2) · 3.000–3.900 / 7.733–9.400 | strong blow-out with pixel blocks, decays over ~0.45 s · slashes over the first ~0.4 s · typewriter from ~0.1 s, 0.05 s/letter (all 7 letters by ~0.5 s) | halo · tag (phrase 2+) | flashBig |
| *Non-last:* closer end · last ~0.2 s | blur rising into the bridge cut | — | — |
| Bridge · 3.900–4.900 | B&W (below) · letterbox bars slide in over the first 3 frames · heroine alone ~0.33 s → blur transition ~0.17 s → duet with the friend ~0.5 s | tag beside the face | shutter |
| *Last:* closer tail · 8.6–9.4 | words gone after ~0.9 s · clean face ~0.4 s · blur-out ~0.4 s with zoom-out and upward drift · one white frame | halo | flash before the blur |

Tag: only in the bridge in phrase 1; on every shot from phrase 2 on.

**Palette** (change together; white stays every word and doodle fill): halo and stairs
`#f7cbfd` · giant fill `#f8d8fc`, flat, no stroke · starburst fill `#f5e7fb`, thin lilac
edge · word/doodle outline thin lilac-grey · magenta wash: shadows/mids toward `#c34ca7`, highlights
toward `#f6d2ea` · white frames `#f7fafc` (not pure white). YAONG example palette: outline
`#c98be0`, stairs `#f6c6ef`, burst `#efdcf8`.

**Words** (white fill):
- Arc letters (call): upright bold grotesk, white with a thin (~2 px) lilac-grey outline, each ≈ 1.45·D tall (≈ 130 px at 900 wide), set tangent to an arc of radius ≈ 2.9·D around the head from the left at eye level, over the top, to the right at eye level; drawn **behind** her cutout (the reference's last N hides behind her shoulder); staggered pop-in during the magenta.
- Face word: centered on the nose ≈ 0.6·D below the eye line, cap height ≈ 0.7·D (≈ 60 px), heavy italic, soft grey-lilac drop shadow, no hard stroke; rotates with the head.
- Giant (5:4/4:3): the count word in huge flat italic heavy letters reaching from the top edge to below the shoulders, spread across the frame behind her (only fragments show around her body). 9:16: row 0.15–0.85·W at 0.2·H, size min(0.95·W/n × 1.25, 0.2·H).
- Typewriter (closer): at nose level ≈ 0.35·D below the eye line, centered on the face, cap height ≈ 0.65·D, ≈ 4.3·D wide for 7 letters; first part bold italic, second part thin upright; letters appear in place.
- Tag: white bold ~28 px, dark soft shadow, no stroke; on the outfit near the bottom (x 0.35–0.6·W, y 0.88–0.95·H), rotated per shot anywhere from −60° to 0°; bridge: ~22 px, 0.8 opacity, beside the face, with the "*".

**Doodles**: only on the first call of each phrase, 3 of them (beamed note, "ɜ" squiggle,
single note), white fill with a thin lilac outline, ≈ 0.6–0.8·D, popping in
`easeOut(v)·(1 + 0.25·sin πv)` over 0.1 s, tracked with the face. "*" on the call repeat:
white, ≈ 0.6·D, on the nose tip. No other stickers, no drawn ears, whiskers or blush.

| Theme | Call gesture (Seedance) | Count gesture | Nose mark |
| --- | --- | --- | --- |
| cat (default) | cat-paw hands under the chin | hands raised beside the head (as ears on the giant count) | "*" on call repeat |
| fox | finger "fox" hands by the cheek | same | "*" |
| bunny | two fingers up on top of the head as bunny ears | same | "*" |
| bear | fists by the cheeks | same | "*" |
| puppy | paws at chest height, head tilt | same | "*" |
| none | finger heart | same | "*" |

**Back layers.** Starburst: center ≈ (0, 0.4), R ≈ 3.5·D, 0.6→1 over 0.08 s then slowly
growing, ~15 spikes (outer 0.86–1.2·R, inner 0.5–0.62·R), flat pale fill with a thin lilac
edge, slow rotation. Pixel stairs (all count shots): 3–5 squares 35–45 px in a diagonal
staircase at the top-left, one or two rotated 45°. Halo (all colour shots): her matte offset
≈ +10/+6 px, dilated to a ~12 px band. Order: plate → starburst → arc letters → giant → stairs
→ halo → cutout → face words/doodles → transitions → tag → flashes. No grain.

**Transitions** (every cut gets one; strongest on call and closer):
- **Blow-out / flashlight in** (d 0.33–0.45 s): `k = (1 − u/d)^1.4`; brightness 1 + 1.35k (cap: eyes and lips never burn out; in the reference eyes stay grey and lips pink while the skin goes white), contrast 1 + 0.3k, saturation 1 − 0.45k (hair stays dark); k > 0.3: **pixel blocks**, white 25–40 px squares over the face and hair edge, re-rolled every 2 frames.
- **Magenta**: mosaic ~30 → 4 px over 0.1 s, then a fading magenta tint (shadows `#c34ca7`, highlights `#f6d2ea`), gone by ~0.35 s.
- **White frames**: `#f7fafc` for 2 frames (1 on the last call repeat).
- **Blur pulse**: rising blur + **thin dark frame** (≈ 5 px grey inset border) over ~0.27 s, vertical smear on the last 2 frames, then blur-in ~0.1 s into the next shot.
- **Slashes**: 2–4 tapered white blades with a lilac edge crossing the face diagonally (low left → high right) around nose level, over the first ~0.4 s of the closer.
- **B&W bridge**: grayscale with a faint cool-lilac tint, highlights ≈ (208, 206, 218), blacks crushed to 0; equal black bars top and bottom, each 11.7 % of H (84 px at 720).
- **Blur-out** (end): blur rising over ~0.4 s with a zoom-out and upward drift, then one white frame.

✅ Before the full render, on a mid-shot still of every shot, side by side with the reference
frame of the same role: face word readable, not cut · doodles whole · arc letters off the
face · **blow-out never burns out eyes and lips** (brightness ≤ 1 + 1.35·k) · tag readable ·
friend visible where planned.

## 10. Final

1. One H.264 MP4 (yuv420p, BT.709, web-playable) with the final track (beat + chant + SFX, or song + SFX), 30 fps unless the platform needs 24/60. Final grade: match the reference's look by per-channel distribution (histogram) matching of each shot's plate to the reference frame of the same role (call f10, count f25, giant f50, last count f64, call repeat f84, closer f100/f250, bridge f135, phrase-2 call f160, phrase-2 counts f172/f190/f205), graphics excluded. Outcome to check: whites peak ≈ 248–250, cool-neutral (white frames `#f7fafc`); hair blacks near 0–15; median luma ≈ 190; rosy skin mids ≈ (177, 130, 123); mean saturation (max−min) ≈ 31 on colour shots. Lighter / moodier variants: shift the median ± 10.
2. Compare the final with the reference at the cut-list frames: cuts, transitions, doodle count, letter sizes, framing and grade read the same unless asked otherwise.

✅ Final QA (watch + listen): duration and size as planned · every word on its shot
and caption · every cut has its transition · no framing jerks (eye-center jitter < ~3 px
median) · B&W bridge works, tag readable · blur-out ending with one white frame, no audio click.

## 11. Delivery

Deliver **one final MP4 only**, uploaded from the sandbox: `media_upload` → PUT (HTTP
200) → `media_confirm` → show its confirmed URL or inline player once. QA sheets,
comparisons, intermediates, audio, generation IDs and project files stay internal; a
sandbox path is not a delivery. Save versions v1, v2…; never overwrite.

| Feedback | Fix |
| --- | --- |
| more / fewer doodles | doodle count on the call shots |
| friend not visible | ld 0.08–0.09 on her shots |
| words or letters cut off | lower ly; 9:16 vertical offset |
| transitions too weak | longer blow-out d, more pixel blocks, 2 white frames before every magenta |
| face burned out | lower blow-out k (cap 1 + 1.35·k) |
| gesture ≠ word | move that in-point via the gesture log |
| camera too static | stronger push-in, keep more handheld motion |
| grade too pale / dark | shift the matched median; re-check against the reference frames |
| other colors | palette (§9) |
| other animal | theme + call gesture in the Seedance prompts |
| other words / language | §3 roles → new voice take → recut words → rebuild grid, shots, track; clips stay if the gesture count still matches |