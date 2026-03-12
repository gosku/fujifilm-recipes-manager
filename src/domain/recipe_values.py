"""
Typed values for FujifilmRecipe model fields.

Enum *values* are the exact strings stored in the database (as returned by
exiftool).  Distinct values were sourced directly from the data_fujifilmrecipe
table.

Recipe card ↔ DB translation:
  - .recipe_card_label  → recipe card display string
  - .from_recipe_card() → parse recipe card string into the enum
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


# ---------------------------------------------------------------------------
# film_simulation  (EXIF tag: Film Mode)
# ---------------------------------------------------------------------------

class FilmSimulation(str, Enum):
    CLASSIC_CHROME = "Classic Chrome"
    CLASSIC_NEGATIVE = "Classic Negative"
    ETERNA = "Eterna"
    PROVIA = "F0/Standard (Provia)"
    PRO_NEG_STD = "Pro Neg. Std"
    VELVIA = "F2/Fujichrome (Velvia)"
    ASTIA = "F1b/Studio Portrait Smooth Skin Tone (Astia)"
    BLEACH_BYPASS = "Bleach Bypass"
    PRO_NEG_HI = "Pro Neg. Hi"

    @property
    def recipe_card_label(self) -> str:
        return _FILM_SIMULATION_LABELS[self]

    @classmethod
    def from_recipe_card(cls, label: str) -> FilmSimulation:
        return _FILM_SIMULATION_FROM_LABEL[label]


_FILM_SIMULATION_LABELS: dict[FilmSimulation, str] = {
    FilmSimulation.CLASSIC_CHROME: "CLASSIC CHROME",
    FilmSimulation.CLASSIC_NEGATIVE: "CLASSIC Neg.",
    FilmSimulation.ETERNA: "ETERNA/CINEMA",
    FilmSimulation.PROVIA: "PROVIA/STANDARD",
    FilmSimulation.PRO_NEG_STD: "PRO Neg. Std",
    FilmSimulation.VELVIA: "VELVIA/VIVID",
    FilmSimulation.ASTIA: "ASTIA/SOFT",
    FilmSimulation.BLEACH_BYPASS: "ETERNA BLEACH BYPASS",
    FilmSimulation.PRO_NEG_HI: "PRO Neg. Hi",
}
_FILM_SIMULATION_FROM_LABEL: dict[str, FilmSimulation] = {
    v: k for k, v in _FILM_SIMULATION_LABELS.items()
}


# ---------------------------------------------------------------------------
# white_balance  (EXIF tag: White Balance)
# ---------------------------------------------------------------------------

class WhiteBalance(str, Enum):
    AUTO = "Auto"
    DAYLIGHT = "Daylight"
    KELVIN = "Kelvin"
    INCANDESCENT = "Incandescent"
    DAYLIGHT_FLUORESCENT = "Daylight Fluorescent"
    AUTO_WHITE_PRIORITY = "Auto (white priority)"

    @property
    def recipe_card_label(self) -> str:
        return _WHITE_BALANCE_LABELS[self]

    @classmethod
    def from_recipe_card(cls, label: str) -> WhiteBalance:
        """
        Parse a recipe card WB label such as 'AUTO', 'DAYLIGHT', '5200K'.
        Temperature labels (e.g. '5200K') return WhiteBalance.KELVIN;
        the numeric value goes into the separate color_temperature field.
        """
        if re.match(r"^\d+K$", label):
            return cls.KELVIN
        return _WHITE_BALANCE_FROM_LABEL[label]


_WHITE_BALANCE_LABELS: dict[WhiteBalance, str] = {
    WhiteBalance.AUTO: "AUTO",
    WhiteBalance.DAYLIGHT: "DAYLIGHT",
    WhiteBalance.KELVIN: "{temp}K",  # substitute actual temp, e.g. "5200K"
    WhiteBalance.INCANDESCENT: "INCANDESCENT",
    WhiteBalance.DAYLIGHT_FLUORESCENT: "DAYLIGHT FLUORESCENT",
    WhiteBalance.AUTO_WHITE_PRIORITY: "AUTO WHITE PRIORITY",
}
_WHITE_BALANCE_FROM_LABEL: dict[str, WhiteBalance] = {
    v: k for k, v in _WHITE_BALANCE_LABELS.items() if "{temp}" not in v
}


# ---------------------------------------------------------------------------
# white_balance_fine_tune  (EXIF tag: White Balance Fine Tune, normalised ÷20)
# ---------------------------------------------------------------------------

@dataclass
class WhiteBalanceFineTune:
    """
    WB fine-tune stored as e.g. 'Red +2, Blue -4'.
    Values match recipe card display values directly (already ÷20 from raw EXIF).
    Observed range in DB: -9 to +9 for both channels.
    """
    red: int
    blue: int

    def __str__(self) -> str:
        return f"Red {self.red:+d}, Blue {self.blue:+d}"

    @classmethod
    def from_string(cls, s: str) -> WhiteBalanceFineTune:
        """Parse a normalised WB fine-tune string, e.g. 'Red +2, Blue -4'."""
        m_red = re.search(r"Red\s+([+-]?\d+)", s)
        m_blue = re.search(r"Blue\s+([+-]?\d+)", s)
        return cls(
            red=int(m_red.group(1)) if m_red else 0,
            blue=int(m_blue.group(1)) if m_blue else 0,
        )


# ---------------------------------------------------------------------------
# dynamic_range        (EXIF tag: Dynamic Range)         — always "Standard" in DB
# dynamic_range_setting (EXIF tag: Dynamic Range Setting) — "Auto" | "Manual"
# development_dynamic_range (EXIF tag: Development Dynamic Range) — the meaningful DR value
#
# Recipe cards show a single 'DR Range' field; use DevelopmentDynamicRange.
# ---------------------------------------------------------------------------

class DevelopmentDynamicRange(str, Enum):
    """
    Value = exiftool 'Development Dynamic Range' string.
    This is the field that actually encodes the DR setting from recipe cards.
    DR Auto results in an empty string (camera decides at shoot time).
    """
    AUTO = ""      # dynamic_range_setting = "Auto"
    DR100 = "100"
    DR200 = "200"
    DR400 = "400"
    DR800 = "800"  # requires ISO >= 1600

    @property
    def recipe_card_label(self) -> str:
        return _DDR_LABELS[self]

    @property
    def dynamic_range_setting(self) -> str:
        """Companion 'Dynamic Range Setting' EXIF field value."""
        return "Auto" if self == DevelopmentDynamicRange.AUTO else "Manual"

    @classmethod
    def from_recipe_card(cls, label: str) -> DevelopmentDynamicRange:
        return _DDR_FROM_LABEL[label]


_DDR_LABELS: dict[DevelopmentDynamicRange, str] = {
    DevelopmentDynamicRange.AUTO: "Auto",
    DevelopmentDynamicRange.DR100: "DR100",
    DevelopmentDynamicRange.DR200: "DR200",
    DevelopmentDynamicRange.DR400: "DR400",
    DevelopmentDynamicRange.DR800: "DR800",
}
_DDR_FROM_LABEL: dict[str, DevelopmentDynamicRange] = {
    v: k for k, v in _DDR_LABELS.items()
}


# ---------------------------------------------------------------------------
# color_chrome_effect  (EXIF tag: Color Chrome Effect — recipe cards: CCE)
# ---------------------------------------------------------------------------

class ColorChromeEffect(str, Enum):
    OFF = "Off"
    WEAK = "Weak"
    STRONG = "Strong"

    @property
    def recipe_card_label(self) -> str:
        return self.value

    @classmethod
    def from_recipe_card(cls, label: str) -> ColorChromeEffect:
        return cls(label)


# ---------------------------------------------------------------------------
# color_chrome_fx_blue  (EXIF tag: Color Chrome FX Blue — recipe cards: CFXB)
# ---------------------------------------------------------------------------

class ColorChromeFxBlue(str, Enum):
    OFF = "Off"
    WEAK = "Weak"
    STRONG = "Strong"

    @property
    def recipe_card_label(self) -> str:
        return self.value

    @classmethod
    def from_recipe_card(cls, label: str) -> ColorChromeFxBlue:
        return cls(label)


# ---------------------------------------------------------------------------
# grain_effect_roughness  (EXIF tag: Grain Effect Roughness)
# grain_effect_size       (EXIF tag: Grain Effect Size)
#
# Recipe cards show a combined label e.g. "Strong Large" or "Off".
# ---------------------------------------------------------------------------

class GrainEffectRoughness(str, Enum):
    OFF = "Off"
    WEAK = "Weak"
    STRONG = "Strong"

    @property
    def recipe_card_label(self) -> str:
        return self.value

    @classmethod
    def from_recipe_card(cls, label: str) -> GrainEffectRoughness:
        return cls(label)


class GrainEffectSize(str, Enum):
    OFF = "Off"
    SMALL = "Small"
    LARGE = "Large"

    @property
    def recipe_card_label(self) -> str:
        return self.value

    @classmethod
    def from_recipe_card(cls, label: str) -> GrainEffectSize:
        return cls(label)


@dataclass
class GrainEffect:
    """Combined grain effect parsed from a recipe card label e.g. 'Strong Large' or 'Off'."""
    roughness: GrainEffectRoughness
    size: GrainEffectSize

    @classmethod
    def from_recipe_card(cls, label: str) -> GrainEffect:
        label = label.strip()
        if label.lower() == "off":
            return cls(roughness=GrainEffectRoughness.OFF, size=GrainEffectSize.OFF)
        parts = label.split()
        roughness = GrainEffectRoughness.from_recipe_card(parts[0])
        size = GrainEffectSize.from_recipe_card(parts[1]) if len(parts) > 1 else GrainEffectSize.SMALL
        return cls(roughness=roughness, size=size)

    @property
    def recipe_card_label(self) -> str:
        if self.roughness == GrainEffectRoughness.OFF:
            return "Off"
        return f"{self.roughness.value} {self.size.value}"


# ---------------------------------------------------------------------------
# Tonal / numeric fields
#
# These are stored as strings with a text label suffix by exiftool, e.g.
# "0 (normal)", "+1 (medium hard)", "-2 (soft)".  Half-step values are stored
# as bare floats ("0.5", "-0.5") without a label — this is an exiftool
# inconsistency across camera firmware versions.
#
# highlight_tone  (EXIF: Highlight Tone)
# shadow_tone     (EXIF: Shadow Tone)
# ---------------------------------------------------------------------------

class HighlightTone(str, Enum):
    MINUS_2 = "-2 (soft)"
    MINUS_1_5 = "-1.5"
    MINUS_1 = "-1 (medium soft)"
    MINUS_0_5 = "-0.5"
    ZERO = "0 (normal)"
    PLUS_0_5 = "0.5"
    PLUS_1 = "+1 (medium hard)"
    PLUS_1_5 = "1.5"
    PLUS_2 = "+2 (hard)"

    @property
    def numeric(self) -> float:
        return _TONE_NUMERIC[self]

    @classmethod
    def from_recipe_card(cls, value: str) -> HighlightTone:
        """Parse a recipe card numeric string e.g. '-1.0', '+2.0', '0'."""
        return _HIGHLIGHT_TONE_FROM_NUMERIC[float(value)]


_TONE_NUMERIC: dict[HighlightTone | ShadowTone, float] = {}  # populated below


class ShadowTone(str, Enum):
    MINUS_2 = "-2 (soft)"
    MINUS_1 = "-1 (medium soft)"
    MINUS_0_5 = "-0.5"
    ZERO = "0 (normal)"
    PLUS_1 = "+1 (medium hard)"
    PLUS_1_5 = "1.5"
    PLUS_2 = "+2 (hard)"
    PLUS_3 = "+3 (very hard)"

    @property
    def numeric(self) -> float:
        return _TONE_NUMERIC[self]

    @classmethod
    def from_recipe_card(cls, value: str) -> ShadowTone:
        """Parse a recipe card numeric string e.g. '+1.0', '-2.0', '0'."""
        return _SHADOW_TONE_FROM_NUMERIC[float(value)]


_HIGHLIGHT_TONE_MAP: dict[float, HighlightTone] = {
    -2.0: HighlightTone.MINUS_2,
    -1.5: HighlightTone.MINUS_1_5,
    -1.0: HighlightTone.MINUS_1,
    -0.5: HighlightTone.MINUS_0_5,
     0.0: HighlightTone.ZERO,
     0.5: HighlightTone.PLUS_0_5,
     1.0: HighlightTone.PLUS_1,
     1.5: HighlightTone.PLUS_1_5,
     2.0: HighlightTone.PLUS_2,
}
_SHADOW_TONE_MAP: dict[float, ShadowTone] = {
    -2.0: ShadowTone.MINUS_2,
    -1.0: ShadowTone.MINUS_1,
    -0.5: ShadowTone.MINUS_0_5,
     0.0: ShadowTone.ZERO,
     1.0: ShadowTone.PLUS_1,
     1.5: ShadowTone.PLUS_1_5,
     2.0: ShadowTone.PLUS_2,
     3.0: ShadowTone.PLUS_3,
}
_HIGHLIGHT_TONE_FROM_NUMERIC = _HIGHLIGHT_TONE_MAP
_SHADOW_TONE_FROM_NUMERIC = _SHADOW_TONE_MAP
_TONE_NUMERIC.update({v: k for k, v in _HIGHLIGHT_TONE_MAP.items()})
_TONE_NUMERIC.update({v: k for k, v in _SHADOW_TONE_MAP.items()})


# ---------------------------------------------------------------------------
# color        (EXIF: Saturation — recipe cards: Color)
# sharpness    (EXIF: Sharpness)
# noise_reduction (EXIF: Noise Reduction — recipe cards: ISO Denoise)
# ---------------------------------------------------------------------------

class Color(str, Enum):
    MINUS_4 = "-4 (lowest)"
    MINUS_2 = "-2 (low)"
    ZERO = "0 (normal)"
    PLUS_1 = "+1 (medium high)"
    PLUS_2 = "+2 (high)"
    PLUS_3 = "+3 (very high)"
    PLUS_4 = "+4 (highest)"

    @property
    def numeric(self) -> int:
        return _COLOR_NUMERIC[self]

    @classmethod
    def from_recipe_card(cls, value: str) -> Color:
        return _COLOR_FROM_NUMERIC[int(value)]


_COLOR_MAP: dict[int, Color] = {
    -4: Color.MINUS_4,
    -2: Color.MINUS_2,
     0: Color.ZERO,
     1: Color.PLUS_1,
     2: Color.PLUS_2,
     3: Color.PLUS_3,
     4: Color.PLUS_4,
}
_COLOR_FROM_NUMERIC = _COLOR_MAP
_COLOR_NUMERIC: dict[Color, int] = {v: k for k, v in _COLOR_MAP.items()}


class Sharpness(str, Enum):
    MINUS_3 = "-3 (very soft)"
    MINUS_2 = "-2 (soft)"
    MINUS_1 = "-1 (medium soft)"
    ZERO = "0 (normal)"
    PLUS_1 = "+1 (medium hard)"
    PLUS_2 = "+2 (hard)"
    PLUS_3 = "+3 (very hard)"
    PLUS_4 = "+4 (hardest)"

    @property
    def numeric(self) -> int:
        return _SHARPNESS_NUMERIC[self]

    @classmethod
    def from_recipe_card(cls, value: str) -> Sharpness:
        return _SHARPNESS_FROM_NUMERIC[int(value)]


_SHARPNESS_MAP: dict[int, Sharpness] = {
    -3: Sharpness.MINUS_3,
    -2: Sharpness.MINUS_2,
    -1: Sharpness.MINUS_1,
     0: Sharpness.ZERO,
     1: Sharpness.PLUS_1,
     2: Sharpness.PLUS_2,
     3: Sharpness.PLUS_3,
     4: Sharpness.PLUS_4,
}
_SHARPNESS_FROM_NUMERIC = _SHARPNESS_MAP
_SHARPNESS_NUMERIC: dict[Sharpness, int] = {v: k for k, v in _SHARPNESS_MAP.items()}


class NoiseReduction(str, Enum):
    """Recipe cards label this field 'ISO Denoise'."""
    MINUS_4 = "-4 (weakest)"
    MINUS_3 = "-3 (very weak)"
    MINUS_2 = "-2 (weak)"
    MINUS_1 = "-1 (medium weak)"
    ZERO = "0 (normal)"

    @property
    def numeric(self) -> int:
        return _NOISE_REDUCTION_NUMERIC[self]

    @classmethod
    def from_recipe_card(cls, value: str) -> NoiseReduction:
        return _NOISE_REDUCTION_FROM_NUMERIC[int(value)]


_NOISE_REDUCTION_MAP: dict[int, NoiseReduction] = {
    -4: NoiseReduction.MINUS_4,
    -3: NoiseReduction.MINUS_3,
    -2: NoiseReduction.MINUS_2,
    -1: NoiseReduction.MINUS_1,
     0: NoiseReduction.ZERO,
}
_NOISE_REDUCTION_FROM_NUMERIC = _NOISE_REDUCTION_MAP
_NOISE_REDUCTION_NUMERIC: dict[NoiseReduction, int] = {v: k for k, v in _NOISE_REDUCTION_MAP.items()}


# ---------------------------------------------------------------------------
# clarity  (EXIF: Clarity)
# Stored as a bare integer string in DB. Observed values: -4, 0, 2, 3.
# ---------------------------------------------------------------------------

CLARITY_RANGE = range(-5, 6)  # -5 to +5, step 1
