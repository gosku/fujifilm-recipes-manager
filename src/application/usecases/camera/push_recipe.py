"""
Application-layer use case for pushing a recipe to a Fujifilm camera.
"""
from __future__ import annotations

import logging
import time

from src.data.camera import constants
from src.domain.camera.operations import (
    POST_WRITE_DELAY_S,
    PRE_WRITE_DELAY_S,
    set_prop_with_retry,
    verify_written_properties,
)
from src.domain.camera.ptp_device import CameraConnectionError, PTPDevice
from src.domain.camera.queries import recipe_to_ptp_values
from src.domain.images.dataclasses import RECIPE_NAME_MAX_LEN, FujifilmRecipeData

logger = logging.getLogger(__name__)


def push_recipe_to_camera(
    device: PTPDevice,
    recipe: FujifilmRecipeData,
    *,
    slot_index: int,
    slot_name: str,
) -> list[int]:
    """
    Push a film simulation recipe to a custom C-slot on the connected camera.

    Args:
        device:      A connected PTPDevice instance.
        recipe:      The recipe to write.
        slot_index:  1-based custom slot number (e.g. 1 for C1).
        slot_name:   Display name for the slot.  Required; must be a non-blank
                     string of at most 25 ASCII characters.

    Returns:
        A list of PTP property codes for which the write failed.  An empty
        list means all writes succeeded.

    Raises:
        ValueError: If slot_name is blank, too long, or contains non-ASCII characters.
        RecipeValidationError: If any recipe field contains a camera-invalid value.
        CameraConnectionError: If the camera becomes unreachable during the
                               write sequence.
    """
    # --- Step 1: validate slot_name and set slot cursor ---
    if not slot_name or not slot_name.strip():
        raise ValueError("slot_name must be a non-blank string")
    if len(slot_name) > RECIPE_NAME_MAX_LEN:
        raise ValueError(
            f"slot_name must be ≤{RECIPE_NAME_MAX_LEN} characters, got {len(slot_name)}"
        )
    if not slot_name.isascii():
        raise ValueError(f"slot_name must contain only ASCII characters, got {slot_name!r}")

    rc = device.set_property_uint16(constants.PROP_SLOT_CURSOR, slot_index)
    if rc != 0:
        raise CameraConnectionError(
            f"Failed to set slot cursor to slot {slot_index} (rc={rc})"
        )

    time.sleep(PRE_WRITE_DELAY_S)

    # Rename slot now that the cursor is positioned.
    current_name = device.get_property_string(constants.PROP_SLOT_NAME)
    if current_name != slot_name:
        device.set_property_string(constants.PROP_SLOT_NAME, slot_name)

    # --- Step 2: validate recipe and translate to PTP values ---
    # recipe_to_ptp_values validates the recipe internally before converting.
    ptp_items = recipe_to_ptp_values(recipe).items()

    # --- Step 3: write each property ---
    failed_codes: list[int] = [code for code, _ in ptp_items]  # shrinks as writes succeed
    written: list[tuple[int, int]] = []  # (code, value) pairs that reported success

    for code, value in ptp_items:
        time.sleep(PRE_WRITE_DELAY_S)   # 50 ms before write

        rc = set_prop_with_retry(device, code, value)
        if rc == 0:
            failed_codes.remove(code)
            written.append((code, value))

        time.sleep(POST_WRITE_DELAY_S)  # 200 ms after write

        # Liveness ping after every write — abort if camera is gone.
        ping_rc = device.ping()
        if ping_rc != 0:
            raise CameraConnectionError(
                f"Camera became unreachable after writing property 0x{code:04X} "
                f"(ping returned {ping_rc}).  "
                f"Remaining failed codes: {[hex(c) for c in failed_codes]}"
            )

    # --- Step 4: verify written properties ---
    verified_name = device.get_property_string(constants.PROP_SLOT_NAME)
    if verified_name != slot_name:
        logger.warning(
            "Slot name verification failed: wrote %r, read back %r",
            slot_name,
            verified_name,
        )

    verification_failures = verify_written_properties(device, written)
    failed_codes.extend(verification_failures)

    return failed_codes
