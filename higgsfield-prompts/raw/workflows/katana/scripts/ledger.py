#!/usr/bin/env python3
"""Reference-remake accounting. Exact live estimates, finite hard cap, serialized dispatch.
Commands retain the legacy name approve for internal plan registration, never human consent.
Use quote/params/price-set/approve/guard/add/status/use/jobs/summary; see command help.
"""
from __future__ import annotations

import argparse
import hashlib
import copy
import datetime as _dt
import json
import math
import os
import re
import sys
import tempfile

try:
    import fcntl  # POSIX (sandbox Linux, macOS)
except ImportError:  # pragma: no cover
    fcntl = None

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PRICES = os.path.join(HERE, "prices.json")
STAGES = ("identity", "keyframe", "canary", "batch", "reroll", "matte", "audio", "other")
STATES = ("submitted", "completed", "failed", "nsfw", "ip_detected", "refunded", "bounced")
FAILED = ("failed", "nsfw", "ip_detected")
ACTIVE = ("submitted", "completed")
GUARD_MARGIN = 0.0
LIVE_MAX_AGE_SECONDS = 86400
ALLOWED_VIDEO = {"seedance_2_5", "hf_mult_motion_control", "hf_mult_replace_object"}
VIDEO_UTILITIES = {"sam_3_video"}
AUDIO_REQUEST_FIELDS = {
    "seed_audio": {"voice_id", "voice_type", "format", "sample_rate", "pitch_rate"},
    "elevenlabs_v4": {"dialogue", "stability", "similarity_boost"},
}
CANONICAL_ROLES = {"image", "video", "audio", "start_image", "end_image", "ref_element"}
APPROVE_TOL = 0.05
VIDEO_TOOLS = ("generate_video", "generate_video_batch")
FREE_TEXT = ("analysis, contact sheets, routing, prompts, dedicated estimator price checks, balance/transactions, uploads, "
             "compositing, text, grade, grain, flashes, transitions, sticker placement, tracking, recorded-SFX mixing, QA and "
             "every code revision after the footage (sandbox_exec = 0 cr)")
# fields a second-take line (take_of) does not inherit from the line it repeats
TAKE_OWN = ("id", "optional", "take_of", "take_reason", "reason", "purpose", "full_take", "screen_seconds", "takes",
            "notes", "ip_suspect")
# Historical helper constants; content refusals never trigger an automatic route change.
MT_MODEL = "hf_mult_motion_control"
G5_STILL = {"model": "nano_banana_2", "resolution": "2k"}
BLOCK_MATTE = {"model": "remove_background"}
RECONCILE_HINT = ("transactions carry no job ids: match each job by model + time (+-2 s) + amount, and expect FOREIGN "
                  "charges from other chats on the same account to interleave in this window (VERIFIED 2026-10-08: "
                  "another chat spent 496 cr during a 111 cr run); a charge that matches no job here is not this "
                  "project's spend. Record matches with `status --charged`; refunds of blocked jobs arrive within "
                  "~5 s-4 min.")
DASH = "—"
# the re-roll fail list (budget.md section 3 rung 5 / D11): --reason must name one of these
FAIL_ITEMS = (
    ("identity", r"identity|\bface|likeness|\bhair|skin tone|\bbuild\b"),
    ("wardrobe", r"wardrobe|outfit|cloth|costume|garment"),
    ("garbled text/logo", r"\btext|\blogo|letter|garbled|caption|watermark"),
    ("anatomy", r"anatomy|\bhands?\b|finger|\blimbs?\b|\barms?\b|\blegs?\b|teeth"),
    ("matte-hostile background", r"background|\bmatte"),
    ("missing beat", r"\bbeats?\b|missing"),
    ("job failure", r"job failure|canary|half (of )?(the |its )?shots|whole job"),
)
FAIL_LIST_TEXT = ("identity | wardrobe | garbled text/logo | anatomy | matte-hostile background | missing beat "
                  "(the EDL needs it and no other plate second supplies it) | job failure (the canary, or >= half "
                  "of the job's shots fail for one cause)")

PLAN_HELP = """Plan: {currency: credits, hard_cap: finite number, lock: {aspect, fps, frames},
lines: [{id, model, tool, mode, resolution, duration OR frames+fps, count, takes, aspect_ratio,
quality, prompt, medias: [{role: image|video|audio|start_image|end_image|ref_element, value: actual_id}],
serves_cuts, screen_seconds, stage, options, identity, full_take, ip_suspect}]}.
Fresh video uses seedance_2_5 only. Direct Genjutsu source transformations are exceptions.
Preset-only records require verified_request: {operation: genjutsu_preset, tool: exact callable,
params: exact provider object, source: actual contract evidence, checked_at: UTC ISO timestamp,
allows_empty_prompt: true only when verified}. Native currency must be credits; never invent conversions.
Record each exact one-job estimate with price-set W --line ID --credits C --source estimate_video_cost
(or estimate_image_cost / verified_account_quote) --evidence actual-response-reference.
For a dependent stage use deferred:true, depends_on:[upstream line IDs], and input_bindings such as
{"medias.0.value":"still_line"}; media_id and draft_job_id are also supported binding paths.
Only these bound inputs may use placeholders. Record a verified per-job planning upper bound with
price-set --planning --basis actual-contract-basis plus the same credits/source/evidence fields.
Deferred jobs cannot submit. The first staged approval fixes the whole-workflow ceiling. When each
dependency completes, fill its exact job ID, set deferred:false, obtain a fresh exact quote, then
approve again under the unchanged ceiling. Other settings cannot change and exact cost cannot exceed
the planning bound. Never invent bounds or count a planning estimate as generation readiness.
Register selected work with approve --total N --hard-cap H --note task/account-authority.
Then guard one job, submit once, add its id immediately. Batches are disabled. Refunds require evidence.
A blocked route yields authorized alternatives/free work/partial delivery, never questions or consent."""


class LedgerError(Exception):
    pass


class Refused(Exception):
    pass


# ----------------------------------------------------------------------------------------------------
# small utils
# ----------------------------------------------------------------------------------------------------
def now_iso():
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def r2(x):
    return None if x is None else round(float(x) + 0.0, 2)


def fmt_cr(x):
    """3297.5 -> '3,297.5'; 0.96 -> '0.96'; 44.0 -> '44'."""
    if x is None:
        return "?"
    x = float(x)
    if x.is_integer():
        return f"{int(x):,}"
    return f"{x:,.12f}".rstrip("0").rstrip(".")


def fmt_signed(x):
    """+15 / -4 / +0 (credits delta)."""
    return ("-" if x is not None and float(x) < -1e-9 else "+") + fmt_cr(abs(float(x or 0)))


