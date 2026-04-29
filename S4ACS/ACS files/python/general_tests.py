import json
import os
from datetime import datetime
from os.path import dirname, join, realpath

import astropy.io.fits as fits
import numpy as np
import pandas as pd
from astropy.time import Time
from header import (
    ICS,
    S4GUI,
    TCS,
    Focuser,
    General_ECHARPE_KWs,
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
    "ICS": ics_kw,
}
dicts = {k: json.dumps(v) for (k, v) in dicts.items()}

log_file = "C:\\Users\\Denis\\SPARC4\\ACS\\20250429\\acs_ch1_keywords.log"
csv_folder = join(dirname(realpath(__file__)), "csvs", "echarpe")
hdr_params = Header_Parameters(csv_folder)
hdr = fits.Header(hdr_params.cards)
for cls in [Focuser]:
    tcs = cls(dicts, log_file, hdr_params, csv_folder)
    tcs.extract_info()
    tcs.fix_keywords()
    tcs.validate_info()
    hdr = tcs.fill_image_header(hdr)
print(repr(hdr))

# image = np.zeros((100, 100), dtype=np.int16)
# file = os.path.join("C:\\", "images", "today", "test.fits")
# fits.writeto(file, image, header=tcs.hdr, overwrite=True)
