#!/usr/bin/env python3
"""fit_narration.py - check voice-over text against timed windows (pure stdlib).

Reports words, words/sec and an estimated speech time per segment, and flags
segments that will not fit their window. Optionally measures a real WAV take.

Segments:
  --text "line" --seconds 10          one segment
  --file script.txt --seconds 10      one segment per non-empty line; a line may start
                                      with its own window: "[9]", "[9s]" or "[00:00-00:09]"
  --windows 10,10,6                   per-segment windows, applied in order (overrides --seconds)

Pause marks inside the text (stripped before counting words, priced as silence):
  /   short breath            0.4 s
  //  full pause             0.8 s
  [whispers] [scoffs] ...     performed cue, 0 words, 1.0 s
  (stage direction)           ignored (direction, not spoken)

Model (calibrated on English ElevenLabs takes; other languages are ESTIMATES):
  speech_s = words / articulation_wps + internal pauses
  internal pauses = 0.7 s per sentence stop that is not the last, 0.5 s per comma/semicolon/colon,
                    plus explicit marks. Comfortable fill of a window: 78%..95% of it.

Examples:
  fit_narration.py --text "Most of the ocean has never been seen." --seconds 4 --lang en
  fit_narration.py --file vo.txt --seconds 10 --lang pl
  fit_narration.py --text "..." --seconds 10 --lang pl --measured 9.4      # calibrate from a real take
  fit_narration.py --text "..." --audio take.wav --seconds 10 --lang pl    # measure a 16-bit WAV

Exit code: 0 all fit, 1 at least one OVER/RUSHED/PAUSEY, 2 usage error.
Status: OK, UNDER (dead air), SLOW, OVER (too long for the window); with --audio also RUSHED, PAUSEY.
"""
import argparse
import array
import json
import math
import re
import sys
import wave

# lang: (multiplier vs English, vowel letters for the syllable estimate)
LANGS = {
    "en": (1.00, "aeiouy"),
    "pl": (0.80, "aeiouyąęó"),
    "de": (0.85, "aeiouyäöü"),
    "es": (1.00, "aeiouáéíóúü"),
    "fr": (1.00, "aeiouyàâæéèêëîïôœùûü"),
    "ru": (0.82, "аеёиоуыэюя"),
    "cs": (0.80, "aeiouyáéěíóúůý"),
}
EN_ARTIC_WPS = 2.95      # articulation rate without pauses (derived from 20-23 words / 7.8-9.5 s)
EN_NATURAL = (2.4, 2.6)  # measured all-in words/sec
EN_RUSHED = 2.9          # all-in ceiling
EN_SLOW = 2.1            # all-in floor
FILL_MIN, FILL_MAX = 0.78, 0.95
P_STOP, P_COMMA, P_BREATH, P_PAUSE, P_CUE = 0.7, 0.5, 0.4, 0.8, 1.0


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def lang_params(lang, wps_override=None):
    mult = LANGS.get(lang, (1.0, LANGS["en"][1]))[0]
    artic = EN_ARTIC_WPS * mult
    if wps_override:
        artic = wps_override
        mult = artic / EN_ARTIC_WPS
    return {
        "artic": artic,
        "natural": (EN_NATURAL[0] * mult, EN_NATURAL[1] * mult),
        "rushed": EN_RUSHED * mult,
        "slow": EN_SLOW * mult,
    }


def parse_window(prefix):
    """[00:00-00:09] (inclusive end, so 10 s) | [9] | [9s]  ->  seconds, or None."""
    m = re.fullmatch(r"\[\s*(\d+):(\d+)\s*-\s*(\d+):(\d+)\s*\]", prefix)
    if m:
        a = int(m.group(1)) * 60 + int(m.group(2))
        b = int(m.group(3)) * 60 + int(m.group(4))
        if b <= a:
            return None
        return float(b - a + (1 if b % 10 == 9 else 0))
    m = re.fullmatch(r"\[\s*(\d+(?:\.\d+)?)\s*s?\s*\]", prefix)
    return float(m.group(1)) if m else None


