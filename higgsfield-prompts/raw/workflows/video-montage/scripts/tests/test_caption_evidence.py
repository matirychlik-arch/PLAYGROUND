import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from caption_evidence import prepare, verify, sha256, samples
from caption_placement import read_regions


class CaptionEvidenceTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg required")
    def test_long_caption_preserves_every_exact_frame_across_bounded_batches(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); video = td/"in.mp4"; srt = td/"caps.srt"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                            "testsrc2=s=160x288:r=10:d=30", "-c:v", "libx264", str(video)], check=True)
            srt.write_text("1\n00:00:00,000 --> 00:00:30,000\nLong caption\n")
            run = subprocess.run
            selections = []
            def bounded_run(command, **kwargs):
                if command[0] == "ffmpeg" and "-vf" in command:
                    expression = command[command.index("-vf")+1]
                    self.assertLessEqual(expression.count("eq(n,"), 24,
                                         "FFmpeg 5.x filter parser regression")
                    selections.append(expression)
                return run(command, **kwargs)
            with patch("caption_evidence.subprocess.run", side_effect=bounded_run):
                evidence = prepare(video, srt, td/"evidence")
            rows = evidence["samples"]
            self.assertGreater(len(rows), 100)
            self.assertGreater(len(selections), 4)
            self.assertEqual(len({r["frame_index"] for r in rows}), sum(s.count("eq(n,") for s in selections))
            # Compare independently decoded frames on either side of a batch edge,
            # and the final displayed frame; filenames must not alias other batches.
            for row in [rows[0], rows[23], rows[24], rows[-1]]:
                exact = td/f"exact-{row['id']}.jpg"
                run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(video), "-vf",
                     f"select='eq(n,{row['frame_index']})'", "-frames:v", "1", "-q:v", "2", str(exact)], check=True)
                self.assertEqual(sha256(exact), row["sha256"])
            self.assertTrue(all((td/"evidence"/name).stat().st_size < 2*1024*1024 for name in evidence["sheets"]))

    def test_every_short_cue_and_edges_are_sampled(self):
        rows = samples([(0, .08, "Hi"), (2, 3, "Hello there")])
        self.assertEqual({r["cue"] for r in rows}, {0, 1})
        self.assertGreaterEqual(len(rows), 7)
        for cue in (0, 1):
            times = [r["time"] for r in rows if r["cue"] == cue]
            self.assertLessEqual(max(b-a for a,b in zip(times,times[1:])), .25)

    def test_source_identity_and_temporal_coverage_are_required(self):
        with tempfile.TemporaryDirectory() as td:
            video=Path(td)/"video"; video.write_bytes(b"source")
            file=Path(td)/"regions.json"
            data={"video_sha256":sha256(video),"reviewed_duration":3,
                  "reviewed_intervals":[{"start":0,"end":1}], "regions":[]}
            file.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"every caption interval"):
                read_regions(file,3,video,[(0,2,"Two words")])
            data["reviewed_intervals"].append({"start":1,"end":2})
            file.write_text(json.dumps(data))
            self.assertEqual(read_regions(file,3,video,[(0,2,"Two words")]),[])
            video.write_bytes(b"different")
            with self.assertRaisesRegex(ValueError,"different source"):
                read_regions(file,3,video,[(0,2,"Two words")])

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg required")
    @patch("caption_guard.check_delivery")
    def test_real_evidence_rejects_missing_failed_stale_and_tampered_reviews(self, _guard):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); video=td/"in.mp4"; srt=td/"caps.srt"
            subprocess.run(["ffmpeg","-v","error","-f","lavfi","-i",
                            "color=c=blue:s=160x288:r=24:d=2",
                            "-c:v","libx264",str(video)],check=True)
            srt.write_text("1\n00:00:01,700 --> 00:00:02,000\nTwo words\n")
            layout=Path(str(video)+'.captions.json')
            layout.write_text(json.dumps({'profile':'safe','verdict':'RENDERED','video_sha256':sha256(video),'srt_sha256':sha256(srt)}))
            ev=td/"frames"; evidence=prepare(video,srt,ev)
            self.assertLess(evidence["samples"][-1]["frame_time"], 2)
            manifest=ev/"evidence.json"; review=td/"review.json"; receipt=td/"receipt.json"
            answers=json.loads((ev/"review-template.json").read_text())
            review.write_text(json.dumps(answers))
            with self.assertRaisesRegex(ValueError,"incomplete"):
                verify(video,srt,manifest,review,receipt)
            # Test fixture is known uniform blue, deliberately review it explicitly.
            for row in answers["frames"]:
                row.update(clear=True,text_ok=True,notes="test fixture: uniform blue; synthetic review")
            review.write_text(json.dumps(answers))
            self.assertEqual(verify(video,srt,manifest,review,receipt)["verdict"],"PASS")
            answers["frames"][0]["clear"]=False
            review.write_text(json.dumps(answers))
            with self.assertRaises(ValueError): verify(video,srt,manifest,review,receipt)
            self.assertEqual(json.loads(receipt.read_text())["verdict"],"FAIL")
            answers["frames"][0]["clear"]=True
            dropped=answers["frames"].pop()
            review.write_text(json.dumps(answers))
            with self.assertRaisesRegex(ValueError,"every frame"): verify(video,srt,manifest,review,receipt)
            answers["frames"].append(dropped); review.write_text(json.dumps(answers))
            srt.write_text(srt.read_text().replace("Two words","Changed text"))
            with self.assertRaisesRegex(ValueError,"stale"):
                verify(video,srt,manifest,review,receipt)
            srt.write_text(srt.read_text().replace("Changed text","Two words"))
            frame=ev/json.loads(manifest.read_text())["samples"][0]["frame"]
            frame.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError,"frame missing or changed"):
                verify(video,srt,manifest,review,receipt)


if __name__ == "__main__":
    unittest.main()
