import unittest
from pathlib import Path

import astropy.io.fits as fits
import numpy as np
from freezegun import freeze_time
from header_formatter.post_processor import Post_Processor


class Test_Setup(unittest.TestCase):
    def setUp(self) -> None:
        self.file_name = Path.home() / "images" / "today" / "00000000_s4c1_000001.fits"
        self.data = np.asarray([[1, 0, 1], [0, 0, 0], [1, 0, 0]])
        self.hdr = fits.Header()
        self.hdr["CHANNEL"] = 1
        self.hdr["EMMODE"] = "Conventional"
        self.post_proc = Post_Processor(self.file_name, self.data, self.hdr)
        return super().setUp()

    def test_init(self) -> None:
        assert self.file_name == self.post_proc.file_name
        assert self.hdr == self.post_proc.hdr
        assert np.allclose(self.data, self.post_proc.data)
        assert self.post_proc.data.dtype == np.uint16

    @freeze_time("2026-07-17T12:00:00.123456")
    def test_fix_str_kws(self) -> None:
        hdu = fits.PrimaryHDU(self.data, self.hdr)
        hdu = self.post_proc._fix_standard_keywords(hdu)
        assert tuple(hdu.header.cards["BZERO"])[1:] == (
            32768,
            "Zero point in scaling equation",
        )
        assert tuple(hdu.header.cards["BSCALE"])[1:] == (
            1,
            "Linear factor in scaling equation",
        )
        assert tuple(hdu.header.cards["NAXIS1"])[1:] == (3, "Number of columns")
        assert tuple(hdu.header.cards["NAXIS2"])[1:] == (3, "Number of rows")
        assert hdu.header["DATEFILE"] == "2026-07-17T12:00:00.123456"
        assert hdu.verify_checksum()
        assert hdu.verify_datasum()

    def test_rotation_image_1(self) -> None:
        self.post_proc._rotate_image()
        data = np.asarray([[1, 0, 1], [0, 0, 0], [0, 0, 1]])
        assert np.allclose(self.post_proc.data, data)

    def test_rotation_image_2(self) -> None:
        self.post_proc.hdr["CHANNEL"] = 2
        self.post_proc._rotate_image()
        data = np.asarray([[1, 0, 1], [0, 0, 0], [1, 0, 0]])
        assert np.allclose(self.post_proc.data, data)

    def test_rotation_image_3(self) -> None:
        self.post_proc.hdr["CHANNEL"] = 3
        self.post_proc._rotate_image()
        data = np.asarray([[0, 0, 1], [0, 0, 0], [1, 0, 1]])
        assert np.allclose(self.post_proc.data, data)

    def test_rotation_image_4(self) -> None:
        self.post_proc.hdr["CHANNEL"] = 4
        self.post_proc._rotate_image()
        data = np.asarray([[1, 0, 1], [0, 0, 0], [0, 0, 1]])
        assert np.allclose(self.post_proc.data, data)

    def test_rotation_image_5(self) -> None:
        self.post_proc.hdr["EMMODE"] = "Electron Multiplying"
        self.post_proc._rotate_image()
        data = np.asarray([[1, 0, 1], [0, 0, 0], [1, 0, 0]])
        assert np.allclose(self.post_proc.data, data)

    def test_rotation_image_6(self) -> None:
        self.post_proc.hdr["EMMODE"] = "Electron Multiplying"
        self.post_proc.hdr["CHANNEL"] = 2
        self.post_proc._rotate_image()
        data = np.asarray([[1, 0, 1], [0, 0, 0], [0, 0, 1]])
        assert np.allclose(self.post_proc.data, data)

    def test_rotation_image_7(self) -> None:
        self.post_proc.hdr["EMMODE"] = "Electron Multiplying"
        self.post_proc.hdr["CHANNEL"] = 3
        self.post_proc._rotate_image()
        data = np.asarray([[1, 0, 1], [0, 0, 0], [0, 0, 1]])
        assert np.allclose(self.post_proc.data, data)

    def test_rotation_image_8(self) -> None:
        self.post_proc.hdr["EMMODE"] = "Electron Multiplying"
        self.post_proc.hdr["CHANNEL"] = 4
        self.post_proc._rotate_image()
        data = np.asarray([[0, 0, 1], [0, 0, 0], [1, 0, 1]])
        assert np.allclose(self.post_proc.data, data)

    def test_process(self) -> None:
        self.post_proc.process()
        assert self.file_name.exists()
        if self.file_name.exists():
            self.file_name.unlink()
