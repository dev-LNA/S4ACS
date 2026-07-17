import json
import unittest
from pathlib import Path

import astropy.io.fits as fits
import numpy as np
import pandas as pd

from python.header import (
    GUI,
    ICS,
    General_ECHARPE_KWs,
    General_KWs,
    General_SPARC4_KWs,
    Header_Tester,
    Weather_Station,
)
from python.header_content import Header_Content
from python.setup import Header_Class_Setup


class Test_Header(unittest.TestCase):
    dict_header_jsons: dict = {"TESTER": "", "CCD": '{"FILENAME":"s4acs1_000001.fits"}'}
    # log_file = join("tests", "files", "log.log")
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
    }

    @classmethod
    def setUpClass(cls) -> None:
        setup = Header_Class_Setup("tester")
        setup.create_setup()
        cls.fixed_tester = setup.header_classes_list[0]
        cls.fixed_tester.write_header_all_apps(setup.hdr_data)
        cls.fixed_tester.get_app_header_data()
        cls.fixed_tester.fix_header_data()
        cls.fixed_tester.load_json()
        cls.fixed_tester.extract_data()
        cls.fixed_tester.fix_keywords()
        cls.fixed_tester.validate_info()
        cls.fixed_tester.fill_image_header(setup.hdr)

    def test_init_header_empty_json(self) -> None:
        dict_header_jsons = {"TESTER": "", "CCD": '{"FILENAME":"s4acs1_000001.fits"}'}
        tester = Header_Tester(
            dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
        )
        assert tester.original_hdr_data is None

    def test_init_header_json(self) -> None:
        tester = Header_Tester(
            self.dict_header_jsons.copy(),
            self.log_file,
            self.hdr_cnt,
            self.csv_folder,
        )
        assert (
            tester.header_keywords
            == [
                "FRAMETRF",
                "EMGAIN",
                "EXPTIME",
                "OBSERVER",
                "VSHIFT",
                "INSTMODE",
                "GUIVRSN",
                "WPROMODE",
                "PRESSURE",
            ]
        ).all()

        assert tester.to_bool_kws == ["FRAMETRF"]
        assert tester.to_int_kws == ["EMGAIN"]
        assert tester.to_float_kws == ["EXPTIME", "PRESSURE"]
        assert tester.replace_comma_kws == ["PRESSURE"]
        assert tester.write_any_val == ["OBSERVER"]
        assert tester.write_predefined_val == ["INSTMODE"]
        assert tester.kws_in_dict == ["VSHIFT"]
        assert tester.regex_strings == ["GUIVRSN"]
        assert tester.to_bool_w_cond_kws == {"WPROMODE": ["SIMULATED", "ACTIVE"]}

    def test_extract_info(self) -> None:
        self.tester = Header_Tester(
            self.dict_header_jsons.copy(),
            self.log_file,
            self.hdr_cnt,
            self.csv_folder,
        )
        self.tester.extract_info()
        assert self.tester.new_json == self.tester_hdr_content

    def test_convert_to_float(self) -> None:
        self.tester._replace_comma()
        self.tester._convert_to_float()
        assert self.tester.new_json["EXPTIME"] == 1.1

    def test_convert_to_int(self) -> None:
        self.tester._convert_to_int()
        assert self.tester.new_json["EMGAIN"] == 2

    def test_convert_to_boolean(self) -> None:
        self.tester._convert_to_boolean()
        assert self.tester.new_json["FRAMETRF"] == True

    def test_convert_to_boolean_w_condition(self) -> None:
        self.tester._convert_to_bool_with_condition()
        assert self.tester.new_json["WPROMODE"] == True

    def test_replace_comma(self) -> None:
        tester_hdr_content = self.tester_hdr_content.copy()
        tester_hdr_content["PRESSURE"] = "10,1"
        dict_header_jsons = self.dict_header_jsons.copy()
        dict_header_jsons["TESTER"] = json.dumps(tester_hdr_content)
        tester = Header_Tester(
            dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
        )
        tester.extract_info()
        tester._replace_comma()
        assert tester.new_json["PRESSURE"] == "10.1"

    def test_search_unwanted_kw(self) -> None:
        tester_hdr_content = self.tester_hdr_content.copy()
        tester_hdr_content["PRESSURE"] = "10,1"
        dict_header_jsons = self.dict_header_jsons.copy()
        dict_header_jsons["TESTER"] = json.dumps(tester_hdr_content)
        tester = Header_Tester(
            dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
        )
        tester.extract_info()
        tester._search_unwanted_kw("PRESSURE", ",")

    def test_verify_regex(self) -> None:
        self.tester._verify_regex()
        assert self.tester.new_json["GUIVRSN"] == "v0.0.0"

    def test_verify_broken_regex(self) -> None:
        tester_hdr_content = self.tester_hdr_content.copy()
        tester_hdr_content["GUIVRSN"] = "0.0.0"
        dict_header_jsons = self.dict_header_jsons.copy()
        dict_header_jsons["TESTER"] = json.dumps(tester_hdr_content)
        tester = Header_Tester(
            dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
        )
        tester.extract_info()
        tester._verify_regex()
        assert tester.new_json["GUIVRSN"] == "v0.0.0"

    def test_replace_empty_kws(self) -> None:
        self.tester._replace_empty_kws()
        self.tester.new_json["BITPIX"] == 16

    def test_write_any_value(self) -> None:
        self.tester._write_any_value()
        self.tester.new_json["OBSERVER"] == "DENIS"

    def test_predefined_values(self) -> None:
        self.tester._write_predefined_value()
        self.tester.new_json["INSTMODE"] == "PHOT"

    def test_kws_in_dict(self) -> None:
        self.tester._kw_in_dict()
        self.tester.new_json["VSHIFT"] == 4.33

    def test_predefined_values(self) -> None:
        self.tester._write_predefined_value()
        self.tester.new_json["INSTMODE"] == "PHOT"

    # -------------------------------------------------------------------------------------

    def test_check_str_in_allowed_values(self) -> None:
        self.fixed_tester._check_string_in_allowed_values("INSTMODE")
        assert self.fixed_tester.new_json["INSTMODE"] == "PHOT"

    def test_check_str_not_in_allowed_values(self) -> None:
        tester_hdr_content = self.tester_hdr_content.copy()
        tester_hdr_content["INSTMODE"] = "AAA"
        dict_header_jsons = self.dict_header_jsons.copy()
        dict_header_jsons["TESTER"] = json.dumps(tester_hdr_content)
        tester = Header_Tester(
            dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
        )
        tester.extract_info()
        tester.fix_keywords()
        tester._check_string_in_allowed_values("INSTMODE")
        assert tester.new_json["INSTMODE"] == ""

    def test_check_number_not_in_range(self) -> None:
        tester_hdr_content = self.tester_hdr_content.copy()
        tester_hdr_content["EMGAIN"] = 1
        dict_header_jsons = self.dict_header_jsons.copy()
        dict_header_jsons["TESTER"] = json.dumps(tester_hdr_content)
        tester = Header_Tester(
            dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
        )
        tester.extract_info()
        tester.fix_keywords()
        tester._check_number_in_range("EMGAIN")
        assert tester.new_json["EMGAIN"] == ""

    def test_check_number_in_range(self) -> None:
        self.fixed_tester._check_number_in_range("EMGAIN")
        assert self.fixed_tester.new_json["EMGAIN"] == 2

    def test_check_allowed_values(self) -> None:
        self.fixed_tester._check_allowed_values()

    def test_check_type(self) -> None:
        self.fixed_tester._check_type()

    def test_check_wrong_type(self) -> None:
        tester = tester = Header_Tester(
            self.dict_header_jsons.copy(),
            self.log_file,
            self.hdr_cnt,
            self.csv_folder,
        )
        tester.extract_info()
        tester.fix_keywords()
        tester.new_json["EMGAIN"] = "1"
        tester._check_type()
        assert tester.new_json["EMGAIN"] == ""

    def test_validate_info(self) -> None:
        self.fixed_tester.validate_info()

    def test_Weather_Station(self) -> None:
        dict_header_jsons = self.dict_header_jsons.copy()
        dict_header_jsons["WSTATION"] = json.dumps(self.tester_hdr_content)
        tester = Weather_Station(
            dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
        )
        tester.extract_info()
        tester.fix_keywords()
        assert tester.new_json["PRESSURE"] == 10.1
