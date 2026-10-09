import importlib.util
import contextlib
import io
from types import SimpleNamespace
from unittest.mock import patch
import json
from pathlib import Path
import sys
import tempfile
import subprocess
import shutil
import unittest
from PIL import Image, ImageDraw

SCRIPTS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SCRIPTS))
from caption_placement import place, intersects, read_regions
import subtitle_paper_burn as burn
from caption_evidence import sha256
import caption_guard

class PlacementTests(unittest.TestCase):
    def overlay(self):
        image=Image.new('RGBA',(1080,1920))
        ImageDraw.Draw(image).rectangle((240,1450,840,1540),fill='white')
        return image

    def test_fox_face_is_clear_at_all_active_intervals(self):
        regions=[{'start':10,'end':20,'box':[.32,.70,.70,.90]}]
        image,box=place(self.overlay(),12,14,regions)
        self.assertFalse(intersects(box,regions[0]['box'],.015))
        self.assertGreaterEqual(box[1],.60)
        self.assertLessEqual(box[3],.83)
        self.assertEqual(image.size,(1080,1920))

    def test_nonoverlapping_time_does_not_move_caption(self):
        _,plain=place(self.overlay(),0,1,[])
        _,other=place(self.overlay(),0,1,[{'start':1,'end':2,'box':[0,.5,1,1]}])
        self.assertEqual(plain,other)

    def test_no_space_fails_instead_of_covering_subject(self):
        with self.assertRaisesRegex(ValueError,'no subject-clear position'):
            place(self.overlay(),0,1,[{'start':0,'end':2,'box':[0,0,1,1]}])

    def test_lower_closeup_uses_clear_upper_area(self):
        region={'start':0,'end':2,'box':[0,.48,1,1]}
        _,box=place(self.overlay(),0,1,[region])
        self.assertGreaterEqual(box[1],.10)
        self.assertLessEqual(box[3],.40)
        self.assertFalse(intersects(box,region['box'],.015))

    def test_empty_overlay_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'no visible ink'):
            place(Image.new('RGBA',(100,200)),0,1,[])

    def test_reviewed_duration_and_regions_are_validated(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'regions.json'
            p.write_text(json.dumps({'reviewed_duration':30,'regions':[]}))
            self.assertEqual(read_regions(p,30),[])
            with self.assertRaises(ValueError):read_regions(p,40)
            for box in ([0,0,2,1],[.7,0,.1,1],[0,0,float('nan'),1]):
                p.write_text(json.dumps({'reviewed_duration':30,'regions':[{'start':0,'end':10,'box':box}]}))
                with self.assertRaises(ValueError):read_regions(p,30)

    def test_canonical_caption_cli_entrypoints_are_runnable(self):
        for name in ('audio_to_captions.py','subtitle_paper_burn.py'):
            result=subprocess.run([sys.executable,str(SCRIPTS/name),'--help'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('usage:',result.stdout)

    def test_numeric_caption_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'caps.srt';p.write_text('1\n00:00:00,100 --> 00:00:01,100\n123\n')
            self.assertEqual(burn.parse_srt(p)[0][2],'123')

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
    def test_real_render_preserves_audio_and_failed_rerun_invalidates_layout(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);video=td/'in.mp4';out=td/'out.mp4';srt=td/'caps.srt';regions=td/'regions.json'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=0x456789:s=320x576:r=24:d=3','-f','lavfi','-i','sine=frequency=440:duration=3','-c:v','libx264','-c:a','aac','-shortest',str(video)],check=True)
            srt.write_text('1\n00:00:00,100 --> 00:00:01,800\nRain comes home\n')
            reviewed={'video_sha256':sha256(video),'reviewed_duration':3,'reviewed_intervals':[{'start':0,'end':3}],'regions':[{'start':0,'end':3,'box':[.35,.72,.65,.88]}]}
            regions.write_text(json.dumps(reviewed))
            args=[sys.executable,str(SCRIPTS/'subtitle_paper_burn.py'),'--in',str(video),'--out',str(out),'--srt',str(srt),'--style','bold','--no-caps','--font-key','montserrat','--profile','safe','--protected-regions',str(regions)]
            region_receipt=td/'region-review.json'
            state_patch=patch.object(caption_guard,'STATE_ROOT',td/'state')
            state_patch.start(); self.addCleanup(state_patch.stop)
            caption_guard.reserve_regions(video,sha256(regions))
            caption_guard.prepared(video,'synthetic-test-evidence')
            approval={'verdict':'REGIONS_REVIEWED', 'review_view':'source_boxes_unprotected','video_sha256':sha256(video),
                      'srt_sha256':sha256(srt),'regions_sha256':sha256(regions),
                      'evidence_sha256':'synthetic-test-evidence'}
            caption_guard.approve(video,approval);region_receipt.write_text(json.dumps(approval))
            args += ['--region-review',str(region_receipt)]
            def run_burn():
                try:
                    with patch.object(sys,'argv',args[1:]), contextlib.redirect_stdout(io.StringIO()):
                        burn.main()
                    return SimpleNamespace(returncode=0,stderr='')
                except ValueError as error:
                    return SimpleNamespace(returncode=1,stderr=str(error))
            result=run_burn()
            self.assertEqual(result.returncode,0,result.stderr)
            receipt=Path(str(out)+'.captions.json')
            self.assertEqual(json.loads(receipt.read_text())['verdict'],'RENDERED')
            self.assertEqual(json.loads(receipt.read_text())['visual_review'],'PENDING')
            def audio_hash(p):
                return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a','-c','copy','-f','hash','-'],text=True)
            self.assertEqual(audio_hash(video),audio_hash(out))
            reviewed['regions']=[{'start':0,'end':3,'box':[0,0,1,1]}]
            regions.write_text(json.dumps(reviewed))
            failed=run_burn()
            self.assertNotEqual(failed.returncode,0)
            self.assertIn('frozen',failed.stderr)
            self.assertEqual(json.loads(receipt.read_text())['verdict'],'FAIL')

class FacelessBottomTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
    def test_orientation_bottom_layout_without_region_maps_and_delivery(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); srt=root/'caps.srt'
            srt.write_text('1\n00:00:00,200 --> 00:00:01,200\nRain falls\n\n2\n00:00:01,300 --> 00:00:02,300\nOn the valley\n')
            for width,height in [(320,576),(576,320),(400,400)]:
                with self.subTest(size=(width,height)):
                    source=root/f'{width}x{height}.mp4'; final=root/'final.mp4'
                    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i',f'color=c=0x203040:s={width}x{height}:r=24:d=3','-f','lavfi','-i','sine=frequency=440:duration=3','-c:v','libx264','-c:a','aac','-shortest',str(source)],check=True)
                    command=[sys.executable,str(SCRIPTS/'subtitle_paper_burn.py'),'--in',str(source),'--srt',str(srt),'--out',str(final),'--style','bold','--no-caps','--font-key','montserrat','--profile','faceless']
                    result=subprocess.run(command,capture_output=True,text=True)
                    self.assertEqual(result.returncode,0,result.stderr)
                    layout=json.loads(Path(str(final)+'.captions.json').read_text())
                    self.assertEqual(layout['placement_mode'],'bottom_center')
                    boxes=[r['box'] for r in layout['placements']]
                    self.assertEqual(boxes[0][3],boxes[1][3])
                    for box in boxes:
                        self.assertAlmostEqual((box[0]+box[2])/2,.5,delta=1/width)
                        self.assertGreaterEqual(box[1],.60)
                        self.assertAlmostEqual(box[3],.83 if height>width else .90,delta=1/height)
                    def audio_hash(path):
                        return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a','-c','copy','-f','hash','-'],text=True)
                    self.assertEqual(audio_hash(source),audio_hash(final))
                    raw=subprocess.check_output(['ffmpeg','-v','error','-ss','0.5','-i',str(final),'-frames:v','1','-pix_fmt','gray','-f','rawvideo','-'])
                    ink=[i//width for i,pixel in enumerate(raw) if pixel>220]
                    self.assertTrue(ink)
                    self.assertGreaterEqual(min(ink),height*.60)
                    self.assertLessEqual(max(ink),height*(.83 if height>width else .90)+1)

if __name__=='__main__':unittest.main()
