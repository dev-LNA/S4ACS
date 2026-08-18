import json
import unittest

from header_formatter.header import (
    General_KWs,
    General_SPARC4_KWs,
)
from header_formatter.setup import Header_Class_Setup
from header_formatter.utils import general_kw


class Test_General_Kws(unittest.TestCase):
    def setUp(self) -> None:
        self._general_kw = {k.upper(): v for (k, v) in general_kw.items()}
        self._hdr_data = dict.fromkeys(
            ["CCD", "GUI", "ICS", "FOCUSER", "WSTATION", "GENERAL KW", "TCS"], "{}"
        )
        self._hdr_data["GENERAL KW"] = json.dumps(general_kw)
        setup = Header_Class_Setup("sparc4")
        self.hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
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
        self.tester.fix_remainder_keywords()
        self.tester.check_kws_types()
        self.tester.check_allowed_values()
        self.hdr = self.tester.fill_image_header(self.hdr)

    def test_fixed_keywords(self) -> None:
        assert self.tester.fixed_data["CYCLIND"] == 1


class Test_General_SPARC4_Kws(unittest.TestCase):
    def setUp(self) -> None:
        self._general_kw = {k.upper(): v for (k, v) in general_kw.items()}
        self._hdr_data = dict.fromkeys(
            ["CCD", "GUI", "ICS", "FOCUSER", "WSTATION", "GENERAL KW", "TCS"], "{}"
        )
        self._hdr_data["GENERAL KW"] = json.dumps(general_kw)
        setup = Header_Class_Setup("sparc4")
        self.hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
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
        self.tester.fix_remainder_keywords()
        self.tester.check_kws_types()
        self.tester.check_allowed_values()
        self.hdr = self.tester.fill_image_header(self.hdr)

    def test_fixed_keywords(self) -> None:
        assert self.tester.fixed_data["CYCLIND"] == 1
        assert self.tester.fixed_data["SEQINDEX"] == 1

    def test_num_kws_predefined_vals(self) -> None:
        assert "BITPIX" in self.tester.num_kws_predefined_vals
