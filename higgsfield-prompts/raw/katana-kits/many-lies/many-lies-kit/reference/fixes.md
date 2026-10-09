# Review and fixes

## What to look at
- `qa/edit_NN.jpg`: one still per template shot (label `output-frame shot-id`), rendered exactly as the final.
- `edit_report.json`: `picks` (slot -> source window `sf`..`sf+n-1`, camera `cx cy z`, score, notes) and `warnings`.
- After render: `qa/cmp_NN.jpg` = pairs *reference | this render* at the template QA frames, `qa/qa.json` checks.

Slot names are in `template/timeline.json` (`slots`, each with `kind` and a note). Shot ids map to slots there
too (`shots[].slot`). The strobe is `s0..s8` (even = `strA`, odd = `strB`).

## Typical problems -> fix
| seen on the sheet | fix in `<job>/fixes.json` |
|---|---|
| wrong person / someone else in a close-up | pin the slot to a frame with the hero: `{"slots": {"tell": {"frame": 412}}}` |
| two neighbouring shots look the same | pin one of them elsewhere |
| face cut by the crop, too tight / too loose | `{"slots": {"watch": {"frame": 86, "cx": 980, "cy": 420, "z": 2.2}}}` (source px of `web/src/v0`, z >= cover) |
| a colour-pop shot shows random red patches | `{"shots": {"hero1": {"g": "bw"}}}` |
| a shot too dark | `{"shots": {"stack": {"gamma": 0.8}}}` |
| finale is not someone leaving | pin `back` to the clip's best turn-away / walk-out moment |

To find frames: `ML sheet "<job>" --f ...` renders plan stills; for raw source frames read
`web/ana/v0/NNNNN.jpg` (480 px, 0-based, 24 fps: frame = seconds x 24). Re-run `ML edit` (no sheet:
`--no-sheet`), then `ML render`. Two rounds at most; then deliver with one honest line.

## Clips that cannot match the template well
- no face at all (scenery, product): every face slot falls back to centre crops; tell the user the edit is made
  for a person on camera.
- very short clips (< 8 s): moments repeat (the report says "reuses footage"); suggest a longer clip.
- several people: the largest face is the hero; pin slots if the scorer follows the wrong one.
