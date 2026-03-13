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

        # Standard image fields
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
        exif = image.recipe

        # Creative / recipe fields
        assert exif.film_simulation == "Classic Negative"
        assert exif.dynamic_range == "Standard"
        assert exif.dynamic_range_setting == "Manual"
        assert exif.development_dynamic_range == "400"
        assert exif.white_balance == "Auto"
        assert exif.white_balance_fine_tune == "Red +3, Blue -5"
        assert exif.sharpness == "-1 (medium soft)"
        assert exif.noise_reduction == "-4 (weakest)"
        assert exif.clarity == "0"
        assert exif.color_chrome_effect == "Off"
        assert exif.color_chrome_fx_blue == "Strong"
        assert exif.grain_effect_roughness == "Off"
        assert exif.grain_effect_size == "Off"

        # Autofocus fields
        assert exif.af_mode == "Zone"
        assert exif.focus_pixel == "2249 1209"
        assert exif.af_s_priority == "Focus"
        assert exif.af_c_priority == "Release"
        assert exif.focus_mode_2 == "AF-S"
        assert exif.pre_af == "Off"
        assert exif.af_area_mode == "Zone"
        assert exif.af_area_point_size == "n/a"
        assert exif.af_area_zone_size == "3 x 3"
        assert exif.af_c_setting == "Set 1 (multi-purpose)"
        assert exif.af_c_tracking_sensitivity == "2"
        assert exif.af_c_speed_tracking_sensitivity == "0"
        assert exif.af_c_zone_area_switching == "Auto"

        # Drive / misc fields
        assert exif.slow_sync == "Off"
        assert exif.auto_bracketing == "Off"
        assert exif.drive_speed == "n/a"
        assert exif.crop_mode == "n/a"
        assert exif.flicker_reduction == "Off (0x0002)"

        # Shot metadata fields
        assert exif.sequence_number == "0"
        assert exif.exposure_count == "1"
        assert exif.image_generation == "Original Image"
        assert exif.image_count == "18069"

        # Warning fields
        assert exif.blur_warning == "None"
        assert exif.focus_warning == "Good"
        assert exif.exposure_warning == "Good"

        # Lens info fields
        assert exif.min_focal_length == "35"
        assert exif.max_focal_length == "35"
        assert exif.max_aperture_at_min_focal == "2"
        assert exif.max_aperture_at_max_focal == "2"

        # Camera hardware fields
        assert exif.version == "0130"
        assert exif.internal_serial_number == "FF02B6275695     Y56201 2020:12:02 C6B310316B40"
        assert exif.fuji_model == "X-S10_0100"
        assert exif.fuji_model_2 == "X-S10_0100"

        # Face detection fields
        assert exif.faces_detected == "0"
        assert exif.num_face_elements == "0"

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
