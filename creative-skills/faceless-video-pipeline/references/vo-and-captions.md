# vo-and-captions.md: fixed-window voice-over, mix and subtitle handoff

Contents
1. Voiceover: one line per block
2. LINE HYGIENE: how the word count gets filled
3. Mix and level law (and how to verify it)
4. Music bed
5. Captions spec

## 1. Voiceover: ONE LINE PER BLOCK

- **One narrator voice for the whole video.** Pick it once at intake. Hints for the user only: History = a deep, dry male storyteller; Kids = a warm bright voice; Explainer = a lively, slightly dry conversational voice; Picture Story = match the tone. Record the exact engine, model, voice id and settings and use the SAME identity on EVERY line; a take that comes back in a different timbre is a failed take, regenerate it. Custom (own, consented) voices work as well as library voices.
- **Intonation and mood live in the SCRIPT, not in the voice:** fit delivery to the channel type + topic (sombre topic = measured wording, fewer gags; playful = lighter lines, more performed brackets). The voice never changes mid-video.
- **Kids call-and-response:** the narrator addresses characters and the viewer by name ("Say hi to Masha!", "Can YOU count the apples?") and the video stages the visible reaction. Questions go at the END of a line: the block boundary IS the answer beat, and the next line opens with the payoff ("That's right, three!"). Never leave a pause of 0.8 s or more inside a line for the answer. Narrator-spoken sound-words ("whoosh!", "ding!") and catchphrases count as words in the Kids 17 to 21 budget: seasoning, not filling, at most ONE per line.
- **One spoken line per block** (block N = `voiceNN.wav`). No timecodes in the script, no big continuous chunk, no clip-by-clip delay juggling. One line = one 10 s scene = sync by construction. (Stills videos are the exception: one continuous read, see `format-variants.md`.)
- **Line prompt format: delivery direction, not pacing.** Where your TTS front-end accepts a direction bracket, send every line as `[ {DELIVERY}, {optional block mood}, starts speaking immediately] [00:00-00:09] {text}`. {DELIVERY} is ONE direction phrase composed once for the whole video to fit the channel type + topic (e.g. `wry conversational explainer, neutral accent, bright dry timbre, lively pace`) and repeated VERBATIM on every line; that keeps the timbre consistent across blocks. {optional block mood} is 2 to 4 words for the beat (`a bright knowing reveal`, `hushed conspiratorial`). "starts speaking immediately" kills the leading pause. The `[00:00-00:09]` window did not control pacing in ElevenLabs. If your tool reads the bracket aloud, drop it and keep the delivery phrase in the voice settings or a plain instruction field.
- **Length: each line FILLS the 10 s block, target about 7.8 to 9.5 s of speech** (the edit centres the line's SPEECH in its window, ignoring the file's edge silences). Use **20 to 23 words, at most TWO sentences**, comma-light, one flowing clause where you can. Word count is the only length lever. An over-budget line does not fail loudly: the voice just RACES (a 41-word five-sentence line containing "August 15th, 1977" came back as an auctioneer read with a dead tail). **Write every number as words** ("nineteen seventy-seven", "the fifteenth of August"); digits, dates and abbreviations are spoken far longer than they are written and blow the budget invisibly.
  - Target 7.8 to 9.5 s; soft 7.2 to 7.8 s only after one retry; hard reject outside 7.2 to 9.5 s; **no internal pause of 0.8 s or more** (rewrite flowing and regenerate, do not ship stalls).
  - Kids run hotter: **17 to 21 words** with an EXCITED delivery cue and bounded performed brackets (`style-packs.md` section 10 and `format-variants.md` Kids section); warmth = word choice, not pauses.
  - Non-English: the budgets shrink with word length (Polish about 16 to 19 words per 10 s). Use `narration-vo` for the exact numbers and `fit_narration.py`.
  - **Measure the pace, not only the length:** words/sec above 2.9 (English, all-in) is a RUSHED take and a REWRITE even when the speech length sits inside the window; a rushed take is the "auctioneer" complaint in its pure form.
  - **If speech exceeds 9.5 s: rewrite shorter. NEVER speed up, slow down or pitch-shift the audio to fit**, and leave the engine's speech-rate setting alone unless asked.
  - **Floor: speech ending before 7.8 s: rewrite DENSER and regenerate.** A short line sits centred with dead air on both sides and reads as a stall; fill the block. Prefer one flowing clause over clipped sentences and keep commas sparse: TTS pauses about 0.7 s at every period and about 0.5 s at every comma.
  - Measured retries: an overlong take is shortened to the recommended count only for that slot; passing takes are immutable; a line that misses after three attempts is a failure, not a deliverable.
- **Emotion in [square brackets]:** performed non-verbals `[scoffs] [dry laugh] [sighs] [chuckles] [mock gasp] [whispers]`. Round-paren `(cues)` = direction, not spoken. Each performed bracket adds about 1 s, so count it toward the 9.5 s ceiling. Use them only if your engine supports bracket cues (ElevenLabs v3 does; test one line).
- Open with a hook question when asked ("Have you ever wondered why..."). Characters never lip-sync (external narrator).
- **Verify what the take SAYS**, not only how long it is: transcribe each take (any STT) against the script line before assembly; under load a TTS can return another video's audio with perfect length.

## 2. LINE HYGIENE: how the word count gets filled

The word floor is a floor for CONTENT. Reaching it with filler and stacked adjectives turns an educational video into a video about adjectives, and it wrecks the captions too, because speech-to-text swallows the quiet fillers.

