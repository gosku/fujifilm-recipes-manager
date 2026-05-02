from decimal import Decimal

import pytest

_URL = "/recipes/create/"


def _valid_data(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "name": "My Recipe",
        "film_simulation": "Provia",
        "dynamic_range": "DR100",
        "d_range_priority": "Off",
        "grain_roughness": "Off",
        "grain_size": "Off",
        "color_chrome_effect": "Off",
        "color_chrome_fx_blue": "Off",
        "white_balance": "Auto",
        "white_balance_red": "0",
        "white_balance_blue": "0",
        "highlight": "0",
        "shadow": "0",
        "color": "0",
        "sharpness": "0",
        "high_iso_nr": "0",
        "clarity": "0",
    }
    base.update(overrides)
    return base


@pytest.mark.django_db
class TestCreateRecipeView:
    def test_get_renders_the_form(self, client) -> None:
        response = client.get(_URL)
        assert response.status_code == 200

    def test_post_with_valid_data_returns_no_errors(self, client) -> None:
        response = client.post(_URL, _valid_data())
        assert response.status_code == 200
        assert not response.context["form"].errors

    def test_post_without_name_shows_error(self, client) -> None:
        data = _valid_data()
        del data["name"]
        form = client.post(_URL, data).context["form"]
        assert "name" in form.errors

    def test_post_with_name_exceeding_max_length_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(name="a" * 26)).context["form"]
        assert "name" in form.errors

    # ── Field range validation ────────────────────────────────────

    def test_post_with_color_above_max_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(color="5")).context["form"]
        assert "color" in form.errors

    def test_post_with_color_below_min_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(color="-5")).context["form"]
        assert "color" in form.errors

    def test_post_with_highlight_above_max_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(highlight="5")).context["form"]
        assert "highlight" in form.errors

    def test_post_with_highlight_below_min_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(highlight="-3")).context["form"]
        assert "highlight" in form.errors

    def test_post_with_highlight_on_invalid_step_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(highlight="1.3")).context["form"]
        assert "highlight" in form.errors

    def test_post_with_highlight_on_valid_half_step_returns_no_error(self, client) -> None:
        form = client.post(_URL, _valid_data(highlight="1.5")).context["form"]
        assert "highlight" not in form.errors

    def test_post_with_sharpness_above_max_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(sharpness="5")).context["form"]
        assert "sharpness" in form.errors

    def test_post_with_clarity_above_max_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(clarity="6")).context["form"]
        assert "clarity" in form.errors

    def test_post_with_white_balance_red_above_max_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(white_balance_red="10")).context["form"]
        assert "white_balance_red" in form.errors

    def test_post_with_white_balance_blue_below_min_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(white_balance_blue="-10")).context["form"]
        assert "white_balance_blue" in form.errors

    # ── Kelvin white balance ──────────────────────────────────────

    def test_post_with_kelvin_wb_without_temperature_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(white_balance="Kelvin")).context["form"]
        assert "kelvin_temperature" in form.errors

    def test_post_with_kelvin_wb_and_valid_temperature_returns_no_errors(self, client) -> None:
        form = client.post(_URL, _valid_data(white_balance="Kelvin", kelvin_temperature="6500")).context["form"]
        assert not form.errors

    def test_post_with_kelvin_temperature_out_of_range_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(white_balance="Kelvin", kelvin_temperature="100")).context["form"]
        assert "kelvin_temperature" in form.errors

    def test_post_with_non_kelvin_wb_cleans_temperature_to_none(self, client) -> None:
        form = client.post(_URL, _valid_data(white_balance="Auto", kelvin_temperature="6500")).context["form"]
        assert form.cleaned_data["kelvin_temperature"] is None

    # ── Monochromatic cross-field cleaning ────────────────────────

    def test_post_with_mono_film_sim_preserves_mono_fields(self, client) -> None:
        form = client.post(_URL, _valid_data(
            film_simulation="Acros STD",
            monochromatic_color_warm_cool="3",
            monochromatic_color_magenta_green="-2",
        )).context["form"]
        assert form.cleaned_data["monochromatic_color_warm_cool"] == Decimal("3")
        assert form.cleaned_data["monochromatic_color_magenta_green"] == Decimal("-2")

    def test_post_with_non_mono_film_sim_cleans_mono_fields_to_none(self, client) -> None:
        form = client.post(_URL, _valid_data(
            film_simulation="Provia",
            monochromatic_color_warm_cool="3",
            monochromatic_color_magenta_green="-2",
        )).context["form"]
        assert form.cleaned_data["monochromatic_color_warm_cool"] is None
        assert form.cleaned_data["monochromatic_color_magenta_green"] is None

    def test_post_with_mono_field_out_of_range_shows_error(self, client) -> None:
        form = client.post(_URL, _valid_data(
            film_simulation="Acros STD",
            monochromatic_color_warm_cool="10",
        )).context["form"]
        assert "monochromatic_color_warm_cool" in form.errors

    # ── Grain cross-field cleaning ────────────────────────────────

    def test_post_with_grain_roughness_off_cleans_grain_size_to_none(self, client) -> None:
        form = client.post(_URL, _valid_data(grain_roughness="Off", grain_size="Large")).context["form"]
        assert form.cleaned_data["grain_size"] is None

    def test_post_with_grain_roughness_set_preserves_grain_size(self, client) -> None:
        form = client.post(_URL, _valid_data(grain_roughness="Weak", grain_size="Large")).context["form"]
        assert form.cleaned_data["grain_size"] == "Large"

    # ── D-Range Priority cross-field cleaning ─────────────────────

    def test_post_with_active_d_range_priority_cleans_dynamic_range_to_none(self, client) -> None:
        form = client.post(_URL, _valid_data(d_range_priority="Weak", dynamic_range="DR200")).context["form"]
        assert form.cleaned_data["dynamic_range"] is None

    def test_post_with_active_d_range_priority_without_dynamic_range_returns_no_error(self, client) -> None:
        # Browser does not submit disabled selects; dynamic_range must not be required
        # when D-Range Priority is active.
        data = _valid_data(d_range_priority="Weak")
        del data["dynamic_range"]
        form = client.post(_URL, data).context["form"]
        assert "dynamic_range" not in form.errors

    def test_post_with_d_range_priority_off_preserves_dynamic_range(self, client) -> None:
        form = client.post(_URL, _valid_data(d_range_priority="Off", dynamic_range="DR400")).context["form"]
        assert form.cleaned_data["dynamic_range"] == "DR400"

    def test_post_with_d_range_priority_off_and_no_dynamic_range_shows_error(self, client) -> None:
        data = _valid_data(d_range_priority="Off")
        del data["dynamic_range"]
        form = client.post(_URL, data).context["form"]
        assert "dynamic_range" in form.errors
