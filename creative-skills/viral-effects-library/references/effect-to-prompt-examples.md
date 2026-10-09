# Effect to prompt: worked examples

Contents:
1. How these were built (constructed examples, not catalog text)
2. Vanish (hook)
3. Eyes in (transition)
4. Floating fall (product)
5. Frozen in motion (surreal)
6. Selfie twin (hook, Chinese copy for Seedance 2)
7. A 3-clip hook sequence with handoff table

## How these were built

The catalog description supplies the idea; everything else follows the 7-slot recipe in SKILL.md (subject lock, start state, action beats, camera, end state, format, avoid). The prompts below are constructed for this library, not copied from a catalog, so adjust names, outfits and products. Each was written for a 5 s, 9:16 clip unless stated.

## Vanish (hook)

Catalog: "The subject's body instantly disappears, leaving their empty clothing to suddenly collapse and fall flat onto the ground."

```text
A woman in her late twenties with shoulder-length dark hair, wearing an oversized beige trench coat, white sneakers and a small black crossbody bag, stands still in the middle of an empty sunlit city sidewalk, facing the camera. Same person and same outfit throughout.
0-2 s: she stands calmly, hands in her coat pockets, breeze moves the coat slightly.
2-2.5 s: her body disappears instantly, with no smoke and no flash.
2.5-4 s: the empty coat, sneakers and bag collapse straight down and lie flat on the pavement, the sleeves loosely crumpled.
The camera is locked at eye level on a tripod, medium-wide framing, no movement.
The final second holds on the empty clothes on the pavement, nothing moves.
Vertical 9:16, 5 seconds, natural daylight, no text, no captions, no watermark.
```
Negative: ghost outline, transparent body, smoke, extra people, morphing clothes, face visible after 2.5 s.

Edit notes: cut on the frame the clothes land; add a short impact sound in the editor.

## Eyes in (transition)

Catalog: "The camera dives directly into the subject's eye, seamlessly passing through the dark void of the pupil to transport the viewer into an entirely new scene."

```text
Extreme close-up of a young man's face, his eye filling the frame, soft window light, shallow depth of field. Same face and same eye color throughout.
0-1 s: he blinks once slowly and looks straight into the lens.
1-3 s: the camera pushes forward into the eye, past the iris, into the black pupil until the frame is fully black.
3-5 s: from the black, the camera emerges into a bright rooftop terrace at sunset, wide shot, no person visible yet, warm orange light.
One continuous forward camera move, steady speed, no cuts.
The final second holds on the rooftop terrace, still.
Vertical 9:16, 5 seconds, no text, no captions, no watermark.
```
Negative: second eye, warped iris, cut to another shot, flash frame, text.

Handoff: end state is "rooftop terrace at sunset, wide, empty" so the next clip can start from the last frame.

## Floating fall (product)

Catalog: "Falls backward as their belongings float in midair, with the camera moving through crisp product close-ups before the fall resumes."

```text
A young woman in a denim jacket falls backward in slow motion onto a pale studio floor. Her belongings float in midair around her: a white sneaker, a tube of hand cream with the readable label "VELA", sunglasses and a paper coffee cup. Same woman and same product shape and label throughout.
0-1.5 s: she tips backward, hair lifting, items drifting up from her bag.
1.5-3.5 s: the fall pauses in zero gravity; the camera glides past the hand cream tube in a crisp close-up so the label "VELA" is sharp and legible, then past the sneaker.
3.5-5 s: the camera pulls back, gravity resumes, she continues the fall as the items drift down.
Smooth continuous camera move, shallow depth of field, soft bounce light.
The final second holds on a clean frame with the hand cream tube centered and in focus.
Vertical 9:16, 5 seconds, silent, no extra text, no captions, no watermark.
```
Negative: changed label text, duplicate products, extra limbs, melting objects, hands holding the product.

Why this works: the product moment is a camera pass with a named end focus, so the label stays legible even if the body motion is loose. If the label warps, regenerate with a shorter fall and a longer product pass, or replace the label in the editor.

## Frozen in motion (surreal)

Catalog: "The subject freezes in midair while pedestrians and traffic continue moving naturally around them."

```text
A man in a red bomber jacket jumps in the middle of a busy crosswalk in a European city street. Same man and same jacket throughout.
0-1 s: he jumps, both feet leaving the ground.
1-4 s: he stays frozen in midair, knees bent, arms out, expression fixed, hair and jacket perfectly still. Pedestrians walk past him and cars and a tram keep moving normally in the background.
The camera is locked at eye level, wide framing, no movement.
The final second holds, the man still frozen, background still moving.
Vertical 9:16, 5 seconds, daylight, no text, no captions, no watermark.
```
Negative: everyone frozen, whole frame paused, slow motion of the background, blurred man.

Key line: name what is frozen and what keeps moving; the contrast is the effect.

## Selfie twin (hook, with Chinese copy)

Catalog: "A second, identical version walks in, sits down, takes a selfie, and vanishes."

```text
A woman with a long brown ponytail in a green hoodie sits on a living-room sofa and looks at the camera. Same woman and same hoodie throughout.
0-1.5 s: an identical second version of her walks into frame from the left.
1.5-3 s: the double sits down next to her and both lean in as the double holds up a phone for a selfie.
3-4 s: the double vanishes instantly and the original stays seated, smiling.
The camera is locked, medium shot, no movement.
The final second holds on the original alone on the sofa.
Vertical 9:16, 5 seconds, natural indoor light, no text, no captions, no watermark.
```
Negative (do not forbid the double): third person, wrong outfit on the double, face merging, extra arms.

Chinese copy for Seedance 2:

```text
主体：长棕色马尾、穿绿色卫衣的女生坐在客厅沙发上看向镜头，全程同一个人、同一件卫衣。
动作：0-1.5秒 一个一模一样的她从画面左侧走进来；1.5-3秒 分身坐在她旁边，两人凑近，分身举起手机自拍；3-4秒 分身瞬间消失，本体留在沙发上微笑。
镜头：固定机位，中景，不移动。
结尾：最后一秒画面稳定，只有本体坐在沙发上。竖屏9:16，5秒，自然室内光，无文字，无字幕，无水印。
```

## A 3-clip hook sequence with handoff table

Brief: 15 s opener for a sparkling-water brand. Hook (Vanish), bridge (Eyes in), reveal (Floating fall style product pass or a camera push-in).

| Clip | Effect | Start state | End state | Duration |
|---|---|---|---|---|
| A | Vanish | Woman in trench coat on sunny sidewalk | Empty coat and sneakers lying on the pavement, still | 4 s |
| B | Eyes in | Extreme close-up of the same woman's eye (generated from a portrait of her, same light) | Wide shot of a bright kitchen counter with a can in the center, still | 5 s |
| C | Push-in (see `camera-moves.md`) | Last frame of B as the start image | Strong close hero framing of the can, label readable | 6 s |

Rules applied: one hero effect per clip; each end state is the next start state; the subject lock sentence for the woman is copied into A and B; the can label is described identically in B and C; the CTA text and logo are added in the editor after C.

Editing hint for the bridge A to B: A ends on clothes, B begins on an eye, so insert a 4 to 6 frame white flash or a hard cut on a sound hit; the shape change is intended.
