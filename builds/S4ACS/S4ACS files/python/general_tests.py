import json
import os
from datetime import datetime

import astropy.io.fits as fits
import numpy as np
import pandas as pd
from astropy.time import Time
from header import CCD, S4GUI, S4ICS, TCS, Focuser, General_KWs, Weather_Station
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
    "S4GUI": s4gui_json,
    "GENERAL KW": general_kw,
}

dicts = {k: json.dumps(v) for (k, v) in dicts.items()}
dicts["S4ICS"] = ics_kw
log_file = "C:\\Users\\Denis\\SPARC4\\ACS\\20250429\\acs_ch1_keywords.log"
for cls in [S4ICS]:
    tcs = cls(dicts, log_file)
    tcs.fix_keywords()
print(repr(tcs.hdr))

# image = np.zeros((100, 100), dtype=np.int16)
# file = os.path.join("C:\\", "images", "today", "test.fits")
# fits.writeto(file, image, header=tcs.hdr, overwrite=True)
