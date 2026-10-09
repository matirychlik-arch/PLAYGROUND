# Text overlay rules (hierarchy, contrast, safe zones)

Contents:
1. What makes headline text high-impact (the six-trait stack)
2. Hierarchy, word count, placement, safe zones
3. The 5 proven style presets as design specs
4. Font menu and stroke caveats
5. Three ways to deliver the text (baked in the image model, Figma/Photoshop, After Effects)
6. Pre-export check

Default policy: the generated image is clean (no text) and the headline is added as a
typographic layer on top, because a typographic layer is always legible and exactly
spelled. Bake text into the generation only on an explicit ask, or when the image model is
known to render the string reliably (Nano Banana Pro usually does; still verify).

## 1. What makes text high-impact

Not one trick but a stack of six; remove any one and it falls apart.

| Trait | Value | Why |
|---|---|---|
| Font | **Anton** (or Anton SC), one weight, reads 900-heavy | fat condensed grotesk, the signature |
| Case | **ALL CAPS** | maximum density and aggression |
| Stroke | manual, **thick** (8-14% of cap size), drawn UNDER the fill | separates letters from any background |
| Shadow | hard, dark, offset down, blur shifted | "sticker" depth |
| Color | white / yellow-orange-red gradient / acid lime `#D4FF3F` | punchy contrast, reads in the feed |
| Tracking | tight (-0.01 to -0.02em), line-height 0.9 | letters lock together like a logo |

The stroke must sit BEHIND the fill (Figma: stroke "Outside"; Photoshop: Stroke layer
style, position Outside; CSS: `paint-order: stroke fill`). A stroke painted on top eats half
of each letter, which is the most common bug in home-made big-bold text.

## 2. Hierarchy, word count, placement, safe zones

Hierarchy (one thing leads, the rest supports):
1. The face / hero element is read first (largest, highest contrast).
2. The headline is read second: ONE punch word or phrase, the biggest type in the frame.
3. A secondary tag (optional, e.g. "DAY 87", a number, an arrow label) is much smaller and never competes with the headline.
No third text element. A thumbnail with three competing text layers fails the 120px test.

Word count and size:
- **2-4 words max** (up to 6 only when a locked hook demands it). A headline, not a sentence.
- Cap height **12-18% of frame height** (about 86-130px on a 720px-tall frame, about 230-345px on 1920px-tall). When in doubt, bigger.
- The headline should complete the information gap with the title, never repeat the title.
- Polish text: keep diacritics (ą ć ę ł ń ó ś ź ż) and check the font supports them; Anton, Bebas Neue, Oswald, Archivo Black, Montserrat, Poppins, Inter all cover Latin Extended.

Placement:
- **Not on the face.** Put text in a free quarter (bottom, a side, a corner) chosen after looking at the render. Choose `top`, `bottom`, `left`, `right` or `center` so the headline occupies empty space.
- Keep a comfortable margin: at least 5% of the frame from every edge (about 64px at 1280 wide).
- Contrast: the text color must beat the background it sits on. If the area behind is busy, darken or blur that area (a soft dark gradient or the stroke) rather than shrinking the text. Use one punchy color per headline.

Safe zones (rules of thumb; platform UIs change, so check the current look on a phone):

| Format | Canvas | Keep clear |
|---|---|---|
| YouTube thumbnail | 1280x720 (16:9), upload under 2 MB | bottom-right corner (about 200x80px) where the video duration badge sits; small icons appear in the top-right corner on hover; keep the headline and face away from the outer 5% |
| Shorts / Reels / TikTok cover | 1080x1920 (9:16) | top about 12% (username, status), bottom about 25% (caption, buttons), right about 8% (action buttons); keep face and headline in the middle band |
| Instagram profile grid | 1080x1350 (4:5) or the centre crop of a 9:16 cover | the grid shows a centre crop, so keep the face and headline inside the centre 4:5 area (1080x1350) of a 9:16 cover |

Design the faces in the upper two-thirds on 9:16 and put the headline just under the face,
above the bottom caption zone.

## 3. The 5 proven style presets as design specs

Use the same recipe in any tool; values are for a 16:9 frame and scale with frame height.

### Beast (default): white fill + thick black stroke
- Fill `#FFFFFF`, stroke `#000000` at about 14px per 120px type (about 11% of cap size), stroke outside/behind.
- Shadow: hard offset 8px down at 35% black, plus a soft shadow 14px down, 24px blur, 55% black.

### Fire: yellow to orange to red gradient
- Fill: vertical gradient `#FFE24B` (0%) to `#FF9A1F` (45%) to `#FF2E2E` (100%).
- Stroke `#1A0A00` about 14px per 120px type, outside.
- Warm outer glow `rgba(255,120,0,.55)` about 22px, plus a hard dark offset shadow 10px down at 40%.

