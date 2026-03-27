import pytest
from bs4 import BeautifulSoup

from src.data.camera import constants
from src.domain.camera.ptp_device import CameraConnectionError, CameraWriteError
from tests.factories import FujifilmRecipeFactory
from tests.fakes import FakePTPDevice


def _recipe(**kwargs):
    return FujifilmRecipeFactory(sharpness=0, high_iso_nr=0, clarity=0, **kwargs)


@pytest.mark.django_db
class TestSelectSlotView:
    @pytest.fixture(autouse=True)
    def _no_sleep(self, monkeypatch):
        monkeypatch.setattr("time.sleep", lambda _: None)

    def test_success_renders_recipe_name_and_slots(self, client):
        recipe = _recipe(name="Kodak Portra")
        # autouse fixture → FakePTPDevice(camera_name="X-S10") → 4 slots

        response = client.get(f"/recipes/{recipe.id}/push/")

        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "html.parser")
        assert soup.find(string="Kodak Portra") is not None
        slot_labels = [el.get_text(strip=True) for el in soup.select(".slot-label")]
        assert slot_labels == ["C1", "C2", "C3", "C4"]

    def test_each_slot_form_posts_to_push_view(self, client):
        recipe = _recipe(name="My Recipe")

        response = client.get(f"/recipes/{recipe.id}/push/")

        soup = BeautifulSoup(response.content, "html.parser")
        forms = soup.select(".slot-form")
        assert len(forms) == 4
        for form, slot in zip(forms, ["C1", "C2", "C3", "C4"]):
            assert form["action"] == f"/recipes/{recipe.id}/push/{slot}/"
            assert form["method"] == "post"

    def test_recipe_not_found_returns_404(self, client):
        response = client.get("/recipes/99999/push/")

        assert response.status_code == 404

    def test_recipe_without_name_returns_404(self, client):
        recipe = _recipe(name="")

        response = client.get(f"/recipes/{recipe.id}/push/")

        assert response.status_code == 404

    def test_camera_connection_error_returns_503(self, client, settings):
        recipe = _recipe(name="My Recipe")
        settings.PTP_DEVICE = lambda: FakePTPDevice(
            set_errors={constants.PROP_SLOT_CURSOR: CameraConnectionError("USB timeout")}
        )

        response = client.get(f"/recipes/{recipe.id}/push/")

        assert response.status_code == 503
        assert "Camera connection error" in response.json()["error"]

    def test_camera_write_error_returns_500(self, client, settings):
        recipe = _recipe(name="My Recipe")
        settings.PTP_DEVICE = lambda: FakePTPDevice(
            set_rejection_codes={constants.PROP_SLOT_CURSOR: 0x2005}
        )

        response = client.get(f"/recipes/{recipe.id}/push/")

        assert response.status_code == 500
        assert "Camera write error" in response.json()["error"]

    def test_unexpected_error_returns_500_with_generic_message(self, client, settings):
        recipe = _recipe(name="My Recipe")

        def raise_runtime_error():
            raise RuntimeError("Unexpected boom")

        settings.PTP_DEVICE = raise_runtime_error

        response = client.get(f"/recipes/{recipe.id}/push/")

        assert response.status_code == 500
        assert response.json() == {"error": "Unexpected error happened"}
