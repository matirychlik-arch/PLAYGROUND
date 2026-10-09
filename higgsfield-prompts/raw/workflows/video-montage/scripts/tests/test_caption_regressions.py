"""Offline caption regressions: supplied geometry, words and actual rendered pixels.

Synthetic boxes are known ground truth, not a test of automatic face recognition.
STT words are fixed input; these tests do not measure recognition accuracy.
"""
import json
import contextlib
import io
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import audio_to_captions as audio
import subtitle_paper_burn as burn
from caption_evidence import prepare, sha256
from caption_placement import intersects, place

FONT = str(SCRIPTS / 'fonts/Montserrat-ExtraBold.ttf')


class TranscriptRegressionTests(unittest.TestCase):
    def test_repeated_words_numbers_brands_and_russian_survive_roundtrip(self):
        tokens = ['Medicube', '50', 'ml,', 'very', 'very', 'nice.', 'Крем', '50', 'мл.', 'Да,', 'да.']
        words = [{'word': word, 'start': .5+i*.3, 'end': .7+i*.3}
                 for i, word in enumerate(tokens)]
        with tempfile.TemporaryDirectory() as td:
            srt=Path(td)/'caps.srt'
            srt.write_text(audio.to_srt(audio.group_captions(words)),encoding='utf8')
            parsed=burn.parse_srt(srt)
            self.assertEqual(' '.join(row[2] for row in parsed).split(),tokens)
            self.assertEqual(parsed[0][0],.5)
            self.assertAlmostEqual(parsed[-1][1],3.7)

    def test_silence_and_clip_boundaries_do_not_join_phrases(self):
        words=[{'word':'Hello','start':.4,'end':.8},
               {'word':'again','start':.8,'end':1.1},
               {'word':'Next','start':3,'end':3.4},
               {'word':'scene','start':3.4,'end':3.8}]
        grouped=audio.group_captions(words)
        self.assertEqual([(c['start'],c['end']) for c in grouped],[(.4,1.1),(3,3.8)])
        self.assertEqual(audio.group_captions([]),[])

    def test_invalid_srt_block_never_silently_drops_spoken_words(self):
        good='1\n00:00:00,100 --> 00:00:01,000\nKeep me\n'
        for bad in ['2\nmalformed time\nLost words',
                    '2\n00:00:60,000 --> 00:00:62,000\nLost words',
                    '2\n00:00:01,000 --> 00:00:02,000\n',
                    '2\n-00:00:01,000 --> 00:00:02,000\nLost words']:
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as td:
                p=Path(td)/'caps.srt';p.write_text(good+'\n'+bad)
                with self.assertRaises(ValueError):burn.parse_srt(p)

    def test_unrelated_authored_script_is_rejected(self):
        with self.assertRaises(ValueError):
            audio.align_words_to_script([{'word':'hello','start':0,'end':1}],['unrelated','advertisement'])


