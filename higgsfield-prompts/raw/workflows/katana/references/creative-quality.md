# Creative planning, reference discovery, sound and motion reviews

Read `analysis/task-contract.json`: `mode` is `remix` by default and `exact` only for an explicit request for exact reproduction. Its `mode_reason`, `explicit_locks` and `creative_freedoms` govern the work. This standard adds no intake questions, consent steps, purchases or paid exploratory renders. Infer unresolved creative choices from the task, supplied media and inspected references; record the decision and continue.

In **remix**, learn the reference's visual grammar—rhythm, shot scale, motion, texture, typography and musical arc—and use it to author a new result. Story, scenes, camera angle, text, duration, frame count and shot order may change within the user's locks. A source observation is evidence, not automatically an output lock. In **exact**, preserve source structure and appearance outside explicitly requested changes; new ideas must not replace measured choreography, lettering or sound. Never claim a remix is a 1:1 reconstruction.

## Find and actually inspect references

If a primary video is supplied, inspect it fully. Supplementary examples can inform unlocked remix choices; they cannot replace locked source properties. If none is supplied, search current relevant popular TikTok videos and YouTube Shorts using the requested subject, mood, format and uploaded material. Use a real search/browser capability, never invent a stock-search or download tool. [TikTok Creative Center](https://ads.tiktok.com/creative/creativeCenter/trends?LanguageId=1) provides a starting point for current videos and music; ordinary YouTube Shorts search can supply another.

Shortlist up to three promising accessible clips. Inspect their actual complete playback or decoded frame sequence; inspect audible music when playback supports it. A title, thumbnail, snippet, view count or preview cover is not evidence of watching the clip. Record observed popularity signals with their retrieval date; do not label a result trending without evidence. Relevance and observable craft matter more than a large view count. Select a primary autonomously, state that selection briefly, and run the full every-frame/every-second analysis before paid work in either mode. Optimize inspection in batches, never by skipping subtle textures, transitions or intervals.

Use `analysis/references.json` to record each source URL/media ID, source role, viewing coverage, access method, retrieved date, observable popularity evidence and selection rationale. Always account for:

- Montage: actual cut rhythm, shot scale, subject/camera movement, transitions and effect timing.
- Music: actual track/segment, pulse, vocal or instrumental structure, edit points, ending and silence.
- Typography: actual letterforms, weights, tracking, placement, animation and occlusion at readable resolution.

The primary video can supply all three. Record absent properties explicitly. In exact mode, a silent or textless source stays so unless the user requests a change. In remix, add music or text only when it serves the creative plan; absence is neither a requirement to add something nor a prohibition. Inspect additional font specimens or audio references when they materially inform an unlocked choice.

If an exact user-designated clip cannot be accessed, try authorized available routes before reporting the limitation. If no clip was designated, select another accessible candidate. Never ask the user to upload a replacement, pretend a hidden preview was inspected, or silently claim a substitute is the requested exact source.

## Creative brief and assets before production

Keep source observations in `analysis/breakdown.json` and authored output decisions in `plan/creative-plan.json`. Write the brief before pricing/generating missing assets. It contains:

- `output_target`: chosen dimensions, aspect, frame rate, duration/frame count and audio interval, with applicable user locks. Derive unlocked values from the task; do not import a fixed format, song, font set or shot count from a preset.
- The central tension/theme and a concise logline. Use a story with setup/payoff where narrative helps; otherwise use a visual motif and its progression. Do not force a plot or fighting/chase template onto a product, lyric edit or abstract montage.
- Output shot roles, intended action/camera angle/scale, rhythm and text role. Plan purposeful visual rhymes and contrast where useful; no quota of rhymes, transitions or effect changes is required.
- `source_evidence`: observed mechanisms each decision draws on, applicable locks, and reasons for deliberate departures. New output shots need not correspond one-to-one with source shots.
- A shot-role-to-asset map: existing material to reuse, missing images/footage/graphics/audio, selected production route and required on-screen duration. Generate only assets that fill a real planned gap.

Prefer suitable existing footage and whole-plate editing, then source-frame plus supplied-identity image preparation where needed, and Seedance 2.5 when genuinely new motion is needed. A supported Genjutsu transformation or preset is optional when preserving source performance best serves that shot; it is not the default engine for all creative work. A still plus code can suffice for a planned hold, pan or graphic treatment. Do not force every shot to move or require character sheets, location plates, alternate takes or extra preset passes. Requested identity replacement covers every relevant subject shot, including back views, silhouettes, hands and occlusion; it does not require revealing a face hidden by the planned composition.

In exact mode this brief records the source reconstruction and explicit changes; it does not invent a new story or alter the output grid unless the user explicitly requested that change. The finite live-priced plan and existing account/task authority in `budget.md` still apply in both modes. Creative freedom does not authorize unlimited generation or invented provider contracts.

## Recorded music and stock SFX

Use the source's actual soundtrack when it serves the task. In exact mode retain it unless changed by the user. In remix, keep it by default when it fits; when a different musical arc is needed, identify a suitable TikTok track or use a stock/audio-library recording with the right mood, instrumentation, tempo and development. [YouTube Audio Library](https://support.google.com/youtube/answer/3376882?hl=en-uk) is one documented source of recorded music and sound effects. Use available permitted files or library operations; a discovery URL alone is not an audio asset.

New SFX must be actual stock recordings selected for the visible event and the chosen acoustic character. Preserve suitable effects already baked into source audio. Record provenance, actual file/media ID, segment in/out, timeline placement, gain and any attribution associated with the chosen asset. Audition the actual selected segment when possible; label audio as measured rather than heard when playback is unavailable. Do not silently purchase, subscribe, bypass access controls or request consent. If one source is unavailable, try another suitable accessible recording under existing authority; keep source audio where appropriate or report the unresolved audio element precisely.

Do not synthesize a melody, drum loop, bassline, whoosh, impact or substitute song from oscillators, noise, procedural beats or text-to-audio merely because it is convenient. Code is for cutting, aligning, mixing, fades, dynamics and muxing existing recordings. It is not the music or SFX source. The compositor accepts a prepared, timeline-aligned recorded SFX bed through `--sfx-file` or `audio.sfx_src`; legacy procedural `audio.beat` and the `sfx` synthesis command are disabled.

Keep music, SFX and lyric text separate from generated footage. Preserve supplied lyrics and their wording. Preserve visible lyric pixels when exact; otherwise align supplied words or a checked transcription of user-supplied audio/video to the selected segment and render them in the final text pass. Do not send whole lyrics into scene-generation prompts. Do not add lyric captions merely because a song has vocals; they need a role in the task or creative plan. Do not retrieve full protected lyrics from an online-only song that the user did not supply. Continue permitted visual/audio work if a particular text element is unavailable, without inventing words or entering a question flow.

## Typography and deliberate effects

Plan text as part of the message before generating footage, then apply it deterministically in final assembly. Remix can author new wording and hierarchy within user locks; supplied lyrics remain intact. Choose a typeface for the message, language, visual grammar and actual glyph coverage. Verify it loads, then tune width, weight, slant, spacing, placement and animation. In exact mode, unchanged source text pixels or outlines give the most direct match; changed words must match measured source styling. Never request font files or present a typography picker.

Effects must have a scene-specific purpose: reveal, conceal, accent, transition, contrast or motif development. In exact mode reconstruct measured source timing, displacement, texture, intensity and layer order, including intentional roughness. In remix adapt those mechanisms to the new action and rhythm; a new effect can be appropriate without appearing in the source. Do not prescribe generic glitch, RGB splits, shake or zoom as filler, change palettes on every cut by rule, or draw a random treatment for each scene. Seeded randomness may drive texture variation inside an intentionally chosen effect; it must not choose the concept or replace art direction.

Whole-plate editing, global grades, camera transforms and separate graphics are permitted. Code must not swap, paste, redraw, warp or retouch facial/head pixels, hair or anatomy to create or repair likeness. A tracked decorative graphic remains a separate graphic, never a disguised face repair; `hairfix` stays disabled. Underlying identity corrections need a supported authorized model, subject to the same finite plan.

## Three motion reviews

Keep `analysis/motion-reviews.json` with three separately recorded passes, concrete frame/cut evidence, defects, corrections and remaining deviations. Complete all three on the motion plan before generation. Recheck them on representative/current composition previews before the final render and on the rendered sequence before delivery; reuse observations that still apply. These are internal reviews, not three paid takes, three variants or user approval rounds.

1. Timing and rhythm: inspect entrances, pauses, speed changes, beat/vocal anchors and transition start/peak/end frames. Exact mode compares against the primary source; remix compares against its authored musical and dramatic arc while respecting locks.
2. Spatial motion and continuity: inspect trajectories, camera movement, subject scale, acceleration, overlap, framing and direction across cuts. Include every relevant body/occluded shot. Assess newly authored motion against its shot role rather than requiring source choreography in remix.
3. Distinctive detail and polish: remove generic filler, check easing, texture/cadence, typography motion, transitions and sound accents at full size. Each added decision must serve this specific scene and its chosen references.

Do not always choose the third or most unusual idea. Keep the strongest coherent solution, including intentional stillness or unchanged motion. Exact mode preserves original choreography; remix may create new choreography within locks. Record a valid unchanged decision rather than manufacturing three changes to satisfy three passes.
