from pathlib import Path

from django.core.management.base import BaseCommand

from src.domain.operations import NoFilmSimulationError, process_image
from src.domain.queries import AmbiguousImageMatch, ImageNotFound, collect_image_paths, find_image_for_path


class Command(BaseCommand):
    help = "Mark images in the given folder as favorites in the database."

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str, help="Path to the folder containing favorite images.")

    def handle(self, *args, **options):
        folder = options["folder"]
        self.stdout.write(f"Scanning {folder} for JPG files…")

        paths = collect_image_paths(folder)
        self.stdout.write(f"Found {len(paths)} images.")

        marked = 0
        not_found = 0

        for path in paths:
            filename = Path(path).name
            try:
                image = find_image_for_path(path)
            except ImageNotFound:
                try:
                    image = process_image(path)
                    image.mark_as_favorite()
                    self.stdout.write(f"Added and marked as favorite: {filename}")
                    marked += 1
                except NoFilmSimulationError:
                    self.stderr.write(f"Skipped {filename}: not in DB and no Fujifilm metadata.")
                    not_found += 1
                continue
            except AmbiguousImageMatch:
                try:
                    image = process_image(path)
                    image.mark_as_favorite()
                    self.stdout.write(f"Added and marked as favorite: {filename}")
                    marked += 1
                except NoFilmSimulationError:
                    self.stderr.write(f"Skipped {filename}: ambiguous in DB and no Fujifilm metadata.")
                    not_found += 1
                continue

            image.mark_as_favorite()
            self.stdout.write(f"Marked as favorite: {filename}")
            marked += 1

        self.stdout.write(self.style.SUCCESS(f"Done. {marked} marked as favorite, {not_found} not found."))
