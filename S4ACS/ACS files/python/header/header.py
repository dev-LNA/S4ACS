import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from os.path import dirname, join, realpath
from pathlib import Path

import astropy.io.fits as fits
import pandas as pd
from astropy.time import Time
from numpy import abs

from .utils import Header_Parameters


class Header(ABC):

    kw_types = {"integer": int, "boolean": bool, "float": float, "string": str}
    sub_system = "HEADER"

    def __init__(
        self,
        dict_header_jsons: dict,
        log_file: str,
        hdr_params: Header_Parameters,
        csv_folder: Path,
    ) -> None:
        self.header_keywords = None
        self.to_int_kws = None
        self.to_float_kws = None
        self.to_bool_kws = None
        self.to_bool_w_cond_kws = None
        self.kws_in_dict = None
        self.dict_w_kws = None
        self.replace_comma_kws = None
        self.empty_kws = None
        self.write_any_val = None
        self.write_predefined_val = None
        self.regex_strings = None
        self.new_json = None
        self.how_to_fix_regex = None
        self.regex_expressions = None
        self.log_file = log_file
        self.hdr_params = hdr_params
        self.json_string = dict_header_jsons[self.sub_system]
        self.csv_folder = csv_folder
        self.filename = json.loads(dict_header_jsons["CCD"])["FILENAME"]

        self.original_json = self._load_json()
        self._read_kws_config()

        return

    def _load_json(self) -> dict:
        try:
            if self.json_string == "":
                return
            _json = json.loads(self.json_string)
            return {k.upper(): v for k, v in _json.items()}
        except Exception as e:
            self._write_log_file(
                f"{self.sub_system}: There was an error when loading the JSON data --> {self.json_string}."
                + repr(e),
                "",
            )

    def _read_kws_config(self) -> None:
        csv_file_path = join(
            self.csv_folder, "keywords config", self.sub_system + ".csv"
        )
        kws_config = pd.read_csv(csv_file_path).fillna("")
        self.header_keywords = kws_config["Header Keywords"].values
        if "to bool" in kws_config.keys():
            self.to_bool_kws = [
                val for val in kws_config["to bool"].values if val != ""
            ]
        if "to int" in kws_config.keys():
            self.to_int_kws = [val for val in kws_config["to int"].values if val != ""]
        if "to float" in kws_config.keys():
            self.to_float_kws = [
                val for val in kws_config["to float"].values if val != ""
            ]
        if "replace comma" in kws_config.keys():
            self.replace_comma_kws = [
                val for val in kws_config["replace comma"].values if val != ""
            ]
        if "write any val" in kws_config.keys():
            self.write_any_val = [
                val for val in kws_config["write any val"].values if val != ""
            ]
        if "write predefined val" in kws_config.keys():
            self.write_predefined_val = [
                val for val in kws_config["write predefined val"].values if val != ""
            ]
        if "kws in dict" in kws_config.keys():
            self.kws_in_dict = [
                val for val in kws_config["kws in dict"].values if val != ""
            ]
        if "regex strings" in kws_config.keys():
            self.regex_strings = [
                val for val in kws_config["regex strings"].values if val != ""
            ]
        self.to_bool_w_cond_kws = self._get_bool_w_cond_kws(kws_config)

        return

    @staticmethod
    def _get_bool_w_cond_kws(kws_config) -> dict:
        if "to bool w cond" in kws_config.keys():
            return {
                kw: condition.split(";")
                for (kw, condition) in zip(
                    kws_config["to bool w cond"], kws_config["to bool condition"]
                )
                if kw != ""
            }
        return

    def extract_info(self) -> None:
        new_json = {}
        for hdr_kw in self.header_keywords:
            try:
                json_kw = hdr_kw
                expected_name = self.hdr_params.expected_kw_names[hdr_kw]
                if expected_name != "":
                    json_kw = expected_name
                new_json[hdr_kw] = self.original_json[json_kw]
            except Exception as e:
                self._write_log_file(repr(e), hdr_kw)
        self.new_json = new_json

    def validate_info(self) -> None:
        self._check_type()
        self._check_allowed_values()
        return

    def _check_type(self):
        for hdr_kw in self.header_keywords:
            try:
                val = self.new_json[hdr_kw]
                _type = self.hdr_params.keyword_types[hdr_kw]
                if not isinstance(val, self.kw_types[_type]):
                    self.new_json[hdr_kw] = ""
                    self._write_log_file(
                        f'Keyword value "{val}" is not an instance of {repr(_type)}.',
                        hdr_kw,
                    )
            except Exception as e:
                self._write_log_file(repr(e), hdr_kw)

    def _check_allowed_values(self):
        for hdr_kw in self.header_keywords:
            try:
                _type = self.hdr_params.keyword_types[hdr_kw]
                if _type in ["integer", "float"]:
                    self._check_number_in_range(hdr_kw)
                elif _type == "string":
                    self._check_string_in_allowed_values(hdr_kw)
            except Exception as e:
                self._write_log_file(repr(e), hdr_kw)

        return

    def _check_number_in_range(self, hdr_kw):
        val = self.new_json[hdr_kw]
        a_values = self.hdr_params.allowed_kw_values[hdr_kw]
        min, *max = a_values
        if not min <= val <= max[-1]:
            self.new_json[hdr_kw] = ""
            self._write_log_file(
                f'The provided keyword value is out of range {a_values}. "{val}" was found.',
                hdr_kw,
            )
        return

    def _check_string_in_allowed_values(self, hdr_kw):
        val = self.new_json[hdr_kw]
        a_values = self.hdr_params.allowed_kw_values[hdr_kw]
        if val not in a_values and a_values != "":
            self.new_json[hdr_kw] = ""
            self._write_log_file(
                f'The expected values for this keyword are {a_values}. "{val}" was found.',
                hdr_kw,
            )
        return

    def fill_image_header(self, hdr: fits.Header) -> fits.Header:
        for kw in self.new_json:
            try:
                hdr[kw] = self.new_json[kw]
            except Exception as e:
                self._write_log_file(repr(e), kw)
        return hdr

    def fix_keywords(self):
        for func in [
            self._replace_comma,
            self._convert_to_boolean,
            self._convert_to_float,
            self._convert_to_int,
            self._convert_to_bool_with_condition,
            self._write_any_value,
            self._write_predefined_value,
            self._verify_regex,
            self._kw_in_dict,
            self._replace_empty_kws,
        ]:
            func()
        return

    def _write_log_file(self, message, keyword):
        with open(self.log_file, "a") as file:
            now = str(datetime.now())
            file.write(
                now
                + " - "
                + f"FILENAME= {self.filename}, "
                + f"SUB-SYTEM={self.sub_system}, KEYWORD={keyword} - "
                + message
                + "\n"
            )

    # ----------------------------------------------------------------------------------

    def _convert_to_float(self) -> None:
        if self.to_float_kws == None:
            return
        for kw in self.to_float_kws:
            try:
                self.new_json[kw] = float(self.new_json[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_int(self) -> None:
        if self.to_int_kws == None:
            return
        for kw in self.to_int_kws:
            try:
                self.new_json[kw] = int(self.new_json[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_boolean(self) -> None:
        if self.to_bool_kws == None:
            return
        for kw in self.to_bool_kws:
            try:
                self.new_json[kw] = bool(self.new_json[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_bool_with_condition(self) -> None:
        if self.to_bool_w_cond_kws == None:
            return
        for kw, (off, on) in self.to_bool_w_cond_kws.items():
            try:
                val = self.new_json[kw]
                if val == off:
                    self.new_json[kw] = False
                elif val == on:
                    self.new_json[kw] = True
                else:
                    pass
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _replace_comma(self) -> None:
        if self.replace_comma_kws == None:
            return
        for kw in self.replace_comma_kws:
            try:
                self._search_unwanted_kw(kw, ",")
                self.new_json[kw] = self.new_json[kw].replace(",", ".")
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _verify_regex(self) -> None:
        if self.regex_strings == None:
            return
        for kw in self.regex_strings:
            try:
                kw_value = self.new_json[kw]
                regex_expr, ex_val = self.regex_expressions[kw]
                if re.match(regex_expr, kw_value) == None:
                    self._write_log_file(
                        f"The provided value for the keyword {kw} '{kw_value}' does not match the expected format {ex_val}. Trying to fix...",
                        kw,
                    )
                    self._fix_regex_keyword(kw)
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _fix_regex_keyword(self, kw) -> None:
        try:
            kw_value = self.new_json[kw]
            regex_expr, _ = self.regex_expressions[kw]
            if kw not in self.how_to_fix_regex.keys():
                self._write_log_file(
                    f"The method to fix this keyword was not found.", kw
                )
                return
            new_value = self.how_to_fix_regex[kw](kw_value)
            if re.match(regex_expr, new_value) == None:
                self._write_log_file(
                    f"The provided value {kw_value} could not be fixed.", kw
                )
                return
            self.new_json[kw] = new_value
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return

    def _replace_empty_kws(self) -> None:
        if self.empty_kws == None:
            return
        for kw, val in self.empty_kws.items():
            try:
                self.new_json[kw] = val
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _write_any_value(self) -> None:
        if self.write_any_val == None:
            return
        for kw in self.write_any_val:
            try:
                self.new_json[kw] = self.new_json[kw]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _write_predefined_value(self) -> None:
        if self.write_predefined_val == None:
            return
        for kw in self.write_predefined_val:
            try:
                _list = self.hdr_params.allowed_kw_values[kw]
                val = self.new_json[kw]
                if val not in _list:
                    self._write_log_file(
                        f"The provided value should be in the expected values list {_list}. {val} was found.",
                        kw,
                    )

            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _kw_in_dict(self) -> None:
        if self.kws_in_dict == None:
            return
        for kw in self.kws_in_dict:
            try:
                val = self.new_json[kw]
                self.new_json[kw] = self.dict_w_kws[kw][val]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _search_unwanted_kw(self, kw, _str):
        if _str in self.new_json[kw]:
            self._write_log_file(
                f"An unexpected string was found in the keyword value: {_str}", kw
            )


class Focuser(Header):

    sub_system = "FOCUSER"


class Weather_Station(Header):

    sub_system = "WSTATION"

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder):
        json_string = dict_header_jsons[self.sub_system]
        if "Weather" in json_string[:7]:
            json_string = json_string.replace("Weather", "")
        dict_header_jsons[self.sub_system] = json_string
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)


class ICS(Header):

    sub_system = "ICS"

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder) -> None:
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.how_to_fix_regex = {"ICSVRSN": self._fix_ICSVRSN}
        self.regex_expressions = {"ICSVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0")}
        return

    @staticmethod
    def _fix_ICSVRSN(kw_value):
        return "v" + kw_value


class S4ICS(ICS):

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder) -> None:
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.dict_w_kws = {
            "WPSEL": {"OFF": "None", "L/2": "L2", "L/4": "L4"},
            "CALW": {
                "POLARIZER": "POLARIZER",
                "DEPOLARIZER": "DEPOLARIZER",
                "CLEAR": "CLEAR",
                "OFF": "CLEAR",
                "PINHOLE": "SPARE",
                "SPARE": "SPARE",
                "SHUTTER": "CLOSED",
                "CLOSED": "CLOSED",
            },
        }
        self.inst_mode = json.loads(dict_header_jsons["GUI"])["INSTMODE"]
        return

    def _create_s4ics_kws(self):
        mechanisms = self._treat_s4ics_json()

        components_list = [
            "WPROMODE",
            "WPSEMODE",
            "CALWMODE",
            "ANMODE",
            "GMIRMODE",
            "GFOCMODE",
        ]
        s4ics_correspondents = ["WPROT", "WPSEL", "CALW", "ASEL", "GMIR", "GFOC"]
        self._write_s4ics_kws_into_json(
            mechanisms, components_list, s4ics_correspondents, "mode"
        )

        components_list = ["WPANG", "WPSELPO", "CALWANG", "ANALANG", "GMIR", "GFOC"]
        self._write_s4ics_kws_into_json(
            mechanisms, components_list, s4ics_correspondents, "position"
        )

        components_list = ["WPSEL", "CALW", "ASEL"]
        self._write_s4ics_kws_into_json(
            mechanisms, components_list, components_list, "pos_name"
        )

        try:
            self.original_json["ICSVRSN"] = self.original_json["VERSION"]
        except Exception as e:
            self._write_log_file(repr(e), "ICSVRSN")

        self._write_WPPOS(mechanisms["WPROT"]["pos_id"])

    def _write_s4ics_kws_into_json(
        self, mechanisms, components_list, s4ics_correspondents, st_param
    ):
        for comp, ics_corresp in zip(components_list, s4ics_correspondents):
            try:
                self.original_json[comp] = mechanisms[ics_corresp][st_param]
            except Exception as e:
                self._write_log_file(repr(e), comp)

    def _treat_s4ics_json(self) -> dict:
        try:
            mechanisms_list = self.original_json["MECHANISMS"]
            mechanisms = {}
            for mechanism in mechanisms_list:
                status = mechanism["status"]
                name = mechanism["name"]
                pos_id = int(status["pos_id"])
                if pos_id == -1 and name != "WPROT":
                    self._write_log_file(
                        f"There was an error related to the {name} position: {status}.",
                        "",
                    )
                mechanisms[name] = status

            return mechanisms
        except Exception as e:
            self._write_log_file(repr(e), "")
            return {}

    def _write_WPPOS(self, wppos) -> None:
        try:
            kw = "WPPOS"
            wppos = int(wppos)
            if wppos == -1 and self.inst_mode == "PHOT":
                self.original_json[kw] = 0
            elif 1 <= wppos <= 16 and self.inst_mode == "POLAR":
                self.original_json[kw] = wppos
            else:
                self._write_log_file(f"The unexpected value {wppos} was found.", kw)
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return

    def extract_info(self):
        self._create_s4ics_kws()
        super().extract_info()


class TCS(Header):

    sub_system = "TCS"

    def __init__(self, dict_header_jsons, night_dir, hdr_params, csv_folder) -> None:
        super().__init__(dict_header_jsons, night_dir, hdr_params, csv_folder)
        self.obstype = json.loads(dict_header_jsons["GUI"])["OBSTYPE"]
        self.how_to_fix_regex = {
            k: self._fix_coordinates for k in ["RA", "DEC", "TCSHA"]
        }
        self.regex_expressions = {
            "RA": (r"[\+-]?\d{2}:\d{2}:\d{2}\.\d{2}", "HH:MM:SS.ss"),
            "DEC": (r"[\+-]?\d{2}:\d{2}:\d{2}\.\d{2}", "HH:MM:SS.ss"),
            "TCSHA": (r"[\+-]?\d{2}:\d{2}:\d{2}\.\d{2}", "HH:MM:SS.ss"),
        }

    def fix_keywords(self):
        super().fix_keywords()
        self._write_TCSDATE()
        self.fix_RA_DEC()
        return

    def _write_TCSDATE(self) -> None:
        try:
            for kw in ["DATE", "TIME"]:
                if not isinstance(self.original_json[kw], str):
                    self._write_log_file(
                        f'Keyword value "{self.original_json[kw]}" is not an instance of {repr(str)}.',
                        kw,
                    )
                    return
            date, time = self.original_json["DATE"], self.original_json["TIME"]
            date = date.split("/")[::-1]
            time = time.split(":")
            tmp = [int(val) for val in date + time]
            tmp[0] += 2000
            tcsdate = Time(datetime(*tmp)).isot
            self.new_json["TCSDATE"] = tcsdate
        except Exception as e:
            self._write_log_file(repr(e), "TCSDATE")

    @staticmethod
    def _fix_coordinates(
        kw_value: str,
    ) -> str:  # está gerando log de erro. tratar melhor
        new_value = kw_value.strip()
        new_value = re.sub(r"^([+-]?\d{1,2})$", r"\1:00:00", new_value)
        new_value = re.sub(r"^([+-]?\d{1,2}):(\d{1,2})$", r"\1:\2:00", new_value)
        h, m, s = new_value.split(":")
        h, m, s = abs(int(h)), abs(int(m)), abs(float(s))
        new_value = f"{h:02}:{m:02}:{s:05.2f}"

        if "-" in kw_value:
            new_value = "-" + new_value
        return new_value

    def fix_RA_DEC(self) -> None:
        for kw in ["RA", "DEC"]:
            try:
                kw_value = self.new_json[kw]
                if kw_value == "" and self.obstype in ["ZERO", "FLAT", "DARK"]:
                    new_value = "00:00:00.00"
                    self._write_log_file(
                        f"An empty string was found for the keyword {kw}. As OBSTYPE={self.obstype}, the keyword value was changed to {new_value}",
                        kw,
                    )
                    self.new_json[kw] = new_value
            except Exception as e:
                self._write_log_file(repr(e), kw)


class S4GUI(Header):

    sub_system = "GUI"

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder) -> None:
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.regex_expressions = {
            "GUIVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0"),
        }
        return

    def _write_COMMENT(self):
        kw = "COMMENT"
        try:
            val = self.original_json[kw]
            if not isinstance(val, str):
                self._write_log_file(
                    f'Keyword value "{val}" is not an instance of {str}.', kw
                )
                return
            if self.original_json[kw] == "":
                return
            self.new_json[kw] = val
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return

    def fix_keywords(self):
        super().fix_keywords()
        self._write_COMMENT()
        return


