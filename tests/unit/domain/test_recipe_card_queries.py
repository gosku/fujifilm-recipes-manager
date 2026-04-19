import json

import pytest

from src.data import models
from src.domain.recipes.cards import queries, templates


def _recipe(**kwargs: object) -> models.FujifilmRecipe:
    """Return an unsaved FujifilmRecipe with sensible defaults, overridable via kwargs."""
    defaults: dict[str, object] = {
        "film_simulation": "Provia",
        "dynamic_range": "DR100",
        "d_range_priority": "Off",
        "grain_roughness": "Off",
        "grain_size": "Off",
        "color_chrome_effect": "Off",
        "color_chrome_fx_blue": "Off",
        "white_balance": "Auto",
        "white_balance_red": 0,
        "white_balance_blue": 0,
    }
    defaults.update(kwargs)
    return models.FujifilmRecipe(**defaults)


class TestGetRecipeAsJson:
    def test_includes_version_key(self) -> None:
        payload = json.loads(queries.get_recipe_as_json(recipe=_recipe()))
        assert payload["v"] == 1

    def test_includes_film_simulation(self) -> None:
        payload = json.loads(queries.get_recipe_as_json(recipe=_recipe(film_simulation="Classic Chrome")))
        assert payload["film_simulation"] == "Classic Chrome"

    def test_output_is_minified(self) -> None:
        result = queries.get_recipe_as_json(recipe=_recipe())
        assert " " not in result

    def test_omits_color_only_fields_for_monochromatic_simulation(self) -> None:
        recipe = _recipe(film_simulation="Acros STD", color=None, color_chrome_effect=None, color_chrome_fx_blue=None)
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert "color" not in payload
        assert "color_chrome_effect" not in payload
        assert "color_chrome_fx_blue" not in payload

    def test_includes_color_fields_for_colour_simulation(self) -> None:
        recipe = _recipe(film_simulation="Provia", color_chrome_effect="Strong", color_chrome_fx_blue="Weak")
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert "color_chrome_effect" in payload
        assert "color_chrome_fx_blue" in payload

    def test_omits_monochrome_only_fields_for_colour_simulation(self) -> None:
        recipe = _recipe(film_simulation="Provia", monochromatic_color_warm_cool=None, monochromatic_color_magenta_green=None)
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert "monochromatic_color_warm_cool" not in payload
        assert "monochromatic_color_magenta_green" not in payload

    def test_includes_monochrome_only_fields_for_monochromatic_simulation(self) -> None:
        from decimal import Decimal
        recipe = _recipe(
            film_simulation="Acros STD",
            monochromatic_color_warm_cool=Decimal("0"),
            monochromatic_color_magenta_green=Decimal("2"),
        )
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert "monochromatic_color_warm_cool" in payload
        assert "monochromatic_color_magenta_green" in payload

    def test_includes_zero_decimal_values(self) -> None:
        from decimal import Decimal
        recipe = _recipe(highlight=Decimal("0"), shadow=Decimal("0"))
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert "highlight" in payload
        assert payload["highlight"] == 0

    def test_omits_none_values_for_applicable_fields(self) -> None:
        recipe = _recipe(highlight=None, shadow=None)
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert "highlight" not in payload
        assert "shadow" not in payload

    def test_omits_grain_size_when_grain_roughness_is_off(self) -> None:
        recipe = _recipe(grain_roughness="Off", grain_size="Small")
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert "grain_size" not in payload

    def test_includes_grain_size_when_grain_roughness_is_not_off(self) -> None:
        recipe = _recipe(grain_roughness="Weak", grain_size="Small")
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert "grain_size" in payload

    def test_includes_name_when_recipe_has_a_name(self) -> None:
        recipe = _recipe(name="My Summer Recipe")
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert payload["name"] == "My Summer Recipe"

    def test_omits_name_when_recipe_is_unnamed(self) -> None:
        recipe = _recipe()  # default model name is ""
        payload = json.loads(queries.get_recipe_as_json(recipe=recipe))
        assert "name" not in payload
