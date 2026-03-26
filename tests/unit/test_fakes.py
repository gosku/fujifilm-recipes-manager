"""Tests for FakePTPDevice — verifies the fake models the real device contract."""

import pytest

from src.domain.camera.ptp_device import CameraConnectionError, PTPDevice
from tests.fakes import FakePTPDevice


class TestProtocolConformance:
    def test_satisfies_ptp_device_protocol(self):
        assert isinstance(FakePTPDevice(), PTPDevice)


class TestDefaults:
    def test_missing_int_property_returns_zero(self):
        assert FakePTPDevice().get_property_int(0xD192) == 0

    def test_missing_string_property_returns_empty_string(self):
        assert FakePTPDevice().get_property_string(0xD18D) == ""

    def test_camera_name_default(self):
        assert FakePTPDevice().camera_name == "X-S10"

    def test_ping_succeeds_by_default(self):
        assert FakePTPDevice().ping() == 0

    def test_connect_and_disconnect_are_no_ops(self):
        d = FakePTPDevice()
        d.connect()
        d.disconnect()


class TestInitialValues:
    def test_int_values_returned_on_get(self):
        d = FakePTPDevice(int_values={0xD192: 5, 0xD190: 65535})
        assert d.get_property_int(0xD192) == 5
        assert d.get_property_int(0xD190) == 65535

    def test_string_values_returned_on_get(self):
        d = FakePTPDevice(string_values={0xD18D: "Portrait"})
        assert d.get_property_string(0xD18D) == "Portrait"

    def test_custom_camera_name(self):
        assert FakePTPDevice(camera_name="X-T5").camera_name == "X-T5"


class TestWriteThenRead:
    def test_set_property_int_updates_store(self):
        d = FakePTPDevice()
        d.set_property_int(0xD192, 3)
        assert d.get_property_int(0xD192) == 3

    def test_set_property_uint16_masks_to_16_bits(self):
        d = FakePTPDevice()
        d.set_property_uint16(0xD190, 0x1_FFFF)  # only lower 16 bits stored
        assert d.get_property_int(0xD190) == 0xFFFF

    def test_set_property_string_updates_store(self):
        d = FakePTPDevice()
        d.set_property_string(0xD18D, "Landscape")
        assert d.get_property_string(0xD18D) == "Landscape"

    def test_set_overwrites_initial_value(self):
        d = FakePTPDevice(int_values={0xD192: 1})
        d.set_property_int(0xD192, 17)
        assert d.get_property_int(0xD192) == 17

    def test_successful_set_returns_zero(self):
        d = FakePTPDevice()
        assert d.set_property_int(0xD192, 1) == 0
        assert d.set_property_uint16(0xD18C, 1) == 0
        assert d.set_property_string(0xD18D, "x") == 0


class TestGetPropertyInt16:
    def test_positive_value_unchanged(self):
        d = FakePTPDevice(int_values={0xD001: 10})
        assert d.get_property_int16(0xD001) == 10

    def test_uint16_wraparound_decoded_as_negative(self):
        # −1 × 10 is stored as 65526 (0xFFF6) in the camera
        d = FakePTPDevice(int_values={0xD001: 65526})
        assert d.get_property_int16(0xD001) == -10

    def test_zero_is_zero(self):
        d = FakePTPDevice(int_values={0xD001: 0})
        assert d.get_property_int16(0xD001) == 0


class TestPingFailure:
    def test_ping_returns_minus_one_when_configured(self):
        assert FakePTPDevice(ping_fails=True).ping() == -1


