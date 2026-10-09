---
name: narration-vo
description: "Write, fit and QA voice-over (lektor, narracja) for timed windows: words-per-second budgets per language incl. Polish, trimming rules, breath and pause marks, one locked voice across takes and long chunked reads, plus presenter mode (a talking-head narrator inserted into an existing edit). Use whenever the user has a script plus a duration or a cut with scene lengths, or says the voice-over is too long, too short, rushed or pausey, even without the word narration. Includes scripts/fit_narration.py (pure stdlib) reporting words/sec and flagging over-budget segments. Trigger on: lektor, voice over, narracja, dopasuj tekst do czasu, ile słów na 10 sekund, za długi lektor, za szybko czyta, ElevenLabs, jeden głos w całym filmie, pauzy i oddechy, wstaw mnie jako narratora, talking head w filmie, prezenter. Route to faceless-video-pipeline for the whole video, caption-and-title-systems for subtitles, ugc-video-scripts for creator ads."
---

# Narration and Voice-Over Fitting

Turn text plus time into a voice-over that fits: the right number of words for each window, a stable voice from first take to last, and, when asked, an on-screen presenter added to an existing video. The skill owns the numbers (words per second, pauses, windows); the user's TTS tool does the speaking.

## When to use / when not

Use when:
- A script must fit fixed windows (a 10 s scene, a 4 s caption beat, a 60 s reel) and the user asks how many words, or the read runs long, short, rushed or with dead air.
- A long narration (documentary, stills story, audiobook-style chapter) must be read in ONE voice across chunks.
- The user wants themselves, or another consenting person, to appear as the narrator in an existing edit ("put me in as the narrator", "talking head over my clip").
- A pasted ready script must be split into timed blocks without rewriting it.

Do not use for:
- Writing the whole video (hook, beats, shot list, visuals): use `faceless-video-pipeline`. It calls this skill for the voice step.
- Subtitle styling and timing: `caption-and-title-systems`.
- Creator-style ads with a spoken hook on camera: `ugc-video-scripts`.
- Voice cloning or imitating a real person, music, SFX, singing: out of scope. Library voices or the user's own consented voice only.
- "Read this aloud" with no time constraint: just use the TTS; no fitting needed.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

- The text, or a topic plus facts to write from. Pasted text is verbatim: do not rewrite it.
- Windows: one duration for all (default 10 s per block) or a list per scene. Default speech fill 78 to 95 percent of the window.
- Language, inferred from the text (default Polish if the user writes Polish, English otherwise). The budget changes with the language.
- Voice identity: engine, model, voice id, voice type, one delivery phrase. Default: ask the user to name the voice they already use; if none, propose a neutral one and record it.
- Mode: per-window takes (default), continuous read, or presenter mode (a base video plus a photo of a consenting person).
- Optional: calibration take (seconds of speech for a known text) to replace the estimates.

## Workflow

1. Pick the mode. Per-window takes: continue at 2. Continuous read: go to 7. Base video plus a person's photo, or "put me in as the narrator": go to 8.
2. Look up the budget in `references/timing-budgets.md` for the language and window (English 20 to 23 words per 10 s, about 2.4 to 2.6 words/sec all-in; Polish about 16 to 19 words per 10 s, about 1.9 to 2.1 words/sec; Polish and other non-English numbers are estimates until calibrated).
3. Write or split the text at sentence boundaries, one line per window, at most two sentences, comma-light, numbers as words, no filler. Mark breaths with `/` and pauses with `//` where the delivery needs them.
4. Run the fit check on every line:
   ```
   python3 scripts/fit_narration.py --file vo.txt --seconds 10 --lang pl
   ```
   One line per segment; a line may start with its own window (`[6]`, `[00:00-00:09]`). The report gives words, window, estimated speech seconds, fill, words/sec and a fix ("cut 4 words, target 16 to 19"). Exit code 1 means at least one segment is over budget.
5. Apply the trimming rules in order (modifiers, filler, stops and commas, long numbers, a clause; add FACTS not adjectives when short). Re-run until every line is OK. Never change speed or pitch to fit.
6. Produce the voice sheet (Output format): voice lock, delivery phrase, final lines with marks converted for the TTS, and the QA plan. After the user generates takes, measure each: `python3 scripts/fit_narration.py --text "<line>" --audio voiceNN.wav --seconds 10 --lang pl`. Rewrite and regenerate only failing lines (max 3 attempts, the third needs changed text). After the first real take, calibrate with `--measured <seconds>` and reuse the printed `--wps` for every later check.
7. Continuous read: split into chunks of about 1800 characters at paragraph boundaries, same voice identity and delivery phrase on every chunk, numbered in reading order; join losslessly; measure the joined duration; if it misses the target, rewrite by `new words = old words * target / measured` (identical text is never resubmitted to chase duration; at most two rewrite corrections). Time visuals from word-level timestamps of the final audio, never from guesses.
8. Presenter mode: follow `references/presenter-mode.md`. Confirm consent, choose route A (real footage) or B (generated from a photo), budget 31 to 35 words per 10 s block in English (about 25 to 28 in Polish), make the green-screen identity image, generate one talking clip per block, replace the voice speech-to-speech with the locked voice, composite as cutout, badge or fullframe, and deliver with the presenter brief.
9. Final pass: voice lock identical on every line, no line above budget, captions source text equals the spoken text.

