from __future__ import annotations

import importlib.util
import io
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1]
SUBTITLE_SCRIPTS_DIRECTORY = SCRIPTS_DIRECTORY.parents[1] / "video-montage" / "scripts"


def _load_module(name: str, filename: str, directory: Path = SCRIPTS_DIRECTORY):
    spec = importlib.util.spec_from_file_location(
        name,
        directory / filename,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


audio_to_captions = _load_module("audio_to_captions", "audio_to_captions.py", SUBTITLE_SCRIPTS_DIRECTORY)
subtitle_audio_to_captions = _load_module(
    "faceless_subtitle_audio_to_captions",
    "audio_to_captions.py",
    SUBTITLE_SCRIPTS_DIRECTORY,
)
bind_scene_frame_results = _load_module(
    "bind_scene_frame_results",
    "bind_scene_frame_results.py",
)
build_scene_timeline = _load_module(
    "build_scene_timeline",
    "build_scene_timeline.py",
)
materialize_scene_frames = _load_module(
    "materialize_scene_frames",
    "materialize_scene_frames.py",
)
validate_motion_script = _load_module(
    "validate_motion_script",
    "validate_motion_script.py",
)
measure_narration_takes = _load_module(
    "measure_narration_takes",
    "measure_narration_takes.py",
)
validate_song_prompt = _load_module(
    "validate_song_prompt",
    "validate_song_prompt.py",
)
validate_picture_story = _load_module(
    "validate_picture_story",
    "validate_picture_story.py",
)
validate_result_manifests = _load_module(
    "validate_result_manifests",
    "validate_result_manifests.py",
)
# Digit-free filler: the validator rejects digits in a narration line (numbers must be
# written as words), so the helper cannot number its own tokens.
_ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def _words(count: int, offset: int = 0) -> str:
    """Distinct filler words. `offset` shifts the whole run.

    Every block needs its OWN run: the validator now rejects a verbatim phrase shared by
    two lines, because that is exactly the shape of the padding a run invented on
    2026-07-31 (one identical closing sentence appended to 36 of 60 blocks). Without the
    offset the helper would hand every block the same opening words.
    """

    def token(index: int) -> str:
        first = _ALPHABET[index % 26]
        second = _ALPHABET[(index // 26) % 26]
        third = _ALPHABET[(index // 676) % 26]
        return f"word{first}{second}{third}"

    return " ".join(token(offset + index) for index in range(count))


_SHOT_SIZES = ["WIDE", "MEDIUM", "CU", "DETAIL", "ECU"]


def _shots(count: int, offset: int = 0) -> list[str]:
    """Shots that satisfy the framing-size gate: every neighbour a different size."""
    return [
        f"{_SHOT_SIZES[position % len(_SHOT_SIZES)]}: {_words(3, offset + position * 10)}"
        for position in range(count)
    ]


def _cold_open(total_words: int = 30, offset: int = 0) -> str:
    """A line whose first sentence is short enough for the cold-open gate."""
    return f"{_words(6, offset)}. {_words(total_words - 6, offset + 300)}"


class AssembleSlidesScriptTest(unittest.TestCase):
    def test_canonicalizes_relative_frames_before_writing_ffconcat(self) -> None:
        script = (SCRIPTS_DIRECTORY / "assemble_slides.sh").read_text()

        canonicalize = 'im="$(realpath "$im")"'
        ffconcat_write = 'printf "file \'%s\'\\nduration %s\\n" "$im" "$du"'
        self.assertIn(canonicalize, script)
        self.assertIn(ffconcat_write, script)
        self.assertLess(script.index(canonicalize), script.index(ffconcat_write))


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires ffmpeg/ffprobe")
class AssembleFinalAudioTest(unittest.TestCase):
    """Exercise actual mixing/encoding for the canonical faceless assembler."""

    ASSEMBLERS = {
        "canonical": SCRIPTS_DIRECTORY / "assemble_final.sh",
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.directory = Path(cls.temporary.name)
        cls.run_command([
            "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
            "testsrc2=size=96x64:rate=10:duration=2", "-f", "lavfi", "-i",
            "sine=frequency=1379:sample_rate=48000:duration=2",
            "-c:v", "libx264", "-c:a", "aac", "clip.mp4",
        ])
        cls.run_command([
            "ffmpeg", "-y", "-v", "error", "-i", "clip.mp4",
            "-an", "-c:v", "copy", "silent.mp4",
        ])
        for filename, duration in [("voice.wav", 1), ("song.wav", 2), ("long-song.wav", 4)]:
            cls.run_command([
                "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                f"sine=frequency=440:sample_rate=48000:duration={duration}",
                "-af", "volume=4", filename,
            ])

    @classmethod
    def run_command(cls, command: list[str]) -> subprocess.CompletedProcess:
        result = subprocess.run(command, cwd=cls.directory, capture_output=True, timeout=60)
        if result.returncode:
            raise AssertionError(result.stderr.decode(errors="replace"))
        return result

    def assemble(
        self,
        assembler_name: str,
        name: str,
        clip: str,
        volume: str | None,
        *,
        song: bool = False,
        blocks: int = 1,
    ):
        out = f"{assembler_name}-{name}.mp4"
        args = [
            "bash", str(self.ASSEMBLERS[assembler_name]),
            "--out", out, "--blocks", str(blocks), "--clip-seconds", "2",
        ]
        if volume is not None:
            args.extend(["--sfx-vol", volume])
        if song:
            args.extend(["--song", "song.wav" if blocks == 1 else "long-song.wav", *([clip] * blocks)])
        else:
            args.extend([clip, "voice.wav"] * blocks)
        self.run_command(args)
        sidecar = json.loads((self.directory / f"{out}.assembly.json").read_text())
        self.assertAlmostEqual(sidecar["actual_s"], blocks * 2, delta=0.15)
        pcm = self.run_command([
            "ffmpeg", "-v", "error", "-xerror", "-i", out, "-vn",
            "-ar", "16000", "-ac", "1", "-f", "s16le", "-",
        ]).stdout
        self.assertGreater(len(pcm), blocks * 60000)
        if song:
            # Container duration can hide a truncated audio stream. Check decoded
            # duration and audible song through the tail, not silence padded later.
            bytes_per_second = 16000 * 2
            self.assertAlmostEqual(len(pcm) / bytes_per_second, blocks * 2, delta=0.075)
            tail = pcm[int((blocks * 2 - 0.1) * bytes_per_second):blocks * 2 * bytes_per_second]
            samples = [sample for (sample,) in struct.iter_unpack("<h", tail)]
            self.assertTrue(samples, "Song must reach the final video window")
            mean_square = sum(sample * sample for sample in samples) / len(samples)
            self.assertGreater(mean_square, 500 ** 2, "Song tail must be audible")
        self.assertNotEqual(set(pcm), {0}, "Narration/song must remain audible")
        return pcm, sidecar

    def test_zero_and_clamped_negative_exclude_clip_audio(self) -> None:
        for assembler_name in self.ASSEMBLERS:
            with self.subTest(assembler=assembler_name):
                reference, _ = self.assemble(assembler_name, "voice-only", "silent.mp4", None)
                for index, value in enumerate(["0", "0.000", "-1"]):
                    with self.subTest(assembler=assembler_name, sfx_vol=value):
                        actual, sidecar = self.assemble(
                            assembler_name, f"mute-{index}", "clip.mp4", value
                        )
                        self.assertEqual(sidecar["sfx_vol"], 0)
                        self.assertEqual(actual, reference, "Mute must match the voice-only PCM")

    def test_default_preserves_nonzero_clip_audio(self) -> None:
        for assembler_name in self.ASSEMBLERS:
            with self.subTest(assembler=assembler_name):
                default, _ = self.assemble(assembler_name, "default", "clip.mp4", None)
                explicit, _ = self.assemble(assembler_name, "explicit", "clip.mp4", "0.12")
                voice_only, _ = self.assemble(
                    assembler_name, "nonzero-reference", "silent.mp4", None
                )
                self.assertEqual(default, explicit)
                self.assertNotEqual(default, voice_only, "Default SFX must not be removed")

    def test_song_mode_still_honors_zero(self) -> None:
        for assembler_name in self.ASSEMBLERS:
            with self.subTest(assembler=assembler_name):
                muted, sidecar = self.assemble(
                    assembler_name, "song-muted", "clip.mp4", "0", song=True
                )
                reference, _ = self.assemble(
                    assembler_name, "song-only", "silent.mp4", "0", song=True
                )
                self.assertTrue(sidecar["song"])
                self.assertEqual(sidecar["sfx_vol"], 0)
                self.assertEqual(muted, reference)

    def test_song_spans_multiple_blocks_with_clip_audio(self) -> None:
        for assembler_name in self.ASSEMBLERS:
            with self.subTest(assembler=assembler_name):
                _, sidecar = self.assemble(
                    assembler_name, "song-multiblock", "clip.mp4", "0.12", song=True, blocks=2
                )
                self.assertEqual(sidecar["blocks"], 2)
                self.assertEqual(sidecar["sfx_vol"], 0.12)

    def test_retried_soft_band_flows_through_finish_without_relaxing_other_blocks(self):
        self.run_command([
            "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
            "testsrc2=size=96x64:rate=10:duration=10", "-c:v", "libx264", "block10.mp4",
        ])
        for name, duration in [("normal", 8.2), ("soft", 7.58), ("short", 7.1)]:
            self.run_command([
                "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                f"sine=frequency=440:sample_rate=48000:duration={duration}",
                "-af", "tremolo=f=5:d=1,volume=4", f"{name}.wav",
            ])
        assembler = str(SCRIPTS_DIRECTORY / "assemble_final.sh")
        for soft, voice, message in [(None, "soft", "7.800"), ("1", "soft", "7.800"), ("2", "short", "7.200"), ("3", "soft", "outside the manifest")]:
            args = ["bash", assembler, "--blocks", "2", "--allow-mismatch",
                    "--out", "refused.mp4"]
            if soft:
                args += ["--accept-soft-blocks", soft]
            args += ["block10.mp4", "normal.wav", "block10.mp4", f"{voice}.wav"]
            result = subprocess.run(args, cwd=self.directory, capture_output=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(message, result.stderr.decode())
            self.assertFalse((self.directory / "refused.mp4").exists())
        (self.directory / "clips.txt").write_text((str(self.directory / "block10.mp4") + "\n") * 2)
        (self.directory / "voices.txt").write_text(
            str(self.directory / "normal.wav") + "\n" + str(self.directory / "soft.wav") + "\n")
        self.run_command([
            "bash", str(SCRIPTS_DIRECTORY / "finish_video.sh"), "--blocks", "2",
            "--clips-file", "clips.txt", "--voices-file", "voices.txt", "--no-verify-audio",
            "--accept-soft-blocks", "2", "--out", "accepted.mp4",
        ])
        sidecar = json.loads((self.directory / "accepted.mp4.assembly.json").read_text())
        self.assertAlmostEqual(sidecar["actual_s"], 20, delta=0.15)
        self.assertFalse(sidecar["per_block"][0]["soft_band_accepted"])
        self.assertEqual(sidecar["per_block"][0]["speech_min_s"], 7.8)
        self.assertTrue(sidecar["per_block"][1]["soft_band_accepted"])
        self.assertEqual(sidecar["per_block"][1]["speech_min_s"], 7.2)
        self.assertAlmostEqual(sidecar["per_block"][1]["speech_s"], 7.58, delta=0.08)


def _motion_script(*, last_word_count: int = 22):
    through_line_asset = "prop_gauge"
    return {
        "topic": "Why city trees cool streets",
        "genre": "education",
        "animation_mode": "fully_animated",
        "style": "Editorial Motion Graphics",
        "through_line": {
            "name": "heat gauge",
            "asset": through_line_asset,
            "progression": "the needle falls in every block",
            "resolution": "the needle reaches the cool zone",
        },
        "arc": {
            "hook": 1,
            "build": [],
            "turn": 2,
            "payoff": 3,
        },
        "blocks": [
            {
                "n": 1,
                "arc_role": "hook",
                "vo_line": _cold_open(22, 0),
                "location": "hot street",
                "through_line_state": "needle pinned hot",
                "shots": _shots(5, 0),
                "assets_used": ["hot street", through_line_asset],
            },
            {
                "n": 2,
                "arc_role": "turn",
                "vo_line": _words(22, 100),
                "location": "tree canopy",
                "through_line_state": "needle moving down",
                "shots": _shots(5, 400),
                "assets_used": ["tree canopy", through_line_asset],
            },
            {
                "n": 3,
                "arc_role": "payoff",
                "vo_line": _words(last_word_count, 200),
                "location": "cool boulevard",
                "through_line_state": "needle resolves in cool zone",
                "shots": _shots(5, 500),
                "assets_used": ["cool boulevard", through_line_asset],
            },
        ],
        "sources": ["https://www.epa.gov/heatislands"],
    }


class NarrationMeasurementsTest(unittest.TestCase):
    def measure(self, metrics, *, script=None, missing=(), **kwargs):
        script = script or _motion_script()
        calls = []
        values = iter(metrics)

        def runner(command, **_kwargs):
            calls.append(command)
            return subprocess.CompletedProcess(
                command, 0, stdout=json.dumps(next(values)), stderr=""
            )

        with tempfile.TemporaryDirectory() as directory:
            voice_dir = Path(directory)
            for index in range(1, len(script["blocks"]) + 1):
                if index not in missing:
                    (voice_dir / f"voice{index:02d}.wav").touch()
            result = measure_narration_takes.measure(
                script, voice_dir,
                measure_narration_takes._default_metrics_script(),
                runner=runner, **kwargs,
            )
        return result, calls

    @staticmethod
    def metric(speech=8.5, *, words=22, rate="ok", pauses=0):
        return {"speech": speech, "words": words, "rate": rate, "pauses": pauses}

    def test_measures_exact_manifest_text_and_returns_complete_retry_set(self):
        script = _motion_script()
        result, calls = self.measure([
            self.metric(10.61, rate="SLOW"),
            self.metric(),
            self.metric(6.5),
        ], script=script)
        self.assertFalse(result["valid"])
        self.assertEqual(result["retry_blocks"], [1, 3])
        self.assertEqual(result["overlong_blocks"], [1])
        self.assertEqual(result["revalidate_with"], "--duration-retry-blocks 1")
        self.assertEqual(result["takes"][0]["recommended_words"], 19)
        self.assertEqual(result["takes"][2]["recommended_words"], 23)
        self.assertEqual([call[4] for call in calls], [b["vo_line"] for b in script["blocks"]])
        self.assertTrue(all(call[0] == "bash" for call in calls))
        self.assertTrue(all("narration/scripts/speech_metrics.sh" in call[1] for call in calls))

    def test_soft_band_requires_one_retry_and_never_waives_hard_or_rate_gates(self):
        metrics = [self.metric(7.5, words=20), self.metric(), self.metric()]
        first, _ = self.measure(metrics)
        retried, _ = self.measure(metrics, accept_soft_blocks={1})
        self.assertEqual(first["retry_blocks"], [1])
        self.assertEqual(first["takes"][0]["state"], "soft_retry")
        self.assertTrue(retried["valid"])
        self.assertEqual(retried["takes"][0]["state"], "soft_pass")
        for metric in [self.metric(7.1), self.metric(9.6), self.metric(rate="RUSHED"), self.metric(pauses=1)]:
            with self.subTest(metric=metric):
                result, _ = self.measure([metric, self.metric(), self.metric()], accept_soft_blocks={1})
                self.assertEqual(result["retry_blocks"], [1])

    def test_recorded_pause_and_word_floor_failures_require_concrete_rewrites(self):
        result, _ = self.measure([
            self.metric(9.299, words=19, pauses=1, rate="SLOW"),
            self.metric(9.81, words=17, rate="SLOW"),
            self.metric(10.022, words=21, pauses=1),
        ])
        self.assertFalse(result["valid"])
        self.assertEqual(result["retry_blocks"], [1, 2, 3])
        # Pauses do not hide an independently measured overlong take.
        self.assertEqual(result["overlong_blocks"], [2, 3])
        self.assertIn("one flowing clause", result["takes"][0]["rewrite_requirements"][0])
        self.assertEqual(result["takes"][1]["recommended_words"], 17)
        self.assertIn("word floor", result["takes"][1]["rewrite_requirements"][0])
        self.assertLess(result["takes"][2]["recommended_words"], 21)

    def test_native_dialogue_is_not_measured_as_narration(self):
        script = _motion_script()
        script.update(genre="kids", talking_characters=True)
        for index, block in enumerate(script["blocks"], 1):
            block["block_kind"] = "dialogue" if index % 2 == 0 else "narration"
        result, calls = self.measure([self.metric(), self.metric()], script=script, missing={2})
        self.assertTrue(result["valid"])
        self.assertEqual(result["takes"][1], {"block": 2, "state": "native_dialogue"})
        self.assertEqual([Path(call[2]).name for call in calls], ["voice01.wav", "voice03.wav"])

    def test_short_last_block_scales_duration_and_retry_word_budget(self):
        result, _ = self.measure([self.metric(), self.metric(), self.metric(4.3, words=11)], duration_seconds=25)
        self.assertTrue(result["valid"])
        overlong, _ = self.measure([self.metric(), self.metric(), self.metric(5.5, words=11)], duration_seconds=25)
        self.assertEqual(overlong["overlong_blocks"], [3])
        self.assertEqual(overlong["takes"][2]["recommended_words"], 9)

    def test_missing_take_is_in_retry_set_without_a_metric_call(self):
        result, calls = self.measure([self.metric(), self.metric()], missing={2})
        self.assertEqual(result["retry_blocks"], [2])
        self.assertEqual(result["takes"][1]["state"], "missing")
        self.assertEqual(len(calls), 2)

    def test_cli_uses_an_explicit_metrics_script_and_preserves_authored_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = _motion_script()
            # User text is an argv value, never shell source.
            script["blocks"][0]["vo_line"] = "Someone's exact line; $(false) is not shell code"
            (root / "script.json").write_text(json.dumps(script))
            for index in range(1, 4):
                (root / f"voice{index:02d}.wav").touch()
            metrics = root / "metrics.sh"
            metrics.write_text("#!/bin/bash\nprintf '%s' \"$3\" > \"$1.text\"\n" + "printf '%s\\n' " +
                               "'{\"speech\":8.5,\"words\":22,\"rate\":\"ok\",\"pauses\":0}'\n")
            result = subprocess.run([
                sys.executable, str(SCRIPTS_DIRECTORY / "measure_narration_takes.py"),
                "--script", str(root / "script.json"), "--voice-dir", str(root),
                "--metrics-script", str(metrics), "--duration-seconds", "30",
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["valid"])
            self.assertEqual((root / "voice01.wav.text").read_text(), script["blocks"][0]["vo_line"])


class MotionScriptValidatorTest(unittest.TestCase):
    def test_allows_only_measured_duration_retry_blocks_below_initial_floor(self):
        script = _motion_script()
        script["blocks"][0]["vo_line"] = _cold_open(18, 0)
        script["blocks"][1]["vo_line"] = _words(18, 100)
        result = validate_motion_script._validate(script, 30, duration_retry_blocks={1})
        self.assertFalse(result["valid"])
        self.assertNotIn(1, [block["n"] for block in result["invalid_blocks"]])
        block_two = next(block for block in result["invalid_blocks"] if block["n"] == 2)
        self.assertIn("vo_line must contain 20-23 words", block_two["errors"])
        accepted = validate_motion_script._validate(script, 30, duration_retry_blocks={1, 2})
        self.assertTrue(accepted["valid"], accepted)

    def test_rejects_unknown_duration_retry_block(self):
        result = validate_motion_script._validate(_motion_script(), 30, duration_retry_blocks={4})
        self.assertFalse(result["valid"])
        self.assertIn("duration retry blocks do not exist: 4", result["errors"])

    def test_accepts_complete_structured_script(self) -> None:
        result = validate_motion_script._validate(_motion_script(), 30)

        self.assertTrue(result["valid"], result)

    def test_rejects_one_filler_sentence_shared_by_two_blocks(self) -> None:
        # The 2026-07-31 ten-minute marathon appended this exact sentence to 36 of its 60
        # lines to stretch them to the word budget, pushed those takes past the speech
        # ceiling and delivered no video after 60 clip jobs and 60 takes.
        suffix = " it was an event that no one at the time could have ever predicted"
        script = _motion_script()
        script["blocks"][0]["vo_line"] = _words(15, 0) + suffix
        script["blocks"][1]["vo_line"] = _words(15, 100) + suffix

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any("share the verbatim phrase" in error for error in result["errors"]),
            result,
        )

    def test_names_the_expected_arc_shape_when_the_arc_is_wrong(self) -> None:
        # Reporting only what is wrong made a run rewrite the whole manifest three times,
        # guessing hook_block, then build_blocks, then prose.
        script = _motion_script()
        script["arc"] = {
            "hook_block": 1,
            "build_blocks": [],
            "turn_block": 2,
            "payoff_block": 3,
        }

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any("expected arc shape" in error for error in result["errors"]),
            result,
        )

    def test_script_lock_frees_formatting_and_catches_an_appended_word(self) -> None:
        script = _motion_script()
        digest = validate_motion_script._narration_digest(script)

        first = script["blocks"][0]["vo_line"]
        script["blocks"][0]["vo_line"] = f"  {first.upper()}.  "
        self.assertEqual(validate_motion_script._narration_digest(script), digest)

        script["blocks"][0]["vo_line"] = f"{first} and one appended word"
        self.assertNotEqual(validate_motion_script._narration_digest(script), digest)

    def test_a_year_written_as_words_is_not_padding(self) -> None:
        # The skill orders numbers written as words; "in the year twenty twenty" then
        # tripped the adjective-soup rule on a run that had obeyed both rules.
        script = _motion_script()
        script["blocks"][0]["vo_line"] = f"In the year twenty twenty. {_words(16, 600)}"

        result = validate_motion_script._validate(script, 30)

        self.assertTrue(result["valid"], result)

    def test_rejects_a_shot_without_a_framing_size(self) -> None:
        script = _motion_script()
        script["blocks"][0]["shots"][2] = "the gauge sits on the kerb"

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            "shot 3 does not open with a framing size",
            " ".join(result["invalid_blocks"][0]["errors"]),
        )

    def test_rejects_two_neighbouring_shots_of_the_same_size(self) -> None:
        script = _motion_script()
        script["blocks"][0]["shots"][1] = f"WIDE: {_words(3, 700)}"

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            "shots 1 and 2 are both WIDE",
            " ".join(result["invalid_blocks"][0]["errors"]),
        )

    def test_rejects_an_ots_that_names_no_shoulder(self) -> None:
        script = _motion_script()
        script["blocks"][0]["shots"][2] = f"OTS: {_words(3, 800)}"

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            "is an OTS but names no shoulder",
            " ".join(result["invalid_blocks"][0]["errors"]),
        )

    def test_accepts_an_ots_that_names_a_shoulder(self) -> None:
        script = _motion_script()
        script["blocks"][0]["shots"][2] = "OTS over the courier's shoulder, the gauge beyond"

        result = validate_motion_script._validate(script, 30)

        self.assertTrue(result["valid"], result)

    def test_rejects_re_establishing_a_location_already_seen(self) -> None:
        script = _motion_script()
        script["blocks"][2]["location"] = "hot street"

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any("returns to location" in error for error in result["errors"]),
            result,
        )

    def test_rejects_the_same_shot_description_in_two_blocks(self) -> None:
        script = _motion_script()
        script["blocks"][0]["shots"][0] = f"WIDE: {_words(10, 900)}"
        script["blocks"][2]["shots"][0] = f"MEDIUM: {_words(10, 900)}"

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any("share the verbatim phrase" in error for error in result["errors"]),
            result,
        )

    def test_rejects_two_nearby_blocks_that_render_from_the_same_inputs(self) -> None:
        # The complaint from dev: the narration differs but the clip looks like the block
        # from two back, because the same location and the same assets in the same order
        # go into the render.
        script = _motion_script()
        script["blocks"][2]["location"] = "hot street"
        script["blocks"][2]["assets_used"] = list(script["blocks"][0]["assets_used"])
        script["blocks"][2]["shots"] = _shots(5, 700)
        script["blocks"][2]["shots"][0] = f"CU: {_words(3, 750)}"

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any("render from the same inputs" in error for error in result["errors"]),
            result,
        )

    def test_allows_the_same_location_when_the_assets_differ(self) -> None:
        script = _motion_script()
        script["blocks"][2]["location"] = "hot street"
        script["blocks"][2]["assets_used"] = ["hot street", "prop_gauge", "kerb_stone"]
        script["blocks"][2]["shots"] = _shots(5, 700)
        script["blocks"][2]["shots"][0] = f"CU: {_words(3, 750)}"

        result = validate_motion_script._validate(script, 30)

        self.assertTrue(result["valid"], result)

    def test_rejects_a_cold_open_that_runs_past_eight_words(self) -> None:
        script = _motion_script()
        script["blocks"][0]["vo_line"] = _words(30, 0)

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any("the cold open is" in error for error in result["errors"]),
            result,
        )

    def test_kids_keeps_its_warm_opening(self) -> None:
        # The cold-open brevity binds History and Explainer; Kids keeps its host manner.
        script = _motion_script(last_word_count=19)
        script["genre"] = "kids"
        script["sources"] = []
        for index, block in enumerate(script["blocks"]):
            block["shots"] = _shots(4, index * 100)
            block["vo_line"] = _words(19, index * 100)

        result = validate_motion_script._validate(script, 30)

        self.assertTrue(result["valid"], result)

    def test_rejects_line_over_word_budget(self) -> None:
        result = validate_motion_script._validate(
            _motion_script(last_word_count=35),
            30,
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "vo_line must contain 20-23 words",
            result["invalid_blocks"][0]["errors"],
        )

    def test_rejects_line_broken_into_many_sentences(self) -> None:
        script = _motion_script()
        script["blocks"][0]["vo_line"] = (
            "Ice is slippery. Everybody knows that. But it is not because it is smooth. "
            "A mirror is smoother than ice, yet nobody slips on a window pane."
        )

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any(
                "sentences into one block" in error
                for error in result["invalid_blocks"][0]["errors"]
            ),
            result["invalid_blocks"][0]["errors"],
        )

    def test_rejects_digits_in_voice_line(self) -> None:
        script = _motion_script()
        script["blocks"][0]["vo_line"] = (
            "On August 15th, 1977 a volunteer astronomer flipping through printouts "
            "spotted a signal so loud that he scrawled one stunned word beside it"
        )

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any(
                "write numbers, dates and years as words" in error
                for error in result["invalid_blocks"][0]["errors"]
            ),
            result["invalid_blocks"][0]["errors"],
        )

    def test_rejects_tts_prompt_wrapper_inside_voice_line(self) -> None:
        script = _motion_script()
        script["blocks"][0]["vo_line"] = (
            "[deadpan, starts speaking immediately] [00:00-00:09] "
            + _words(30)
        )

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            (
                "vo_line must contain authored narration only, without "
                "TTS delivery instructions or timecodes"
            ),
            result["invalid_blocks"][0]["errors"],
        )


    def test_accepts_kids_word_budget(self) -> None:
        # Lowered again 2026-08-03 to 20-24: the house band came down to 23-27 because a
        # line packed to the top of the old band lands flush against the TTS bracket and
        # loses the release of its closing word, and Kids stays one band below the house.
        script = _motion_script(last_word_count=19)
        script["genre"] = "kids"
        for index, block in enumerate(script["blocks"]):
            block["shots"] = _shots(4, index * 100)
            block["vo_line"] = _words(19, index * 100)
        script["sources"] = []

        result = validate_motion_script._validate(script, 30)

        self.assertTrue(result["valid"], result)

    def _talking_characters_script(self):
        script = _motion_script()
        script["genre"] = "kids"
        script["talking_characters"] = True
        script["sources"] = []
        kinds = ("narration", "dialogue", "narration")
        for index, block in enumerate(script["blocks"], start=1):
            block["shots"] = _shots(4, index * 100)
            block["block_kind"] = kinds[index - 1]
            if kinds[index - 1] == "dialogue":
                block["vo_line"] = _words(19, index * 100)
                block["speakers"] = ["bee", "butterfly"]
            else:
                block["vo_line"] = _words(19, index * 100)
                block.pop("speakers", None)
        return script

    def test_accepts_alternating_talking_characters_script(self) -> None:
        result = validate_motion_script._validate(
            self._talking_characters_script(), 30
        )

        self.assertTrue(result["valid"], result)

    def test_rejects_dialogue_block_written_at_narration_length(self) -> None:
        script = self._talking_characters_script()
        script["blocks"][1]["vo_line"] = _words(32)

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            "vo_line must contain 16-22 words",
            result["invalid_blocks"][0]["errors"],
        )

    def test_rejects_broken_block_kind_alternation(self) -> None:
        script = self._talking_characters_script()
        script["blocks"][1]["block_kind"] = "narration"
        script["blocks"][1].pop("speakers", None)

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            "block_kind must alternate: block 2 must be 'dialogue'",
            result["invalid_blocks"][0]["errors"],
        )

    def test_rejects_three_speakers_in_one_dialogue_block(self) -> None:
        script = self._talking_characters_script()
        script["blocks"][1]["speakers"] = ["bee", "butterfly", "ladybird"]

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            "a dialogue block takes at most 2 speaking characters",
            result["invalid_blocks"][0]["errors"],
        )

    def test_rejects_talking_characters_outside_kids(self) -> None:
        script = self._talking_characters_script()
        script["genre"] = "education"
        script["sources"] = ["https://www.epa.gov/heatislands"]

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn("talking_characters is a Kids-only direction", result["errors"])

    def test_block_kind_needs_flag(self) -> None:
        script = _motion_script()
        script["blocks"][0]["block_kind"] = "dialogue"

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            "block_kind belongs to talking_characters runs only",
            result["invalid_blocks"][0]["errors"],
        )

    def test_rejects_conversational_filler(self) -> None:
        script = _motion_script()
        script["blocks"][0]["vo_line"] = "You know " + _words(20)

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            'vo_line must not use conversational filler: "you know" — reach the '
            "word count with content, not padding",
            result["invalid_blocks"][0]["errors"],
        )

    def test_rejects_stacked_repeated_modifier(self) -> None:
        script = _motion_script()
        script["blocks"][0]["vo_line"] = "sparkly dreamy sparkly sky " + _words(18)

        result = validate_motion_script._validate(script, 30)

        self.assertFalse(result["valid"])
        self.assertIn(
            'vo_line repeats "sparkly" within 6 words — stacked epithets read as '
            "padding; keep one modifier per thing",
            result["invalid_blocks"][0]["errors"],
        )


