import pytest
from bs4 import BeautifulSoup

from tests.factories import FujifilmRecipeFactory, ImageFactory


@pytest.mark.django_db
class TestRecipeFaceting:
    """Recipe filter participates in bidirectional faceted search."""

    def test_field_filter_hides_non_matching_recipes(self, client):
        """Selecting film_simulation=Provia should hide Velvia-only recipes from the dropdown."""
        recipe_provia = FujifilmRecipeFactory(name="Provia Recipe", film_simulation="Provia")
        recipe_velvia = FujifilmRecipeFactory(name="Velvia Recipe", film_simulation="Velvia")
        ImageFactory.create_batch(51, fujifilm_recipe=recipe_provia)
        ImageFactory.create_batch(51, fujifilm_recipe=recipe_velvia)

        response = client.get("/images/", {"film_simulation": "Provia"})

        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        provia_option = soup.find("option", {"value": str(recipe_provia.id)})
        velvia_option = soup.find("option", {"value": str(recipe_velvia.id)})
        assert provia_option is not None
        assert velvia_option is None

    def test_recipe_selection_narrows_field_options(self, client):
        """Selecting a recipe should restrict field filter options to that recipe's images."""
        recipe_provia = FujifilmRecipeFactory(name="Provia Recipe", film_simulation="Provia", grain_size="Off")
        recipe_velvia = FujifilmRecipeFactory(name="Velvia Recipe", film_simulation="Velvia", grain_size="Strong")
        ImageFactory(fujifilm_recipe=recipe_provia)
        ImageFactory(fujifilm_recipe=recipe_velvia)

        response = client.get("/images/", {"recipe_id": str(recipe_provia.id)}, HTTP_HX_REQUEST="true")

        soup = BeautifulSoup(response.content, "html.parser")
        grain_checkboxes = {cb["value"] for cb in soup.find_all("input", {"name": "grain_size"})}
        assert "Off" in grain_checkboxes
        assert "Strong" not in grain_checkboxes

    def test_htmx_response_includes_recipe_filter_oob(self, client):
        recipe = FujifilmRecipeFactory(name="My Recipe")
        ImageFactory(fujifilm_recipe=recipe)

        response = client.get("/images/", {"film_simulation": "Provia"}, HTTP_HX_REQUEST="true")

        soup = BeautifulSoup(response.content, "html.parser")
        recipe_div = soup.find(id="recipe-filter")
        assert recipe_div is not None
        assert recipe_div.get("hx-swap-oob") == "true"

    def test_recipe_filter_count_reflects_active_field_filters(self, client):
        """The count shown for each recipe should be the filtered image count, not total."""
        recipe = FujifilmRecipeFactory(name="My Recipe", film_simulation="Provia")
        ImageFactory.create_batch(3, fujifilm_recipe=recipe)
        # Extra images with a different film sim — won't be counted when filtering by Provia
        other = FujifilmRecipeFactory(film_simulation="Velvia")
        ImageFactory.create_batch(51, fujifilm_recipe=other)

        response = client.get("/images/", {"film_simulation": "Provia"})

        soup = BeautifulSoup(response.content, "html.parser")
        recipe_option = soup.find("option", {"value": str(recipe.id)})
        assert recipe_option is not None
        assert "(3)" in recipe_option.text

    def test_selected_recipe_still_shown_when_images_unavailable(self, client):
        """A selected recipe with no matching field-filter images is still shown so it can be deselected."""
        recipe_provia = FujifilmRecipeFactory(name="Provia Recipe", film_simulation="Provia")
        recipe_velvia = FujifilmRecipeFactory(name="Velvia Recipe", film_simulation="Velvia")
        ImageFactory.create_batch(51, fujifilm_recipe=recipe_provia)
        ImageFactory.create_batch(51, fujifilm_recipe=recipe_velvia)

        # Select Velvia recipe but filter by Provia film sim → Velvia recipe has no matching images
        response = client.get(
            f"/images/?recipe_id={recipe_velvia.id}&film_simulation=Provia"
        )

        soup = BeautifulSoup(response.content, "html.parser")
        velvia_option = soup.find("option", {"value": str(recipe_velvia.id)})
        assert velvia_option is not None
        assert velvia_option.has_attr("selected")