## Output format

Always return this sheet; the fit table is generated by the script, never estimated by eye.

````markdown
# Voice-over sheet - <project> (<lang>, <N> windows)

## Voice lock
engine: <ElevenLabs | other>   model: <...>   voice: <id or name>   type: <library | own>
settings: <stability / similarity / style as used>   (identical on every take)
delivery phrase (repeat verbatim on every take): <wry conversational explainer, neutral accent, bright dry timbre, lively pace>

## Fit table (fit_narration.py output)
| # | Window | Words | Est. speech | Fill | w/s | Status | Fix |
|---|--------|-------|-------------|------|-----|--------|-----|

## Lines (marks: / breath 0.4 s, // pause 0.8 s)
1. [00:00-00:09] <line with marks>
2. ...

## Send to the TTS (marks converted: / -> comma, // -> period, cues kept only if supported)
1. <clean line>
2. ...

## QA plan
Convert -> measure speech, pauses, w/s -> accept 7.8 to 9.5 s of a 10 s window -> rewrite text only on failure -> verify words by transcription.
````

Presenter mode returns the brief from `references/presenter-mode.md` section 11 instead.

## Tool adapters

- ElevenLabs: use a multilingual model for Polish; keep stability, similarity and style identical on every take; leave the speed setting at neutral and fix length with words. Bracket cues such as `[whispers]` work only on models that support audio tags (v3); test one line before using them in bulk. Use previous/next text conditioning on chunked reads if offered.
- Any other TTS (Azure, Google, local models): same rules; per-request character limits differ, so chunk size is the only change. Polish quality varies, so run the calibration take first.
- Premiere Pro: import takes, place on one audio track per voice, apply Essential Sound (Dialogue) with the same preset to every take, loudness target about -16 LUFS integrated for online video, duck music 12 to 18 dB under speech. Never use Time Stretch or Rate Stretch on a take; re-cut the picture or rewrite the line.
- After Effects: for presenter mode, key with Keylight plus Spill Suppressor; the badge disc is a shape layer with the clip precomposed inside a circle mask.
- KLING / Seedance 2 / Higgsfield Cinema Studio: only for the route B talking clip (a video model that speaks from a reference photo). Seedance 2 takes EN and ZH prompts; keep the line in quotes inside an English prompt. Poor fit: long continuous takes over 10 s and wide shots, where identity drifts.
- Nano Banana Pro: makes the green-screen identity image from the person's photo (an image-edit model that keeps the face unchanged); give the exact prompt from `references/presenter-mode.md`.
- Figma: nothing to do for this skill.

## QA checklist

- [ ] Every line passes `fit_narration.py` (exit code 0) for its own window and language.
- [ ] Numbers are written as words; no digits in lines sent to the TTS.
- [ ] No filler phrases, no modifier repeated inside a line, one new concrete fact per line.
- [ ] At most two sentences per 10 s line; at most one `//` per window.
- [ ] One voice identity and one delivery phrase on all takes; any different timbre was regenerated.
- [ ] Takes converted with the tail-click chain, measured on SPEECH seconds, no internal pause of 0.8 s or more.
- [ ] No time-stretch, pitch-shift, speed change or silence trimming anywhere.
- [ ] Pasted authored text is untouched except sentence-boundary splitting.
- [ ] Final spoken wording equals the caption/subtitle source.
- [ ] Presenter mode: consent confirmed, identity unchanged, key is clean, presenter never covers key base content, original-audio decision stated.

## References

- `references/timing-budgets.md`: read for the measured numbers, per-language budgets (Polish included), window-to-words table, trimming rules, pause marks, locked-voice rules, take QA and the continuous read.
- `references/presenter-mode.md`: read for any "put me in as the narrator" request: consent, routes, script budget, master prompts, voice replacement, framing and eyeline, composite numbers, keying, brief template.
- `scripts/fit_narration.py`: run it for every fit check; `--help` lists options (`--file`, `--windows`, `--lang`, `--wps`, `--measured`, `--audio`, `--json`).
