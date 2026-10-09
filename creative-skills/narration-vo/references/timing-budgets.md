# Timing budgets, trimming rules, pause marks, locked voice

Contents
1. The measured core (English, ElevenLabs-class TTS) - the numbers everything else scales from
2. Budgets per language, incl. Polish (estimates: calibrate on your first take)
3. Window to word-count cheat table
4. Trimming and padding rules (the only legal ways to change a length)
5. Breath and pause marks (script notation)
6. Locked voice across takes and chunks
7. Take QA: convert, measure, accept, retry
8. Continuous long-form read

## 1. The measured core

These come from production runs with an ElevenLabs-class engine. Treat them as ground truth for English and as the anchor for the estimates in section 2.

| Quantity | Value | Why it matters |
|---|---|---|
| Fixed 10 s window, target speech | 7.8 to 9.5 s | The speech is centred in the window; below 7.8 s the scene sits in silence on both sides and reads as a stall |
| Soft band | 7.2 to 7.8 s | Accept only after one retry of the line |
| Hard reject | under 7.2 s or over 9.5 s | Over 9.5 s collides with the next scene; no speed-up allowed |
| Words per full 10 s line | 20 to 23, at most 2 sentences, comma-light | Word count is the only length lever |
| Kids / excited delivery | 17 to 21 words | Excited delivery and performed cues take time |
| Natural pace, all-in | 2.4 to 2.6 words/sec (takes measured 2.37 to 2.65) | Words / speech seconds, pauses included |
| RUSHED ceiling | above 2.9 words/sec | Fits the clock, sounds like an auctioneer; rewrite shorter |
| SLOW floor | below 2.1 words/sec | Usually a pausey or padded line |
| Pause cost | period about 0.7 s, comma about 0.5 s | Fewer stops = shorter AND less pausey; one flowing clause beats three clipped sentences |
| Performed cue `[scoffs]` | about 1 s each | Budget it like words |
| Internal pause | none of 0.8 s or more | Pausey takes get rewritten, not trimmed |
| Presenter on camera (video model speaks) | 3.1 to 3.5 words/sec, 31 to 35 words per 10 s | Brisk steady pace of a talking clip; see presenter-mode.md |

Lengths are bimodal: the same line tends to come back near 9.0 s or near 10.4 s. The speech-rate knob is a weak, noisy lever, so do not rely on it. What moves a take between the two modes is plus or minus 1 to 2 words and unrolling comma lists into one flowing clause.

Dead air floor: a line ending before 7.8 s of a 10 s window gets denser content, never filler.

## 2. Budgets per language

Only English is measured. The other rows scale the English numbers by average spoken word length, so they are starting points. Run `python3 scripts/fit_narration.py --text "..." --seconds 10 --lang pl --measured <seconds of your real take>` once and pass the printed `--wps` to every later check.

| Lang | Multiplier vs EN | Natural all-in w/s | RUSHED above | SLOW below | Words per 10 s line | Note |
|---|---|---|---|---|---|---|
| en | 1.00 | 2.40 to 2.60 | 2.90 | 2.10 | 20 to 23 | Measured |
| pl | 0.80 | 1.90 to 2.10 | 2.30 | 1.70 | 16 to 19 | Long inflected words; numbers spoken out are very long ("dwa tysiące dwudziesty piąty") |
| de | 0.85 | 2.05 to 2.20 | 2.45 | 1.80 | 17 to 21 | Compounds count as one word |
| es | 1.00 | 2.40 to 2.60 | 2.90 | 2.10 | 20 to 23 | Short words but fast syllable rate; verify |
| fr | 1.00 | 2.40 to 2.60 | 2.90 | 2.10 | 20 to 23 | Elisions merge words; verify |
| ru | 0.82 | 1.95 to 2.15 | 2.40 | 1.70 | 16 to 20 | |
| cs | 0.80 | 1.90 to 2.10 | 2.30 | 1.70 | 16 to 19 | |

Polish rules of thumb:
- Budget about 20 percent fewer words than the English template for the same window. A Polish 10 s block holds 16 to 19 words, a Kids block about 14 to 17.
- Characters per second is steadier across languages than words per second: roughly 13 to 15 characters of letters per second of speech. Use it as a cross-check when a line is full of very short or very long words.
- Spell numbers as words and prefer short forms: "w czterdziestym piątym" over "w tysiąc dziewięćset czterdziestym piątym". A year in digits is read in full and blows the window silently.
- Diacritics matter to the TTS: always write ą ę ć ł ń ó ś ź ż, never ASCII fallbacks.
- Mixed English brand names inside Polish text (names of apps, products) are read with Polish rules by some engines; test one line and respell phonetically if needed ("najki" is a last resort, prefer rephrasing).
- Declension makes numerals and names longer than they look: count the spoken form, not the written one.

