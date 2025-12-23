import json
import os
from datetime import datetime
from os.path import dirname, join, realpath

import astropy.io.fits as fits
import numpy as np
import pandas as pd
from astropy.time import Time
from header import (
    S4GUI,
    S4ICS,
    TCS,
    Focuser,
    General_SPARC4_KWs,
    Header_Parameters,
    Weather_Station,
    iKon_L,
    iXon_Ultra,
)
from utils import (
    WS_json,
    ccd_kw,
    everthing_json,
    focuser_json,
    general_kw,
    ics_kw,
    s4gui_json,
    tcs_json,
    test_json,
)

dicts = {
    "CCD": ccd_kw,
    "WSTATION": WS_json,
    "FOCUSER": focuser_json,
    "GENERAL KW": general_kw,
    "TCS": tcs_json,
    "GUI": s4gui_json,
    "GENERAL KW": general_kw,
}

dicts = {k: json.dumps(v) for (k, v) in dicts.items()}
dicts["ICS"] = ics_kw
log_file = "C:\\Users\\Denis\\SPARC4\\ACS\\20250429\\acs_ch1_keywords.log"
csv_folder = join(dirname(realpath(__file__)), "csvs", "sparc4")
hdr_params = Header_Parameters(csv_folder)
for cls in [iXon_Ultra]:
    tcs = cls(dicts, log_file, hdr_params)
    tcs.extract_info()
    tcs.fix_keywords()
    tcs.validate_info()
print(repr(tcs.new_json))

# image = np.zeros((100, 100), dtype=np.int16)
# file = os.path.join("C:\\", "images", "today", "test.fits")
# fits.writeto(file, image, header=tcs.hdr, overwrite=True)
