# Fujifilm White Balance — EXIF Mapping


## EXIF fields involved

| Field | Exiftool tag | Notes |
|---|---|---|
| `white_balance` | `White Balance` | The WB mode (e.g. `"Auto"`, `"Daylight"`, `"Kelvin"`) |
| `white_balance_fine_tune` | `White Balance Fine Tune` | Raw EXIF value is 20× the camera display value; normalised on read |
| `color_temperature` | `Color Temperature` | Only present when `white_balance` is `"Kelvin"` |

## WB mode mapping table

| Camera menu name | `white_balance` EXIF value | Recipe display value |
|---|---|---|
| Auto | `Auto` | `Auto` |
| Auto White Priority | `Auto (white priority)` | `Auto (white priority)` |
| Daylight | `Daylight` | `Daylight` |
| Fluorescent (Daylight) | `Daylight Fluorescent` | `Daylight Fluorescent` |
| Incandescent | `Incandescent` | `Incandescent` |
| Kelvin | `Kelvin` | `<value>K` (e.g. `5500K`) |

## Fine tune normalisation

Raw EXIF fine tune values are stored at 20× the camera display value.  `read_image_exif`
divides by 20 on read, producing values in the range −9 to +9 for both channels.

| Raw EXIF value (Red, Blue) | Normalised (÷20) | Recipe display |
|---|---|---|
| `(40, -60)` | `(+2, -3)` | `"Red +2, Blue -3"` |
| `(0, 0)` | `(0, 0)` | `"Red 0, Blue 0"` |
| `(-180, 180)` | `(-9, +9)` | `"Red -9, Blue +9"` |

- Both channels are always present in the output string, even when zero.
- Format is always `"Red <signed_int>, Blue <signed_int>"`.
- Fine tune range: −9 to +9 for both red and blue channels (after normalisation).

## Color temperature (Kelvin mode)

When `white_balance` is `"Kelvin"`, `color_temperature` holds the numeric temperature
value (e.g. `5500`).  The recipe field renders this as `"5500K"`.  For all other WB
modes, `color_temperature` is absent and the recipe field uses the `white_balance`
EXIF value directly.

## Key observations

- `white_balance_fine_tune` normalisation (÷20) is applied in `read_image_exif` at read time; the rest of the codebase always works with the normalised value.
- For Kelvin mode the numeric temperature is stored in a separate field (`color_temperature`), not in `white_balance` itself — the WB field only ever holds the string `"Kelvin"`.
- Fine tune is independent of WB mode; it is present for every mode including Kelvin.
