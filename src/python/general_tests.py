import json
import os
from pathlib import Path

import numpy as np
from astropy.io import fits
from header_formatter.header import (
    GUI,
    S4ICS,
    Focuser,
    General_SPARC4_KWs,
    Weather_Station,
    iXon_Ultra,
)
from header_formatter.setup import Header_Class_Setup
from header_formatter.utils import (
    WS_json,
    focuser_json,
    general_s4_kw,
    ics_kw,
    ixon_kw,
    s4gui_json,
    tcs_json,
)

_hdr_data = dict.fromkeys(
    ["CCD", "GUI", "ICS", "FOCUSER", "WSTATION", "GENERAL KW", "TCS"], "{}"
)
_hdr_data["CCD"] = json.dumps(ixon_kw)
_hdr_data["GUI"] = json.dumps(s4gui_json)
_hdr_data["WSTATION"] = json.dumps(WS_json)
_hdr_data["FOCUSER"] = json.dumps(focuser_json)
_hdr_data["ICS"] = json.dumps(ics_kw)
_hdr_data["TCS"] = json.dumps(tcs_json)
_hdr_data["GENERAL KW"] = json.dumps(general_s4_kw)
setup = Header_Class_Setup("sparc4")
hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
    json.dumps(_hdr_data), "00000000_s4c1_000001.fits"
)

for obj in [GUI, S4ICS, Focuser, General_SPARC4_KWs, iXon_Ultra, Weather_Station]:
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
print(repr(hdr))

image = np.zeros((100, 100), dtype=np.int16)
file = os.path.join("C:\\", "images", "today", "test.fits")
fits.writeto(file, image, header=hdr, overwrite=True)
