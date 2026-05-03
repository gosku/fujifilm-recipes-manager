import pytest

from src.data import models
from src.domain.images import dataclasses as image_dataclasses
from src.domain.images import events
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
    def test_creates_recipe_and_returns_created_true(self) -> None:
        recipe, created = get_or_create_recipe_from_data(data=_make_data(name="First"))

        assert recipe.pk is not None
        assert created is True

    def test_returns_existing_recipe_and_created_false_on_second_call(self) -> None:
        first, _ = get_or_create_recipe_from_data(data=_make_data(name="First"))
        second, created = get_or_create_recipe_from_data(data=_make_data(name="First"))

        assert second.pk == first.pk
        assert created is False
        assert models.FujifilmRecipe.objects.count() == 1

    def test_publishes_created_event_on_first_call(self, captured_logs) -> None:
        recipe, _ = get_or_create_recipe_from_data(data=_make_data())

        created_events = [e for e in captured_logs if e.get("event_type") == events.RECIPE_CREATED]
        assert len(created_events) == 1
        assert created_events[0]["recipe_id"] == recipe.pk

    def test_publishes_deduplicated_event_on_subsequent_call(self, captured_logs) -> None:
        recipe, _ = get_or_create_recipe_from_data(data=_make_data())
        captured_logs.clear()
        get_or_create_recipe_from_data(data=_make_data())

        assert not [e for e in captured_logs if e.get("event_type") == events.RECIPE_CREATED]
        dedup_events = [e for e in captured_logs if e.get("event_type") == events.RECIPE_DEDUPLICATED]
        assert len(dedup_events) == 1
        assert dedup_events[0]["recipe_id"] == recipe.pk

    # ── Name is settings-lookup-only, never written back on get path ────────

    def test_same_settings_different_name_deduplicates_to_same_recipe(self) -> None:
        first, _ = get_or_create_recipe_from_data(data=_make_data(name="Alpha"))

        second, created = get_or_create_recipe_from_data(data=_make_data(name="Beta"))

        assert second.pk == first.pk
        assert created is False

    def test_name_from_first_create_is_preserved_on_get(self) -> None:
        get_or_create_recipe_from_data(data=_make_data(name="Original"))

        recipe, _ = get_or_create_recipe_from_data(data=_make_data(name="Ignored"))

        recipe.refresh_from_db()
        assert recipe.name == "Original"

    def test_different_settings_produce_separate_recipes(self) -> None:
        _, created_a = get_or_create_recipe_from_data(data=_make_data(white_balance_red=1))
        _, created_b = get_or_create_recipe_from_data(data=_make_data(white_balance_red=2))

        assert created_a is True
        assert created_b is True
        assert models.FujifilmRecipe.objects.count() == 2

    def test_raises_invalid_recipe_data_before_touching_db(self) -> None:
        # DRP active but dynamic_range is provided — structurally inconsistent.
        invalid_data = _make_data(d_range_priority="Auto", dynamic_range="DR100", highlight=None, shadow=None)
        with pytest.raises(InvalidFujifilmRecipeData) as exc_info:
            get_or_create_recipe_from_data(data=invalid_data)
        assert exc_info.value.field == "dynamic_range"
        assert models.FujifilmRecipe.objects.count() == 0
