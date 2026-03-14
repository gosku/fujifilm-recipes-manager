# Fujifilm Monochromatic Color Tuning — EXIF Mapping


## EXIF fields involved

| Field | Exiftool tag | Recipe field | Notes |
|---|---|---|---|
| `bw_adjustment` | `BW Adjustment` | `monochromatic_color_warm_cool` | Warm/cool (yellow/blue) axis; range −18 to +18 |
| `bw_magenta_green` | `BW Magenta Green` | `monochromatic_color_magenta_green` | Magenta/green axis; range −18 to +18 |

## Value format

Both fields store signed integer strings with no label suffix.  The EXIF value is a
direct pass-through to the recipe field — no conversion is needed.

| Camera display value | EXIF stored value | Recipe output |
|---|---|---|
| −18 | `"-18"` | `"-18"` |
| −5 | `"-5"` | `"-5"` |
| 0 | `"0"` | `"0"` |
| +3 | `"+3"` | `"+3"` |
| +10 | `"+10"` | `"+10"` |
| +18 | `"+18"` | `"+18"` |

## Availability

Monochromatic color tuning is only available when the active film simulation is
B&W (Monochrome), Acros, or Sepia.  For all colour simulations, both EXIF fields
are **empty** and the recipe returns `"N/A"`.

| Condition | `bw_adjustment` | `bw_magenta_green` | Recipe output |
|---|---|---|---|
| B&W / Acros / Sepia active | signed integer string | signed integer string | value as-is |
| Colour simulation active | `""` (empty) | `""` (empty) | `"N/A"` |

## Key observations

- Both fields are independent; each axis can be set to any value in the −18 to +18 range regardless of the other.
- `bw_adjustment` controls the warm/cool axis: positive values shift towards yellow (warm), negative values shift towards blue (cool).
- `bw_magenta_green` controls the magenta/green axis: positive values shift towards magenta, negative values shift towards green.
- EXIF values are already formatted as signed integer strings (`"+10"`, `"-5"`, `"0"`); no reformatting is required.
