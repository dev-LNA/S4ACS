import json
import os
import traceback

import astropy.io.fits as fits
import numpy as np
from header import CCD, S4GUI, S4ICS, TCS, Focuser, General_KWs, Weather_Station
from utils import (
    fix_image_orientation,
    sub_systems,
    verify_file_already_exists,
    write_error_log,
)


def main(night_dir, file, data, tuple_header_jsons, log_file):
    error_json = {"status": False, "code": 0, "source": ""}
    try:
        dict_header_jsons = {k: v for (k, v) in zip(sub_systems, tuple_header_jsons)}
        data = np.asarray(data, dtype=np.uint16)
        file = os.path.join(night_dir, file)

        for cls in [Focuser, S4ICS, S4GUI, TCS, Weather_Station, General_KWs, CCD]:
            obj = cls(dict_header_jsons, log_file)
            obj.fix_keywords()
            hdr = obj.hdr
        obj.reset_header()
        data = fix_image_orientation(hdr["CHANNEL"], hdr["EMMODE"], data)
        file = verify_file_already_exists(file)
        hdu = fits.PrimaryHDU(data, hdr)
        hdu.header["BZERO"] = (32768, "Zero point in scaling equation")
        hdu.header["BSCALE"] = (1, "Linear factor in scaling equation")
        hdu.header["NAXIS1"] = (hdu.header["NAXIS1"], "Number of columns")
        hdu.header["NAXIS2"] = (hdu.header["NAXIS2"], "Number of rows")
        hdu.writeto(file, output_verify="ignore")
        return json.dumps(error_json)
    except Exception as e:
        error_json["status"] = True
        error_json["code"] = 1
        error_json["source"] = repr(e)
        return json.dumps(error_json)
