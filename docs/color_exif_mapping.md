# Fujifilm Color / Saturation — EXIF Mapping


## EXIF fields involved

| Field | Exiftool tag | Notes |
|---|---|---|
| `color` | `Saturation` | Dual-purpose: saturation adjustment for colour simulations; simulation name for B&W/Acros/Sepia |

## Dual-purpose behaviour

The `Saturation` EXIF tag is shared between two unrelated meanings depending on the active
film simulation.  See also `film_simulation_exif_mapping.md` for the B&W/Acros/Sepia lookup.

```
if color is a numeric label (e.g. "0 (normal)", "+2 (high)"):
    → saturation adjustment; decode using table below

elif color is a non-numeric string (e.g. "Acros", "None (B&W)", "Film Simulation"):
    → film simulation name or special case; recipe returns "N/A" for the Color field
```

## Numeric saturation mapping table

| Camera display value | EXIF stored value | Recipe output |
|---|---|---|
| −4 | `-4 (lowest)` | `"-4"` |
| −3 | `-3 (very low)` | `"-3"` |
| −2 | `-2 (low)` | `"-2"` |
| −1 | `-1 (medium low)` | `"-1"` |
| 0 | `0 (normal)` | `"0"` |
| +1 | `+1 (medium high)` | `"+1"` |
| +2 | `+2 (high)` | `"+2"` |
| +3 | `+3 (very high)` | `"+3"` |
| +4 | `+4 (highest)` | `"+4"` |

## Non-numeric values that produce "N/A"

| `color` EXIF value | Reason |
|---|---|
| `None (B&W)` | Monochrome simulation — no saturation adjustment |
| `B&W Red Filter` | Monochrome + Red filter |
| `B&W Yellow Filter` | Monochrome + Yellow filter |
| `B&W Green Filter` | Monochrome + Green filter |
| `B&W Sepia` | Sepia simulation |
| `Acros` | Acros simulation |
| `Acros Red Filter` | Acros + Red filter |
| `Acros Yellow Filter` | Acros + Yellow filter |
| `Acros Green Filter` | Acros + Green filter |
| `Film Simulation` | Saturation controlled by film profile (not user-set) |

## Key observations

- `Film Simulation` appears for some film simulations (e.g. Eterna, Astia, Pro Neg. Std); it means the film profile controls saturation internally and the user cannot override it.
- For B&W/Acros/Sepia simulations the `Film Mode` EXIF field is absent; `Saturation` encodes the simulation name instead.  In those cases the Color recipe field is `"N/A"` — there is no separate saturation adjustment.
- Recipe output for numeric values is a signed integer string: `"-2"`, `"+3"`, `"0"`.
