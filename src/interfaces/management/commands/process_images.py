from django.core.management.base import BaseCommand

from src.domain import events
from src.domain.queries import collect_image_paths
from src.interfaces.tasks import process_image_task


class Command(BaseCommand):
    help = "Enqueue a Celery task for every JPG image found in the given folder."

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str, help="Path to the folder containing images.")

    def handle(self, *args, **options):
        folder = options["folder"]
        self.stdout.write(f"Scanning {folder} for JPG files…")

        paths = collect_image_paths(folder)
        total = len(paths)
        self.stdout.write(f"Found {total} images. Enqueuing tasks…")

        for path in paths:
            process_image_task.delay(path)
            events.publish_event(
                event_type=events.TASK_IMAGE_ENQUEUED,
                params={"image_path": path},
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully enqueued {total} tasks."))
