import pytest

from src.data import models
from src.domain.images import dataclasses as image_dataclasses
from src.domain.recipes.operations import get_or_create_recipe_from_data
from src.domain.recipes.validation import InvalidFujifilmRecipeData


def _make_data(**overrides: object) -> image_dataclasses.FujifilmRecipeData:
    base = dict(
        film_simulation="Provia",
        d_range_priority="Off",
        grain_roughness="Off",
        color_chrome_effect="Off",
        color_chrome_fx_blue="Off",
        white_balance="Auto",
        white_balance_red=0,
        white_balance_blue=0,
        sharpness="0",
        high_iso_nr="0",
        clarity="0",
        dynamic_range="DR100",
        highlight="0",
        shadow="0",
        color="0",
    )
    base.update(overrides)
    return image_dataclasses.FujifilmRecipeData(**base)


@pytest.mark.django_db
class TestGetOrCreateRecipeFromData:
    def test_raises_invalid_recipe_data_before_touching_db(self) -> None:
        # DRP active but dynamic_range is provided — structurally inconsistent.
        invalid_data = _make_data(d_range_priority="Auto", dynamic_range="DR100", highlight=None, shadow=None)
        with pytest.raises(InvalidFujifilmRecipeData) as exc_info:
            get_or_create_recipe_from_data(data=invalid_data)
        assert exc_info.value.field == "dynamic_range"
        assert models.FujifilmRecipe.objects.count() == 0
