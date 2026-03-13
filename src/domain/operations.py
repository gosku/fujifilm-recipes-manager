import dataclasses
import os

from src.data.models import FujifilmExif, Image, RECIPE_FIELDS
from src.domain import events
from src.domain.queries import parse_exif_date, read_image_exif


class NoFilmSimulationError(Exception):
    """Raised when an image has no film simulation in its EXIF data."""

    def __init__(self, image_path: str) -> None:
        self.image_path = image_path
        super().__init__(f"No film simulation found in {image_path}")



def process_image(image_path: str) -> Image:
    """Read EXIF data from *image_path* and persist it to the database.

    If a record for the same filepath already exists it is updated in-place.
    A FujifilmExif record is looked up or created for the image's EXIF field
    combination and linked via the recipe FK.

    Raises:
        NoFilmSimulationError: If the image has no film simulation EXIF data.
    """
    metadata = read_image_exif(image_path)

    if metadata.camera_make.upper() != "FUJIFILM":
        raise NoFilmSimulationError(image_path)
    filename = os.path.basename(image_path)

    # Convert date string to timezone-aware datetime
    date_taken = parse_exif_date(metadata.date_taken) if metadata.date_taken else None

    exif_fields = dataclasses.asdict(metadata)
    exif_fields.pop("date_taken")
    recipe_fields = {field: exif_fields.pop(field) for field in RECIPE_FIELDS}

    fujifilm_exif, _ = FujifilmExif.objects.get_or_create(**recipe_fields)
    image, created = Image.objects.update_or_create(
        filepath=image_path,
        defaults={"filename": filename, "date_taken": date_taken, "recipe": fujifilm_exif, **exif_fields},
    )

    event_params = {
        "recipe_id": image.pk,
        "filename": filename,
        "film_simulation": fujifilm_exif.film_simulation,
        "date_taken": image.date_taken.isoformat() if image.date_taken else "",
    }
    events.publish_event(
        event_type=events.RECIPE_IMAGE_CREATED if created else events.RECIPE_IMAGE_UPDATED,
        params=event_params,
    )
    return image
