import json
import traceback

import numpy as np

from python.header import (
    S4GUI,
    S4ICS,
    TCS,
    Focuser,
    General_SPARC4_KWs,
    Weather_Station,
    iXon_Ultra,
)
from python.post_processor import Post_Processor
from python.setup import Header_Class_Setup


def main(
    _file_name: str,
    _data: np.ndarray,
    _hdr_data: tuple,
    log_file: str,
) -> str:
    error_json = {"status": False, "code": 0, "source": ""}
    try:
        setup = Header_Class_Setup("sparc4")
        setup.create_setup(_hdr_data, _file_name)
        hdr = setup.hdr

        for cls in [
            Focuser,
            S4ICS,
            S4GUI,
            TCS,
            Weather_Station,
            General_SPARC4_KWs,
            iXon_Ultra,
        ]:
            kws_specs = setup.create_hdr_specs(cls.name)
            obj = cls(log_file, setup.hdr_cnt, kws_specs)
            obj.write_header_all_apps(setup.hdr_data)
            obj.get_app_header_data()
            obj.fix_header_data()
            obj.load_json()
            obj.extract_data()
            obj.fix_keywords()
            obj.validate_info()
            hdr = obj.fill_image_header(hdr)

        processor = Post_Processor(setup.file_name, _data, hdr)
        processor.process()

        return json.dumps(error_json)
    except Exception:
        error_json["status"] = True
        error_json["code"] = 1
        error_json["source"] = traceback.format_exc()
        return json.dumps(error_json)
