from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest
from src.data.models import FujifilmExif, Image
from src.domain.queries import AmbiguousImageMatch, ImageNotFound, find_image_for_path
from src.domain.operations import process_image

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "images"
FIXTURE_IMAGE = str(FIXTURES_DIR / "XS107114.JPG")

# UTC equivalent of the fixture image's DateTimeOriginal (2025-12-31T12:23:57+11:00)
FIXTURE_DATE_UTC = datetime(2025, 12, 31, 1, 23, 57, tzinfo=timezone.utc)


@pytest.mark.django_db
class TestFindImageForPath:
    def test_returns_matching_image(self):
        image = process_image(FIXTURE_IMAGE)

        result = find_image_for_path(FIXTURE_IMAGE)

        assert result.pk == image.pk

    def test_raises_image_not_found_when_no_record_in_db(self):
        with pytest.raises(ImageNotFound):
            find_image_for_path(FIXTURE_IMAGE)

    def test_raises_ambiguous_image_match_when_multiple_records(self):
        Image.objects.create(filename="XS107114.JPG", filepath="/a/XS107114.JPG", date_taken=FIXTURE_DATE_UTC)
        Image.objects.create(filename="XS107114.JPG", filepath="/b/XS107114.JPG", date_taken=FIXTURE_DATE_UTC)

        with pytest.raises(AmbiguousImageMatch):
            find_image_for_path(FIXTURE_IMAGE)

    def test_continues_to_next_strategy_after_multiple_matches(self):
        # Strategy 1 (_by_filename_and_date): no match — wrong filename.
        # Strategy 2 (_by_date_and_image_count): multiple — both records share image_count.
        # Strategy 3 (_by_date_film_and_wb): 1 match — film_simulation differs.
        exif_a = FujifilmExif.objects.create(image_count="18069", film_simulation="Classic Negative", white_balance_fine_tune="Red +3, Blue -5")
        exif_b = FujifilmExif.objects.create(image_count="18069", film_simulation="Classic Chrome", white_balance_fine_tune="Red +0, Blue +0")
        image_a = Image.objects.create(filename="BURST001.JPG", filepath="/a/BURST001.JPG", date_taken=FIXTURE_DATE_UTC, fujifilm_exif=exif_a)
        Image.objects.create(filename="BURST002.JPG", filepath="/b/BURST002.JPG", date_taken=FIXTURE_DATE_UTC, fujifilm_exif=exif_b)

        # Fixture image has film_simulation="Classic Negative" and matching WB fine tune
        result = find_image_for_path(FIXTURE_IMAGE)

        assert result.pk == image_a.pk

    def test_disambiguates_burst_shots_by_image_count(self):
        # Two burst shots at the same second — only image_count differs.
        # The fixture image has image_count="18069".
        exif_a = FujifilmExif.objects.create(image_count="18069")
        exif_b = FujifilmExif.objects.create(image_count="18070")
        image_a = Image.objects.create(filename="BURST001.JPG", filepath="/a/BURST001.JPG", date_taken=FIXTURE_DATE_UTC, fujifilm_exif=exif_a)
        Image.objects.create(filename="BURST002.JPG", filepath="/b/BURST002.JPG", date_taken=FIXTURE_DATE_UTC, fujifilm_exif=exif_b)

        result = find_image_for_path(FIXTURE_IMAGE)

        assert result.pk == image_a.pk