class CCD(Header):

    sub_system = "CCD"

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder):
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
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

    def fix_keywords(self):
        super().fix_keywords()
        self._write_ccd_gain()
        self._write_read_noise()
        self._fix_EXPTIME()
        self.calc_NAXIS1()
        self.calc_NAXIS2()
        self.new_json["FRAMEIND"] += 1

        return

    def _write_read_noise(self):
        try:
            val = self.hdr_params.rd_values[f"{self.new_json['CCDSERN']}"][self.idx_tab]
            self.new_json["RDNOISE"] = float(val)
        except Exception as e:
            self._write_log_file(repr(e), "RDNOISE")

    def _write_ccd_gain(self):
        try:
            val = self.hdr_params.gain_values[f"{self.new_json['CCDSERN']}"][
                self.idx_tab
            ]
            self.new_json["GAIN"] = float(val)
        except Exception as e:
            self._write_log_file(repr(e), "GAIN")

    def _find_index_tab(self) -> int:
        _json = self.original_json
        index = 2 * _json["READRATE"] + _json["PREAMP"]
        return index

    def _fix_EXPTIME(self):
        if 1e-5 > self.new_json["EXPTIME"] > 9.999999e-6:
            self.new_json["EXPTIME"] = 10e-6
        return

    def calc_NAXIS1(self) -> None:
        self.new_json["NAXIS1"] = (
            self.new_json["FINALLIN"] - self.new_json["INITLIN"]
        ) // self.new_json["VBIN"] + 1
        return

    def calc_NAXIS2(self) -> None:
        self.new_json["NAXIS2"] = (
            self.new_json["FINALCOL"] - self.new_json["INITCOL"]
        ) // self.new_json["HBIN"] + 1
        return


