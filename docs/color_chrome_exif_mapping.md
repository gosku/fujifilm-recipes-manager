# Fujifilm Color Chrome Effect — EXIF Mapping


## EXIF fields involved

| Field | Exiftool tag | Notes |
|---|---|---|
| `color_chrome_effect` | `Color Chrome Effect` | `"Off"`, `"Weak"`, or `"Strong"` |
| `color_chrome_fx_blue` | `Color Chrome FX Blue` | `"Off"`, `"Weak"`, or `"Strong"` |

## Full mapping table

| Camera menu setting | `color_chrome_effect` | `color_chrome_fx_blue` |
|---|---|---|
| CCE: Off / CCFXB: Off | `Off` | `Off` |
| CCE: Weak / CCFXB: Off | `Weak` | `Off` |
| CCE: Strong / CCFXB: Off | `Strong` | `Off` |
| CCE: Off / CCFXB: Weak | `Off` | `Weak` |
| CCE: Off / CCFXB: Strong | `Off` | `Strong` |
| CCE: Weak / CCFXB: Weak | `Weak` | `Weak` |
| CCE: Strong / CCFXB: Strong | `Strong` | `Strong` |

## Key observations

- Both EXIF values map directly to recipe card display values — no translation needed.
- The two fields are fully independent; any combination of `Off`, `Weak`, and `Strong` is valid.
- `color_chrome_effect` (CCE) enhances colour saturation and detail on vivid, highly saturated colours across the full spectrum.
- `color_chrome_fx_blue` (CCFXB) applies the same treatment specifically to blue tones; useful for deepening skies and water without affecting other hues.
- Both fields accept the values `Off`, `Weak`, and `Strong`.
