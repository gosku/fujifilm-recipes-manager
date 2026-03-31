import attrs

from src.data import models
from src.domain.images import operations, queries


@attrs.frozen
class FavoriteFolderResult:
    marked: tuple[str, ...]
    skipped: tuple[str, ...]


def mark_images_in_folder_as_favorite(*, folder: str) -> FavoriteFolderResult:
    """Mark every Fujifilm image found under *folder* as a favourite.

    Returns a result describing which files were marked and which were
    skipped due to missing Fujifilm metadata.
    """
    paths = queries.collect_image_paths(folder=folder)
    marked: list[str] = []
    skipped: list[str] = []
    for path in paths:
        try:
            mark_image_as_favorite(image_path=path)
            marked.append(path)
        except operations.NoFilmSimulationError:
            skipped.append(path)
    return FavoriteFolderResult(marked=tuple(marked), skipped=tuple(skipped))


def mark_image_as_favorite(*, image_path: str) -> models.Image:
    """Find or process the Image for *image_path* and mark it as a favourite.

    If the image is not yet in the database, or the match is ambiguous,
    it is first processed and stored via process_image().

    Raises:
        operations.NoFilmSimulationError: If the image has no Fujifilm metadata.
    """
    try:
        image = queries.find_image_for_path(image_path=image_path)
    except (queries.ImageNotFound, queries.AmbiguousImageMatch):
        image = operations.process_image(image_path=image_path)
    image.set_as_favorite()
    return image
