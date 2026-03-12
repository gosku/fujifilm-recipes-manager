from pathlib import Path

import pytest
from django.core.management import call_command

from src.data.models import Image
from src.domain import events

FIXTURES_DIR = str(Path(__file__).resolve().parent.parent / "fixtures" / "images")


@pytest.mark.django_db
class TestProcessImagesSyncCommand:
    def test_processes_all_images_in_folder(self, capsys, captured_logs):
        call_command("process_images_sync", FIXTURES_DIR)
        assert Image.objects.count() == 6

        captured = capsys.readouterr()
        assert "Successfully processed 7 images." in captured.out

        created = [e for e in captured_logs if e.get("event_type") == events.RECIPE_IMAGE_CREATED]
        assert len(created) == 6
