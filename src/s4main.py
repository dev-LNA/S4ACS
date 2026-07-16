import traceback

import numpy as np

from python.data_types import Error_Json
from python.post_processor import Post_Processor
from python.setup import Header_Class_Setup


def main(
    file_name: str,
    data: np.ndarray,
    hdr_data: tuple,
) -> str:
    error_json = Error_Json.no_error()

    try:
        setup = Header_Class_Setup("sparc4")
        setup.create_setup(hdr_data, file_name)
        hdr = setup.hdr

        for obj in setup.header_classes_list:
            obj.write_header_all_apps(setup.hdr_data)
            obj.get_app_header_data()
            obj.fix_header_data()
            obj.load_json()
            obj.extract_data()
            obj.fix_keywords()
            obj.validate_info()
            hdr = obj.fill_image_header(hdr)

        processor = Post_Processor(setup.file_name, data, hdr)
        processor.process()
    except Exception:
        error_json.status = True
        error_json.code = 1
        error_json.source = traceback.format_exc()

    return error_json.model_dump_json()