def analyse(text, lang, window, wps_override=None):
    p = lang_params(lang, wps_override)
    vowels = LANGS.get(lang, LANGS["en"])[1]
    cues = len(re.findall(r"\[[^\]\[]*\]", text))
    clean = re.sub(r"\[[^\]\[]*\]", " ", text)
    clean = re.sub(r"\([^()]*\)", " ", clean)
    pauses = len(re.findall(r"//", clean))
    breaths = len(re.findall(r"(?<!/)/(?!/)", clean))
    clean = clean.replace("//", " ").replace("/", " ")
    words_list = re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", clean, re.UNICODE)
    words = len(words_list)
    chars = len(re.sub(r"\s+", "", "".join(words_list)))
    syll = sum(max(1, len(re.findall("[" + vowels + "]+", w.lower()))) for w in words_list)
    stops = len(re.findall(r"[.!?…]+(?=\s|$|[\"'”)])", clean.strip()))
    internal_stops = max(0, stops - 1)
    commas = len(re.findall(r"[,;:—–]", clean))
    sentences = max(1, stops)
    pause_s = (internal_stops * P_STOP + commas * P_COMMA + breaths * P_BREATH
               + pauses * P_PAUSE + cues * P_CUE)
    speech = words / p["artic"] + pause_s if words else 0.0
    wps = words / speech if speech else 0.0
    hi_words = max(0, int((FILL_MAX * window - pause_s) * p["artic"]))
    lo_words = max(0, math.ceil((FILL_MIN * window - pause_s) * p["artic"]))
    fill = speech / window if window else 0.0
    flags = []
    if re.search(r"\d", text):
        flags.append("digits: write numbers as words (spoken length and TTS reading differ)")
    if window <= 10.5 and sentences > 2:
        flags.append("more than 2 sentences per 10 s window")
    if fill > FILL_MAX:
        status = "OVER"
    elif fill < FILL_MIN:
        status = "UNDER"
    else:
        status = "OK"
    if status == "OK" and wps < p["slow"]:
        status = "SLOW"
    delta = 0
    if status == "OVER":
        delta = -(words - hi_words)
    elif status in ("UNDER", "SLOW"):
        delta = lo_words - words
    return {
        "words": words, "chars": chars, "syllables": syll, "sentences": sentences,
        "window_s": window, "est_speech_s": round(speech, 2), "fill": round(fill, 2),
        "wps": round(wps, 2), "cps": round(chars / speech, 1) if speech else 0.0,
        "pause_cost_s": round(pause_s, 2), "status": status,
        "target_words": [lo_words, hi_words], "word_delta": delta, "flags": flags,
        "wps_band": [round(p["natural"][0], 2), round(p["natural"][1], 2)],
    }


