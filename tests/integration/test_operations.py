from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.data.models import Image
from src.domain import events
from src.domain.operations import process_image

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "images"
FIXTURE_IMAGE = str(FIXTURES_DIR / "XS107114.JPG")


@pytest.mark.django_db
class TestProcessImagePersistence:
    def test_creates_recipe_record(self, captured_logs):
        image = process_image(FIXTURE_IMAGE)
        assert isinstance(image, Image)
        assert image.pk is not None
        assert image.filename == "XS107114.JPG"
        assert image.filepath == FIXTURE_IMAGE
        assert image.camera_make == "FUJIFILM"
        assert image.camera_model == "X-S10"
        assert image.quality == "FINE"
        assert image.flash_mode == "Not Attached"
        assert image.flash_exposure_comp == "0"
        assert image.focus_mode == "Auto"
        assert image.shutter_type == "Mechanical"
        assert image.lens_modulation_optimizer == "On"
        assert image.picture_mode == "Aperture-priority AE"
        assert image.drive_mode == "Single"
        assert image.iso == "640"
        assert image.exposure_compensation == "+0.33"
        assert image.date_taken == datetime(2025, 12, 31, 12, 23, 57, tzinfo=timezone(timedelta(hours=11)))

        assert image.recipe is not None
        assert image.recipe.film_simulation == "Classic Negative"
        assert image.recipe.dynamic_range == "Standard"
        assert image.recipe.dynamic_range_setting == "Manual"
        assert image.recipe.development_dynamic_range == "400"
        assert image.recipe.white_balance == "Auto"
        assert image.recipe.white_balance_fine_tune == "Red +3, Blue -5"
        assert image.recipe.sharpness == "-1 (medium soft)"
        assert image.recipe.color_chrome_effect == "Off"
        assert image.recipe.color_chrome_fx_blue == "Strong"
        assert image.recipe.grain_effect_roughness == "Off"
        assert image.recipe.grain_effect_size == "Off"

        # Assert event was logged
        created_events = [e for e in captured_logs if e.get("event_type") == events.RECIPE_IMAGE_CREATED]
        assert len(created_events) == 1
        assert created_events[0]["params"]["filename"] == "XS107114.JPG"
        assert created_events[0]["params"]["film_simulation"] == "Classic Negative"
        assert created_events[0]["params"]["date_taken"] == "2025-12-31T12:23:57+11:00"
        assert created_events[0]["params"]["recipe_id"] == image.pk

    def test_updates_existing_record(self, captured_logs):
        image1 = process_image(FIXTURE_IMAGE)
        image2 = process_image(FIXTURE_IMAGE)

        assert image1.pk == image2.pk
        assert Image.objects.count() == 1

        # First call emits created, second call emits updated
        created_events = [e for e in captured_logs if e.get("event_type") == events.RECIPE_IMAGE_CREATED]
        assert len(created_events) == 1

        updated_events = [e for e in captured_logs if e.get("event_type") == events.RECIPE_IMAGE_UPDATED]
        assert len(updated_events) == 1
        assert updated_events[0]["params"]["recipe_id"] == image2.pk
        assert updated_events[0]["params"]["filename"] == "XS107114.JPG"
        assert updated_events[0]["params"]["film_simulation"] == "Classic Negative"
        assert updated_events[0]["params"]["date_taken"] == "2025-12-31T12:23:57+11:00"