def fmt_num(x, nd=2):
    if x is None:
        return "?"
    x = float(x)
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    s = f"{x:.{nd}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def write_atomic(path, text):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        um = os.umask(0)
        os.umask(um)
        os.chmod(tmp, 0o666 & ~um)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def save_json(path, obj):
    write_atomic(path, json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def load_json(path, default=None, what="file"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if default is not None:
            return copy.deepcopy(default)
        raise LedgerError(f"{what} not found: {path}")
    except json.JSONDecodeError as e:
        raise LedgerError(f"{what} is not valid JSON: {path}: {e}")


class Lock:
    """Exclusive advisory lock on W/plan/.ledger.lock (parallel chats share one sandbox)."""

    def __init__(self, W):
        self.path = os.path.join(W, "plan", ".ledger.lock")
        self.fh = None

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.fh = open(self.path, "a+")
        if fcntl:
            fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        if self.fh:
            if fcntl:
                fcntl.flock(self.fh.fileno(), fcntl.LOCK_UN)
            self.fh.close()
        return False


def plan_dir(W):
    return os.path.join(W, "plan")


def p_plan(W):
    return os.path.join(W, "plan", "gen_plan.json")


def p_ledger(W):
    return os.path.join(W, "plan", "ledger.json")


def p_override(W):
    return os.path.join(W, "plan", "prices_override.json")


def norm_res(r):
    if r is None:
        return None
    s = str(r).strip().lower().replace(" ", "")
    if not s:
        return None
    if s.isdigit():
        s += "p"
    if s in ("2160p", "uhd"):
        s = "4k"
    return s


def fps_value(fps):
    if fps is None or fps == "":
        return None
    try:
        if isinstance(fps, str) and "/" in fps:
            n, d = fps.split("/", 1)
            return float(n) / float(d)
        return float(fps)
    except (TypeError, ValueError, ZeroDivisionError):
        raise LedgerError(f"bad fps {fps!r}")


def split_ids(vals):
    out = []
    for v in vals or []:
        for x in str(v).replace(";", ",").split(","):
            x = x.strip()
            if x and x not in out:
                out.append(x)
    return out


def fail_item(reason):
    """Canonical fail-list item named by a re-roll reason, or None ('a better take' is not a failure)."""
    s = str(reason or "").strip().lower()
    if not s:
        return None
    for name, pat in FAIL_ITEMS:
        if re.search(pat, s):
            return name
    return None


# ----------------------------------------------------------------------------------------------------
# prices
# ----------------------------------------------------------------------------------------------------
def finite_amount(value, name):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise LedgerError(f"{name} must be a finite nonnegative number")
    if not math.isfinite(number) or number < 0:
        raise LedgerError(f"{name} must be a finite nonnegative number")
    return number


def read_prompt(W, name):
    path = os.path.realpath(os.path.join(W, name))
    root = os.path.realpath(W)
    if os.path.commonpath([path, root]) != root:
        raise LedgerError("prompt_file must remain inside the current workspace")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    except OSError as exc:
        raise LedgerError(f"cannot read prompt_file: {exc}")


def config_hash(line, W=None):
    # Per submitted job: count/takes are serial repetitions, not one provider call.
    keys = ("model", "mode", "resolution", "duration", "frames", "fps", "quality", "aspect_ratio", "aspect",
            "draft", "finalize", "draft_job_id", "medias", "refs", "prompt", "prompt_file", "options",
            "generate_audio", "bitrate_mode", "media_type", "media_id", "chars", "declined_preset_id",
            "voice_id", "voice_type", "format", "sample_rate", "pitch_rate", "dialogue", "stability", "similarity_boost",
            "verified_request", "use_unlim", "use_free_gens", "_format_lock")
    data = {k: line[k] for k in keys if k in line}
    if line.get("prompt_file"):
        if W is None:
            raise LedgerError("workspace required to fingerprint prompt_file contents")
        data["prompt_file_contents"] = read_prompt(W, line["prompt_file"])
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def fresh_timestamp(at):
    try:
        stamp = _dt.datetime.fromisoformat(str(at))
        if stamp.tzinfo is None:
            return False
        age = (_dt.datetime.now(_dt.timezone.utc) - stamp).total_seconds()
        return 0 <= age <= LIVE_MAX_AGE_SECONDS
    except (ValueError, TypeError):
        return False


def exact_record(P, line):
    key = config_hash(line, P.W)
    return next((x for x in reversed(P.over.get("exact_quotes", []))
                 if x.get("config_hash") == key and x.get("currency") == "credits"
                 and x.get("evidence") and fresh_timestamp(x.get("at"))), None)


def planning_record(P, line):
    """A dependency-stage upper bound is never an executable request quote."""
    key = config_hash(line, P.W)
    return next((x for x in reversed(P.over.get("planning_quotes", []))
                 if x.get("config_hash") == key and x.get("currency") == "credits"
                 and x.get("evidence") and x.get("basis") and fresh_timestamp(x.get("at"))), None)


def bound_input(line, path, value=None, write=False):
    """Only documented job/media-ID fields may be resolved between stages."""
    if not isinstance(path, str) or not re.fullmatch(r"medias\.\d+\.value|media_id|draft_job_id", path):
        raise LedgerError("input_bindings paths must be medias.N.value, media_id or draft_job_id")
    parts = path.split(".")
    node = line
    try:
        for part in parts[:-1]:
            node = node[int(part)] if isinstance(node, list) else node[part]
        key = int(parts[-1]) if isinstance(node, list) else parts[-1]
        old = node[key]
        if write:
            node[key] = value
        return old
    except (KeyError, IndexError, TypeError, ValueError):
        raise LedgerError(f"input_bindings path does not exist: {path}")


def dependency_scope(line, W):
    bindings, deps = line.get("input_bindings"), line.get("depends_on")
    if (not isinstance(bindings, dict) or not bindings or not isinstance(deps, list) or not deps
            or any(not isinstance(x, str) or not x for x in deps)
            or len(set(deps)) != len(deps)
            or any(not isinstance(x, str) for x in bindings.values())
            or set(bindings.values()) != set(deps)):
        raise LedgerError("dependent lines require depends_on and input_bindings covering the same upstream line IDs")
    normalized = copy.deepcopy(line)
    for path, dep in bindings.items():
        bound_input(normalized, path, f"<dependency:{dep}>", write=True)
    return {"depends_on": deps, "input_bindings": bindings,
            "scope_hash": config_hash(normalized, W),
            "count": int(line.get("count", 1)), "takes": int(line.get("takes", 1))}


def validate_dependencies(lines):
    by_id = {line["id"]: line for line in lines}
    visiting, done = set(), set()

    def visit(lid):
        if lid in visiting:
            raise LedgerError("dependency plan contains a cycle")
        if lid in done:
            return
        visiting.add(lid)
        deps = by_id[lid].get("depends_on") or []
        if not isinstance(deps, list):
            raise LedgerError("depends_on must be a list of selected upstream line IDs")
        for dep in deps:
            if not isinstance(dep, str) or dep not in by_id:
                raise LedgerError("dependency is not a selected plan line")
            visit(dep)
        visiting.remove(lid)
        done.add(lid)

    for lid in by_id:
        visit(lid)


def deferred_contract(W, plan, line, q, P):
    contract = dependency_scope(line, W)
    # Validate the complete supported call shape while keeping future IDs out of executable params.
    ready_shape = copy.deepcopy(line)
    for path in contract["input_bindings"]:
        value = bound_input(line, path)
        if not isinstance(value, str) or not (value.startswith("<") and value.endswith(">")):
            raise LedgerError("deferred input bindings must use explicit unresolved placeholders")
        bound_input(ready_shape, path, "dependency-result-for-local-validation", write=True)
    tool, params, _, _ = params_skeleton(W, plan, ready_shape, q, P.entry(q["model"], line.get("mode")))
    validate_request(ready_shape, params, tool)
    validate_duration_warnings(q)
    if tool.endswith("_batch") or q.get("free"):
        raise LedgerError("deferred stages must be supported single paid jobs")
    contract["per_job_bound"] = q["per_job"]
    contract["planning_quote"] = copy.deepcopy(planning_record(P, line))
    return contract


def validate_activation(W, line, q, contract, ledger):
    scope = dependency_scope(line, W)
    if any(scope[k] != contract[k] for k in scope):
        raise LedgerError("deferred stage scope/settings changed; only its bound input IDs may resolve")
    if q["per_job"] > contract["per_job_bound"] + 1e-9:
        raise LedgerError("exact dependent-job quote exceeds its verified planning upper bound")
    for path, dep in contract["input_bindings"].items():
        actual = bound_input(line, path)
        if not any(job.get("line") == dep and job.get("job_id") == actual
                   and job.get("state") == "completed" for job in ledger["jobs"]):
            raise LedgerError(f"{path} must name a completed job from dependency {dep}")


def verified_preset(line, record):
    model = str(line.get("model") or "")
    return (isinstance(record, dict) and bool(record.get("source")) and fresh_timestamp(record.get("checked_at"))
            and isinstance(record.get("params"), dict) and bool(record.get("tool"))
            and record.get("operation") == "genjutsu_preset"
            and (model.startswith("genjutsu:") or model == "higgsfield/genjutsu/restyle/v1.0"))


def validate_request(line, params, tool=None):
    def placeholders(value):
        if isinstance(value, str):
            return value.startswith("<") and value.endswith(">")
        if isinstance(value, dict):
            return any(placeholders(x) for x in value.values())
        if isinstance(value, list):
            return any(placeholders(x) for x in value)
        return False
    if placeholders(params):
        raise LedgerError("request has unresolved prompt/media/format placeholders")
    if params.get("count", 1) != 1:
        raise LedgerError("provider count must be one for serialized dispatch")
    validate_payment_fields(params, tool)
    actual_model = params.get("model")
    if actual_model is not None and actual_model != line.get("model"):
        vr = line.get("verified_request")
        preset_id = str(params.get("preset_id") or "")
        verified_wrapper = (actual_model == "higgsfield_preset" and preset_id
                            and line.get("model") == "genjutsu:" + preset_id
                            and verified_preset(line, vr))
        if not vr or (actual_model not in ALLOWED_VIDEO and not verified_wrapper):
            raise LedgerError("provider model differs from the allowed planned operation")
    # Pricing metadata describes cost, never grants a creative video-engine exception.
    operation = str(tool or "").rsplit("__", 1)[-1]
    if operation in VIDEO_TOOLS:
        wrapper = (actual_model == "higgsfield_preset" and bool(params.get("preset_id"))
                   and line.get("model") == "genjutsu:" + str(params["preset_id"])
                   and verified_preset(line, line.get("verified_request")))
        if actual_model not in ALLOWED_VIDEO | VIDEO_UTILITIES and not wrapper:
            raise LedgerError("video callable requires seedance_2_5, a direct Genjutsu operation, or an explicit supported utility/preset")
    if line.get("model") == "seed_audio":
        if not isinstance(params.get("voice_id"), str) or not params["voice_id"].strip():
            raise LedgerError("selected voice_id is missing; preserve source audio or report the unsupported branch")
    if line.get("model") == "elevenlabs_v4":
        dialogue = params.get("dialogue")
        if not isinstance(dialogue, list) or not dialogue or any(
                not isinstance(turn, dict) or not isinstance(turn.get("text"), str)
                or not isinstance(turn.get("voice_id"), str) or not turn["voice_id"].strip()
                or not isinstance(turn.get("voice_type"), str) or not turn["voice_type"].strip()
                for turn in dialogue):
            raise LedgerError("dialogue requires text and an existing selected voice pair for every turn")
    for media in params.get("medias", []):
        if not isinstance(media, dict) or media.get("role") not in CANONICAL_ROLES or not media.get("value"):
            raise LedgerError("media must use a supported canonical role and actual reference id")
    if line.get("model") in ("hf_mult_motion_control", "hf_mult_replace_object") or line.get("verified_request"):
        prompt = str(params.get("prompt", ""))
        if len(prompt.split()) > 40 or len(re.findall(r"[.!?](?:\s|$)", prompt)) > 2:
            raise LedgerError("Genjutsu prompt exceeds two short sentences or 40 words")
        if not prompt and not (line.get("verified_request") or {}).get("allows_empty_prompt"):
            raise LedgerError("empty Genjutsu prompt requires a verified preset contract that explicitly allows it")


def validate_payment_fields(params, tool):
    operation = str(tool or "").rsplit("__", 1)[-1]
    for field in ("use_unlim", "use_free_gens"):
        if field not in params:
            continue
        if not isinstance(params[field], bool):
            raise LedgerError(f"{field} must be a boolean covered by existing payment authority")
        supported = (operation in ("generate_image", "generate_video") if field == "use_unlim" else
                     operation == "generate_video" and params.get("model") in
                     ("hf_mult_replace_object", "hf_mult_motion_control"))
        if not supported:
            raise LedgerError(f"{field} is unsupported for this callable/model; do not invent allowance fields")


def hard_cap(plan):
    if plan.get("hard_cap") is None:
        raise LedgerError("explicit finite hard_cap missing")
    return min(finite_amount(plan[k], k) for k in ("hard_cap", "user_limit", "account_limit", "workflow_ceiling") if plan.get(k) is not None)


def submission_price(W, plan, line, P):
    if line.get("deferred"):
        raise LedgerError("deferred stage is non-executable; resolve dependencies and register its fresh exact quote first")
    q = price_line(line, P)
    if q.get("free"):
        return q
    record = exact_record(P, line)
    if record is None:
        raise LedgerError(f"{line['id']}: current exact one-job cost estimate missing; use a non-submitting estimator")
    tool, params, notes, spec = params_skeleton(W, plan, line, q, P.entry(q["model"], line.get("mode")))
    validate_request(line, params, tool)
    validate_duration_warnings(q)
    if tool.endswith("_batch"):
        raise LedgerError("batch submission is disabled; use one-job serialization")
    return q


def validate_duration_warnings(q):
    if any("REJECTED" in w or "exceeds the model maximum" in w or "longer than the longest allowed" in w
           for w in q.get("warnings", [])):
        raise LedgerError("planned duration violates the supported model contract")


class Prices:
    def __init__(self, default_path=DEFAULT_PRICES, W=None):
        self.path = default_path
        self.W = W
        self.base = load_json(default_path, what="price table")
        self.aliases = {k.lower(): v for k, v in (self.base.get("aliases") or {}).items()}
        self.free = set(x.lower() for x in self.base.get("free") or [])
        self.override_path = p_override(W) if W else None
        self.over = {"entries": []}
        if self.override_path and os.path.exists(self.override_path):
            self.over = load_json(self.override_path, what="price override")
            self.over.setdefault("entries", [])

    def canon(self, model):
        if model is None:
            return None
        m = str(model).strip()
        return self.aliases.get(m.lower(), m)

    def is_free(self, model_or_tool):
        return model_or_tool is not None and str(model_or_tool).strip().lower() in self.free

    def entry(self, model, mode=None):
        """Effective price entry for (model, mode): base + mode overrides + live overrides.

        Returns None for an unknown model. Adds '_live' {rate_key: override record} and '_mode'.
        """
        m = self.canon(model)
        base = (self.base.get("models") or {}).get(m)
        ovs = [o for o in self.over.get("entries", []) if self.canon(o.get("model")) == m]
        if base is None and not ovs:
            return None
        if base is None:
            o0 = ovs[-1]
            base = {"kind": o0.get("kind") or ("video" if o0.get("unit") == "second" else "image"),
                    "unit": o0.get("unit", "job"), "rates": {}, "min_s": 0, "seconds": "ceil"}
        e = copy.deepcopy(base)
        modes = e.get("modes") or {}
        eff_mode = mode if (mode and mode in modes) else None
        if eff_mode:
            md = modes[eff_mode]
            for k, v in md.items():
                if k == "note":
                    e["note"] = (e.get("note", "") + " | " if e.get("note") else "") + v
                else:
                    e[k] = copy.deepcopy(v)
        e["_mode"] = eff_mode
        e["_live"] = {}
        for o in ovs:  # later entries win
            om = o.get("mode")
            om = om if (om and om in modes) else None
            if om != eff_mode:
                continue
            e.setdefault("rates", {})[o["key"]] = o["price"]
            e["_live"][o["key"]] = o
            if o.get("unit") and o["unit"] != e.get("unit"):
                e["unit"] = o["unit"]
        e["_model"] = m
        return e

    def lookup(self, e, res, quality):
        """(rate_key, rate) for the requested resolution / quality, or (None, None)."""
        rates = e.get("rates") or {}
        res = norm_res(res) or norm_res(e.get("default_res"))
        res = (e.get("res_aliases") or {}).get(res, res)
        q = (quality or e.get("default_quality"))
        q = str(q).strip().lower() if q else None
        cands = []
        if q:
            cands += [f"{q}/{res}", f"{q}/*"]
        cands += [res, "*"]
        for k in cands:
            if k is not None and k in rates:
                return k, float(rates[k])
        return None, None


def bill_seconds(d, e):
    """Billed seconds for a planned duration d under entry e -> (billed, notes, warnings).

    Rules (prices.json): ceil (Seedance, Genjutsu replace: trim/pad to an exact integer), round (Genjutsu
    motion transfer: round to nearest; pad only when the fraction is > 0.1 s), exact.
    """
    notes, warns = [], []
    rule = e.get("seconds", "ceil")
    eps = float(e.get("eps", 0.01))
    fps = float(e.get("driving_fps") or 24)
    if rule == "round":
        s = math.floor(d + 0.5)
    elif rule == "exact":
        s = float(d)
    else:
        s = math.ceil(d - eps) if d > eps else 0
    mn = float(e.get("min_s", 0) or 0)
    if rule != "exact" and abs(s - d) > 1e-6 and d >= mn - 1e-6:
        if rule == "ceil" and e.get("fixed_input"):
            lo = max(int(s) - 1, int(mn))
            notes.append(f"{fmt_num(d, 3)} s input bills as {fmt_num(s)} s (rounds up): trim to exactly "
                         f"{lo}.00 s ({int(lo * fps)} frames @{fmt_num(fps)}) or pad to exactly {fmt_num(s)}.00 s "
                         f"({int(s * fps)} frames); cuts under 4 s real time: ping-pong to exactly 96 frames @24")
        elif rule == "round" and e.get("fixed_input"):
            if s < d:
                lost = d - s
                lost_f = int(math.ceil(lost * fps - 1e-6))
                if lost <= 0.1 + 1e-9:
                    notes.append(f"{fmt_num(d, 3)} s input bills as {fmt_num(s)} s (rounds to nearest): do not pad; "
                                 f"fill the <= {lost_f} lost tail frame(s) in code")
                else:
                    notes.append(f"{fmt_num(d, 3)} s input bills as {fmt_num(s)} s (rounds to nearest) and drops "
                                 f"~{fmt_num(lost, 2)} s ({lost_f} frames): freeze-pad to exactly {fmt_num(s + 1)}.00 s "
                                 f"({int((s + 1) * fps)} frames @{fmt_num(fps)}) and re-price, or trim to "
                                 f"{fmt_num(s)}.00 s")
            else:
                notes.append(f"{fmt_num(d, 3)} s input bills as {fmt_num(s)} s (rounds up to the nearest second): "
                             f"freeze-pad to exactly {fmt_num(s)}.00 s ({int(s * fps)} frames @{fmt_num(fps)}) so the "
                             f"paid second carries frames")
        elif rule == "ceil":
            notes.append(f"duration {fmt_num(d)} s -> {fmt_num(s)} s (whole seconds)")
    if e.get("min_rule") == "reject" and d < mn - 1e-6:
        warns.append(f"{fmt_num(d, 3)} s input is under the ~{fmt_num(mn)} s minimum and will be REJECTED: "
                     f"ping-pong pad to 96 frames @24 (4.00 s); priced at {fmt_num(max(s, mn))} s")
    if s < mn:
        if e.get("min_rule") != "reject":
            notes.append(f"min-duration billing: pays {fmt_num(mn)} s for {fmt_num(d)} s (pack short shots into a plate)")
        s = mn
    allowed = e.get("allowed_s")
    if allowed:
        up = [a for a in sorted(allowed) if a >= s - 1e-9]
        if up:
            if abs(up[0] - s) > 1e-9:
                notes.append(f"{fmt_num(s)} s snaps to the allowed {fmt_num(up[0])} s")
            s = up[0]
        else:
            warns.append(f"{fmt_num(d)} s is longer than the longest allowed duration {max(allowed)} s: split it")
            s = max(allowed)
    mx = e.get("max_s")
    if mx and s > float(mx) + 1e-9:
        warns.append(f"{fmt_num(s)} s exceeds the model maximum {fmt_num(mx)} s: split into several jobs")
    return float(s), notes, warns


def line_duration(line):
    """Seconds of a line: frames / fps when both are given (the probed driving clip), else duration."""
    fpsv = fps_value(line.get("fps"))
    if line.get("frames") is not None and fpsv:
        return float(line["frames"]) / fpsv
    if line.get("duration") is not None:
        return float(line["duration"])
    return None


def price_line(line, P):
    """Price one plan line. Returns a dict with per_job, credits, jobs, billed_s, rerolls, notes, ..."""
    lid = str(line.get("id"))
    stage = line.get("stage") or "other"
    tool = line.get("tool")
    model = line.get("model")
    if not model and tool in ("remove_background",):
        model = "image_background_remover" if str(line.get("media_type", "")).lower() == "image" else "remove_background"
    count = int(line.get("count", 1) if line.get("count") is not None else 1)
    takes = int(line.get("takes", 1) if line.get("takes") is not None else 1)
    if count < 1 or takes < 1:
        raise LedgerError("count and takes must be positive integers")
    for key in ("duration", "frames", "fps"):
        if line.get(key) is not None:
            value = fps_value(line[key]) if key == "fps" else finite_amount(line[key], key)
            if not math.isfinite(value) or value <= 0:
                raise LedgerError(f"{key} must be positive and finite")
    jobs = count * takes
    out = {"id": lid, "stage": stage, "purpose": line.get("purpose", ""), "tool": tool, "model": model,
           "mode": line.get("mode"), "resolution": None, "quality": line.get("quality"),
           "draft": bool(line.get("draft")), "duration": line_duration(line), "billed_s": None,
           "frames": line.get("frames"), "fps": line.get("fps"),
           "count": count, "takes": takes, "jobs": jobs, "unit": None, "unit_price": None, "per_job": 0.0,
           "credits": 0.0, "est": False, "free": False, "price_source": None, "rate_key": None,
           "serves_cuts": line.get("serves_cuts") or [], "screen_seconds": line.get("screen_seconds"),
           "kind": None, "reroll_per_job": 0.0, "est_uncertainty": 0.0, "notes": [], "warnings": [],
           "options": dict(line.get("options") or {}),
           "optional": bool(line.get("optional")), "take_of": line.get("take_of"),
           "full_take": bool(line.get("full_take")), "identity": bool(line.get("identity")),
           "take_reason": line.get("take_reason") or line.get("reason")}
    if (not model and P.is_free(tool)) or P.is_free(model):
        out.update(free=True, kind="free", price_source="free", model=model or tool)
        return out
    if not model:
        raise LedgerError(f"line {lid}: no model (and tool {tool!r} is not a free tool)")
    e = P.entry(model, line.get("mode"))
    if e is None:
        vr = line.get("verified_request")
        if not verified_preset(line, vr):
            raise LedgerError(f"{model}: missing supported model contract; no generic call will be fabricated")
        exact = planning_record(P, line) if line.get("deferred") else exact_record(P, line)
        if exact is None:
            raise LedgerError("verified preset needs its exact native-credit estimate before pricing")
        e = {"kind": "post", "unit": "job", "rates": {"*": exact["credits"]}, "_model": model}
    out["model"] = e.get("_model", model)
    if e.get("kind") == "video" and out["model"] not in ALLOWED_VIDEO:
        raise LedgerError(f"{out['model']}: fresh video is limited to seedance_2_5; only verified Genjutsu transformations are exceptions")
    out["kind"] = e.get("kind", "video")
    if out["kind"] == "image" and takes > 3:
        raise LedgerError("at most three image attempts per item, including retries")
    out["unit"] = e.get("unit", "job")
    own_res = line.get("resolution")
    if own_res is not None and "resolution" in (line.get("_inherited") or ()) and not res_is_key(e, own_res):
        # defaults.resolution is a video setting: a still's size, a matte or a TTS take does not inherit it
        if out["kind"] == "video":
            out["notes"].append(f"defaults.resolution {own_res} is not a resolution of {out['model']}: its default "
                                f"{e.get('default_res') or '-'} is used")
        own_res = None
    res = norm_res(own_res) or norm_res(e.get("default_res"))
    bill_res = res
    fin = e.get("finalize") or {}
    out["finalize"] = bool(line.get("finalize"))
    if out["finalize"]:
        if out["draft"]:
            out["warnings"].append("a line is either a draft or its finalize, not both")
        elif not fin:
            out["warnings"].append(f"finalize (draft_job_id) is not supported for {out['model']} in prices.json")
        else:
            fres = norm_res(fin.get("res", "1080p"))
            line_res = None if "resolution" in (line.get("_inherited") or ()) else norm_res(line.get("resolution"))
            if line_res and line_res != fres:
                out["warnings"].append(f"finalize is always {fres} (a {line_res} param is ignored): priced at {fres}")
            res = bill_res = fres
            if line.get("duration") is None and line.get("frames") is None:
                out["duration"] = float(fin.get("default_s", 5))
                out["warnings"].append(f"finalize without duration prices {fmt_num(out['duration'])} s: pass "
                                       f"the draft's own duration")
            if fin.get("note"):
                out["notes"].append(fin["note"])
    if out["draft"]:
        rates0 = e.get("rates") or {}
        if "draft" in rates0 or e.get("draft_res"):
            bill_res = "draft" if "draft" in rates0 else e["draft_res"]
            out["notes"].append(e.get("draft_note") or f"draft bills at {bill_res}; finalize = a full "
                                                       f"{norm_res(fin.get('res', '1080p'))} job")
        else:
            out["warnings"].append(f"draft is not supported for {out['model']} in prices.json")
    out["resolution"] = res
    if line.get("unit_price") is not None and e.get("rates") is not None and not out["est"]:
        key, rate = "plan", float(line["unit_price"])
        out["price_source"] = "plan unit_price"
        out["est"] = bool(line.get("est", True))
    else:
        key, rate = P.lookup(e, bill_res, line.get("quality"))
        if key is None:
            have = ", ".join(sorted((e.get("rates") or {}).keys()))
            raise LedgerError(f"line {lid}: no price for {out['model']} at {bill_res or '-'}"
                              f"{' / ' + str(line.get('quality')) if line.get('quality') else ''} (have: {have})")
        live = e.get("_live", {}).get(key)
        out["price_source"] = (f"live {live.get('source', 'dedicated estimator')} {live.get('at', '')[:10]}".strip()
                               if live else "default " + str(P.base.get("verified_at", "")))
        if e.get("est") and not live:
            out["est"] = True
    out["rate_key"] = key
    out["unit_price"] = rate
    unit = out["unit"]
    fpsv = fps_value(line.get("fps"))
    dfps = e.get("driving_fps")
    if dfps and fpsv and abs(fpsv - float(dfps)) > 0.01:
        out["warnings"].append(f"driving clip at {fmt_num(fpsv, 3)} fps: Genjutsu inputs are {fmt_num(dfps)} fps "
                               f"exports (frames.py export --fps {fmt_num(dfps)}, then pad); a native-fps pad of a "
                               f"25/30/50/60 fps reference runs longer than the cut and bills more")
    if unit == "second":
        d = out["duration"]
        if d is None:
            raise LedgerError(f"line {lid}: {out['model']} is billed per second: give duration (or frames + fps)")
        if (line.get("frames") is not None and fpsv and line.get("duration") is not None
                and abs(float(line["duration"]) - d) > 0.005):
            out["notes"].append(f"priced from frames ({line['frames']} f @{fmt_num(fpsv, 3)} = {fmt_num(d, 3)} s), "
                                f"not duration {fmt_num(line['duration'])}")
        billed, notes, warns = bill_seconds(d, e)
        out["billed_s"] = billed
        out["notes"] += notes
        out["warnings"] += warns
        per_job = billed * rate
    elif unit == "chars":
        chars = line.get("chars")
        if chars is None:
            chars = e.get("default_chars", 300)
            out["est"] = True
            out["notes"].append(f"no chars given: assumed {chars} characters")
        per = float(e.get("per_chars", 30))
        per_job = math.ceil(float(chars) / per) * rate
    else:
        per_job = rate
    for opt, val in (line.get("options") or {}).items():
        if not val:
            continue
        o = (e.get("options") or {}).get(opt)
        if o is None:
            continue
        per_job += float(o.get("surcharge", 0) or 0)
        if o.get("est"):
            out["est"] = True
        if o.get("note"):
            out["notes"].append(f"{opt}: {o['note']}")
    exact = planning_record(P, line) if line.get("deferred") else exact_record(P, line)
    if line.get("deferred") and exact is None:
        raise LedgerError(f"{lid}: deferred stage needs a current verified planning upper bound, not historical rates")
    if exact is not None:
        per_job = finite_amount(exact["credits"], "live job estimate")
        out["price_source"] = ("planning upper bound " if line.get("deferred") else "live exact ") + exact["at"]
        out["est"] = False
    out["deferred"] = bool(line.get("deferred"))
    out["per_job"] = per_job
    out["credits"] = per_job * jobs
    if e.get("est_hi") is not None and out["est"]:
        mult = out["billed_s"] if unit == "second" else 1.0
        out["est_uncertainty"] = max(0.0, (float(e["est_hi"]) - rate) * mult * jobs)
    # A permitted retry can cost the entire source job, never just its minimum duration.
    if stage != "reroll" and not out["draft"] and jobs > 0:
        if out["kind"] == "video":
            out["reroll_per_job"] = per_job
        elif out["kind"] == "image":
            out["reroll_per_job"] = per_job * min(jobs, max(0, 3 * count - jobs)) / jobs
    out["e_fixed_input"] = bool(e.get("fixed_input"))
    out["e_genjutsu"] = e.get("genjutsu")
    out["e_min_s"] = float(e.get("min_s", 0) or 0)
    out["e_allowed"] = e.get("allowed_s")
    out["e_size_factor"] = e.get("size_factor") or [1.5, 2.5]
    out["e_rates"] = dict(e.get("rates") or {})
    out["e_res_aliases"] = dict(e.get("res_aliases") or {})
    call = e.get("call") or {}
    out["e_check"] = list(call.get("check") or [])
    out["e_set"] = dict(call.get("set") or {})
    vl = e.get("verified_live") or {}
    out["verified_live"] = (vl.get(key) if not (e.get("_live") or {}).get(key) else None) if key != "plan" else None
    if out["kind"] == "image":
        # a still's size: its own resolution, else the model's default size (never the plan's video default)
        out["img_size"] = res or norm_res(call.get("res_default"))
    out["res_label"] = res_label(out)
    if e.get("note"):
        out["model_note"] = e["note"]
    return out


def res_is_key(e, r):
    """True when resolution r names a rate of entry e (directly, via res_aliases, or as the size of a q/size key)."""
    s = norm_res(r)
    if not s:
        return False
    s = (e.get("res_aliases") or {}).get(s, s)
    rates = e.get("rates") or {}
    return s in rates or any(str(k).split("/")[-1] == s for k in rates)


def res_label(q):
    """The quote's Res cell: resolution for video (and per-second post jobs), quality/size for a still, an em
    dash for everything else (mattes, audio): a still never shows the plan's video resolution."""
    if q.get("free"):
        return "-"
    if q.get("kind") == "video" or (q.get("unit") == "second" and q.get("kind") == "post"):
        s = q.get("resolution") or DASH
        if q.get("draft"):
            s += " (draft)"
        if q.get("finalize"):
            s += " (finalize)"
        if q.get("identity"):
            s += " · identity"
        return s
    if q.get("kind") == "image":
        parts = []
        for x in (q.get("quality"), q.get("img_size")):
            x = str(x).strip().lower() if x else None
            if x and x not in parts:
                parts.append(x)
        return "/".join(parts) or DASH
    return DASH


def fingerprint(q):
    """Settings that fix what one job of a line costs and returns (stored at approval)."""
    return {"model": q.get("model"), "mode": q.get("mode"), "resolution": q.get("resolution"),
            "quality": q.get("quality"), "draft": bool(q.get("draft")), "finalize": bool(q.get("finalize")),
            "billed_s": q.get("billed_s"), "unit": q.get("unit")}


def fp_changes(al, q):
    """'field old -> new; ...' for an approved line record vs the current pricing (None if unchanged)."""
    out = []
    fp = fingerprint(q)
    for k, v in fp.items():
        if k not in al:
            continue
        old = al.get(k)
        if (k == "resolution" and q.get("kind") != "video" and q.get("unit") != "second"
                and al.get("per_job") is not None and abs(float(al["per_job"]) - float(q.get("per_job") or 0)) < 0.005):
            continue  # a still / matte / audio line: a resolution label that does not change its price
        if k == "billed_s":
            if old is None and v is None:
                continue
            if old is not None and v is not None and abs(float(old) - float(v)) < 1e-6:
                continue
        elif (old or None) == (v or None):
            continue
        sv = (lambda x: "-" if x is None else (fmt_num(x) if isinstance(x, (int, float)) and not isinstance(x, bool)
                                               else str(x)))
        out.append(f"{k} {sv(old)} -> {sv(v)}")
    if al.get("jobs") is not None and q.get("jobs", 0) > int(al["jobs"]):
        out.append(f"jobs {al['jobs']} -> {q['jobs']}")
    return "; ".join(out) or None


# ----------------------------------------------------------------------------------------------------
# plan
# ----------------------------------------------------------------------------------------------------
def load_plan(W, required=True):
    path = p_plan(W)
    if not os.path.exists(path):
        if required:
            raise LedgerError(f"no plan: write {path} first (see `ledger.py quote --help`)")
        return None
    plan = load_json(path, what="plan")
    if not isinstance(plan, dict) or not isinstance(plan.get("lines"), list):
        raise LedgerError(f"{path}: expected an object with a 'lines' list")
    if plan.get("currency", "credits") != "credits":
        raise LedgerError("plan currency must be credits; native-currency quotes cannot be implicitly converted")
    return plan


def plan_lines(plan):
    defaults = plan.get("defaults") or {}
    out, seen = [], set()
    for i, ln in enumerate(plan.get("lines") or []):
        if not isinstance(ln, dict):
            raise LedgerError(f"plan line #{i + 1} is not an object")
        L = dict(defaults)
        L.update(ln)
        L["_format_lock"] = copy.deepcopy(plan.get("lock") or {})
        inh = [k for k in defaults if k not in ln]
        if inh:
            L["_inherited"] = inh
        if not L.get("id"):
            L["id"] = f"L{i + 1}"
        if L["id"] in seen:
            raise LedgerError(f"duplicate plan line id {L['id']!r}")
        seen.add(L["id"])
        out.append(L)
    # a second-take line (take_of) inherits the settings of the line it repeats (its own keys win)
    byid = {str(L["id"]): L for L in out}
    raw = {str(ln.get("id") or f"L{i + 1}"): ln for i, ln in enumerate(plan.get("lines") or [])}
    for i, L in enumerate(out):
        t = L.get("take_of")
        if t is not None and str(t) in byid and str(t) != str(L["id"]):
            M = {k: v for k, v in byid[str(t)].items() if k not in TAKE_OWN}
            own = raw.get(str(L["id"]), {})
            M.update(own)
            for k in TAKE_OWN:
                if k in L:
                    M[k] = L[k]
            if own.get("resolution") is not None:  # the take's own resolution is never 'inherited'
                M["_inherited"] = [k for k in (M.get("_inherited") or []) if k != "resolution"]
            out[i] = M
    return out


def find_line(plan, lid):
    if not plan:
        return None
    for L in plan_lines(plan):
        if str(L.get("id")) == str(lid):
            return L
    return None


def get_approval(plan):
    a = (plan or {}).get("approval")
    return a if isinstance(a, dict) else None


def approved_lines(plan):
    """{line id: approved record} or None (no approval, or approved by an older ledger.py without lines)."""
    a = get_approval(plan)
    if a and isinstance(a.get("lines"), dict):
        return a["lines"]
    return None


def variant_line(L0, duration=None, frames=None, fps=None):
    """The line with a probed / changed length (re-priced from it)."""
    A = dict(L0)
    if frames is not None:
        A["frames"] = int(frames)
        A["fps"] = fps if fps is not None else (A.get("fps") or 24)
        A.pop("duration", None)
    elif duration is not None:
        A["duration"] = float(duration)
        A.pop("frames", None)
        A.pop("fps", None)
    return A


def reroll_line(L0, P, slot=None, duration=None, frames=None, fps=None):
    """One re-roll job of a line: a single-shot job of max(min_s, ceil(2 x slot)) s (shot failure), or the
    whole job again (job failure / Genjutsu: the same driving clip)."""
    q0 = price_line(L0, P)
    A = dict(L0)
    A["count"], A["takes"] = 1, 1
    A["optional"] = False
    if slot is not None:
        if q0.get("e_fixed_input"):
            raise LedgerError(f"line {L0.get('id')}: --slot applies to generated plates; a Genjutsu re-roll re-runs "
                              f"the same driving clip (whole job)")
        if q0.get("unit") != "second":
            raise LedgerError(f"line {L0.get('id')}: --slot only applies to per-second video lines")
        d = max(q0.get("e_min_s") or 0, math.ceil(2.0 * float(slot) - 1e-9))
        A = variant_line(A, duration=d)
    elif duration is not None or frames is not None:
        A = variant_line(A, duration=duration, frames=frames, fps=fps)
    return A


# ----------------------------------------------------------------------------------------------------
# quote
# ----------------------------------------------------------------------------------------------------
def settings_str(q):
    if q.get("free"):
        return f"{q.get('model') or q.get('tool')} (free)"
    parts = [q["model"]]
    if q.get("mode"):
        parts.append(q["mode"])
    if q.get("quality"):
        parts.append(str(q["quality"]))
    if q.get("resolution") and (q.get("kind") == "video" or q.get("rate_key") not in ("*", None)):
        parts.append(q["resolution"])
    if q.get("draft"):
        parts.append("draft")
    if q.get("finalize"):
        parts.append("finalize")
    return " ".join(str(p) for p in parts if p)


def model_str(q):
    """Model, mode, quality and options (resolution has its own column)."""
    if q.get("free"):
        return f"{q.get('model') or q.get('tool')} (free)"
    parts = [q["model"], q.get("mode"), q.get("quality")]
    parts += [k for k, v in (q.get("options") or {}).items() if v]
    return " ".join(str(p) for p in parts if p)


def qty_str(q):
    if q.get("free"):
        return "-"
    if q["unit"] == "second":
        b, d = q["billed_s"], q["duration"]
        s = f"{fmt_num(b)} s"
        if d is not None and abs(b - d) > 1e-6:
            s = f"{fmt_num(b)} s ({fmt_num(d)})"
        return f"{s} x {q['jobs']}" if q["jobs"] != 1 else s
    return str(q["jobs"])


def unit_str(q):
    if q.get("free"):
        return "0"
    u = fmt_num(q["unit_price"], 4)
    if q["unit"] == "second":
        return f"{u}/s"
    if q["unit"] == "chars":
        return f"{u}/30ch"
    return u


def with_res(L, res):
    """Line L at another resolution (an explicit choice: no longer 'inherited' from defaults)."""
    A = dict(L)
    A["resolution"] = res
    if A.get("_inherited"):
        A["_inherited"] = [k for k in A["_inherited"] if k != "resolution"]
    return A


def ip_suspect_map(plan, lines, priced):
    """IP-suspect cuts on planned Genjutsu replace (SWAP) lines.

    Sources: a line's "ip_suspect" (true = all its cuts, "film name" = all its cuts of that film, [cuts] = those
    cuts) and the plan's "ip_suspect_cuts" ([cuts] or {film: [cuts]}). Returns {"by_line": {line id: [cuts]},
    "film": {cut: film or None}, "cuts": [...], "warnings": [...]}.
    """
    warns = []
    plan_cuts = {}
    raw = (plan or {}).get("ip_suspect_cuts")
    if isinstance(raw, dict):
        for f, cs in raw.items():
            for c in (cs if isinstance(cs, list) else [cs]):
                plan_cuts[str(c)] = str(f)
    elif isinstance(raw, list):
        for c in raw:
            plan_cuts[str(c)] = None
    elif raw is not None:
        warns.append("ip_suspect_cuts: expected a list of cut ids or {\"film\": [cut ids]}")
    by_line, film, seen = {}, {}, set()
    for L, q in zip(lines, priced):
        flag = L.get("ip_suspect")
        serves = [str(c) for c in (q.get("serves_cuts") or [])]
        is_rep = q.get("e_genjutsu") == "replace" and not q.get("free")
        cuts = []
        if flag:
            if not is_rep:
                warns.append(f"{q['id']}: ip_suspect applies to Genjutsu replace (SWAP) lines; {q.get('model')} has "
                             f"no 'if blocked' re-route (motion transfer is not IP-blocked in the evidence)")
            elif q.get("in_plan"):
                if isinstance(flag, list):
                    cuts = [str(c) for c in flag]
                    label = None
                else:
                    cuts = serves or [f"{q['id']}#{i + 1}" for i in range(q["count"])]
                    label = flag if isinstance(flag, str) else None
                for c in cuts:
                    film.setdefault(c, label)
        if is_rep and q.get("in_plan"):
            for c in serves:
                if c in plan_cuts and c not in cuts:
                    cuts.append(c)
                    film[c] = plan_cuts[c] if plan_cuts[c] is not None else film.get(c)
        if cuts:
            cuts = list(dict.fromkeys(cuts))
            if len(cuts) > q["count"]:
                warns.append(f"{q['id']}: {len(cuts)} IP-suspect cuts on a line of count {q['count']}: only "
                             f"{q['count']} priced in the 'if blocked' row (one Genjutsu job per cut)")
                cuts = cuts[:q["count"]]
            by_line[q["id"]] = cuts
            seen.update(cuts)
    missing = [c for c in plan_cuts if c not in seen]
    if missing:
        warns.append(f"ip_suspect_cuts {', '.join(missing)}: not served by a planned Genjutsu replace line, so no "
                     f"'if blocked' cost for them (fine once they are re-routed to motion transfer; otherwise add each "
                     f"cut to its SWAP line's serves_cuts)")
    if by_line:
        stage_of = {q["id"]: q["stage"] for q in priced}
        on_canary = {c for lid, cs in by_line.items() if stage_of.get(lid) == "canary" for c in cs}
        groups = {}
        for cs in by_line.values():
            for c in cs:
                groups.setdefault(film.get(c) or "", []).append(c)
        for f, cs in groups.items():
            if not on_canary & set(cs):
                who = f"IP-suspect {f}" if f else "IP-suspect cuts without a film name"
                warns.append(f"{who} ({', '.join(cs)}): none on a canary-stage line: one cut per suspected film rides "
                             f"in the planned test sequence; verify any refund separately")
    return {"by_line": by_line, "film": film, "cuts": [c for cs in by_line.values() for c in cs], "warnings": warns}


def if_blocked(lines, priced, P, ipm, planned, worst):
    # A refusal does not authorize a model switch, new still, matte or assumed refund.
    return None


def why_no_alt(lines, priced, has_genjutsu, has_ip):
    """Why no cheaper alternative is derivable, per line group (the quote says it instead of a bare 'none')."""
    groups = {}
    for L, q in zip(lines, priced):
        if q.get("free"):
            continue
        if q.get("kind") != "video":
            why = "priced per still / job / take (nothing to size down)"
        else:
            r = []
            res = q.get("resolution")
            if q.get("draft"):
                r.append("draft (already the cheapest preview)")
            elif q.get("finalize"):
                r.append("finalize (always 1080p)")
            elif L.get("must_res"):
                r.append(f"must_res {res}")
            elif str(q.get("rate_key", "")).startswith("plan"):
                r.append("unit_price line")
            else:
                r.append(f"already {res or 'its lowest planned resolution'}")
            if q.get("e_fixed_input"):
                b = q.get("billed_s")
                mn = q.get("e_min_s") or 0
                r.append(f"fixed input: billed by its driving clip ({fmt_num(b)} s"
                         + (", the minimum" if b is not None and b <= mn + 1e-9 else "")
                         + "): a shorter job means a shorter cut")
            elif q.get("unit") == "second":
                if L.get("fixed_duration"):
                    r.append("fixed_duration")
                elif (q.get("billed_s") or 0) <= (q.get("e_min_s") or 0) + 1e-9:
                    r.append(f"already the {fmt_num(q.get('e_min_s'))} s minimum")
                elif not L.get("screen_seconds"):
                    r.append("no screen_seconds to size it down")
                else:
                    r.append("already sized to its screen seconds")
            why = "; ".join(r)
        groups.setdefault(why, []).append(str(q["id"]))
    parts = [f"{', '.join(ids)}: {why}" for why, ids in groups.items()]
    parts.append("1 take everywhere, no opted-in optional lines")
    if has_genjutsu and not has_ip:
        parts.append("The only cheaper plan keeps more cuts as the original (the hero leaves them): mark IP-suspect "
                     "cuts with \"ip_suspect\" / \"ip_suspect_cuts\" to price that, or offer named cuts by hand")
    return ". ".join(parts)


def derive_alt(lines, P, priced, ipm=None):
    """One cheaper alternative, the first rule that applies:
    1. settings: drop opted-in optional lines; 1080p+ -> 720p (not must_res / finalize / unit_price); 1 take;
       generated plates sized to screen seconds x the lower size factor;
    2. else KEEP the IP-suspect cuts as the original (their Genjutsu replace jobs dropped);
    3. else nothing: `why` says per line why.
    Returns (alt_lines, alt_priced, changes, kind, why)."""
    alt_lines, changes = [], []
    for L, q in zip(lines, priced):
        if q.get("optional") and q.get("in_plan"):
            changes.append((L["id"], [("line", "opted-in optional", "dropped")]))
            continue
        A = dict(L)
        ch = []
        if not q.get("free") and q.get("kind") == "video" and not q.get("draft") and q.get("stage") != "reroll":
            res = q.get("resolution")
            rates = q.get("e_rates", {})
            ali = q.get("e_res_aliases", {})
            if (not L.get("must_res") and not q.get("finalize") and res in ("1080p", "2k", "4k", "pro")
                    and ("720p" in rates or ali.get("720p") in rates) and not str(q.get("rate_key", "")).startswith("plan")):
                A = with_res(A, "720p")
                ch.append(("resolution", res, "720p"))
            if q["takes"] > 1:
                A["takes"] = 1
                ch.append(("takes", q["takes"], 1))
            ss = L.get("screen_seconds")
            d = q.get("duration")
            if (ss and d and not q.get("e_fixed_input") and not L.get("fixed_duration") and q.get("unit") == "second"):
                f = float((q.get("e_size_factor") or [1.5])[0])
                d_alt = max(q.get("e_min_s") or 0, math.ceil(float(ss) * f - 1e-9))
                allowed = q.get("e_allowed")
                if allowed:
                    up = [a for a in sorted(allowed) if a >= d_alt]
                    d_alt = up[0] if up else d_alt
                if d_alt < d - 1e-9:
                    A["duration"] = d_alt
                    A.pop("frames", None)
                    ch.append(("duration", d, d_alt))
        elif not q.get("free") and q["takes"] > 1 and q.get("stage") != "reroll":
            A["takes"] = 1
            ch.append(("takes", q["takes"], 1))
        alt_lines.append(A)
        if ch:
            changes.append((L["id"], ch))
    kind = "settings" if changes else None
    why = None
    if not changes and ipm and ipm["by_line"]:
        alt_lines, kind = [], "keep_ip"
        for L, q in zip(lines, priced):
            cuts = ipm["by_line"].get(q["id"])
            if not cuts:
                alt_lines.append(dict(L))
                continue
            n_new = max(0, int(q["count"]) - len(cuts))
            ch = [("count", q["count"], n_new), ("keep", "SWAP", ", ".join(cuts))]
            changes.append((L["id"], ch))
            if n_new > 0:
                A = dict(L)
                A["count"] = n_new
                A["serves_cuts"] = [c for c in (L.get("serves_cuts") or []) if str(c) not in cuts]
                alt_lines.append(A)
    if not changes:
        has_gj = any(q.get("e_genjutsu") for q in priced if not q.get("free"))
        why = why_no_alt(lines, priced, has_gj, bool(ipm and ipm["by_line"]))
    alt_priced = [price_line(A, P) for A in alt_lines]
    return alt_lines, alt_priced, changes, kind, why


def identity_1080p(lines, priced, P):
    """D6: the optional 'all identity jobs at 1080p' delta over planned identity lines at 720p.
    Returns {"delta", "lines", "variant": (lines at 1080p, their pricing)} or None."""
    out = []
    var_lines, var_priced = list(lines), list(priced)
    for i, (L, q) in enumerate(zip(lines, priced)):
        if not q.get("in_plan") or q.get("free") or not L.get("identity") or q.get("kind") != "video":
            continue
        if str(q.get("rate_key", "")).startswith("plan") or q.get("draft") or q.get("finalize"):
            continue
        rates, ali = q.get("e_rates", {}), q.get("e_res_aliases", {})
        res = q.get("resolution")
        if not (res == "720p" or (ali.get("720p") and ali.get(res, res) == ali.get("720p"))):
            continue
        if not ("1080p" in rates or ali.get("1080p") in rates):
            continue
        A = with_res(L, "1080p")
        try:
            qa = price_line(A, P)
        except LedgerError:
            continue
        delta = qa["credits"] - q["credits"]
        if delta > 1e-9:
            qa["in_plan"] = q.get("in_plan")
            var_lines[i], var_priced[i] = A, qa
            out.append({"id": q["id"], "from": q["credits"], "to": qa["credits"], "delta": delta})
    if not out:
        return None
    return {"delta": sum(x["delta"] for x in out), "lines": out, "variant": (var_lines, var_priced)}


def build_quote(W, P, plan):
    lines = plan_lines(plan)
    priced = [price_line(L, P) for L in lines]
    appr = get_approval(plan)
    appr_lines = approved_lines(plan)
    opt_in = set(appr.get("optional_in") or []) if appr else set()
    byid = {q["id"]: q for q in priced}
    for q in priced:
        q["in_plan"] = (not q["optional"]) or q["id"] in opt_in
    planned_L = [L for L, q in zip(lines, priced) if q["in_plan"]]
    planned_q = [q for q in priced if q["in_plan"]]
    optional_q = [q for q in priced if not q["in_plan"]]
    warnings = []
    for L, q in zip(lines, priced):
        for w in q["warnings"]:
            warnings.append(f"{q['id']}: {w}")
        if q["stage"] not in STAGES:
            warnings.append(f"{q['id']}: unknown stage {q['stage']!r} (use {', '.join(STAGES)})")
        if not q.get("free") and q.get("kind") == "video" and not q["serves_cuts"] and not q["draft"]:
            warnings.append(f"{q['id']}: paid video line serves no cut: waste unless it does (routing.md section 5)")
        if (not q.get("free") and q.get("kind") == "video" and q.get("screen_seconds") is None and not q["draft"]
                and not q["optional"]):
            warnings.append(f"{q['id']}: no screen_seconds: utilisation of this line unknown")
        if q["takes"] > 1 and not L.get("take_reason"):
            warnings.append(f"{q['id']}: {q['takes']} takes without take_reason: a second take needs a named reason "
                            f"within the existing finite plan (budget.md section 6)")
        if q["optional"]:
            if q["take_of"] is not None and str(q["take_of"]) not in byid:
                warnings.append(f"{q['id']}: take_of {q['take_of']!r} is not a line of the plan")
            if not q.get("take_reason"):
                warnings.append(f"{q['id']}: excluded line lacks an internal fidelity reason (take_reason)")
        if q.get("kind") == "image" and q["takes"] > 3:
            warnings.append(f"{q['id']}: more than three attempts per still is prohibited")
        if q.get("finalize") and not q["optional"]:
            warnings.append(f"{q['id']}: a draft finalize in the planned total: the draft -> finalize path is an "
                            f"unverified quality path; exclude unless the existing execution scope requires it")
    # every Seedance-type line states generate_audio:false + bitrate_mode:"high" as plan fields (generation.md)
    ab_missing, ab_wrong = [], []
    for L, q in zip(lines, priced):
        chk = [k for k in (q.get("e_check") or []) if k in ("generate_audio", "bitrate_mode")]
        if q.get("free") or not chk:
            continue
        miss = [k for k in chk if k not in L]
        want = q.get("e_set") or {}
        opts = L.get("options") if isinstance(L.get("options"), dict) else {}
        bad = [f"{k} {json.dumps(L[k])}" for k in chk if k in L and L[k] != want.get(k)]
        bad += [f"options.{k} {json.dumps(opts[k])}" for k in chk if k in opts and opts[k] != want.get(k)]
        if miss:
            ab_missing.append(f"{q['id']} ({', '.join(miss)})")
        if bad:
            ab_wrong.append(f"{q['id']} ({', '.join(bad)})")
    if ab_missing:
        warnings.append("Seedance lines without explicit plan fields: " + "; ".join(ab_missing) + ". Add "
                        "\"generate_audio\": false, \"bitrate_mode\": \"high\" to each line (the model default is "
                        "audio ON; `params` sends false / high either way)")
    if ab_wrong:
        warnings.append("Seedance lines with other values: " + "; ".join(ab_wrong) + ". `params` always sends "
                        "generate_audio false + bitrate_mode high (audio refs are re-spoken and audio-on came back "
                        "nsfw): fix the plan line")
    full_take = None
    ipm = ip_suspect_map(plan, lines, priced)
    warnings += ipm["warnings"]
    planned = sum(q["credits"] for q in planned_q)
    optional_cr = sum(q["credits"] for q in optional_q)
    by_stage = {}
    for q in planned_q:
        by_stage[q["stage"]] = by_stage.get(q["stage"], 0.0) + q["credits"]
    stills = sum(q["credits"] for q in planned_q if q.get("kind") == "image")
    has_video = any(q.get("kind") == "video" and not q.get("free") for q in planned_q)
    if has_video and planned > 0 and stills > 0.10 * planned:
        warnings.append(f"stills are {stills / planned:.0%} of the quote (> ~10%): over-iterating on images?")
    reroll_jobs = sum(q["jobs"] for q in planned_q if q["reroll_per_job"] > 0) + (1 if full_take else 0)
    reroll_cr = sum(q["reroll_per_job"] * q["jobs"] for q in planned_q) + (full_take["credits"] if full_take else 0)
    est_unc = sum(q["est_uncertainty"] for q in planned_q)
    worst = planned + reroll_cr + est_unc
    rr_same = [q for q in planned_q if q["reroll_per_job"] > 0 and q.get("e_fixed_input")]
    rr_shot = [q for q in planned_q if q["reroll_per_job"] > 0 and not q.get("e_fixed_input")]
    blocked = if_blocked(lines, priced, P, ipm, planned, worst)
    if blocked:
        warnings += blocked.pop("warnings")
    approved = plan.get("approved_total")
    base_for_guard = plan.get("hard_cap")
    id1080 = None
    id1080_blocked = None
    # utilisation (D24): the 1.5-2.5x target applies to generated plates only; Genjutsu = fixed input
    vids = [q for q in planned_q if q.get("kind") == "video" and not q.get("free") and not q["draft"]]
    sized = [q for q in vids if not q.get("e_fixed_input")]
    fixed = [q for q in vids if q.get("e_fixed_input")]
    gen_s = sum((q["billed_s"] or 0) * q["jobs"] for q in sized)
    line_screen = sum(float(q["screen_seconds"]) for q in sized if q.get("screen_seconds") is not None)
    screen = plan.get("unique_screen_seconds")
    screen = float(screen) if screen is not None else (line_screen if line_screen > 0 else None)
    ratio = (gen_s / screen) if (screen and sized) else None
    if not sized:
        verdict = "no generated plates (Seedance-type lines): no target"
    elif ratio is None:
        verdict = "unknown (add screen_seconds to the plate lines)"
    elif ratio > 3.0:
        verdict = "OVERSIZED: target 1.5-2.5x (budget.md section 4)"
    elif ratio < 1.2:
        verdict = "TIGHT: little room for slow gestures or in-point choice"
    else:
        verdict = "ok (target 1.5-2.5x)"
    per_line_util = []
    for q in sized:
        if q.get("screen_seconds"):
            r = (q["billed_s"] or 0) * q["jobs"] / float(q["screen_seconds"])
            forced = (q["billed_s"] or 0) <= (q.get("e_min_s") or 0) + 1e-9 and q["takes"] == 1
            per_line_util.append({"id": q["id"], "generated_s": (q["billed_s"] or 0) * q["jobs"],
                                  "screen_s": float(q["screen_seconds"]), "ratio": round(r, 2),
                                  "forced_by_min": forced, "fixed_input": False})
    for q in fixed:
        per_line_util.append({"id": q["id"], "generated_s": (q["billed_s"] or 0) * q["jobs"],
                              "screen_s": float(q["screen_seconds"]) if q.get("screen_seconds") is not None else None,
                              "ratio": None, "forced_by_min": True, "fixed_input": True})
    fixed_info = {"lines": [q["id"] for q in fixed],
                  "generated_s": r2(sum((q["billed_s"] or 0) * q["jobs"] for q in fixed)),
                  "screen_s": r2(sum(float(q["screen_seconds"]) for q in fixed if q.get("screen_seconds") is not None)),
                  "verdict": "fixed input (min-billed): sized by the driving clip, no target; never group cuts into "
                             "one Genjutsu input to raise the ratio (untested)"}
    min_billing = []
    for q in priced:
        for n in q["notes"]:
            if "min-duration" in n or "bills as" in n or "priced from frames" in n:
                min_billing.append(f"{q['id']}: {n}")
        for w in q["warnings"]:
            if "REJECTED" in w:
                min_billing.append(f"{q['id']}: {w}")
    alt_lines, alt_priced, changes, alt_kind, alt_why = planned_L, planned_q, [], "disabled", "reference fidelity selects the plan"
    alt_total = sum(q["credits"] for q in alt_priced)
    loses = []
    res_l = [lid for lid, ch in changes if any(c[0] == "resolution" for c in ch)]
    take_l = [lid for lid, ch in changes if any(c[0] == "takes" for c in ch)]
    dur_l = [lid for lid, ch in changes if any(c[0] == "duration" for c in ch)]
    drop_l = [lid for lid, ch in changes if any(c[0] == "line" for c in ch)]
    keep_c = [c for lid, ch in changes for x in ch if x[0] == "keep" for c in str(x[2]).split(", ")]
    if drop_l:
        why_d = {q["id"]: q.get("take_reason") for q in planned_q}
        loses.append("the opted-in optional line(s) " + "; ".join(
            f"{lid}" + (f" ({why_d[lid]})" if why_d.get(lid) else "") for lid in drop_l))
    if res_l:
        loses.append(f"720p instead of 1080p on {', '.join(res_l)}: softer only where an identity-legible shot is "
                     f"upscaled >= 1.3x in the delivery frame (the reference's own pixel size by default); invisible "
                     f"in windows, letterbox or under heavy stylisation (budget.md section 5)")
    if keep_c:
        loses.append(f"the original performers stay in the {len(keep_c)} IP-suspect cut(s) {', '.join(keep_c)}: the "
                     f"hero is missing from them (nothing can come back ip_detected, no 'if blocked' switch)")
    if take_l:
        loses.append(f"1 take on {', '.join(take_l)}: no lottery pick between takes; failed shots are re-rolled "
                     f"as the shortest job instead")
    if dur_l:
        loses.append(f"shorter jobs on {', '.join(dur_l)} (screen seconds x size factor, >= model minimum): less "
                     f"choice of in-points; Seedance gestures run 1.5-2x slower than prompted")
    free_items = [FREE_TEXT]
    for q in priced:
        if q.get("free"):
            free_items.append(f"{q['id']}: {q['purpose'] or q['model']}")
    q_json = {
        "schema": "katana.quote/2",
        "workspace": os.path.abspath(W),
        "plan": p_plan(W),
        "title": plan.get("title") or os.path.basename(os.path.abspath(W)),
        "generated_at": now_iso(),
        "currency": "credits",
        "prices": {"table": P.path, "verified_at": P.base.get("verified_at"), "source": P.base.get("source"),
                   "live_overrides": len(P.over.get("entries", [])),
                   "verified_live": sorted({q["model"] + ("" if q["rate_key"] == "*" else f" {q['rate_key']}")
                                            for q in priced if q.get("verified_live")})},
        "lines": [{k: v for k, v in q.items() if not k.startswith("e_")} for q in priced],
        "totals": {"planned": planned, "by_stage": dict(by_stage),
                   "optional": {"credits": optional_cr, "lines": [q["id"] for q in optional_q]},
                   "planned_with_optional": planned + optional_cr,
                   "identity_1080p": ({"delta": r2(id1080["delta"]), "planned": r2(planned + id1080["delta"]),
                                       "planned_if_blocked": r2(id1080_blocked),
                                       "lines": [{k: (r2(v) if isinstance(v, float) else v) for k, v in x.items()}
                                                 for x in id1080["lines"]]} if id1080 else None),
                   "rerolls": {"jobs": reroll_jobs, "credits": reroll_cr,
                               "short": {"jobs": reroll_jobs - (1 if full_take else 0),
                                         "credits": r2(reroll_cr - (full_take["credits"] if full_take else 0))},
                               "shot": {"jobs": sum(q["jobs"] for q in rr_shot),
                                        "credits": r2(sum(q["reroll_per_job"] * q["jobs"] for q in rr_shot))},
                               "same_job": {"jobs": sum(q["jobs"] for q in rr_same),
                                            "credits": r2(sum(q["reroll_per_job"] * q["jobs"] for q in rr_same))},
                               "full_take": ({"line": full_take["line"], "credits": r2(full_take["credits"])}
                                             if full_take else None)},
                   "if_blocked": (None if not blocked else {
                       "cuts": blocked["cuts"], "n": blocked["n"], "delta": r2(blocked["delta"]),
                       "planned": r2(blocked["planned"]), "worst": r2(blocked["worst"]),
                       "guard_at": r2(blocked["guard_at"]), "still": blocked["still"], "matte": r2(blocked["matte"]),
                       "lines": [{k: (r2(v) if isinstance(v, float) else v) for k, v in x.items()}
                                 for x in blocked["lines"]],
                       "films": [{k: (r2(v) if isinstance(v, float) else v) for k, v in x.items()}
                                 for x in blocked["films"]]}),
                   "est_uncertainty": est_unc, "worst": worst,
                   "approved_total": approved, "guard_at": base_for_guard,
                   "stills": r2(stills)},
        "free": free_items,
        "utilisation": {"scope": "Seedance/generated plates (Genjutsu and other fixed-input lines apart)",
                        "generated_s": r2(gen_s), "screen_s": r2(screen) if screen is not None else None,
                        "ratio": r2(ratio) if ratio is not None else None, "target": [1.5, 2.5],
                        "verdict": verdict, "per_line": per_line_util, "fixed_input": fixed_info},
        "min_billing": min_billing,
        "alt": {"kind": alt_kind, "why_none": alt_why, "total": r2(alt_total), "saving": r2(planned - alt_total),
                "saving_pct": r2(100.0 * (planned - alt_total) / planned) if planned else None,
                "changes": [{"id": lid, "changes": [{"field": c[0], "from": c[1], "to": c[2]} for c in ch]}
                            for lid, ch in changes],
                "loses": loses,
                "lines": [{"id": q["id"], "settings": settings_str(q), "qty": qty_str(q), "credits": r2(q["credits"])}
                          for q in alt_priced]},
        "warnings": [w for w in warnings if not re.search(r"ask|user|opt|mini-quote|refunded|go\b", w, re.I)],
    }
    return q_json, priced


def alt_change_str(chs):
    """'resolution 1080p -> 720p; count 3 -> 1; KEEP the original in c02, c03' for one alternative line."""
    v = lambda x: fmt_num(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else str(x)
    out = []
    for x in chs:
        if x["field"] == "line":
            out.append(f"dropped ({x['from']} line)")
        elif x["field"] == "keep":
            out.append(f"KEEP the original in {x['to']}")
        else:
            out.append(f"{x['field']} {v(x['from'])} -> {v(x['to'])}")
    return "; ".join(out)


def quote_md(q, priced, with_alt=False):
    t = q["totals"]
    out = [f"# Generation estimate: {q['title']}", "", "| Line | Model | Jobs | Credits |", "|---|---|---:|---:|"]
    for item in priced:
        if item.get("in_plan"):
            label = str(item["id"]) + (" (deferred, non-executable)" if item.get("deferred") else "")
            out.append(f"| {label} | {item['model']} | {item['jobs']} | {fmt_cr(item['credits'])} |")
    out += ["", f"Planned: {fmt_cr(t['planned'])} credits.",
            f"Bounded maximum including one retry per required image/video job: {fmt_cr(t['worst'])} credits.",
            f"Registered hard cap: {fmt_cr(t['guard_at']) if t.get('guard_at') is not None else 'not registered'}.",
            "A current exact estimator record is required for every submission. Dispatch one job at a time through guard → submit → add.",
            "Deferred amounts are verified planning upper bounds; they reserve the fixed workflow ceiling and cannot authorize a submission.",
            "Content refusals do not authorize model switches; refunds release exposure only after verified reconciliation."]
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------------------------------------
# params skeleton (D5)
# ----------------------------------------------------------------------------------------------------
GENERIC_TOOL = {"video": "generate_video", "image": "generate_image", "audio": "generate_audio"}


def call_spec(e, q):
    spec = copy.deepcopy((e or {}).get("call") or {})
    if not spec or not spec.get("tool"):
        raise LedgerError(f"{q.get('model')}: no supported call contract; use a verified_request or an authorized supported route")
    spec["_verified"] = True
    return spec


def res_param_value(q, e, spec):
    res = q.get("resolution")
    ali = (e or {}).get("res_aliases") or {}
    if spec.get("res_param") == "mode":
        return ali.get(res, res)
    vals = spec.get("res_values")
    if vals:
        return res if res in vals else spec.get("res_default")
    rates = (e or {}).get("rates") or {}
    keys = {str(k).split("/")[-1] for k in rates}
    if res and (res in keys or ali.get(res) in keys):
        return res
    return None


def ref_role(ref, default):
    s = str(ref).strip().lower()
    if s.startswith("@video") or s.startswith("video"):
        return "video"
    if s.startswith("@audio") or s.startswith("audio"):
        return "audio"
    if s.startswith("start"):
        return "start_image"
    if s.startswith("end"):
        return "end_image"
    return default


def params_skeleton(W, plan, L, q, e):
    vr = L.get("verified_request")
    if vr is not None:
        if not verified_preset(L, vr):
            raise LedgerError("unsupported or unverified preset request contract")
        params = copy.deepcopy(vr["params"])
        for field in ("use_unlim", "use_free_gens"):
            if field in L and (field not in params or params[field] != L[field]):
                raise LedgerError(f"{field} must match the verified preset request, never be silently omitted")
        validate_payment_fields(params, vr["tool"])
        return vr["tool"], params, [], {"_verified": True, "preset": True}
    """(tool, params, notes) for one job of plan line L (priced q, price entry e)."""
    notes = []
    spec = call_spec(e, q)
    tool = spec["tool"]
    clip = None
    if q.get("duration") is not None:
        fpsv = fps_value(L.get("fps"))
        if L.get("frames") is not None and fpsv:
            clip = f"{int(L['frames'])} f @{fmt_num(fpsv, 3)} = {q['duration']:.2f} s"
        else:
            clip = f"{q['duration']:.2f} s"
        if q.get("billed_s") is not None:
            clip += f", bills {fmt_num(q['billed_s'])} s"
    if spec.get("raw") is not None:
        p = copy.deepcopy(spec["raw"])
        for field in ("use_unlim", "use_free_gens"):
            if field in L:
                p[field] = L[field]
        validate_payment_fields(p, tool)
        # Bind only the documented utility input; raw templates are not arbitrary overrides.
        if tool == "remove_background":
            if L.get("media_type") is not None and L["media_type"] != p.get("media_type"):
                raise LedgerError("media_type conflicts with the selected background-removal operation")
            if L.get("media_id") is not None:
                if not isinstance(L["media_id"], str) or not L["media_id"].strip():
                    raise LedgerError("background removal requires a nonempty actual media_id")
                p["media_id"] = L["media_id"]
        return tool, p, notes, spec
    p = {"model": q["model"]}
    mode = L.get("mode")
    res_param = spec.get("res_param", "resolution")
    if mode and res_param != "mode" and not spec.get("no_mode"):
        p["mode"] = mode
    elif mode and res_param == "mode":
        notes.append(f"line mode {mode!r} is a pricing variant of {q['model']}: check its API flag in models_get/models_search")
    if res_param:
        rv = res_param_value(q, e, spec)
        if rv is not None:
            p[res_param] = rv
        elif q.get("resolution"):
            notes.append(f"resolution {q['resolution']} is not a {res_param} value of {q['model']}: model default used")
    if spec.get("quality_param"):
        qual = L.get("quality") or (e or {}).get("default_quality")
        if qual:
            p["quality"] = str(qual).lower()
    if spec.get("duration") and q.get("billed_s") is not None:
        p["duration"] = int(round(q["billed_s"]))
        if q.get("duration") is not None and abs(q["duration"] - q["billed_s"]) > 1e-6:
            notes.append(f"duration {fmt_num(q['duration'], 3)} s -> {p['duration']} (the billed integer seconds)")
    if spec.get("aspect"):
        lock = plan.get("lock") if isinstance(plan.get("lock"), dict) else {}
        p["aspect_ratio"] = (L.get("aspect_ratio") or L.get("aspect") or lock.get("aspect")
                             or "<from the format lock, e.g. 9:16>")
    for k, v in (spec.get("set") or {}).items():
        p[k] = copy.deepcopy(v)
    for field in ("use_unlim", "use_free_gens"):
        if field in L:
            p[field] = L[field]
    validate_payment_fields(p, tool)
    if tool == "generate_audio":
        for k in AUDIO_REQUEST_FIELDS.get(q.get("model"), set()):
            if k in L:
                p[k] = copy.deepcopy(L[k])
    for k, v in (L.get("options") or {}).items():
        allowed = set((e or {}).get("options") or {}) | set(spec.get("set") or {})
        if k not in allowed or k in {"model", "mode", "duration", "resolution", "quality", "count", "prompt", "medias", "aspect_ratio", "draft_job_id"}:
            raise LedgerError(f"options.{k} cannot override or invent a provider field")
        if k in (spec.get("set") or {}) and v != spec["set"][k]:
            raise LedgerError(f"options.{k} conflicts with the verified required setting")
        p[k] = v
    for k in spec.get("check") or []:  # fixed params (Seedance generate_audio:false, bitrate_mode:high) always win
        want = (spec.get("set") or {}).get(k)
        p[k] = copy.deepcopy(want)
        for src, d in (("plan line", L), ("options", L.get("options") if isinstance(L.get("options"), dict) else {})):
            if k in d and d[k] != want:
                notes.append(f"{src} says {k} {json.dumps(d[k])}: sent as {json.dumps(want)} (fix the plan line)")
    if q.get("draft"):
        p["draft"] = True
    if q.get("finalize"):
        p["draft_job_id"] = L.get("draft_job_id") or "<the completed draft job_id (finalize within 7 days)>"
        notes.append("finalize: fill draft_job_id with the completed draft and keep the draft's duration; preflight "
                     "with a dedicated non-submitting estimator first")
    if spec.get("frames_count") and L.get("frames") is not None:
        p["frames_count"] = int(L["frames"])
    if spec.get("count"):
        p["count"] = 1
    if not spec.get("no_prompt") or L.get("prompt"):
        prompt = L.get("prompt")
        if not prompt and L.get("prompt_file"):
            prompt = read_prompt(W, L["prompt_file"])
        if prompt is not None:
            p["prompt"] = prompt
        elif not spec.get("no_prompt"):
            p["prompt"] = "<missing actual prompt>"
    if not spec.get("no_medias"):
        default_role = spec.get("ref_role", "image")
        if isinstance(L.get("medias"), list) and L["medias"]:
            medias = copy.deepcopy(L["medias"])
        elif L.get("refs"):
            medias = [{"role": ref_role(r, default_role), "value": f"<{r}: media_id or job_id>"}
                      for r in L["refs"]]
        else:
            by_mode = spec.get("medias_by_mode") or {}
            tmpl = by_mode[mode] if (mode in by_mode) else spec.get("medias")
            medias = copy.deepcopy(tmpl or [])
        if spec.get("require_video") and not any(m.get("role") == "video" for m in medias):
            medias.append({"role": "video", "value": "<driving clip media_id: {clip}>"})
        for m in medias:
            if isinstance(m.get("value"), str) and "{clip}" in m["value"]:
                m["value"] = m["value"].replace("{clip}", clip or "<padded 24 fps clip>")
        mr = spec.get("max_refs")
        if mr is not None and len(medias) > int(mr):
            notes.append(f"{q['model']} takes at most {mr} ref(s); this line has {len(medias)}")
        if any(m.get("role") == "audio" for m in medias) and str(q["model"]).startswith("seedance"):
            notes.append("audio refs on Seedance: it re-speaks them, and with generate_audio:true it came back nsfw 4/4")
        if medias:
            p["medias"] = medias
    if L.get("declined_preset_id"):
        p["declined_preset_id"] = L["declined_preset_id"]
    return tool, p, notes, spec


def check_params(got, want, spec, P):
    if not isinstance(got, dict):
        return ["params must be an object"]
    g = got.get("params", got)
    if not isinstance(g, dict):
        return ["params must be an object"]
    if g == want:
        return []
    return [f"{key}: actual request differs from the registered request" for key in sorted(set(g) | set(want))
            if g.get(key) != want.get(key) or (key in g) != (key in want)]


# ----------------------------------------------------------------------------------------------------
# ledger
# ----------------------------------------------------------------------------------------------------
def load_ledger(W):
    L = load_json(p_ledger(W), default={"schema": "katana.ledger/1", "currency": "credits", "jobs": []},
                  what="ledger")
    L.setdefault("jobs", [])
    return L


def eff_charge(j):
    if j.get("state") == "refunded" and j.get("refund_evidence"):
        return finite_amount(j.get("charged") or 0, "remaining charge after refund"), "refunded"
    if j.get("state") == "bounced" and j.get("no_charge_evidence"):
        return finite_amount(j.get("charged") or 0, "remaining charge after no-job outcome"), "no job"
    quoted = finite_amount(j.get("quoted") or 0, "quoted")
    charged = j.get("charged")
    failed_without_refund = (any(h.get("state") in FAILED for h in j.get("history", []))
                             and not j.get("refund_evidence"))
    if j.get("state") in FAILED or j.get("state") in ("refunded", "bounced") or failed_without_refund:
        return max(quoted, finite_amount(charged or 0, "charged")), "charged though failed; refund unverified"
    if j.get("state") == "submitted":
        return max(quoted, finite_amount(charged or 0, "charged")), "in flight"
    if charged is not None:
        return finite_amount(charged, "charged"), "recorded"
    return quoted, "assumed = quoted" if j.get("state") == "completed" else "in flight"


def committed(L):
    pending = L.get("pending_submission") or {}
    return sum(eff_charge(j)[0] for j in L["jobs"]) + finite_amount(pending.get("credits") or 0, "reservation")


def find_job(L, jid):
    for j in L["jobs"]:
        if j["job_id"] == jid:
            return j
    return None


def line_policy(plan, q, Lg, jobs_req=None):
    if jobs_req not in (None, 1):
        return "serialized submission requires exactly one job", 0, 0, 0
    al = (approved_lines(plan) or {}).get(q["id"])
    if al is None:
        return "line is not registered; prepare a compatible finite plan within the existing cap", 0, 0, 0
    ch = fp_changes(al, q)
    if ch:
        return f"registered settings changed ({ch}); no submission", 0, 0, 0
    roots = [j for j in Lg["jobs"] if j.get("line") == q["id"] and not j.get("reroll_of")]
    n = len(roots)
    allowed = int(al["jobs"])
    if n >= allowed:
        return "base attempts exhausted, including failed attempts; only a bounded documented retry is eligible", 1, allowed, n
    return None, 1, allowed, n


def reroll_refusal(Lg, target, cost):
    j = find_job(Lg, target)
    if j is None:
        return "retry target is missing from the ledger"
    if j.get("reroll_of") or j.get("unplanned"):
        return "a retry cannot itself be retried or originate from unplanned spend"
    if j.get("state") == "submitted":
        return "target is still running; resolve its actual outcome first"
    states = {j.get("state")} | {h.get("state") for h in j.get("history", [])}
    if states & {"nsfw", "ip_detected"}:
        return "content refusal is terminal for this requested content; no retry or model bypass"
    if any(x.get("reroll_of") == target for x in Lg["jobs"]):
        return "one retry per source job is exhausted, regardless of failures or refunds"
    if cost > finite_amount(j.get("quoted") or 0, "original quote") + 1e-9:
        return "retry exceeds the original job's reserved per-job amount"
    return None


# ----------------------------------------------------------------------------------------------------
# commands
# ----------------------------------------------------------------------------------------------------
def ws(path):
    W = os.path.abspath(path)
    if not os.path.isdir(W):
        raise LedgerError(f"workspace not found: {W}")
    return W


def get_prices(a, W=None):
    return Prices(a.prices or DEFAULT_PRICES, W)


def cmd_quote(a):
    W = ws(a.W)
    P = get_prices(a, W)
    plan = load_plan(W)
    q, priced = build_quote(W, P, plan)
    md = quote_md(q, priced, with_alt=a.alt)
    if not a.no_write:
        save_json(os.path.join(plan_dir(W), "quote.json"), q)
        write_atomic(os.path.join(plan_dir(W), "quote.md"), md)
    sys.stdout.write(md)
    if not a.no_write:
        print(f"\nwrote {os.path.join(plan_dir(W), 'quote.md')} and quote.json")
    return 0


def cmd_approve(a):
    W = ws(a.W)
    if a.total is None or not (a.note or "").strip():
        raise LedgerError("plan registration requires --total and --note recording existing task/account authority")
    with Lock(W):
        P = get_prices(a, W)
        plan = load_plan(W)
        ledger = load_ledger(W)
        if ledger.get("pending_submission"):
            raise LedgerError("unresolved submission reservation; reconcile it before changing the plan")
        chosen = set(split_ids(a.with_optional))
        selected = [L for L in plan_lines(plan) if not L.get("optional") or L["id"] in chosen]
        if chosen - {L["id"] for L in selected}:
            raise LedgerError("unknown selected optional line")
        validate_dependencies(selected)
        previous = approved_lines(plan) or {}
        priced, contracts = [], {}
        for line in selected:
            old_contract = (previous.get(line["id"]) or {}).get("deferred_contract")
            if line.get("deferred"):
                q = price_line(line, P)
                contract = deferred_contract(W, plan, line, q, P)
                if old_contract and any(contract[k] != old_contract[k] for k in contract if k != "planning_quote"):
                    raise LedgerError("registered deferred contract cannot be expanded or replaced")
                contracts[line["id"]] = contract
            else:
                q = submission_price(W, plan, line, P)
                if old_contract:
                    validate_activation(W, line, q, old_contract, ledger)
                    contracts[line["id"]] = old_contract
                elif line.get("depends_on") or line.get("input_bindings"):
                    raise LedgerError("dependent stage must first be registered as deferred with a planning upper bound")
            priced.append(q)
        expected = sum(q["credits"] for q in priced)
        total = finite_amount(a.total, "total")
        if abs(total - expected) > 1e-9:
            raise LedgerError(f"plan subtotal changed: --total must equal {fmt_cr(expected)}; recompute the finite plan")
        cap = a.hard_cap if a.hard_cap is not None else plan.get("hard_cap")
        if cap is None:
            raise LedgerError("plan requires explicit finite --hard-cap or hard_cap; derive it from live-priced required work and bounded retries")
        cap = finite_amount(cap, "hard_cap")
        registered_ceiling = ledger.get("workflow_ceiling")
        if plan.get("workflow_ceiling") is not None and registered_ceiling is None:
            raise LedgerError("workflow_ceiling is created by the first verified staged registration, never hand-authored")
        limits = [cap] + [finite_amount(plan[k], k) for k in ("user_limit", "account_limit", "hard_cap") if plan.get(k) is not None]
        if registered_ceiling is not None:
            limits.append(finite_amount(registered_ceiling, "registered workflow ceiling"))
        cap = min(limits)
        worst = expected + sum(q["reroll_per_job"] * q["jobs"] for q in priced)
        # The first staged registration bounds all stages. Activating a cheaper stage must not
        # shrink that previously fixed envelope to the subtotal of whatever is ready today.
        if registered_ceiling is None:
            cap = min(cap, worst)
        if expected > cap + 1e-9 or committed(ledger) > cap + 1e-9:
            raise LedgerError("required plan or existing commitments exceed the finite cap; select a supported partial plan")
        recs = {}
        for L, q in zip(selected, priced):
            recs[q["id"]] = dict(fingerprint(q), jobs=q["jobs"], per_job=q["per_job"],
                                 config_hash=config_hash(L, W), credits=q["credits"], count=q["count"], takes=q["takes"])
            if q["id"] in contracts:
                recs[q["id"]].update(deferred=bool(L.get("deferred")), deferred_contract=contracts[q["id"]])
        plan["approval"] = {"total": total, "at": now_iso(), "note": a.note, "optional_in": sorted(chosen), "lines": recs}
        plan["approved_total"] = total
        plan["hard_cap"] = cap
        if contracts and registered_ceiling is None:
            registered_ceiling = cap
            ledger["workflow_ceiling"] = cap
            save_json(p_ledger(W), ledger)
        if registered_ceiling is not None:
            plan["workflow_ceiling"] = registered_ceiling
        plan["approved_note"] = a.note
        save_json(p_plan(W), plan)
    print(f"Registered plan {fmt_cr(total)} credits; hard cap {fmt_cr(cap)}; no additional consent implied.")
    return 0


def cmd_params(a):
    W = ws(a.W)
    P = get_prices(a, W)
    plan = load_plan(W)
    L0 = find_line(plan, a.line)
    if L0 is None:
        raise LedgerError(f"line {a.line!r} is not in the plan")
    if L0.get("deferred"):
        raise LedgerError("deferred stage has no executable params; resolve its declared dependency IDs first")
    if a.slot is not None:
        A = reroll_line(L0, P, slot=a.slot)
    else:
        A = variant_line(L0, duration=a.duration, frames=a.frames, fps=a.fps)
    q = price_line(A, P)
    if q.get("free"):
        raise LedgerError(f"line {a.line}: {q['model']} is free (code), no paid call")
    e = P.entry(q["model"], A.get("mode"))
    tool, p, notes, spec = params_skeleton(W, plan, A, q, e)
    body = {"params": p}
    if a.check is not None:
        src = a.check
        try:
            if os.path.exists(src):
                with open(src, "r", encoding="utf-8") as f:
                    got = json.load(f)
            else:
                got = json.loads(src)
        except (OSError, json.JSONDecodeError) as ex:
            raise LedgerError(f"--check: not a JSON file or string: {ex}")
        diffs = check_params(got, p, spec, P)
        if diffs:
            print(f"params: MISMATCH with plan line {a.line} (= unplanned spend: stop; fix the params or re-quote):")
            for d in diffs:
                print(f"  - {d}")
            return 1
        print(f"params: OK, match plan line {a.line} ({q['model']} {q.get('mode') or ''} {q.get('resolution') or ''}"
              f"{', ' + fmt_num(q['billed_s']) + ' s' if q.get('billed_s') else ''}; {fmt_cr(q['per_job'])} cr per job)")
        return 0
    print(json.dumps(body, indent=1, ensure_ascii=False))
    if q.get("unit") == "second":
        bill = f"bills {fmt_num(q['billed_s'])} s x {unit_str(q)}"
    elif q.get("unit") == "chars":
        bill = f"{unit_str(q)}"
    else:
        bill = f"{unit_str(q)} per {q.get('unit') or 'job'}"
    info = [f"tool: {tool} · line {a.line} · {fmt_cr(q['per_job'])} cr per job ({bill}) x {q['jobs']} job(s) = "
            f"{fmt_cr(q['credits'])} for the line"]
    if q["jobs"] > 1 and spec.get("raw") is None:
        per_call = p.get("count", 1) or 1
        info.append(f"submit {q['jobs'] // per_call if per_call > 1 else q['jobs']} item(s) of these params "
                    f"(serialized: guard one job, submit once, add before the next job)")
    info.append("pre-submit check: model, mode, resolution and duration must equal this skeleton (`params W --line "
                f"{a.line} --check '<json>'`); a mismatch is unplanned spend: stop")
    if not spec.get("_verified"):
        info.append(f"no verified call shape for {q['model']} in prices.json: check models_get/models_search before submitting")
    elif spec.get("verified"):
        info.append(f"shape: {spec['verified']}")
    for n in notes + q["notes"] + q["warnings"]:
        info.append(n)
    for n in info:
        print(f"# {n}", file=sys.stderr)
    return 0


def cmd_price_set(a):
    W = ws(a.W)
    obsolete = ("res", "mode", "quality", "per_second", "per_image", "flat")
    if any(getattr(a, key, None) is not None for key in obsolete):
        raise LedgerError("legacy rate/config flags are disabled; set exact fields on the plan line, then record --line ID --credits C")
    if not a.line or a.credits is None:
        raise LedgerError("live pricing requires --line ID --credits C from the exact one-job estimator response")
    if a.source not in ("estimate_video_cost", "estimate_image_cost", "verified_account_quote"):
        raise LedgerError("source must be a non-submitting estimator or a verified account quote")
    if a.currency != "credits":
        raise LedgerError("this ledger records credits; do not convert or mislabel a native-currency API quote")
    if not (a.evidence or "").strip():
        raise LedgerError("live quote requires --evidence identifying the actual estimator response")
    plan = load_plan(W)
    L0 = find_line(plan, a.line)
    if L0 is None:
        raise LedgerError("line does not exist")
    if a.planning:
        if not L0.get("deferred") or not (a.basis or "").strip():
            raise LedgerError("planning price requires a deferred line and --basis explaining its verified upper bound")
        if any(x is not None for x in (a.slot, a.duration, a.frames, a.fps)):
            raise LedgerError("planning estimates bind the declared stage settings; no length overrides")
        dependency_scope(L0, W)
    elif L0.get("deferred"):
        raise LedgerError("deferred inputs cannot receive an exact submission quote; use a verified --planning upper bound")
    A = variant_line(L0, duration=a.duration, frames=a.frames, fps=a.fps)
    if a.slot is not None:
        A = reroll_line(L0, get_prices(a, W), slot=a.slot)
    if a.model and a.model != A.get("model"):
        raise LedgerError("--model does not match the selected line")
    entry = get_prices(a, W).entry(A.get("model"), A.get("mode"))
    kind = (entry or {}).get("kind")
    if (kind == "image" and a.source == "estimate_video_cost") or (kind == "video" and a.source == "estimate_image_cost"):
        raise LedgerError("estimator source does not match the model's media kind")
    credits = finite_amount(a.credits, "live quote")
    rec = {"config_hash": config_hash(A, W), "credits": credits, "at": now_iso(), "source": a.source,
           "currency": "credits", "evidence": a.evidence}
    if a.planning:
        rec["basis"] = a.basis
    collection = "planning_quotes" if a.planning else "exact_quotes"
    with Lock(W):
        data = load_json(p_override(W), default={"entries": []})
        data[collection] = [x for x in data.get(collection, []) if x.get("config_hash") != rec["config_hash"]] + [rec]
        save_json(p_override(W), data)
    print(f"Recorded {'planning upper bound (non-executable)' if a.planning else 'exact one-job estimate'} for {a.line}: {fmt_cr(credits)} credits.")
    return 0


def cmd_guard(a):
    W = ws(a.W)
    if a.next is not None or not a.line:
        raise LedgerError("only registered plan lines can submit; unplanned guard and batch dispatch are disabled")
    if a.jobs not in (None, 1):
        raise LedgerError("serialized dispatch only: guard one job, submit once, add its id before the next guard")
    with Lock(W):
        P = get_prices(a, W)
        plan = load_plan(W)
        Lg = load_ledger(W)
        if Lg.get("pending_submission"):
            raise LedgerError("unresolved submission reservation; recover its job id or verify no submission before continuing")
        if plan.get("approved_total") is None or plan.get("hard_cap") is None:
            raise LedgerError("finite plan is not registered; complete free preparation and register existing task/account authority")
        L0 = find_line(plan, a.line)
        if L0 is None:
            raise LedgerError("line is not in the registered plan")
        A = (reroll_line(L0, P, slot=a.slot, duration=a.duration, frames=a.frames, fps=a.fps)
             if a.reroll_of else variant_line(L0, duration=a.duration, frames=a.frames, fps=a.fps))
        q = submission_price(W, plan, A, P)
        if q.get("free"):
            raise LedgerError("free work has no paid submission to reserve")
        rec = (approved_lines(plan) or {}).get(a.line)
        if rec is None:
            raise LedgerError("line is not registered; no paid submission")
        if rec.get("deferred"):
            raise LedgerError("dependent stage is not activated; register its resolved inputs and fresh exact quote")
        if q.get("kind") == "image":
            if rec.get("count") is None or rec.get("takes") is None:
                raise LedgerError("legacy registration lacks image attempt counts; re-register within the existing cap")
            if int(L0.get("count", 1)) != rec["count"] or int(L0.get("takes", 1)) != rec["takes"]:
                raise LedgerError("registered image count/takes changed; retry cannot expand its attempt ceiling")
        if a.reroll_of:
            if not fail_item(a.reason):
                raise LedgerError("retry requires a documented fail-list reason")
            target = find_job(Lg, a.reroll_of)
            if not target or target.get("line") != a.line:
                raise LedgerError("retry must name a source job from this exact plan line")
            original = {k: v for k, v in rec.items() if k != "billed_s"}
            changed = fp_changes(original, q)
            if changed or target.get("model") != q.get("model"):
                raise LedgerError("retry changes the registered operation/settings; prepare a separate supported plan within the existing cap")
            refusal = reroll_refusal(Lg, a.reroll_of, q["per_job"])
        else:
            refusal = line_policy(plan, q, Lg, 1)[0]
            rec = (approved_lines(plan) or {}).get(a.line, {})
            if rec.get("config_hash") != config_hash(A, W):
                refusal = "request changed since plan registration; no submission"
        if refusal:
            raise LedgerError(refusal)
        if q.get("kind") == "image":
            attempts = sum(j.get("line") == a.line for j in Lg["jobs"])
            if attempts >= 3 * rec["count"]:
                raise LedgerError("three image attempts per item exhausted, including failed attempts and retries")
        cap = hard_cap(plan)
        after = committed(Lg) + q["per_job"]
        if after > cap + 1e-9:
            raise LedgerError(f"hard cap reached: committed + next {fmt_cr(after)} > {fmt_cr(cap)}; continue free work or a truthful partial")
        Lg["pending_submission"] = {"line": a.line, "credits": q["per_job"], "config_hash": config_hash(A, W),
                                    "reroll_of": a.reroll_of, "reason": a.reason, "at": now_iso()}
        save_json(p_ledger(W), Lg)
    print(f"Reserved one job: {a.line}, {fmt_cr(q['per_job'])} credits; committed after submit {fmt_cr(after)} / hard cap {fmt_cr(cap)}. Submit once, then add its id.")
    return 0


def cmd_add(a):
    W = ws(a.W)
    ids = split_ids(a.job)
    if len(ids) != 1:
        raise LedgerError("serialized dispatch records exactly one job id; do not submit batches")
    with Lock(W):
        plan = load_plan(W)
        Lg = load_ledger(W)
        if find_job(Lg, ids[0]):
            raise LedgerError("job id already recorded")
        pending = Lg.get("pending_submission")
        line = find_line(plan, a.line)
        P = get_prices(a, W)
        A = (reroll_line(line, P, slot=a.slot, duration=a.duration, frames=a.frames, fps=a.fps)
             if a.reroll_of else variant_line(line, duration=a.duration, frames=a.frames, fps=a.fps)) if line else None
        if not a.unplanned:
            if not pending or pending["line"] != a.line or pending.get("reroll_of") != a.reroll_of:
                raise LedgerError("job does not match the outstanding reservation; reconcile actual submitted work")
            if not A or pending["config_hash"] != config_hash(A, W):
                raise LedgerError("submitted settings differ from the reserved request")
            quoted = pending["credits"]
            if a.quoted is not None and abs(a.quoted - quoted) > 1e-9:
                raise LedgerError("--quoted cannot replace the reserved exact price")
            del Lg["pending_submission"]
        else:
            if not (a.reason or "").strip() or a.quoted is None:
                raise LedgerError("unplanned reconciliation requires a reason and actual quoted exposure")
            quoted = finite_amount(a.quoted, "unplanned exposure")
        q = price_line(A, P) if A else {}
        t = now_iso()
        j = {"job_id": ids[0], "line": a.line, "planned": not a.unplanned, "unplanned": bool(a.unplanned),
             "reroll_of": a.reroll_of, "reason": a.reason, "stage": a.stage or ("reroll" if a.reroll_of else (line or {}).get("stage", "other")),
             "model": a.model or q.get("model"), "mode": q.get("mode"), "resolution": a.res or q.get("resolution"),
             "duration": q.get("duration"), "frames": (A or {}).get("frames"), "billed_s": q.get("billed_s"),
             "kind": q.get("kind"), "quoted": quoted, "charged": None, "state": "submitted",
             "submitted_at": t, "updated_at": t, "history": [{"at": t, "state": "submitted"}],
             "screen_seconds": None, "used": None, "note": a.note}
        Lg["jobs"].append(j)
        save_json(p_ledger(W), Lg)
    print(f"Recorded {ids[0]} on {a.line}; exposure {fmt_cr(quoted)} credits. Persist the workspace.")
    return 0


def cmd_release(a):
    W = ws(a.W)
    if not (a.evidence or "").strip():
        raise LedgerError("release requires provider evidence that no job and no charge were created")
    with Lock(W):
        L = load_ledger(W)
        pending = L.pop("pending_submission", None)
        if pending is None:
            raise LedgerError("no outstanding reservation")
        L.setdefault("reservation_history", []).append(dict(pending, release_evidence=a.evidence, released_at=now_iso()))
        save_json(p_ledger(W), L)
    print("Reconciled unused reservation from verified provider evidence.")
    return 0


def cmd_status(a):
    W = ws(a.W)
    ids = split_ids(a.job)
    if not ids:
        raise LedgerError("no job id given")
    if a.state in ("refunded", "bounced") and not (a.evidence or "").strip():
        raise LedgerError("refund/no-charge state requires transaction or provider --evidence")
    if a.charged is not None:
        finite_amount(a.charged, "charged")
    with Lock(W):
        L = load_ledger(W)
        missing = [i for i in ids if find_job(L, i) is None]
        if missing:
            raise LedgerError(f"unknown job id(s) {', '.join(missing)}: `ledger.py add` them first")
        t = now_iso()
        for i in ids:
            j = find_job(L, i)
            prev = j.get("charged")
            j["state"] = a.state
            if a.state == "refunded":
                j["refund_evidence"] = a.evidence
                basis = j.get("charged_before_refund")
                if basis is None:
                    basis = prev if prev is not None else j.get("quoted", 0)
                j["charged_before_refund"] = finite_amount(basis, "pre-refund debit")
            elif a.state == "bounced":
                j["no_charge_evidence"] = a.evidence
            h = {"at": t, "state": a.state}
            if a.charged is not None:
                j["charged"] = finite_amount(a.charged, "charged")
                h["charged"] = j["charged"]
            elif a.state == "refunded":
                j["refund_evidence"] = a.evidence
                j["charged"] = 0.0
                h["charged"] = 0.0
            elif a.state == "bounced":
                j["no_charge_evidence"] = a.evidence
                j["charged"] = 0.0
                h["charged"] = 0.0
            if a.note:
                j["note"] = ((j.get("note") or "") + " | " + a.note).strip(" |")
                h["note"] = a.note
            j["updated_at"] = t
            j.setdefault("history", []).append(h)
        save_json(p_ledger(W), L)
    for i in ids:
        j = find_job(L, i)
        c, basis = eff_charge(j)
        print(f"{i}: {j['state']}  counted {fmt_cr(c)} ({basis})")
    print(f"wrote {p_ledger(W)}")
    return 0


def cmd_use(a):
    W = ws(a.W)
    ids = split_ids(a.job)
    modes = sum(1 for x in (a.screen_seconds is not None, a.ref_only, a.unused) if x)
    if modes != 1:
        raise LedgerError("give exactly one of --screen-seconds S, --ref-only, --unused")
    with Lock(W):
        L = load_ledger(W)
        missing = [i for i in ids if find_job(L, i) is None]
        if missing:
            raise LedgerError(f"unknown job id(s) {', '.join(missing)}: `ledger.py add` them first")
        for i in ids:
            j = find_job(L, i)
            if a.unused:
                j["used"], j["screen_seconds"] = False, 0.0
            elif a.ref_only:
                j["used"], j["screen_seconds"] = True, 0.0
                j["used_as"] = "reference"
            else:
                s = float(a.screen_seconds)
                if s < 0:
                    raise LedgerError("--screen-seconds must be >= 0")
                j["screen_seconds"] = round(s, 3)
                j["used"] = s > 0
                d = j.get("duration")
                if d and s > float(d) + 0.05 and j.get("kind") == "video":
                    print(f"WARNING: {i}: {s} s on screen > {d} s generated (frames reused or slowed? fine if so)",
                          file=sys.stderr)
            j["use_reason"] = a.reason
            j["updated_at"] = now_iso()
        save_json(p_ledger(W), L)
    for i in ids:
        j = find_job(L, i)
        print(f"{i}: used={j['used']} screen={fmt_num(j['screen_seconds'])} s"
              + (f" ({a.reason})" if a.reason else ""))
    print(f"wrote {p_ledger(W)}")
    return 0


def job_tag(j):
    if j.get("reroll_of"):
        return f" (re-roll of {j['reroll_of']})"
    if j.get("unplanned"):
        return " (unplanned)"
    return ""


def cmd_jobs(a):
    W = ws(a.W)
    L = load_ledger(W)
    if not L["jobs"]:
        print("ledger is empty")
        return 0
    print("| Job | Line | Stage | Model | State | Quoted | Charged | Screen s |")
    print("|---|---|---|---|---|---|---|---|")
    for j in L["jobs"]:
        print(f"| {j['job_id']} | {j.get('line')}{job_tag(j)} | {j.get('stage')} | {j.get('model')} "
              f"{j.get('resolution') or ''} | {j.get('state')} | {fmt_cr(j.get('quoted'))} | {fmt_cr(j.get('charged'))} | "
              f"{fmt_num(j.get('screen_seconds')) if j.get('screen_seconds') is not None else '-'} |")
    print(f"committed (charged + in flight, refunds excluded): {fmt_cr(committed(L))}")
    return 0


def build_summary(W, plan, L, final_seconds=None):
    jobs = L["jobs"]
    rows, waste = [], []
    tot = {"quoted": 0.0, "charged": 0.0, "used": 0.0, "assumed": 0.0, "unconfirmed": 0.0, "in_flight": 0.0,
           "refunded": 0.0, "auto_refunded": 0.0, "gen_s": 0.0, "screen_s": 0.0}
    stages = {}
    appr_l = approved_lines(plan) if plan else None
    unplanned, rerolls = [], []
    for j in jobs:
        c, basis = eff_charge(j)
        q = float(j.get("quoted") or 0)
        st = j.get("stage") or "other"
        S = stages.setdefault(st, {"jobs": 0, "quoted": 0.0, "charged": 0.0, "used": 0.0, "gen_s": 0.0,
                                   "screen_s": 0.0})
        S["jobs"] += 1
        S["quoted"] += q
        S["charged"] += c
        tot["quoted"] += q
        tot["charged"] += c
        if basis == "assumed = quoted":
            tot["assumed"] += c
        elif basis.startswith("charged though failed"):
            tot["unconfirmed"] += c
        elif basis == "in flight":
            tot["in_flight"] += c
        elif basis == "auto-refunded":
            tot["auto_refunded"] += q
        if j.get("state") == "refunded":
            tot["refunded"] += max(0.0, float(j.get("charged_before_refund") or j.get("quoted") or 0) - c)
        gen = 0.0
        if j.get("kind") == "video" and j.get("state") == "completed":
            gen = float(j.get("duration") or j.get("billed_s") or 0)
        S["gen_s"] += gen
        tot["gen_s"] += gen
        scr = float(j.get("screen_seconds") or 0)
        S["screen_s"] += scr
        tot["screen_s"] += scr
        if j.get("used"):
            S["used"] += c
            tot["used"] += c
        st_ = j.get("state")
        if st_ == "completed" and j.get("used") is False:
            waste.append((j, c, "unused" + (f": {j.get('use_reason')}" if j.get("use_reason") else "")))
        elif st_ == "completed" and j.get("used") is None:
            waste.append((j, c, "not marked used/unused yet (`ledger.py use`)"))
        elif st_ in FAILED and c > 0:
            waste.append((j, c, f"{st_} but charged ({basis}); check transactions for the refund"))
        elif st_ == "submitted":
            waste.append((j, c, "still in flight: jobs_wait until terminal before cataloguing"))
        if j.get("reroll_of"):
            rerolls.append((j, c))
        elif (j.get("unplanned") or j.get("planned") is False
              or (appr_l is not None and j.get("line") not in appr_l)):
            unplanned.append((j, c))
        rows.append((j, c, basis))
    if final_seconds is None:
        final_seconds = plan.get("final_seconds") if plan else None
        if final_seconds is None and plan and isinstance(plan.get("lock"), dict):
            lk = plan["lock"]
            try:
                fps = lk.get("fps")
                if isinstance(fps, str) and "/" in fps:
                    n, d = fps.split("/", 1)
                    fps = float(n) / float(d)
                final_seconds = float(lk["frames"]) / float(fps)
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                final_seconds = None
    approved = plan.get("approved_total") if plan else None
    waste_cr = sum(c for (j, c, why) in waste if not why.startswith("still in flight") and not why.startswith("not marked"))
    unmarked_cr = sum(c for (j, c, why) in waste if why.startswith("not marked"))
    gnext = L.get("guard_next") or []
    by_model = {}
    for j, c, basis in rows:
        m = by_model.setdefault(str(j.get("model") or "?"), {"jobs": 0, "counted": 0.0})
        m["jobs"] += 1
        m["counted"] += c
    t_from = min((j.get("submitted_at") for j in jobs if j.get("submitted_at")), default=None)
    t_to = max((j.get("updated_at") or j.get("submitted_at") for j in jobs
                if j.get("updated_at") or j.get("submitted_at")), default=None)
    s = {
        "schema": "katana.ledger_summary/2", "generated_at": now_iso(), "workspace": os.path.abspath(W),
        "approved_total": approved,
        "guard_at": plan.get("hard_cap") if plan else None,
        "totals": {k: r2(v) for k, v in tot.items()},
        "waste_credits": r2(waste_cr), "unmarked_credits": r2(unmarked_cr),
        "unplanned": {"credits": r2(sum(c for _, c in unplanned)),
                      "jobs": [{"job_id": j["job_id"], "line": j.get("line"), "state": j.get("state"),
                                "credits": r2(c), "reason": j.get("reason")} for j, c in unplanned],
                      "guard_next": gnext,
                      "guard_next_ok_credits": r2(sum(float(g.get("credits") or 0) for g in gnext
                                                      if g.get("result") == "ok"))},
        "rerolls": {"credits": r2(sum(c for _, c in rerolls)),
                    "jobs": [{"job_id": j["job_id"], "line": j.get("line"), "reroll_of": j.get("reroll_of"),
                              "state": j.get("state"), "credits": r2(c), "reason": j.get("reason")}
                             for j, c in rerolls]},
        "reconcile": {"from": t_from, "to": t_to, "jobs": len(jobs),
                      "by_model": {k: {"jobs": v["jobs"], "counted": r2(v["counted"])} for k, v in by_model.items()},
                      "hint": RECONCILE_HINT},
        "final_seconds": final_seconds,
        "credits_per_final_second": r2(tot["charged"] / float(final_seconds)) if final_seconds else None,
        "utilisation": round(tot["screen_s"] / tot["gen_s"], 4) if tot["gen_s"] else None,
        "per_stage": {k: {kk: (r2(vv) if isinstance(vv, float) else vv) for kk, vv in v.items()}
                      for k, v in stages.items()},
        "waste": [{"job_id": j["job_id"], "line": j.get("line"), "state": j.get("state"), "credits": r2(c),
                   "why": why} for (j, c, why) in waste],
        "jobs": [{"job_id": j["job_id"], "line": j.get("line"), "stage": j.get("stage"), "model": j.get("model"),
                  "resolution": j.get("resolution"), "duration": j.get("duration"), "state": j.get("state"),
                  "quoted": j.get("quoted"), "charged": j.get("charged"), "counted": r2(c), "basis": basis,
                  "screen_seconds": j.get("screen_seconds"), "used": j.get("used"),
                  "use_reason": j.get("use_reason"), "reroll_of": j.get("reroll_of"),
                  "unplanned": bool(j.get("unplanned")), "reason": j.get("reason")} for (j, c, basis) in rows],
    }
    return s


def summary_md(s):
    t = s["totals"]
    out = ["# Spend report", ""]
    out.append("| Job | Line | Stage | Model · settings | Quoted | Charged | State | Gen s | Screen s | Use |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for j in s["jobs"]:
        ch = fmt_cr(j["charged"]) if j["charged"] is not None else f"{fmt_cr(j['counted'])}*"
        use = ("used" if j["used"] else ("unused" if j["used"] is False else "-"))
        if j.get("use_reason"):
            use += f" ({j['use_reason']})"
        gen = fmt_num(j["duration"]) if j.get("duration") and j["state"] == "completed" else "-"
        scr = fmt_num(j["screen_seconds"]) if j.get("screen_seconds") is not None else "-"
        out.append(f"| {j['job_id']} | {j['line']}{job_tag(j)} | {j['stage']} | {j['model'] or '?'} "
                   f"{j['resolution'] or ''} | {fmt_cr(j['quoted'])} | {ch} | {j['state']} | {gen} | {scr} | {use} |")
    out.append(f"| **Total** | | | | **{fmt_cr(t['quoted'])}** | **{fmt_cr(t['charged'])}** | | "
               f"{fmt_num(t['gen_s'], 1)} | {fmt_num(t['screen_s'], 2)} | used {fmt_cr(t['used'])} |")
    out.append("")
    notes = []
    if t["assumed"]:
        notes.append(f"{fmt_cr(t['assumed'])} assumed = quoted (no charge recorded; reconcile with `transactions`)")
    if t["unconfirmed"]:
        notes.append(f"{fmt_cr(t['unconfirmed'])} charged on failed jobs (refund not seen yet)")
    if t["in_flight"]:
        notes.append(f"{fmt_cr(t['in_flight'])} still in flight")
    if t["refunded"]:
        notes.append(f"{fmt_cr(t['refunded'])} refunded")
    if notes:
        out.append("* " + "; ".join(notes) + ".")
    out.append(f"Quoted {fmt_cr(t['quoted'])} · charged {fmt_cr(t['charged'])} · used {fmt_cr(t['used'])} · "
               f"waste {fmt_cr(s['waste_credits'])}"
               + (f" · not yet marked {fmt_cr(s['unmarked_credits'])}" if s["unmarked_credits"] else ""))
    if s["approved_total"] is not None:
        out.append(f"Approved {fmt_cr(s['approved_total'])} (guard {fmt_cr(s['guard_at'])}): spent "
                   f"{float(t['charged']) / float(s['approved_total']):.0%} of registered subtotal." if s['approved_total'] else "Registered zero-credit plan.")
    up = s["unplanned"]
    if up["jobs"]:
        out.append(f"Unplanned spend: {fmt_cr(up['credits'])} in {len(up['jobs'])} job(s) outside the approval "
                   f"(lines not approved, or beyond a line's count): "
                   + "; ".join(f"{x['job_id']} ({x['line']}, {x['state']}, {fmt_cr(x['credits'])}"
                               f"{': ' + str(x['reason']) if x.get('reason') else ''})" for x in up["jobs"]) + ".")
    else:
        out.append("Unplanned spend: none recorded.")
    if up["guard_next"]:
        out.append(f"guard --next checks ({len(up['guard_next'])}; {fmt_cr(up['guard_next_ok_credits'])} passed): "
                   + "; ".join(f"{fmt_cr(g.get('credits'))} {g.get('result')}: {g.get('reason')}"
                               for g in up["guard_next"]) + ".")
    rr = s["rerolls"]
    if rr["jobs"]:
        out.append(f"Re-rolls: {fmt_cr(rr['credits'])} in {len(rr['jobs'])} job(s): "
                   + "; ".join(f"{x['job_id']} of {x['reroll_of']} ({x.get('reason') or '?'}, {fmt_cr(x['credits'])})"
                               for x in rr["jobs"]) + ".")
    if s["utilisation"] is not None:
        out.append(f"Utilisation: {fmt_num(t['screen_s'], 2)} s on screen of {fmt_num(t['gen_s'], 1)} s generated "
                   f"= {s['utilisation']:.1%}.")
    if s["credits_per_final_second"] is not None:
        out.append(f"Credits per final second: {fmt_cr(s['credits_per_final_second'])} "
                   f"({fmt_cr(t['charged'])} / {fmt_num(s['final_seconds'], 2)} s).")
    rc = s.get("reconcile") or {}
    if rc.get("jobs"):
        mods = ", ".join(f"{k} x{v['jobs']} ({fmt_cr(v['counted'])})" for k, v in rc["by_model"].items())
        out.append(f"Reconcile with `transactions` ({rc.get('from') or '?'} .. {rc.get('to') or '?'} UTC; {mods}): "
                   + rc["hint"])
    out.append("")
    out.append("| Stage | Jobs | Quoted | Charged | Used | Gen s | Screen s |")
    out.append("|---|---|---|---|---|---|---|")
    for k, v in s["per_stage"].items():
        out.append(f"| {k} | {v['jobs']} | {fmt_cr(v['quoted'])} | {fmt_cr(v['charged'])} | {fmt_cr(v['used'])} | "
                   f"{fmt_num(v['gen_s'], 1)} | {fmt_num(v['screen_s'], 2)} |")
    out.append("")
    if s["waste"]:
        out.append("Waste / open items:")
        for w in s["waste"]:
            out.append(f"- {w['job_id']} ({w['line']}, {w['state']}): {fmt_cr(w['credits'])} - {w['why']}")
    else:
        out.append("Waste: none recorded.")
    return "\n".join(out) + "\n"


def cmd_summary(a):
    W = ws(a.W)
    plan = load_plan(W, required=False)
    L = load_ledger(W)
    s = build_summary(W, plan, L, a.final_seconds)
    md = summary_md(s)
    save_json(os.path.join(plan_dir(W), "ledger_summary.json"), s)
    write_atomic(os.path.join(plan_dir(W), "ledger_summary.md"), md)
    sys.stdout.write(md)
    print(f"\nwrote {os.path.join(plan_dir(W), 'ledger_summary.md')} and ledger_summary.json")
    return 0


def cmd_prices(a):
    W = os.path.abspath(a.W) if a.W else None
    P = get_prices(a, W)
    models = [P.canon(a.model)] if a.model else sorted((P.base.get("models") or {}).keys())
    print(f"# prices: {P.path} (verified {P.base.get('verified_at')})"
          + (f" + {len(P.over.get('entries', []))} live override(s)" if P.over.get("entries") else ""))
    for m in models:
        e = P.entry(m)
        if e is None:
            print(f"{m}: unknown")
            continue
        rates = ", ".join(f"{k}={fmt_num(v, 4)}{'*' if k in e['_live'] else ''}" for k, v in e.get("rates", {}).items())
        extra = []
        if e.get("unit") == "second":
            extra.append(f"min {fmt_num(e.get('min_s', 0))} s")
            if e.get("allowed_s"):
                extra.append(f"allowed {e['allowed_s']}")
            extra.append(f"seconds={e.get('seconds', 'ceil')}")
        if e.get("est"):
            extra.append("est.")
        print(f"{m} [{e.get('kind')}/{e.get('unit')}] {rates}  {' '.join(extra)}")
        for mode in (e.get("modes") or {}):
            em = P.entry(m, mode)
            print(f"   mode {mode}: " + ", ".join(f"{k}={fmt_num(v, 4)}" for k, v in em.get("rates", {}).items()))
    return 0


def build_parser():
    ap = argparse.ArgumentParser(
        prog="ledger.py", description=__doc__, epilog=PLAN_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prices", help=f"default price table (default {DEFAULT_PRICES})")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, help_, **kw):
        p = sub.add_parser(name, help=help_, description=help_, epilog=kw.pop("epilog", None),
                           formatter_class=argparse.RawDescriptionHelpFormatter)
        p.add_argument("--prices", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
        return p

    def length_args(p, slot=True):
        if slot:
            p.add_argument("--slot", type=float,
                           help="re-roll of one failed shot: its slot seconds -> a single-shot job of "
                                "max(min, ceil(2 x slot)) s at the line's resolution (generated plates only)")
        p.add_argument("--duration", type=float, help="the probed / changed duration (re-prices the job)")
        p.add_argument("--frames", type=int, help="the PROBED frame count of the driving clip (re-prices the job)")
        p.add_argument("--fps", help="fps of --frames (default: the line's fps, else 24)")

    p = add("quote", "price plan/gen_plan.json -> plan/quote.md + quote.json (table, planned total, optional lines, "
                     "bounded maximum, free work and utilisation; legacy --alt is accepted without menus)", epilog=PLAN_HELP)
    p.add_argument("W")
    p.add_argument("--alt", action="store_true", help="legacy compatibility flag; no alternative menu is generated")
    p.add_argument("--no-write", action="store_true", help="print only")
    p.set_defaults(fn=cmd_quote)

    p = add("approve", "register a finite plan under existing task/account authority; does not create permission")
    p.add_argument("W")
    p.add_argument("--total", type=float, help="exact selected plan subtotal")
    p.add_argument("--with-optional", action="append", metavar="ID",
                   help="internally selected existing line within scope (repeat or comma-separate)")
    p.add_argument("--note", help="existing task/account authority and scope; never fabricate consent")
    p.add_argument("--hard-cap", type=float, help="finite maximum derived from live-priced work and bounded retries")
    p.set_defaults(fn=cmd_approve)

    p = add("params", "print the exact generate_* params skeleton of a plan line (model, mode, resolution, "
                      "duration, aspect, Seedance generate_audio:false + bitrate_mode:high, count, medias); "
                      "--check compares params you are about to send (exit 1 = mismatch = unplanned spend)")
    p.add_argument("W")
    p.add_argument("--line", required=True, help="plan line id")
    length_args(p)
    p.add_argument("--check", help="params JSON (string or file) to compare with the line before submitting")
    p.set_defaults(fn=cmd_params)

    p = add("price-set", "record a live dedicated estimator price in plan/prices_override.json (quote and guard use it)")
    p.add_argument("W")
    p.add_argument("--model")
    p.add_argument("--res", help="disabled legacy flag; set resolution on the plan line")
    p.add_argument("--mode", help="disabled legacy flag; set mode on the plan line")
    p.add_argument("--quality", help="disabled legacy flag; set quality on the plan line")
    p.add_argument("--per-second", type=float, help="disabled legacy rate flag; use exact --credits")
    p.add_argument("--per-image", type=float, help="disabled legacy rate flag; use exact --credits")
    p.add_argument("--flat", type=float, help="disabled legacy rate flag; use exact --credits")
    p.add_argument("--credits", type=float, help="the dedicated estimator result for one job (with --duration for video)")
    p.add_argument("--duration", type=float, help="duration (s) of the preflighted job")
    p.add_argument("--source", default="estimate_video_cost")
    p.add_argument("--line")
    p.add_argument("--evidence")
    p.add_argument("--currency", default="credits")
    p.add_argument("--frames", type=int)
    p.add_argument("--fps")
    p.add_argument("--slot", type=float)
    p.add_argument("--planning", action="store_true", help="record only a non-executable upper bound for a declared deferred stage")
    p.add_argument("--basis", help="actual estimator/account evidence explaining why the bound covers the deferred settings")
    p.set_defaults(fn=cmd_price_set)

    p = add("guard", "reserve one exact live-priced job within the finite hard cap; no batch dispatch")
    p.add_argument("W")
    p.add_argument("--line", help="the plan line for exactly one submission")
    p.add_argument("--jobs", type=int, help="legacy compatibility; only 1 is allowed")
    p.add_argument("--reroll-of", metavar="JOB", help="with --line: re-roll this completed job (once per job)")
    length_args(p)
    p.add_argument("--next", type=float, help="disabled legacy flag; unplanned submissions cannot be authorized")
    p.add_argument("--reason", help="with --reroll-of: the documented fail-list item")
    p.set_defaults(fn=cmd_guard)

    p = add("add", "record exactly one returned job id against its outstanding reservation; no batches")
    p.add_argument("W")
    p.add_argument("--line", required=True, help="plan line id")
    p.add_argument("--job", action="append", required=True, help="exactly one returned job id; repetitions and comma-separated batches are rejected")
    p.add_argument("--quoted", type=float, help="optional consistency check against reserved credits; required for unplanned reconciliation")
    p.add_argument("--reroll-of", metavar="JOB", help="this job re-rolls that completed job (needs --reason)")
    p.add_argument("--unplanned", action="store_true",
                   help="reconcile work already submitted outside the plan; requires reason and exposure, never authorizes new work")
    p.add_argument("--reason", help="re-roll fail-list item, or why the unplanned job was submitted")
    p.add_argument("--stage", choices=STAGES, help="override (unplanned lines)")
    p.add_argument("--model")
    p.add_argument("--res")
    length_args(p)
    p.add_argument("--note")
    p.set_defaults(fn=cmd_add)

    p = add("status", "update job state (after jobs_wait / transactions) and the charged credits")
    p.add_argument("W")
    p.add_argument("--job", action="append", required=True)
    p.add_argument("--state", required=True, choices=STATES)
    p.add_argument("--charged", type=float, help="actual remaining net debit per job; on refunded, omit only for a verified full refund")
    p.add_argument("--note")
    p.add_argument("--evidence", help="actual refund/no-charge transaction or provider evidence")
    p.set_defaults(fn=cmd_status)

    p = add("use", "record what a job contributes to the final (after the EDL exists)")
    p.add_argument("W")
    p.add_argument("--job", action="append", required=True)
    p.add_argument("--screen-seconds", type=float, help="seconds of this job on screen in the final")
    p.add_argument("--ref-only", action="store_true", help="used as a reference (identity anchor, start frame)")
    p.add_argument("--unused", action="store_true", help="not used in the final")
    p.add_argument("--reason")
    p.set_defaults(fn=cmd_use)

    p = add("jobs", "print the job table")
    p.add_argument("W")
    p.set_defaults(fn=cmd_jobs)

    p = add("summary", "spend report -> plan/ledger_summary.md + .json (incl. unplanned spend and re-rolls)")
    p.add_argument("W")
    p.add_argument("--final-seconds", type=float, help="final film length (default: plan final_seconds)")
    p.set_defaults(fn=cmd_summary)

    p = add("prices", "print the effective price table (defaults + live overrides of W)")
    p.add_argument("--W", help="workspace (to include its live overrides)")
    p.add_argument("--model")
    p.set_defaults(fn=cmd_prices)
    p = add("release", "reconcile a reserved submission only after provider evidence of no job/no charge")
    p.add_argument("W")
    p.add_argument("--evidence", required=True)
    p.set_defaults(fn=cmd_release)
    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if not hasattr(a, "prices"):
        a.prices = None
    try:
        return a.fn(a)
    except (LedgerError, ValueError, TypeError) as e:
        print(f"ledger: error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
