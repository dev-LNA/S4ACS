import json
import unittest
from pathlib import Path

from header_formatter.header import (
    General_KWs,
    General_SPARC4_KWs,
)
from header_formatter.setup import Header_Class_Setup


class Test_General_Kws(unittest.TestCase):
    def setUp(self) -> None:
        self._dict_data = {
            "FILENAME": "",
            "NCYCLES": 1,
            "CYCLIND": 0,
            "ACSVRSN": "v0.0.0",
            "ACSMODE": True,
            "SDKVRSN": "0.000.00000.0",
            "CHANNEL": 1,
            "ACQERROR": False,
            "SEQINDEX": 1,
            "NSEQ": 1,
        }
        self._hdr_data = dict.fromkeys(
            ["CCD", "GUI", "ICS", "FOCUSER", "WSTATION", "GENERAL KW", "TCS"], "{}"
        )
        self._hdr_data["GENERAL KW"] = json.dumps(self._dict_data)
        setup = Header_Class_Setup("sparc4")
        hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
            json.dumps(self._hdr_data), "00000000_s4c1_000001.fits"
        )
        kws_specs = setup.create_hdr_specs(General_KWs.name)
        self.tester = General_KWs(kws_specs, hdr_cnt, log_file, file_name)
        self.tester.write_header_all_apps(hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        self.tester.fix_keywords()

    def test_fixed_keywords(self) -> None:
        self._dict_data["CYCLIND"] = 1
        assert self.tester.fixed_data == self._dict_data


class Test_General_SPARC4_Kws(unittest.TestCase):
    def setUp(self) -> None:
        self._dict_data = {
            "FILENAME": "",
            "NCYCLES": 1,
            "CYCLIND": 0,
            "ACSVRSN": "v0.0.0",
            "ACSMODE": True,
            "SDKVRSN": "0.000.00000.0",
            "CHANNEL": 1,
            "ACQERROR": False,
            "SEQINDEX": 0,
            "NSEQ": 1,
        }
        self._hdr_data = dict.fromkeys(
            ["CCD", "GUI", "ICS", "FOCUSER", "WSTATION", "GENERAL KW", "TCS"], "{}"
        )
        self._hdr_data["GENERAL KW"] = json.dumps(self._dict_data)
        setup = Header_Class_Setup("sparc4")
        hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
            json.dumps(self._hdr_data), "00000000_s4c1_000001.fits"
        )
        kws_specs = setup.create_hdr_specs(General_KWs.name)
        self.tester = General_SPARC4_KWs(kws_specs, hdr_cnt, log_file, file_name)
        self.tester.write_header_all_apps(hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        self.tester.fix_keywords()

    def test_fixed_keywords(self) -> None:
        self._dict_data["CYCLIND"] = 1
        self._dict_data["SEQINDEX"] = 1
        assert self.tester.fixed_data == self._dict_data
