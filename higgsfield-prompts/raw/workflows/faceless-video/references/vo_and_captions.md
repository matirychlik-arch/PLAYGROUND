# vo_and_captions.md — fixed-window ElevenLabs voiceover + subtitle handoff

## Voiceover — text2speech_v2 / ElevenLabs · ONE LINE PER BLOCK

- **One narrator voice for the whole video — the USER picks it in the voice library
  widget at intake** (`kind:"entity"`, `entity:{type:"voice"}`; no generated audition
  samples), with a one-line channel recommendation posted next to the widget:
  **History → Arthur or Callum · Kids → Remy · Explainer → Remy, Roxie or Cillian ·
  Picture Story → match the tone.** Those names are a HINT FOR THE USER only. **When
  nothing was picked — hands-off, an empty widget, a voiceless brief — the voice is the
  PINNED PAIR `d8ba9f14-8a24-44db-932b-99e16c45bd32` / `preset` (Cillian), on every
  channel type, with no name lookup.** Custom (element) voices work as well as presets. Record the picked pair and
  use the SAME `voice_id`+`voice_type` on EVERY line — never let lines come out in
  different voices; a take that comes back in a different timbre = `failed` → regenerate
  with the locked pair.
- **Intonation & mood live in the SCRIPT, not in the voice:** fit delivery to the channel
  type + topic (sombre topic → measured wording, fewer gags; playful → lighter lines,
  more performed brackets). The voice never changes mid-video.
- **Kids call-and-response:** the narrator addresses characters and the viewer by name
  ("Say hi to Masha!", "Can YOU count the apples?") and the video stages the visible
  reaction (see kids-styles.md). Questions go at the END of a line — the block boundary
  IS the answer beat, and the next line opens with the payoff ("That's right — three!").
  Never leave a ≥0.8s pause inside a line for the answer. Narrator-spoken sound-words
  ("whoosh!", "ding!") and catchphrases count as words in the Kids 17–21 budget — they
  are seasoning, not filling: at most ONE per line (LINE HYGIENE below).
- **One spoken line per block** (block N → `voiceNN.wav`). No timecodes, no big continuous
  chunk, no `adelay` juggling. One line = one 10s scene → perfect sync by construction.