class PreinstalledPythonCompatibilityTest(unittest.TestCase):
    """Sandboxes may run bundled scripts on Python 3.9; CI runs a newer Python."""

    def test_bundled_workflow_scripts_avoid_python_310_only_constructs(self) -> None:
        import ast

        resources = SCRIPTS_DIRECTORY.parents[1]
        problems = []
        for path in sorted(resources.rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source, filename=str(path), feature_version=(3, 9))
            except SyntaxError as error:
                problems.append(f"{path.relative_to(resources)}:{error.lineno}: {error.msg}")
                continue
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "zip"
                    and any(keyword.arg == "strict" for keyword in node.keywords)
                ):
                    problems.append(f"{path.relative_to(resources)}:{node.lineno}: zip(strict=...)")
        self.assertEqual(problems, [])


class CaptionAlignmentTest(unittest.TestCase):
    def test_block_alignment_rejects_mismatched_block_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "1 spoken blocks but 2 authored blocks"):
            audio_to_captions.align_blocks_to_script(
                [{"n": 1, "words": [], "speech_start": 0.0, "speech_end": 1.0}],
                [["one"], ["two"]],
                minimum_similarity=0.75,
            )

    def test_missing_local_whisper_is_a_distinct_unavailable_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            audio = Path(temporary_directory) / "narration.wav"
            output = Path(temporary_directory) / "captions.srt"
            audio.write_bytes(b"not-a-real-audio-file")

            original = subtitle_audio_to_captions.get_words
            try:
                subtitle_audio_to_captions.get_words = lambda *args, **kwargs: (
                    (_ for _ in ()).throw(
                        subtitle_audio_to_captions.WhisperUnavailableError("missing")
                    )
                )
                old_argv = sys.argv
                sys.argv = [
                    "audio_to_captions.py",
                    str(audio),
                    "--srt",
                    str(output),
                ]
                self.assertEqual(
                    subtitle_audio_to_captions.main(),
                    subtitle_audio_to_captions.WHISPER_UNAVAILABLE_EXIT_CODE,
                )
                self.assertFalse(output.exists())
            finally:
                sys.argv = old_argv
                subtitle_audio_to_captions.get_words = original

    def test_caption_alignment_failure_is_not_whisper_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            audio = Path(temporary_directory) / "narration.wav"
            script = Path(temporary_directory) / "script_manifest.json"
            output = Path(temporary_directory) / "captions.srt"
            audio.write_bytes(b"not-a-real-audio-file")
            script.write_text(
                '{"beats":[{"phrase":"authored words here now"}]}',
                encoding="utf-8",
            )

            original = subtitle_audio_to_captions.get_words
            try:
                subtitle_audio_to_captions.get_words = lambda *args, **kwargs: (
                    [{"word": "unrelated", "start": 0.0, "end": 0.2}],
                    "test",
                )
                old_argv = sys.argv
                sys.argv = [
                    "audio_to_captions.py",
                    str(audio),
                    "--srt",
                    str(output),
                    "--script",
                    str(script),
                ]
                self.assertEqual(subtitle_audio_to_captions.main(), 1)
                self.assertFalse(output.exists())
            finally:
                sys.argv = old_argv
                subtitle_audio_to_captions.get_words = original

    def test_keeps_a_dropped_opener_inside_its_own_block_window(self) -> None:
        # The STT swallowed the quiet opener "You know" of a block that starts at
        # 21.4s. Without a floor the authored words are spread from the previous
        # block's last word (or 0.0) and the caption fires seconds too early.
        whisper_words = [
            {"word": "sleep", "start": 22.6, "end": 22.9},
            {"word": "rebuilds", "start": 22.9, "end": 23.4},
        ]

        aligned, _ = audio_to_captions.align_words_to_script(
            whisper_words,
            ["You", "know", "sleep", "rebuilds"],
            span_floor=21.4,
            span_ceiling=31.0,
        )

        self.assertEqual([word["word"] for word in aligned], ["You", "know", "sleep", "rebuilds"])
        self.assertGreaterEqual(aligned[0]["start"], 21.4)
        self.assertLessEqual(aligned[1]["end"], 22.6)

    def test_clamps_a_dropped_tail_to_the_block_ceiling(self) -> None:
        whisper_words = [
            {"word": "deep", "start": 4.9, "end": 5.0},
            {"word": "sleep", "start": 5.0, "end": 5.2},
            {"word": "rebuilds", "start": 5.2, "end": 5.6},
            {"word": "memory", "start": 5.6, "end": 5.9},
        ]

        aligned, _ = audio_to_captions.align_words_to_script(
            whisper_words,
            ["deep", "sleep", "rebuilds", "memory", "every", "night"],
            span_floor=4.8,
            span_ceiling=6.1,
        )

        self.assertEqual(
            [word["word"] for word in aligned],
            ["deep", "sleep", "rebuilds", "memory", "every", "night"],
        )
        self.assertLessEqual(aligned[-1]["end"], 6.1)

    def test_replaces_whisper_substitution_with_exact_authored_words(self) -> None:
        whisper_words = [
            {"word": "Rain", "start": 0.0, "end": 0.2},
            {"word": "fell", "start": 0.2, "end": 0.4},
            {"word": "softly", "start": 0.4, "end": 0.7},
            {"word": "attacks", "start": 0.8, "end": 1.2},
            {"word": "Her", "start": 1.3, "end": 1.5},
            {"word": "smile", "start": 1.5, "end": 1.8},
            {"word": "dimmed", "start": 1.8, "end": 2.1},
        ]
        script_tokens = [
            "Rain",
            "fell",
            "softly.",
            "A",
            "tag",
            "swayed.",
            "Her",
            "smile",
            "dimmed.",
        ]

        aligned, similarity = audio_to_captions.align_words_to_script(
            whisper_words,
            script_tokens,
        )

        self.assertGreaterEqual(similarity, 0.55)
        self.assertEqual(
            [word["word"] for word in aligned],
            script_tokens,
        )
        self.assertEqual(aligned[3]["start"], 0.8)
        self.assertEqual(aligned[5]["end"], 1.2)


