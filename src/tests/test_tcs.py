import json
import unittest
from os.path import dirname, join, realpath

from python.header import TCS


class Test_TCS(unittest.TestCase):
    dict_header_jsons: dict = {
        "CCD": '{"FILENAME":"s4acs1_000001.fits"}',
        "GUI": '{"OBSTYPE":"ZERO"}',
    }
    log_file = join("tests", "files", "log.log")
    tester_hdr_content = {
        "DATE": "27/02/24",
        "TIME": "10:14:59",
        "RAACQUIS": "",
        "DECACQUIS": "",
        "AIRMASS": 1.0,
        "HOURANGLE": "00",
        "GUIDEANG": 0,
    }

    @classmethod
    def setUpClass(cls):
        cls.csv_folder = join(dirname(realpath(__file__)), "..", "csvs", "sparc4")
        cls.hdr_params = Header_Parameters(cls.csv_folder)

        cls.dict_header_jsons["TCS"] = json.dumps(cls.tester_hdr_content)
        cls.tester = TCS(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.tester.extract_info()
        cls.fixed_tester = TCS(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.fixed_tester.extract_info()
        cls.fixed_tester.fix_keywords()

    def test_TCS(self):
        assert self.tester.obstype == "ZERO"

    def test_write_tcsdate(self):
        assert self.fixed_tester.new_json["TCSDATE"] == "2024-02-27T10:14:59.000"

    def test_RA_DEC_TCSHA(self):
        assert self.fixed_tester.new_json["RA"] == "00:00:00.00"
        assert self.fixed_tester.new_json["DEC"] == "00:00:00.00"
        assert self.fixed_tester.new_json["TCSHA"] == "00:00:00.00"