- **Line prompt format — delivery direction, not pacing:** send every line as
  `[ {DELIVERY}, {optional block mood}, starts speaking immediately] [00:00-00:09] {text}`.
  {DELIVERY} is ONE direction phrase composed once for the whole video to fit the channel
  type + topic (e.g. `wry conversational explainer, neutral accent, bright dry timbre,
  lively pace`) and repeated VERBATIM on every line — that keeps the timbre consistent
  across blocks. {optional block mood} is 2–4 words for this block's beat (`a bright
  knowing reveal`, `hushed conspiratorial`). `starts speaking immediately` kills the
  leading pause. ElevenLabs ignores the `[00:00-00:09]` window for pacing.
- **Measured retries:** the initial word band is not an unbreakable retry floor.
  After converted WAVs exist, run `${HF_WORKFLOWS}/faceless-video/scripts/measure_narration_takes.py`
  with `--script script_manifest.json --voice-dir work/voices --duration-seconds {requested_seconds}`
  in that same call. For measured overlong slots only, follow `recommended_words`
  and revalidate with the cumulative `--duration-retry-blocks` set (17-word floor
  per full block). Passing takes are immutable. Soft 7.2–7.8s is accepted only
  after one retry: pass the identical `--accept-soft-blocks N,...` list to the
  measurement script and `finish_video.sh` (or `assemble_final.sh`). This applies
  only to full 10-second narration blocks; other blocks retain the normal floor.
  A hard miss after three attempts is a failure, not a deliverable.
- **Length: each line FILLS the 10s block — target ~7.8–9.5s of speech** (the assembler
  CENTRES the line's SPEECH in its window, ignoring the file's edge silences). With the
  timecode format uses **20–23 words, at most TWO sentences**, comma-light, one
  flowing clause where you can. Word count is the only length lever. An over-budget
  line does not fail loudly: the voice just RACES. A 41-word five-sentence line
  containing "August 15th, 1977" both came back as auctioneer reads with a dead tail.
  **Write every number as words** ("nineteen seventy-seven", "the fifteenth of August"):
  digits, dates and abbreviations are spoken far longer than they are written and blow
  the budget invisibly. Target 7.8–9.5s; soft 7.2–7.8s only after one retry, hard reject outside 7.2–9.5s,
  and **no internal pause ≥0.8s** — the assembler flags pausey takes (WARN with the pause
  length); rewrite flowing and regenerate, don't ship stalls. Kids run hotter: **17–21
  words** with an EXCITED {DELIVERY} cue and bounded performed
  brackets (`references/kids-styles.md §Kids voice pace`) — warmth = word choice, not pauses.
  `validate_motion_script.py` enforces the initial bands (20–23, Kids 17–21), the measured per-slot retry exception, the
  two-sentence cap and the no-digits rule.
  **MEASURE THE PACE, NOT ONLY THE LENGTH:** run
  `measure_narration_takes.py` on every wave against the exact manifest text —
  `rate=RUSHED` (over 2.9 words/sec) is a REWRITE even when `speech=` sits inside the
  window, because a rushed take is the "tarratorit" complaint in its pure form.
  Convert the returned MP3 with the exact reverse-trim/fade recipe in
  the loaded `narration` workflow, then `ffprobe` it. **If speech exceeds 9.5s → rewrite shorter.
  NEVER `atempo` /
  speed-up / slow-down / pitch-shift** to fit. Do NOT touch `speech_rate` unless asked.
  **Floor: detected speech ending before 7.8s → rewrite DENSER and regenerate** — a short line
  sits centred with dead air on both sides and reads as a stall; fill the block. Prefer
  one flowing clause over clipped sentences and keep commas sparse: TTS pauses ~0.7s at
  every period and ~0.5s at every comma, so fewer of them both shortens the take and
  removes the pausey feel.
- **Emotion in [square brackets]** — performed non-verbals: `[scoffs] [dry laugh] [sighs]
  [chuckles] [mock gasp] [whispers]`. Round-paren `(cues)` = direction, not spoken. Each
  performed bracket adds ~1s — count it toward the 9.5s ceiling.
- Open with a hook question when asked ("Have you ever wondered why…"). Numbers spelled out.
  Characters never lip-sync (external narrator).

## LINE HYGIENE — how the word count gets filled (gated in `validate_motion_script.py`)

The word floor is a floor for CONTENT. Reaching it with filler and stacked adjectives
turns an educational video into a video about adjectives — and it wrecks the captions
too, because the STT swallows the quiet fillers and the burner then interpolates them.

1. **Filler is BANNED, in any language.** No "you know", "y'know", "I mean", "sort of",
   "kinda", "basically", "um/uh", no "right?" / "okay?" tacked onto a line, no "so
   yeah", no "let's talk about". The validator rejects the line. The ban applies in
   EVERY language: whatever the local equivalent of a verbal shrug is, it is still
   filler, and the validator's word list only covers English — so a non-English script
   needs the author's own judgement here, not the gate's.
2. **ONE modifier per thing. Never repeat a modifier inside a line.** "sparkly dreamy
   sparkly sky" is three words of padding and zero information — write "the sky turns
   the colour of a peach". A content word repeated within six words fails the gate.
3. **Every line pays rent: ONE new concrete thing** — a number, a name, a place, a
   mechanism, a comparison the previous line did not have. If a line only re-describes
   what the last one said with new adjectives, delete it and write the next fact.
4. **Diminutives and endearments: at most ONE per line, zero in factual channels.**
   Kids warmth comes from direct address and energy ("watch this!", "count with me"),
   not from a pile of "-ies" in one breath. Same for exclamations: one per line.
5. **Sensory description earns its place only when the shot shows it** — describe what
   the block's own visuals stage, never generic prettiness.
6. **Too short? Add a FACT, never an adjective.** Too long? Cut modifiers first, facts
   last. This is the only legal way to move a line's length (no `atempo`, ever).

## Assemble (do NOT hand-roll — one command)

`${HF_WORKFLOWS}/faceless-video/scripts/assemble_final.sh --out final.mp4 --blocks N --manifest pairs.txt [--music bed.mp3] [--stepped 12]`
`--blocks N` is REQUIRED and the manifest is written for EVERY run (mispaired or
missing lines are hard fails). Captions are NOT part of assembly — Phase 7 invokes
the `video-montage` skill afterwards. It centers each 7.8–9.5s line in its fixed 10s block,
concatenates to **N×10s** (never shortened), and enforces the LEVEL LAW: voice 1.0
always, the clips' diegetic SFX kept under it at ~0.12, optional music bed at ~0.10
generic / **0.05 for the kids-look default bed**, DUCKED under speech by a
sidechain keyed on the voice (both hard-clamped ≤0.20) + `loudnorm -16 LUFS`;

**VERIFY THE MIX, DO NOT ASSUME IT.** The law above is what the script asks for; what
matters is what came out. After assembly, measure every block and compare:

```
for i in $(seq 1 N); do ffmpeg -hide_banner -ss $(((i-1)*10)) -t 10 -i final.mp4 \
  -vn -af volumedetect -f null - 2>&1 | grep mean_volume; done
