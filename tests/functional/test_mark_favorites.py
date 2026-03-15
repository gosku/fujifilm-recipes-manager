import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from django.core.management import call_command

from src.data.models import Image
from src.domain.operations import NoFilmSimulationError
from src.domain.queries import AmbiguousImageMatch, ImageNotFound

FIXTURES_DIR = str(Path(__file__).resolve().parent.parent / "fixtures" / "images")


@pytest.mark.django_db
class TestMarkFavoritesCommand:
    def test_marks_matching_images_as_favorite(self, capsys):
        call_command("process_images_sync", FIXTURES_DIR)
        total = Image.objects.count()
        assert total > 0

        call_command("mark_favorites", FIXTURES_DIR)

        assert Image.objects.filter(is_favorite=True).count() == total

    def test_adds_unimported_fujifilm_image_as_favorite(self, tmp_path, capsys):
        fixture_image = Path(FIXTURES_DIR) / "XS107114.JPG"
        shutil.copy(fixture_image, tmp_path / fixture_image.name)

        call_command("mark_favorites", str(tmp_path))

        captured = capsys.readouterr()
        assert "Added and marked as favorite" in captured.out
        image = Image.objects.get(filename="XS107114.JPG")
        assert image.is_favorite is True

    def test_skips_image_with_no_fujifilm_metadata(self, tmp_path, capsys):
        fixture_image = Path(FIXTURES_DIR) / "XS107114.JPG"
        shutil.copy(fixture_image, tmp_path / fixture_image.name)

        with patch("src.interfaces.management.commands.mark_favorites.find_image_for_path", side_effect=ImageNotFound):
            with patch("src.interfaces.management.commands.mark_favorites.process_image", side_effect=NoFilmSimulationError("dummy")):
                call_command("mark_favorites", str(tmp_path))

        captured = capsys.readouterr()
        assert "Skipped" in captured.err
        assert "no Fujifilm metadata" in captured.err
        assert Image.objects.count() == 0

    def test_adds_ambiguous_fujifilm_image_as_new_favorite(self, tmp_path, capsys):
        fixture_image = Path(FIXTURES_DIR) / "XS107114.JPG"
        shutil.copy(fixture_image, tmp_path / fixture_image.name)

        with patch("src.interfaces.management.commands.mark_favorites.find_image_for_path", side_effect=AmbiguousImageMatch):
            call_command("mark_favorites", str(tmp_path))

        captured = capsys.readouterr()
        assert "Added and marked as favorite" in captured.out
        assert Image.objects.filter(is_favorite=True).count() == 1

    def test_skips_ambiguous_image_with_no_fujifilm_metadata(self, tmp_path, capsys):
        fixture_image = Path(FIXTURES_DIR) / "XS107114.JPG"
        shutil.copy(fixture_image, tmp_path / fixture_image.name)

        with patch("src.interfaces.management.commands.mark_favorites.find_image_for_path", side_effect=AmbiguousImageMatch):
            with patch("src.interfaces.management.commands.mark_favorites.process_image", side_effect=NoFilmSimulationError("dummy")):
                call_command("mark_favorites", str(tmp_path))

        captured = capsys.readouterr()
        assert "Skipped" in captured.err
        assert "no Fujifilm metadata" in captured.err
        assert Image.objects.count() == 0

    def test_does_not_affect_other_images(self, capsys):
        call_command("process_images_sync", FIXTURES_DIR)

        fixture_image = Path(FIXTURES_DIR) / "XS107114.JPG"

        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(fixture_image, Path(tmp) / fixture_image.name)
            call_command("mark_favorites", tmp)

        favorites = Image.objects.filter(is_favorite=True)
        non_favorites = Image.objects.filter(is_favorite=False)
        assert favorites.count() == 1
        assert favorites.first().filename == "XS107114.JPG"
        assert non_favorites.count() == Image.objects.count() - 1