class LayoutRegressionTests(unittest.TestCase):
    def overlay(self,width,height):
        image=Image.new('RGBA',(width,height))
        ImageDraw.Draw(image).rectangle((width*.2,height*.72,width*.8,height*.75),fill='white')
        return image

    def test_moving_faces_product_and_existing_step_text_are_all_protected(self):
        regions=[{'start':0,'end':1,'box':[0,.65,.48,.92]},
                 {'start':1,'end':2,'box':[.45,.6,1,.9]},
                 {'start':0,'end':2,'box':[.2,.78,.75,.98]},
                 {'start':0,'end':2,'box':[.1,.10,.9,.20]}]
        _,box=place(self.overlay(1080,1920),.5,1.5,regions)
        # The cue spans the cut; neither face may be covered, nor the product/Step N.
        for region in regions:self.assertFalse(intersects(box,region['box'],.015))

    def test_safe_area_and_stability_in_portrait_landscape_and_square(self):
        for width,height in [(1080,1920),(1920,1080),(1080,1080)]:
            with self.subTest(size=(width,height)):
                image=self.overlay(width,height)
                _,a=place(image,0,1,[]);_,b=place(image,1,2,[])
                self.assertEqual(a,b)
                side=.11 if height>width else .075
                self.assertGreaterEqual(a[0],side)
                self.assertLessEqual(a[2],1-side)
                self.assertGreaterEqual(a[1],.1)
                self.assertLessEqual(a[3],.83 if height>width else .90)

    def test_entire_paper_plate_and_shadow_clear_the_subject(self):
        font=ImageFont.truetype(FONT,36)
        overlay=burn.paper_label('Rain comes home',font,720,1280,.17,.7)
        protected={'start':0,'end':2,'box':[.2,.62,.8,.9]}
        moved,box=place(overlay,0,1,[protected])
        self.assertFalse(intersects(box,protected['box'],.015))
        self.assertEqual(np.asarray(overlay)[:,:,3].sum(),np.asarray(moved)[:,:,3].sum())

    def test_long_word_cannot_force_font_below_readable_floor(self):
        draw=ImageDraw.Draw(Image.new('RGBA',(10,10)))
        with self.assertRaises(ValueError):
            burn.bold_fit_size(draw,['W'*150],FONT,50,700,min_size=38,single_line=True)

    def test_overflow_cannot_silently_truncate_a_third_line(self):
        font=ImageFont.truetype(FONT,48)
        with self.assertRaises(ValueError):
            burn.bold_label('one two three four five six seven eight nine ten',font,320,576,.17,.4)

    def test_missing_explicit_font_fails_instead_of_substituting_silently(self):
        with self.assertRaises(OSError):
            burn.font_for_text('/definitely-missing-caption-font.ttf','montserrat',['Hello'])


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
class RenderRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.video=self.root/'clean.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=0x456789:s=320x576:r=24:d=2',
                        '-f','lavfi','-i','sine=frequency=500:duration=2','-c:v','libx264','-c:a','aac',str(self.video)],check=True)
        self.srt=self.root/'caps.srt';self.out=self.root/'out.mp4';self.regions=self.root/'regions.json'
        self.srt.write_text('1\n00:00:00,250 --> 00:00:00,750\nHello there\n\n2\n00:00:01,250 --> 00:00:01,750\nПривет мир\n')
        self.regions.write_text(json.dumps({'video_sha256':sha256(self.video),'reviewed_duration':2,
            'reviewed_intervals':[{'start':0,'end':2}],'regions':[]}))

    def render(self,*extra):
        import caption_guard as guard
        receipt=self.root/'region-review.json'
        with patch.object(guard,'STATE_ROOT',self.root/'state'):
            if self.srt.exists():
                guard.reserve_regions(self.video,sha256(self.regions))
                guard.prepared(self.video,'synthetic-blue-fixture')
                approval={'verdict':'REGIONS_REVIEWED', 'review_view':'source_boxes_unprotected','video_sha256':sha256(self.video),
                          'srt_sha256':sha256(self.srt),'regions_sha256':sha256(self.regions),
                          'evidence_sha256':'synthetic-blue-fixture'}
                guard.approve(self.video,approval);receipt.write_text(json.dumps(approval))
            args=['burn','--in',str(self.video),'--srt',str(self.srt),'--out',str(self.out),
                  '--style','bold','--font-key','montserrat','--no-caps','--profile','safe',
                  '--protected-regions',str(self.regions),'--region-review',str(receipt),*extra]
            try:
                with patch.object(sys,'argv',args), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    burn.main()
                return SimpleNamespace(returncode=0,stderr='')
            except (ValueError,OSError,SystemExit) as error:
                return SimpleNamespace(returncode=1,stderr=str(error))

    def test_actual_pixels_show_both_languages_only_inside_cue_windows(self):
        result=self.render();self.assertEqual(result.returncode,0,result.stderr)
        raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(self.out),'-f','rawvideo','-pix_fmt','rgb24','-'])
        frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,576,320,3)
        # Uniform source: white caption ink is independent evidence from the sidecar.
        for index in [0,5,18,24,29,42,47]:
            self.assertLess(np.mean(np.all(frames[index]>210,axis=2)),.0001)
        for index in [6,12,17,30,36,41]:
            self.assertGreater(np.mean(np.all(frames[index]>210,axis=2)),.0002)
        self.assertEqual(len(frames),48)
        def audiohash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a','-c','copy','-f','hash','-'])
        self.assertEqual(audiohash(self.video),audiohash(self.out))

    def test_explicit_paper_profile_renders_and_preserves_cue_text(self):
        result=self.render('--style','paper','--font-key','caveat')
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(Path(str(self.out)+'.captions.json').read_text())
        self.assertEqual([r['text'] for r in data['placements']],['Hello there','Привет мир'])
        self.assertEqual(data['verdict'],'RENDERED')

    def test_failed_font_and_bad_timing_invalidate_old_render_receipt(self):
        for extra,source in [(['--font','/missing-caption-font.ttf'],self.srt.read_text()),
                             ([], '1\n00:00:01,000 --> 00:00:00,500\nBackwards\n')]:
            with self.subTest(extra=extra):
                receipt=Path(str(self.out)+'.captions.json');receipt.write_text('{"verdict":"RENDERED"}')
                self.srt.write_text(source)
                result=self.render(*extra)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(json.loads(receipt.read_text())['verdict'],'FAIL')
                self.assertTrue(self.video.exists())

    def test_missing_transcript_does_not_render_or_approve_old_output(self):
        receipt=Path(str(self.out)+'.captions.json');receipt.write_text('{"verdict":"RENDERED"}')
        self.srt.unlink()
        result=self.render()
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(self.out.exists())
        self.assertEqual(json.loads(receipt.read_text())['verdict'],'FAIL')

    def test_too_long_caption_or_tiny_requested_font_is_rejected(self):
        normal=self.srt.read_text()
        for text,extra in [(normal,['--fontsize-frac','0.001']),
                           ('1\n00:00:00,250 --> 00:00:01,750\n'+'W'*150+'\n',[])]:
            with self.subTest(extra=extra):
                self.srt.write_text(text)
                result=self.render(*extra)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('minimum readable',result.stderr)
                self.assertFalse(self.out.exists())

    def test_render_refuses_to_overwrite_clean_source(self):
        before=sha256(self.video)
        self.assertNotEqual(self.render('--out',str(self.video)).returncode,0)
        self.assertEqual(sha256(self.video),before)

    def test_evidence_selects_visible_frames_at_cut_and_last_frame(self):
        result=self.render();self.assertEqual(result.returncode,0,result.stderr)
        data=prepare(self.out,self.srt,self.root/'evidence')
        for row in data['samples']:
            start,end,_=burn.parse_srt(self.srt)[row['cue']]
            self.assertGreaterEqual(row['frame_time'],start)
            self.assertLess(row['frame_time'],end)
            with Image.open(self.root/'evidence'/row['frame']) as im:
                self.assertGreater(np.mean(np.all(np.asarray(im)>210,axis=2)),.0002)


if __name__=='__main__':unittest.main()
