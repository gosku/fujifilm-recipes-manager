from django.core.management.base import BaseCommand

from src.application.usecases.images import favorite_images


class Command(BaseCommand):
    help = "Mark images in the given folder as favorites in the database."

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str, help="Path to the folder containing favorite images.")

    def handle(self, *args, **options):
        folder = options["folder"]
        self.stdout.write(f"Scanning {folder} for JPG files…")

        result = favorite_images.mark_images_in_folder_as_favorite(folder=folder)

        for path in result.marked:
            self.stdout.write(f"Marked as favorite: {path.split('/')[-1]}")
        for path in result.skipped:
            self.stderr.write(f"Skipped {path.split('/')[-1]}: no Fujifilm metadata.")

        self.stdout.write(self.style.SUCCESS(
            f"Done. {len(result.marked)} marked as favorite, {len(result.skipped)} not found."
        ))