def measure_wav(path, noise_db=-45.0, min_pause=0.8):
    with wave.open(path, "rb") as w:
        if w.getsampwidth() != 2:
            fail("error: only 16-bit PCM WAV is supported (convert with ffmpeg first)")
        ch, rate, n = w.getnchannels(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    samples = array.array("h")
    samples.frombytes(raw)
    if sys.byteorder == "big":
        samples.byteswap()
    if ch > 1:
        samples = array.array("h", samples[0::ch])
    hop = max(1, int(rate * 0.02))
    thr = 32768.0 * (10 ** (noise_db / 20.0))
    voiced = []
    for i in range(0, len(samples) - hop + 1, hop):
        seg = samples[i:i + hop]
        rms = math.sqrt(sum(s * s for s in seg) / hop)
        voiced.append(rms > thr)
    if not any(voiced):
        return {"duration_s": round(len(samples) / rate, 3), "speech_s": 0.0, "pauses": 0, "longest_pause_s": 0.0}
    first = voiced.index(True)
    last = len(voiced) - 1 - voiced[::-1].index(True)
    step = hop / rate
    longest, count, run = 0.0, 0, 0
    for v in voiced[first:last + 1]:
        if not v:
            run += 1
        else:
            if run * step >= min_pause:
                count += 1
            longest = max(longest, run * step)
            run = 0
    return {
        "duration_s": round(len(samples) / rate, 3),
        "speech_start_s": round(first * step, 3),
        "speech_end_s": round((last + 1) * step, 3),
        "speech_s": round((last + 1 - first) * step, 3),
        "pauses": count, "longest_pause_s": round(longest, 2),
    }


def load_segments(args):
    segs = []
    if args.text:
        segs.append((args.text.strip(), None))
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                m = re.match(r"^(\[[^\]]*\])\s*(.*)$", line)
                win = None
                if m:
                    win = parse_window(m.group(1))
                    if win is not None:
                        line = m.group(2)
                segs.append((line, win))
    if not segs:
        fail("error: give --text or --file")
    wins = [float(x) for x in args.windows.split(",")] if args.windows else []
    out = []
    for i, (t, w) in enumerate(segs):
        if i < len(wins):
            w = wins[i]
        if w is None:
            w = args.seconds
        if not w or w <= 0:
            fail("error: give --seconds (or a window per segment)")
        out.append((t, w))
    return out


def main():
    ap = argparse.ArgumentParser(description="Check voice-over text against timed windows.")
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--seconds", type=float, help="window per segment in seconds")
    ap.add_argument("--windows", help="comma list of windows, one per segment")
    ap.add_argument("--lang", default="en", help="en pl de es fr ru cs (default en)")
    ap.add_argument("--wps", type=float, help="override articulation words/sec (no pauses) from your own take")
    ap.add_argument("--measured", type=float, help="real speech seconds of ONE text; prints your calibrated wps")
    ap.add_argument("--audio", help="16-bit PCM WAV of a real take (one segment); measures speech and pauses")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.lang not in LANGS:
        print("warning: unknown --lang %r, using English numbers" % args.lang, file=sys.stderr)

    segs = load_segments(args)
    results = []
    for i, (t, w) in enumerate(segs, 1):
        r = analyse(t, args.lang, w, args.wps)
        r["n"] = i
        r["text"] = t
        results.append(r)

    extra = {}
    if (args.audio or args.measured) and len(results) != 1:
        fail("error: --audio/--measured work on exactly one segment")
    if args.audio:
        m = measure_wav(args.audio)
        extra["audio"] = m
        r = results[0]
        sp = m["speech_s"]
        if sp:
            r["measured_wps"] = round(r["words"] / sp, 2)
            r["measured_fill"] = round(sp / r["window_s"], 2)
            p = lang_params(args.lang, args.wps)
            if r["measured_wps"] > p["rushed"]:
                r["status"] = "RUSHED"
            elif sp > FILL_MAX * r["window_s"]:
                r["status"] = "OVER"
            elif sp < FILL_MIN * r["window_s"]:
                r["status"] = "UNDER"
            else:
                r["status"] = "OK"
            if r["status"] in ("OVER", "UNDER", "RUSHED"):
                target = max(1, round(r["words"] * 0.87 * r["window_s"] / sp))
                r["word_delta"] = target - r["words"]
                r["target_words"] = [target, target]
            else:
                r["word_delta"] = 0
            if m["pauses"]:
                r["flags"].append("internal pause >= 0.8 s (%.2f s): rewrite as one flowing clause" % m["longest_pause_s"])
                r["status"] = "PAUSEY" if r["status"] == "OK" else r["status"]
    if args.measured:
        r = results[0]
        pause_s = r["pause_cost_s"]
        artic = r["words"] / max(0.1, args.measured - pause_s)
        extra["calibration"] = {
            "all_in_wps": round(r["words"] / args.measured, 2),
            "articulation_wps": round(artic, 2),
            "hint": "pass --wps %.2f to size the next lines on your own voice" % artic,
        }

    if args.json:
        print(json.dumps({"segments": results, **extra}, ensure_ascii=False, indent=2))
    else:
        print("lang=%s  band(all-in wps)=%.2f-%.2f  fill target %d-%d%% of window" % (
            args.lang, lang_params(args.lang, args.wps)["natural"][0],
            lang_params(args.lang, args.wps)["natural"][1], FILL_MIN * 100, FILL_MAX * 100))
        print("%3s %5s %5s %6s %7s %5s %5s  %-7s %s" % ("#", "words", "win_s", "est_s", "fill", "wps", "syl", "status", "fix"))
        for r in results:
            fix = ""
            if r["word_delta"] < 0:
                fix = "cut %d word(s) (target %d-%d)" % (-r["word_delta"], *r["target_words"])
            elif r["word_delta"] > 0:
                fix = "add %d word(s) of CONTENT (target %d-%d)" % (r["word_delta"], *r["target_words"])
            print("%3d %5d %5.1f %6.2f %6d%% %5.2f %5d  %-7s %s" % (
                r["n"], r["words"], r["window_s"], r["est_speech_s"], round(r["fill"] * 100),
                r["wps"], r["syllables"], r["status"], fix))
            for f in r["flags"]:
                print("      ! " + f)
            if "measured_wps" in r:
                print("      measured: speech=%.2fs wps=%.2f fill=%d%%" % (
                    extra["audio"]["speech_s"], r["measured_wps"], round(r["measured_fill"] * 100)))
        if "calibration" in extra:
            c = extra["calibration"]
            print("calibration: all-in wps=%.2f, articulation wps=%.2f -> %s" % (
                c["all_in_wps"], c["articulation_wps"], c["hint"]))
    bad = any(r["status"] in ("OVER", "RUSHED", "PAUSEY") for r in results)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