class iXon_Ultra(CCD):

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder):
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.dict_w_kws["VSHIFT"] = [0.6, 1.13, 2.2, 4.33]
        self.dict_w_kws["PREAMP"] = ["Gain 1", "Gain 2"]
        self.dict_w_kws["EMMODE"] = ["Electron Multiplying", "Conventional"]
        self.dict_w_kws["READRATE"] = {0: [30.0, 20.0, 10.0, 1.0], 1: [1.0, 0.1]}

    def _find_index_tab(self) -> int:
        _json = self.original_json
        return 8 * _json["EMMODE"] + 2 * _json["READRATE"] + _json["PREAMP"]

    def fix_keywords(self):
        super().fix_keywords()
        self._write_READRATE()

    def _write_READRATE(self):
        _json = self.original_json
        try:
            self.new_json["READRATE"] = self.dict_w_kws["READRATE"][_json["EMMODE"]][
                _json["READRATE"]
            ]
        except ValueError as e:
            self._write_log_file(repr(e), "READRATE")


class iKon_L(CCD):

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder):
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.dict_w_kws["VSHIFT"] = [38.55, 76.95]
        self.dict_w_kws["PREAMP"] = ["Gain 1", "Gain 2", "Gain 4"]
        self.dict_w_kws["READRATE"] = [0.05, 1.0, 3.0, 5.0]


