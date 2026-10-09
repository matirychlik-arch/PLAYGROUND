# Typography in images: the three-case rule

Contents:
- Why free composition is the default
- Case 1: exact text specified
- Case 2: text added later in design software
- Case 3: nothing said about text
- Exact-string rules
- When to leave text out of the generator

Default behavior with a text-capable image model is to compose freely, without carving out empty space. Empty "reserved zones" make generators render flat color bands or dull gradients, which always look bad. Avoid forcing them.

## Case 1: the user specified concrete text to include

If the user wrote exact words (`the headline should say 'New Drop'`, `add 'Sale ends Friday'`), include the text directly in the prompt as part of the composition. A generator that renders text well will integrate it as typography inside the scene.

```text
[TYPOGRAPHY]
Integrated typography in the scene reads "New Drop" — set in {{font style: bold sans-serif / elegant serif / hand-lettered / clean modern}}, positioned {{naturally within the composition}}, color {{contrasting with background for legibility}}.
```

## Case 2: the user will overlay text in Figma, Canva or Photoshop

Only when the user says they will add text afterward (`I'll add the headline in Figma`, `leave space for typography`), instruct the composition to leave a tonally uniform area:

```text
[COMPOSITION FOR TEXT OVERLAY]
Leave one area of the frame visually calm and tonally uniform — natural soft gradient, atmospheric blur, or smooth surface — so the user can overlay typography in post-production. This area must still feel like part of the scene (sky, blurred background, surface), NOT a hard-edged empty rectangle.
```

The key phrase is "tonally uniform area within the natural scene". Never write `clean negative space` or `reserved white space`; those phrases trigger a drawn flat band. Add the anti-flat-band negatives from negatives.md.

## Case 3: nothing said about text (default)

Do not mention text or overlay zones at all. Let the generator compose freely for maximum visual quality.

## Exact-string rules

Written for this skill, from general practice with text-capable image models:

- Put the exact string in straight double quotes and copy it character by character, including punctuation and Polish diacritics (ą ć ę ł ń ó ś ź ż). Say once: "render exactly as written, no extra words".
- Keep strings short. One to six words per text element renders reliably; paragraphs usually do not.
- State language and case if it matters ("Polish, all caps").
- Describe the typeface in visual terms (bold geometric sans-serif, high-contrast serif, hand-lettered script) and its role (headline, label, price tag), plus position and contrast with the background.
- One text element per area; avoid text on curved, reflective or busy surfaces unless the brief needs it.
- Text printed on a real product must be copied from the reference, not retyped; see product-shot-recipes for identity rules.
- Check the output at 100% zoom, letter by letter. If a diacritic or a letter is wrong after two attempts, generate without text and set the type in design software; that is faster than rerolling.