## 3. Window to word-count cheat table

Fill target 78 to 95 percent of the window, normal punctuation (about 1.2 s of pauses per 10 s). Real takes vary by a word or two; confirm with the script.

| Window | EN words | PL words | DE words | Typical use |
|---|---|---|---|---|
| 3 s | 6 to 8 | 5 to 6 | 5 to 7 | stinger, label line |
| 4 s | 8 to 11 | 7 to 8 | 7 to 9 | short caption beat |
| 5 s | 11 to 13 | 8 to 11 | 9 to 11 | |
| 6 s | 13 to 16 | 10 to 13 | 11 to 13 | |
| 8 s | 16 to 20 | 12 to 16 | 13 to 17 | |
| 10 s | 20 to 23 | 16 to 19 | 17 to 21 | the standard block |
| 15 s | 29 to 37 | 23 to 29 | 25 to 31 | |
| 20 s | 39 to 49 | 31 to 39 | 33 to 42 | |
| 30 s | 58 to 73 | 47 to 59 | 50 to 62 | |
| 60 s | 117 to 147 | 93 to 118 | 99 to 125 | continuous read: natural 2.4 to 2.6 w/s EN, about 1.9 to 2.1 w/s PL |

A short final window (not a multiple of 10 s) gets its own window and its own word budget; never reuse the full-block count.

## 4. Trimming and padding rules

Order of operations when a line is wrong. Never change the audio speed, pitch, or the engine's speech-rate setting to fit; the words are the lever.

Too long (over the window or RUSHED):
1. Delete modifiers first (one modifier per noun, never a modifier repeated inside the line).
2. Delete filler and softeners (see list below).
3. Unroll comma lists into one flowing clause; remove sentence stops (each stop costs about 0.7 s).
4. Replace long number phrases with a comparison or a shorter form.
5. Drop a subordinate clause, keep the claim. Facts go last.
6. Still long: split the sentence across two windows; do not squeeze it.

Too short (UNDER or SLOW):
1. Add a FACT: a number, a name, a place, a mechanism, a comparison the line did not have. Never add an adjective.
2. A line that only re-describes the previous line with new adjectives gets deleted and replaced with the next fact.

Pausey take (internal pause of 0.8 s or more): rewrite as ONE flowing clause with no internal sentence stops, commas, dashes or performed pauses. Changing only the delivery direction does not fix it.

Filler list (banned in any language, including the local equivalents): "you know", "I mean", "basically", "sort of", "kinda", "um/uh", a trailing "right?" / "okay?", "so yeah", "let's talk about". Polish equivalents to cut: "no więc", "w sumie", "jakby", "wiesz", "tak naprawdę", "generalnie", "prawda?" tacked on the end.

Line hygiene (density is content, not adjectives):
- one modifier per thing; no content word repeated within six words
- every line pays rent with one new concrete
- at most one diminutive or exclamation per line, zero diminutives in factual channels
- no phrase of five or more words repeated in two lines

Pasted authored text (a ready script) is VERBATIM: do not tighten it. Split only at sentence boundaries, report the resulting window count (`N = ceil(total words / words per window)`), and if the length disagrees with a stated duration say both numbers and ask once which wins. Numbers and dates are the usual reason a pasted script overruns.

## 5. Breath and pause marks

A planning notation for the script. Strip or convert it before sending text to the TTS (most engines take punctuation, not custom marks).

| Mark | Meaning | Costs | Convert to |
|---|---|---|---|
| `/` | short breath, phrase boundary | 0.4 s | comma |
| `//` | full pause, thought boundary | 0.8 s | period, or a line break between takes |
| `[breath]` | audible inhale before a big line | 1 s, engine permitting | remove if the engine reads it aloud |
| `[whispers]` `[scoffs]` `[dry laugh]` `[sighs]` | performed non-verbal | about 1 s each | keep only if the engine supports bracket cues (ElevenLabs v3 does; test one line first), else delete |
| `(slower)` | direction for the editor, not spoken | 0 | delete |
| `...` | trailing hesitation | about 0.9 s | use sparingly, engines vary |

