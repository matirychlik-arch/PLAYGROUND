# Subtitle fonts

Binaries are NOT part of the bundle — the workflow resource loader serves text files only,
so nothing here is a `.ttf` until something downloads it.

**Do not curl these by hand: run the fetch script.**

```bash
bash ${HF_WORKFLOWS}/video-montage/scripts/fetch_fonts.sh          # idempotent, non-fatal per font
bash ${HF_WORKFLOWS}/video-montage/scripts/fetch_fonts.sh --force  # re-download everything
```

It writes into THIS folder, which is where both burners look
(`subtitle_paper_burn.py` resolves `<script dir>/fonts/<file>`, `burn_caps_clean.sh`
passes the folder to libass as `fontsdir`). Sources per face: `$FONT_BASE_URL`
(default `https://static.higgsfield.ai/faceless/fonts`) first, then the upstream
open-licence URL, then nothing — and a missing face is never fatal.

## TikTok Sans — the default face for `bold` and `clean`

The native TikTok/Shorts caption face, open-sourced by TikTok under the SIL Open Font
License 1.1. Latin + Cyrillic + Greek (460+ languages), so it also covers Russian
captions. `subtitle_paper_burn.py` expects `TikTokSans-Bold.ttf`; `burn_caps_clean.sh`
asks libass for the family name `TikTok Sans`.

## The other keys

| `--font-key` | file                          | look                                  |
| ------------ | ----------------------------- | ------------------------------------- |
| `patrick`    | `PatrickHand-Regular.ttf`     | legible handwritten (paper default)   |
| `caveat`     | `Caveat-Regular.ttf`          | flowing cursive script                |
| `marker`     | `PermanentMarker-Regular.ttf` | bold marker, punchy (Latin only)      |
| `anton`      | `Anton-Regular.ttf`           | heavy condensed display               |
| `montserrat` | `Montserrat-ExtraBold.ttf`    | clean geometric caps                  |
| `tiktok`     | `TikTokSans-Bold.ttf`         | native TikTok caps (**bold default**) |
| `metropolis` | `Metropolis-ExtraBold.ttf`    | optional drop-in                      |

All are SIL OFL and downloadable from Google Fonts. A missing file is not fatal:
the burner falls back to `tiktok` → `montserrat` → `caveat` and says so, and it
re-checks glyph coverage before drawing (a Latin-only face never ships an empty
Cyrillic label).