1. **Filler is BANNED, in any language.** No "you know", "y'know", "I mean", "sort of", "kinda", "basically", "um/uh", no "right?" / "okay?" tacked onto a line, no "so yeah", no "let's talk about". Whatever the local equivalent of a verbal shrug is, it is still filler (Polish: "no więc", "w sumie", "jakby", "wiesz", "tak naprawdę", "generalnie").
2. **ONE modifier per thing. Never repeat a modifier inside a line.** "sparkly dreamy sparkly sky" is three words of padding and zero information; write "the sky turns the colour of a peach". A content word repeated within six words fails.
3. **Every line pays rent: ONE new concrete thing** (a number, a name, a place, a mechanism, a comparison the previous line did not have). If a line only re-describes the last one with new adjectives, delete it and write the next fact.
4. **Diminutives and endearments: at most ONE per line, zero in factual channels.** Kids warmth comes from direct address and energy ("watch this!", "count with me"), not from a pile of "-ies" in one breath. Same for exclamations: one per line.
5. **Sensory description earns its place only when the shot shows it**: describe what the block's own visuals stage, never generic prettiness.
6. **Too short? Add a FACT, never an adjective. Too long? Cut modifiers first, facts last.** This is the only legal way to move a line's length.

## 3. Mix and level law (and how to verify it)

Assembly is done in Premiere Pro (see `assembly-brief.md`). Rules:
- Each 7.8 to 9.5 s line is CENTRED in its fixed 10 s block; total = N x 10 s, never shortened to fit short audio (if the video feels short, ADD narration, never trim the video).
- **LEVEL LAW:** voice 1.0 always; the clips' diegetic SFX kept under it at about 0.12; optional music bed at about 0.10 generic, **0.05 for the kids-look default bed**, DUCKED under speech by a sidechain keyed on the voice (never above 0.20); final loudness about -16 LUFS integrated. In Premiere: Essential Sound > Music > Ducking against the dialogue track.
- **Verify the mix, do not assume it.** After export, measure every block and compare:
  ```
  for i in $(seq 1 N); do ffmpeg -hide_banner -ss $(((i-1)*10)) -t 10 -i final.mp4 \
    -vn -af volumedetect -f null - 2>&1 | grep mean_volume; done
  ```
  Every block must land within about 3 dB of the others, and a spoken block should sit around -18 to -21 dB mean. Two failures seen: music and clip SFX ended up LOUDER than the narrator (the bed was mixed before the voice was normalized), and in a Talking Characters run the narration blocks came out quieter than native dialogue blocks (native dialogue audio can arrive hot at about -21 dB while a fresh TTS take is about -31 dB before normalization). So: **normalize the VOICE first, then place the bed/SFX under the normalized voice, then re-measure.** A block more than 3 dB off its neighbours is remixed, not shipped.
- Diegetic SFX already live in the clips (whooshes, sparkles for Kids). A music bed when the user supplied a file or asked, plus the Kids and Fairy Tale channels where a wordless bed is on by default.

## 4. Music bed

Source priority: (1) a file the user supplied; (2) a generated instrumental bed at the video's exact duration (one continuous track; for very long runs generate parts with the same prompt and join them losslessly into one bed file); (3) none, and say so in one line. Never synthesize music with the speech model, and never block delivery on a bed. Bed prompt: the topic's mood translated into tempo, instruments and feel, instrumental, no lyrics, at most 2 sentences (1 is best); moods per channel in `style-packs.md` section 10.

## 5. Captions spec

Captions are a separate pass on the finished clean master; the spec below is what you hand to the captioning step (Premiere Pro Captions, After Effects, or `caption-and-title-systems`). Do not hand-time captions from the script.

- **Clock:** word timestamps come from speech-to-text run on the CLEAN voice takes (or the clean continuous narration for stills), shifted by each take's speech offset in the final timeline. NEVER transcribe the mixed final: music and SFX are exactly what makes an STT swallow words; this is the #1 cause of "subtitles don't match the audio".
- **Wording:** the displayed words come from the AUTHORED script (names and numbers spelled right); the STT only supplies timing. Require complete coverage of the script words before burning, and inspect the encoded result afterwards.
- **Language:** lock the caption language code from the actual script text (`pl`, `en`, ...), not from the topic.
- **Looks** (pick one for the whole video):
  - `clean` (default): slim white CAPS, small, fixed at the bottom about 12 percent of the frame, no plate.
  - `paper`: torn cream label with handwritten type; storybook tones. Default for Fairy Tale and Myth.
  - `bold`: UGC-style ALL-CAPS, large, with platform safe zones respected.
- Default per channel: Fairy Tale and Myth = `paper`, everything else = `clean`, unless the user asked otherwise.
- **Placement and size:** fixed bottom position, one or two short lines at a time (roughly 30 to 42 characters per line is a safe starting range; shorter for 9:16). No multi-line paragraphs across the middle of the frame. Keep clear of platform UI: for 9:16 stay out of the bottom 320 px (of 1920) and the right edge rail.
- **Font:** choose a font that covers the script's glyphs. Polish needs ą ć ę ł ń ó ś ź ż; verify by rendering a test line "Zażółć gęślą jaźń" before burning.
- **Song and sung content:** no captions (STT on singing is unreliable) unless the lyrics are supplied as authored text.
- If speech-to-text is unavailable, deliver unsubtitled and say so; do not hand-time.
- Deliver the clean master untouched next to the captioned version, and keep the SRT with it.
