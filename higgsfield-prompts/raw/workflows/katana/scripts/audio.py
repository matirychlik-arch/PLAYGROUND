#!/usr/bin/env python3
"""audio.py - reference audio forensics for katana (stdlib + numpy + ffmpeg; no scipy/librosa).

Subcommands (W = project workspace, e.g. /home/user/rr/<slug>):
  extract W [--src PATH]
      ref audio -> W/audio/ref.wav (22050 Hz mono s16, aligned to video t=0), W/audio/ref_orig.<ext>
      (stream copy, for muxing the final without re-encoding) and W/audio/ref_audio.json.
  beats W [--audio PATH] [--start S] [--dur D] [--bpm X] [--bpm-min A --bpm-max B] [--fps F]
      -> W/audio/beats.json + beats.jpg timeline strip (or beats_<name>.json/.jpg with --audio):
      bpm, period, phase (grid t(b) = phase + b*period), beats, downbeats, onsets, strong_onsets,
      low_onsets (<150 Hz), sections [{t0,t1,label,db}], silence, loudness {I, LRA, TP} (ffmpeg
      ebur128=peak=true), octave (half/double/4:3) decision with a confidence, *_frames at the ref fps.
  cutsync W [--beats PATH] [--analysis PATH | --cuts f,f,f] [--tol 2]
      cut list (analysis/analysis.json cuts[].f0) vs beats -> W/audio/cutsync.json + cutsync.jpg:
      per cut the nearest beat / onset / strong / low / downbeat offset in frames, shares within
      +-tol frames next to the share random cuts would get, cut lead, BPM octave check from intervals.
  align W --track SONG [--ref-audio PATH] [--win 4] [--hop 0.5] [--residual OUT.wav]
      where does a known song sit inside the ref audio? windowed normalised cross-correlation
      (8 kHz search, 22.05 kHz sub-sample refinement, Viterbi over windows) -> W/audio/align.json:
      segments [{ref_t0, ref_t1, song_t0, song_t1, song_offset, ncc, gain_db, residual_db}],
      hidden_edits (splices, ~ms accurate), speed check (sped-up / time-stretched refs), and SFX
      candidates (what the ref adds on top of the song, STFT-magnitude residual).
  slice SRC (--seg T0:T1[:NAME] ... | --segs-json F | --from-align ALIGN.json) [--out-dir D] [--concat OUT]
      cut word / segment clips by explicit times with fades (--snap: cut at the quietest point
      nearby), join them with equal-power crossfades, or rebuild the ref's music edit from a song.

Conventions: seconds; a cut at frame f starts at t = f/fps; beat_frames = round(t*fps); song_t =
ref_t + song_offset. Every JSON has a "schema" key. Exit 1 = bad input, 3 = no audio stream.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

try:
    import rrio  # noqa: E402
except Exception:  # pragma: no cover - rrio ships next to this file
    rrio = None

FFMPEG = os.environ.get("RR_FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("RR_FFPROBE", "ffprobe")
SR = 22050
EPS = 1e-12


class AudioError(Exception):
    def __init__(self, msg, code=1):
        super().__init__(msg)
        self.code = code


# ----------------------------------------------------------------------------------------------------
# small utils
# ----------------------------------------------------------------------------------------------------
def r3(x):
    return None if x is None or not math.isfinite(float(x)) else round(float(x), 3)


def r4(x):
    return None if x is None or not math.isfinite(float(x)) else round(float(x), 4)


def db(x, floor=-120.0):
    return max(floor, 10.0 * math.log10(max(float(x), 1e-30)))


def jsonable(o):
    if rrio is not None:
        return rrio.jsonable(o)
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return float(o) if math.isfinite(float(o)) else None
    return o


def save_json(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if rrio is not None:
        return rrio.save_json(path, obj)
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(jsonable(obj), f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)
    return path


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ffprobe_json(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise AudioError(f"ffprobe failed for {path}: {r.stderr.strip()[-400:]}")
    return json.loads(r.stdout or "{}")


def _fnum(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def stream_info(path):
    """Audio + video stream facts needed for alignment and muxing."""
    j = ffprobe_json(path)
    st = j.get("streams", [])
    fmt = j.get("format", {})
    a = next((s for s in st if s.get("codec_type") == "audio"), None)
    v = next((s for s in st if s.get("codec_type") == "video"
              and not (s.get("disposition") or {}).get("attached_pic")), None)
    info = {"path": path, "format_name": fmt.get("format_name"), "format_duration": _fnum(fmt.get("duration")),
            "has_audio": a is not None, "has_video": v is not None}
    if a is not None:
        info.update({"audio_index": a.get("index"), "codec": a.get("codec_name"),
                     "profile": a.get("profile"), "sample_rate": int(a.get("sample_rate") or 0) or None,
                     "channels": a.get("channels"), "channel_layout": a.get("channel_layout"),
                     "bit_rate": int(a["bit_rate"]) if str(a.get("bit_rate", "")).isdigit() else None,
                     "audio_duration": _fnum(a.get("duration")), "audio_start": _fnum(a.get("start_time")) or 0.0})
    if v is not None:
        fps = None
        nbf = None
        try:
            if rrio is not None:
                p = rrio.probe(path)
                fps = p.get("fps_str")
                nbf = p.get("nb_frames")
        except Exception:
            fps = None
        if fps is None:
            fps = v.get("avg_frame_rate") or v.get("r_frame_rate")
        if nbf is None and str(v.get("nb_frames", "")).isdigit():
            nbf = int(v["nb_frames"])
        info.update({"video_start": _fnum(v.get("start_time")) or 0.0, "fps": fps, "nb_frames": nbf,
                     "video_duration": _fnum(v.get("duration"))})
    return info


def parse_fps(v):
    if v is None:
        return None
    if rrio is not None:
        f = rrio.parse_fps(v)
        return float(f) if f else None
    s = str(v)
    if "/" in s:
        n, d = s.split("/", 1)
        return float(n) / float(d) if float(d) else None
    return float(s)


def decode(path, sr=SR, mono=True, channels=None):
    """Decode any media's first audio stream to float32 at `sr` (mono, or N channels -> (n, ch))."""
    ch = 1 if mono else int(channels or 2)
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-i", path, "-map", "0:a:0", "-vn",
           "-ac", str(ch), "-ar", str(int(sr)), "-f", "f32le", "-acodec", "pcm_f32le", "-"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        msg = r.stderr.decode("utf-8", "replace").strip()[-400:]
        if "matches no streams" in msg or "Stream map" in msg:
            raise AudioError(f"no audio stream in {path}", 3)
        raise AudioError(f"ffmpeg could not decode audio from {path}: {msg}")
    y = np.frombuffer(r.stdout, dtype="<f4").astype(np.float32)
    if ch > 1:
        y = y[: len(y) // ch * ch].reshape(-1, ch)
    return y


def write_audio(path, y, sr, codec_args=None):
    """Write float audio (n,) or (n, ch). .wav -> PCM s16 via the wave module; anything else via ffmpeg."""
    y = np.asarray(y, dtype=np.float32)
    if y.ndim == 1:
        y = y[:, None]
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    tmp = path + ".part" + os.path.splitext(path)[1]
    if path.lower().endswith(".wav") and not codec_args:
        pcm = np.clip(np.round(y * 32767.0), -32768, 32767).astype("<i2")
        with wave.open(tmp, "wb") as wf:
            wf.setnchannels(y.shape[1])
            wf.setsampwidth(2)
            wf.setframerate(int(sr))
            wf.writeframes(pcm.tobytes())
    else:
        ext = os.path.splitext(path)[1].lower()
        if codec_args is None:
            codec_args = {".m4a": ["-c:a", "aac", "-b:a", "256k"], ".aac": ["-c:a", "aac", "-b:a", "256k"],
                          ".mp3": ["-c:a", "libmp3lame", "-b:a", "256k"], ".flac": ["-c:a", "flac"],
                          ".wav": ["-c:a", "pcm_s16le"]}.get(ext, [])
        cmd = [FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(int(sr)),
               "-ac", str(y.shape[1]), "-i", "-", *codec_args, tmp]
        r = subprocess.run(cmd, input=np.ascontiguousarray(y).astype("<f4").tobytes(), capture_output=True)
        if r.returncode != 0:
            raise AudioError("ffmpeg encode failed: " + r.stderr.decode("utf-8", "replace")[-400:])
    os.replace(tmp, path)
    return path


# ----------------------------------------------------------------------------------------------------
# DSP primitives (vectorised numpy)
# ----------------------------------------------------------------------------------------------------
def frames_view(y, n_fft, hop):
    """Centred frames: frame i is centred on sample i*hop (zero padded)."""
    yp = np.pad(np.asarray(y, np.float32), (n_fft // 2, n_fft // 2))
    n = 1 + max(0, (len(yp) - n_fft) // hop)
    s = yp.strides[0]
    return np.lib.stride_tricks.as_strided(yp, shape=(n, n_fft), strides=(hop * s, s), writeable=False)


def stft_power(y, n_fft, hop, chunk=2048):
    fr = frames_view(y, n_fft, hop)
    win = np.hanning(n_fft + 1)[:-1].astype(np.float32)
    out = np.empty((fr.shape[0], n_fft // 2 + 1), np.float32)
    for i in range(0, fr.shape[0], chunk):
        X = np.fft.rfft(fr[i:i + chunk] * win, axis=1)
        out[i:i + chunk] = X.real ** 2 + X.imag ** 2
    return out


def mel_fb(sr, n_fft, n_mels=64, fmin=30.0, fmax=None):
    fmax = min(fmax or sr / 2.0, sr / 2.0)
    hz2mel = lambda f: 2595.0 * np.log10(1.0 + np.asarray(f) / 700.0)  # noqa: E731
    mel2hz = lambda m: 700.0 * (10.0 ** (np.asarray(m) / 2595.0) - 1.0)  # noqa: E731
    hz = mel2hz(np.linspace(hz2mel(fmin), hz2mel(fmax), n_mels + 2))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    fb = np.zeros((n_mels, len(freqs)), np.float32)
    for i in range(n_mels):
        lo, c, hi = hz[i], hz[i + 1], hz[i + 2]
        up = (freqs - lo) / max(c - lo, 1e-9)
        down = (hi - freqs) / max(hi - c, 1e-9)
        fb[i] = np.maximum(0.0, np.minimum(up, down))
        if fb[i].sum() <= 0:  # band narrower than a bin: take the nearest bin
            fb[i, int(np.argmin(np.abs(freqs - c)))] = 1.0
    return fb


def moving_mean(x, n):
    """Centred moving average with edge renormalisation (uniform_filter1d replacement)."""
    n = max(1, int(n))
    if n == 1:
        return x.astype(np.float64)
    c = np.concatenate([[0.0], np.cumsum(x, dtype=np.float64)])
    i = np.arange(len(x))
    lo = np.clip(i - n // 2, 0, len(x))
    hi = np.clip(i - n // 2 + n, 0, len(x))
    return (c[hi] - c[lo]) / np.maximum(hi - lo, 1)


def sliding_max(x, before, after):
    """max(x[i-before : i+after+1]) for every i (edges padded with -inf)."""
    xp = np.pad(x.astype(np.float64), (before, after), constant_values=-np.inf)
    w = before + after + 1
    s = xp.strides[0]
    v = np.lib.stride_tricks.as_strided(xp, shape=(len(x), w), strides=(s, s), writeable=False)
    return v.max(axis=1)


def rms_db_env(y, sr, win_s, hop_s):
    """RMS level in dBFS over windows of win_s every hop_s. Returns (t_centres, db)."""
    win = max(2, int(round(win_s * sr)))
    hop = max(1, int(round(hop_s * sr)))
    c = np.concatenate([[0.0], np.cumsum(np.asarray(y, np.float64) ** 2)])
    if len(y) < win:
        return np.array([len(y) / 2 / sr]), np.array([db(c[-1] / max(1, len(y)))])
    idx = np.arange(0, len(y) - win + 1, hop)
    e = (c[idx + win] - c[idx]) / win
    return (idx + win / 2.0) / sr, 10.0 * np.log10(e + 1e-13)


def band_signal(y, sr, f_lo=None, f_hi=None):
    """Brick-wall FFT band filter of the whole signal (zero phase)."""
    n = len(y)
    nf = 1 << int(math.ceil(math.log2(max(2, n))))
    X = np.fft.rfft(y.astype(np.float64), nf)
    f = np.fft.rfftfreq(nf, 1.0 / sr)
    m = np.ones_like(f)
    if f_lo:
        m *= np.clip((f - f_lo * 0.8) / (f_lo * 0.2), 0, 1)
    if f_hi:
        m *= np.clip((f_hi * 1.25 - f) / (f_hi * 0.25), 0, 1)
    return np.fft.irfft(X * m, nf)[:n].astype(np.float32)


def pick_peaks(x, rate, wait_s=0.05, avg_s=0.12, delta=0.0, thresh=0.0):
    """Indices of local maxima (±wait/2 neighbourhood) above local mean + delta and thresh,
    thinned greedily (strongest first) to a minimum spacing of wait_s."""
    if len(x) < 3:
        return np.zeros(0, int)
    k = max(1, int(round(wait_s * rate / 2)))
    lm = sliding_max(x, k, k)
    la = moving_mean(x, max(1, int(round(avg_s * rate))))
    cand = np.nonzero((x >= lm) & (x > la + delta) & (x > thresh) & (x > 0))[0]
    if len(cand) == 0:
        return cand
    order = cand[np.argsort(-x[cand], kind="stable")]
    wait = max(1, int(round(wait_s * rate)))
    taken = np.zeros(len(x) + 2 * wait + 2, bool)
    keep = []
    for i in order:
        if not taken[i:i + 2 * wait + 1].any():
            keep.append(i)
            taken[i + wait] = True  # mark position i (offset by wait)
    keep = np.array(sorted(keep), int)
    return keep


# ----------------------------------------------------------------------------------------------------
# onset envelope + refinement
# ----------------------------------------------------------------------------------------------------
class OnsetEnv:
    pass


def onset_envelope(y, sr, hop=128, n_fft=1024):
    """Spectral-flux onset envelope (log mel, lag 2) + low band (<150 Hz) flux + band levels."""
    P = stft_power(y, n_fft, hop)
    fb = mel_fb(sr, n_fft, 64, 30.0, min(11000.0, sr / 2.0))
    M = P @ fb.T
    L = 10.0 * np.log10(M + 1e-10)
    L = np.maximum(L, L.max() - 80.0)
    lag = 2
    flux = np.zeros(len(L), np.float32)
    flux[lag:] = np.maximum(0.0, L[lag:] - L[:-lag]).mean(axis=1)
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    lowm = (freqs >= 20) & (freqs < 150)
    lowp = P[:, lowm].sum(axis=1)
    Ll = 10.0 * np.log10(lowp + 1e-10)
    Ll = np.maximum(Ll, Ll.max() - 50.0)
    lflux = np.zeros(len(Ll), np.float32)
    lflux[lag:] = np.maximum(0.0, Ll[lag:] - Ll[:-lag])
    # band powers for sections: low <150, lowmid 150-1k, himid 1k-5k, high >5k
    edges = [(20, 150), (150, 1000), (1000, 5000), (5000, sr / 2)]
    bands = np.stack([P[:, (freqs >= a) & (freqs < b)].sum(axis=1) for a, b in edges], axis=1)
    e = OnsetEnv()
    e.rate = sr / float(hop)
    e.hop = hop
    e.n_fft = n_fft
    e.t = (np.arange(len(flux)) - lag / 2.0) * hop / float(sr)
    e.flux = flux
    e.low = lflux
    e.bands = bands  # power per frame (frame centre times = i*hop/sr)
    e.tb = np.arange(len(flux)) * hop / float(sr)
    # detrended envelopes (remove slow level, ~0.4 s)
    e.env = np.maximum(0.0, flux - moving_mean(flux, int(0.4 * e.rate))).astype(np.float32)
    e.lenv = np.maximum(0.0, lflux - moving_mean(lflux, int(0.4 * e.rate))).astype(np.float32)
    return e


class Refiner:
    """Moves envelope-peak onset times to the steepest rise of a short-window level envelope."""

    def __init__(self, y, sr, win_s=0.004, hop_s=0.001, low=False):
        sig = band_signal(y, sr, None, 150.0) if low else y
        if low:
            win_s, hop_s = 0.012, 0.002
        self.t, self.db = rms_db_env(sig, sr, win_s, hop_s)
        self.hop_s = hop_s
        self.span = max(1, int(round((0.006 if not low else 0.016) / hop_s)))

    def refine(self, t0, before=0.045, after=0.03):
        i0 = int(np.searchsorted(self.t, t0 - before))
        i1 = int(np.searchsorted(self.t, t0 + after))
        k = self.span
        if i1 - i0 <= k + 1 or i1 + k >= len(self.db):
            return t0
        seg = self.db[i0:i1 + k]
        rise = seg[k:] - seg[:-k]
        j = int(np.argmax(rise))
        if rise[j] < 3.0:  # no clear transient: keep the envelope time
            return t0
        return float(self.t[i0 + j] + k * self.hop_s / 2.0)


# ----------------------------------------------------------------------------------------------------
# tempo
# ----------------------------------------------------------------------------------------------------
def fold_scores(env, rate, bpms, nb=48, chunk=160):
    """Mean envelope per phase bin when folding the envelope at each candidate period.
    Returns (ncand, nb) array normalised by the envelope mean (1.0 = no periodic structure)."""
    env = np.asarray(env, np.float64)
    N = len(env)
    mu = env.mean() + EPS
    i = np.arange(N, dtype=np.float64)
    out = np.empty((len(bpms), nb))
    for c0 in range(0, len(bpms), chunk):
        b = np.asarray(bpms[c0:c0 + chunk], np.float64)
        p = 60.0 / b * rate
        ph = np.mod(i[None, :] / p[:, None], 1.0)
        bins = np.minimum((ph * nb).astype(np.int64), nb - 1) + (np.arange(len(b)) * nb)[:, None]
        w = np.broadcast_to(env, bins.shape)
        s = np.bincount(bins.ravel(), weights=w.ravel(), minlength=len(b) * nb)
        n = np.bincount(bins.ravel(), minlength=len(b) * nb)
        out[c0:c0 + len(b)] = (s / np.maximum(n, 1)).reshape(len(b), nb)
    k = np.array([1, 2, 3, 2, 1], np.float64) / 9.0
    sm = sum(k[j] * np.roll(out, j - 2, axis=1) for j in range(5))
    return sm / mu


def tempo_prior(bpm, center=120.0, sigma=1.0):
    return np.exp(-0.5 * (np.log2(np.asarray(bpm, np.float64) / center) / sigma) ** 2)


def estimate_tempo(env, rate, bpm_min=60.0, bpm_max=200.0, fixed_bpm=None, onsets=None, weights=None):
    """Fold-score tempogram over 30..300 BPM, metrical family of the strongest pulse, octave choice by
    a log-normal prior (centre 120 BPM) times the fold score, with a half-beat support check."""
    out = {}
    if fixed_bpm:
        bpms = np.array([float(fixed_bpm)])
        F = fold_scores(env, rate, bpms)
        R = F.max(axis=1) - 1.0
        out.update(bpm=float(fixed_bpm), score=float(R[0]), candidates=[], family=[], octave_margin=None,
                   method="fixed")
        return out
    lo, hi = 30.0, 300.0
    bpms = np.exp(np.arange(np.log(lo), np.log(hi), 0.0015))  # ~0.15% steps
    F = fold_scores(env, rate, bpms)
    R = F.max(axis=1) - 1.0
    # local maxima of R
    lm = sliding_max(R, 6, 6)
    pk = np.nonzero((R >= lm) & (R > 0))[0]
    if len(pk) == 0:
        out.update(bpm=None, score=0.0, candidates=[], family=[], octave_margin=None, method="fold")
        return out
    pk = pk[np.argsort(-R[pk])][:12]
    cands = [{"bpm": float(bpms[j]), "score": float(R[j])} for j in pk]

    def score_at(b):
        """Best fold score within ±1.2 % of b (local refinement)."""
        if b < lo or b > hi:
            return 0.0, b
        sel = np.nonzero(np.abs(np.log(bpms / b)) <= 0.012)[0]
        if len(sel) == 0:
            return 0.0, b
        j = sel[int(np.argmax(R[sel]))]
        return float(R[j]), float(bpms[j])

    on_t = np.asarray(onsets if onsets is not None else [], np.float64)
    on_w = np.asarray(weights if weights is not None else np.ones(len(on_t)), np.float64)

    def subdiv(b):
        """Onset weight at the half / third / quarter positions between this level's beats, relative to
        the weight on the beats (phase from the fold). Returns (half, best_subdivision)."""
        Fb = fold_scores(env, rate, np.array([b]))[0]
        nb = len(Fb)
        per = 60.0 / b
        ph = (int(np.argmax(Fb)) + 0.5) / nb * per
        if len(on_t) < 4:
            return 1.0, 1.0
        x = np.mod((on_t - ph) / per, 1.0)
        tol = max(0.025 / per, 0.04)

        def near(pos):
            d = np.abs(x - pos)
            d = np.minimum(d, 1.0 - d)
            return float(on_w[d <= tol].sum())

        beat = max(near(0.0), EPS)
        half = near(0.5) / beat
        third = (near(1 / 3.0) + near(2 / 3.0)) / 2.0 / beat
        quarter = (near(0.25) + near(0.75)) / 2.0 / beat
        return float(min(half, 2.0)), float(min(max(half, third, quarter), 2.0))

    # family of the strongest pulse (metrical relatives) + strong independent candidates in range
    best0 = max(cands, key=lambda c: c["score"])
    ratios = [0.25, 1 / 3.0, 0.5, 2 / 3.0, 0.75, 1.0, 4 / 3.0, 1.5, 2.0, 3.0, 4.0]
    fam = []
    for rt in ratios:
        s, b = score_at(best0["bpm"] * rt)
        if bpm_min <= b <= bpm_max and s > 0 and not any(abs(math.log(b / f["bpm"])) < 0.012 for f in fam):
            fam.append({"bpm": b, "ratio": rt, "score": s})
    for c in cands:
        if bpm_min <= c["bpm"] <= bpm_max and not any(abs(math.log(c["bpm"] / f["bpm"])) < 0.012 for f in fam):
            fam.append({"bpm": c["bpm"], "ratio": c["bpm"] / best0["bpm"], "score": c["score"]})
    if not fam:  # nothing inside the range: fold the best into it by octaves
        b = best0["bpm"]
        while b < bpm_min:
            b *= 2
        while b > bpm_max:
            b /= 2
        s, b = score_at(b)
        fam = [{"bpm": b, "ratio": b / best0["bpm"], "score": s}]
    smax = max(f["score"] for f in fam)
    for f in fam:
        f["prior"] = float(tempo_prior(f["bpm"]))
        f["half_support"], f["sub_support"] = subdiv(f["bpm"])
        pen, why = 1.0, []
        # nothing between this level's beats -> it is the fastest pulse (tatum): the beat is slower
        slower = [g for g in fam if g is not f and g["score"] >= 0.5 * f["score"] and
                  any(abs(math.log(g["bpm"] * k / f["bpm"])) < 0.015 for k in (2.0, 3.0))]
        if f["sub_support"] < 0.2 and (slower or any(bpm_min <= f["bpm"] / k for k in (2.0, 3.0))):
            pen *= 0.45
            why.append("tatum")
        # the half-beat position is as strong as the beat -> the double tempo is the pulse
        if f["half_support"] >= 0.8 and f["bpm"] * 2 <= bpm_max:
            pen *= 0.7
            why.append("half-beat as strong as the beat")
        if f["score"] < 0.35 * smax:
            pen *= 0.5
            why.append("weak")
        f["penalty"] = pen
        f["why"] = why
        f["final"] = f["score"] * f["prior"] * pen
    fam.sort(key=lambda f: -f["final"])
    chosen = fam[0]
    notes = [f"{f['bpm']:.1f}: {', '.join(f['why'])}" for f in fam if f["why"]][:4]
    others = [f for f in fam if f is not chosen]
    second = max((f["final"] for f in others), default=0.0)
    margin = chosen["final"] / max(second, EPS) - 1.0 if others else 1.0
    out.update(bpm=chosen["bpm"], score=chosen["score"], candidates=cands[:8], family=fam,
               octave_margin=float(margin), half_support=chosen["half_support"],
               sub_support=chosen["sub_support"], notes=notes, method="fold+prior+tatum")
    return out


def fit_grid(onset_t, onset_w, period, phase0, dur, tol_frac=0.12, iters=3, div=1):
    """Weighted least squares t = phase + x*period over onsets near grid lines, where x is a whole beat
    (div=1) or a 1/div subdivision (div=4: 16ths, more data points in syncopated music).
    Returns (period, phase, used_count, residual_ms_median)."""
    per, ph = float(period), float(phase0)
    used = 0
    med = None
    for _ in range(iters):
        n = np.round((onset_t - ph) / (per / div)) / div
        res = onset_t - (ph + n * per)
        if div == 1:
            tol = max(0.03, tol_frac * per) if _ == 0 else max(0.022, 0.07 * per)
        else:
            tol = min(0.025, 0.2 * per / div)
        m = np.abs(res) <= tol
        used = int(m.sum())
        if used < 4:
            break
        x = n[m]
        yv = onset_t[m]
        w = onset_w[m]
        A = np.stack([np.ones_like(x), x], axis=1) * np.sqrt(w)[:, None]
        sol, *_ = np.linalg.lstsq(A, yv * np.sqrt(w), rcond=None)
        ph_new, per_new = float(sol[0]), float(sol[1])
        if not (0.9 * per < per_new < 1.1 * per):
            break
        ph, per = ph_new, per_new
        med = float(np.median(np.abs(yv - (ph + x * per)))) * 1000.0
    return per, ph, used, med


def grid_phase_from_fold(env, rate, bpm):
    F = fold_scores(env, rate, np.array([bpm]), nb=96)[0]
    j = int(np.argmax(F))
    period = 60.0 / bpm
    return (j + 0.5) / 96.0 * period  # time of the first grid line (env frame time base)


def dp_track(env, rate, period_s, tightness=80.0):
    """Ellis-style dynamic-programming beat tracker (used when a fixed grid drifts)."""
    p = period_s * rate
    N = len(env)
    lo, hi = int(round(2 * p)), max(1, int(round(p / 2)))
    if N <= lo + 2:
        return np.zeros(0)
    e = env / (env.std() + EPS)
    offs = np.arange(-lo, -hi + 1)
    tx = -tightness * np.log(-offs / p) ** 2
    score = e.astype(np.float64).copy()
    back = -np.ones(N, int)
    for i in range(lo, N):
        c = score[i + offs] + tx
        j = int(np.argmax(c))
        score[i] = e[i] + c[j]
        back[i] = i + offs[j]
    tail = slice(max(0, N - int(round(p))), N)
    i = int(np.argmax(score[tail])) + tail.start
    beats = []
    while i >= 0:
        beats.append(i)
        i = back[i]
    return np.array(beats[::-1], float) / rate


# ----------------------------------------------------------------------------------------------------
# loudness (ffmpeg ebur128)
# ----------------------------------------------------------------------------------------------------
def ebur128(path, start=None, dur=None):
    def run(extra_opts):
        cmd = [FFMPEG, "-hide_banner", "-nostdin", "-nostats", "-loglevel", "info"]
        if start:
            cmd += ["-ss", f"{start:.6f}"]
        if dur:
            cmd += ["-t", f"{dur:.6f}"]
        cmd += ["-i", path, "-map", "0:a:0", "-vn", "-af", "ebur128=peak=true" + extra_opts, "-f", "null", "-"]
        return subprocess.run(cmd, capture_output=True, text=True, errors="replace")

    r = run(":framelog=verbose")
    if r.returncode != 0:
        r = run("")
    if r.returncode != 0:
        return {"I": None, "LRA": None, "TP": None, "error": r.stderr.strip()[-300:]}
    txt = r.stderr
    k = txt.rfind("Summary:")
    s = txt[k:] if k >= 0 else txt

    def grab(pat):
        m = re.search(pat, s)
        return float(m.group(1)) if m else None

    out = {"I": grab(r"I:\s*(-?[\d.]+|-inf)\s*LUFS"), "LRA": grab(r"LRA:\s*(-?[\d.]+)\s*LU"),
           "TP": grab(r"Peak:\s*(-?[\d.]+|-inf)\s*dBFS"), "threshold": grab(r"Threshold:\s*(-?[\d.]+)\s*LUFS"),
           "LRA_low": grab(r"LRA low:\s*(-?[\d.]+)"), "LRA_high": grab(r"LRA high:\s*(-?[\d.]+)"),
           "unit": {"I": "LUFS", "LRA": "LU", "TP": "dBTP"}, "tool": "ffmpeg ebur128=peak=true"}
    return out


# ----------------------------------------------------------------------------------------------------
# workspace helpers
# ----------------------------------------------------------------------------------------------------
def ws_paths(W):
    W = os.path.abspath(W)
    return {"W": W, "audio": os.path.join(W, "audio"), "ref_mp4": os.path.join(W, "ref", "ref.mp4"),
            "ref_json": os.path.join(W, "ref", "ref.json"), "ref_wav": os.path.join(W, "audio", "ref.wav"),
            "ref_audio_json": os.path.join(W, "audio", "ref_audio.json"),
            "beats": os.path.join(W, "audio", "beats.json"), "analysis": os.path.join(W, "analysis", "analysis.json"),
            "cutsync": os.path.join(W, "audio", "cutsync.json"), "align": os.path.join(W, "audio", "align.json")}


def find_ref_video(W):
    p = ws_paths(W)
    if os.path.exists(p["ref_mp4"]):
        return p["ref_mp4"]
    refdir = os.path.join(p["W"], "ref")
    if os.path.isdir(refdir):
        for n in sorted(os.listdir(refdir)):
            if n.startswith("ref.") and n.rsplit(".", 1)[-1].lower() in ("mp4", "mov", "webm", "mkv", "m4v"):
                return os.path.join(refdir, n)
    return None


def ref_fps(W):
    """(fps float, fps string, nb_frames) of the reference video, or (None, None, None)."""
    p = ws_paths(W)
    for src in (p["ref_json"], os.path.join(p["W"], "analysis", "analysis.json")):
        if os.path.exists(src):
            try:
                j = load_json(src)
                fps = j.get("fps") or (j.get("ref") or {}).get("fps") or (j.get("video") or {}).get("fps")
                nb = j.get("nb_frames") or (j.get("ref") or {}).get("nb_frames") or j.get("frames")
                if fps:
                    f = parse_fps(fps)
                    if f:
                        return f, str(fps), nb
            except Exception:
                pass
    v = find_ref_video(W)
    if v:
        try:
            si = stream_info(v)
            if si.get("fps"):
                return parse_fps(si["fps"]), str(si["fps"]), si.get("nb_frames")
        except AudioError:
            pass
    return None, None, None


# ----------------------------------------------------------------------------------------------------
# extract
# ----------------------------------------------------------------------------------------------------
ORIG_EXT = {"aac": "m4a", "alac": "m4a", "mp3": "mp3", "opus": "mka", "vorbis": "ogg", "flac": "flac",
            "ac3": "ac3", "eac3": "eac3", "pcm_s16le": "wav", "pcm_s24le": "wav", "pcm_f32le": "wav"}


def do_extract(W, src=None, sr=SR, quiet=False):
    p = ws_paths(W)
    src = src or find_ref_video(W)
    if not src or not os.path.exists(src):
        raise AudioError(f"no reference media: pass --src or put the video at {p['ref_mp4']}")
    os.makedirs(p["audio"], exist_ok=True)
    si = stream_info(src)
    info = {"schema": "rr.ref_audio/1", "src": os.path.abspath(src), **{k: v for k, v in si.items() if k != "path"}}
    if not si["has_audio"]:
        info.update(wav=None, note="the reference has no audio stream")
        save_json(p["ref_audio_json"], info)
        raise AudioError(f"no audio stream in {src} (wrote {p['ref_audio_json']})", 3)
    y = decode(src, sr)
    # align to video t=0: audio that starts later than the video gets leading silence, earlier gets trimmed
    off = 0.0
    if si.get("has_video"):
        off = float(si.get("audio_start") or 0.0) - float(si.get("video_start") or 0.0)
    n_off = int(round(off * sr))
    if n_off > 0:
        y = np.concatenate([np.zeros(n_off, np.float32), y])
    elif n_off < 0:
        y = y[-n_off:]
    write_audio(p["ref_wav"], y, sr)
    # stream copy of the original audio (for muxing the final without re-encoding)
    ext = ORIG_EXT.get(si.get("codec") or "", "mka")
    orig = os.path.join(p["audio"], "ref_orig." + ext)
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", "-i", src, "-map", "0:a:0",
                        "-vn", "-c:a", "copy", orig], capture_output=True)
    if r.returncode != 0:
        orig = None
    peak = float(np.max(np.abs(y))) if len(y) else 0.0
    rms = float(np.sqrt(np.mean(np.asarray(y, np.float64) ** 2))) if len(y) else 0.0
    info.update({"wav": p["ref_wav"], "wav_sr": sr, "wav_channels": 1, "wav_samples": int(len(y)),
                 "wav_duration": r4(len(y) / sr), "offset_applied_s": r4(off), "orig_copy": orig,
                 "peak_dbfs": r3(20 * math.log10(max(peak, 1e-9))), "rms_dbfs": r3(20 * math.log10(max(rms, 1e-9)))})
    vd = si.get("video_duration")
    ad = len(y) / float(sr)  # decoded length (container durations lie for HE-AAC priming)
    cad = si.get("audio_duration")
    if vd and (abs(ad - vd) > 0.02 or (cad and abs(cad - vd) > 0.04)):
        info["length_note"] = (f"decoded audio {ad:.3f} s (container says {cad if cad is None else round(cad, 3)} s)"
                               f" vs video {vd:.3f} s: the edit length is the VIDEO frame count "
                               f"({si.get('nb_frames')} frames)")
    save_json(p["ref_audio_json"], info)
    if not quiet:
        print(f"extract: {src}")
        print(f"  audio {si.get('codec')} {si.get('sample_rate')} Hz x{si.get('channels')}  "
              f"dur {si.get('audio_duration')}  start offset vs video {off:+.4f} s")
        print(f"  wrote {p['ref_wav']} ({sr} Hz mono, {len(y) / sr:.3f} s, peak {info['peak_dbfs']} dBFS)")
        if orig:
            print(f"  wrote {orig} (stream copy)")
        if info.get("length_note"):
            print("  note: " + info["length_note"])
        print(f"  wrote {p['ref_audio_json']}")
    return info


def cmd_extract(a):
    do_extract(a.W, a.src, a.sr)


# ----------------------------------------------------------------------------------------------------
# beats
# ----------------------------------------------------------------------------------------------------
def analyse_sections(y, sr, oe, dur, beats, onsets_strong, silence):
    """Level/timbre novelty -> boundaries refined to the sharpest level step -> labelled sections."""
    # 50 ms band-level features from the onset STFT
    blk = max(1, int(round(0.05 * oe.rate)))
    nblk = len(oe.bands) // blk
    if nblk < 6:
        tdb, ldb = rms_db_env(y, sr, 0.1, 0.05)
        lv = 10 * math.log10(float(np.mean(10 ** (ldb / 10.0))) + 1e-13) if len(ldb) else -120.0
        return [{"t0": 0.0, "t1": r3(dur), "label": "loud", "db": r3(lv), "rel_db": 0.0, "step_db": None,
                 "beat0": 0 if beats is not None and len(beats) else None}]
    Bp = oe.bands[: nblk * blk].reshape(nblk, blk, -1).mean(axis=1)
    Fdb = 10 * np.log10(Bp + 1e-10)
    Fdb = np.maximum(Fdb, Fdb.max() - 60.0)
    tot = 10 * np.log10(Bp.sum(axis=1) + 1e-10)
    tf = (np.arange(nblk) + 0.5) * blk / oe.rate
    feats = np.concatenate([Fdb, tot[:, None]], axis=1)
    c = np.concatenate([np.zeros((1, feats.shape[1])), np.cumsum(feats, axis=0)], axis=0)
    nov = np.zeros(nblk)
    for wsec, wt in ((0.6, 1.0), (1.5, 1.0)):
        w = max(2, int(round(wsec / 0.05)))
        i = np.arange(nblk)
        a0 = np.clip(i - w, 0, nblk)
        b1 = np.clip(i + w, 0, nblk)
        nl = np.maximum(i - a0, 1)[:, None]
        nr = np.maximum(b1 - i, 1)[:, None]
        left = (c[i] - c[a0]) / nl
        right = (c[b1] - c[i]) / nr
        d = np.sqrt(np.mean((right - left) ** 2, axis=1))
        d[(i - a0) < w // 2] = 0
        d[(b1 - i) < w // 2] = 0
        nov = np.maximum(nov, wt * d)
    pk = pick_peaks(nov, 20.0, wait_s=1.0, avg_s=2.0, delta=0.5, thresh=4.0)
    # refine each boundary to the sharpest level step (10 ms resolution)
    th, ldb = rms_db_env(y, sr, 0.02, 0.005)
    span = int(round(0.12 / 0.005))
    cl = np.concatenate([[0.0], np.cumsum(ldb)])
    bounds = []
    for j in pk:
        t = tf[j]
        i0 = int(np.searchsorted(th, t - 0.35))
        i1 = int(np.searchsorted(th, t + 0.35))
        best, bt = 0.0, t
        for i in range(max(span, i0), min(len(ldb) - span, i1)):
            step = (cl[i + span] - cl[i]) / span - (cl[i] - cl[i - span]) / span
            if abs(step) > abs(best):
                best, bt = step, th[i] - 0.0025
        # snap a rising boundary to an onset within 50 ms (a drop starts on its hit)
        if len(onsets_strong) and best > 0:
            k = int(np.argmin(np.abs(onsets_strong - bt)))
            if abs(onsets_strong[k] - bt) <= 0.05:
                bt = float(onsets_strong[k])
        bounds.append(bt)
    # silences become their own sections; their edges win over nearby novelty boundaries
    sil_edges = sorted(set(round(float(e), 3) for s in silence for e in (s["t0"], s["t1"]) if 0.0 < e < dur))
    merged = list(sil_edges)
    for b in sorted(set(round(b, 3) for b in bounds if 0.05 < b < dur - 0.05)):
        if all(abs(b - m) >= 0.2 for m in merged):
            merged.append(b)
    merged.sort()
    edges = [0.0] + merged + [dur]
    pw = 10 ** (ldb / 10.0)

    def seg_db(a, b):
        m = (th >= a) & (th < b)
        return 10 * math.log10(float(pw[m].mean()) + 1e-13) if m.any() else -120.0

    secs = []
    for a, b in zip(edges[:-1], edges[1:]):
        if b - a <= 0.001:
            continue
        is_sil = any(abs(s["t0"] - a) < 0.02 and abs(s["t1"] - b) < 0.02 for s in silence)
        secs.append({"t0": a, "t1": b, "db": seg_db(a, b), "sil": is_sil})
    # merge very short non-silent sections (<0.6 s) into the neighbour with the closer level
    changed = True
    while changed and len(secs) > 1:
        changed = False
        for k, s in enumerate(secs):
            if s["sil"] or s["t1"] - s["t0"] >= 0.6:
                continue
            nbrs = [j for j in (k - 1, k + 1) if 0 <= j < len(secs) and not secs[j]["sil"]]
            if not nbrs:
                continue
            j = min(nbrs, key=lambda q: abs(secs[q]["db"] - s["db"]))
            a, b = min(secs[j]["t0"], s["t0"]), max(secs[j]["t1"], s["t1"])
            secs[j] = {"t0": a, "t1": b, "db": seg_db(a, b), "sil": False}
            del secs[k]
            changed = True
            break
    # merge neighbours whose level differs by < 2.5 dB (timbre-only boundaries are not edit sections)
    k = 1
    while k < len(secs):
        A, Bq = secs[k - 1], secs[k]
        if not A["sil"] and not Bq["sil"] and abs(A["db"] - Bq["db"]) < 2.5:
            secs[k - 1] = {"t0": A["t0"], "t1": Bq["t1"], "db": seg_db(A["t0"], Bq["t1"]), "sil": False}
            del secs[k]
        else:
            k += 1
    loud = max((s["db"] for s in secs if not s["sil"]), default=-120.0)
    out = []
    prev = None
    for s in secs:
        rel = s["db"] - loud
        if s["sil"]:
            lab = "silence"
        elif rel >= -4.0:
            lab = "loud"
        elif rel >= -10.0:
            lab = "mid"
        else:
            lab = "quiet"
        step = None if prev is None else s["db"] - prev["db"]
        if lab == "loud" and prev is not None and (step >= 6.0 or prev.get("label") in ("silence", "quiet")):
            lab = "drop"
        if lab in ("quiet", "mid") and prev is not None and prev.get("label") in ("loud", "drop") and step <= -6.0:
            lab = "break"
        e = {"t0": r3(s["t0"]), "t1": r3(s["t1"]), "label": lab, "db": r3(s["db"]), "rel_db": r3(rel),
             "step_db": r3(step) if step is not None else None}
        if beats is not None and len(beats):
            k = int(np.argmin(np.abs(beats - s["t0"])))
            e["beat0"] = int(k) if abs(beats[k] - s["t0"]) <= 0.07 else None
        out.append(e)
        prev = {"db": s["db"], "label": lab}
    return out


def find_silence(y, sr, dur, min_len=0.25, rel_db=-30.0, onsets=None):
    """Gaps: 40 ms RMS more than 30 dB under the track's loud level (p95), or under -60 dBFS, for at
    least min_len. These are the musical 'dead air' moments (Katana: 13.06-13.74 before the drop)."""
    th, ldb = rms_db_env(y, sr, 0.04, 0.005)
    if len(ldb) == 0:
        return [], None
    ref = float(np.percentile(ldb, 95))
    thr = max(-60.0, ref + rel_db)
    m = ldb < thr
    out = []
    i = 0
    n = len(m)
    while i < n:
        if m[i]:
            j = i
            while j < n and m[j]:
                j += 1
            t0 = th[i] - 0.0025 if i > 0 else 0.0
            # an abrupt onset lifts the 40 ms window ~20 ms early: the gap ends at the onset itself
            t1 = th[j - 1] + 0.0225 if j < n else dur
            if j < n and onsets is not None and len(onsets):
                k = int(np.argmin(np.abs(onsets - t1)))
                if abs(onsets[k] - t1) <= 0.03:
                    t1 = float(onsets[k])
            raw = (th[j - 1] if j < n else dur) - (th[i] if i > 0 else 0.0) + 0.005
            if raw >= min_len:
                out.append({"t0": r3(max(0.0, t0)), "t1": r3(min(dur, t1)),
                            "db": r3(10 * math.log10(float(np.mean(10 ** (ldb[i:j] / 10.0))) + 1e-13))})
            i = j
        else:
            i += 1
    return out, thr


def strip_plot(path, dur, env_t, env_db, beats=None, downbeats=None, strong=None, low=None, sections=None,
               silence=None, cuts=None, title="", row_sec=None, width=1600):
    """Timeline strip(s) as JPEG: level envelope, beats (top ticks; downbeats tall), strong onsets
    (orange, bottom), low onsets (blue), sections (coloured bands + labels), silence (red), cuts (green)."""
    if rrio is None:
        return None
    row_sec = row_sec or (dur if dur <= 16 else 15.0)
    nrows = max(1, int(math.ceil(dur / row_sec - 1e-9)))
    # lanes inside a row: ruler 0-12, beats 12-30, strong onsets 30-42, low onsets 42-54, level 56-rh
    rh, gap, top = 170, 10, 34
    H = top + nrows * (rh + gap)
    img = np.full((H, width, 3), 18, np.uint8)
    pal = {"silence": (90, 28, 28), "quiet": (30, 38, 62), "mid": (36, 54, 70), "loud": (66, 52, 28),
           "drop": (100, 56, 18), "break": (44, 38, 84)}
    pxs = (width - 20) / row_sec

    def X(t, row):
        return int(round(10 + (t - row * row_sec) * pxs))

    lo, hi = -50.0, 0.0
    for row in range(nrows):
        y0 = top + row * (rh + gap)
        t0, t1 = row * row_sec, min(dur, (row + 1) * row_sec)
        xe = X(t1, row) + 1
        img[y0:y0 + rh, 10:xe] = (28, 28, 28)
        g0, g1 = y0 + 56, y0 + rh
        for s in sections or []:
            a, b = max(s["t0"], t0), min(s["t1"], t1)
            if b > a:
                img[g0:g1, X(a, row):max(X(a, row) + 1, X(b, row))] = pal.get(s["label"], (40, 40, 40))
        # level graph from the bottom (max per pixel column), -50..0 dBFS
        m = (env_t >= t0) & (env_t < t1)
        if m.any():
            cols = np.clip(((env_t[m] - t0) * pxs + 10).astype(int), 0, width - 1)
            vals = np.clip((env_db[m] - lo) / (hi - lo), 0, 1)
            hh = (vals * (g1 - g0 - 14)).astype(int)
            colmax = np.zeros(width, int)
            np.maximum.at(colmax, cols, hh)
            for x in np.nonzero(colmax)[0]:
                img[g1 - colmax[x]:g1, x] = (150, 150, 150)
        for dbl in (-40, -20):
            yy = g1 - int((dbl - lo) / (hi - lo) * (g1 - g0 - 14))
            img[yy, 10:xe:4] = (90, 90, 90)
        for s in silence or []:
            a, b = max(s["t0"], t0), min(s["t1"], t1)
            if b > a:
                img[g1 - 6:g1, X(a, row):max(X(a, row) + 1, X(b, row))] = (230, 50, 50)
        # seconds ruler
        step = 1.0 if row_sec <= 20 else 5.0
        s = math.ceil(t0 / step) * step
        while s <= t1 + 1e-9:
            x = X(s, row)
            img[y0:y0 + rh, x] = np.maximum(img[y0:y0 + rh, x], 48)
            rrio.draw_text(img, f"{s:g}", x + 2, y0 + 2, scale=1, color=(170, 170, 170), bg=None)
            s += step
        for b in beats if beats is not None else []:
            if t0 <= b < t1:
                img[y0 + 18:y0 + 30, X(b, row)] = (230, 230, 110)
        for b in downbeats if downbeats is not None else []:
            if t0 <= b < t1:
                x = X(b, row)
                img[y0 + 12:y0 + 30, max(0, x - 1):x + 1] = (255, 255, 170)
        for o in strong if strong is not None else []:
            if t0 <= o < t1:
                img[y0 + 31:y0 + 42, X(o, row)] = (255, 150, 40)
        for o in low if low is not None else []:
            if t0 <= o < t1:
                img[y0 + 43:y0 + 54, X(o, row)] = (80, 160, 255)
        for c in cuts if cuts is not None else []:
            if t0 <= c < t1:
                x = X(c, row)
                img[y0 + 12:y0 + rh, max(0, x - 1):x + 1] = (60, 230, 90)
        last_x = -999
        for s in sections or []:
            if t0 <= s["t0"] < t1:
                x = X(s["t0"], row) + 3
                lab = s["label"].upper()
                if x - last_x < 6 * len(lab) + 8:
                    continue
                rrio.draw_text(img, lab, x, g0 + 3, scale=1, color=(240, 240, 240), bg=None)
                last_x = x
    rrio.draw_text(img, title[:200], 10, 4, scale=1, color=(235, 235, 235), bg=None)
    rrio.draw_text(img, "BEATS (TALL = DOWNBEAT)   STRONG ONSETS (ORANGE)   LOW <150HZ (BLUE)   CUTS (GREEN)   "
                        "SILENCE (RED)   LEVEL -50..0 DBFS", 10, 18, scale=1, color=(150, 150, 150), bg=None)
    rrio.write_image(path, img, quality=82)
    return path


def do_beats(W, audio=None, start=0.0, dur=None, bpm=None, bpm_min=60.0, bpm_max=200.0, fps=None,
             out=None, png=True, quiet=False):
    p = ws_paths(W)
    t_start = time.time()
    src_media = None
    if audio:
        if not os.path.exists(audio):
            raise AudioError(f"audio file not found: {audio}")
        src = audio
        src_media = audio
        kind = "track"
    else:
        if not os.path.exists(p["ref_wav"]):
            do_extract(W, quiet=quiet)
        src = p["ref_wav"]
        kind = "ref"
        try:
            src_media = load_json(p["ref_audio_json"]).get("src") or find_ref_video(W)
        except Exception:
            src_media = find_ref_video(W)
    y_full = decode(src, SR)
    i0 = int(round(max(0.0, start or 0.0) * SR))
    i1 = len(y_full) if not dur else min(len(y_full), i0 + int(round(dur * SR)))
    y = y_full[i0:i1]
    if len(y) < SR // 2:
        raise AudioError(f"audio too short to analyse ({len(y) / SR:.2f} s)")
    D = len(y) / SR
    oe = onset_envelope(y, SR)
    rate = oe.rate
    ref_full = Refiner(y, SR)
    ref_low = Refiner(y, SR, low=True)
    # onsets (all / strong / low)
    env = oe.env
    p99 = float(np.percentile(env, 99)) if len(env) else 0.0
    # absolute floor 0.5 dB mean-band flux: steady tones / noise floors give ~0.06, real onsets 2-20
    pk = pick_peaks(env, rate, wait_s=0.05, avg_s=0.15, delta=0.04 * p99, thresh=max(0.08 * p99, 0.5))
    on_t = np.array([ref_full.refine(oe.t[i]) for i in pk]) if len(pk) else np.zeros(0)
    on_w = env[pk] if len(pk) else np.zeros(0)
    strong_thr = max(0.35 * p99, float(np.percentile(on_w, 70)) if len(on_w) else 0.0)
    sm = on_w >= strong_thr
    lenv = oe.lenv
    lp99 = float(np.percentile(lenv, 99)) if len(lenv) else 0.0
    lpk = pick_peaks(lenv, rate, wait_s=0.12, avg_s=0.3, delta=0.1 * lp99, thresh=max(0.3 * lp99, 1.5))
    low_t = np.array([ref_low.refine(oe.t[i], before=0.05, after=0.04) for i in lpk]) if len(lpk) else np.zeros(0)
    # tempo (needs some onsets: a pad, a tone or speech-free silence has no pulse)
    if len(pk) < max(4, 0.4 * D) and not bpm:
        tempo = {"bpm": None, "notes": [f"only {len(pk)} onsets in {D:.1f} s: no pulse"]}
    else:
        tempo = estimate_tempo(env[::2] if rate > 120 else env, rate / 2 if rate > 120 else rate,
                               bpm_min, bpm_max, fixed_bpm=bpm, onsets=pk / rate if len(pk) else None,
                               weights=on_w if len(pk) else None)
    beats_out = {}
    if tempo.get("bpm"):
        b0 = tempo["bpm"]
        per0 = 60.0 / b0
        ph0 = grid_phase_from_fold(env, rate, b0) + oe.t[0]
        # least squares on refined onsets (all onsets, weighted by strength)
        per, ph, used, med = fit_grid(on_t, np.maximum(on_w, EPS), per0, ph0, D)
        if not bpm and len(on_t) >= 12:
            # refine on the 16th grid (full-band onsets; the low-band refiner runs ~3 ms early); keep it only
            # when it barely moves the grid
            per2, ph2, used2, med2 = fit_grid(on_t, np.maximum(on_w, EPS), per, ph, D, iters=3, div=4)
            if used2 >= 12 and abs(per2 / per - 1) < 0.004 and abs(ph2 - ph) < 0.02:
                per, ph = per2, ph2
                used, med = used2, med2
        if bpm:  # fixed tempo: keep the period, fit only the phase
            per = per0
            _, ph, used, med = fit_grid(on_t, np.maximum(on_w, EPS), per0, ph, D, iters=1)
            n = np.round((on_t - ph) / per)
            res = on_t - (ph + n * per)
            m = np.abs(res) <= max(0.022, 0.07 * per)
            if m.sum() >= 2:
                ph = ph + float(np.average(res[m], weights=np.maximum(on_w[m], EPS)))
        # bring the phase to the first grid line at or after -0.05 s
        k = math.floor((ph + 0.05) / per)
        ph -= k * per
        if ph < -0.05:
            ph += per
        beats = np.arange(ph, D, per)
        # drift check: phase error in the first vs the second half
        drift = None
        if len(on_t) >= 8:
            n = np.round((on_t - ph) / per)
            res = on_t - (ph + n * per)
            ok = np.abs(res) <= max(0.03, 0.08 * per)
            h1 = ok & (on_t < D / 2)
            h2 = ok & (on_t >= D / 2)
            if h1.sum() >= 3 and h2.sum() >= 3:
                drift = (float(np.median(res[h2])) - float(np.median(res[h1]))) * 1000.0
        grid = "fixed"
        if drift is not None and abs(drift) > 35.0 and not bpm:
            tb = dp_track(env, rate, per)
            if len(tb) >= 4:
                tb = np.array([ref_full.refine(t, before=0.03, after=0.03) for t in tb + oe.t[0]])
                beats = tb
                grid = "tracked"
        # 8th-note grid hit share of strong onsets
        st = on_t[sm]
        if len(st):
            half = per / 2.0
            n2 = np.round((st - ph) / half)
            r2 = np.abs(st - (ph + n2 * half))
            hit8 = float(np.mean(r2 <= 0.035))
            n1 = np.round((st - ph) / per)
            hit4 = float(np.mean(np.abs(st - (ph + n1 * per)) <= 0.035))
        else:
            hit8 = hit4 = 0.0
        beats_out = {"bpm": 60.0 / per, "period": per, "phase": ph, "beats": beats, "grid": grid,
                     "fit": {"onsets_used": used, "median_abs_err_ms": med, "drift_ms": drift,
                             "strong_on_beat_share": hit4, "strong_on_8th_share": hit8}}
    # downbeats: offset k (mod 4) with the most low-band/onset energy + section-start agreement
    snap_t = np.sort(np.concatenate([on_t[on_w >= 0.3 * p99] if len(on_t) else np.zeros(0), low_t]))
    silence, sil_thr = find_silence(y, SR, D, onsets=np.sort(np.concatenate([on_t, low_t])))
    sections = analyse_sections(y, SR, oe, D, beats_out.get("beats"), snap_t, silence)
    downbeats, db_off, db_conf = [], None, None
    if beats_out and len(beats_out["beats"]) >= 8:
        bt = np.asarray(beats_out["beats"])
        idx = np.clip(np.round((bt - oe.t[0]) * rate).astype(int), 0, len(env) - 1)
        win = max(1, int(round(0.03 * rate)))
        lv = np.array([lenv[max(0, i - win):i + win + 1].max() for i in idx])
        ev = np.array([env[max(0, i - win):i + win + 1].max() for i in idx])
        val = lv / (lv.mean() + EPS) + 0.5 * ev / (ev.mean() + EPS)
        sc = np.array([val[k::4].mean() if len(val[k::4]) else 0 for k in range(4)])
        bstarts = [s.get("beat0") for s in sections[1:] if s.get("beat0") is not None and s["label"] != "silence"]
        for b in bstarts:
            sc[b % 4] += 0.6 / max(1, len(bstarts)) * 2.0
        db_off = int(np.argmax(sc))
        srt = np.sort(sc)[::-1]
        db_conf = float(min(1.0, (srt[0] - srt[1]) / max(srt[0], EPS) * 4.0))
        downbeats = bt[db_off::4]
    # loudness on the original media (not the mono 22.05 kHz downmix)
    loud = ebur128(src_media or src, start=start if start else None, dur=dur if dur else None)
    th, ldb = rms_db_env(y, SR, 0.01, 0.005)
    # confidence
    conf = 0.0
    if beats_out:
        sc_ = tempo.get("score") or 0.0
        om = tempo.get("octave_margin")
        om = 1.0 if om is None else om
        fit = beats_out["fit"]
        conf = (0.35 * min(1.0, sc_ / 1.2) + 0.35 * min(1.0, max(0.0, om) / 0.5)
                + 0.30 * fit["strong_on_8th_share"])
        if fit.get("drift_ms") is not None and abs(fit["drift_ms"]) > 35:
            conf *= 0.7
        conf *= min(1.0, (fit.get("onsets_used") or 0) / 12.0)  # few onsets on the grid = weak evidence
        conf = float(max(0.0, min(1.0, conf)))
    fps_f, fps_s, nb = (None, None, None)
    if fps:
        fps_f, fps_s = parse_fps(fps), str(fps)
    else:
        fps_f, fps_s, nb = ref_fps(W)
    res = {"schema": "rr.beats/1", "source": os.path.abspath(src), "source_media": src_media, "kind": kind,
           "sr": SR, "source_offset_s": r4(start or 0.0), "duration": r4(D),
           "time_base": "seconds from the analysed window start (source time = t + source_offset_s)"}
    if beats_out:
        bts = np.asarray(beats_out["beats"])
        res.update({
            "bpm": round(beats_out["bpm"], 2), "period": round(beats_out["period"], 5),
            "phase": r4(beats_out["phase"]),
            "beat_grid": f"t(b) = {beats_out['phase']:.4f} + b*{beats_out['period']:.5f}",
            "grid": beats_out["grid"], "confidence": round(conf, 3),
            "octave": {"chosen": round(beats_out["bpm"], 2), "half": round(beats_out["bpm"] / 2, 2),
                       "double": round(beats_out["bpm"] * 2, 2),
                       "margin": r3(tempo.get("octave_margin")), "half_support": r3(tempo.get("half_support")),
                       "ambiguous": bool(tempo.get("octave_margin") is not None and tempo["octave_margin"] < 0.25),
                       "sub_support": r3(tempo.get("sub_support")),
                       "notes": tempo.get("notes", []),
                       "family": [{"bpm": round(f["bpm"], 2), "score": r3(f["score"]), "prior": r3(f["prior"]),
                                   "half_support": r3(f.get("half_support")), "sub_support": r3(f.get("sub_support")),
                                   "penalty": r3(f.get("penalty")), "final": r3(f["final"])}
                                  for f in tempo.get("family", [])]},
            "alternatives": [{"bpm": round(c["bpm"], 2), "score": r3(c["score"])} for c in tempo.get("candidates", [])],
            "grid_fit": {k: (r3(v) if isinstance(v, float) else v) for k, v in beats_out["fit"].items()},
            "beats": [r4(t) for t in bts],
            "downbeats": [r4(t) for t in downbeats], "downbeat_offset": db_off,
            "downbeat_confidence": r3(db_conf), "meter_assumed": "4/4",
        })
    else:
        res.update({"bpm": None, "period": None, "phase": None, "confidence": 0.0, "beats": [], "downbeats": [],
                    "note": "; ".join(tempo.get("notes") or ["no periodic pulse found"])})
    res.update({
        "onsets": [r4(t) for t in on_t], "onset_strength": [r3(w / max(p99, EPS)) for w in on_w],
        "strong_onsets": [r4(t) for t in on_t[sm]] if len(on_t) else [],
        "low_onsets": [r4(t) for t in low_t],
        "sections": sections, "silence": silence, "silence_threshold_db": r3(sil_thr),
        "loudness": loud, "peak_dbfs": r3(20 * math.log10(max(float(np.max(np.abs(y))), 1e-9))),
        "rms_dbfs": r3(10 * math.log10(float(np.mean(np.asarray(y, np.float64) ** 2)) + 1e-13)),
    })
    if fps_f:
        res["fps"] = fps_s
        res["beat_frames"] = [int(round(t * fps_f)) for t in res["beats"]]
        res["downbeat_frames"] = [int(round(t * fps_f)) for t in res["downbeats"]]
        res["strong_onset_frames"] = [int(round(t * fps_f)) for t in res["strong_onsets"]]
        if nb:
            res["nb_frames"] = nb
    if not out:
        if kind == "ref":
            out = p["beats"]
        else:
            stem = re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.splitext(os.path.basename(src))[0]) or "track"
            out = os.path.join(p["audio"], f"beats_{stem}.json")
    save_json(out, res)
    jpg = None
    if png:
        try:
            jpg = os.path.splitext(out)[0] + ".jpg"
            title = (f"{os.path.basename(src)}  {res.get('bpm')} BPM  grid {res.get('beat_grid', '')}  "
                     f"conf {res.get('confidence')}  I {loud.get('I')} LUFS")
            strip_plot(jpg, D, th, ldb, beats=np.asarray(res["beats"]), downbeats=np.asarray(res["downbeats"]),
                       strong=np.asarray(res["strong_onsets"]), low=np.asarray(res["low_onsets"]),
                       sections=sections, silence=silence, title=title)
        except Exception as e:  # the plot is a convenience, never fatal
            jpg = None
            if not quiet:
                print(f"  (strip plot skipped: {e})")
    if not quiet:
        print(f"beats: {src}  [{start or 0:.2f}s +{D:.2f}s]  ({time.time() - t_start:.1f} s)")
        if res.get("bpm"):
            o = res["octave"]
            print(f"  bpm {res['bpm']}  ({res['beat_grid']})  grid={res['grid']}  confidence {res['confidence']}")
            print(f"  octave: half {o['half']} / double {o['double']}  margin {o['margin']}  "
                  f"ambiguous={o['ambiguous']}  {'; '.join(o['notes'])}")
            gf = res["grid_fit"]
            print(f"  fit: {gf['onsets_used']} onsets, median err {gf['median_abs_err_ms']} ms, drift "
                  f"{gf['drift_ms']} ms, strong on beat {gf['strong_on_beat_share']}, on 8th {gf['strong_on_8th_share']}")
            print(f"  beats {len(res['beats'])}, downbeats {len(res['downbeats'])} (offset {res['downbeat_offset']}, "
                  f"conf {res['downbeat_confidence']})")
        else:
            print("  " + str(res.get("note") or "no periodic pulse found"))
        print(f"  onsets {len(res['onsets'])}, strong {len(res['strong_onsets'])}, low {len(res['low_onsets'])}")
        for s in sections:
            print(f"  section {s['t0']:7.3f}-{s['t1']:7.3f}  {s['label']:<7} {s['db']:6.1f} dB (step {s['step_db']})")
        for s in silence:
            print(f"  silence {s['t0']:.3f}-{s['t1']:.3f} ({s['db']} dB)")
        print(f"  loudness I {loud.get('I')} LUFS  LRA {loud.get('LRA')} LU  TP {loud.get('TP')} dBTP")
        print(f"  wrote {out}" + (f" and {jpg}" if jpg else ""))
    return res


def cmd_beats(a):
    do_beats(a.W, a.audio, a.start, a.dur, a.bpm, a.bpm_min, a.bpm_max, a.fps, a.out, not a.no_png)


# ----------------------------------------------------------------------------------------------------
# cutsync
# ----------------------------------------------------------------------------------------------------
def read_cuts(path, fps):
    """Cut starts from analysis.json / breakdown.json / an EDL: [{f, id, kind, confidence}] sorted by f.
    Accepts cuts[] dicts (f0 | frame | start_frame | f | start, or t0 | t | time | start_s seconds), plain
    frame numbers, or a top-level cut_frames list."""
    j = load_json(path)
    cuts = None
    if isinstance(j, dict):
        for key in ("cuts", "cut_frames", "cut_candidates", "boundaries", "shots"):
            if isinstance(j.get(key), list) and j[key]:
                cuts = j[key]
                break
    elif isinstance(j, list):
        cuts = j
    if not cuts:
        raise AudioError(f"no cut list in {path} (expected a 'cuts' list)")
    out = {}
    for c in cuts:
        f = None
        meta = {}
        if isinstance(c, (int, float)) and not isinstance(c, bool):
            f = int(round(c))
        elif isinstance(c, dict):
            for k in ("f0", "frame", "start_frame", "f", "start"):
                if isinstance(c.get(k), (int, float)) and not isinstance(c.get(k), bool):
                    f = int(round(c[k]))
                    break
            if f is None:
                for k in ("t0", "t", "time", "start_s"):
                    if isinstance(c.get(k), (int, float)):
                        f = int(round(float(c[k]) * fps))
                        break
            meta = {k: c[k] for k in ("id", "kind", "confidence") if k in c}
        if f is not None and f not in out:
            out[f] = {"f": f, **meta}
    return [out[k] for k in sorted(out)]


def nearest(arr, t):
    if arr is None or len(arr) == 0:
        return None, None
    k = int(np.searchsorted(arr, t))
    best = None
    for j in (k - 1, k):
        if 0 <= j < len(arr) and (best is None or abs(arr[j] - t) < abs(arr[best] - t)):
            best = j
    return best, float(arr[best])


def do_cutsync(W, beats_path=None, analysis=None, cuts_arg=None, tol=2.0, fps=None, out=None, png=True, quiet=False):
    p = ws_paths(W)
    beats_path = beats_path or p["beats"]
    if not os.path.exists(beats_path):
        if beats_path == p["beats"]:
            do_beats(W, quiet=True)
        else:
            raise AudioError(f"beats file not found: {beats_path}")
    B = load_json(beats_path)
    fps_f, fps_s, nb = (parse_fps(fps), str(fps), None) if fps else ref_fps(W)
    if not fps_f and B.get("fps"):
        fps_f, fps_s = parse_fps(B["fps"]), B["fps"]
    if not fps_f:
        raise AudioError("unknown fps: pass --fps or provide W/ref/ref.json")
    if cuts_arg:
        try:
            cl = [{"f": f} for f in sorted(set(int(x) for x in re.split(r"[,\s]+", cuts_arg.strip()) if x))]
        except ValueError:
            raise AudioError(f"bad --cuts {cuts_arg!r}: use frame numbers 'f1,f2,...'") from None
        cut_src = "--cuts"
    else:
        analysis = analysis or p["analysis"]
        if not os.path.exists(analysis):
            raise AudioError(f"no cut list: {analysis} is missing (run analyze_ref.py or pass --cuts)")
        cl = read_cuts(analysis, fps_f)
        cut_src = analysis
    cl = [c for c in cl if c["f"] > 0]
    frames = [c["f"] for c in cl]
    if not frames:
        raise AudioError("the cut list has no cuts after frame 0")
    beats = np.asarray(B.get("beats") or [], float)
    per = B.get("period")
    onsets = np.asarray(B.get("onsets") or [], float)
    strength = np.asarray(B.get("onset_strength") or [], float)
    strong = np.asarray(B.get("strong_onsets") or [], float)
    low = np.asarray(B.get("low_onsets") or [], float)
    down = np.asarray(B.get("downbeats") or [], float)
    rows = []
    for c in cl:
        f = c["f"]
        t = f / fps_f
        r = {"f": int(f), "t": r4(t), **{k: v for k, v in c.items() if k != "f"}}
        for name, arr in (("beat", beats), ("onset", onsets), ("strong", strong), ("low", low), ("downbeat", down)):
            k, v = nearest(arr, t)
            if k is None:
                r[name] = None
                continue
            r[name] = {"t": r4(v), "offset_frames": round((t - v) * fps_f, 2)}
            if name == "beat":
                r[name]["b"] = int(k)
            if name == "onset" and len(strength) == len(onsets):
                r[name]["strength"] = r3(strength[k])
        if per and len(beats):
            pos = (t - beats[0]) / per
            r["beat_pos"] = round(pos, 3)
            r["sub16_offset_frames"] = round((pos * 4 - round(pos * 4)) * per / 4 * fps_f, 2)
        rows.append(r)

    def share(name, tol_f):
        v = [abs(r[name]["offset_frames"]) <= tol_f for r in rows if r.get(name)]
        return round(float(np.mean(v)), 3) if v else None

    dur_b = float(B.get("duration") or (frames[-1] / fps_f + 1.0))

    def chance(arr):
        """Share of the timeline within +-tol frames of an event = the hit rate of randomly placed cuts."""
        if arr is None or len(arr) == 0:
            return None
        h = tol / fps_f
        iv = np.stack([np.clip(arr - h, 0, dur_b), np.clip(arr + h, 0, dur_b)], axis=1)
        iv = iv[np.argsort(iv[:, 0])]
        tot, cur0, cur1 = 0.0, iv[0, 0], iv[0, 1]
        for a0, a1 in iv[1:]:
            if a0 > cur1:
                tot += cur1 - cur0
                cur0, cur1 = a0, a1
            else:
                cur1 = max(cur1, a1)
        tot += cur1 - cur0
        return round(tot / dur_b, 3)

    offs = np.array([r["onset"]["offset_frames"] for r in rows if r.get("onset")])
    near = offs[np.abs(offs) <= tol] if len(offs) else offs
    summ = {"cuts": len(rows), "tol_frames": tol,
            "on_beat_share": share("beat", tol), "on_onset_share": share("onset", tol),
            "on_strong_share": share("strong", tol), "on_low_share": share("low", tol),
            "on_downbeat_share": share("downbeat", tol),
            "on_8th_share": None, "on_16th_share": None,
            "chance": {"beat": chance(beats), "onset": chance(onsets), "strong": chance(strong), "low": chance(low),
                       "note": "share a random cut list would get; compare the shares above with these"},
            "median_onset_offset_frames": round(float(np.median(near)), 2) if len(near) else None,
            "cut_lead_frames": round(-float(np.median(near)), 2) if len(near) else None}
    if per:
        for name, div in (("8th", 2), ("16th", 4)):
            summ["chance"][name] = round(min(1.0, 2 * tol / fps_f / (per / div)), 3)
    if per and len(beats):
        for name, div in (("on_8th_share", 2), ("on_16th_share", 4)):
            v = []
            for r in rows:
                pos = (r["t"] - beats[0]) / per * div
                v.append(abs(pos - round(pos)) * per / div * fps_f <= tol)
            summ[name] = round(float(np.mean(v)), 3)
    # BPM octave check from the cut intervals (analysis.md 6.1)
    check = []
    if per and len(frames) >= 3:
        iv = np.diff(np.array([0] + frames)) / fps_f
        iv = iv[iv > 0.05]
        for fac in (1.0, 2.0, 0.5, 0.75, 4 / 3.0):
            bl = per / fac
            x = iv / bl
            near_half = np.abs(x * 2 - np.round(x * 2)) / 2 <= 0.08
            near_whole = np.abs(x - np.round(x)) <= 0.08
            check.append({"bpm": round(60.0 / bl, 2), "factor": round(fac, 3),
                          "intervals_on_half_beats": round(float(near_half.mean()), 3),
                          "intervals_on_whole_beats": round(float(near_whole.mean()), 3),
                          "median_interval_beats": round(float(np.median(x)), 2)})
    sh = summ["on_onset_share"] or 0.0
    ch = summ["chance"]["onset"] or 0.0
    verdict = ("onset-locked: keep our cuts on the reference frames / re-snap to the new track's onsets"
               if sh >= 0.7 else "cuts follow picture or words more than the music" if sh < 0.45
               else "partly music-locked: check the low-share cuts on the sheets")
    if ch >= 0.6 and sh - ch < 0.15:
        verdict += (f" (weak evidence: onsets are so dense that random cuts would score {ch}; "
                    f"look at on_strong_share {summ['on_strong_share']} vs chance {summ['chance']['strong']})")
    res = {"schema": "rr.cutsync/1", "beats_file": os.path.abspath(beats_path), "cuts_from": cut_src,
           "fps": fps_s, "convention": "cut at frame f starts at t=f/fps; offset_frames = (t_cut - t_event)*fps, "
                                       "negative = the cut leads the event",
           "bpm": B.get("bpm"), "summary": summ, "verdict": verdict, "bpm_check": check, "cuts": rows}
    out = out or p["cutsync"]
    save_json(out, res)
    jpg = None
    if png and rrio is not None:
        try:
            src = B.get("source")
            y = decode(src, SR) if src and os.path.exists(src) else None
            if y is not None:
                off = float(B.get("source_offset_s") or 0.0)
                y = y[int(off * SR):int((off + float(B.get("duration") or len(y) / SR)) * SR)]
                th, ldb = rms_db_env(y, SR, 0.01, 0.005)
                jpg = os.path.splitext(out)[0] + ".jpg"
                strip_plot(jpg, float(B.get("duration") or len(y) / SR), th, ldb, beats=beats, downbeats=down,
                           strong=strong, low=low, sections=B.get("sections"), silence=B.get("silence"),
                           cuts=np.array([r["t"] for r in rows]),
                           title=f"cuts (green) vs beats: on-onset {summ['on_onset_share']} on-beat "
                                 f"{summ['on_beat_share']} on-16th {summ['on_16th_share']} (tol {tol} f)")
        except Exception as e:
            jpg = None
            if not quiet:
                print(f"  (strip plot skipped: {e})")
    if not quiet:
        print(f"cutsync: {len(rows)} cuts @ {fps_s} fps vs {B.get('bpm')} BPM  (tol +-{tol} frames)")
        print(f"  on onset {summ['on_onset_share']}  strong {summ['on_strong_share']}  low {summ['on_low_share']}  "
              f"beat {summ['on_beat_share']}  8th {summ['on_8th_share']}  16th {summ['on_16th_share']}  "
              f"downbeat {summ['on_downbeat_share']}")
        cz = summ["chance"]
        print(f"  random-cut chance: onset {cz['onset']}  strong {cz['strong']}  low {cz['low']}  beat {cz['beat']}  "
              f"8th {cz.get('8th')}  16th {cz.get('16th')}")
        print(f"  cut lead (median, frames, + = cut before onset): {summ['cut_lead_frames']}")
        print(f"  verdict: {verdict}")
        for c in check:
            print(f"  bpm_check {c['bpm']:>7} (x{c['factor']}): intervals on half beats {c['intervals_on_half_beats']}, "
                  f"whole {c['intervals_on_whole_beats']}, median {c['median_interval_beats']} beats")
        for r in rows[:200]:
            b = r.get("beat") or {}
            o = r.get("onset") or {}
            print(f"   f{r['f']:>5} t={r['t']:7.3f}  beat {b.get('b', '-')!s:>4} {b.get('offset_frames', '-')!s:>6}f   "
                  f"onset {o.get('offset_frames', '-')!s:>6}f")
        print(f"  wrote {out}" + (f" and {jpg}" if jpg else ""))
    return res


def cmd_cutsync(a):
    do_cutsync(a.W, a.beats, a.analysis, a.cuts, a.tol, a.fps, a.out, not a.no_png)


# ----------------------------------------------------------------------------------------------------
# align
# ----------------------------------------------------------------------------------------------------
def _next_pow2(n):
    return 1 << int(math.ceil(math.log2(max(2, n))))


class SongCorr:
    """FFT cross-correlation of reference windows against a whole song, normalised (NCC)."""

    def __init__(self, song, nmax_win):
        self.s = np.asarray(song, np.float64)
        self.N = _next_pow2(len(self.s) + nmax_win)
        self.S = np.fft.rfft(self.s, self.N)
        self.c2 = np.concatenate([[0.0], np.cumsum(self.s ** 2)])

    def ncc(self, w):
        w = np.asarray(w, np.float64)
        nw = len(w)
        L = len(self.s) - nw + 1
        if L <= 0:
            return np.zeros(0)
        c = np.fft.irfft(self.S * np.conj(np.fft.rfft(w, self.N)), self.N)[:L]
        e = self.c2[nw:nw + L] - self.c2[:L]
        return c / (np.sqrt(np.maximum(e, 0)) * (np.linalg.norm(w) + EPS) + EPS)


def top_peaks(x, k, guard):
    x = x.copy()
    out = []
    for _ in range(k):
        if len(x) == 0:
            break
        j = int(np.argmax(x))
        if not np.isfinite(x[j]) or x[j] <= -1:
            break
        out.append((j, float(x[j])))
        x[max(0, j - guard):j + guard + 1] = -np.inf
    return out


def fine_lag(r_f, s_f, a, nw, k0, rad):
    """Best integer lag k (song start sample) near k0 for ref window r_f[a:a+nw] at the fine rate,
    with parabolic sub-sample interpolation. Returns (k_float, ncc)."""
    w = r_f[a:a + nw].astype(np.float64)
    wn = np.linalg.norm(w) + EPS
    ks = np.arange(max(0, k0 - rad), min(len(s_f) - nw, k0 + rad) + 1)
    if len(ks) == 0:
        return float(k0), 0.0
    vals = np.empty(len(ks))
    for i, k in enumerate(ks):
        s = s_f[k:k + nw].astype(np.float64)
        vals[i] = float(np.dot(w, s) / (wn * (np.linalg.norm(s) + EPS)))
    j = int(np.argmax(vals))
    kf = float(ks[j])
    if 0 < j < len(vals) - 1:
        y0, y1, y2 = vals[j - 1], vals[j], vals[j + 1]
        den = y0 - 2 * y1 + y2
        if den < 0:
            kf += 0.5 * (y0 - y2) / den
    return kf, float(vals[j])


def shift_song(s_f, off_s, sr, t0, t1):
    """Song samples aligned to ref times [t0, t1): song(t + off), linear interp for sub-samples."""
    n = int(round((t1 - t0) * sr))
    pos = (np.arange(n) + t0 * sr) + off_s * sr
    i = np.floor(pos).astype(np.int64)
    fr = (pos - i).astype(np.float32)
    ok = (i >= 0) & (i + 1 < len(s_f))
    out = np.zeros(n, np.float32)
    ii = i[ok]
    out[ok] = s_f[ii] * (1 - fr[ok]) + s_f[ii + 1] * fr[ok]
    return out


def env100(y, sr):
    """100 Hz spectral-flux envelope (pitch-robust) for speed scans."""
    hop = int(round(sr / 100.0))
    P = stft_power(y, 1024, hop)
    fb = mel_fb(sr, 1024, 40, 40.0, min(8000.0, sr / 2))
    L = 10 * np.log10(P @ fb.T + 1e-10)
    L = np.maximum(L, L.max() - 70)
    f = np.zeros(len(L))
    f[1:] = np.maximum(0, L[1:] - L[:-1]).mean(axis=1)
    f = f - moving_mean(f, 50)
    return f


def speed_scan(r, s, sr, rates):
    """Envelope NCC for each playback rate (ref plays the song at `rate` x). Returns list of
    (rate, ncc, song_offset_at_ref_t0)."""
    er = env100(r, sr)
    es = env100(s, sr)
    out = []
    sc = SongCorr(es, int(len(er) * max(rates)) + 8)
    for rt in rates:
        n = max(8, int(round(len(er) * rt)))
        x = np.interp(np.arange(n) / rt, np.arange(len(er)), er)  # ref env on the song time scale
        c = sc.ncc(x - x.mean())
        if len(c) == 0:
            continue
        j = int(np.argmax(c))
        out.append((float(rt), float(c[j]), j / 100.0))
    return out


def resample_linear(x, rate):
    """x played `rate` times faster (pitch follows): y(t) = x(rate*t)."""
    n = int(len(x) / rate)
    pos = np.arange(n) * rate
    return np.interp(pos, np.arange(len(x)), x).astype(np.float32)


def window_align(r_c, s_c, r_f, s_f, sr_c, sr_f, win, hop, K=4):
    """Per window: up to 2K candidate offsets (plain + pre-emphasised NCC peaks), refined at the fine rate."""
    nw_c = int(round(win * sr_c))
    nw_f = int(round(win * sr_f))
    D = len(r_c) / sr_c
    starts = np.arange(0.0, max(1e-9, D - win * 0.5), hop)
    starts = starts[starts + 0.5 * win <= D + 1e-9]
    if len(starts) == 0:
        starts = np.array([0.0])
    sc_plain = SongCorr(s_c, nw_c)
    pre = lambda v: np.concatenate([[0.0], v[1:] - 0.95 * v[:-1]])  # noqa: E731
    sc_pre = SongCorr(pre(s_c), nw_c)
    guard = int(0.02 * sr_c)
    ratio = sr_f / float(sr_c)
    wins = []
    for t0 in starts:
        a = int(round(t0 * sr_c))
        w = r_c[a:a + nw_c]
        if len(w) < nw_c * 0.5 or float(np.sqrt(np.mean(w.astype(np.float64) ** 2))) < 1e-4:
            wins.append({"t0": float(t0), "t1": float(min(D, t0 + win)), "cands": [], "silent": True})
            continue
        cands = top_peaks(sc_plain.ncc(w), K, guard) + top_peaks(sc_pre.ncc(pre(w)), K, guard)
        af = int(round(t0 * sr_f))
        nwf = min(nw_f, len(r_f) - af)
        seen = []
        out = []
        for j, _v in cands:
            k0 = int(round((j) * ratio))
            kf, v = fine_lag(r_f, s_f, af, nwf, k0, int(math.ceil(ratio)) + 3)
            off = (kf - af) / sr_f
            if any(abs(off - o) < 0.002 for o in seen):
                continue
            seen.append(off)
            out.append({"off": off, "ncc": v})
        out.sort(key=lambda c: -c["ncc"])
        wins.append({"t0": float(t0), "t1": float(min(D, t0 + win)), "cands": out, "silent": False})
    return wins


def viterbi(wins, null_score=0.2, jump=0.35, tol=0.004):
    states = []
    for w in wins:
        st = [{"off": None, "ncc": null_score}] + [c for c in w["cands"]]
        states.append(st)
    n = len(states)
    if n == 0:
        return []
    score = [np.array([s["ncc"] for s in states[0]])]
    back = [None]
    for i in range(1, n):
        prev, cur = states[i - 1], states[i]
        sc = np.empty(len(cur))
        bk = np.empty(len(cur), int)
        for j, c in enumerate(cur):
            best, bj = -1e9, 0
            for k, pv in enumerate(prev):
                if c["off"] is None and pv["off"] is None:
                    pen = 0.0
                elif c["off"] is None or pv["off"] is None:
                    pen = jump / 2
                else:
                    pen = 0.0 if abs(c["off"] - pv["off"]) <= tol else jump
                v = score[-1][k] - pen
                if v > best:
                    best, bj = v, k
            sc[j] = best + c["ncc"]
            bk[j] = bj
        score.append(sc)
        back.append(bk)
    j = int(np.argmax(score[-1]))
    path = [j]
    for i in range(n - 1, 0, -1):
        j = int(back[i][j])
        path.append(j)
    path = path[::-1]
    return [states[i][path[i]] for i in range(n)]


def split_point(r, a_pred, b_pred, sr, lo_t, hi_t):
    """Time in [lo_t, hi_t] minimising sum_{t<ts} (r-a)^2 + sum_{t>=ts} (r-b)^2 (predictions on ref time)."""
    i0, i1 = int(max(0, lo_t * sr)), int(min(len(r), hi_t * sr))
    if i1 - i0 < 4:
        return (lo_t + hi_t) / 2
    rr = r[i0:i1].astype(np.float64)
    ea = (rr - a_pred[i0:i1]) ** 2
    eb = (rr - b_pred[i0:i1]) ** 2
    ca = np.concatenate([[0.0], np.cumsum(ea)])
    cb = np.concatenate([[0.0], np.cumsum(eb)])
    tot = ca + (cb[-1] - cb)
    k = int(np.argmin(tot))
    return (i0 + k) / sr


def do_align(W, track, ref_audio=None, win=4.0, hop=0.5, null=0.25, jump=0.35, residual=None, out=None,
             quiet=False, scan_speed="auto", sfx_db=-6.0):
    p = ws_paths(W)
    t_start = time.time()
    if not track or not os.path.exists(track):
        raise AudioError(f"track not found: {track}")
    if ref_audio is None:
        if not os.path.exists(p["ref_wav"]):
            do_extract(W, quiet=True)
        ref_audio = p["ref_wav"]
    elif not os.path.exists(ref_audio):
        raise AudioError(f"ref audio not found: {ref_audio}")
    win = float(min(6.0, max(3.0, win)))
    sr_c, sr_f = 8000, SR
    r_c, s_c = decode(ref_audio, sr_c), decode(track, sr_c)
    r_f, s_f = decode(ref_audio, sr_f), decode(track, sr_f)
    D = len(r_f) / sr_f
    if D < 1.0:
        raise AudioError("ref audio shorter than 1 s")
    win_eff = min(win, D)
    if D / hop > 160:  # long refs: cap the window count (~160) to stay inside the foreground time limit
        hop = round(D / 160.0, 2)
    wins = window_align(r_c, s_c, r_f, s_f, sr_c, sr_f, win_eff, hop)
    best = [w["cands"][0]["ncc"] for w in wins if w["cands"]]
    med = float(np.median(best)) if best else 0.0
    speed = {"rate": 1.0, "mode": "same speed", "scanned": False}
    song_rate = 1.0
    stretch_only = False
    good = float(np.mean([b >= 0.5 for b in best])) if best else 0.0
    if (scan_speed == "always") or (scan_speed == "auto" and (med < 0.8 or good < 0.8)):
        rates = np.round(np.arange(0.80, 1.2501, 0.005), 4)
        sc = speed_scan(r_f, s_f, sr_f, rates)
        if sc:
            sc.sort(key=lambda x: -x[1])
            br, bv, boff = sc[0]
            v1 = next((v for rt, v, o in sc if abs(rt - 1.0) < 1e-6), 0.0)
            speed.update(scanned=True, env_best_rate=br, env_best_ncc=round(bv, 3), env_ncc_at_1=round(v1, 3),
                         env_song_offset=round(boff, 3))
            if abs(br - 1.0) > 0.004 and bv > max(0.3, v1 + 0.08):
                s_c2 = resample_linear(s_c, br)
                s_f2 = resample_linear(s_f, br)
                wins2 = window_align(r_c, s_c2, r_f, s_f2, sr_c, sr_f, win_eff, hop)
                best2 = [w["cands"][0]["ncc"] for w in wins2 if w["cands"]]
                med2 = float(np.median(best2)) if best2 else 0.0
                if med2 > max(med + 0.15, 0.4):
                    wins, s_c, s_f, med, song_rate = wins2, s_c2, s_f2, med2, br
                    speed.update(rate=br, mode="resampled (speed and pitch changed together)")
                else:
                    speed.update(rate=br, mode="time-stretched (pitch kept) or re-pitched: waveform match "
                                               "impossible; envelope-level mapping only")
                    stretch_only = True
    if stretch_only:
        off = speed["env_song_offset"]
        rt = speed["rate"]
        seg = {"ref_t0": 0.0, "ref_t1": r3(D), "song_t0": r3(off), "song_t1": r3(off + D * rt),
               "song_offset": r4(off), "ncc": speed["env_best_ncc"], "match": True, "method": "envelope",
               "rate": rt, "gain": None, "gain_db": None, "residual_db": None, "alt_offsets": []}
        res = {"schema": "rr.align/1", "ref_audio": os.path.abspath(ref_audio), "track": os.path.abspath(track),
               "sr": sr_f, "win_s": win_eff, "hop_s": hop,
               "convention": "song_t = song_t0 + (ref_t - ref_t0) * rate", "speed": speed, "coverage": 1.0,
               "median_window_ncc": r3(med), "segments": [seg], "hidden_edits": [], "single_offset": True,
               "sfx_candidates": [], "residual_wav": None, "windows": [],
               "notes": [f"ref plays the song time-stretched x{rt} from song {off:.2f} s (envelope match "
                         f"{speed['env_best_ncc']} vs {speed['env_ncc_at_1']} at x1.0); hidden edits are not "
                         f"resolved in this mode"]}
        out = out or p["align"]
        save_json(out, res)
        if not quiet:
            print(f"align: {track} inside {ref_audio}  ({time.time() - t_start:.1f} s)")
            print(f"  speed: x{rt} ({speed['mode']})")
            print(f"  ref 0.000-{D:.3f} ~ song {off:.2f}-{off + D * rt:.2f} (envelope ncc {speed['env_best_ncc']})")
            print("  note: " + res["notes"][0])
            print(f"  wrote {out}")
        return res
    path = viterbi(wins, null_score=null, jump=jump)
    # runs of equal state
    runs = []
    for w, st in zip(wins, path):
        key = None if st["off"] is None else st["off"]
        if runs and ((key is None and runs[-1]["off"] is None) or
                     (key is not None and runs[-1]["off"] is not None and abs(key - runs[-1]["off"]) <= 0.004)):
            runs[-1]["wins"].append((w, st))
        else:
            runs.append({"off": key, "wins": [(w, st)]})
    for rn in runs:
        if rn["off"] is not None:
            offs = [st["off"] for _, st in rn["wins"]]
            nc = [st["ncc"] for _, st in rn["wins"]]
            k = int(np.argmax(nc))
            rn["off"] = float(offs[k])
            rn["ncc"] = float(np.median(nc))
            rn["ncc_max"] = float(np.max(nc))
            # alternative offsets that are as good in at least half of the run's windows (repeated loops)
            votes = []
            for w, st in rn["wins"]:
                seen_w = []
                for c in w["cands"]:
                    if abs(c["off"] - rn["off"]) > 0.05 and c["ncc"] >= st["ncc"] - 0.03 and \
                            not any(abs(c["off"] - o) < 0.005 for o in seen_w):
                        seen_w.append(c["off"])
                votes.extend(seen_w)
            alts = []
            for o in votes:
                n_o = sum(1 for v in votes if abs(v - o) < 0.005)
                if n_o >= max(2, len(rn["wins"]) / 2.0) and not any(abs(o - a) < 0.005 for a in alts):
                    alts.append(float(o))
            rn["alts"] = sorted(alts)
        rn["t0"] = rn["wins"][0][0]["t0"]
        rn["t1"] = rn["wins"][-1][0]["t1"]
    # gains (least squares over the run's windows) for prediction models
    for rn in runs:
        if rn["off"] is None:
            rn["gain"] = 0.0
            continue
        pred = shift_song(s_f, rn["off"], sr_f, 0.0, D)
        a, b = int(rn["t0"] * sr_f), int(min(D, rn["t1"]) * sr_f)
        num = float(np.dot(r_f[a:b].astype(np.float64), pred[a:b].astype(np.float64)))
        den = float(np.dot(pred[a:b].astype(np.float64), pred[a:b].astype(np.float64))) + EPS
        rn["gain"] = num / den
        rn["raw"] = pred
        rn["pred"] = pred * rn["gain"]
    zero = np.zeros(len(r_f), np.float32)

    def regain(rn, a, b):
        """Least-squares gain of the aligned song over [a, b) of the ref."""
        if rn["off"] is None:
            return
        raw = rn["raw"]
        ia, ib = int(a * sr_f), int(b * sr_f)
        x, yv = raw[ia:ib].astype(np.float64), r_f[ia:ib].astype(np.float64)
        g = float(np.dot(x, yv) / (np.dot(x, x) + EPS)) if ib - ia > 16 else rn["gain"]
        rn["gain"] = g
        rn["pred"] = raw * g

    # boundaries between consecutive runs (monotonic; runs squeezed under 0.1 s are dropped and the
    # neighbours re-split; then gains are re-estimated inside the final bounds and split once more)
    def split_all(runs):
        edges = [0.0]
        for A, Bn in zip(runs[:-1], runs[1:]):
            lo = max(edges[-1], A["wins"][-1][0]["t0"])
            hi = max(lo, min(D, Bn["wins"][0][0]["t1"]))
            edges.append(split_point(r_f, A.get("pred", zero), Bn.get("pred", zero), sr_f, lo, hi))
        edges.append(D)
        return edges

    for _pass in range(2):
        while True:
            edges = split_all(runs)
            short = [k for k in range(len(runs)) if edges[k + 1] - edges[k] < 0.1 and len(runs) > 1]
            if not short:
                break
            k = short[0]
            if 0 < k < len(runs) - 1 and runs[k - 1]["off"] is not None and runs[k + 1]["off"] is not None \
                    and abs(runs[k - 1]["off"] - runs[k + 1]["off"]) <= 0.004:
                runs[k - 1]["wins"].extend(runs[k]["wins"] + runs[k + 1]["wins"])
                runs[k - 1]["t1"] = runs[k + 1]["t1"]
                del runs[k:k + 2]
            else:
                del runs[k]
        for rn, a, b in zip(runs, edges[:-1], edges[1:]):
            regain(rn, a, b)
    # leading / trailing parts where the song is absent (the window grid is coarse)
    def local_ncc(pred, a, b):
        ia, ib = int(a * sr_f), int(b * sr_f)
        x, yv = pred[ia:ib].astype(np.float64), r_f[ia:ib].astype(np.float64)
        return float(np.dot(x, yv) / (np.linalg.norm(x) * np.linalg.norm(yv) + EPS)) if ib - ia > 16 else 1.0

    segs = []
    for rn, a, b in zip(runs, edges[:-1], edges[1:]):
        if rn["off"] is not None and rn is runs[0]:
            ts = split_point(r_f, zero, rn["pred"], sr_f, 0.0, min(b, a + win_eff))
            if ts >= 0.2 and local_ncc(rn["pred"], 0.0, ts) < max(0.1, 0.3 * rn.get("ncc", 1.0)):
                segs.append({"run": None, "t0": 0.0, "t1": ts})
                a = ts
        tail = None
        if rn["off"] is not None and rn is runs[-1]:
            ts = split_point(r_f, rn["pred"], zero, sr_f, max(a, b - win_eff), b)
            if b - ts >= 0.2 and local_ncc(rn["pred"], ts, b) < max(0.1, 0.3 * rn.get("ncc", 1.0)):
                tail = {"run": None, "t0": ts, "t1": b}
                b = ts
        segs.append({"run": rn, "t0": a, "t1": b})
        if tail:
            segs.append(tail)
    segments = []
    for sg in segs:
        rn = sg["run"]
        a, b = sg["t0"], sg["t1"]
        if b - a < 0.02:
            continue
        ia, ib = int(a * sr_f), int(b * sr_f)
        rr = r_f[ia:ib].astype(np.float64)
        e_r = float(np.dot(rr, rr)) + EPS
        if rn is None or rn["off"] is None:
            segments.append({"ref_t0": r3(a), "ref_t1": r3(b), "match": False,
                             "ref_db": r3(10 * math.log10(e_r / max(1, len(rr)) + 1e-13))})
            continue
        pr = rn["pred"][ia:ib].astype(np.float64)
        resid = float(np.dot(rr - pr, rr - pr))
        ncc_seg = float(np.dot(rr, pr) / (math.sqrt(e_r) * (np.linalg.norm(pr) + EPS)))
        off = rn["off"]
        s0 = (a + off) * song_rate
        s1 = (b + off) * song_rate
        segments.append({"ref_t0": r3(a), "ref_t1": r3(b), "song_t0": r3(s0), "song_t1": r3(s1),
                         "song_offset": r4(off * song_rate if song_rate == 1.0 else s0 - a),
                         "ncc": r3(ncc_seg), "ncc_windows_median": r3(rn["ncc"]), "match": True,
                         "gain": r4(rn["gain"]), "gain_db": r3(20 * math.log10(abs(rn["gain"]) + 1e-9)),
                         "polarity": -1 if rn["gain"] < 0 else 1,
                         "residual_db": r3(10 * math.log10(resid / e_r + 1e-13)),
                         "alt_offsets": [round(float(x), 2) for x in rn.get("alts", [])][:6]})
    matched = [s for s in segments if s["match"]]
    hidden = []
    for A, Bs in zip(matched[:-1], matched[1:]):
        hidden.append({"t": Bs["ref_t0"], "from_s": A["song_t1"], "to_s": Bs["song_t0"],
                       "jump_s": r3(Bs["song_t0"] - A["song_t1"] - (Bs["ref_t0"] - A["ref_t1"]) * song_rate),
                       "gap_s": r3(Bs["ref_t0"] - A["ref_t1"]),
                       "ncc": r3(min(A["ncc"], Bs["ncc"]))})
    cover = sum(s["ref_t1"] - s["ref_t0"] for s in matched) / D if D else 0.0
    # optional residual (ref minus the aligned, gain-matched song) and SFX candidates. Events are found in
    # the STFT magnitude domain (|R| - |P| > 0), which ignores codec phase noise.
    sfx = []
    full_pred = np.zeros(len(r_f), np.float32)
    for sg in segs:
        rn = sg["run"]
        if rn is not None and rn.get("off") is not None:
            ia, ib = int(sg["t0"] * sr_f), int(sg["t1"] * sr_f)
            full_pred[ia:ib] = rn["pred"][ia:ib]
    if matched and song_rate == 1.0:
        n_fft, hop_s = 1024, 256
        PR = np.sqrt(stft_power(r_f, n_fft, hop_s))
        PP = np.sqrt(stft_power(full_pred, n_fft, hop_s))
        resm = np.maximum(PR - 1.12 * PP, 0.0)  # 1 dB headroom for gain/EQ mismatch
        e_res = (resm ** 2).sum(axis=1)
        e_ref = (PR ** 2).sum(axis=1) + 1e-12
        frac_db = 10 * np.log10(e_res / e_ref + 1e-12)
        lvl = 10 * np.log10(e_res + 1e-12)
        tt = np.arange(len(lvl)) * hop_s / float(sr_f)
        freqs = np.fft.rfftfreq(n_fft, 1.0 / sr_f)
        base = float(np.median(lvl))
        x = np.maximum(0.0, lvl - base)
        x[frac_db < sfx_db] = 0.0  # default -6: >= 25 % of the frame unexplained (AAC noise stays under ~-7 dB)
        in_song = np.zeros(len(tt), bool)
        for sm_ in matched:
            in_song |= (tt >= sm_["ref_t0"]) & (tt < sm_["ref_t1"])
        x[~in_song] = 0.0
        pk = pick_peaks(x, sr_f / float(hop_s), wait_s=0.15, avg_s=0.6, delta=6.0, thresh=12.0)
        for i in pk:
            spec = (resm[max(0, i - 2):i + 3] ** 2).mean(axis=0)
            cen = float((spec * freqs).sum() / (spec.sum() + 1e-12))
            kind = "low boom" if cen < 200 else "low-mid hit" if cen < 1000 else "mid/high (whoosh, hit, riser)" \
                if cen < 5000 else "high (hiss, shutter, click)"
            sfx.append({"t": r3(tt[i]), "unexplained_db": r3(frac_db[i]), "over_floor_db": r3(x[i]),
                        "centroid_hz": int(cen), "type_guess": kind})
        if residual:
            write_audio(residual, r_f - full_pred, sr_f)
    res = {"schema": "rr.align/1", "ref_audio": os.path.abspath(ref_audio), "track": os.path.abspath(track),
           "sr": sr_f, "win_s": win_eff, "hop_s": hop,
           "convention": "song_t = ref_t + song_offset (rate 1); with rate != 1: song_t = song_t0 + "
                         "(ref_t - ref_t0) * rate",
           "speed": speed, "coverage": r3(cover), "median_window_ncc": r3(med),
           "segments": segments, "hidden_edits": hidden, "single_offset": len(matched) == 1,
           "sfx_candidates": sfx[:200], "residual_wav": residual if (residual and matched) else None,
           "windows": [{"ref_t0": r3(w["t0"]), "ref_t1": r3(w["t1"]),
                        "song_offset": r4(st["off"]) if st["off"] is not None else None,
                        "ncc": r3(st["ncc"]) if st["off"] is not None else None,
                        "best": r3(w["cands"][0]["ncc"]) if w["cands"] else None,
                        "best_offset": r4(w["cands"][0]["off"]) if w["cands"] else None}
                       for w, st in zip(wins, path)]}
    notes = []
    if not matched:
        notes.append("the song was not found in the ref audio (different song/version, heavy processing, "
                     "or a time-stretch the scan did not resolve)")
    if any(s.get("alt_offsets") for s in matched):
        notes.append("some segments match several song positions equally well (repeated loop): "
                     "any listed offset sounds the same")
    if speed.get("rate", 1.0) != 1.0:
        notes.append(f"ref plays the song at x{speed['rate']} ({speed['mode']})")
    res["notes"] = notes
    out = out or p["align"]
    save_json(out, res)
    if not quiet:
        print(f"align: {track} inside {ref_audio}  ({time.time() - t_start:.1f} s, win {win_eff}s hop {hop}s)")
        print(f"  speed: x{speed.get('rate')} ({speed.get('mode')})  coverage {res['coverage']}  "
              f"median window ncc {res['median_window_ncc']}")
        for s in segments:
            if s["match"]:
                print(f"  ref {s['ref_t0']:7.3f}-{s['ref_t1']:7.3f}  = song {s['song_t0']:7.3f}-{s['song_t1']:7.3f}  "
                      f"(offset {s['song_offset']:+.4f})  ncc {s['ncc']}  gain {s['gain_db']} dB  "
                      f"residual {s['residual_db']} dB" + (f"  alt {s['alt_offsets']}" if s["alt_offsets"] else ""))
            else:
                print(f"  ref {s['ref_t0']:7.3f}-{s['ref_t1']:7.3f}  no song ({s['ref_db']} dB)")
        for h in hidden:
            print(f"  HIDDEN EDIT at ref {h['t']:.3f}s: song {h['from_s']:.3f} -> {h['to_s']:.3f} "
                  f"(jump {h['jump_s']:+.3f} s)")
        if sfx:
            print(f"  {len(sfx)} residual events (SFX layer candidates), e.g. " +
                  ", ".join(f"{e['t']}s" for e in sfx[:8]))
        for n in notes:
            print("  note: " + n)
        print(f"  wrote {out}" + (f" and {residual}" if res["residual_wav"] else ""))
    return res


def cmd_align(a):
    do_align(a.W, a.track, a.ref_audio, a.win, a.hop, a.null, a.jump, a.residual, a.out,
             scan_speed=a.speed_scan, sfx_db=a.sfx_db)


# ----------------------------------------------------------------------------------------------------
# slice
# ----------------------------------------------------------------------------------------------------
def parse_seg(s):
    parts = s.split(":")
    if len(parts) < 2:
        raise AudioError(f"bad --seg {s!r}: use T0:T1[:NAME]")
    try:
        t0, t1 = float(parts[0]), float(parts[1])
    except ValueError:
        raise AudioError(f"bad --seg {s!r}: times must be seconds") from None
    name = ":".join(parts[2:]) if len(parts) > 2 else None
    if t1 <= t0:
        raise AudioError(f"bad --seg {s!r}: t1 must be > t0")
    return {"t0": t0, "t1": t1, "name": name}


def fade_curve(n, shape):
    x = (np.arange(n) + 0.5) / max(1, n)
    if shape == "lin":
        return x.astype(np.float32)
    return np.sin(x * np.pi / 2).astype(np.float32)  # equal power


def snap_times(mono, sr, t0, t1, radius):
    """Move each boundary to the quietest point (5 ms RMS) within +-radius: the cleanest cut between words."""
    th, ldb = rms_db_env(mono, sr, 0.005, 0.001)
    if len(th) == 0:
        return t0, t1

    def q(t):
        m = (th >= t - radius) & (th <= t + radius)
        if not m.any():
            return t
        idx = np.nonzero(m)[0]
        return float(th[idx[int(np.argmin(ldb[idx]))]])

    n0, n1 = q(t0), q(t1)
    if n1 - n0 < 0.02:
        return t0, t1
    return max(0.0, n0), n1


def do_slice(src, segs=None, segs_json=None, from_align=None, out_dir=None, concat=None, fade_in=5.0,
             fade_out=10.0, xfade=10.0, shape="sin", sr=48000, channels=2, gain_db=0.0, snap=0.0, fmt="wav",
             length=None, match_gain=False, quiet=False):
    if not os.path.exists(src):
        raise AudioError(f"source not found: {src}")
    y = decode(src, sr, mono=(channels == 1), channels=channels)
    if y.ndim == 1:
        y = y[:, None]
    mono = y.mean(axis=1)
    dur = len(y) / sr
    items = []
    if segs:
        items += [parse_seg(s) for s in segs]
    if segs_json:
        j = load_json(segs_json)
        lst = j.get("segments", j.get("words", [])) if isinstance(j, dict) else j
        for k, e in enumerate(lst):
            t0 = e.get("t0", e.get("start"))
            t1 = e.get("t1", e.get("end"))
            if t0 is None or t1 is None:
                continue
            items.append({"t0": float(t0), "t1": float(t1),
                          "name": e.get("name") or e.get("word") or e.get("text"),
                          "fade_in": e.get("fade_in"), "fade_out": e.get("fade_out"), "gain_db": e.get("gain_db")})
    written = []
    if from_align:
        A = load_json(from_align)
        matched = [s for s in A.get("segments", []) if s.get("match")]
        if not matched:
            raise AudioError(f"{from_align} has no matched segments")
        L = float(length) if length else max(s["ref_t1"] for s in A["segments"])
        n = int(round(L * sr))
        bed = np.zeros((n, y.shape[1]), np.float32)
        xf = xfade / 1000.0
        for k, s in enumerate(matched):
            a_ref, b_ref = s["ref_t0"], s["ref_t1"]
            ext_a = xf / 2 if k > 0 else 0.0
            ext_b = xf / 2 if k < len(matched) - 1 else 0.0
            ra, rb = max(0.0, a_ref - ext_a), min(L, b_ref + ext_b)
            sa = s["song_t0"] - (a_ref - ra)
            ia, ib = int(round(ra * sr)), int(round(rb * sr))
            ja = int(round(sa * sr))
            seg = np.zeros((ib - ia, y.shape[1]), np.float32)
            lo, hi = max(0, ja), min(len(y), ja + (ib - ia))
            if hi > lo:
                seg[lo - ja:hi - ja] = y[lo:hi]
            g = 10 ** (gain_db / 20.0) * (abs(s.get("gain", 1.0)) if match_gain else 1.0)
            seg *= g
            nfi = int(round((xf if k > 0 else fade_in / 1000.0) * sr))
            nfo = int(round((xf if k < len(matched) - 1 else fade_out / 1000.0) * sr))
            if nfi > 0:
                seg[:nfi] *= fade_curve(min(nfi, len(seg)), shape)[:, None][:len(seg[:nfi])]
            if nfo > 0:
                seg[-nfo:] *= fade_curve(min(nfo, len(seg)), shape)[::-1][:, None][-len(seg[-nfo:]):]
            bed[ia:ib] += seg
        outp = concat or os.path.join(out_dir or ".", "music_rebuilt." + fmt)
        write_audio(outp, bed, sr)
        written.append({"path": outp, "t0": 0.0, "t1": r3(L), "dur": r3(L), "segments": len(matched)})
        if not quiet:
            print(f"slice: rebuilt the ref's music edit from {from_align}: {len(matched)} segments, "
                  f"{L:.3f} s -> {outp}")
        return written
    if not items:
        raise AudioError("nothing to cut: pass --seg T0:T1[:NAME], --segs-json or --from-align")
    clips = []
    for k, it in enumerate(items):
        t0, t1 = it["t0"], it["t1"]
        if snap:
            t0, t1 = snap_times(mono, sr, t0, t1, snap)
        t0, t1 = max(0.0, t0), min(dur, t1)
        if t1 <= t0:
            raise AudioError(f"segment {k} ({it['t0']}-{it['t1']}) is outside the source ({dur:.3f} s)")
        c = y[int(round(t0 * sr)):int(round(t1 * sr))].copy()
        fi = it.get("fade_in") if it.get("fade_in") is not None else fade_in
        fo = it.get("fade_out") if it.get("fade_out") is not None else fade_out
        g = it.get("gain_db") if it.get("gain_db") is not None else gain_db
        nfi = min(len(c), int(round(fi / 1000.0 * sr)))
        nfo = min(len(c), int(round(fo / 1000.0 * sr)))
        if nfi > 0:
            c[:nfi] *= fade_curve(nfi, shape)[:, None]
        if nfo > 0:
            c[-nfo:] *= fade_curve(nfo, shape)[::-1][:, None]
        c *= 10 ** (g / 20.0)
        name = it.get("name") or f"seg{k:02d}"
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", str(name)).strip("_") or f"seg{k:02d}"
        clips.append((name, t0, t1, c))
    if out_dir or not concat:
        od = out_dir or "."
        os.makedirs(od, exist_ok=True)
        used = set()
        for k, (name, t0, t1, c) in enumerate(clips):
            nm = name if name not in used else f"{name}_{k:02d}"
            used.add(nm)
            pth = os.path.join(od, f"{nm}.{fmt}")
            write_audio(pth, c, sr)
            written.append({"path": pth, "t0": r4(t0), "t1": r4(t1), "dur": r4(t1 - t0)})
    if concat:
        nx = int(round(xfade / 1000.0 * sr))
        acc = clips[0][3]
        for _, _, _, c in clips[1:]:
            n = min(nx, len(acc), len(c))
            if n > 0:
                fo = fade_curve(n, shape)[::-1][:, None]
                fi = fade_curve(n, shape)[:, None]
                mid = acc[-n:] * fo + c[:n] * fi
                acc = np.concatenate([acc[:-n], mid, c[n:]])
            else:
                acc = np.concatenate([acc, c])
        write_audio(concat, acc, sr)
        written.append({"path": concat, "t0": 0.0, "t1": r4(len(acc) / sr), "dur": r4(len(acc) / sr),
                        "segments": len(clips)})
    if not quiet:
        for w in written:
            print(f"  wrote {w['path']}  ({w['t0']}-{w['t1']} s, {w['dur']} s)")
    return written


def cmd_slice(a):
    w = do_slice(a.src, a.seg, a.segs_json, a.from_align, a.out_dir, a.concat, a.fade_in, a.fade_out, a.xfade,
                 a.shape, a.sr, a.channels, a.gain_db, a.snap, a.format, a.length, a.match_gain)
    if a.json:
        print(json.dumps(jsonable(w)))


# ----------------------------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------------------------
def build_parser():
    ap = argparse.ArgumentParser(
        prog="audio.py",
        description="Reference audio forensics: extract, beats/onsets/sections/loudness, cut sync, "
                    "song alignment (hidden music edits), slicing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python3 $RR/audio.py extract $W\n"
               "  python3 $RR/audio.py beats $W\n"
               "  python3 $RR/audio.py beats $W --audio $W/ref/user_track.mp3 --out $W/audio/track_beats.json\n"
               "  python3 $RR/audio.py cutsync $W\n"
               "  python3 $RR/audio.py align $W --track $W/ref/song.mp3 --residual $W/audio/residual.wav\n"
               "  python3 $RR/audio.py slice song.mp3 --from-align $W/audio/align.json --concat $W/audio/music.wav\n"
               "  python3 $RR/audio.py slice chant.wav --seg 0.10:0.42:yaong --seg 0.55:0.80:hana --snap 0.05 "
               "--out-dir $W/audio/words")
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("extract", help="ref audio -> W/audio/ref.wav (22050 mono) + ref_orig.<ext> + ref_audio.json")
    e.add_argument("W")
    e.add_argument("--src", help="media to extract from (default W/ref/ref.mp4)")
    e.add_argument("--sr", type=int, default=SR)
    e.set_defaults(fn=cmd_extract)

    b = sub.add_parser("beats", help="bpm/beats/downbeats/onsets/sections/silence/loudness -> W/audio/beats.json")
    b.add_argument("W")
    b.add_argument("--audio", help="analyse this file instead of the ref audio (e.g. the user's track)")
    b.add_argument("--start", type=float, default=0.0, help="analysis window start in the source (s)")
    b.add_argument("--dur", type=float, default=None, help="analysis window length (s)")
    b.add_argument("--bpm", type=float, default=None, help="force the tempo (fit only the phase)")
    b.add_argument("--bpm-min", type=float, default=60.0)
    b.add_argument("--bpm-max", type=float, default=200.0)
    b.add_argument("--fps", default=None, help="fps for *_frames fields (default: the ref video's)")
    b.add_argument("--out", default=None, help="output json (default W/audio/beats.json for the ref, W/audio/beats_<name>.json for --audio)")
    b.add_argument("--no-png", action="store_true", help="skip the beats.jpg timeline strip")
    b.set_defaults(fn=cmd_beats)

    c = sub.add_parser("cutsync", help="cuts vs beats/onsets -> W/audio/cutsync.json")
    c.add_argument("W")
    c.add_argument("--beats", default=None, help="beats json (default W/audio/beats.json; computed if missing)")
    c.add_argument("--analysis", default=None, help="json with a 'cuts' list (default W/analysis/analysis.json; "
                                                     "breakdown.json works too)")
    c.add_argument("--cuts", default=None, help="explicit cut frames 'f1,f2,...' instead of a json")
    c.add_argument("--tol", type=float, default=2.0, help="on-beat tolerance in frames (default 2)")
    c.add_argument("--fps", default=None)
    c.add_argument("--out", default=None)
    c.add_argument("--no-png", action="store_true")
    c.set_defaults(fn=cmd_cutsync)

    al = sub.add_parser("align", help="find where a known song sits in the ref (hidden edits) -> W/audio/align.json")
    al.add_argument("W")
    al.add_argument("--track", required=True, help="the source song")
    al.add_argument("--ref-audio", default=None, help="audio to search in (default W/audio/ref.wav)")
    al.add_argument("--win", type=float, default=4.0, help="window length 3-6 s (default 4)")
    al.add_argument("--hop", type=float, default=0.5, help="window hop (default 0.5 s)")
    al.add_argument("--null", type=float, default=0.25, help="NCC below which a window counts as 'song absent'")
    al.add_argument("--jump", type=float, default=0.35, help="path penalty for an offset jump")
    al.add_argument("--speed-scan", choices=["auto", "always", "never"], default="auto",
                    help="scan playback rates 0.80-1.25 (auto: only when the waveform match is poor)")
    al.add_argument("--residual", default=None, help="write ref minus aligned song here (wav)")
    al.add_argument("--sfx-db", type=float, default=-6.0,
                    help="SFX candidate gate: share of a frame's energy the song does not explain, dB "
                         "(default -6 = 25%%; -9 finds quieter SFX but also codec noise)")
    al.add_argument("--out", default=None)
    al.set_defaults(fn=cmd_align)

    s = sub.add_parser("slice", help="cut clips by explicit times with fades / concat / rebuild a music edit")
    s.add_argument("src")
    s.add_argument("--seg", action="append", default=[], help="T0:T1[:NAME] (repeatable)")
    s.add_argument("--segs-json", default=None, help="json list [{t0,t1,name,fade_in,fade_out,gain_db}] "
                                                     "(also words.json with start/end/word)")
    s.add_argument("--from-align", default=None, help="align.json: rebuild the ref's music edit from SRC (the song)")
    s.add_argument("--out-dir", default=None, help="write one file per segment here")
    s.add_argument("--concat", default=None, help="join the segments (crossfaded) into this file")
    s.add_argument("--fade-in", type=float, default=5.0, help="ms (default 5)")
    s.add_argument("--fade-out", type=float, default=10.0, help="ms (default 10)")
    s.add_argument("--xfade", type=float, default=10.0, help="crossfade between joined segments, ms (default 10)")
    s.add_argument("--shape", choices=["sin", "lin"], default="sin", help="fade shape (sin = equal power)")
    s.add_argument("--sr", type=int, default=48000)
    s.add_argument("--channels", type=int, default=2)
    s.add_argument("--gain-db", type=float, default=0.0)
    s.add_argument("--match-gain", action="store_true", help="--from-align: apply each segment's measured gain")
    s.add_argument("--length", type=float, default=None, help="--from-align: output length (default ref length)")
    s.add_argument("--snap", type=float, default=0.0, help="move t0/t1 to the quietest point within +-SEC (clean word cuts)")
    s.add_argument("--format", default="wav", help="extension for --out-dir files (wav, m4a, flac, mp3)")
    s.add_argument("--json", action="store_true", help="print the written files as JSON")
    s.set_defaults(fn=cmd_slice)
    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    try:
        if hasattr(a, "W") and a.cmd != "slice" and not os.path.isdir(a.W):
            if a.cmd in ("extract", "beats", "align") and (getattr(a, "src", None) or getattr(a, "audio", None)
                                                           or getattr(a, "ref_audio", None)):
                os.makedirs(a.W, exist_ok=True)
            else:
                raise AudioError(f"workspace not found: {a.W}")
        a.fn(a)
    except AudioError as e:
        print(f"audio.py: error: {e}", file=sys.stderr)
        return e.code
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