class PictureStoryValidatorTest(unittest.TestCase):
    def test_accepts_continuous_narration_without_per_beat_pause_budget(self) -> None:
        script = {
            "genre": "storytelling",
            "animation_mode": "scene_based",
            "motion_mode": "stills",
            "beats": [
                {
                    "n": index,
                    "phrase": "one two three four five",
                    "image_mode": "new",
                }
                for index in range(1, 28)
            ],
        }

        result = validate_picture_story._validate(script, 60)

        self.assertTrue(result["valid"])
        self.assertEqual(result["total_word_count"], 135)
        self.assertEqual(result["maximum_word_count"], 150)

    def test_enforces_product_beat_density(self) -> None:
        script = {
            "genre": "storytelling",
            "animation_mode": "scene_based",
            "beats": [
                {
                    "n": index,
                    "phrase": "four exact words here",
                    "image_mode": "new",
                }
                for index in range(1, 21)
            ]
        }

        result = validate_picture_story._validate(script, 31)

        self.assertFalse(result["valid"])
        self.assertEqual(
            result["expected_beat_count"],
            {"minimum": 13, "maximum": 18},
        )

    def test_rejects_three_word_phrase(self) -> None:
        script = {
            "genre": "storytelling",
            "animation_mode": "scene_based",
            "beats": [
                {
                    "n": index,
                    "phrase": (
                        "only three words"
                        if index == 1
                        else "four exact words here"
                    ),
                    "image_mode": "new",
                }
                for index in range(1, 14)
            ]
        }

        result = validate_picture_story._validate(script, 31)

        self.assertFalse(result["valid"])
        self.assertIn(
            "phrase must contain 4-8 words",
            result["invalid_beats"][0]["errors"],
        )


