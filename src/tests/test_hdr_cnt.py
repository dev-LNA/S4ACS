import unittest
from pathlib import Path

from python.header_content import Header_Content


class Test_Hdr_Cnt(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.csv_folder = Path.cwd() / "csv" / "tester"
        return super().setUpClass()

    def test_init(self) -> None:
        hdr_cnt = Header_Content(self.csv_folder)
        assert hdr_cnt.keywords == [
            "VSHIFT",
            "PRESSURE",
            "FRAMETRF",
            "GUIVRSN",
            "EMGAIN",
            "OBSERVER",
            "INSTMODE",
            "WPROMODE",
            "EXPTIME",
        ]
        assert hdr_cnt.comments == [
            "Vertical shift speed (ms)",
            "Barometric pressure (mb), weather tower",
            "Frame transfer on: T or F",
            "S4GUI software version",
            "Electron multiplier gain",
            "Observer(s)",
            "Instrument mode: PHOT or POLAR",
            "Waveplate rotator: real (T) or simulated (F)",
            "Exposure time (s)",
        ]
        assert hdr_cnt.keyword_types["FRAMETRF"] == "boolean"
        assert hdr_cnt.expected_kw_names["FRAMETRF"] == "FRAME"
        assert hdr_cnt.allowed_kw_values["FRAMETRF"] == [True, False]
        assert hdr_cnt.allowed_kw_values["EMGAIN"] == [2, 300]
        assert hdr_cnt.allowed_kw_values["EXPTIME"] == [1e-5, 86400]
        assert hdr_cnt.cards[0] == ("VSHIFT", "", "Vertical shift speed (ms)")