class General_KWs(Header):

    sub_system = "GENERAL KW"

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder):
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.regex_expressions = {
            "ACSVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0"),
        }
        # O pandas trata tudo como uma string
        self.empty_kws = {
            "NAXIS": 2,
            "OBSLONG": -45.5825,
            "OBSLAT": -22.534,
            "OBSALT": 1864.0,
            "EQUINOX": 2000.0,
            "SIMPLE": True,
            "BITPIX": 16,
            "BZERO": 1,
            "BSCALE": 32768,
        }

    def fix_keywords(self):
        super().fix_keywords()
        self.new_json["CYCLIND"] = self.new_json["CYCLIND"] + 1


class General_SPARC4_KWs(General_KWs):

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder):
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.regex_expressions["FILENAME"] = (
            r"\d{8}_s4c[1-4]_\d{6}(_[a-z0-9]+)?\.fits",
            "YYYYMMDD_s4c1_000000.fits",
        )
        self.empty_kws["INSTRUME"] = "SPARC4"

    def fix_keywords(self):
        super().fix_keywords()
        self.new_json["SEQINDEX"] = self.new_json["SEQINDEX"] + 1


class General_ECHARPE_KWs(General_KWs):
    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder):
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.regex_expressions["FILENAME"] = (
            r"\d{8}_ECH_(BLUE|RED)_\d{6}[ozdfts](_[a-z0-9]+)?\.fits",
            "YYYYMMDD_s4c1_000000.fits",
        )
        self.empty_kws["INSTRUME"] = "ECHARPE"

        return


class Header_Tester(Header):

    sub_system = "TESTER"

    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder):
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.dict_w_kws = {"VSHIFT": [0.6, 1.13, 2.2, 4.33]}
        self.regex_expressions = {"GUIVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0")}
        self.how_to_fix_regex = {"GUIVRSN": self._fix_soft_version}
        self.empty_kws = {"BITPIX": 16}

    @staticmethod
    def _fix_soft_version(kw_value):
        return "v" + kw_value
