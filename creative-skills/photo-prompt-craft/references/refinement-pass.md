# Refinement pass

Contents:
- When to run
- Step 1: audit against the brief
- Step 2: pick the weakest area (defect categories)
- Step 3: write the focused fix prompt (fix language per defect, verbatim)
- Step 4: re-generate with the previous image as reference
- Step 5: re-audit and budget
- When not to refine
- Sets: carousels and ad packs
- Defect log

Run a refinement for a defect you can actually see in the image, or for a specific correction the user asked for. If you cannot view the image, say the result is unverified and ask what to change; never invent defects.

## Step 1: Audit against the brief

Write the brief as a checklist first (subject, preserved details, scene, light, camera, look, text, negatives), then compare the generated image against each line. Only mark a line as passed if the pixels show it. A prompt, a thumbnail or a status message is not evidence for tiny text or full-resolution sharpness.

Critique template (fill it in, one line each):

```text
Brief line            | Seen in image          | Verdict (pass / fail / unclear)
Subject + identity    | ...                    |
Label text / logo     | ...                    |
Scene + composition   | ...                    |
Light (dir/quality/K) | ...                    |
Camera (lens, DoF)    | ...                    |
Look / palette        | ...                    |
On-image text         | ...                    |
Anatomy (if people)   | ...                    |
Artifacts             | ...                    |
```

## Step 2: Identify the weakest area

Choose the user-specified correction, or the single biggest observed issue. Common categories:

- **Lighting flat**: no clear direction, shadows too soft, no rim or separation
- **Plastic surface**: texture looks rendered not photographed
- **Warped text**: label letters mangled or AI-fictional
- **Anatomy off**: fingers, eyes, ears, hairline issues on people
- **Composition imbalance**: subject off-anchor, weak focal hierarchy
- **Palette drift**: colors don't match known brand context
- **Stock feel**: composition feels generic / over-staged
- **AI sheen**: that telltale rendered-looking smoothness
- **Aesthetic half-applied** (restyle only): source style still bleeding through
- **Flat color band**: model rendered an empty solid-color or dull gradient strip (often happens when text-overlay space was requested and interpreted too literally)

Pick ONE, the highest-impact issue. Fixing three things at once makes the generator change things that were already right.

## Step 3: Write the focused fix prompt

Structure:

```text
Refine the previous image. Keep composition, subject, framing, and overall scene IDENTICAL.
Only change: {{specific photographic instruction targeting the weakest area}}.
{{Preservation directive for what must not change: product identity, label, face, palette, layout}}.
```

### Fix-prompt language by issue type

**Lighting flat:**
> Add directional key light from camera-left at 45°, 4500K, with stronger rim separation on the opposite side. Deepen contact shadow at the base. Increase tonal range between highlight and shadow.

**Plastic surface:**
> Refine surface to show realistic micro-texture. Add tactile detail — visible weave / brushstroke / pore / grain depending on material. Remove rendered-looking sheen.

**Warped text:**
> Sharpen the product label text to fully legible commercial-print quality. Letters must be crisp and intact, not warped or merged.

**Anatomy off:**
> Correct the {{specific body part — fingers / hands / face / eye placement}}. Anatomically correct human proportions, natural realistic detail. Preserve facial likeness.

**Composition imbalance:**
> Reposition subject toward {{specific anchor — left third / right third}}. Strengthen focal hierarchy, focal anchor moved off dead-center.

**Palette drift:**
> Shift palette toward {{specific known brand colors}}. Reduce {{drifting color}} dominance. Bring {{brand accent}} forward.

**Stock feel:**
> Move away from generic staging. Add lived-in detail, intentional asymmetry, and one specific narrative cue {{name a cue}}. Photographic, not staged-stock aesthetic.

**AI sheen:**
> Remove rendered-looking sheen. Add film-grain photographic feel. Realistic skin texture with natural micro-imperfection. Hyper-realistic, not hyper-smooth.

**Aesthetic half-applied (restyle):**
> Source unchanged. Push aesthetic harder toward {{preset specifics — palette, surface, light, mood}}. Stronger {{specific element}} commitment. Source's previous aesthetic completely gone.

**Flat color band:**
> Replace the flat solid-color {{top / bottom / left / right}} area with natural scene continuation — extend the actual environment (sky, blurred background, surface texture, atmospheric gradient) into that area. The frame must read as one cohesive scene, no artificial empty rectangles.

## Step 4: Re-generate with the previous image as reference

Attach the latest version of the SAME image as the single reference (an image-edit or image-to-image input), keep the original aspect ratio, and send the focused fix prompt. Where the tool has no edit mode, rewrite the original full prompt instead: keep every passing line, replace only the failing line with the fix language, and add the failure as a negative.

Rewrite pattern for a full-prompt tool:

```text
ORIGINAL PROMPT (unchanged lines) + REPLACED LINE (the fix) + one added negative for the observed failure
```

## Step 5: Re-audit and budget

Run the critique template again on the new image.

- Major issue remains: refine once more.
- All checked lines pass: deliver.
- A different format is needed entirely: explain the mismatch and ask before starting new scope.

Budget: 1 first pass plus up to 2 refinements per image. After that, deliver the best version and name the remaining limitation; do not keep rerolling with a rebuilt prompt. For text defects that survive two passes, move the text to design software (see typography.md).

## When not to refine

- No pixels and no specific user correction: deliver with visual QA marked unverified.
- The first pass passes every checked line: deliver.
- The "weakness" is subjective taste, not a failed line: deliver and ask the user.
- The change would alter subject or composition rather than polish it: that is a fresh generation.

## Sets: carousels and ad packs

Audit the set first, then individual images:
1. Is the palette continuous across the images?
2. Is the light direction the same?
3. Does the surface or backdrop carry through?
4. Does the narrative order work?

If one image breaks the system, refine only that image, using the locked visual-system block as the preservation directive. Do not regenerate the whole set.

## Defect log

When delivering, name the observed defect or requested correction in one line. Say a defect was fixed only if you inspected the result; otherwise say the correction was applied but unverified.

Example: "First pass had flat lighting on the left side; refined with stronger rim separation."
