import json
import unittest
from os.path import dirname, join, realpath

from header import ICS, S4ICS, Header_Parameters


class Test_ICS(unittest.TestCase):

    dict_header_jsons: dict = {
        "CCD": '{"FILENAME":"s4acs1_000001.fits"}',
    }
    log_file = join("tests", "files", "log.log")
    tester_hdr_content = {"VERSION": "0.0.0"}

    @classmethod
    def setUpClass(cls):
        cls.csv_folder = join(dirname(realpath(__file__)), "..", "csvs", "sparc4")
        cls.hdr_params = Header_Parameters(cls.csv_folder)

        cls.dict_header_jsons["ICS"] = json.dumps(cls.tester_hdr_content)
        cls.tester = ICS(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.tester.extract_info()
        cls.fixed_tester = ICS(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.fixed_tester.extract_info()
        cls.fixed_tester.fix_keywords()

    def test_ICS(self):
        assert self.fixed_tester.new_json["ICSVRSN"] == "v0.0.0"


class Test_S4ICS(unittest.TestCase):

    dict_header_jsons: dict = {
        "CCD": '{"FILENAME":"s4acs1_000001.fits"}',
        "GUI": '{"INSTMODE":"POLAR"}',
    }
    log_file = join("tests", "files", "log.log")
    tester_hdr_content = {
        "VERSION": "0.0.0",
        "mechanisms": [
            {
                "name": "WPROT",
                "status": {
                    "mode": "ACTIVE",
                    "condition": "READY",
                    "position": "0.000",
                    "pos_name": "NONE",
                    "pos_id": "3",
                },
            },
            {
                "name": "WPSEL",
                "status": {
                    "mode": "ACTIVE",
                    "condition": "READY",
                    "position": "80.000",
                    "pos_name": "OFF",
                    "pos_id": "2",
                },
            },
            {
                "name": "CALW",
                "status": {
                    "mode": "ACTIVE",
                    "condition": "READY",
                    "position": "216.000",
                    "pos_name": "CLOSED",
                    "pos_id": "4",
                },
            },
            {
                "name": "ASEL",
                "status": {
                    "mode": "ACTIVE",
                    "condition": "READY",
                    "position": "0.000",
                    "pos_name": "OFF",
                    "pos_id": "1",
                },
            },
            {
                "name": "GMIR",
                "status": {
                    "mode": "ACTIVE",
                    "condition": "READY",
                    "position": "0.000",
                    "pos_name": "TARGET",
                    "pos_id": "1",
                },
            },
            {
                "name": "GFOC",
                "status": {
                    "mode": "ACTIVE",
                    "condition": "READY",
                    "position": "8.0",
                    "pos_name": "TARGET",
                    "pos_id": "-1",
                },
            },
        ],
    }

    @classmethod
    def setUpClass(cls):
        cls.csv_folder = join(dirname(realpath(__file__)), "..", "csvs", "sparc4")
        cls.hdr_params = Header_Parameters(cls.csv_folder)

        cls.dict_header_jsons["ICS"] = json.dumps(cls.tester_hdr_content)
        cls.tester = S4ICS(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.fixed_tester = S4ICS(
            cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
        )
        cls.fixed_tester.extract_info()
        # cls.fixed_tester.fix_keywords()

    def test_S4ICS(self):
        assert self.tester.dict_w_kws == {
            "WPSEL": {"OFF": "None", "L/2": "L2", "L/4": "L4"},
            "CALW": {
                "POLARIZER": "POLARIZER",
                "DEPOLARIZER": "DEPOLARIZER",
                "CLEAR": "CLEAR",
                "OFF": "CLEAR",
                "PINHOLE": "SPARE",
                "SPARE": "SPARE",
                "SHUTTER": "CLOSED",
                "CLOSED": "CLOSED",
            },
        }

    def test_treat_s4ics_json(self):
        mechanisms = self.tester._treat_s4ics_json()
        status_list = [
            mechanism["status"] for mechanism in self.tester_hdr_content["mechanisms"]
        ]
        for mechanism, status in mechanisms.items():
            assert mechanism in ["GMIR", "GFOC", "ASEL", "CALW", "WPSEL", "WPROT"]
            assert status in status_list

    def test_write_s4ics_kws_into_json(self):
        mechanisms = self.tester._treat_s4ics_json()
        components_list = [
            "WPROMODE",
            "WPSEMODE",
            "CALWMODE",
            "ANMODE",
            "GMIRMODE",
            "GFOCMODE",
        ]
        s4ics_correspondents = ["WPROT", "WPSEL", "CALW", "ASEL", "GMIR", "GFOC"]
        self.tester._write_s4ics_kws_into_json(
            mechanisms, components_list, s4ics_correspondents, "mode"
        )
        for comp, mechanism in zip(components_list, mechanisms.keys()):
            assert self.tester.original_json[comp] == mechanisms[mechanism]["mode"]

    def test_write_WPPOS(self):
        self.tester._write_WPPOS("3")
        assert self.tester.original_json["WPPOS"] == 3

    def test_create_s4ics_kws(self):
        for component in [
            "WPROMODE",
            "WPSEMODE",
            "CALWMODE",
            "ANMODE",
            "GMIRMODE",
            "GFOCMODE",
        ]:
            assert self.fixed_tester.original_json[component] == "ACTIVE"

        position_list = ["0.000", "80.000", "216.000", "0.000", "0.000", "8.0"]
        comp_list = ["WPANG", "WPSELPO", "CALWANG", "ANALANG", "GMIR", "GFOC"]
        for component, position in zip(comp_list, position_list):
            assert self.fixed_tester.original_json[component] == position

        pos_name_list = ["OFF", "CLOSED", "OFF"]
        comp_list = ["WPSEL", "CALW", "ASEL"]
        for component, pos_name in zip(comp_list, pos_name_list):
            assert self.fixed_tester.original_json[component] == pos_name
