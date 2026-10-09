#!/usr/bin/env python3
"""Measure every per-block narration take against its exact manifest line.

The agent used to hand-build one ``speech_metrics.sh`` command per take. That made the
retry set depend on prose interpretation and, in one failed run, measured the final
takes with ``--text 'final take'`` instead of the words actually sent to TTS. This
wrapper owns the manifest-to-file mapping and returns one machine-readable retry set.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

TARGET_MIN = 7.8
HARD_MIN = 7.2
HARD_MAX = 9.5
ADAPTIVE_WORD_MIN = 17
DEFAULT_WORD_MAX = 23


def _parse_blocks(value: str) -> set[int]:
    if not value.strip():
        return set()
    try:
        blocks = {int(item.strip()) for item in value.split(",") if item.strip()}
    except ValueError as error:
        raise argparse.ArgumentTypeError("block lists contain integers only") from error
    if any(block < 1 for block in blocks):
        raise argparse.ArgumentTypeError("block numbers start at 1")
    return blocks


def _default_metrics_script() -> Path:
    here = Path(__file__).resolve()
    # Both the MCP resource tree and HF_WORKFLOWS install these as siblings.
    candidate = here.parents[2] / "narration" / "scripts" / "speech_metrics.sh"
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(
        "could not locate narration/scripts/speech_metrics.sh; restore the narrator "
        "bundle or pass --metrics-script"
    )


def _recommended_words(words: int, speech: float, window: float = 10.0) -> int:
    scale = window / 10.0
    if speech <= 0:
        return words
    if speech > HARD_MAX * scale:
        target = round(words * 9.0 * scale / speech)
        return max(max(1, math.floor(ADAPTIVE_WORD_MIN * scale)), min(words - 1, target))
    if speech < HARD_MIN * scale:
        target = math.ceil(words * 8.5 * scale / speech)
        return min(math.ceil(DEFAULT_WORD_MAX * scale), max(words + 1, target))
    return words


def _classify(
    metric: dict[str, Any], *, accept_soft: bool, window: float = 10.0
) -> tuple[str, bool]:
    speech = float(metric["speech"])
    pauses = int(metric.get("pauses", 0))
    rate = metric.get("rate")
    scale = window / 10.0
    if not math.isfinite(speech) or speech < 0 or pauses < 0:
        raise ValueError("speech metrics must be finite and non-negative")
    if pauses:
        return "pausey", False
    if speech > HARD_MAX * scale:
        return "too_long", False
    if speech < HARD_MIN * scale:
        return "too_short", False
    if rate == "RUSHED":
        return "rushed", False
    if rate == "SLOW":
        return "slow", False
    if rate != "ok":
        raise ValueError("speech metrics must include a known delivery rate")
    if speech < TARGET_MIN * scale:
        return ("soft_pass" if accept_soft else "soft_retry"), accept_soft
    return "pass", True


def measure(
    script: dict[str, Any],
    voice_dir: Path,
    metrics_script: Path,
    *,
    accept_soft_blocks: set[int] | None = None,
    duration_seconds: float | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    accept_soft_blocks = accept_soft_blocks or set()
    blocks = script.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("script must contain a non-empty blocks array")
    if duration_seconds is None:
        duration_seconds = len(blocks) * 10.0
    if (
        not math.isfinite(duration_seconds)
        or duration_seconds <= 0
        or math.ceil(duration_seconds / 10) != len(blocks)
    ):
        raise ValueError("duration must be positive and match the manifest block count")
    if any(block < 1 or block > len(blocks) for block in accept_soft_blocks):
        raise ValueError("accepted soft blocks must exist in the manifest")

    takes: list[dict[str, Any]] = []
    retry_blocks: list[int] = []
    overlong_blocks: list[int] = []
    for index, block in enumerate(blocks, start=1):
        if not isinstance(block, dict) or not isinstance(block.get("vo_line"), str):
            raise ValueError(f"block {index} has no vo_line")
        if block.get("n", index) != index:
            raise ValueError(f"block {index} has an incorrect n")
        # Dialogue uses the clip's full-length native audio, never a TTS window.
        if script.get("talking_characters") and block.get("block_kind") == "dialogue":
            takes.append({"block": index, "state": "native_dialogue"})
            continue
        window = min(10.0, duration_seconds - (index - 1) * 10)
        voice = voice_dir / f"voice{index:02d}.wav"
        if not voice.is_file():
            takes.append({"block": index, "state": "missing", "file": str(voice)})
            retry_blocks.append(index)
            continue

        completed = runner(
            [
                "bash",
                str(metrics_script),
                str(voice),
                "--text",
                block["vo_line"],
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()[:500]
            raise RuntimeError(f"speech metrics failed for block {index}: {detail}")
        metric = json.loads(completed.stdout)
        state, accepted = _classify(
            metric, accept_soft=index in accept_soft_blocks, window=window
        )
        take = {"block": index, "state": state, **metric}
        speech = float(metric["speech"])
        overlong = speech > HARD_MAX * window / 10.0
        if overlong or state == "too_short":
            take["recommended_words"] = _recommended_words(
                int(metric["words"]), speech, window
            )
        requirements = []
        if int(metric.get("pauses", 0)):
            requirements.append("Rewrite as one flowing clause without internal sentence stops, commas, dashes or performed pauses.")
        if overlong:
            if take["recommended_words"] >= int(metric["words"]):
                requirements.append("At the adaptive word floor: keep the minimum word count but use shorter, simpler spoken words; do not repeat the failed line.")
            else:
                requirements.append("Shorten the exact spoken line to recommended_words while preserving its meaning.")
        if metric.get("rate") == "SLOW":
            requirements.append("Use direct everyday wording without dramatic punctuation; retain the locked voice and base delivery phrase, then remeasure rate.")
        if metric.get("rate") == "RUSHED":
            requirements.append("Rewrite for an unhurried, natural read and remeasure rate; never stretch the audio.")
        if requirements:
            take["rewrite_requirements"] = requirements
        takes.append(take)
        if not accepted:
            retry_blocks.append(index)
        if overlong:
            overlong_blocks.append(index)

    result: dict[str, Any] = {
        "valid": not retry_blocks,
        "retry_blocks": retry_blocks,
        "overlong_blocks": overlong_blocks,
        "takes": takes,
    }
    if overlong_blocks:
        joined = ",".join(str(block) for block in overlong_blocks)
        result["revalidate_with"] = f"--duration-retry-blocks {joined}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--voice-dir", required=True, type=Path)
    parser.add_argument("--metrics-script", type=Path, default=None)
    parser.add_argument(
        "--duration-seconds", type=float, default=None,
        help="Requested motion duration; scales the window for a short final block",
    )
    parser.add_argument(
        "--accept-soft-blocks",
        type=_parse_blocks,
        default=set(),
        help="Comma-separated blocks already retried once in the 7.2-7.8s soft band",
    )
    arguments = parser.parse_args()
    try:
        script = json.loads(arguments.script.read_text(encoding="utf-8"))
        result = measure(
            script,
            arguments.voice_dir,
            arguments.metrics_script or _default_metrics_script(),
            accept_soft_blocks=arguments.accept_soft_blocks,
            duration_seconds=arguments.duration_seconds,
        )
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)]}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