class ResultManifestValidatorTest(unittest.TestCase):
    def test_authored_picture_story_manifest_does_not_need_runtime_frame_urls(self) -> None:
        script = {
            "genre": "storytelling",
            "animation_mode": "scene_based",
            "beats": [
                {
                    "n": 1,
                    "phrase": "one two three four",
                    "image_mode": "new",
                },
                {
                    "n": 2,
                    "phrase": "five six seven eight",
                    "image_mode": "variation",
                    "variation_of": 1,
                    "change_only": "eyes open",
                },
            ],
            "sources": ["https://example.com/story"],
        }
        assets = {
            "assets": [
                {
                    "name": "style key",
                    "kind": "style_key",
                    "job_id": "style-job",
                    "url": "https://cdn.example.com/style.png",
                }
            ]
        }

        result = validate_result_manifests._validate(script, assets)

        self.assertTrue(result["valid"], result)


class SceneTimelineBuilderTest(unittest.TestCase):
    def test_builds_contiguous_manifest_v2_frames(self) -> None:
        script = {
            "genre": "storytelling",
            "animation_mode": "scene_based",
            "beats": [
                {
                    "n": 1,
                    "phrase": "one two three four",
                    "image_mode": "new",
                },
                {
                    "n": 2,
                    "phrase": "five six seven eight",
                    "image_mode": "new",
                },
            ],
        }
        words = [
            {"word": token, "start": index * 0.25, "end": (index + 1) * 0.25}
            for index, token in enumerate(
                "one two three four five six seven eight".split()
            )
        ]

        manifest = build_scene_timeline.build_scene_manifest(
            script,
            {"words": words},
            2.0,
        )

        self.assertEqual(manifest["manifest_version"], 2)
        self.assertEqual(manifest["frames"][0]["start"], 0.0)
        self.assertEqual(manifest["frames"][-1]["end"], 2.0)
        self.assertEqual(
            [frame["n"] for frame in manifest["frames"]],
            list(range(1, len(manifest["frames"]) + 1)),
        )
        self.assertTrue(
            all(
                0 < frame["duration"] <= 1.5
                for frame in manifest["frames"]
            )
        )
        for frame in manifest["frames"]:
            self.assertEqual(frame["output_slot"], f"frame-{frame['n']:03d}")

    def test_builds_dependency_waves_and_caps_variation_chains(self) -> None:
        script = {
            "beats": [
                {
                    "n": 1,
                    "phrase": "one two three four",
                    "image_mode": "new",
                }
            ]
        }
        words = [
            {"word": token, "start": index, "end": index + 0.5}
            for index, token in enumerate("one two three four".split())
        ]

        manifest = build_scene_timeline.build_scene_manifest(
            script,
            {"words": words},
            6.0,
        )

        self.assertEqual(
            [frame["generation_wave"] for frame in manifest["frames"]],
            [0, 1, 2, 0, 1],
        )
        self.assertEqual(
            manifest["generation_waves"],
            [
                {"wave": 0, "output_slots": ["frame-001", "frame-004"]},
                {"wave": 1, "output_slots": ["frame-002", "frame-005"]},
                {"wave": 2, "output_slots": ["frame-003"]},
            ],
        )
        for frame in manifest["frames"]:
            if frame["image_mode"] == "variation":
                self.assertEqual(
                    frame["generation_wave"],
                    manifest["frames"][frame["variation_of_frame"] - 1][
                        "generation_wave"
                    ]
                    + 1,
                )

    def test_rejects_unrelated_narration(self) -> None:
        script = {
            "beats": [
                {
                    "n": 1,
                    "phrase": "one two three four",
                    "image_mode": "new",
                }
            ]
        }
        words = [
            {"word": token, "start": index, "end": index + 0.5}
            for index, token in enumerate("alpha beta gamma delta".split())
        ]

        with self.assertRaisesRegex(ValueError, "similarity"):
            build_scene_timeline.build_scene_manifest(
                script,
                {"words": words},
                4.0,
            )

    def test_rejects_narration_far_shorter_than_requested_duration(self) -> None:
        script = {
            "beats": [
                {
                    "n": 1,
                    "phrase": "one two three four",
                    "image_mode": "new",
                }
            ]
        }
        words = [
            {"word": token, "start": index, "end": index + 0.5}
            for index, token in enumerate("one two three four".split())
        ]

        with self.assertRaisesRegex(ValueError, "requested duration"):
            build_scene_timeline.build_scene_manifest(
                script,
                {"words": words},
                41.1,
                60,
            )


