#!/usr/bin/env python3
"""Convert word timestamps into a chunked SRT (dependency-free, Python 3.8+).

Input JSON (any of):
  - Whisper / faster-whisper style: {"segments": [{"words": [{"word": "Cześć", "start": 0.1, "end": 0.4}, ...]}]}
  - Flat list: [{"word": "...", "start": 0.1, "end": 0.4}, ...]  (also accepts "text" instead of "word")

Rules implemented (starting points, tune by eye):
  - max words / max chars per cue
  - new cue at sentence end or after a real pause
  - hold a cue to the next one when the gap is small (bridge), else end shortly after its last word (tail)
  - non-overlapping cues, minimum duration
  - optional authored script: replaces recognized words when token counts line up
  - optional balanced two-line break
Times always come from the audio words; the script only supplies spelling.
"""
import argparse
import difflib
import json
import re
import sys


def load_words(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    items = []
    if isinstance(data, dict) and "segments" in data:
        for seg in data["segments"]:
            items.extend(seg.get("words", []))
    elif isinstance(data, dict) and "words" in data:
        items = data["words"]
    elif isinstance(data, list):
        items = data
    else:
        sys.exit("Unrecognized JSON: expected {segments:[{words:[...]}]} or a list of words")
    words = []
    for w in items:
        text = (w.get("word") if "word" in w else w.get("text", "")).strip()
        if not text:
            continue
        words.append({"t": text, "s": float(w["start"]), "e": float(w["end"])})
    if not words:
        sys.exit("No words with timestamps found")
    words.sort(key=lambda x: x["s"])
    return words


def norm(tok):
    return re.sub(r"[^\w]", "", tok.lower(), flags=re.UNICODE)


def apply_script(words, script_text):
    """Replace recognized words with authored words, keeping audio times.
    Works when authored and recognized tokens align (same count inside each differing block)."""
    authored = script_text.split()
    rec = [norm(w["t"]) for w in words]
    aut = [norm(t) for t in authored]
    sm = difflib.SequenceMatcher(a=rec, b=aut, autojunk=False)
    out = []
    warned = False
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                w = dict(words[i1 + k])
                w["t"] = authored[j1 + k]
                out.append(w)
        elif tag == "replace" and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                w = dict(words[i1 + k])
                w["t"] = authored[j1 + k]
                out.append(w)
        else:
            warned = True
            for k in range(i1, i2):
                out.append(dict(words[k]))
            if tag in ("insert", "replace"):
                print("WARN: script/transcript mismatch near recognized words %d-%d "
                      "(authored %r vs heard %r); kept recognized words"
                      % (i1, i2, " ".join(authored[j1:j2]), " ".join(w["t"] for w in words[i1:i2])),
                      file=sys.stderr)
    ratio = sm.ratio()
    print("script similarity: %.2f" % ratio, file=sys.stderr)
    if ratio < 0.90:
        print("WARN: similarity below 0.90, re-run alignment (larger model or per-block) before styling",
              file=sys.stderr)
    if warned:
        print("WARN: some words were not replaced; check them by hand", file=sys.stderr)
    return out


def chunk(words, max_words, max_chars, pause_break):
    cues, cur = [], []

    def text_len(ws):
        return len(" ".join(w["t"] for w in ws))

    for i, w in enumerate(words):
        if cur:
            gap = w["s"] - cur[-1]["e"]
            too_many = len(cur) + 1 > max_words
            too_long = text_len(cur + [w]) > max_chars
            if gap >= pause_break or too_many or too_long:
                cues.append(cur)
                cur = []
        cur.append(w)
        if re.search(r"[.!?…]$", w["t"]):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    return cues


def balance(text):
    ws = text.split()
    if len(ws) < 3 or len(text) < 18:
        return text
    best, best_diff = 1, 10 ** 9
    for k in range(1, len(ws)):
        a, b = " ".join(ws[:k]), " ".join(ws[k:])
        d = abs(len(a) - len(b))
        if d < best_diff:
            best, best_diff = k, d
    return " ".join(ws[:best]) + "\n" + " ".join(ws[best:])


def fmt(t):
    t = max(0.0, t)
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def build(cues, bridge, tail, min_dur, case, lines):
    out = []
    for idx, ws in enumerate(cues):
        start = ws[0]["s"]
        end = ws[-1]["e"]
        if idx + 1 < len(cues):
            nxt = cues[idx + 1][0]["s"]
            gap = nxt - end
            if gap <= bridge:
                end = nxt  # continuous speech: hold until the next cue appears
            else:
                end = min(end + tail, nxt)  # real pause: linger briefly, never across the pause
        else:
            end = end + tail
        if end - start < min_dur:
            end = start + min_dur
            if idx + 1 < len(cues):
                end = min(end, cues[idx + 1][0]["s"])
        text = " ".join(w["t"] for w in ws)
        if case == "upper":
            text = text.upper()
        elif case == "lower":
            text = text.lower()
        if lines == 2:
            text = balance(text)
        out.append((start, end, text))
    # enforce no overlap
    fixed = []
    for i, (s, e, t) in enumerate(out):
        if i + 1 < len(out) and e > out[i + 1][0]:
            e = out[i + 1][0]
        if e > s:
            fixed.append((s, e, t))
    return fixed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="word-timestamp JSON")
    ap.add_argument("-o", "--out", default="-", help="output .srt path (default stdout)")
    ap.add_argument("--max-words", type=int, default=5)
    ap.add_argument("--max-chars", type=int, default=32)
    ap.add_argument("--pause-break", type=float, default=0.5, help="start a new cue after a gap this long (s)")
    ap.add_argument("--bridge", type=float, default=0.5, help="hold a cue to the next one if the gap is at most this (s)")
    ap.add_argument("--tail", type=float, default=0.3, help="linger after last word before a real pause (s)")
    ap.add_argument("--min-dur", type=float, default=0.6, help="minimum cue duration (s)")
    ap.add_argument("--case", choices=["original", "upper", "lower"], default="original")
    ap.add_argument("--lines", type=int, choices=[1, 2], default=1, help="2 inserts a balanced line break")
    ap.add_argument("--script", help="text file with the authored words (spelling source only)")
    a = ap.parse_args()

    words = load_words(a.input)
    if a.script:
        with open(a.script, encoding="utf-8") as f:
            words = apply_script(words, f.read())
    cues = chunk(words, a.max_words, a.max_chars, a.pause_break)
    srt = build(cues, a.bridge, a.tail, a.min_dur, a.case, a.lines)
    body = []
    for n, (s, e, t) in enumerate(srt, 1):
        body.append("%d\n%s --> %s\n%s\n" % (n, fmt(s), fmt(e), t))
    text = "\n".join(body)
    if a.out == "-":
        sys.stdout.write(text)
    else:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote %s (%d cues, %d words)" % (a.out, len(srt), len(words)), file=sys.stderr)


if __name__ == "__main__":
    main()
