from django.core.management.base import BaseCommand

from src.domain.operations import NoFilmSimulationError, process_image
from src.domain.queries import collect_image_paths


class Command(BaseCommand):
    help = "Process every JPG image found in the given folder synchronously (no Celery)."

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str, help="Path to the folder containing images.")

    def handle(self, *args, **options):
        folder = options["folder"]
        self.stdout.write(f"Scanning {folder} for JPG files…")

        paths = collect_image_paths(folder)
        total = len(paths)
        self.stdout.write(f"Found {total} images. Processing…")

        for path in paths:
            try:
                process_image(path)
            except NoFilmSimulationError:
                self.stderr.write(f"Skipped {path} (no film simulation)")

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {total} images."))
