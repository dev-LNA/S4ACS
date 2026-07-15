import json
import traceback
from pathlib import Path

import astropy.io.fits as fits
import numpy as np

from python.data_types import SPARC4_Applications
from python.header import (
    S4GUI,
    S4ICS,
    TCS,
    Focuser,
    General_SPARC4_KWs,
    Weather_Station,
    iXon_Ultra,
)
from python.header_content import Header_Content
from python.utils import (
    fix_image_orientation,
    fix_standard_keywords,
    verify_file_already_exists,
)


def main(
    night_dir: str,
    _file: str,
    _data: np.ndarray,
    _header_jsons: tuple,
    log_file: str,
) -> str:
    error_json = {"status": False, "code": 0, "source": ""}
    try:
        header_jsons = SPARC4_Applications.from_tuple(_header_jsons)
        data: np.ndarray = np.asarray(_data, dtype=np.uint16)
        file = Path(night_dir) / _file
        csv_folder = Path(__file__).parent / "csv" / "sparc4"
        hdr_params = Header_Content(csv_folder)
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
            header_data = header_jsons.model_dump()
            obj = cls(log_file, hdr_params, csv_folder)
            obj.write_header_all_apps(header_data)
            obj.get_app_header_data()
            obj.fix_header_data()
            obj.load_json()
            obj.extract_data()
            obj.fix_keywords()
            obj.validate_info()
            hdr = obj.fill_image_header(hdr)

        data = fix_image_orientation((hdr["CHANNEL"]), hdr["EMMODE"], data)  # type: ignore
        hdu = fits.PrimaryHDU(data, hdr)
        hdu = fix_standard_keywords(hdu)
        file = verify_file_already_exists(file)
        hdu.writeto(file, output_verify="ignore")
        return json.dumps(error_json)
    except Exception:
        error_json["status"] = True
        error_json["code"] = 1
        error_json["source"] = traceback.format_exc()
        return json.dumps(error_json)