### Neon Lime: acid lime + glow
- Fill `#D4FF3F`, stroke `#0A1400` about 12px per 120px type, outside.
- Lime glow `rgba(180,255,40,.7)` about 26px, plus a hard dark offset shadow 10px down at 40%.

### Clean Glass: Inter ExtraBold (800) on a frosted pill
- White Inter 800, tracking -0.02em, no stroke.
- Behind the text: a rounded rectangle `rgba(20,20,25,.45)` with background blur about 16px, padding about 0.12em vertical and 0.5em horizontal, corner radius about 0.2em, soft shadow (20px down, 60px blur, 50% black).
- For calm or premium topics.

### Marker: black Anton on lime line-boxes
- Text `#0A0A0A` on solid `#D4FF3F` boxes behind each line (tight padding about 0.18em), hard shadow 8px down at 50%.
- Each line gets its own box, like highlighter marks.

## 4. Font menu (Anton is the default; these are the overrides)

A named font by the user wins. "Something else / not Anton": pick the closest fit below and
say which you chose. All are on Google Fonts.

**A. Top 3 on YouTube (punchy display, the Anton alternates)**

| Font | Weight | Vibe / use |
|---|---|---|
| Bebas Neue | 400 (reads bold) | tall narrow ALL-CAPS, the #1 Anton alternative, maximum cap height |
| Oswald | 600-700 | condensed grotesk, a touch softer than Anton |
| Archivo Black | 400 (ultra-bold) | blocky, wide, very loud headline |

**B. 5 most-used bold workhorses**

| Font | Weight | Vibe / use |
|---|---|---|
| Montserrat | 900 (Black) | clean geometric sans, modern headline |
| Poppins | 800 (ExtraBold) | rounded geometric, friendly |
| Roboto Condensed | 700 (Bold) | neutral condensed workhorse |
| Inter | 800 | modern UI sans (same face as the Clean Glass preset) |
| Barlow Condensed | 800 (ExtraBold) | condensed, energetic |

**C. 5 aesthetic (girls' vlogs / soft-elegant)**

| Font | Weight | Vibe / use |
|---|---|---|
| Playfair Display | 700-900 | elegant high-contrast serif, classic "aesthetic" title |
| Cormorant Garamond | 600-700 | delicate refined serif, editorial feel |
| DM Serif Display | 400 | high-end display serif |
| Fraunces | 600-900 | soft "old-style" serif, trendy |
| Sacramento | 400 (script) | handwritten script: ACCENT / secondary line only, never the hero word (a script fails the 120px legibility test as the main headline) |

Swapping a font keeps everything else (stroke, shadow, stroke order, tracking); only the
family and weight change.

**Stroke caveat by font class:** heavy condensed faces (Anton, Bebas Neue, Oswald, Archivo
Black) take the full 8-14% stroke. The delicate serifs and the script (Playfair, Cormorant,
DM Serif, Fraunces, Sacramento) clog with a thick stroke: drop it to 3-6% (or none) and lean on
a soft drop shadow for separation instead.

## 5. Three ways to deliver the text

**A. Bake it in the image model (Nano Banana Pro or any model that renders text well).**
Use when speed matters and the string is short. Put the exact string in quotes in the TEXT
contract (see prompt-blocks.md block 3), add the style as art direction (for example
`thick black outline, hard drop shadow, heavy condensed all-caps sans-serif, white fill`),
name the position (`bottom-left, away from the face`) and say `No other text, no watermark.`
After rendering, compare the rendered letters to the intended string character by character
(Polish diacritics are the usual failure). If it mismatches, re-render once or twice; if it
still fails, render a clean version and use route B.

**B. Typographic layer in Figma / Photoshop / Illustrator (deterministic, recommended for final).**
Place the clean render as the background, add the headline with the preset from section 3
(text layer, stroke outside, drop shadows as listed), position it in the free quarter, export
the native-resolution PNG or JPG. Exact spelling guaranteed, easy to A/B different headlines.

**C. After Effects / Premiere** when the cover is also an animated intro or a video frame:
build the same text layer there, and export a still frame for the thumbnail.

For the baked-in-model route write the spec like this, which doubles as the brief for B:

```
Headline: "<TEXT>" (2-4 words, ALL CAPS)
Style: Beast | Fire | Neon Lime | Clean Glass | Marker
Font: Anton (fallback Bebas Neue)
Position: bottom | top | left | right | center (free quarter, off the face)
Size: cap height ~16% of frame height
Colors: fill / stroke / shadow (from the preset)
```

## 6. Pre-export check

- [ ] Font Anton (or the chosen menu font), ALL CAPS, 2-4 words.
- [ ] Stroke thick and drawn under the fill (outside stroke).
- [ ] Text does not cover the face; sits in a free quarter.
- [ ] Text inside the safe zone, at least 5% from the edges, clear of the duration badge (16:9) or the UI bands (9:16).
- [ ] One punchy color per headline; contrast holds against the background.
- [ ] Spelling and diacritics match the intended string exactly.
- [ ] Reads at about 120px wide.
