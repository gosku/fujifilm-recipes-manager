import pytest

from src.data.camera import constants
from src.domain.camera.operations import push_recipe
from src.domain.camera.ptp_device import CameraConnectionError
from src.domain.images.dataclasses import FujifilmRecipeData
from tests.fakes import FakePTPDevice


def _make_recipe(**overrides: object) -> FujifilmRecipeData:
    defaults = dict(
        film_simulation="Provia",
        dynamic_range="DR100",
        d_range_priority="Off",
        grain_roughness="Off",
        grain_size="Off",
        color_chrome_effect="Off",
        color_chrome_fx_blue="Off",
        white_balance="Auto",
        white_balance_red=0,
        white_balance_blue=0,
        highlight="0",
        shadow="0",
        color="0",
        sharpness="0",
        high_iso_nr="0",
        clarity="0",
        monochromatic_color_warm_cool="N/A",
        monochromatic_color_magenta_green="N/A",
    )
    defaults.update(overrides)
    return FujifilmRecipeData(**defaults)


class TestPushRecipeVerification:
    def test_verification_passes_when_readback_matches(self):
        # Default FakePTPDevice: writes update the store, reads return the
        # same value → verification always passes.
        failed = push_recipe(FakePTPDevice(), _make_recipe(), slot_index=1)
        assert failed == []

    def test_verification_detects_mismatched_readback(self):
        # FilmSimulation (0xD192) is written as 1 (Provia) but the camera
        # reports 99 on read-back — simulates a normalisation mismatch.
        device = FakePTPDevice(int_read_overrides={0xD192: 99})
        failed = push_recipe(device, _make_recipe(film_simulation="Provia"), slot_index=1)
        assert 0xD192 in failed

    def test_verification_detects_name_mismatch(self, caplog):
        # The camera rejects the slot-name write (set_rejection_codes), so
        # the store keeps the original "Wrong Name".  Verification reads it
        # back and logs a warning.
        device = FakePTPDevice(
            string_values={constants.PROP_SLOT_NAME: "Wrong Name"},
            set_rejection_codes={constants.PROP_SLOT_NAME: 0x2005},
        )
        push_recipe(device, _make_recipe(), slot_index=1, slot_name="My Recipe")
        assert any("Slot name verification failed" in rec.message for rec in caplog.records)

    def test_verification_handles_read_error_gracefully(self):
        # All get_property_int calls raise — simulates the camera going away
        # during the verification phase.  push_recipe should report all
        # written codes as failed rather than propagating the exception.
        device = FakePTPDevice(
            default_get_error=CameraConnectionError("USB read failed"),
        )
        failed = push_recipe(device, _make_recipe(), slot_index=1)
        assert len(failed) > 0