class BindSceneFrameResultsTest(unittest.TestCase):
    def test_binds_urls_job_ids_and_variation_lineage(self) -> None:
        manifest = {
            "manifest_version": 2,
            "frames": [
                {"n": 1, "output_slot": "frame-001", "image_mode": "new"},
                {
                    "n": 2,
                    "output_slot": "frame-002",
                    "image_mode": "variation",
                    "reference_output_slot": "frame-001",
                },
            ],
        }
        generate_result = {
            "requests": [
                {"output_slot": "frame-001", "job_ids": ["job-1"]},
                {"output_slot": "frame-002", "job_ids": ["job-2"]},
            ]
        }
        status_result = {
            "results": [
                {"job_id": "job-1", "result": {"url": "https://cdn/1.png"}},
                {"job_id": "job-2", "url": "https://cdn/2.png"},
            ]
        }

        bound = bind_scene_frame_results.bind_scene_frame_results(
            manifest,
            [generate_result, status_result],
        )

        self.assertEqual(bound["frames"][0]["frame_job_id"], "job-1")
        self.assertEqual(bound["frames"][1]["frame_url"], "https://cdn/2.png")
        self.assertEqual(
            bound["frames"][1]["reference_frame_job_id"],
            "job-1",
        )
        self.assertEqual(
            bound["frames"][1]["reference_frame_url"],
            "https://cdn/1.png",
        )

    def test_binds_openai_indexed_jobs_wait_results(self) -> None:
        manifest = {
            "manifest_version": 2,
            "frames": [
                {"n": 1, "output_slot": "frame-001", "image_mode": "new"},
                {
                    "n": 2,
                    "output_slot": "frame-002",
                    "image_mode": "variation",
                    "reference_output_slot": "frame-001",
                },
            ],
        }
        jobs_wait_result = {
            "jobs": [
                {
                    "index": 1,
                    "job_id": "job-1",
                    "status": "completed",
                    "result_url": "https://cdn/1.png",
                },
                {
                    "index": 2,
                    "job_id": "job-2",
                    "status": "completed",
                    "result_url": "https://cdn/2.png",
                },
            ]
        }

        bound = bind_scene_frame_results.bind_scene_frame_results(
            manifest,
            [jobs_wait_result],
        )

        self.assertEqual(bound["frames"][0]["frame_job_id"], "job-1")
        self.assertEqual(bound["frames"][1]["frame_url"], "https://cdn/2.png")
        self.assertEqual(
            bound["frames"][1]["reference_frame_job_id"],
            "job-1",
        )

    def test_rejects_missing_frame_result(self) -> None:
        manifest = {
            "manifest_version": 2,
            "frames": [
                {"n": 1, "output_slot": "frame-001", "image_mode": "new"},
            ],
        }

        with self.assertRaisesRegex(ValueError, "no completed job_id/url"):
            bind_scene_frame_results.bind_scene_frame_results(manifest, [])


