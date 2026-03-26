"""
Domain-layer write helpers for Fujifilm PTP/USB camera communication.

Timing requirements (must be respected to avoid camera errors):
  - 50 ms BEFORE each property write
  - 200 ms AFTER each property write
  - A liveness ping AFTER each property write

These helpers are consumed by the application-layer use case
push_recipe_to_camera.
"""

from __future__ import annotations

import logging
import time

from src.domain.camera import events
from src.domain.camera.ptp_device import CameraConnectionError, PTPDevice

logger = logging.getLogger(__name__)

PRE_WRITE_DELAY_S = 0.050    # 50 ms before each write
POST_WRITE_DELAY_S = 0.200   # 200 ms after each write

_WRITE_MAX_RETRIES = 3        # attempts per property before giving up
_WRITE_RETRY_BACKOFF_S = 0.3  # base back-off; doubles each attempt (0.3 s, 0.6 s, 1.2 s)


def set_prop_with_retry(device: PTPDevice, code: int, value: int) -> int:
    """
    Write a single property, retrying on transport failures with exponential back-off.

    Publishes camera.ptp_write.failed for every failed attempt and
    camera.ptp_write.succeeded when the write completes successfully.

    Camera rejections (non-zero return code) are published as a single
    camera.ptp_write.failed event and returned immediately without retry,
    because the camera has actively declined the write.

    Returns:
        0 on success, non-zero on failure (transport exhausted or camera rejected).
    """
    last_error: CameraConnectionError | None = None
    prop_hex = f"0x{code:04X}"

    for attempt in range(1, _WRITE_MAX_RETRIES + 1):
        if attempt > 1:
            time.sleep(_WRITE_RETRY_BACKOFF_S * (2 ** (attempt - 2)))

        try:
            rc = device.set_property_int(code, value)
        except CameraConnectionError as exc:
            last_error = exc
            events.publish_event(
                event_type=events.PTP_WRITE_FAILED,
                params={
                    "description": (
                        f"{prop_hex} = {value}: {exc} "
                        f"(attempt {attempt}/{_WRITE_MAX_RETRIES})"
                    )
                },
            )
            continue

        if rc != 0:
            events.publish_event(
                event_type=events.PTP_WRITE_FAILED,
                params={
                    "description": (
                        f"{prop_hex} = {value}: camera rejected write (rc={rc:#x})"
                    )
                },
            )
            return rc

        events.publish_event(
            event_type=events.PTP_WRITE_SUCCEEDED,
            params={"description": f"{prop_hex} = {value}"},
        )
        return 0

    # All retries exhausted due to transport failure; already published per-attempt events.
    assert last_error is not None
    return -1


def verify_written_properties(
    device: PTPDevice,
    written: list[tuple[int, int]],
) -> list[int]:
    """Read back each successfully written property and check its value.

    Returns a list of PTP codes where the read-back value did not match.
    """
    mismatched: list[int] = []
    for code, expected in written:
        try:
            actual = device.get_property_int(code)
            # Compare lower 32 bits — handles signed/unsigned differences.
            if (actual & 0xFFFFFFFF) != (expected & 0xFFFFFFFF):
                logger.warning(
                    "Verification failed for 0x%04X: wrote %d, read back %d",
                    code,
                    expected,
                    actual,
                )
                mismatched.append(code)
        except CameraConnectionError:
            logger.warning(
                "Verification read failed for 0x%04X (camera error)", code
            )
            mismatched.append(code)
    return mismatched
