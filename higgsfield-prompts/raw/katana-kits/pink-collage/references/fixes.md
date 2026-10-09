# Review and fixes

## What to look at

- `qa/edit_A.jpg`, `qa/edit_B.jpg`: one still per main beat (label `output-time phrase slot`), rendered exactly as
  the final. Template slot -> cast keys it shows: drop -> `drop`, poster -> `poster`, photo -> `photo`, collage ->
  `col_frame` (framed photo) + `col_cut` (cut-out sticker), square / closeup -> `square`, card1 -> `card1`,
  card2 -> `card2` (+ card1 behind), textcu -> `text_cu`, nametype / namebold -> `name_bg`, close1 -> `close1`,
  rack -> `rack`, oval -> `oval_bg` (blurred background) + `oval_cut` (cut-out in the mirror), face -> `face`,
  inset -> `face` + `inset`, collage2 -> `face2` (centre) + `face3` (bottom left) + `inset2` (top right).
- `edit_report.json`: `heroes`, `people` (identity #, samples, first appearance), `picks[A|B][key]` (`t` = source
  seconds, framing `cx cy zoom` or `cx cy w h` or `box`, score, notes) and `warnings`.
- Raw source frames to pick from: `PC src "<job>" --t0 8 --t1 12 --every 0.25` -> `qa/src_v0.jpg` (labels = source s).
- After render: `qa/cmp_NN.jpg` = pairs template | render, `qa/qa.json`.

## fixes.json

```json
{
  "heroes": { "A": 0, "B": 0 },
  "A": { "text_cu": { "t": 8.4 }, "oval_cut": { "t": 12.1, "box": [600, 0, 1400, 1080] } },
  "B": {
    "close1": { "t": 20.9, "cx": 980, "cy": 420, "zoom": 1.6 },
    "face": { "t": 21.3, "w": 520, "h": 520 }
  }
}
```

- `t` pins the slot's start (source seconds; the slot plays from there, so stay inside one shot).
- `cx`, `cy` (source px of `src/v0.mp4`, short side 1080), `zoom` (shot slots, relative to fit-height, >= cover),
  `w`, `h` (crop slots), `box` (cut-out slots: segmentation box), `y_cut` (`col_cut`: where the sticker is cut off)
  override the framing computed for that moment.
- `heroes` picks which identity stars in each phrase (`people` in the report).

## Typical problems -> fix

| seen on the sheet                                          | fix                                                                                |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| someone else in a face beat                                | pin `t` to a moment with the hero, or set `heroes`                                 |
| another person's body in the drop / collage / oval cut-out | pin the slot to a moment where the hero stands alone, or narrow `box`              |
| face cut by a frame, too tight / too loose                 | `cx`/`cy` and `zoom` (shots) or `w`/`h` (crops)                                    |
| two neighbouring beats look the same                       | pin one of them elsewhere                                                          |
| soft, mushy close-ups                                      | the clip has only small faces; pin to the largest-face moments, say so to the user |
| a beat starts on a different shot than it ends             | move `t` earlier / later so the window stays inside one shot                       |

Re-run `PC edit` (`--no-sheet` to skip the stills), check the sheets, then `PC render`. Two rounds at most; then
deliver with one honest line.

## Clips that cannot match the template well

- no person on camera: every face beat falls back to centre crops and the cut-outs fail; tell the user the edit is
  made for a person on camera.
- the hero is on screen only a few seconds: moments repeat (warning); suggest a longer clip or a second clip.
- very wide shots only: close-ups hit the 2.2x upscale cap and look soft.
