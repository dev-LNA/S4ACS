from datetime import datetime
from pathlib import Path

import astropy.io.fits as fits
import numpy as np


class Post_Processor:
    IMAGE_ROTATION_MAP: dict = {
        "Conventional": {
            1: [False, True, 2],
            2: [False, False, 0],
            3: [True, False, -1],
            4: [False, False, -1],
        },
        "Electron Multiplying": {
            1: [True, True, 2],
            2: [True, False, 0],
            3: [False, False, -1],
            4: [True, False, -1],
        },
    }

    def __init__(self, file_name: Path, data: np.ndarray, hdr: fits.Header) -> None:
        self.file_name = file_name
        self.data = np.array(data, dtype=np.uint16)  # type: ignore
        self.hdr = hdr

    def process(self) -> None:
        self._rotate_image()
        hdu = fits.PrimaryHDU(self.data, self.hdr)
        hdu = self._fix_standard_keywords(hdu)
        hdu.writeto(self.file_name)

    @staticmethod
    def _fix_standard_keywords(hdu: fits.PrimaryHDU) -> fits.PrimaryHDU:
        hdu.header["BZERO"] = (32768, "Zero point in scaling equation")
        hdu.header["BSCALE"] = (1, "Linear factor in scaling equation")
        hdu.header["NAXIS1"] = (hdu.header["NAXIS1"], "Number of columns")
        hdu.header["NAXIS2"] = (hdu.header["NAXIS2"], "Number of rows")
        hdu.header["DATEFILE"] = datetime.now().isoformat()
        hdu.add_datasum(when="Data unit checksum")
        hdu.add_checksum(when="HDU checksum", override_datasum=True)
        return hdu

    def _rotate_image(self) -> None:
        channel, em_mode = self.hdr["CHANNEL"], self.hdr["EMMODE"]
        invert_x, invert_y, nrot90deg = self.IMAGE_ROTATION_MAP[em_mode][channel]
        if invert_x:
            self.data = np.fliplr(self.data)
        if invert_y:
            self.data = np.flipud(self.data)
        if nrot90deg != 0:
            self.data = np.rot90(self.data, k=nrot90deg)
