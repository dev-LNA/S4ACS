import pandas as pd

from .header import Header


class CCD(Header):
    name = "CCD"

    def __init__(self, log_file, hdr_cnt, csv_folder) -> None:
        super().__init__(log_file, hdr_cnt, csv_folder)
        self.gain_values = pd.read_csv(csv_folder / "preamp_gains.csv")
        self.rd_values = pd.read_csv(csv_folder / "read_noises.csv")

        self.idx_tab = self._find_index_tab()
        self.dict_w_kws = {
            "TRIGGER": {0: "Internal", 6: "External"},
            "ACQMODE": {1: "Single Scan", 3: "Kinetics"},
            "SHUTTER": ["Auto", "Open", "Closed"],
            "VCLKAMP": ["Normal", "+1", "+2", "+3", "+4"],
            "VSHIFT": [],
            "PREAMP": [],
            "READRATE": [],
        }
        self.regex_expressions = {
            "DATE-OBS": (
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}",
                "YYYY-MM-DDTHH:MM:SS.ssssss",
            ),
            "UTTIME": (r"\d{2}:\d{2}:\d{2}\.\d{6}", "HH:MM:SS.ssssss"),
            "UTDATE": (r"\d{4}-\d{2}-\d{2}", "YYYY-MM-DD"),
        }

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._write_ccd_gain()
        self._write_read_noise()
        self._fix_EXPTIME()
        self.calc_NAXIS1()
        self.calc_NAXIS2()
        self.fixed_data["FRAMEIND"] += 1

        return

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

    def _find_index_tab(self) -> int:
        _json = self.extracted_data
        index = 2 * _json["READRATE"] + _json["PREAMP"]
        return index

    def _fix_EXPTIME(self) -> None:
        if 1e-5 > self.fixed_data["EXPTIME"] > 9.999999e-6:
            self.fixed_data["EXPTIME"] = 1e-5
        return

    def calc_NAXIS1(self) -> None:
        self.fixed_data["NAXIS1"] = (
            self.fixed_data["FINALLIN"] - self.fixed_data["INITLIN"]
        ) // self.fixed_data["VBIN"] + 1
        return

    def calc_NAXIS2(self) -> None:
        self.fixed_data["NAXIS2"] = (
            self.fixed_data["FINALCOL"] - self.fixed_data["INITCOL"]
        ) // self.fixed_data["HBIN"] + 1
        return


class iXon_Ultra(CCD):
    def __init__(self, log_file, hdr_cnt, csv_folder) -> None:
        super().__init__(log_file, hdr_cnt, csv_folder)
        self.dict_w_kws["VSHIFT"] = [0.6, 1.13, 2.2, 4.33]
        self.dict_w_kws["PREAMP"] = ["Gain 1", "Gain 2"]
        self.dict_w_kws["EMMODE"] = ["Electron Multiplying", "Conventional"]
        self.dict_w_kws["READRATE"] = {
            0: [30.0, 20.0, 10.0, 1.0],
            1: [1.0, 0.1],
        }

    def _find_index_tab(self) -> int:
        _json = self.extracted_data
        return 8 * _json["EMMODE"] + 2 * _json["READRATE"] + _json["PREAMP"]

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._write_READRATE()

    def _write_READRATE(self) -> None:
        _json = self.extracted_data
        try:
            self.fixed_data["READRATE"] = self.dict_w_kws["READRATE"][_json["EMMODE"]][
                _json["READRATE"]
            ]
        except ValueError as e:
            self._write_log_file(repr(e), "READRATE")


class iKon_L(CCD):
    def __init__(self, log_file, hdr_cnt, csv_folder) -> None:
        super().__init__(log_file, hdr_cnt, csv_folder)
        self.dict_w_kws["VSHIFT"] = [38.55, 76.95]
        self.dict_w_kws["PREAMP"] = ["Gain 1", "Gain 2", "Gain 4"]
        self.dict_w_kws["READRATE"] = [0.05, 1.0, 3.0, 5.0]
