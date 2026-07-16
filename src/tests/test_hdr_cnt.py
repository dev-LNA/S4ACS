import unittest
from pathlib import Path

import numpy as np

from python.header_content import Header_Content


class Test_Hdr_Cnt(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.csv_folder = Path.cwd() / "csv" / "tester"
        return super().setUpClass()

    def test_init(self) -> None:
        hdr_cnt = Header_Content(self.csv_folder)
        assert hdr_cnt.keywords == ["SIMPLE", "SIMPLE1", "SIMPLE2", "SIMPLE3"]
        assert hdr_cnt.comments == ["conforms to FITS standard"] * 4
        assert hdr_cnt.keyword_types["SIMPLE"] == "boolean"
        assert hdr_cnt.expected_kw_names["SIMPLE"] == "NAME"
        assert hdr_cnt.allowed_kw_values["SIMPLE"] == [True, False]
        assert hdr_cnt.allowed_kw_values["SIMPLE1"] == [0, 100]
        assert hdr_cnt.allowed_kw_values["SIMPLE2"] == [-1, 1]
        assert hdr_cnt.allowed_kw_values["SIMPLE3"] == [1, np.inf]
        assert hdr_cnt.cards[0] == ("SIMPLE", "", "conforms to FITS standard")
