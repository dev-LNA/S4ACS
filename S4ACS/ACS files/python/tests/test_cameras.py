import json
import unittest
from os.path import dirname, join, realpath
from pathlib import Path

import astropy.io.fits as fits
import numpy as np
import pandas as pd
from header import (
    CCD,
    ICS,
    S4GUI,
    General_ECHARPE_KWs,
    General_KWs,
    General_SPARC4_KWs,
    Header_Parameters,
    Header_Tester,
    Weather_Station,
)


class Test_Camera(unittest.TestCase):

    dict_header_jsons: dict = {"CCD": '{"FILENAME":"s4acs1_000001.fits"}'}
    log_file = join("tests", "files", "log.log")
    tester_hdr_content = {
        "FILENAME": "00000000_s4c1_000000.fits",
        "READRATE": 1,
        "PREAMP": 1,
        "FRAMEIND": 0,
        "EXPTIME": 9.9999999e-6,
        "VBIN": 1,
        "INITLIN": 1,
        "INITCOL": 1,
        "FINALLIN": 1024,
        "FINALCOL": 1024,
        "HBIN": 1,
        "CCDSERN": 9914,
        "TRIGGER": 0,
        "ACQMODE": 3,
        "SHUTTER": 2,
        "VCLKAMP": 0,
        "NFRAMES": 1,
        "DATE-OBS": "0000-00-00T00:00:00.000000",
        "UTDATE": "0000-00-00",
        "UTTIME": "00:00:00.000000",
        "CCDTEMP": -30,
        "TEMPST": "TEMPERATURE_STABILIZED",
        "TGTEMP": -30,
        "COOLER": True,
    }

    @classmethod
    def setUpClass(cls):
        cls.csv_folder = join(dirname(realpath(__file__)), "..", "csvs", "sparc4")
        cls.hdr_params = Header_Parameters(cls.csv_folder)

        cls.dict_header_jsons["CCD"] = json.dumps(cls.tester_hdr_content)
        cls.tester = CCD(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.tester.extract_info()
        cls.fixed_tester = CCD(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.fixed_tester.extract_info()
        cls.fixed_tester.fix_keywords()

    def test_idx_tab(self):
        assert self.tester.idx_tab == 3

    def test_write_read_noise(self):
        assert self.fixed_tester.new_json["RDNOISE"] == 65.5

    def test_write_gain(self):
        assert self.fixed_tester.new_json["GAIN"] == 4.39

    def test_fix_exp_time(self):
        assert self.fixed_tester.new_json["EXPTIME"] == 1e-5

    def test_calc_NAXIS1(self):
        assert self.fixed_tester.new_json["NAXIS1"] == 1024

    def test_calc_NAXIS2(self):
        assert self.fixed_tester.new_json["NAXIS2"] == 1024

    def test_TRIGGER(self):
        assert self.fixed_tester.new_json["TRIGGER"] == "Internal"

    def test_ACQMODE(self):
        assert self.fixed_tester.new_json["ACQMODE"] == "Kinetics"

    def test_SHUTTER(self):
        assert self.fixed_tester.new_json["SHUTTER"] == "Closed"

    def test_VCLKAMP(self):
        assert self.fixed_tester.new_json["VCLKAMP"] == "Normal"

    def test_NFRAMES(self):
        assert self.fixed_tester.new_json["NFRAMES"] == 1

    def test_date_obs(self):
        assert self.fixed_tester.new_json["DATE-OBS"] == "0000-00-00T00:00:00.000000"

    def test_utdate(self):
        assert self.fixed_tester.new_json["UTDATE"] == "0000-00-00"

    def test_uttime(self):
        assert self.fixed_tester.new_json["UTTIME"] == "00:00:00.000000"

    def test_ccd_temp(self):
        assert self.fixed_tester.new_json["CCDTEMP"] == -30

    def test_temp_status(self):
        assert self.fixed_tester.new_json["TEMPST"] == "TEMPERATURE_STABILIZED"

    def test_target_temp(self):
        assert self.fixed_tester.new_json["TGTEMP"] == -30

    def test_cooler(self):
        assert self.fixed_tester.new_json["COOLER"] == True
