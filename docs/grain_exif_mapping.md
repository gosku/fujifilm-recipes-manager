# Fujifilm Grain Effect — EXIF Mapping


## EXIF fields involved

| Field | Exiftool tag | Notes |
|---|---|---|
| `grain_effect_roughness` | `Grain Effect Roughness` | `"Off"`, `"Weak"`, or `"Strong"` |
| `grain_effect_size` | `Grain Effect Size` | `"Off"`, `"Small"`, or `"Large"` |

## Full mapping table

| Camera menu setting | `grain_effect_roughness` | `grain_effect_size` |
|---|---|---|
| Grain Effect: Off | `Off` | `Off` |
| Grain Effect: Weak, Small | `Weak` | `Small` |
| Grain Effect: Weak, Large | `Weak` | `Large` |
| Grain Effect: Strong, Small | `Strong` | `Small` |
| Grain Effect: Strong, Large | `Strong` | `Large` |

## Key observations

- The EXIF values map directly to recipe card display values — no translation needed.
- `grain_effect_size` is **always `"Off"`** when `grain_effect_roughness` is `"Off"`.
  The camera never stores a size value independently of roughness.
- When `grain_effect_roughness` is `"Weak"` or `"Strong"`, `grain_effect_size` is
  always either `"Small"` or `"Large"` — never `"Off"`.
- Recipe cards combine both fields into a single label: `"Off"`, `"Weak Small"`,
  `"Weak Large"`, `"Strong Small"`, or `"Strong Large"`.
