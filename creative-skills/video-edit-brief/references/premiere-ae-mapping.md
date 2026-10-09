# Mapping the numeric recipe to Premiere Pro and After Effects

Contents
1. Project setup (frame base first)
2. Division of labour: what goes in Premiere, what goes in After Effects
3. Recipe element -> operation table
4. Expression snippets (After Effects)
5. Premiere-only techniques without expressions
6. Text and title animators
7. Audio hits, markers and mix
8. Export
9. Setup traps

Menu names move between versions. If a name differs in your version, search the Effects panel for the effect name given here. Where this file is unsure it says so.

## 1. Project setup

- Frame base before anything else: sequence/composition frame size, frame rate (24, 25, 30, 23.976 = 24000/1001, 29.97 = 30000/1001 non-drop), pixel aspect square. A recipe written in frames only works if the project runs at the recipe's fps.
- Show time as frames: Premiere: Source/Program monitor and timeline panel menu > Time Display Style or project settings > Timecode > Frames. After Effects: Project Settings > Time Display Style > Frames; Composition frame numbers start at 0 or 1 depending on Project Settings (Start Numbering Frames at 0 or 1). Use 0-based to match the recipe.
- Sequence length = planned frame count: set the comp duration/work area exactly; check the last frame number on export.
- Colour: SDR Rec.709 / sRGB workflow. Do not mix Log, HDR and Rec.709 in one timeline unless you convert on purpose.
- Keep one master timeline; build effects and complex titles in After Effects comps and bring them in as Dynamic Link or rendered clips (ProRes 4444 with alpha for graphics).

## 2. Division of labour

| Do in Premiere | Do in After Effects |
|---|---|
| cutting to the edit map, trimming, speed changes, audio sync and mix, markers on hits | camera keyframes with expressions, shake/punch/ladder, text animators, trim paths, tracking, roto, halftone and glitch looks, light leaks, grain with per-frame seed |
| adjustment-layer flashes and inverts (simple), Lumetri grades | complex strobe, behind-subject text, sticker/doodle layers, nested-panel cascades |
| final assembly and export | render graphics as an alpha clip when Premiere would be slow |

## 3. Recipe element -> operation