class TestGetErrors:
    def test_get_int_raises_configured_exception(self):
        err = CameraConnectionError("USB timeout")
        d = FakePTPDevice(get_errors={0xD192: err})
        with pytest.raises(CameraConnectionError, match="USB timeout"):
            d.get_property_int(0xD192)

    def test_get_string_raises_configured_exception(self):
        err = CameraConnectionError("USB timeout")
        d = FakePTPDevice(get_errors={0xD18D: err})
        with pytest.raises(CameraConnectionError):
            d.get_property_string(0xD18D)

    def test_get_error_only_affects_configured_code(self):
        err = CameraConnectionError("timeout")
        d = FakePTPDevice(int_values={0xD190: 42}, get_errors={0xD192: err})
        assert d.get_property_int(0xD190) == 42  # unaffected

    def test_per_code_get_error_takes_priority_over_default(self):
        per_code = CameraConnectionError("per-code")
        default = CameraConnectionError("default")
        d = FakePTPDevice(get_errors={0xD192: per_code}, default_get_error=default)
        with pytest.raises(CameraConnectionError, match="per-code"):
            d.get_property_int(0xD192)


class TestDefaultGetError:
    def test_raises_for_any_int_read(self):
        err = CameraConnectionError("camera gone")
        d = FakePTPDevice(default_get_error=err)
        with pytest.raises(CameraConnectionError, match="camera gone"):
            d.get_property_int(0xD192)

    def test_raises_for_any_string_read(self):
        err = CameraConnectionError("camera gone")
        d = FakePTPDevice(default_get_error=err)
        with pytest.raises(CameraConnectionError):
            d.get_property_string(0xD18D)

    def test_does_not_affect_ping(self):
        err = CameraConnectionError("camera gone")
        d = FakePTPDevice(default_get_error=err)
        assert d.ping() == 0  # ping is independent of get_property_int


class TestIntReadOverrides:
    def test_returns_override_instead_of_store(self):
        d = FakePTPDevice(int_values={0xD192: 1}, int_read_overrides={0xD192: 99})
        assert d.get_property_int(0xD192) == 99

    def test_override_persists_after_write(self):
        d = FakePTPDevice(int_read_overrides={0xD192: 99})
        d.set_property_int(0xD192, 1)
        assert d.get_property_int(0xD192) == 99  # override wins

    def test_override_only_affects_configured_code(self):
        d = FakePTPDevice(int_values={0xD190: 42}, int_read_overrides={0xD192: 99})
        assert d.get_property_int(0xD190) == 42  # unaffected


class TestSetErrors:
    def test_set_int_raises_on_transport_failure(self):
        err = CameraConnectionError("cable pulled")
        d = FakePTPDevice(set_errors={0xD192: err})
        with pytest.raises(CameraConnectionError, match="cable pulled"):
            d.set_property_int(0xD192, 1)

    def test_set_uint16_raises_on_transport_failure(self):
        err = CameraConnectionError("cable pulled")
        d = FakePTPDevice(set_errors={0xD18C: err})
        with pytest.raises(CameraConnectionError):
            d.set_property_uint16(0xD18C, 1)

    def test_set_string_raises_on_transport_failure(self):
        err = CameraConnectionError("cable pulled")
        d = FakePTPDevice(set_errors={0xD18D: err})
        with pytest.raises(CameraConnectionError):
            d.set_property_string(0xD18D, "x")

    def test_store_not_updated_when_transport_fails(self):
        err = CameraConnectionError("timeout")
        d = FakePTPDevice(int_values={0xD192: 1}, set_errors={0xD192: err})
        with pytest.raises(CameraConnectionError):
            d.set_property_int(0xD192, 99)
        assert d.get_property_int(0xD192) == 1  # unchanged


class TestSetRejectionCodes:
    def test_set_returns_nonzero_on_camera_rejection(self):
        d = FakePTPDevice(set_rejection_codes={0xD192: 0x2005})
        rc = d.set_property_int(0xD192, 99)
        assert rc == 0x2005

    def test_store_not_updated_on_camera_rejection(self):
        d = FakePTPDevice(int_values={0xD192: 1}, set_rejection_codes={0xD192: 0x2005})
        d.set_property_int(0xD192, 99)
        assert d.get_property_int(0xD192) == 1  # unchanged

    def test_rejection_does_not_raise(self):
        d = FakePTPDevice(set_rejection_codes={0xD192: 0x2005})
        # Should return non-zero, not raise
        rc = d.set_property_int(0xD192, 1)
        assert rc != 0
