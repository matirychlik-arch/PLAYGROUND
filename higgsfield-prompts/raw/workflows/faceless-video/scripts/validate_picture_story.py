#!/usr/bin/env python3
"""Validate deterministic scene-based script gates before TTS spend."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


WORD_PATTERN = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*", re.UNICODE)
MINIMUM_BEATS_PER_MINUTE = 25
MAXIMUM_BEATS_PER_MINUTE = 35
MINIMUM_WORDS_PER_BEAT = 4
MAXIMUM_WORDS_PER_BEAT = 8
MAXIMUM_NARRATION_WORDS_PER_SECOND = 2.5


def _word_count(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def _phrase_from(beat: dict[str, Any]) -> tuple[str, str]:
    for field in ("phrase", "vo_line"):
        value = beat.get(field)
        if isinstance(value, str) and value.strip():
            return field, value.strip()
    return "phrase", ""


def _validate(script: Any, duration_seconds: float) -> dict[str, Any]:
    errors: list[str] = []
    invalid_beats: list[dict[str, Any]] = []
    beats = script.get("beats") if isinstance(script, dict) else None
    if isinstance(script, dict):
        genre = script.get("genre")
        if genre not in {"education", "history", "kids", "storytelling"}:
            errors.append(
                "genre must be education, history, kids, or storytelling"
            )
        if script.get("animation_mode") != "scene_based":
            errors.append("animation_mode must be scene_based")
    if not isinstance(beats, list) or not beats:
        return {
            "valid": False,
            "errors": ["script must contain a non-empty beats array"],
            "invalid_beats": [],
        }

    minimum_beats = max(
        1,
        math.ceil(duration_seconds * MINIMUM_BEATS_PER_MINUTE / 60),
    )
    maximum_beats = max(
        minimum_beats,
        math.floor(duration_seconds * MAXIMUM_BEATS_PER_MINUTE / 60),
    )
    if not minimum_beats <= len(beats) <= maximum_beats:
        errors.append(
            f"beat count {len(beats)} is outside {minimum_beats}-{maximum_beats} "
            f"for {duration_seconds:g}s "
            f"({MINIMUM_BEATS_PER_MINUTE}-{MAXIMUM_BEATS_PER_MINUTE} beats/minute)"
        )

    total_word_count = 0
    for index, raw_beat in enumerate(beats, start=1):
        if not isinstance(raw_beat, dict):
            invalid_beats.append(
                {
                    "n": index,
                    "error": "beat must be an object",
                    "word_count": 0,
                }
            )
            continue
        phrase_field, phrase = _phrase_from(raw_beat)
        word_count = _word_count(phrase)
        total_word_count += word_count
        declared_number = raw_beat.get("n")
        beat_number = declared_number if isinstance(declared_number, int) else index
        beat_errors: list[str] = []
        if declared_number != index:
            beat_errors.append(f"n must be {index}")
        if not phrase:
            beat_errors.append("phrase is required")
        elif not MINIMUM_WORDS_PER_BEAT <= word_count <= MAXIMUM_WORDS_PER_BEAT:
            beat_errors.append(
                f"phrase must contain {MINIMUM_WORDS_PER_BEAT}-"
                f"{MAXIMUM_WORDS_PER_BEAT} words"
            )
        image_mode = raw_beat.get("image_mode")
        if image_mode not in {"new", "variation"}:
            beat_errors.append("image_mode must be new or variation")
        elif image_mode == "variation":
            if index == 1:
                beat_errors.append("the first beat cannot be a variation")
            if raw_beat.get("variation_of") != index - 1:
                beat_errors.append(
                    f"variation_of must be the immediately previous beat ({index - 1})"
                )
            change_only = raw_beat.get("change_only")
            if not isinstance(change_only, str) or not change_only.strip():
                beat_errors.append("variation requires a non-empty change_only")
        if beat_errors:
            invalid_beats.append(
                {
                    "n": beat_number,
                    "field": phrase_field,
                    "phrase": phrase,
                    "word_count": word_count,
                    "errors": beat_errors,
                }
            )

    maximum_word_count = max(
        1,
        math.floor(duration_seconds * MAXIMUM_NARRATION_WORDS_PER_SECOND),
    )
    if total_word_count > maximum_word_count:
        errors.append(
            f"total word count {total_word_count} exceeds the "
            f"{maximum_word_count}-word pre-TTS budget for {duration_seconds:g}s"
        )

    return {
        "valid": not errors and not invalid_beats,
        "beat_count": len(beats),
        "total_word_count": total_word_count,
        "maximum_word_count": maximum_word_count,
        "expected_beat_count": {
            "minimum": minimum_beats,
            "maximum": maximum_beats,
        },
        "errors": errors,
        "invalid_beats": invalid_beats,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--duration-seconds", required=True, type=float)
    arguments = parser.parse_args()
    if arguments.duration_seconds <= 0:
        parser.error("--duration-seconds must be positive")

    try:
        script = json.loads(arguments.script.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(
            json.dumps(
                {"valid": False, "errors": [str(error)], "invalid_beats": []},
                ensure_ascii=False,
            )
        )
        return 1

    result = _validate(script, arguments.duration_seconds)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
