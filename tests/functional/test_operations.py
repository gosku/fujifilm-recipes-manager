from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from src.data.models import Image
from src.domain.operations import process_image

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "images"
SAMPLE_IMAGE = str(FIXTURES_DIR / "XS107508.jpg")


@pytest.mark.django_db
class TestProcessImageEndToEnd:
    """End-to-end tests that run exiftool against a real Fujifilm image."""

    def test_extracts_and_stores_recipe(self):
        image = process_image(SAMPLE_IMAGE)

        assert image.pk is not None
        assert image.filename == "XS107508.jpg"
        assert image.filepath == SAMPLE_IMAGE

        # Camera
        assert image.camera_make == "FUJIFILM"
        assert image.camera_model == "X-S10"

        # Shooting settings
        assert image.quality == "FINE"
        assert image.flash_mode == "Not Attached"
        assert image.flash_exposure_comp == "0"
        assert image.focus_mode == "Auto"
        assert image.shutter_type == "Mechanical"
        assert image.lens_modulation_optimizer == "On"
        assert image.picture_mode == "Aperture-priority AE"
        assert image.drive_mode == "Single"

        # Exposure
        assert image.iso == "1600"
        assert image.exposure_compensation == "+0.33"

        # Date
        assert image.date_taken == datetime(2026, 3, 9, 9, 29, 32, tzinfo=timezone(timedelta(hours=11)))

        # Recipe
        assert image.recipe is not None
        assert image.recipe.film_simulation == "Classic Negative"
        assert image.recipe.dynamic_range == "Standard"
        assert image.recipe.dynamic_range_setting == "Manual"
        assert image.recipe.development_dynamic_range == "400"
        assert image.recipe.white_balance == "Auto"
        assert image.recipe.white_balance_fine_tune == "Red +3, Blue -5"
        assert image.recipe.highlight_tone == "0 (normal)"
        assert image.recipe.shadow_tone == "+1 (medium hard)"
        assert image.recipe.color == "+4 (highest)"
        assert image.recipe.sharpness == "-1 (medium soft)"
        assert image.recipe.noise_reduction == "-4 (weakest)"
        assert image.recipe.clarity == "0"
        assert image.recipe.color_chrome_effect == "Off"
        assert image.recipe.color_chrome_fx_blue == "Strong"
        assert image.recipe.grain_effect_roughness == "Off"
        assert image.recipe.grain_effect_size == "Off"

    def test_is_idempotent(self):
        image1 = process_image(SAMPLE_IMAGE)
        image2 = process_image(SAMPLE_IMAGE)

        assert image1.pk == image2.pk
        assert Image.objects.filter(filepath=SAMPLE_IMAGE).count() == 1

    def test_persists_to_database(self):
        process_image(SAMPLE_IMAGE)

        from_db = Image.objects.get(filepath=SAMPLE_IMAGE)
        assert from_db.recipe.film_simulation == "Classic Negative"
        assert from_db.camera_make == "FUJIFILM"
