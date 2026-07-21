import json
import unittest

from python.header import ICS, S4ICS
from python.setup import Header_Class_Setup
from python.utils import ics_kw


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


#     @classmethod
#     def setUpClass(cls):
#         cls.csv_folder = join(dirname(realpath(__file__)), "..", "csvs", "sparc4")
#         cls.hdr_params = Header_Parameters(cls.csv_folder)

#         cls.dict_header_jsons["ICS"] = json.dumps(cls.tester_hdr_content)
#         cls.tester = S4ICS(
#             cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
#         )
#         cls.fixed_tester = S4ICS(
#             cls.dict_header_jsons, cls.log_file, cls.hdr_params, cls.csv_folder
#         )
#         cls.fixed_tester.extract_info()
#         # cls.fixed_tester.fix_keywords()

#     def test_S4ICS(self):
#         assert self.tester.dict_w_kws == {
#             "WPSEL": {"OFF": "None", "L/2": "L2", "L/4": "L4"},
#             "CALW": {
#                 "POLARIZER": "POLARIZER",
#                 "DEPOLARIZER": "DEPOLARIZER",
#                 "CLEAR": "CLEAR",
#                 "OFF": "CLEAR",
#                 "PINHOLE": "SPARE",
#                 "SPARE": "SPARE",
#                 "SHUTTER": "CLOSED",
#                 "CLOSED": "CLOSED",
#             },
#         }

#     def test_treat_s4ics_json(self):
#         mechanisms = self.tester._treat_s4ics_json()
#         status_list = [
#             mechanism["status"] for mechanism in self.tester_hdr_content["mechanisms"]
#         ]
#         for mechanism, status in mechanisms.items():
#             assert mechanism in ["GMIR", "GFOC", "ASEL", "CALW", "WPSEL", "WPROT"]
#             assert status in status_list

#     def test_write_s4ics_kws_into_json(self):
#         mechanisms = self.tester._treat_s4ics_json()
#         components_list = [
#             "WPROMODE",
#             "WPSEMODE",
#             "CALWMODE",
#             "ANMODE",
#             "GMIRMODE",
#             "GFOCMODE",
#         ]
#         s4ics_correspondents = ["WPROT", "WPSEL", "CALW", "ASEL", "GMIR", "GFOC"]
#         self.tester._write_s4ics_kws_into_json(
#             mechanisms, components_list, s4ics_correspondents, "mode"
#         )
#         for comp, mechanism in zip(components_list, mechanisms.keys()):
#             assert self.tester.original_json[comp] == mechanisms[mechanism]["mode"]

#     def test_write_WPPOS(self):
#         self.tester._write_WPPOS("3")
#         assert self.tester.original_json["WPPOS"] == 3

#     def test_create_s4ics_kws(self):
#         for component in [
#             "WPROMODE",
#             "WPSEMODE",
#             "CALWMODE",
#             "ANMODE",
#             "GMIRMODE",
#             "GFOCMODE",
#         ]:
#             assert self.fixed_tester.original_json[component] == "ACTIVE"

#         position_list = ["0.000", "80.000", "216.000", "0.000", "0.000", "8.0"]
#         comp_list = ["WPANG", "WPSELPO", "CALWANG", "ANALANG", "GMIR", "GFOC"]
#         for component, position in zip(comp_list, position_list):
#             assert self.fixed_tester.original_json[component] == position

#         pos_name_list = ["OFF", "CLOSED", "OFF"]
#         comp_list = ["WPSEL", "CALW", "ASEL"]
#         for component, pos_name in zip(comp_list, pos_name_list):
#             assert self.fixed_tester.original_json[component] == pos_name
