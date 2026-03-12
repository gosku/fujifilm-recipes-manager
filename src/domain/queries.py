import os
import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.domain.dataclasses import ImageExifData

EXIFTOOL_FIELD_MAP = {
    "Make": "camera_make",
    "Camera Model Name": "camera_model",
    "Film Mode": "film_simulation",
    "Quality": "quality",
    "Dynamic Range": "dynamic_range",
    "Dynamic Range Setting": "dynamic_range_setting",
    "Development Dynamic Range": "development_dynamic_range",
    "White Balance": "white_balance",
    "White Balance Fine Tune": "white_balance_fine_tune",
    "Color Temperature": "color_temperature",
    "Highlight Tone": "highlight_tone",
    "Shadow Tone": "shadow_tone",
    "Saturation": "color",
    "Sharpness": "sharpness",
    "Noise Reduction": "noise_reduction",
    "Clarity": "clarity",
    "Color Chrome Effect": "color_chrome_effect",
    "Color Chrome FX Blue": "color_chrome_fx_blue",
    "Grain Effect Roughness": "grain_effect_roughness",
    "Grain Effect Size": "grain_effect_size",
    "Fuji Flash Mode": "flash_mode",
    "Flash Exposure Comp": "flash_exposure_comp",
    "Focus Mode": "focus_mode",
    "Shutter Type": "shutter_type",
    "Lens Modulation Optimizer": "lens_modulation_optimizer",
    "Picture Mode": "picture_mode",
    "Drive Mode": "drive_mode",
    "Image Stabilization": "image_stabilization",
    "ISO": "iso",
    "Exposure Compensation": "exposure_compensation",
    "Date/Time Original": "date_taken",
}

_EXIF_DATE_RE = re.compile(
    r"^(\d{4}):(\d{2}):(\d{2}) (\d{2}):(\d{2}):(\d{2})(?:([+-]\d{2}:\d{2}))?$"
)

_WB_FINE_TUNE_RE = re.compile(r"(Red|Blue)\s+([+-]?\d+)")

# Regex to strip the [Group] prefix added by exiftool -G1
_G1_PREFIX_RE = re.compile(r"^\[(\w+)\]\s+")

# When a field appears in multiple groups, use the value from this group.
# Default is FujiFilm; fields listed here override that default.
_DEFAULT_GROUP = "FujiFilm"
_GROUP_OVERRIDES = {
    "date_taken": "Composite",
}


def parse_exif_date(value: str) -> datetime | None:
    """Parse an exiftool date string into a timezone-aware datetime."""
    m = _EXIF_DATE_RE.match(value.strip())
    if not m:
        return None
    year, month, day, hour, minute, second = (int(g) for g in m.groups()[:6])
    tz_str = m.group(7)
    if tz_str:
        sign = 1 if tz_str[0] == "+" else -1
        tz_h, tz_m = tz_str[1:].split(":")
        tz = timezone(timedelta(hours=sign * int(tz_h), minutes=sign * int(tz_m)))
    else:
        tz = timezone.utc
    return datetime(year, month, day, hour, minute, second, tzinfo=tz)


def _normalise_wb_fine_tune(raw: str) -> str:
    """Divide exiftool White Balance Fine Tune values by 20 to get camera values."""
    def _divide(m: re.Match) -> str:
        return f"{m.group(1)} {int(m.group(2)) // 20:+d}"
    return _WB_FINE_TUNE_RE.sub(_divide, raw)


def read_image_exif(image_path: str) -> ImageExifData:
    """Run exiftool on the given image and return a dict of recipe-relevant fields."""
    result = subprocess.run(
        ["exiftool", "-a", "-G1", image_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"exiftool failed for {image_path}: {result.stderr}")

    # Collect all (group, value) occurrences per field
    all_values: dict[str, list[tuple[str, str]]] = {}
    for line in result.stdout.splitlines():
        m = _G1_PREFIX_RE.match(line)
        if not m:
            continue
        group = m.group(1)
        rest = line[m.end():]
        if ":" not in rest:
            continue
        key, _, val = rest.partition(":")
        key = key.strip()
        val = val.strip()
        if key in EXIFTOOL_FIELD_MAP:
            field = EXIFTOOL_FIELD_MAP[key]
            all_values.setdefault(field, []).append((group, val))

    metadata: dict[str, str] = {}
    for field, occurrences in all_values.items():
        preferred_group = _GROUP_OVERRIDES.get(field, _DEFAULT_GROUP)
        value = next((v for g, v in occurrences if g == preferred_group), occurrences[0][1])
        metadata[field] = value
    if "white_balance_fine_tune" in metadata:
        metadata["white_balance_fine_tune"] = _normalise_wb_fine_tune(
            metadata["white_balance_fine_tune"]
        )
    return ImageExifData(**metadata)


def collect_image_paths(folder: str) -> list[str]:
    """Return absolute paths of all JPG files inside *folder* (recursively)."""
    root = Path(folder)
    if not root.is_dir():
        raise FileNotFoundError(f"Directory not found: {folder}")

    extensions = {".jpg", ".jpeg"}
    paths: list[str] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            if Path(fname).suffix.lower() in extensions:
                paths.append(os.path.join(dirpath, fname))

    paths.sort()
    return paths