```

Every block must land within ~3 dB of the others, and a spoken block must sit around
−18…−21 dB mean. **Two failures seen on dev 2026-07-29:** music and clip SFX ended up
LOUDER than the narrator (the bed was mixed before the voice was normalized), and in a
Talking Characters run the narration blocks came out noticeably quieter than the dialogue
blocks (native dialogue audio can arrive already hot at ≈−21 dB, while a
fresh TTS take is ≈−31 dB before normalization). So: **normalize the VOICE first, then
place the bed/SFX under the normalized voice, then re-measure.** A block that is more than
3 dB off its neighbours is remixed, not shipped.
outputs ONE file with no leading freeze. Diegetic SFX already live in the clips (whooshes, sparkles for Kids). Music
bed when the user supplied a file or explicitly asked — PLUS the Kids channel, where
a wordless bed is ON BY DEFAULT. A due bed needs no file: it is GENERATED with
`sonilo_music` at the VIDEO's exact duration (≤600s in one request — verified;
longer = join parts; `references/kids-styles.md §Kids music bed`); otherwise run
without `--music` —
voices + the clips' diegetic SFX are the mix. Never block delivery on a bed, never
synthesize music with the speech model (`text2speech_v2` speaks, `sonilo_music` plays).

## Subtitles — DELEGATED to the `video-montage` skill

Captions are no longer built here. When subtitles are on, Phase 7 invokes the
**`video-montage`** skill on the assembled cut and passes:

- the immutable assembled clean master (before any optional post-delivery upscale);
- `script_manifest.json` as the AUTHORED WORDING (Whisper stays the clock — every
  displayed word comes from the exact `vo_line` / `phrase`);
- the look: `clean` (default) · `paper` (torn cream label, handwritten — storybook
  tones) · `bold` (UGC ALL-CAPS with platform safe zones).

That skill owns EVERY caption decision — line length, character count, position, the
burners, font choice and per-language glyph coverage, the Whisper dependency and the
"unavailable → deliver unsubbed and say so" fallback. **Nothing here overrides it and
nothing here re-implements it.** No `ffmpeg` filter with `subtitles=` / `ass=` /
`drawtext=`, no hand-written `.srt`, no burner call. A run that has captions but no
`.srt` from the skill next to the final did it by hand and is not deliverable.

Note: `${HF_WORKFLOWS}/faceless-video/scripts/audio_to_captions.py` still ships with THIS skill for ONE reason —
Picture Story uses its word timestamps to build the FRAME TIMELINE (Phase 5b), a
timing job. Pointing it at captions here is the forbidden path.
