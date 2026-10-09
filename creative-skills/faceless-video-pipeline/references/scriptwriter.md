# scriptwriter.md: script craft for faceless narrated video

Contents
1. Through-line first
2. The arc (hook, build, turn, payoff) + Kids variant 2b
3. Research targets
4. VO line craft (mechanics and density)
5. Rewrite pass (run before locking the script / before voicing)
6. Script table format and numeric limits

The mechanics are N blocks, five varied shots of about 2 s per block (Kids 4), one VO line of 20 to 23 words (Kids 17 to 21) of at most two sentences filling about 7.8 to 9.5 s, humor per channel type. This file owns the SHAPE. The failure mode of a faceless script is not "boring"; it is **a list**: fact, fact, fact gives the viewer no reason to keep watching. Facts are material; shape is the product.

## 1. Through-line first

Before Block 1 exists, name ONE physical object or process that appears in every block and **escalates monotonically** (shorter / taller / fuller, never merely recurring as decoration): a fuse burning down, a stack growing until it blocks a door, a map filling with dots, a plate scraped into an overflowing bin.

- It must be renderable in the chosen style. **Give it a prop asset** (generated once, reused in every shot) so it stays identical across blocks (diorama: the burnt-orange prop; collage: its own cutout).
- Each block's shots show it at its current state; the **payoff block resolves it** (the fuse reaches the keg). If the finale does not pay it off, pick a different object.
- Name the through-line when showing the script for approval.

## 2. The arc, sharpened (hook, build, turn, payoff)

- **Hook: cold open, SHORT.** The most surprising concrete thing, stated flat; understatement makes a big number bigger. **Keep block 1's opening line PUNCHY: the first sentence is at most 8 words** (ideally the raw fact: "Most of the ocean has never been seen."), THEN the block's line fills out to the normal 20 to 23-word density. No greeting, no "in this video", no throat-clearing, no windup clause before the hook lands. (Kids keeps its warm host manner and catchphrases; the cold-open brevity binds History and Explainer.) A sharp direct question is a legal hook (also at most 8 words); if used, withhold the answer until the payoff and let it live in the visuals.
- **Early stakes.** One beat answering "why should I care": the misconception ("everyone blames X, wrong") or the proximity (it touches the viewer this week).
- **Build: evidence, escalating.** ONE idea per block (the cuts are angles on that idea, not separate ideas). Every block anchored to a concrete: number, date, place, named thing, comparison. **The reorder test:** if the build blocks could be shuffled without loss, you listed instead of escalated; each must be bigger, weirder, or more specific than the last.
- **Turn.** The counterintuitive reveal, usually block N-1. Test: does it change what the viewer thought two blocks ago, or just summarize? A summary is not a turn.
- **Payoff.** Land the answer, then a kicker that **reframes the hook**: echo its image or number with new meaning, do not repeat it. The through-line resolves here. Humor styles still apply (deadpan setup, absurd punch; Barnum lines; confirmation-bias gags).

### 2b. Kids topics: the question IS the hook, and the answer follows immediately

On a Kids run the generic hook works differently. A child's topic is a question ("what is a cell", "why is the sky blue", "how do bees make honey"), so the hook is that question SAID OUT LOUD, and the answer arrives in the same block rather than being withheld for the turn:

```
Block 1  "What is a cell? A cell is a tiny room, and every living thing is built out of them."
Block 2  one concrete example, shown doing the thing
Block 3+ one new idea per block: where it is -> what it does -> what happens without it
Last     the wow quantity in words, then the opening question answered again in five words
```

Withholding the answer to build suspense is an adult move; on Kids it reads as random. The full skeleton, the picture-storytelling rules and the first-sentences test are in `format-variants.md` (Kids section).

## 3. Research targets (factual topics, before scripting)

History and factual Explainer topics: quick web research first, never script from memory alone. You are done when you hold: the **hook stat** (the number that stops the scroll), **3 to 5 concrete facts**, the **counterintuitive turn**, and vivid physical specifics the shots can stage. Cross-check spoken numbers against a second source; keep a Sources line for delivery. Fantasy and Kids topics: skip research, invent freely (but nothing fake about the real world).

## 4. VO line craft (works with vo-and-captions.md)

- **20 to 23 words (Kids 17 to 21), at most TWO sentences, comma-light, filling about 7.8 to 9.5 s**, **minimal full stops**: TTS pauses about 0.7 s at periods and about 0.5 s at commas, so one flowing clause fits where three clipped sentences both overrun AND sound pausey. Performed brackets (`[scoffs]`) cost about 1 s each, so budget them. (Non-English: the word band shrinks; Polish is about 16 to 19 words per 10 s, see `narration-vo`.)
- **Dead-air floor:** the line must FILL its block, about 7.8 to 9.5 s of speech. A line ending before 7.8 s sits centred in its 10 s block with silence on BOTH sides and reads as a stall. Rewrite denser (never pad with filler, never stretch anything).
- **Density is CONTENT, not adjectives.** LINE HYGIENE (`vo-and-captions.md`) is a hard gate: no conversational filler ("you know", "I mean", "basically"), one modifier per thing, no modifier repeated inside a line, one new concrete per line, at most one diminutive or exclamation. A short line gets another FACT, never another epithet.
- Numbers spelled out. No sentence or near-identical phrase in two blocks.

## 5. Rewrite pass (run before locking the script / before voicing)

1. Does the hook work standalone, zero context?
2. Is every number/date traceable to the research?
3. One idea per block; every cut serves that idea?
4. Do build blocks fail the reorder test (i.e., escalate)?
5. Does the turn surprise rather than summarize?
6. Does the payoff's kicker echo the hook and resolve the through-line?
7. Every full-block line 20 to 23 words (Kids 17 to 21), at most two sentences, numbers written as words, flowing and comma-light, filling about 7.8 to 9.5 s when spoken; humor lands per the channel type's voice?
7a. LINE HYGIENE clean: zero filler phrases, no modifier repeated inside a line, every line carrying one new concrete, at most one diminutive/exclamation each?
8. Does every block's SHOT text stage the CONCRETE nouns/quantities of ITS OWN line (spices on screen when the line says spices)? No action motif repeated back to back, none beyond its budget (long-form: the motif ledger in `format-variants.md`)?

## 6. Script table format and numeric limits

Write the script as a table the user can read in chat and a tool can parse. Machine-checkable limits (check them by hand or with any word counter):

| Check | Limit |
|---|---|
| Block count | N = duration seconds / 10 (a short last block gets a proportional line) |
| Words per full 10 s line | 20 to 23 (Kids 17 to 21; Talking Characters dialogue blocks 16 to 22 total) |
| Sentences per line | at most 2 |
| Digits in a VO line | none, numbers as words |
| Cold open (Explainer, History) | first sentence at most 8 words |
| Phrase repeated in two blocks | no run of 5 or more identical words |
| Same filler / stacked modifier | none; a content word is not repeated within 6 words |
| Locations | at most 2 consecutive blocks per location |
| Shot sizes | adjacent shots never share a size; no re-establishing a location already visited |
| Through-line | present in every block, resolved in the payoff block |
| Arc roles | hook = block 1, payoff = last block, turn from 3 blocks up, build = the blocks between |
| Sources | factual Explainer / History: at least one absolute URL |

Pacing numbers at a glance: 6 blocks per minute; 30 shots per minute (5 shots x 2 s) or 24 for Kids (4 x 2.5 s); 120 to 138 English words per minute of finished video (20 to 23 words x 6 blocks); an impact beat about every 3 s; a stills video changes picture about every 1 s.
