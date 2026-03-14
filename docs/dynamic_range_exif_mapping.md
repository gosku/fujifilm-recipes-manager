# Fujifilm Dynamic Range — EXIF Mapping


## EXIF fields involved

| Field | Exiftool tag | Notes |
|---|---|---|
| `dynamic_range` | `Dynamic Range` | Always `"Standard"` on modern X-series — not useful |
| `dynamic_range_setting` | `Dynamic Range Setting` | `"Manual"` or `"Auto"` |
| `development_dynamic_range` | `Development Dynamic Range` | The actual DR value: `"100"`, `"200"`, `"400"` |
| `auto_dynamic_range` | `Auto Dynamic Range` | Set when DR-Auto is active, e.g. `"200%"` |
| `d_range_priority` | `D Range Priority` | `"Auto"` or `"Fixed"` when D-Range Priority is active |
| `d_range_priority_auto` | `D Range Priority Auto` | `"Weak"` or `"Strong"` when `d_range_priority = "Fixed"` |
| `picture_mode` | `Picture Mode` | `"HDR"` when HDR drive mode is active |

## Full mapping table

| Camera setting | `dynamic_range_setting` | `development_dynamic_range` | `d_range_priority` | `d_range_priority_auto` | `picture_mode` |
|---|---|---|---|---|---|
| DR100 | `Manual` | `100` | — | — | (normal) |
| DR-Auto | `Auto` | — | — | — | (normal) |
| DR200 | `Manual` | `200` | — | — | (normal) |
| DR400 | `Manual` | `400` | — | — | (normal) |
| D-Range Priority Auto | — | — | `Auto` | — | (normal) |
| D-Range Priority Weak | — | — | `Fixed` | `Weak` | (normal) |
| D-Range Priority Strong | — | — | `Fixed` | `Strong` | (normal) |
| HDR drive mode (800%) | `Manual` | `800` | — | — | `HDR` |

## Key observations

- `dynamic_range` is always `"Standard"` on modern X-series cameras and carries no useful information.
- **DR-Auto** (`dynamic_range_setting = "Auto"`) and **manual DR** (`dynamic_range_setting = "Manual"`) are mutually exclusive with **D-Range Priority** — when `d_range_priority` is present, the `dynamic_range_setting` / `development_dynamic_range` fields are absent.
- **DR800** does not appear as a user-facing menu option on modern X-series cameras (max is DR400). A `development_dynamic_range = "800"` record indicates the image was shot in **HDR drive mode**, identifiable by `picture_mode = "HDR"`. HDR drive mode is not a recipe setting.
- When DR-Auto is active, `auto_dynamic_range` records the value the camera actually applied (e.g. `"200%"`), but this field is not always stored.

## Decoding logic for `dynamic_range` recipe field

```
if picture_mode == "HDR":
    → not a recipe image, skip

if d_range_priority == "Auto":
    → "D-Range Priority Auto"
elif d_range_priority == "Fixed" and d_range_priority_auto == "Weak":
    → "D-Range Priority Weak"
elif d_range_priority == "Fixed" and d_range_priority_auto == "Strong":
    → "D-Range Priority Strong"
elif dynamic_range_setting == "Auto":
    → "DR-Auto"
elif development_dynamic_range == "100":
    → "DR100"
elif development_dynamic_range == "200":
    → "DR200"
elif development_dynamic_range == "400":
    → "DR400"
```
