# Katana preset /katana/kawaii-pop: part 2 of 2

## Out of scope (say so before generating)

- Real celebrities or public figures as the heroine.
- Dance, full-body or story edits: everything hangs on a visible face in a selfie.
- Lip-synced singing to a song: Seedance blocks audio references here.
- More than 2 people in a shot, or a friend in every shot.
- Chants over ~8 words per phrase or edits over ~20 s: jump-cut density stops working; propose two edits.

## Preset data

Inputs, settings and reference media published with this preset:

```json
{
  "input_schema": {
    "type": "object",
    "properties": {
      "media": {
        "type": "object",
        "properties": {
          "character": {
            "type": "array",
            "items": {
              "type": "string",
              "format": "uuid",
              "x-media": "image"
            },
            "title": "Character",
            "maxItems": 1,
            "minItems": 0,
            "description": "Photo of the heroine: one person, face visible, both eyes open, framed at least to the chest. Without it a new heroine is generated."
          }
        },
        "additionalProperties": false
      },
      "slot_values": {
        "type": "object",
        "properties": {
          "chant": {
            "type": "string",
            "title": "Chant",
            "description": "Chant words. Default: NYAN / ICHI NI SAN / NYAN / ARI·GATO"
          },
          "prompt": {
            "type": "string",
            "title": "Wishes (optional)",
            "description": "Optional wishes about the inputs or the result. Keep the preset defaults unless a change is explicitly requested."
          }
        },
        "additionalProperties": false
      }
    },
    "additionalProperties": false
  },
  "reference_media": [
    {
      "url": "https://static-public-media.higgsfield.ai/katana-presets/published/37a305221afe1e5d4e7c0b849282e5f93c4fa6afa24136a33d530daeb26482ef",
      "type": "video",
      "width": 900,
      "height": 720,
      "mime_type": "video/mp4",
      "placeholder": "data:image/webp;base64,UklGRkQBAABXRUJQVlA4IDgBAAAwBwCdASogABoAPlEijUQjoiEYDAQAOAUEtgBOmUI+G/BmL3sxdku8qo13d+yNAitbifG7DCozuLB1sIjGUPPJ2AAA/v7C6TklDn3IWJyHYLSujGwLm5ziFA5WF06EDsTmGA7pMbm/vjBDYvuRi5EBnirLxEo8zGB4vHsOca/OWAhw0Ep5DQ7oA03qzBfNFQ9w5vk2Tioug2ArWGzktkU9HoBXpRa7/7IwujaJXyawdnhn/f/bER9o/RVLZtKJ9Yy1wZWBHpfHExaVfrZmbfbKQuqCigElHy2BtzoAtLmpUHDgLT5TwyTIdC5XZ/ufBer2X/gIk/kkXZ/2//Qv4KBL/L/RAl8d3si09c7VP2c5i6c25y/XsPcqv6REZmP8lYEUypOQiD3/S7id+ZjYx3Pd7v80hhwAAAA=",
      "thumbnail_url": "https://static-public-media.higgsfield.ai/katana-presets/published/3226568748b4f56a67bce087d1c73c294c8f25efc19a422db378616773deeaff"
    }
  ]
}
```

---
This is the last part. Follow the complete instructions from their first step.