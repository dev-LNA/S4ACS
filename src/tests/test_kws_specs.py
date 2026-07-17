import unittest
from pathlib import Path

from python.keywords_specs import Keywords_Specifications


class Test_Kws_Specs(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.csv_folder = Path.cwd() / "csv" / "sparc4"
        return super().setUpClass()

    def test_init(self) -> None:
        kws_specs = Keywords_Specifications(self.csv_folder, "TESTER")
        assert kws_specs.to_bool is None
        assert kws_specs.to_int is None
        assert kws_specs.to_float is None
        assert kws_specs.replace_comma is None
        assert kws_specs.any_val is None
        assert kws_specs.predefined_vals is None
        assert kws_specs.kws_in_dict is None
        assert kws_specs.empty_kws is None
        assert kws_specs.regex is None
        assert kws_specs.to_bool_w_cond is None
        assert kws_specs.csv_folder == self.csv_folder
        assert kws_specs.app_name == "TESTER"
        assert (
            kws_specs.kws_specs["Header Keywords"]
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

    def test_load_data(self) -> None:
        kws_specs = Keywords_Specifications(self.csv_folder, "TESTER")
        kws_specs.load_data()
        assert kws_specs.keywords == [
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
        assert kws_specs.to_bool == ["FRAMETRF"]
        assert kws_specs.to_int == ["EMGAIN"]
        assert kws_specs.to_float == ["EXPTIME", "PRESSURE"]
        assert kws_specs.any_val == ["OBSERVER"]
        assert kws_specs.kws_in_dict == ["VSHIFT"]
        assert kws_specs.dict_w_kws == {"VSHIFT": [0.6, 1.13, 2.2, 4.33]}
        assert kws_specs.predefined_vals == ["INSTMODE"]
        assert kws_specs.regex == ["GUIVRSN"]
        assert kws_specs.regex_expressions == {"GUIVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0")}
        assert kws_specs.to_bool_w_cond == {"WPROMODE": ["SIMULATED", "ACTIVE"]}
        assert kws_specs.replace_comma == ["PRESSURE"]
        assert kws_specs.empty_kws == ["BITPIX"]
        assert kws_specs.empty_kws_vals == {"BITPIX": 16}
