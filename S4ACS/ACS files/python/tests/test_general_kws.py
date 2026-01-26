import json
import unittest
from os.path import dirname, join, realpath
from pathlib import Path

import astropy.io.fits as fits
import numpy as np
import pandas as pd
from header import (
    ICS,
    S4GUI,
    General_ECHARPE_KWs,
    General_KWs,
    General_SPARC4_KWs,
    Header_Parameters,
    Header_Tester,
    Weather_Station,
)


class Test_General_Kws(unittest.TestCase):

    dict_header_jsons: dict = {
        "GENERAL KW": "",
        "CCD": '{"FILENAME":"s4acs1_000001.fits"}',
    }
    log_file = join("tests", "files", "log.log")
    tester_hdr_content = {
        "FRAMETRF": True,
        "EMGAIN": 2,
        "EXPTIME": 1.1,
        "OBSERVER": "DENIS",
        "VSHIFT": 3,
        "INSTMODE": "PHOT",
        "GUIVRSN": "v0.0.0",
        "WPROMODE": "ACTIVE",
        "PRESSURE": "10,1",
        "CYCLIND": 0,
        "ACSVRSN": "v0.0.0",
    }

    @classmethod
    def setUpClass(cls):
        cls.csv_folder = join(dirname(realpath(__file__)), "..", "csvs", "sparc4")
        cls.hdr_params = Header_Parameters(cls.csv_folder)

        cls.dict_header_jsons["GENERAL KW"] = json.dumps(cls.tester_hdr_content)
        cls.tester = Header_Tester(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.tester.extract_info()
        cls.fixed_tester = Header_Tester(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.fixed_tester.extract_info()
        cls.fixed_tester.fix_keywords()

    def test_General_KWs(self):
        tester = General_KWs(
            self.dict_header_jsons, self.log_file, self.hdr_params, self.csv_folder
        )
        tester.extract_info()
        tester.fix_keywords()
        assert tester.new_json == {
            "CYCLIND": 1,
            "NAXIS": 2,
            "OBSLONG": -45.5825,
            "OBSLAT": -22.534,
            "OBSALT": 1864.0,
            "EQUINOX": 2000.0,
            "SIMPLE": True,
            "BITPIX": 16,
            "BZERO": 1,
            "BSCALE": 32768,
            "ACSVRSN": "v0.0.0",
        }

    def test_General_SPARC4_KWs(self):
        tester_hdr_content = self.tester_hdr_content.copy()
        tester_hdr_content["SEQINDEX"] = 0
        tester_hdr_content["FILENAME"] = "00000000_s4c1_000000.fits"
        dict_header_jsons = self.dict_header_jsons.copy()
        dict_header_jsons["GENERAL KW"] = json.dumps(tester_hdr_content)
        tester = General_SPARC4_KWs(
            dict_header_jsons, self.log_file, self.hdr_params, self.csv_folder
        )
        tester.extract_info()
        tester.fix_keywords()
        assert tester.new_json == {
            "CYCLIND": 1,
            "NAXIS": 2,
            "OBSLONG": -45.5825,
            "OBSLAT": -22.534,
            "OBSALT": 1864.0,
            "EQUINOX": 2000.0,
            "SIMPLE": True,
            "BITPIX": 16,
            "BZERO": 1,
            "BSCALE": 32768,
            "ACSVRSN": "v0.0.0",
            "SEQINDEX": 1,
            "INSTRUME": "SPARC4",
            "FILENAME": "00000000_s4c1_000000.fits",
        }

    def test_General_ECHARPE_KWs(self):
        tester_hdr_content = self.tester_hdr_content.copy()
        tester_hdr_content["FILENAME"] = "00000000_ECH_BLUE_000000o.fits"
        dict_header_jsons = self.dict_header_jsons.copy()
        dict_header_jsons["GENERAL KW"] = json.dumps(tester_hdr_content)
        tester = General_ECHARPE_KWs(
            dict_header_jsons, self.log_file, self.hdr_params, self.csv_folder
        )
        tester.extract_info()
        tester.fix_keywords()
        assert tester.new_json == {
            "CYCLIND": 1,
            "NAXIS": 2,
            "OBSLONG": -45.5825,
            "OBSLAT": -22.534,
            "OBSALT": 1864.0,
            "EQUINOX": 2000.0,
            "SIMPLE": True,
            "BITPIX": 16,
            "BZERO": 1,
            "BSCALE": 32768,
            "ACSVRSN": "v0.0.0",
            "INSTRUME": "ECHARPE",
            "FILENAME": "00000000_ECH_BLUE_000000o.fits",
        }