@pytest.mark.django_db
class TestMultiValueFiltering:
    """gallery-results endpoint with multiple values for the same field."""

    def test_single_value_filter_returns_matching_images(self, client):
        recipe_a = FujifilmRecipeFactory(film_simulation="Provia")
        recipe_b = FujifilmRecipeFactory(film_simulation="Velvia")
        ImageFactory(filename="provia.jpg", fujifilm_recipe=recipe_a)
        ImageFactory(filename="velvia.jpg", fujifilm_recipe=recipe_b)

        response = client.get("/images/results/", {"film_simulation": "Provia"})

        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        filenames = {c.find(class_="image-filename").text.strip() for c in soup.find_all(class_="image-card")}
        assert filenames == {"provia.jpg"}

    def test_two_values_same_field_are_or_combined(self, client):
        recipe_a = FujifilmRecipeFactory(film_simulation="Provia")
        recipe_b = FujifilmRecipeFactory(film_simulation="Velvia")
        recipe_c = FujifilmRecipeFactory(film_simulation="Astia")
        ImageFactory(filename="provia.jpg", fujifilm_recipe=recipe_a)
        ImageFactory(filename="velvia.jpg", fujifilm_recipe=recipe_b)
        ImageFactory(filename="astia.jpg", fujifilm_recipe=recipe_c)

        response = client.get("/images/results/?film_simulation=Provia&film_simulation=Velvia")

        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        filenames = {c.find(class_="image-filename").text.strip() for c in soup.find_all(class_="image-card")}
        assert filenames == {"provia.jpg", "velvia.jpg"}
        assert "astia.jpg" not in filenames

    def test_filters_across_fields_are_and_combined(self, client):
        # Provia+Off: should match; Provia+Weak: should not (wrong grain); Velvia+Off: should not (wrong sim)
        recipe_match = FujifilmRecipeFactory(film_simulation="Provia", grain_size="Off")
        recipe_wrong_grain = FujifilmRecipeFactory(film_simulation="Provia", grain_size="Weak")
        recipe_wrong_sim = FujifilmRecipeFactory(film_simulation="Velvia", grain_size="Off")
        ImageFactory(filename="match.jpg", fujifilm_recipe=recipe_match)
        ImageFactory(filename="wrong_grain.jpg", fujifilm_recipe=recipe_wrong_grain)
        ImageFactory(filename="wrong_sim.jpg", fujifilm_recipe=recipe_wrong_sim)

        response = client.get("/images/results/", {"film_simulation": "Provia", "grain_size": "Off"})

        soup = BeautifulSoup(response.content, "html.parser")
        filenames = {c.find(class_="image-filename").text.strip() for c in soup.find_all(class_="image-card")}
        assert filenames == {"match.jpg"}

    def test_multi_value_field_combined_with_another_field_filter(self, client):
        recipe_a = FujifilmRecipeFactory(film_simulation="Provia", grain_size="Off")
        recipe_b = FujifilmRecipeFactory(film_simulation="Velvia", grain_size="Off")
        recipe_c = FujifilmRecipeFactory(film_simulation="Astia", grain_size="Off")
        recipe_d = FujifilmRecipeFactory(film_simulation="Provia", grain_size="Weak")
        ImageFactory(filename="provia_off.jpg", fujifilm_recipe=recipe_a)
        ImageFactory(filename="velvia_off.jpg", fujifilm_recipe=recipe_b)
        ImageFactory(filename="astia_off.jpg", fujifilm_recipe=recipe_c)
        ImageFactory(filename="provia_weak.jpg", fujifilm_recipe=recipe_d)

        response = client.get(
            "/images/results/?film_simulation=Provia&film_simulation=Velvia&grain_size=Off"
        )

        soup = BeautifulSoup(response.content, "html.parser")
        filenames = {c.find(class_="image-filename").text.strip() for c in soup.find_all(class_="image-card")}
        assert filenames == {"provia_off.jpg", "velvia_off.jpg"}

    def test_no_results_when_no_images_match(self, client):
        recipe = FujifilmRecipeFactory(film_simulation="Provia")
        ImageFactory(fujifilm_recipe=recipe)

        response = client.get("/images/results/", {"film_simulation": "Velvia"})

        soup = BeautifulSoup(response.content, "html.parser")
        assert soup.find_all(class_="image-card") == []


