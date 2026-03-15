import pytest
from bs4 import BeautifulSoup
from django.test import override_settings

from src.data.models import FujifilmRecipe, Image

_RECIPE_DEFAULTS = dict(
    film_simulation="Classic Chrome",
    dynamic_range="DR Auto",
    d_range_priority="Off",
    grain_roughness="Off",
    grain_size="Off",
    color_chrome_effect="Off",
    color_chrome_fx_blue="Off",
    white_balance="Auto",
    white_balance_red=0,
    white_balance_blue=0,
)


@pytest.mark.django_db
class TestGalleryResultsView:
    def test_filters_images_by_recipe_name(self, client):
        # Arrange: 2 recipes, 3 images (2 for recipe_a, 1 for recipe_b)
        recipe_a = FujifilmRecipe.objects.create(
            name="Classic Chrome Recipe", **_RECIPE_DEFAULTS
        )
        recipe_b = FujifilmRecipe.objects.create(
            name="Velvia Recipe",
            **{**_RECIPE_DEFAULTS, "film_simulation": "Velvia"},
        )
        Image.objects.create(
            filename="fav.jpg",
            filepath="/shots/fav.jpg",
            fujifilm_recipe=recipe_a,
            is_favorite=True,
        )
        Image.objects.create(
            filename="normal.jpg",
            filepath="/shots/normal.jpg",
            fujifilm_recipe=recipe_a,
            is_favorite=False,
        )
        Image.objects.create(
            filename="other.jpg",
            filepath="/shots/other.jpg",
            fujifilm_recipe=recipe_b,
        )

        # Act: filter by recipe_a name
        response = client.get("/images/results/", {"name": recipe_a.name})

        assert response.status_code == 200

        soup = BeautifulSoup(response.content, "html.parser")
        cards = soup.find_all(class_="image-card")

        # Only the 2 images belonging to recipe_a are shown
        assert len(cards) == 2

        # Favorite image appears first, then non-favorite
        filenames = [card.find(class_="image-filename").text.strip() for card in cards]
        assert filenames == ["fav.jpg", "normal.jpg"]

        # Favorite card carries the favourite marker; non-favourite does not
        assert cards[0].find(class_="image-favorite") is not None
        assert cards[1].find(class_="image-favorite") is None

        # Both cards expose the filepath
        assert cards[0].find(class_="image-filepath") is not None
        assert cards[1].find(class_="image-filepath") is not None


@pytest.mark.django_db
class TestGalleryPagination:
    @override_settings(GALLERY_PAGE_SIZE=2)
    def test_first_page_contains_page_size_images(self, client):
        recipe = FujifilmRecipe.objects.create(name="Test Recipe", **_RECIPE_DEFAULTS)
        for i in range(3):
            Image.objects.create(
                filename=f"img{i}.jpg",
                filepath=f"/shots/img{i}.jpg",
                fujifilm_recipe=recipe,
            )

        response = client.get("/images/results/", {"page": "1"})

        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        assert len(soup.find_all(class_="image-card")) == 2

    @override_settings(GALLERY_PAGE_SIZE=2)
    def test_second_page_contains_remaining_images(self, client):
        recipe = FujifilmRecipe.objects.create(name="Test Recipe", **_RECIPE_DEFAULTS)
        for i in range(3):
            Image.objects.create(
                filename=f"img{i}.jpg",
                filepath=f"/shots/img{i}.jpg",
                fujifilm_recipe=recipe,
            )

        response = client.get("/images/results/", {"page": "2"})

        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        assert len(soup.find_all(class_="image-card")) == 1

    @override_settings(GALLERY_PAGE_SIZE=2)
    def test_pagination_controls_shown_when_multiple_pages(self, client):
        recipe = FujifilmRecipe.objects.create(name="Test Recipe", **_RECIPE_DEFAULTS)
        for i in range(3):
            Image.objects.create(
                filename=f"img{i}.jpg",
                filepath=f"/shots/img{i}.jpg",
                fujifilm_recipe=recipe,
            )

        response = client.get("/images/results/")

        soup = BeautifulSoup(response.content, "html.parser")
        assert soup.find(class_="pagination") is not None
        assert soup.find(class_="pagination-next") is not None
        assert soup.find(class_="pagination-prev") is None  # no prev on first page

    @override_settings(GALLERY_PAGE_SIZE=2)
    def test_pagination_controls_hidden_when_single_page(self, client):
        recipe = FujifilmRecipe.objects.create(name="Test Recipe", **_RECIPE_DEFAULTS)
        Image.objects.create(
            filename="only.jpg",
            filepath="/shots/only.jpg",
            fujifilm_recipe=recipe,
        )

        response = client.get("/images/results/")

        soup = BeautifulSoup(response.content, "html.parser")
        assert soup.find(class_="pagination") is None

    @override_settings(GALLERY_PAGE_SIZE=2)
    def test_out_of_range_page_returns_last_page(self, client):
        recipe = FujifilmRecipe.objects.create(name="Test Recipe", **_RECIPE_DEFAULTS)
        for i in range(3):
            Image.objects.create(
                filename=f"img{i}.jpg",
                filepath=f"/shots/img{i}.jpg",
                fujifilm_recipe=recipe,
            )

        response = client.get("/images/results/", {"page": "999"})

        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        # Last page has 1 image; django's get_page() clamps to last page
        assert len(soup.find_all(class_="image-card")) == 1
