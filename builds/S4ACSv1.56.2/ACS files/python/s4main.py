import json
import traceback
from os.path import dirname, join, realpath

import astropy.io.fits as fits
import numpy as np
from header import (
    S4GUI,
    S4ICS,
    TCS,
    Focuser,
    General_SPARC4_KWs,
    Header_Parameters,
    Weather_Station,
    iXon_Ultra,
)
from utils import (
    SUB_SYSTEMS,
    fix_image_orientation,
    fix_standard_keywords,
    verify_file_already_exists,
)


def main(night_dir, file, data, tuple_header_jsons, log_file) -> str:
    error_json = {"status": False, "code": 0, "source": ""}
    try:
        dict_header_jsons = {k: v for (k, v) in zip(SUB_SYSTEMS, tuple_header_jsons)}
        data = np.asarray(data, dtype=np.uint16)
        file = join(night_dir, file)

        csv_folder = join(dirname(realpath(__file__)), "csvs", "sparc4")
        hdr_params = Header_Parameters(csv_folder)
        hdr = fits.Header(hdr_params.cards)

        for cls in [
            Focuser,
            S4ICS,
            S4GUI,
            TCS,
            Weather_Station,
            General_SPARC4_KWs,
            iXon_Ultra,
        ]:
            obj = cls(dict_header_jsons, log_file, hdr_params, csv_folder)
            obj.extract_info()
            obj.fix_keywords()
            obj.validate_info()
            hdr = obj.fill_image_header(hdr)
        data = fix_image_orientation(hdr["CHANNEL"], hdr["EMMODE"], data)
        file = verify_file_already_exists(file)
        hdu = fits.PrimaryHDU(data, hdr)
        hdu = fix_standard_keywords(hdu)
        hdu.writeto(file, output_verify="ignore")
        return json.dumps(error_json)
    except Exception:
        error_json["status"] = True
        error_json["code"] = 1
        error_json["source"] = traceback.format_exc()
        return json.dumps(error_json)
