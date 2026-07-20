import json
import unittest
from pathlib import Path

from python.header import (
    GUI,
    ICS,
    General_ECHARPE_KWs,
    General_KWs,
    General_SPARC4_KWs,
    Header_Tester,
    Weather_Station,
)
from python.setup import Header_Class_Setup


class Test_Header(unittest.TestCase):
    def setUp(self) -> None:
        self._dict_data = {
            "FRAMETRF": 1,
            "EMGAIN": "2",
            "EXPTIME": "1",
            "OBSERVER": "Denis",
            "VSHIFT": 3,
            "INSTMODE": "PHOT",
            "GUIVRSN": "0.0.0",
            "WPROMODE": "ACTIVE",
            "PRESSURE": "10,1",
            "TEST0": True,
        }
        self._hdr_data = ("TESTER " + json.dumps(self._dict_data),)
        self.setup = Header_Class_Setup("tester")
        self.hdr, self.hdr_data, self.hdr_cnt, self.log_file, self.file_name = (
            self.setup.create_setup(self._hdr_data, "00000000_s4c1_000001.fits")
        )
        self.kws_specs = self.setup.create_hdr_specs(Header_Tester.name)
        self.tester = Header_Tester(
            self.kws_specs, self.hdr_cnt, self.log_file, self.file_name
        )
        # ================================================
        self.extracted_tester = Header_Tester(
            self.kws_specs, self.hdr_cnt, self.log_file, self.file_name
        )
        self.extracted_tester.write_header_all_apps(self.hdr_data)
        self.extracted_tester.get_app_header_data()
        self.extracted_tester.fix_original_string()
        self.extracted_tester.load_json()
        self.extracted_tester.fix_original_hdr_data()
        self.extracted_tester.extract_data()

    def test_init(self) -> None:
        assert self.tester.kws_specs == self.kws_specs
        assert self.tester.hdr_cnt == self.hdr_cnt
        assert self.tester.log_file == self.log_file
        assert self.tester.file_name == self.file_name
        assert self.tester.original_string is None
        assert self.tester.fixed_original_string is None
        assert self.tester.original_hdr_data is None
        assert self.tester.extracted_data == {}
        assert self.tester.fixed_data == {k: "" for k in self.kws_specs.keywords}
        assert self.tester.checked_data == {k: "" for k in self.kws_specs.keywords}

    # ===================== Convertions ======================

    def test_convert_to_float(self) -> None:
        self.extracted_tester._convert_to_float()
        assert self.extracted_tester.fixed_data["EXPTIME"] == 1.0

    def test_convert_to_int(self) -> None:
        self.extracted_tester._convert_to_int()
        assert self.extracted_tester.fixed_data["EMGAIN"] == 2

    def test_convert_to_boolean(self) -> None:
        self.extracted_tester._convert_to_boolean()
        assert self.extracted_tester.fixed_data["FRAMETRF"] is True

    def test_convert_to_boolean_w_condition(self) -> None:
        self.extracted_tester._convert_to_bool_with_condition()
        assert self.extracted_tester.fixed_data["WPROMODE"] is True

    def test_replace_comma(self) -> None:
        self.extracted_tester._replace_comma()
        assert self.extracted_tester.extracted_data["PRESSURE"] == "10.1"

    def test_verify_regex(self) -> None:
        self.extracted_tester._verify_regex()
        assert self.extracted_tester.fixed_data["GUIVRSN"] == "v0.0.0"

    def test_replace_empty_kws(self) -> None:
        self.extracted_tester._replace_empty_kws()
        assert self.extracted_tester.fixed_data["BITPIX"] == 16

    def test_write_any_value(self) -> None:
        self.extracted_tester._write_any_value()
        assert self.extracted_tester.fixed_data["OBSERVER"] == "Denis"

    def test_predefined_values(self) -> None:
        self.extracted_tester._write_predefined_value()
        assert self.extracted_tester.fixed_data["INSTMODE"] == "PHOT"

    def test_wrong_predefined_value(self) -> None:
        self.extracted_tester.extracted_data["INSTMODE"] = "PHOOT"
        self.extracted_tester._write_predefined_value()
        assert self.extracted_tester.fixed_data["INSTMODE"] == ""

    def test_kws_in_dict(self) -> None:
        self.extracted_tester._kw_in_dict()
        assert self.extracted_tester.fixed_data["VSHIFT"] == 4.33

    # ========================== Validation  =======================================

    # def test_check_str_in_allowed_values(self) -> None:
    #     self.fixed_tester._check_string_in_allowed_values("INSTMODE")
    #     assert self.fixed_tester.new_json["INSTMODE"] == "PHOT"

    # def test_check_str_not_in_allowed_values(self) -> None:
    #     tester_hdr_content = self.tester_hdr_content.copy()
    #     tester_hdr_content["INSTMODE"] = "AAA"
    #     dict_header_jsons = self.dict_header_jsons.copy()
    #     dict_header_jsons["TESTER"] = json.dumps(tester_hdr_content)
    #     tester = Header_Tester(
    #         dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
    #     )
    #     tester.extract_info()
    #     tester.fix_keywords()
    #     tester._check_string_in_allowed_values("INSTMODE")
    #     assert tester.new_json["INSTMODE"] == ""

    # def test_check_number_not_in_range(self) -> None:
    #     tester_hdr_content = self.tester_hdr_content.copy()
    #     tester_hdr_content["EMGAIN"] = 1
    #     dict_header_jsons = self.dict_header_jsons.copy()
    #     dict_header_jsons["TESTER"] = json.dumps(tester_hdr_content)
    #     tester = Header_Tester(
    #         dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
    #     )
    #     tester.extract_info()
    #     tester.fix_keywords()
    #     tester._check_number_in_range("EMGAIN")
    #     assert tester.new_json["EMGAIN"] == ""

    # def test_check_number_in_range(self) -> None:
    #     self.fixed_tester._check_number_in_range("EMGAIN")
    #     assert self.fixed_tester.new_json["EMGAIN"] == 2

    # def test_check_allowed_values(self) -> None:
    #     self.fixed_tester._check_allowed_values()

    # def test_check_type(self) -> None:
    #     self.fixed_tester._check_type()

    # def test_check_wrong_type(self) -> None:
    #     tester = tester = Header_Tester(
    #         self.dict_header_jsons.copy(),
    #         self.log_file,
    #         self.hdr_cnt,
    #         self.csv_folder,
    #     )
    #     tester.extract_info()
    #     tester.fix_keywords()
    #     tester.new_json["EMGAIN"] = "1"
    #     tester._check_type()
    #     assert tester.new_json["EMGAIN"] == ""

    # def test_validate_info(self) -> None:
    #     self.fixed_tester.validate_info()

    # def test_Weather_Station(self) -> None:
    #     dict_header_jsons = self.dict_header_jsons.copy()
    #     dict_header_jsons["WSTATION"] = json.dumps(self.tester_hdr_content)
    #     tester = Weather_Station(
    #         dict_header_jsons, self.log_file, self.hdr_cnt, self.csv_folder
    #     )
    #     tester.extract_info()
    #     tester.fix_keywords()
    #     assert tester.new_json["PRESSURE"] == 10.1

    # ==========================================================================

    def test_write_hdr_all_apps(self) -> None:
        self.tester.write_header_all_apps(self.hdr_data)
        assert self.tester.header_all_apps == self.hdr_data

    def test_get_app_header_data(self) -> None:
        self.tester.write_header_all_apps(self.hdr_data)
        self.tester.get_app_header_data()
        assert self.tester.original_string == self._hdr_data[0]

    def test_fix_original_string(self) -> None:
        self.tester.write_header_all_apps(self.hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        assert self.tester.fixed_original_string == json.dumps(self._dict_data)

    def test_load_json(self) -> None:
        self.tester.write_header_all_apps(self.hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        assert self.tester.original_hdr_data == self._dict_data

    def test_fix_original_hdr_data(self) -> None:
        self.tester.write_header_all_apps(self.hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        assert self.tester.fixed_original_hdr_data["TEST1"] is True
        assert self.tester.fixed_original_hdr_data["FRAMETRF"] == 1

    def test_extract_data(self) -> None:
        self.tester.write_header_all_apps(self.hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        del self._dict_data["TEST0"]
        assert self.tester.extracted_data == self._dict_data

    def test_fix_keywords(self) -> None:
        self.tester.write_header_all_apps(self.hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        self.tester.fix_keywords()
        assert self.tester.fixed_data["FRAMETRF"] is True
        assert self.tester.fixed_data["EMGAIN"] == 2
        assert self.tester.fixed_data["EXPTIME"] == 1.0
        assert self.tester.fixed_data["OBSERVER"] == "Denis"
        assert self.tester.fixed_data["VSHIFT"] == 4.33
        assert self.tester.fixed_data["INSTMODE"] == "PHOT"
        assert self.tester.fixed_data["GUIVRSN"] == "v0.0.0"
        assert self.tester.fixed_data["WPROMODE"] is True
        assert self.tester.fixed_data["PRESSURE"] == 10.1
