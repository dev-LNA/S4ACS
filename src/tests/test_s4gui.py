import json
import unittest
from pathlib import Path

from python.header import GUI
from python.setup import Header_Class_Setup


class Test_S4GUI(unittest.TestCase):
    def setUp(self) -> None:
        self._dict_data = {
            "CHANNEL1": 1,
            "CHANNEL2": 1,
            "CHANNEL3": 1,
            "CHANNEL4": 1,
            "OBJECT": 1,
            "OBSERVER": 1,
            "PROPID": 1,
            "TCSMODE": 1,
            "FILTER": 1,
            "GUIVRSN": "0.0.0",
            "CTRLINTE": 1,
            "SYNCMODE": 1,
            "INSTMODE": 1,
            "OBSTYPE": 1,
            "COMMENT": "It is a comment",
        }
        self._hdr_data = (json.dumps(self._dict_data),) + ("{}",) * 6
        setup = Header_Class_Setup("sparc4")
        _, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
            self._hdr_data, "00000000_s4c1_000001.fits"
        )
        kws_specs = setup.create_hdr_specs(GUI.name)
        self.tester = GUI(kws_specs, hdr_cnt, log_file, file_name)
        self.tester.write_header_all_apps(hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        self.tester.fix_keywords()

    def test_COMMENT(self) -> None:
        assert self.tester.fixed_data["COMMENT"] == "It is a comment"
