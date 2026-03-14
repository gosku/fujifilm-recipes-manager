# Fujifilm Sharpness, Noise Reduction, and Clarity — EXIF Mapping


## EXIF fields involved

| Field | Exiftool tag | Notes |
|---|---|---|
| `sharpness` | `Sharpness` | Range −4 to +4, step 1; label suffix on every value |
| `noise_reduction` | `Noise Reduction` | Range −4 to +4, step 1; label suffix on every value; legacy `Normal` from older firmware |
| `clarity` | `Clarity` | Range −5 to +5, step 1; bare integer strings, no label suffix |

---

## Sharpness

### Mapping table

| Camera display value | EXIF stored value | Recipe output |
|---|---|---|
| −4 | `-4 (softest)` | `"-4"` |
| −3 | `-3 (very soft)` | `"-3"` |
| −2 | `-2 (soft)` | `"-2"` |
| −1 | `-1 (medium soft)` | `"-1"` |
| 0 | `0 (normal)` | `"0"` |
| +1 | `+1 (medium hard)` | `"+1"` |
| +2 | `+2 (hard)` | `"+2"` |
| +3 | `+3 (very hard)` | `"+3"` |
| +4 | `+4 (hardest)` | `"+4"` |
| (film profile) | `Film Simulation` | `"N/A"` |

### Key observations

- `-4 (softest)` is defined in the exiftool tag table and is included in the enum, though it is rare in practice.
- `Film Simulation` indicates sharpness is controlled by the film profile; recipe returns `"N/A"`.

---

## Noise Reduction (High ISO NR)

### Mapping table

| Camera display value | EXIF stored value | Recipe output |
|---|---|---|
| −4 | `-4 (weakest)` | `"-4"` |
| −3 | `-3 (very weak)` | `"-3"` |
| −2 | `-2 (weak)` | `"-2"` |
| −1 | `-1 (medium weak)` | `"-1"` |
| 0 | `0 (normal)` | `"0"` |
| 0 (legacy) | `Normal` | `"0"` |
| +1 | `+1 (medium strong)` | `"+1"` |
| +2 | `+2 (strong)` | `"+2"` |
| +3 | `+3 (very strong)` | `"+3"` |
| +4 | `+4 (strongest)` | `"+4"` |

### Key observations

- Positive values (`+1` through `+4`) are defined in the exiftool tag table and supported by newer firmware.
- Older firmware stored `"Normal"` instead of `"0 (normal)"` for the centre value; both are treated as `0` in the recipe output.

---

## Clarity

### Mapping table

| Camera display value | EXIF stored value | Recipe output |
|---|---|---|
| −5 | `-5` | `"-5"` |
| −4 | `-4` | `"-4"` |
| −3 | `-3` | `"-3"` |
| −2 | `-2` | `"-2"` |
| −1 | `-1` | `"-1"` |
| 0 | `0` | `"0"` |
| +1 | `1` | `"+1"` |
| +2 | `2` | `"+2"` |
| +3 | `3` | `"+3"` |
| +4 | `4` | `"+4"` |
| +5 | `5` | `"+5"` |

### Key observations

- Raw exiftool output for Clarity is 1000× the display value (e.g. raw `3000` → display `3`); exiftool applies the ÷1000 conversion automatically before the value reaches the codebase.
- Clarity values are stored as bare integer strings with no label suffix — unlike Sharpness and Noise Reduction.
- Recipe output adds a `+` sign for positive values: `"-4"`, `"0"`, `"+3"`.
