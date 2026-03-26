import pytest
from bs4 import BeautifulSoup

from tests.factories import ImageFactory


@pytest.mark.django_db
class TestFavoriteButtonInDetailView:
    def test_favorite_button_is_in_detail_header(self, client):
        image = ImageFactory()

        response = client.get(f"/images/{image.id}/")

        soup = BeautifulSoup(response.content, "html.parser")
        header = soup.find(class_="detail-header")
        assert header is not None
        assert header.find(class_="detail-favorite") is not None

    def test_non_favorite_image_shows_empty_star(self, client):
        image = ImageFactory(is_favorite=False)

        response = client.get(f"/images/{image.id}/")

        soup = BeautifulSoup(response.content, "html.parser")
        btn = soup.find(class_="detail-favorite")
        assert "detail-favorite--active" not in btn.get("class", [])
        assert "\u2606" in btn.get_text()  # ☆ empty star

    def test_favorite_image_shows_filled_star(self, client):
        image = ImageFactory(is_favorite=True)

        response = client.get(f"/images/{image.id}/")

        soup = BeautifulSoup(response.content, "html.parser")
        btn = soup.find(class_="detail-favorite")
        assert "detail-favorite--active" in btn.get("class", [])
        assert "\u2605" in btn.get_text()  # ★ filled star

    def test_clicking_favorite_button_then_page_shows_filled_star(self, client):
        image = ImageFactory(is_favorite=False)

        client.post(f"/images/{image.id}/toggle-favorite/")

        response = client.get(f"/images/{image.id}/")
        soup = BeautifulSoup(response.content, "html.parser")
        btn = soup.find(class_="detail-favorite")
        assert "detail-favorite--active" in btn.get("class", [])
        assert "\u2605" in btn.get_text()  # ★ filled star

    def test_clicking_favorite_button_twice_then_page_shows_empty_star(self, client):
        image = ImageFactory(is_favorite=False)

        client.post(f"/images/{image.id}/toggle-favorite/")
        client.post(f"/images/{image.id}/toggle-favorite/")

        response = client.get(f"/images/{image.id}/")
        soup = BeautifulSoup(response.content, "html.parser")
        btn = soup.find(class_="detail-favorite")
        assert "detail-favorite--active" not in btn.get("class", [])
        assert "\u2606" in btn.get_text()  # ☆ empty star

    def test_toggle_endpoint_returns_404_for_missing_image(self, client):
        response = client.post("/images/99999/toggle-favorite/")
        assert response.status_code == 404

    def test_toggle_endpoint_rejects_get_request(self, client):
        image = ImageFactory()
        response = client.get(f"/images/{image.id}/toggle-favorite/")
        assert response.status_code == 405
