# scriptwriter.md — script craft for Phase 3

Phase 3 owns the mechanics (N blocks, 5 varied ~2s shots per block — Kids 4, one VO line
of 20–23 words — Kids 17–21, at most two sentences — filling ~7.8–9.5s, humor
per channel type).
This file owns the SHAPE. The
failure mode of a faceless script is not "boring" — it is **a list**: fact,
fact, fact gives the viewer no reason to keep watching. Facts are material;
shape is the product.

## 1. Through-line first

Before Block 1 exists, name ONE physical object or process that appears in
every block and **escalates monotonically** (shorter / taller / fuller —
never merely recurring as decoration): a fuse burning down, a stack growing
until it blocks a door, a map filling with dots, a plate scraped into an
overflowing bin.

- It must be renderable in the chosen style — **give it a prop asset in
  Phase 2** so it stays identical across blocks (diorama: the burnt-orange
  prop; collage: its own cutout).
- Each block's shots show it at its current state; the **payoff block
  resolves it** (the fuse reaches the keg). If the finale doesn't pay it off,
  pick a different object.
- Name the through-line when showing the script at SCRIPT LOCK.

## 2. The arc, sharpened (hook → build → turn → payoff)

- **Hook — cold open, SHORT.** The most surprising concrete thing, stated
  flat — understatement makes a big number bigger. **Keep block 1's opening
  line PUNCHY: the first sentence is ≤8 words** (ideally the raw fact — "Most
  of the ocean has never been seen."), THEN the block's line fills out to the
  normal ~20–23-word density. No greeting, no "in this video", no
  throat-clearing, no windup clause before the hook lands. (Kids keeps its
  warm host manner and catchphrases — the cold-open brevity binds History and
  Explainer.) A sharp direct question is a legal hook (also ≤8 words); if
  used, withhold the answer until the payoff and let it live in the visuals.
- **Early stakes.** One beat answering "why should I care": the misconception
  ("everyone blames X — wrong") or the proximity (it touches the viewer this
  week).
- **Build — evidence, escalating.** ONE idea per block (the cuts are angles on
  that idea, not separate ideas). Every block anchored to a concrete:
  number, date, place, named thing, comparison. **The reorder test:** if the
  build blocks could be shuffled without loss, you listed instead of
  escalated — each must be bigger, weirder, or more specific than the last.
- **Turn.** The counterintuitive reveal, usually block N−1. Test: does it
  change what the viewer thought two blocks ago, or just summarize? A
  summary is not a turn.
- **Payoff.** Land the answer, then a kicker that **reframes the hook** —
  echo its image or number with new meaning, don't repeat it. Through-line
  resolves here. Humor styles still apply (deadpan setup → absurd punch).

### 2b. Kids topics: the question IS the hook, and the answer follows immediately

On a Kids run the generic hook works differently. A child's topic is a question ("what is a
cell", "why is the sky blue", "how do bees make honey"), so the hook is that question SAID OUT
LOUD, and the answer arrives in the same block rather than being withheld for the turn:

```
Block 1  "What is a cell? A cell is a tiny room, and every living thing is built out of them."
Block 2  one concrete example, shown doing the thing
Block 3+ one new idea per block: where it is -> what it does -> what happens without it
Last     the wow quantity in words, then the opening question answered again in five words
```

Withholding the answer to build suspense is an adult move; on Kids it reads as random. The full
skeleton, the picture-storytelling rules and the first-sentences test are in
`references/kids-styles.md`.

## 3. Research targets (factual topics — before scripting)

History and factual Explainer topics: quick web research first, never script
from memory alone. You're done when you hold: the **hook stat** (the number
that stops the scroll), **3–5 concrete facts**, the **counterintuitive turn**,
and vivid physical specifics the shots can stage. Cross-check spoken numbers
against a second source; keep a Sources line for delivery. Fantasy/Kids
topics: skip research, invent freely (but nothing fake about the real world).

## 4. VO line craft (works with vo_and_captions.md)

- **20–23 words (Kids 17–21), at most TWO sentences, comma-light, filling ~7.8–9.5s** (the
  `[00:00-00:09]` timecode
  prefix paces the TTS — see vo_and_captions.md), **minimal full stops** — TTS
  pauses ~0.7s at periods and ~0.5s at commas, so one flowing clause fits where
  three clipped sentences both overrun AND sound pausey. Performed brackets
  (`[scoffs]`) cost ~1s each — budget them.
- **Dead-air floor:** the line must FILL its block — target ~7.8–9.5s of speech.
  A line ending before 7.8s sits centred in its 10s block with silence on BOTH
  sides and reads as a stall. Rewrite denser (never pad with filler, never
  stretch anything).
- **Density is CONTENT, not adjectives** — `vo_and_captions.md §LINE HYGIENE` is
  a hard gate: no conversational filler ("you know", "I mean", "basically"), one
  modifier per thing, no modifier repeated inside a line, one new concrete per
  line, at most one diminutive or exclamation. A short line gets another FACT,
  never another epithet.
- Numbers spelled out. No sentence or near-identical phrase in two blocks.

## 5. Rewrite pass (run before SCRIPT LOCK / before voicing)

1. Does the hook work standalone, zero context?
2. Is every number/date traceable to the research?
3. One idea per block; every cut serves that idea?
4. Do build blocks fail the reorder test (i.e., escalate)?
5. Does the turn surprise rather than summarize?
6. Does the payoff's kicker echo the hook and resolve the through-line?
7. Every full-block line 20–23 words (Kids 17–21), at most two sentences, numbers written as words, flowing/comma-light,
   filling ~7.8–9.5s when spoken; humor lands per
   the channel type's voice?
7a. LINE HYGIENE clean — zero filler phrases, no modifier repeated inside a line,
   every line carrying one new concrete, at most one diminutive/exclamation each?
8. Does every block's SHOT text stage the CONCRETE nouns/quantities of ITS OWN line
   (spices on screen when the line says spices)? No action motif repeated back to back,
   none beyond its budget (long-form: the motif ledger in history-longform.md)?