@pytest.mark.django_db
class TestHtmxSidebarOobUpdate:
    """HTMX filter requests must return sidebar options as an OOB swap."""

    def test_htmx_response_includes_sidebar_oob_element(self, client):
        recipe = FujifilmRecipeFactory(film_simulation="Provia")
        ImageFactory(fujifilm_recipe=recipe)

        response = client.get("/images/", {"film_simulation": "Provia"}, HTTP_HX_REQUEST="true")

        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        sidebar = soup.find(id="sidebar-filters")
        assert sidebar is not None
        assert sidebar.get("hx-swap-oob") == "true"

    def test_htmx_sidebar_marks_selected_value_as_checked(self, client):
        recipe = FujifilmRecipeFactory(film_simulation="Provia")
        ImageFactory(fujifilm_recipe=recipe)

        response = client.get("/images/", {"film_simulation": "Provia"}, HTTP_HX_REQUEST="true")

        soup = BeautifulSoup(response.content, "html.parser")
        checkbox = soup.find("input", {"name": "film_simulation", "value": "Provia"})
        assert checkbox is not None
        assert checkbox.has_attr("checked")

    def test_htmx_sidebar_marks_unavailable_selected_value_with_css_class(self, client):
        recipe = FujifilmRecipeFactory(film_simulation="Provia", grain_size="Off")
        ImageFactory(fujifilm_recipe=recipe)

        # Weak grain doesn't exist for Provia images — should be greyed out
        response = client.get(
            "/images/?film_simulation=Provia&grain_size=Weak",
            HTTP_HX_REQUEST="true",
        )

        soup = BeautifulSoup(response.content, "html.parser")
        grain_weak = soup.find("input", {"name": "grain_size", "value": "Weak"})
        assert grain_weak is not None
        assert grain_weak.has_attr("checked")
        label = grain_weak.find_parent("label")
        assert "filter-option--unavailable" in label.get("class", [])

    def test_htmx_sidebar_available_options_exclude_unmatched_values(self, client):
        recipe_a = FujifilmRecipeFactory(film_simulation="Provia", grain_size="Off")
        recipe_b = FujifilmRecipeFactory(film_simulation="Velvia", grain_size="Weak")
        ImageFactory(fujifilm_recipe=recipe_a)
        ImageFactory(fujifilm_recipe=recipe_b)

        # Filter by Provia: only Off grain should be available, Weak should not appear
        response = client.get("/images/", {"film_simulation": "Provia"}, HTTP_HX_REQUEST="true")

        soup = BeautifulSoup(response.content, "html.parser")
        grain_weak = soup.find("input", {"name": "grain_size", "value": "Weak"})
        # Weak is not selected and not available: it should not appear at all
        assert grain_weak is None

    def test_full_page_load_does_not_include_oob_attribute(self, client):
        recipe = FujifilmRecipeFactory(film_simulation="Provia")
        ImageFactory(fujifilm_recipe=recipe)

        response = client.get("/images/", {"film_simulation": "Provia"})

        soup = BeautifulSoup(response.content, "html.parser")
        sidebar = soup.find(id="sidebar-filters")
        assert sidebar is not None
        assert not sidebar.has_attr("hx-swap-oob")
