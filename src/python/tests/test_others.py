import json
import unittest

from header_formatter.header import TCS, Focuser, Weather_Station
from header_formatter.setup import Header_Class_Setup


class Test_TCS(unittest.TestCase):
    def setUp(self) -> None:
        self._dict_data = {
            "RAACQUIS": "00:00",
            "DECACQUIS": "00",
            "HOURANGLE": "00:00:00",
            "GUIDEANG": 0,
            "AIRMASS": 1,
            "DATE": "27/02/24",
            "TIME": "10:14:59",
        }

        self._hdr_data = (
            (json.dumps({"OBSTYPE": "ZERO"}),)
            + ("{}",) * 2
            + (json.dumps(self._dict_data),)
            + ("{}",) * 3
        )
        self.setup = Header_Class_Setup("sparc4")
        _, hdr_data, hdr_cnt, log_file, file_name = self.setup.create_setup(
            self._hdr_data, "00000000_s4c1_000001.fits"
        )
        kws_specs = self.setup.create_hdr_specs(TCS.name)
        self.tester = TCS(kws_specs, hdr_cnt, log_file, file_name)
        self.tester.write_header_all_apps(hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        self.tester.fix_keywords()

    def test_obstype(self) -> None:
        assert self.tester.obstype == "ZERO"

    def test_write_tcsdate(self) -> None:
        assert self.tester.fixed_data["TCSDATE"] == "2024-02-27T10:14:59.000"

    def test_RA_DEC_TCSHA(self) -> None:
        assert self.tester.fixed_data["RA"] == "00:00:00.00"
        assert self.tester.fixed_data["DEC"] == "00:00:00.00"
        assert self.tester.fixed_data["TCSHA"] == "00:00:00.00"


class Test_WStation(unittest.TestCase):
    def setUp(self) -> None:

        self._hdr_data = ("{}",) * 5 + ("Weather " + json.dumps({}),) + ("{}",)
        self.setup = Header_Class_Setup("sparc4")
        _, hdr_data, hdr_cnt, log_file, file_name = self.setup.create_setup(
            self._hdr_data, "00000000_s4c1_000001.fits"
        )
        kws_specs = self.setup.create_hdr_specs(Weather_Station.name)
        self.tester = Weather_Station(kws_specs, hdr_cnt, log_file, file_name)
        self.tester.write_header_all_apps(hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()

    def test_fix_original_string(self) -> None:
        if self.tester.original_string is not None:
            assert "Weather" not in self.tester.original_string


class Test_Focuser(unittest.TestCase):
    def setUp(self) -> None:

        self._hdr_data = (
            ("{}",) * 4
            + (json.dumps({"INITIALIZED": True, "ISMOVING": True}),)
            + ("{}",) * 2
        )
        self.setup = Header_Class_Setup("sparc4")
        _, hdr_data, hdr_cnt, log_file, file_name = self.setup.create_setup(
            self._hdr_data, "00000000_s4c1_000001.fits"
        )
        kws_specs = self.setup.create_hdr_specs(Focuser.name)
        self.tester = Focuser(kws_specs, hdr_cnt, log_file, file_name)
        self.tester.write_header_all_apps(hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        self.tester.fix_keywords()

    def test_fix_keywords(self) -> None:
        assert self.tester.fixed_data["TFOCSTAT"] == "BUSY"