Placement rules:
- Put the breath where a human would: after the subject phrase, before a number or the reveal, never inside a name or a number.
- One `//` per 10 s window at most; a pause is a beat, not a rhythm.
- A question goes at the END of a line so the window boundary is the answer beat; never leave 0.8 s or more of silence inside a line.
- The fit script prices `/` at 0.4 s, `//` at 0.8 s, cues at 1.0 s.

## 6. Locked voice across takes and chunks

The voice is not the emotion. Mood comes from word choice, the delivery phrase and performed cues, never from switching voices mid-job.

1. Write the voice identity down once in a one-line `voice.lock` (engine, model/variant, voice id, voice type, language) and re-read it before EVERY take. A pair passed from memory is how a video ends up with a different voice per scene.
2. Compose ONE delivery phrase for the whole job and repeat it VERBATIM on every take, for example `wry conversational explainer, neutral accent, bright dry timbre, lively pace`. Optional 2 to 4 word mood per line (`hushed conspiratorial`), nothing else varies.
3. Same engine, same model, same settings (stability, similarity, style) on every take. A take that comes back in a different timbre is failed, regenerate with the locked identity. Retrying the same text for timbre or garbling is legal; retrying the same text to chase a duration is not (change the words).
4. Where your TTS front-end accepts a direction bracket, the format that worked was: `[ {DELIVERY}, {optional mood}, starts speaking immediately] [00:00-00:09] {line}`. "starts speaking immediately" removes the leading pause; the timecode is a hint, not a pacing control. Test on your tool and drop it if it gets read aloud.
5. Chunking a long read: most engines cap characters per request. Split at paragraph boundaries into a few LARGE chunks (about 1800 characters, never below a paragraph), same voice identity, same delivery phrase, reading order numbered `chunk-001...`. Do not send per-phrase snippets: each snippet restarts intonation and the seams are audible. A retry reuses the chunk number.
6. Carry context across chunks: if the engine supports previous/next text conditioning (ElevenLabs does), pass the neighbours; otherwise end each chunk on a full stop and start the next on a new sentence.
7. Join chunks losslessly (`ffmpeg -f concat -safe 0 -i parts.txt -c copy narration.wav`), after all chunks are converted to the same sample rate and channel count. Level-match chunks to the same loudness (-16 LUFS integrated is a safe delivery target for online video) before joining, not after.
8. Never clone or imitate a real person's voice from a recording without that person's consent; use library voices or the user's own consented voice.

## 7. Take QA: convert, measure, accept, retry

1. Download as MP3, convert to mono 24 kHz WAV and remove the ElevenLabs tail click with exactly this chain (the only edit allowed on a take):
   ```
   ffmpeg -nostdin -hide_banner -loglevel error -i takeNN.mp3 -ac 1 -ar 24000 \
     -af "areverse,atrim=start=0.030,asetpts=N/SR/TB,afade=t=in:st=0:d=0.060,areverse" \
     -y voiceNN.wav
   ```
2. Measure SPEECH seconds (not file length: providers pad head and tail), internal pauses and words/sec: `python3 scripts/fit_narration.py --text "<the exact line>" --audio voiceNN.wav --seconds 10 --lang pl`.
3. Accept when: speech inside 7.8 to 9.5 s of a 10 s window (scaled for other windows), zero internal pauses of 0.8 s or more, words/sec not above the RUSHED ceiling for the language.
4. Anything else: rewrite the TEXT, regenerate only that line. Passing takes are immutable. At most 3 attempts per line, and the third needs changed text. After 3 failures report the slot, attempts and metrics; do not ship the closest failure.
5. Never trim silence, cut pauses, or time-stretch a take. Two earlier runs passed the metric by cutting internal pauses and shipped audibly choppy narration.
6. Verify WHAT the take says, not only how long it is: transcribe each take (any STT) and compare with the line. A mismatched take can come back with perfect length and the wrong words.
7. If a line is rewritten to fit, update the script and the caption source so captions match what was actually spoken.

## 8. Continuous long-form read

Used when visuals are timed to the audio afterwards (stills stories, documentaries).
- A target duration is a SCRIPT-LENGTH target, not a TTS-speed target. Generate the script once at the natural rate, measure the joined narration.
- If it misses, rewrite: `new words = old words * target seconds / measured seconds`. Submit the NEW wording; identical text is never resubmitted to chase duration.
- One initial read plus at most two text-rewrite corrections for the whole narration. Then return the closest clean take with the exact miss.
- No per-line window gate; reject chunks with wrong timbre, garbled words or internal pauses of 0.8 s or more.
- Time the visuals from word-level timestamps of the final audio (speech-to-text), never from estimated or evenly spread timings: guessed durations make pictures drift ahead of the words.
