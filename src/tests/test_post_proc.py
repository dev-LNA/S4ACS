import unittest
from pathlib import Path

import astropy.io.fits as fits
import numpy as np
from freezegun import freeze_time

from python.post_processor import Post_Processor


class Test_Setup(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:

        return super().setUpClass()

    def test_init(self) -> None:
        file_name = Path.home() / "images" / "today" / "00000000_s4c1_000001.fits"
        data = np.zeros((100, 100), dtype=np.uint32)
        hdr = fits.Header()
        post_proc = Post_Processor(file_name, data, hdr)
        assert file_name == post_proc.file_name
        assert hdr == post_proc.hdr
        assert np.allclose(data, post_proc.data)
        assert post_proc.data.dtype == np.uint16

    @freeze_time("2026-07-17T12:00:00.123456")
    def test_fix_str_kws(self) -> None:
        file_name = Path.home() / "images" / "today" / "00000000_s4c1_000001.fits"
        data = np.zeros((100, 100), dtype=np.uint32)
        hdr = fits.Header()
        post_proc = Post_Processor(file_name, data, hdr)
        hdu = fits.PrimaryHDU(data, hdr)
        hdu = post_proc._fix_standard_keywords(hdu)
        assert tuple(hdu.header.cards["BZERO"])[1:] == (
            32768,
            "Zero point in scaling equation",
        )
        assert tuple(hdu.header.cards["BSCALE"])[1:] == (
            1,
            "Linear factor in scaling equation",
        )
        assert tuple(hdu.header.cards["NAXIS1"])[1:] == (100, "Number of columns")
        assert tuple(hdu.header.cards["NAXIS2"])[1:] == (100, "Number of rows")
        assert hdu.header["DATEFILE"] == "2026-07-17T12:00:00.123456"
        assert hdu.verify_checksum()
        assert hdu.verify_datasum()
