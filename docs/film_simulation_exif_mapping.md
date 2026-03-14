# Fujifilm Film Simulation — EXIF Mapping


## EXIF fields involved

| Field | Exiftool tag | Notes |
|---|---|---|
| `film_simulation` | `Film Mode` | Set for all color simulations; **empty** for Acros, Monochrome, and Sepia |
| `color` | `Saturation` | Used to encode the simulation for Acros, Monochrome, and Sepia variants |

## Decoding logic

```
if film_simulation is not empty:
    → look up in Film Mode table below

elif color is not empty:
    → look up in Saturation table below
```

## Film Mode field values (color simulations)

| Camera menu name | `film_simulation` EXIF value | Display name |
|---|---|---|
| PROVIA/STANDARD | `F0/Standard (Provia)` | Provia |
| VELVIA/VIVID | `F2/Fujichrome (Velvia)` | Velvia |
| ASTIA/SOFT | `F1b/Studio Portrait Smooth Skin Tone (Astia)` | Astia |
| CLASSIC CHROME | `Classic Chrome` | Classic Chrome |
| PRO Neg. Std | `Pro Neg. Std` | Pro Neg. Std |
| PRO Neg. Hi | `Pro Neg. Hi` | Pro Neg. Hi |
| CLASSIC Neg. | `Classic Negative` | Classic Negative |
| ETERNA/CINEMA | `Eterna` | Eterna |
| ETERNA BLEACH BYPASS | `Bleach Bypass` | Eterna Bleach Bypass |
| Reala Ace | `Reala Ace` | Reala Ace |

> **Note:** `Reala Ace` follows the same pattern as other colour simulations (present in the `Film Mode` field).

## Saturation field values (Acros, Monochrome, Sepia)

When the camera is set to a monochromatic or sepia simulation, the `Film Mode`
field is **absent** from the EXIF.  The simulation is encoded in the `Saturation`
field instead.

| Camera menu name | `color` (Saturation) EXIF value | Display name |
|---|---|---|
| ACROS | `Acros` | Acros STD |
| ACROS + Ye | `Acros Yellow Filter` | Acros Yellow |
| ACROS + R | `Acros Red Filter` | Acros Red |
| ACROS + G | `Acros Green Filter` | Acros Green |
| MONOCHROME | `None (B&W)` | Monochrome STD |
| MONOCHROME + Ye | `B&W Yellow Filter` | Monochrome Yellow |
| MONOCHROME + R | `B&W Red Filter` | Monochrome Red |
| MONOCHROME + G | `B&W Green Filter` | Monochrome Green |
| SEPIA | `B&W Sepia` | Sepia |

> **Notes:**
> - When Saturation is a numeric label (e.g. `0 (normal)`, `+2 (high)`) the `Film Mode`
>   field is present and this lookup is not used.

## Key observations

- The dual-source design means you must check `Film Mode` first and fall back to
  `Saturation` — never use `Saturation` alone to determine the simulation for
  color modes (it holds the Color adjustment value there).
- For color simulations, `Saturation` holds the Color recipe setting (e.g.
  `+2 (high)`), not the simulation name.
- For B&W/Acros/Sepia, `Saturation` holds the simulation name and there is no
  separate Color adjustment.
