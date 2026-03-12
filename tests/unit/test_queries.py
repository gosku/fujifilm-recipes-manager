import os
import subprocess
from unittest.mock import patch

import pytest

from src.domain.queries import _normalise_wb_fine_tune, collect_image_paths, read_image_exif

SAMPLE_EXIFTOOL_OUTPUT = """\
[ExifTool]      ExifTool Version Number         : 12.76
[File]          File Name                       : XS107114.JPG
[IFD0]          Make                            : FUJIFILM
[IFD0]          Camera Model Name               : X-S10
[FujiFilm]      Film Mode                       : Classic Negative
[FujiFilm]      Quality                         : FINE
[FujiFilm]      Dynamic Range                   : Standard
[FujiFilm]      Dynamic Range Setting           : Manual
[FujiFilm]      Development Dynamic Range       : 400
[FujiFilm]      White Balance                   : Kelvin
[FujiFilm]      White Balance Fine Tune         : Red +60, Blue -100
[FujiFilm]      Color Temperature               : 6050
[FujiFilm]      Highlight Tone                  : 0 (normal)
[FujiFilm]      Shadow Tone                     : +1 (medium hard)
[FujiFilm]      Saturation                      : +4 (highest)
[FujiFilm]      Sharpness                       : -1 (medium soft)
[ExifIFD]       Sharpness                       : Soft
[FujiFilm]      Noise Reduction                 : -4 (weakest)
[FujiFilm]      Clarity                         : 0
[FujiFilm]      Color Chrome Effect             : Off
[FujiFilm]      Color Chrome FX Blue            : Strong
[FujiFilm]      Grain Effect Roughness          : Off
[FujiFilm]      Grain Effect Size               : Off
[FujiFilm]      Fuji Flash Mode                 : Not Attached
[FujiFilm]      Flash Exposure Comp             : 0
[FujiFilm]      Focus Mode                      : Auto
[FujiFilm]      Shutter Type                    : Mechanical
[FujiFilm]      Lens Modulation Optimizer       : On
[FujiFilm]      Picture Mode                    : Aperture-priority AE
[FujiFilm]      Drive Mode                      : Single
[FujiFilm]      Image Stabilization             : Sensor-shift; On (mode 1, continuous); 0
[ExifIFD]       ISO                             : 640
[ExifIFD]       Exposure Compensation           : +0.33
[ExifIFD]       Date/Time Original              : 2025:12:31 12:23:57
[Composite]     Date/Time Original              : 2025:12:31 12:23:57+11:00
"""