| Recipe element | Premiere Pro | After Effects |
|---|---|---|
| shot from f0 to f1 | razor at f0 and f1+1 (cut happens between frames); ripple delete; or Add Edit (Ctrl/Cmd+K) with playhead on the first frame of the new shot | Split Layer (Ctrl/Cmd+Shift+D) at the first frame of the new shot; or sequence layers (Animation > Keyframe Assistant > Sequence Layers) for stacked clips |
| source in-point | trim clip head to the in-point; check the exact frame in the Source monitor with frame display | slide the layer so the in-point sits at the shot start (Alt+[ trims the head to the playhead), or set it via Time Remapping |
| scale % keyframes | Effect Controls > Motion > Scale; Uniform Scale on; keyframe at f_a and f_b | Transform > Scale (S), keyframe; or Alt-click stopwatch for an expression |
| position / anchor | Motion > Position, Anchor Point (scale and rotation pivot around the anchor, not position) | Transform > Anchor Point (A) and Position (P); Pan-Behind tool moves the anchor without moving the layer |
| rotation | Motion > Rotation | Transform > Rotation (R); rotate on an oversized layer and mask or pre-comp (no-edge rule) |
| easing "out3" (fast start, soft stop) | right-click keyframe > Temporal Interpolation > Ease Out; adjust in the Effect Controls speed graph | select keyframes > F9 Easy Ease, then Graph Editor > Speed graph, or expression `out3` below; quadratic ~ Easy Ease Out at default influence, cubic ~ Ease Out with higher influence (about 70-80%) |
| hold / step keyframe (strobe, boil, stepped shake) | right-click keyframe > Temporal Interpolation > Hold | Animation > Keyframe Interpolation > Temporal > Hold, or Ctrl/Cmd+Alt+H |
| speed % | Clip > Speed/Duration; tick Ripple Edit | Layer > Time > Time Stretch; or Time Remapping (Ctrl/Cmd+Alt+T) with keyframes |
| speed ramp | right-click clip > Show Clip Keyframes > Time Remapping > Speed; add keyframes, drag the ramp handle | Layer > Time > Enable Time Remapping, keyframe, ease in the Graph Editor |
| frame blend vs nearest | clip > Time Interpolation: Frame Sampling (nearest), Frame Blending, Optical Flow. Use Frame Blending for 30-100% slow-mo; Frame Sampling below 30% or on fast limbs; Optical Flow can smear limbs and faces | Layer > Frame Blending (Frame Mix) with comp switch on; or the Timewarp effect: Method "Whole Frames" (nearest), "Frame Mix", "Pixel Motion" |
| stepped cadence 2,2,1 (18 fps in 30 fps) | no direct control; set the stepped look in After Effects and bring it in | precompose the stack, then add Effect > Time > Posterize Time with Frame Rate 18 on the precomp layer (works on the layer it sits on, not on layers beneath an adjustment layer) |
| freeze frame | clip > Add Frame Hold (or Frame Hold Options); choose the exact frame | Layer > Time > Freeze Frame (sets a hold time-remap) |
| stutter (loop 3 source frames) | duplicate the 3 frames and repeat; or nest and loop with Frame Hold on a repeating pattern | Time Remapping expression: `Math.floor(time/thisComp.frameDuration)%3 * thisComp.frameDuration + startFrameTime` |
| flash 60% -> 20% (first two frames) | V-track above: Color Matte (white) or a white Graphic, 2 frames long; Opacity keyframes 60% at f0, 20% at f1 with Hold. Or Adjustment Layer + Lumetri Exposure | White Solid (or adjustment layer + Exposure/Brightness), opacity keys 60 then 20 with Hold interpolation |
| solid white / black frame | cut in a Color Matte or Black Video for N frames; swap the flash colour with #F7FAFC where specified | Solid layer N frames long, Normal mode |
| strobe (alternate frames) | Effect > Video Effects > Stylize > Strobe Light (Strobe Duration, Strobe Period in seconds); or cut A/B clips manually in 2-frame blocks (use Add Edit and snap) | opacity expression on a white solid (section 4); or Effect > Stylize > Strobe Light; or two layers sharing one expression for A/B alternation |
| invert N frames | Adjustment Layer N frames long on the track above, with Effect > Video Effects > Channel > Invert (Channel RGB) | Adjustment Layer N frames long with Effect > Channel > Invert. An adjustment layer also inverts graphics beneath it, as the recipe requires |
| threshold / photocopy | Video Effects > Stylize > Threshold (keyframe Level); keep accent via Lumetri HSL Secondary or a second copy with Color Key | Effect > Stylize > Threshold, or Levels + Curves; accent: duplicate layer, Keylight/Color Range or HSL secondary on the copy |
| halftone | not native; pre-render in After Effects or Photoshop pattern overlay | Effect > Stylize > Color Halftone (Max Dot Radius about half the recipe cell size) |
| duotone / tint | Lumetri Color > Creative or Effect > Color Correction > Tint (Map Black To / Map White To) | Effect > Color Correction > Tint, Tritone, or Gradient Ramp with Color blend |
| hue shift (accent recolour) | Lumetri > Hue Saturation Curves > Hue vs Hue, or Effect > Color Correction > Color Balance (HLS) Hue | Effect > Color Correction > Hue/Saturation, Master Hue (degrees: red 0, orange 25, yellow 50, green 120, cyan 180, blue 220, purple 275) |
| blend modes (screen, add, multiply, overlay, soft light, darken, difference) | Effect Controls > Opacity > Blend Mode | Switches/Modes column (F4 to show), or Layer > Blend Mode |
| overlay opacity ramp | Opacity keyframes | Opacity (T) keyframes |
| light leak | stock leak clip on a track above, Blend Mode Screen (or Add), Opacity about 55%; levels so black stays black | same; or Fractal Noise gradient + Screen |
| film grain | stock grain clip, Blend Mode Overlay or Soft Light, opacity 20-40%; or Effect > Noise & Grain > Noise (Amount 5-10%) as an adjustment layer. | Effect > Noise & Grain > Add Grain / Noise, or Fractal Noise with a per-frame Evolution (section 4), Soft Light |
| vignette | Lumetri Color > Creative > Vignette (Amount negative to darken) | Lumetri Color vignette, or a black solid with an elliptical mask feathered, Multiply |
| softness / bloom / halation | Gaussian Blur 0.7-1.4 px for softness; bloom: duplicate, key highlights (Lumetri highlights up, or Levels), Gaussian Blur radius about 22, Screen at 35% | Gaussian Blur; Glow effect (Threshold about 60%, Radius about 22, Intensity per recipe) |
| RGB split | duplicate the clip on 3 tracks, keep one channel each (Effect > Channel > ... where available, or Lumetri RGB curves), Blend Mode Screen/Add, offset Position by the recipe px; or a third-party RGB-split preset | duplicate 3 times, Effect > Channel > Shift Channels (one channel each: other channels Full Off), Add mode, offset Position; decays by keyframing the offset |
| scanlines | overlay of 2 px dark lines every 4 px at 14% (PNG on a track, Multiply/Normal at 14%) | Effect > Generate > Grid/Stripes or Venetian Blinds on a solid; opacity 14% |
| mosaic / pixel blocks | Effect > Stylize > Mosaic (Horizontal/Vertical Blocks keyframed, e.g. 30 px -> 4 px over 3 frames: set blocks count = width / block size) | Effect > Stylize > Mosaic; same |
| glitch / slices | Displacement Map or Wave Warp on an adjustment layer for 4 frames; transition packs; or Offset effect keyed per frame | Effect > Distort > Displacement Map / Wave Warp; slices via Transform on strips; or fractal noise driving displacement |
| directional blur / whip | Effect > Blur & Sharpen > Directional Blur (Direction 0, Length 120 sin(pi k) + 10 px) on an adjustment layer; Position keyframes on both clips; Transform effect with Motion Blur | Directional Blur, or layer Motion Blur switch (shutter angle 180-360) with Position keyframes |
| shake (decaying) | Transform effect with Position keyed on each frame using the recipe amplitude, Hold interpolation, decaying values (see section 5) | `wiggle` expression with decay (section 4) |
| punch-in (decaying zoom) | Scale keyframes 106% -> 100% over 6 frames with Ease Out | scale expression (section 4) |
| zoom ladder [1, 1.12, 1.24, 1.36] | Scale keyframes with Hold interpolation at equal steps | scale expression with steps (section 4) |
| face-lock / eye pinning | no tracker for faces; track in After Effects and import the tracked clip | Tracker panel > Track Motion on the eyes (or Face Tracking) -> Null -> parent plate; or Stabilize Motion. Coordinates and whole-plate transforms only; never warp facial features |
| subject cut-out / behind-subject text | Duplicate clip on a track above the text; mask or track matte; or use a matte rendered in After Effects | Roto Brush (or a matte from a matting tool); order: plate, text, cut-out copy on top |
| outline / halo around cut-out | pre-render in After Effects | Stroke effect on the matte or Layer Style > Stroke/Outer Glow on the cut-out layer; Simple Choker to dilate |
| cascade / panels / split screen | nested sequences or clips with Crop and Position keyed, feather 0 | precomps with masks; scale and position keys 3-5 frames apart |
| letterbox bars | Effect > Transform > Crop (Top/Bottom % keyed) on the adjustment layer | two black solids or a Crop effect |
| light-beam / flare | stock flare Screen; or Lens Flare effect (Premiere Video Effects > Generate > Lens Flare) | Effect > Generate > Lens Flare, or Optical Flares plugin; soft gaussians per recipe |
| exposure match to a reference | Lumetri Color > Basic Correction and Curves; compare with the Lumetri Scopes (Waveform, Histogram) | Levels/Curves with the Histogram; match luma mean and standard deviation to the recipe |
| time-aligned sticker pop (scale 1.4, .9, 1.05, 1) | Scale keyframes on 4 consecutive frames (Hold or Linear) | same, or Position/Scale Sequence Layers |

## 4. Expression snippets (After Effects)

Use them as written; adjust the constants. `timeToFrames()` returns the frame number of the current time.

Strobe on a white solid: one frame on every P frames (set P).

```javascript
// Opacity of a white solid: on for 1 frame out of every P frames
P = 2;
f = timeToFrames(time);
(f % P == 0) ? 100 : 0;
```

Two-shot alternation (A/B every 2 frames) on opacity, for A (invert for B):

```javascript
// Opacity: A on for 2 frames, B on for the next 2 (put on A; B uses 100 - A)
block = 2;
f = timeToFrames(time - inPoint);
(Math.floor(f / block) % 2 == 0) ? 100 : 0;
```

Flash decay (e.g. 60% -> 20% -> 0 over the first three frames of the layer):

```javascript
f = timeToFrames(time - inPoint);
steps = [60, 20, 0];
f >= 0 && f < steps.length ? steps[f] : 0;
```

Decaying shake from the cut (position):

```javascript
// amp in px, decay per second, freq in Hz (set near the fps for per-frame jitter)
amp = 16; decay = 12; freq = 24;
t = time - inPoint;
t < 0 ? value : wiggle(freq, amp * Math.exp(-t * decay));
```

Stepped (boil) wiggle: the offset changes every n frames:

```javascript
n = 2; // frames per boil step
tq = Math.floor(timeToFrames(time) / n) * n * thisComp.frameDuration;
wiggle(8, 6, 1, 0.5, tq);   // freq, amp, octaves, amp_mult, time
```

Punch-in (scale %, decays like exp(-12 t); 6% at the cut):

```javascript
amp = 0.06; k = 12;
t = Math.max(0, time - inPoint);
s = 100 * (1 + amp * Math.exp(-k * t));
[s, s];
```

Out-cubic ease between two values over a duration from the layer start:

```javascript
d = 0.5;                       // seconds
t = Math.min(1, Math.max(0, (time - inPoint) / d));
e = 1 - Math.pow(1 - t, 3);    // out-cubic
a = 100; b = 112;              // start and end scale %
s = a + (b - a) * e;
[s, s];
```

Zoom ladder:

```javascript
steps = [100, 112, 124, 136];
n = steps.length;
p = (time - inPoint) / (outPoint - inPoint);
i = Math.min(n - 1, Math.max(0, Math.floor(p * n)));
[steps[i], steps[i]];
```

No-edge scale guard (never let a moved or rotated layer show its edge). Put on Scale; compositions at layer anchor centre:

```javascript
W = thisComp.width; H = thisComp.height;
p = transform.position;
dx = Math.abs(p[0] - W / 2); dy = Math.abs(p[1] - H / 2);
rot = Math.abs(transform.rotation);
minS = 100 * (1 + 2 * dx / W + 2 * dy / H + 0.04 * rot);
s = Math.max(value[0], minS);
[s, s];
```

Per-frame grain evolution (Fractal Noise, set Evolution):

```javascript
Math.floor(timeToFrames(time)) * 37;   // new pattern every frame, deterministic
```

Stutter of 3 source frames from the in-point (Time Remap):

```javascript
fd = thisComp.frameDuration;
inP = 0;                       // source time of the in-point
inP + (Math.floor(timeToFrames(time - inPoint)) % 3) * fd;
```

Typewriter on Source Text (about 2 frames per letter):

```javascript
txt = "NOVA FILM";
fpl = 2;                                  // frames per letter
n = Math.max(0, Math.floor(timeToFrames(time - inPoint) / fpl) + 1);
txt.substring(0, n);
```

Slam scale (130, 90, 106, 100 over 4 frames), on Scale:

```javascript
f = timeToFrames(time - inPoint);
steps = [130, 90, 106, 100];
s = f < 0 ? 0 : (f < steps.length ? steps[f] : 100);
[s, s];
```

Audio-driven strobe: select the audio layer > Animation > Keyframe Assistant > Convert Audio to Keyframes; link opacity of the flash to the Both Channels > Slider with `linear(thisComp.layer("Audio Amplitude").effect("Both Channels")("Slider"), 0, 20, 0, 100)`. Use only for a rough first pass; hit-by-hit frames from the hit table are more exact.

Sine-eased pulse after a background flip (+1.2% pulse for 3 frames):

```javascript
t = time - inPoint; s = 100 * (1 + 0.012 * Math.exp(-t * 20)); [s, s];
```

## 5. Premiere-only techniques without expressions

- Decaying shake: a Transform effect with Position keyframes on frames 0, 1, 2, ... of the hit, Hold interpolation, with amplitudes taken from a decay table, e.g. 16, 11, 7, 5, 3, 2, 1, 0 px (alternate signs and axes). Copy and paste the keyframes onto other hits.
- Flash stacks: a nested sequence "FLASH" containing a white Color Matte; place instances at the hit frames and set Opacity keyframes per instance.
- Many strobe frames: make the A/B alternation by cutting both clips into 2-frame pieces with Add Edit on a grid (snap on), or use Strobe Light for a flash-only strobe.
- Inverts and flashes on an adjustment layer: keep a library of N-frame adjustment layer clips (1, 2, 5 frames) and drop them on hit markers.
- Speed ramps: Time Remapping Speed keyframes; keep ramps on separate clips, not under flashes, so the cut timing stays readable.
- Bake and replace: complex things (halftone, glitch, RGB split, cascades) are faster rendered once in After Effects as an alpha ProRes and placed on a track.

## 6. Text and title animators

| Title element | Premiere Pro | After Effects |
|---|---|---|
| text layer | Essential Graphics > Text (or Type tool); Responsive Design - Time to keep intro/outro lengths when stretched | Type tool; Character panel for tracking (in 1/1000 em) |
| position / size envelope | Transform in Essential Graphics (Position, Scale) with the frame % from the title table | Transform > Position and Scale in comp units; use guides at the safe margins (View > Show Grid / Rulers) |
| fade in 2 frames | Opacity 0 -> 100 over 2 frames | Opacity keys |
| pop / slam (scale overshoot) | Scale keyframes 130, 90, 106, 100 over 4 frames | slam expression (section 4) or keyframes |
| typewriter per letter | Essential Graphics: text keyframing is limited; use the Text Animator in AE or the Type-on preset | Text > Animate > Opacity (Range Selector Start 0%, set Opacity 0%, keyframe Offset or Start from 0 to 100%), Based On Characters; Advanced > Shape Ramp Up; or Source Text expression above |
| per-letter stagger | not native; use AE | Animator: Position/Scale/Opacity with Range Selector Offset keyed; Advanced > Randomize Order for chaotic pops; Smoothness 0% for hard steps |
| letter vanish with flicker | not native; use AE | Animator Opacity with Range Selector and Wiggly selector (Wiggles/Second 12, Correlation 0) |
| word by word | stack three text clips: word 1, words 1-2, words 1-3, one per beat | Source Text keyframes with Hold interpolation (word 1, then the longer strings) |
| write-on (handwritten) | not native; use AE | Create Shapes from Text, then Add > Trim Paths with keyed End, or Stroke with Trim Paths |
| text behind subject | track order: footage (V1), text (V2), cut-out copy (V3) with a matte | text layer between the plate and the roto-matted copy of the plate |
| parallax words | separate text clips with different Position speeds (e.g. one at x1.8) | separate layers, Position keyed with different travel; or 3D layers with a camera |
| tracking (letter spacing) animation | not native; use AE | Animator > Tracking Amount keyed (negative numbers pull letters together) |
| blur to sharp | Gaussian Blur 14 -> 0 over 0.12 s | same |
| smear out | Directional Blur (vertical) keyed to rise over the last 2 frames | same |
| outline / echo | Stroke and Shadow in Essential Graphics; duplicate the text with an offset and a different fill | Stroke and Fill in Character panel; duplicate layer with offset and Tint |
| ink / boil | not native | Turbulent Displace (Amount 1-2 px) with Evolution stepped every 2 frames (hold keyframes or the stepped expression in section 4) |
| colour that inverts with the background | Blend Mode Difference with white text (appears as the opposite of the underlying pixels) | same: text layer Mode Difference, white fill |

Rules for editors: set the title table's position in % and convert to pixels once; fonts must contain the glyphs (check Polish letters before animating, an Adobe Fonts entry may substitute silently); export titles with alpha only if you need to stack on a changed grade.

## 7. Audio hits, markers and mix

- Import the track, scrub with the waveform zoomed in until you see the transient, press M to put a marker on the exact frame of each hit. Name markers with the hit id (H01...). Turn on Snap (S in Premiere; Shift-drag snaps in AE) so clips and effects land on markers.
- If cuts need to lead the beat by about 2 frames, move the video edit, not the audio.
- Beat grid: set sequence markers at every beat: beat k at (phase + k x 60 / bpm) seconds; at 120 BPM and 30 fps a beat is exactly 15 frames; at 139.6 BPM and 30 fps it is 12.9 frames, which drifts: place markers by time, not by repeating a frame count.
- Premiere: Audio Track Mixer / Essential Sound for ducking (-6 to -7 dB under speech), Hard Limiter or Dynamics for the ceiling, Loudness Radar or Loudness Meter for integrated loudness. True peak on the encoded file: confirm with an external measurement (ffmpeg `ebur128=peak=true`).
- Place SFX on dedicated tracks, each on its hit marker; trim to the transient; gain about -4 dB relative to music as a start (0.6 amplitude).
- Silence is a choice: black frames with no audio for a planned end (6 frames of black at the end of a strobe edit).

## 8. Export

- Premiere/Media Encoder: H.264, match sequence settings, VBR 2-pass, target 12-20 Mbps for 1080x1920 or 1920x1080 short-form (Media Encoder has no CRF; for a CRF 18 master transcode a high-quality intermediate with ffmpeg: `ffmpeg -i master.mov -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -movflags +faststart -c:a aac -b:a 256k out.mp4`).
- After Effects: render to ProRes (4444 with alpha for graphics, 422 HQ for finished plates), or via Media Encoder.
- Keep the master. Make a smaller social copy if grain makes the file huge.
- After export, decode and count the frames; check audio sync on the first hit and the last; run the QA checklist.

## 9. Setup traps

- 23.976 vs 24 vs 25 mismatch silently drops or repeats frames; match the footage or accept a conversion on purpose.
- Frame blending / optical flow on the wrong clips makes ghosts; set it per clip.
- Drop-frame timecode is a display convention; the frame count is unaffected, but 29.97 DF seconds do not equal clock seconds.
- Nested sequences/precomps change the apparent order of effects; put the finish (grain, vignette) on the top-level adjustment layer so it covers graphics.
- Scale above 100% on low-resolution plates softens them; use the plate's native size (zoom headroom) and cap zoom so a source pixel enlarges at most about 3x.
- Time Remapping + keyframe easing can overshoot the clip end and hold the last frame; check the last frame of every retimed clip.
- An adjustment layer's effect applies to everything beneath, including graphics: exactly right for invert and RGB split; wrong for a look that must not touch titles (put titles above).
- AE `wiggle` is deterministic for a given layer and property, so a re-render repeats; do not call `random()` without `seedRandom(index, true)`.
