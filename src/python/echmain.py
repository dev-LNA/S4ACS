import traceback

import numpy as np
from astropy.io import fits
from header_formatter.data_types import Error_Json
from header_formatter.header import (
    EICS,
    GUI,
    TCS,
    Focuser,
    General_ECHARPE_KWs,
    Weather_Station,
    iKon_L,
)
from header_formatter.setup import Header_Class_Setup


def main(
    _file_name: str,
    data: np.ndarray,
    _hdr_data: str,
) -> str:
    error_json = Error_Json.no_error()

    try:
        setup = Header_Class_Setup("echarpe")
        hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
            _hdr_data, _file_name
        )

        for obj in [
            Focuser,
            EICS,
            GUI,
            TCS,
            Weather_Station,
            General_ECHARPE_KWs,
            iKon_L,
        ]:
            kws_specs = setup.create_hdr_specs(obj.name)
            obj = obj(kws_specs, hdr_cnt, log_file, file_name)
            obj.write_header_all_apps(hdr_data)
            obj.get_app_header_data()
            obj.fix_original_string()
            obj.load_json()
            obj.fix_original_hdr_data()
            obj.extract_data()
            obj.fix_keywords()
            obj.fix_remainder_keywords()
            obj.check_kws_types()
            obj.check_allowed_values()
            hdr = obj.fill_image_header(hdr)

        data = np.array(data, dtype=np.uint16)  # type: ignore
        hdu = fits.PrimaryHDU(data, hdr)
        hdu.writeto(file_name)
    except Exception:
        error_json.status = True
        error_json.code = 1
        error_json.source = traceback.format_exc()

    return error_json.json()