class MaterializeSceneFramesTest(unittest.TestCase):
    def test_atomically_replaces_an_existing_frame_directory(self) -> None:
        manifest = {
            "manifest_version": 2,
            "frames": [
                {
                    "n": 1,
                    "output_slot": "frame-001",
                    "frame_url": "https://cdn/1.png",
                },
                {
                    "n": 2,
                    "output_slot": "frame-002",
                    "frame_url": "https://cdn/2.png",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            frames_directory = Path(temporary_directory) / "frames"
            frames_directory.mkdir()
            (frames_directory / "stale.png").write_bytes(b"old")

            count = materialize_scene_frames.materialize_scene_frames(
                manifest,
                frames_directory,
                open_url=lambda _url: io.BytesIO(b"image" * 20),
            )

            self.assertEqual(count, 2)
            self.assertEqual(
                sorted(path.name for path in frames_directory.iterdir()),
                ["frame001.png", "frame002.png"],
            )


if __name__ == "__main__":
    unittest.main()


_SONG_PROMPT = (
    "A full 1-minute children's dance-along song, SUNG by a warm bright cheerful female "
    "singer. THE BEAT IS STEADY AND CONSTANT from the first second to the last: 112 BPM, "
    "simple 4/4, NO tempo changes. Every lyric line has 8 syllables in steady trochaic "
    "meter, sung one syllable per beat, and every line starts exactly on beat one of its "
    "bar; each line is one 4-bar phrase. Chorus repeats verbatim every time.\n"
    'Verse 1: "Hammy stirs the yellow soup / Carrots tumble in the pot"\n'
    'Chorus: "Stir it stir it, one two three / Hammy cooks for you and me"\n'
)


class SongPromptValidatorTest(unittest.TestCase):
    def test_accepts_prompt_built_from_the_skeleton(self) -> None:
        result = validate_song_prompt.validate(_SONG_PROMPT)

        self.assertTrue(result["valid"], result)

    def test_negated_tempo_clause_is_not_read_as_a_banned_word(self) -> None:
        result = validate_song_prompt.validate(_SONG_PROMPT)

        self.assertNotIn(
            'banned tempo word "tempo change"',
            " ".join(result["errors"]),
        )

    def test_rejects_bridge_and_untested_bpm(self) -> None:
        prompt = _SONG_PROMPT.replace("112 BPM", "96 BPM") + " Add a dreamy bridge."

        result = validate_song_prompt.validate(prompt)

        self.assertFalse(result["valid"])
        joined = " ".join(result["errors"])
        self.assertIn("96 is untested", joined)
        self.assertIn('banned tempo word "bridge"', joined)

    def test_rejects_wandering_meter(self) -> None:
        prompt = _SONG_PROMPT.replace(
            '"Hammy stirs the yellow soup / Carrots tumble in the pot"',
            '"Hammy the hamster cooks an enormous pot of vegetable soup for everyone today"',
        )

        result = validate_song_prompt.validate(prompt)

        self.assertFalse(result["valid"])
        self.assertIn("syllable", " ".join(result["errors"]))