class TestReadImageExif:
    def test_parses_relevant_fields(self, tmp_path):
        image_path = str(tmp_path / "test.jpg")

        with patch("src.domain.queries.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["exiftool", image_path],
                returncode=0,
                stdout=SAMPLE_EXIFTOOL_OUTPUT,
                stderr="",
            )
            metadata = read_image_exif(image_path)

        assert metadata.film_simulation == "Classic Negative"
        assert metadata.camera_make == "FUJIFILM"
        assert metadata.iso == "640"
        assert metadata.sharpness == "-1 (medium soft)"
        assert metadata.white_balance_fine_tune == "Red +3, Blue -5"
        assert metadata.quality == "FINE"
        assert metadata.dynamic_range_setting == "Manual"
        assert metadata.development_dynamic_range == "400"
        assert metadata.flash_mode == "Not Attached"
        assert metadata.flash_exposure_comp == "0"
        assert metadata.focus_mode == "Auto"
        assert metadata.shutter_type == "Mechanical"
        assert metadata.lens_modulation_optimizer == "On"
        assert metadata.picture_mode == "Aperture-priority AE"
        assert metadata.drive_mode == "Single"
        assert metadata.image_stabilization == "Sensor-shift; On (mode 1, continuous); 0"
        assert metadata.color_temperature == "6050"

    def test_prefers_fujifilm_group_for_sharpness(self, tmp_path):
        image_path = str(tmp_path / "test.jpg")

        with patch("src.domain.queries.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["exiftool", image_path],
                returncode=0,
                stdout=SAMPLE_EXIFTOOL_OUTPUT,
                stderr="",
            )
            metadata = read_image_exif(image_path)

        # ExifIFD has "Soft" but FujiFilm group should win
        assert metadata.sharpness == "-1 (medium soft)"

    def test_prefers_composite_group_for_date_taken(self, tmp_path):
        image_path = str(tmp_path / "test.jpg")

        with patch("src.domain.queries.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["exiftool", image_path],
                returncode=0,
                stdout=SAMPLE_EXIFTOOL_OUTPUT,
                stderr="",
            )
            metadata = read_image_exif(image_path)

        # ExifIFD has no timezone but Composite has +11:00 — Composite should win
        assert metadata.date_taken == "2025:12:31 12:23:57+11:00"

    def test_ignores_irrelevant_fields(self, tmp_path):
        image_path = str(tmp_path / "test.jpg")

        with patch("src.domain.queries.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["exiftool", image_path],
                returncode=0,
                stdout="ExifTool Version Number         : 12.76\nFile Name                       : test.jpg\n",
                stderr="",
            )
            metadata = read_image_exif(image_path)

        assert not hasattr(metadata, "exiftool_version_number")
        assert not hasattr(metadata, "file_name")

    def test_raises_on_exiftool_failure(self, tmp_path):
        image_path = str(tmp_path / "test.jpg")

        with patch("src.domain.queries.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["exiftool", image_path],
                returncode=1,
                stdout="",
                stderr="File not found",
            )
            with pytest.raises(RuntimeError, match="exiftool failed"):
                read_image_exif(image_path)


class TestNormaliseWbFineTune:
    def test_divides_values_by_20(self):
        assert _normalise_wb_fine_tune("Red +60, Blue -100") == "Red +3, Blue -5"

    def test_handles_zero(self):
        assert _normalise_wb_fine_tune("Red +20, Blue +0") == "Red +1, Blue +0"

    def test_handles_negative_red(self):
        assert _normalise_wb_fine_tune("Red -40, Blue +60") == "Red -2, Blue +3"


class TestCollectImagePaths:
    def test_returns_jpg_files(self, tmp_path):
        (tmp_path / "photo1.jpg").write_bytes(b"\xff\xd8")
        (tmp_path / "photo2.JPG").write_bytes(b"\xff\xd8")
        (tmp_path / "photo3.jpeg").write_bytes(b"\xff\xd8")
        (tmp_path / "document.pdf").write_bytes(b"%PDF")

        paths = collect_image_paths(str(tmp_path))

        filenames = [os.path.basename(p) for p in paths]
        assert "photo1.jpg" in filenames
        assert "photo2.JPG" in filenames
        assert "photo3.jpeg" in filenames
        assert "document.pdf" not in filenames

    def test_returns_sorted_paths(self, tmp_path):
        (tmp_path / "c.jpg").write_bytes(b"\xff\xd8")
        (tmp_path / "a.jpg").write_bytes(b"\xff\xd8")
        (tmp_path / "b.jpg").write_bytes(b"\xff\xd8")

        paths = collect_image_paths(str(tmp_path))

        filenames = [os.path.basename(p) for p in paths]
        assert filenames == sorted(filenames)

    def test_finds_files_recursively(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "top.jpg").write_bytes(b"\xff\xd8")
        (sub / "nested.jpg").write_bytes(b"\xff\xd8")

        paths = collect_image_paths(str(tmp_path))

        filenames = [os.path.basename(p) for p in paths]
        assert "top.jpg" in filenames
        assert "nested.jpg" in filenames

    def test_returns_absolute_paths(self, tmp_path):
        (tmp_path / "photo.jpg").write_bytes(b"\xff\xd8")

        paths = collect_image_paths(str(tmp_path))

        for p in paths:
            assert os.path.isabs(p)

    def test_empty_folder_returns_empty_list(self, tmp_path):
        paths = collect_image_paths(str(tmp_path))
        assert paths == []

    def test_nonexistent_folder_raises(self):
        with pytest.raises(FileNotFoundError):
            collect_image_paths("/nonexistent/folder")
