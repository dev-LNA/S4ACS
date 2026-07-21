import json
import unittest

from header_formatter.header import S4ICS
from header_formatter.setup import Header_Class_Setup
from header_formatter.utils import ics_kw


class Test_S4ICS(unittest.TestCase):
    def setUp(self) -> None:
        self._hdr_data = (
            (json.dumps({"INSTMODE": "POLAR"}),)
            + ("{}",)
            + (json.dumps(ics_kw),)
            + ("{}",) * 4
        )
        setup = Header_Class_Setup("sparc4")
        hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
            self._hdr_data, "00000000_s4c1_000001.fits"
        )
        kws_specs = setup.create_hdr_specs(S4ICS.name)
        self.tester = S4ICS(kws_specs, hdr_cnt, log_file, file_name)
        self.tester.write_header_all_apps(hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        self.tester.fix_keywords()

    def test_init(self) -> None:
        assert self.tester.how_to_fix_regex == {"ICSVRSN": self.tester._fix_ICSVRSN}

    def test_ICS(self) -> None:
        assert self.tester.fixed_data["ICSVRSN"] == "v0.0.0"

    def test_inst_mode(self) -> None:
        assert self.tester.inst_mode == "POLAR"

    def test_treat_ics_json(self) -> None:
        self.tester.original_hdr_data = {
            "MECHANISMS": [
                {"status": {"pos_id": 1}, "name": "WPROT"}  # type: ignore
            ]
        }
        assert self.tester._treat_s4ics_json() == {"WPROT": {"pos_id": 1}}

    def test_write_s4ics_kws_into_json(self) -> None:
        mechanisms = self.tester._treat_s4ics_json()
        components_list = ["WPROMODE"]
        s4ics_correspondents = ["WPROT"]
        self.tester._write_s4ics_kws_into_json(
            mechanisms, components_list, s4ics_correspondents, "mode"
        )
        assert (
            self.tester.fixed_original_hdr_data["WPROMODE"]
            == mechanisms["WPROT"]["mode"]
        )

    def test_fix_WPPOS(self) -> None:
        mechanism = ics_kw["mechanisms"][0]
        if isinstance(mechanism, dict):
            status = mechanism["status"]
            if isinstance(status, dict):
                self.tester._write_WPPOS(status["pos_id"])
                assert self.tester.fixed_original_hdr_data["WPPOS"] == 1
