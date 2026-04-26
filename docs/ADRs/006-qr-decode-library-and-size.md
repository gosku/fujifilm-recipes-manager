# ADR 006 — QR decode library and minimum QR code size

**Status**: Accepted
**Date**: 2026-04-25

---

## Context

Recipe cards embed a QR code that encodes the recipe as minified JSON. Users can
import a recipe by uploading a card image; the app decodes the QR and creates the
recipe. A bug report showed that a valid, visually intact card failed to import
with `failure_reason=qr_not_found`.

The investigation revealed two separate but related problems:

1. **Decoder bug** — `cv2.QRCodeDetector.detect()` returns finder-pattern centres,
   not QR corners. The bounding box of three finder-pattern centres underestimates
   the QR extent, causing the crop+upscale fallback to cut into the QR itself,
   making it undecodable.

2. **Generation problem** — The QR code was generated at 200×200 px. A typical
   recipe payload encodes as QR version 13–15 (69–77 modules), yielding only
   ~2.6–2.9 px per module after resizing. At that density JPEG compression
   artefacts corrupt module edges, making detection unreliable regardless of which
   library is used.

---

## Problem

Which QR decoding library should be used, and what is the minimum QR size that
makes full-image decoding reliable across all card types (gradient background,
sharp photo background, blurred photo background)?

---

## Options considered

### Option A — Keep `opencv-python-headless` with an improved crop strategy

Fix the bounding-box underestimation bug (increase padding, extend by detected
span) and keep cv2 as the sole decoder.

**Result from testing (200 px QR, 696-card corpus):**
- cv2 direct: 58.3%
- cv2 with crop fix: 79.0%
- Best achievable with cv2 alone: 79.0% — 146 cards unrecoverable.

**Why we did not choose this option:**

Even with the crop fix, cv2 fails on cards where `detect()` returns no points at
all (four cards in the corpus had `pts=None`). The spatial detection algorithm in
`cv2.QRCodeDetector` is fundamentally unsuited to QR codes that are small relative
to the image. The crop strategy also requires position knowledge to recover the
hardest cases, which breaks when template layout changes.

### Option B — Switch to `zxingcpp` with no crop

Replace cv2 entirely with `zxingcpp`, which uses a different binarisation and
spatial detection pipeline, and call it on the full image with no preprocessing.

**Result from testing (200 px QR, 696-card corpus):**
- zxingcpp alone: 57.0% — worse than cv2 with crop fix.

**Why we did not choose this option alone:**

At 200 px / ~2.6 px per module, zxingcpp also struggles. The library is not the
bottleneck; the QR density after JPEG compression is.

### Option C — Combine cv2 and zxingcpp as a fallback chain

Try cv2 (with crop fix) first; fall back to zxingcpp if it fails.

**Result from testing (200 px QR, 696-card corpus):**
- cv2 + zxingcpp combined: 99.3% (691/696)
- With additional cv2 2× upscale step: 99.6% (693/696)
- 3 cards unrecoverable by any strategy (same recipe, same low-contrast grayscale
  background; only position-based crop recovers them).

**Why we did not choose this option:**

It requires two libraries, three decode attempts, and still leaves an irreducible
3-card failure case. Complexity without full reliability.

### Option D — Increase QR size to 300 px and switch to `zxingcpp` ✓ CHOSEN

Increase `_QR_SIZE` from 200 to 300 px at generation time, and replace
`cv2.QRCodeDetector` with `zxingcpp` at decode time.

At 300 px, version-15 QR (77 modules) yields ~3.9 px per module — enough margin
that JPEG compression artefacts no longer corrupt module edges.

**Result from testing (300 px QR, 681-card corpus):**
- zxingcpp on full image: **100%** (681/681) — gradient, sharp photo, blurred photo.
- No cropping, no fallback, no position knowledge required.
- cv2 with crop fix at 300 px: 73.7% — cv2 does not benefit proportionally,
  confirming it is the wrong tool regardless of QR size.

**Intermediate size tested (250 px, 681-card corpus):**
- zxingcpp: 71.7%; cv2 + zxingcpp combined: 87.1% — *worse* than 200 px.
- JPEG quantisation interacts non-monotonically with QR density; 250 px happens
  to land in a worse spot than 200 px. 300 px is where reliable detection begins.

---

## Decision

- **QR size**: increase `_QR_SIZE` from 200 to 300 px in
  `src/domain/recipes/cards/operations.py`.
- **Decode library**: replace `cv2.QRCodeDetector` with `zxingcpp` in
  `src/domain/recipes/cards/queries.py`.
- **Dependencies**: add `zxing-cpp` to `requirements.txt`, remove
  `opencv-python-headless`.

---

## Consequences

**Positive:**
- Single library, single decode call, no position assumption — works for any
  future template layout.
- `zxing-cpp` ships self-contained pre-built wheels for Linux (x86_64, arm64),
  macOS (Intel and Apple Silicon), and Windows. No OS-level library required
  (contrast with `pyzbar`, which requires `libzbar0`).
- `opencv-python-headless` (~30 MB) is replaced by the much lighter `zxing-cpp`.
- 300 px QR is visually larger on the card but still contained within the
  bottom-right quadrant of the 1080×1080 canvas.

**Negative:**
- Existing 200 px cards already generated and shared will be decoded less
  reliably (99.3% with the legacy cv2 + zxingcpp chain, 3 cards unrecoverable).
  Re-generating them is optional but recommended.
- The crop+upscale fallback in `_decode_qr` (cv2-specific) is removed. The
  EXIF fallback (`_read_exif_recipe`) is retained as a secondary path for
  gradient-background cards.
