import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import caption_evidence as evidence
import caption_guard as guard
import caption_regions as regions
import subtitle_paper_burn as burn


class RegionReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(guard, 'STATE_ROOT', self.root/'state')
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.video = self.root/'source.mp4'
        self.srt = self.root/'caps.srt'
        self.map = self.root/'regions.json'
        self.receipt = self.root/'region-receipt.json'
        self.video.write_bytes(b'unit fixture')
        self.srt.write_text('1\n00:00:00,100 --> 00:00:00,900\nHello there\n')

    def register(self, boxes=None):
        self.map.write_text(json.dumps({'video_sha256': evidence.sha256(self.video),
            'reviewed_duration': 1, 'reviewed_intervals': [{'start':0,'end':1}],
            'regions': boxes or []}))
        digest = evidence.sha256(self.map)
        guard.reserve_regions(self.video, digest)
        guard.prepared(self.video, 'prepared-evidence')
        result = {'verdict':'REGIONS_REVIEWED', 'review_view':'source_boxes_unprotected', 'video_sha256': evidence.sha256(self.video),
            'srt_sha256': evidence.sha256(self.srt), 'regions_sha256': digest,
            'evidence_sha256': 'prepared-evidence'}
        guard.approve(self.video, result)
        self.receipt.write_text(json.dumps(result))
        return result

    def test_source_key_survives_renames_and_render_limit_counts_failures(self):
        self.register()
        first = guard.begin_render(self.video, self.srt, self.map, self.receipt)
        self.assertEqual(first['attempt'], 1)
        # Placement fails after reserving an attempt. Renaming the clean source,
        # output, transcript or review cannot create another per-source budget.
        moved = self.root/'other-folder'/'renamed.mp4'
        moved.parent.mkdir(); shutil.copyfile(self.video, moved)
        second = guard.begin_render(moved, self.srt, self.map, self.receipt)
        self.assertEqual(second['attempt'], 2)
        with self.assertRaisesRegex(ValueError, 'render limit'):
            guard.begin_render(moved, self.srt, self.map, self.receipt)
        with self.assertRaisesRegex(ValueError, 'stale or missing'):
            guard.check_delivery({'source_sha256':evidence.sha256(self.video),
                'srt_sha256':evidence.sha256(self.srt), 'region_guard':first})

    def test_reproduced_face_shrink_is_forbidden_after_placement_failure(self):
        face = {'start':0,'end':1,'box':[.15,.03,.85,.43]}
        self.register([face])
        guard.begin_render(self.video, self.srt, self.map, self.receipt)
        face['box'][3] = .31  # Observed failed DEV attempt excluded mouth/chin.
        self.map.write_text(json.dumps({'regions':[face]}))
        with self.assertRaisesRegex(ValueError, 'frozen'):
            guard.reserve_regions(self.video, evidence.sha256(self.map))
        with self.assertRaisesRegex(ValueError, 'frozen'):
            guard.begin_render(self.video, self.srt, self.map, self.receipt)

    def test_only_one_region_correction_before_first_render(self):
        self.register()
        self.register([{'start':0,'end':1,'box':[0,0,.5,.5]}])
        with self.assertRaisesRegex(ValueError, 'revision limit'):
            self.register([{'start':0,'end':1,'box':[0,0,.6,.6]}])

    def test_stale_or_fabricated_receipt_cannot_start_render(self):
        self.register()
        self.srt.write_text(self.srt.read_text().replace('Hello', 'Changed'))
        with self.assertRaisesRegex(ValueError, 'stale'):
            guard.begin_render(self.video, self.srt, self.map, self.receipt)
        with self.assertRaisesRegex(ValueError, 'no longer current'):
            guard.approve(self.video, {'regions_sha256':evidence.sha256(self.map),
                                      'evidence_sha256':'fabricated evidence'})

    def test_approval_from_old_box_only_review_cannot_start_render(self):
        old=self.register();old.pop('review_view')
        with guard.state(self.video) as data:data['approved']=old
        self.receipt.write_text(json.dumps(old))
        with self.assertRaisesRegex(ValueError,'stale annotated-region review'):
            guard.begin_render(self.video,self.srt,self.map,self.receipt)

    def test_boxes_use_source_pixels_and_active_frame_time(self):
        raw = Image.new('RGB', (200,400), 'blue')
        box = {'start':.2,'end':.8,'box':[.2,.3,.8,.7]}
        drawn, active = regions.draw_regions(raw, [box], .5)
        self.assertEqual(active, [0])
        self.assertEqual(drawn.getpixel((40,200)), (255,64,64))
        self.assertEqual(drawn.getpixel((100,279)), (255,64,64))
        self.assertEqual(raw.getpixel((40,200)), (0,0,255))
        absent, active = regions.draw_regions(raw, [box], .8)
        self.assertEqual(active, [])
        self.assertEqual(absent.tobytes(), raw.tobytes())

    def test_unprotected_view_exposes_fingertip_and_transition_gap(self):
        raw = Image.new('RGB', (200,400), 'blue')
        paint = ImageDraw.Draw(raw)
        # A hand crosses the upper edge of its box; the fingertip must stay visible.
        paint.rectangle((170,150,180,230), fill='white')
        boxes = [{'start':0,'end':1,'box':[0,.45,1,.9]}]
        view = regions.unprotected_view(raw, boxes, .5)
        self.assertEqual(view.getpixel((175,150)), (255,255,255))
        self.assertEqual(view.getpixel((175,179)), (255,255,255))
        self.assertEqual(view.getpixel((175,180)), (32,32,32))
        # The observed transition gap must not disappear through padding/rounding.
        boxes = [{'start':0,'end':1,'box':[0,0,1,.25]},
                 {'start':0,'end':1,'box':[0,.30,1,1]}]
        view = regions.unprotected_view(raw, boxes, .5)
        self.assertEqual(view.getpixel((100,99)), (32,32,32))
        self.assertEqual(view.getpixel((100,100)), (0,0,255))
        self.assertEqual(view.getpixel((100,119)), (0,0,255))
        self.assertEqual(view.getpixel((100,120)), (32,32,32))
        boxes[0]['box'][3] = .45
        closed = regions.unprotected_view(raw, boxes, .5)
        self.assertEqual(closed.getpixel((100,110)), (32,32,32))
        self.assertEqual(regions.unprotected_view(raw, boxes, 1).tobytes(), raw.tobytes())

    def test_native_sheet_budget_preserves_dimensions(self):
        sheet = Image.effect_noise((1080,2040),10).convert('RGB')
        path = self.root/'sheet.jpg'
        regions.save_sheet(sheet,path)
        self.assertLessEqual(path.stat().st_size,480*1024)
        with Image.open(path) as saved:self.assertEqual(saved.size,(1080,2040))
        with self.assertRaisesRegex(ValueError,'exceeds image budget'):
            regions.save_sheet(Image.effect_noise((1080,2040),100).convert('RGB'),path)

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required')
    def test_real_annotated_review_render_and_final_gate(self):
        self.video.unlink()
        subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i',
                        'color=blue:s=320x576:r=24:d=1','-c:v','libx264',str(self.video)],check=True)
        self.map.write_text(json.dumps({'video_sha256':evidence.sha256(self.video),
            'reviewed_duration':1,'reviewed_intervals':[{'start':0,'end':1}],
            'regions':[{'start':0,'end':1,'box':[.3,.05,.7,.4]}]}))
        clean = self.root/'clean'; marked = self.root/'marked'; review = self.root/'review.json'
        evidence.prepare(self.video, self.srt, clean)
        result = regions.prepare(self.video, self.srt, self.map, clean/'evidence.json', marked)
        self.assertTrue(result['samples'])
        self.assertLess((marked/result['sheets'][0]['file']).stat().st_size,512*1024)
        answers = json.loads((marked/'region-review-template.json').read_text())
        review.write_text(json.dumps(answers))
        args = [self.video,self.srt,self.map,clean/'evidence.json',marked/'region-evidence.json',review,self.receipt]
        with self.assertRaisesRegex(ValueError, 'failed or uninspected'):
            regions.verify(*args)
        self.assertEqual(json.loads(self.receipt.read_text())['verdict'],'FAIL')
        # Synthetic fixture has no subjects; explicit test review of known pixels.
        for row in answers['frames']:
            row.update(subjects_covered=True, unprotected_subjects=[], notes='Synthetic uniform blue: no face/hand/label outside marked test box.')
        # A broad all-clear cannot override an explicitly observed escaped finger.
        answers['frames'][0]['unprotected_subjects']=['raised fingertip']
        review.write_text(json.dumps(answers))
        with self.assertRaisesRegex(ValueError,'failed or uninspected'):regions.verify(*args)
        answers['frames'][0]['unprotected_subjects']=[]
        review.write_text(json.dumps(answers))
        regions.verify(*args)
        out = self.root/'final.mp4'
        cli = ['burn','--in',str(self.video),'--out',str(out),'--srt',str(self.srt),
               '--style','bold','--no-caps','--profile','safe','--font-key','montserrat',
               '--protected-regions',str(self.map),'--region-review',str(self.receipt)]
        with patch.object(sys,'argv',cli), contextlib.redirect_stdout(io.StringIO()):
            burn.main()
        layout = json.loads(Path(str(out)+'.captions.json').read_text())
        self.assertEqual(layout['region_guard']['attempt'],1)
        guard.check_delivery(layout)
        final = self.root/'final-evidence'; evidence.prepare(out,self.srt,final)
        final_review=json.loads((final/'review-template.json').read_text())
        for row in final_review['frames']:
            row.update(clear=True,text_ok=True,notes='Synthetic blue fixture with visible white text.')
        final_answers=self.root/'final-review.json';final_answers.write_text(json.dumps(final_review))
        self.assertEqual(evidence.verify(out,self.srt,final/'evidence.json',final_answers,self.root/'final-receipt.json')['verdict'],'PASS')
        # A failed re-review invalidates prior approval and final delivery.
        answers['frames'][0]['subjects_covered']=False;review.write_text(json.dumps(answers))
        with self.assertRaisesRegex(ValueError,'failed or uninspected'):regions.verify(*args)
        with self.assertRaisesRegex(ValueError,'stale or missing'):guard.check_delivery(layout)
        # The supplemental view is bound too, not merely generated and discarded.
        exposed=marked/result['samples'][0]['unprotected_frame']
        original=exposed.read_bytes();exposed.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'unprotected frame missing or changed'):regions.verify(*args)
        exposed.write_bytes(original)
        # A changed annotated image cannot be rubber-stamped with the old hash.
        (marked/result['samples'][0]['frame']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'missing or changed'):regions.verify(*args)


if __name__ == '__main__':
    unittest.main()
