# Review and fixes

## What to look at

- `qa/edit_NN.jpg`: one still per segment and per panel arrival (label `output-frame base+layers`), rendered exactly
  as the final.
- `edit_report.json`: `picks` (slot -> source window `sf`..`sf+n-1`, camera `cx cy z`, score, notes) and `warnings`.
- After render: `qa/cmp_NN.jpg` = pairs _reference | this render_ at the template QA frames, `qa/qa.json` checks.

Slot names and kinds are in `template/timeline.json` (`slots`); items (placements) name their slot (`items[id].slot`).
Where each slot shows up is mapped in `references/template.md`.

## fixes.json

```json
{
  "slots": {
    "eye": { "frame": 412 },
    "hero": { "frame": 120, "cx": 980, "cy": 520, "z": 1.1 }
  },
  "items": {
    "hero": { "look": "teal" },
    "fin1": { "zr": [1.0, 1.1] },
    "dark": { "expo": 1.2 }
  }
}
```

- `slots.<slot>.frame`: first source frame of the slot window (0-based, 30 fps of `shots/v0.mp4`: frame = s x 30).
  `cx`, `cy` (working-source px, `job.json` `size`), `z` (1 = the 16:9 cover crop) override the camera.
- `items.<item>`: `look` (`bw`, `bw_hard`, `bw_soft`, `teal`, `warm`, `violet`, `color`, `none`), `expo` (exposure
  factor), `zr` ([start, end] zoom relative to the slot camera), `sharp`, `tone` ([gain, gamma] instead of auto), and
  `cx` / `cy` / `z` for that placement only.
  Re-run `PB edit` (`--no-sheet` to skip sheets), then `PB render`. Two rounds at most; then deliver with one honest
  line.

## Finding frames

- Analysis stills: `web/ana/v0/NNNNN.jpg` (480 px, frame = seconds x 30). Look at a few around the time you want.
- `PB sheet "<job>" --f 7,117,287 --name check` renders plan stills of output frames.
- `features.json` `frames[i]`: `f` faces (bb, eyes), `y` mean luma, `m` motion, `hv/hx/hy` brightest spot,
  `hl` highlight fraction; `shots` = source cuts.

## Typical problems -> fix

| seen on the sheet                            | fix                                                                                                                                                            |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| frame 4 silhouette is a shapeless blob       | pin `open` to a moment where one person stands clear of the background                                                                                         |
| no person in the opening shot (7)            | pin `open` to a full-body / back-view moment                                                                                                                   |
| eye close-up (117) is a whole face or blurry | pin `eye` to the biggest frontal face; the report says "capped" when the source is too small                                                                   |
| someone else fills a face slot               | pin the slot (`facer`, `casB`, `casC`, `dark`, `fin3`, `fin4`) to a frame with the hero                                                                        |
| two panels of a cascade look the same        | pin one of `casA/casB/casC` (or `mcA/mcB/mcC`) elsewhere                                                                                                       |
| hero shot (59-102) is flat / tiny            | pin `hero` to the widest, most dramatic moment with light; it is 44 frames long                                                                                |
| black or credits frames                      | `PB init "<job>" --video "<file>" --max-dur <s> --force`, then `PB prep` and `PB edit` again (pins in `fixes.json` move if `--start` changes), or pin the slot |
| a shot too dark / too bright                 | `{"items": {"<id>": {"expo": 1.3}}}`                                                                                                                           |

## Clips that cannot match the template well

- No face at all (scenery, product): face slots fall back to centre crops and the frame-4 silhouette becomes a
  luminance key; say the edit is made for a person on camera.
- Very short clips (< 10 s): moments repeat (the report says "reuses footage"); suggest a longer clip.
- Several people: the largest face is the hero; pin slots if the scorer follows the wrong one.
- Low-resolution sources (720p and below): close-ups are soft; the eye ECU is capped.
