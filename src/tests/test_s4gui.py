import json
import unittest
from os.path import dirname, join, realpath

from python.header import GUI


class Test_S4GUI(unittest.TestCase):
    dict_header_jsons: dict = {"CCD": '{"FILENAME":"s4acs1_000001.fits"}'}
    log_file = join("tests", "files", "log.log")
    tester_hdr_content = {"GUIVRSN": "v0.0.0", "COMMENT": "It is a comment"}

    @classmethod
    def setUpClass(cls):
        cls.csv_folder = join(dirname(realpath(__file__)), "..", "csvs", "sparc4")
        cls.hdr_params = Header_Parameters(cls.csv_folder)

        cls.dict_header_jsons["GUI"] = json.dumps(cls.tester_hdr_content)
        cls.tester = S4GUI(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.tester.extract_info()
        cls.fixed_tester = S4GUI(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.fixed_tester.extract_info()
        cls.fixed_tester.fix_keywords()

    def test_GUIVSRN(self):
        assert self.tester.new_json["GUIVRSN"] == "v0.0.0"

    def test_COMMENT(self):
        assert self.fixed_tester.new_json["COMMENT"] == "It is a comment"
