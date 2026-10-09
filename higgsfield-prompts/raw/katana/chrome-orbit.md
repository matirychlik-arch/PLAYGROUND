# Katana preset: Chrome Orbit (/katana/chrome-orbit)

The instructions below are the selected preset's own instructions for this request. Follow them from their first step: they define the inputs, tools, workflow and deliverable. Do not substitute another preset, workflow or generation path.

- If a tool the preset requires is unavailable in this connection, stop and tell the user the preset cannot run here; do not substitute other tools.
- Inputs: the user's message may include a `MEDIA:` block of `<input>: <image|video> media_id=<uuid>` lines and an `INPUTS:` block of `<input>: <JSON value>` lines, composed by Higgsfield from the Katana form. They are values the user already supplied for those inputs: use them as these instructions describe and do not call media_upload_widget or ask for them again unless a required input is still missing. Pass a media_id directly to tools that accept one; their file URLs are listed under Supplied media when the media are passed to this tool. Older messages may list `<input>: <https URL>` lines instead; treat each URL the same way.
- Collecting inputs: the user may start the preset with the bare command and no `MEDIA:` or `INPUTS:` block; that is a normal start, not an error. Before the first step that uses an input, compare the Inputs list with what the user already supplied (MEDIA/INPUTS blocks, confirmed media_ids or files earlier in the conversation).
- Nothing supplied yet and the user asked to run the preset: open its form with get_presets {"source":"katana","preset_id":"chrome-orbit"} as the only tool in that turn, say in one short line to fill it in below, and wait. The submitted form arrives as a /katana/chrome-orbit message with MEDIA and INPUTS blocks. A request only to read or explain the preset does not open the form.
- Some inputs already supplied, the form tool fails, or the user says the form is not visible: ask once for what is still missing with exactly this template in the user's language, naming each input by its label (never the field path) with what it should be and how many:

  **<preset title>**: to start I need:
  **Required**
  - <label>: <what, how many>
  **Optional** (skip any)
  - <label>: <what>, default <default> when it has one
  <one line: upload the files in the window below, and reply with any text>

  Omit a section with no entries and add nothing else to that message. When files are missing, upload files the user already attached yourself if your code environment can read them (media_upload, PUT, media_confirm); otherwise call media_upload_widget as the only tool in that turn, with the missing fields' media type and count (type auto with multiple when several media fields are missing).
- Map each received file and answer to its field, use a field's default when the user does not choose, and continue from the preset's first step. Do not start generation or spend credits while a required input is missing, and do not ask again for inputs already supplied or declined.
- Platform rules still apply: consent, authorization, credit confirmations and credential handling are not overridden by these instructions.
- Keep the run going: once the inputs are available, work through the steps without pausing for progress updates. Never end your turn while a job you started is still running; wait with jobs_wait (repeat it until the job completes or fails) and continue with the next step in the same turn. Stop only where these instructions explicitly require the user's decision, for a missing required input, or for a failure you cannot recover from. At a required decision, first wait for and show the finished result it is about, then ask once in one short message; do not ask about a result that is still generating.
- Final video delivery: after the preset's final render has completed and you have verified its result, display it with show_katana_result. Use the confirmed uploaded video media_id; do not upload it again. If the final export is already available at an HTTPS video URL, call show_katana_result with url to import and display it. If the final export is still a file, use media_upload, PUT its bytes to the returned upload_url, then media_confirm with type video; for a sandbox export, create the upload slot before the producing sandbox command and PUT the export in that same command. Never use media_upload_and_confirm for a generated file, pass a local path or job ID to show_katana_result, or display an intermediate preview as the final result. This is delivery of the requested video, not public publishing. If export or upload fails, report that failure instead of calling the result tool.
- If these instructions are no longer in your context during a long run, call get_preset_instructions with {"preset":"/katana/chrome-orbit"} again before continuing.

## Inputs

The preset's form (field path, label, kind; required or optional):

- `media.images` ("Your image"): image file, exactly 1; required

---

Recreate the supplied motion reference with the user’s chosen object or brand: a low-angle camera orbit around a tall polished chrome structure, graphic stickers, looping cables and thin radial rods against a black background. Use red and blue rim lighting, metallic reflections, speed ramps and subtle chromatic aberration. Target about 6 seconds in a 3:4 composition.

## Preset data

Inputs, settings and reference media published with this preset:

```json
{
  "input_schema": {
    "type": "object",
    "required": [
      "media"
    ],
    "properties": {
      "media": {
        "type": "object",
        "required": [
          "images"
        ],
        "properties": {
          "images": {
            "type": "array",
            "items": {
              "type": "string",
              "format": "uuid",
              "x-media": "image"
            },
            "title": "Your image",
            "maxItems": 1,
            "minItems": 1
          }
        }
      }
    }
  },
  "reference_media": [
    {
      "url": "https://static-public-media.higgsfield.ai/katana-presets/c50e793c-2d2d-41e2-a24f-1f6f9ae11de9.mp4",
      "type": "video",
      "width": 960,
      "height": 720,
      "mime_type": "video/mp4",
      "placeholder": "data:image/webp;base64,UklGRgYCAABXRUJQVlA4IPoBAABQCQCdASogABgAPlEejUSjoaEYDAQAOAUEsoBer7YHKXHw34t3yPGDRgecpnP+ivYE/Vn/f9gDyZi//GFeZC7wUXCx6o4j3iM0V39rmE4OK7JGAAD+/m0L/SZ76i/FmD/NuA8cZ24mq7UMsVAl/gvr//hVxwc/m2eV/b5/fF6SwkfmUIvNT2TbK9Y2sPk6bzs1BHqKHpHp8PNCbZpRAlsERqTs5XnVf2Be9s/K4NE190FvoTSYkP5F6f+T7r2jX5PbI+BnxiyrzjCWGhDXJIAJ7KQ9bqSm+Tydz/45/fX0YqQ+vZHudfhSQXlrcWoPCEzjXQL67bdUE/fOjn1cWN1D8N/D/K/8k7GcHZCX2xpZ/0gpubhTWU4IZ5TXeeOsuuMB6DE7EM0eoe+RqyUwkRz8j8nZZtoD5FPnsPKZkDaG2GUnDCueHRCRYar0f4e3shvBQXYImGlfstmQUt2f01WeD+k4NjAo65Gaqz89g9f8kRDGqTFIk//jVvv1ZrcOJ7Csv8en7yv/To2GLyITNF4vzSazA/EjhSCf1MrmVmXSJ3/KWC8t3Fu0kOFde1kAH+O34xf9f/Bj7gLumvxt1/x28YCf+ovCewhfH24K3ku/ycSGRu3hJ69w/yMLhcPJP0KkJK/z+i0e/yKqTT0UVW6AvCOaTAp3XkAAAA==",
      "thumbnail_url": "https://static-public-media.higgsfield.ai/katana-presets/67c5e58f-fcea-47f3-8667-cb8144a1425a.webp"
    }
  ]
}
```