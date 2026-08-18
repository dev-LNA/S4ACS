from pathlib import Path

import pandas as pd
from header_formatter.header_content import Header_Content
from header_formatter.keywords_specs import Keywords_Specifications

from .header import Header


class CCD(Header):
    name = "CCD"

    def __init__(
        self,
        kws_specs: Keywords_Specifications,
        hdr_cnt: Header_Content,
        log_file: Path,
        file_name: Path,
    ) -> None:
        super().__init__(kws_specs, hdr_cnt, log_file, file_name)
        self.gain_values = pd.read_csv(
            kws_specs.csv_folder / "camera" / "preamp_gains.csv"
        )
        self.rd_values = pd.read_csv(
            kws_specs.csv_folder / "camera" / "read_noises.csv"
        )

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._fix_EXPTIME()
        self.fixed_data["FRAMEIND"] += 1

    def fix_remainder_keywords(self) -> None:
        self._find_index_tab()
        self._write_ccd_gain()
        self._write_read_noise()
        self.calc_NAXIS1()
        self.calc_NAXIS2()
        return super().fix_remainder_keywords()

    def _write_read_noise(self) -> None:
        try:
            val = self.rd_values[f"{self.fixed_data['CCDSERN']}"][self.idx_tab]
            self.fixed_data["RDNOISE"] = float(val)
        except Exception as e:
            self._write_log_file(repr(e), "RDNOISE")

    def _write_ccd_gain(self) -> None:
        try:
            val = self.gain_values[f"{self.fixed_data['CCDSERN']}"][self.idx_tab]
            self.fixed_data["GAIN"] = float(val)
        except Exception as e:
            self._write_log_file(repr(e), "GAIN")

    def _find_index_tab(self) -> None:
        _json = self.extracted_data
        self.idx_tab = 2 * _json["READRATE"] + _json["PREAMP"]

    def _fix_EXPTIME(self) -> None:
        if 1e-5 > self.fixed_data["EXPTIME"] > 9.999999e-6:
            self.fixed_data["EXPTIME"] = 1e-5

    def calc_NAXIS1(self) -> None:
        self.fixed_data["NAXIS1"] = (
            self.fixed_data["FINALLIN"] - self.fixed_data["INITLIN"]
        ) // self.fixed_data["VBIN"] + 1

    def calc_NAXIS2(self) -> None:
        self.fixed_data["NAXIS2"] = (
            self.fixed_data["FINALCOL"] - self.fixed_data["INITCOL"]
        ) // self.fixed_data["HBIN"] + 1


class iXon_Ultra(CCD):
    def _find_index_tab(self) -> None:
        _json = self.extracted_data
        self.idx_tab = 8 * _json["EMMODE"] + 2 * _json["READRATE"] + _json["PREAMP"]

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._write_READRATE()

    def _write_READRATE(self) -> None:
        _json = self.extracted_data
        try:
            self.fixed_data["READRATE"] = self.kws_specs.dict_w_kws["READRATE"][
                _json["EMMODE"]
            ][_json["READRATE"]]
        except ValueError as e:
            self._write_log_file(repr(e), "READRATE")


class iKon_L(CCD):
    pass
