"""Plan ordered Seedance clips without a sub-four-second tail. No external IO."""
import argparse
import json
import sys
from pathlib import Path


def plan_duration(duration_seconds):
    if isinstance(duration_seconds, bool) or not isinstance(duration_seconds, int):
        raise ValueError("duration_seconds must be a whole number of seconds")
    if duration_seconds < 4:
        raise ValueError("duration_seconds must be at least 4")
    count = (duration_seconds + 14) // 15
    durations = [15] * (count - 1) + [duration_seconds - 15 * (count - 1)]
    if durations[-1] < 4:
        borrowed = 4 - durations[-1]
        durations[-2] -= borrowed
        durations[-1] = 4
    return {
        "duration_seconds": duration_seconds,
        "clip_count": count,
        "clip_durations": durations,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    try:
        brief = json.loads(args.input.read_text())
        if not isinstance(brief, dict):
            raise ValueError("input must be a JSON object")
        result = plan_duration(brief.get("duration_seconds"))
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
