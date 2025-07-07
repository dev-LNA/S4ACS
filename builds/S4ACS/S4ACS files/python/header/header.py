import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

import astropy.io.fits as fits
from astropy.time import Time

from .utils import (
    allowed_kw_values,
    cards,
    expected_kw_names,
    gains,
    keyword_types,
    read_noise,
)


class Header(ABC):

    hdr = fits.Header(cards)
    kw_types = {"integer": int, "boolean": bool, "float": float, "string": str}
    sub_system = "HEADER"

    def __init__(self, dict_header_jsons, log_file) -> None:
        self.log_file = log_file
        self.dict_header_jsons = dict_header_jsons
        self._load_json(dict_header_jsons)
        self.kw_dataclass = self._initialize_kw_dataclass()
        self.extract_info()
        self._check_type()
        self._check_allowed_values()
        return

    def _load_json(self, dict_header_jsons):
        self.json_string = dict_header_jsons[self.sub_system]
        if self.json_string == "":
            self.original_json = {}
        try:
            _json = json.loads(self.json_string)
            self.original_json = {k.upper(): v for k, v in _json.items()}
        except Exception as e:
            self._write_log_file(
                f"{self.sub_system}: There was an error when loading the JSON data --> {self.json_string}."
                + repr(e),
                "",
            )

    @abstractmethod
    def _initialize_kw_dataclass(self):
        return Keywords_Dataclass()

    def _convert_to_float(self):
        for kw in self.kw_dataclass.to_float_kws:
            try:
                self.hdr[kw] = float(self.new_json[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_int(self):
        for kw in self.kw_dataclass.to_int_kws:
            try:
                self.hdr[kw] = int(self.new_json[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_boolean(self):
        for kw in self.kw_dataclass.to_bool_kws:
            try:
                val = self.new_json[kw]
                self.hdr[kw] = bool(val)
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_bool_with_condition(self):
        for kw, (off, on) in self.kw_dataclass.to_bool_with_condition.items():
            try:
                val = self.new_json[kw]
                if val == off:
                    self.hdr[kw] = False
                elif val == on:
                    self.hdr[kw] = True
                else:
                    pass
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _replace_comma(self):
        for kw in self.kw_dataclass.comma_kws:
            try:
                self._search_unwanted_kw(kw, ",")
                self.new_json[kw] = self.new_json[kw].replace(",", ".")
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _replace_str(self):
        for kw, (prev, new) in self.kw_dataclass.replace_str.items():
            try:
                self._search_unwanted_kw(kw, prev)
                self.hdr[kw] = self.new_json[kw].replace(prev, new)
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _verify_regex(self):
        for kw, (regex_expr, ex_value) in self.kw_dataclass.regex_str.items():
            try:
                kw_value = self.new_json[kw]
                if re.match(regex_expr, kw_value) == None:
                    self._write_log_file(
                        f"The provided value for the keyword {kw} '{kw_value}' does not match the expected format {ex_value}",
                        kw,
                    )
                else:
                    self.hdr[kw] = self.new_json[kw]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _delete_str(self):
        for kw, _str in self.kw_dataclass.delete_str.items():
            try:
                self._search_unwanted_kw(kw, _str)
                self.hdr[kw] = self.hdr[kw].replace(_str, "")
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _replace_empty_str(self):
        for kw, val in self.kw_dataclass.replace_empty_kws.items():
            try:
                if self.hdr[kw] == "":
                    self.hdr[kw] = val
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _write_any_value(self):
        for kw in self.kw_dataclass.write_any_val:
            try:
                self.hdr[kw] = self.new_json[kw]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _write_predefined_value(self):
        for kw in self.kw_dataclass.write_predefined_value:
            try:
                val = self.new_json[kw]
                _list = allowed_kw_values[kw]
                if val in _list:
                    self.hdr[kw] = val
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _substitute_idx_in_dict(self):
        for kw, dict in self.kw_dataclass.idx_in_dict.items():
            try:
                val = self.new_json[kw]
                self.hdr[kw] = dict[val]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _subs_idx_in_list(self):
        for kw in self.kw_dataclass.idx_in_list:
            try:
                _list = allowed_kw_values[kw]
                val = self.new_json[kw]
                self.hdr[kw] = _list[val]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def extract_info(self):
        new_json = {}
        for hdr_kw in self.kw_dataclass.keywords:
            try:
                json_kw = hdr_kw
                expected_name = expected_kw_names[hdr_kw]
                if expected_name != "":
                    json_kw = expected_name
                new_json[hdr_kw] = self.original_json[json_kw]
            except Exception as e:
                self._write_log_file(repr(e), hdr_kw)
        self.new_json = new_json

    def _check_type(self):
        for hdr_kw in self.kw_dataclass.keywords:
            try:
                val = self.new_json[hdr_kw]
                _type = keyword_types[hdr_kw]
                if not isinstance(val, self.kw_types[_type]):
                    self._write_log_file(
                        f'Keyword value "{val}" is not an instance of {repr(_type)}.',
                        hdr_kw,
                    )
            except Exception as e:
                self._write_log_file(repr(e), hdr_kw)

    def _check_allowed_values(self):
        for hdr_kw in self.kw_dataclass.keywords:
            try:
                _type = keyword_types[hdr_kw]
                if _type in ["integer", "float"]:
                    self._check_number_in_range(hdr_kw)
                elif _type == "string":
                    self._check_string_in_allowed_values(hdr_kw)
            except Exception as e:
                self._write_log_file(repr(e), hdr_kw)

        return

    def _check_number_in_range(self, hdr_kw):
        val = self.new_json[hdr_kw]
        a_values = allowed_kw_values[hdr_kw]
        min, *max = a_values
        if not isinstance(val, (int, float)):
            return
        if val < min or val > max[-1]:
            self._write_log_file(
                f'The provided keyword value is out of range {a_values}. "{val}" was found.',
                hdr_kw,
            )
        return

    def _check_string_in_allowed_values(self, hdr_kw):
        val = self.new_json[hdr_kw]
        a_values = allowed_kw_values[hdr_kw]
        if not isinstance(val, str):
            return
        if val not in a_values and a_values != "":
            self._write_log_file(
                f'The expected values for this keyword are {a_values}. "{val}" was found.',
                hdr_kw,
            )
        return

    @abstractmethod
    def fix_keywords(self):
        """Fix header keywords."""
        return

    def _write_log_file(self, message, keyword):
        with open(self.log_file, "a") as file:
            now = str(datetime.now())
            file.write(
                now
                + " - "
                + f"SUB-SYTEM={self.sub_system}, KEYWORD={keyword} - "
                + message
                + "\n"
            )

    def _search_unwanted_kw(self, kw, _str):
        if _str in self.new_json[kw]:
            self._write_log_file(
                f"An unexpected string was found in the keyword value: {_str}", kw
            )

    def reset_header(self):
        Header.hdr = fits.Header(cards)

    def return_empty_header(self):
        return fits.Header(cards)


class Focuser(Header):

    sub_system = "FOCUSER"

    def _initialize_kw_dataclass(self):
        keywords = ["TELFOCUS"]
        to_int_kws = ["TELFOCUS"]
        return Keywords_Dataclass(keywords=keywords, to_int_kws=to_int_kws)

    def fix_keywords(self):
        self._convert_to_int()
        return


class Weather_Station(Header):

    sub_system = "WSTATION"

    def __init__(self, dict_header_jsons, log_file):
        json_string = dict_header_jsons[self.sub_system]
        if "Weather" in json_string[:7]:
            json_string = json_string.replace("Weather", "")
        dict_header_jsons[self.sub_system] = json_string
        super().__init__(dict_header_jsons, log_file)

    def _initialize_kw_dataclass(self):
        keywords = ["HUMIDITY", "EXTTEMP", "PRESSURE"]
        to_float_kws = ["PRESSURE", "HUMIDITY", "EXTTEMP"]
        comma_kws = ["PRESSURE"]
        return Keywords_Dataclass(
            keywords=keywords, to_float_kws=to_float_kws, comma_kws=comma_kws
        )

    def fix_keywords(self):
        self._replace_comma()
        self._convert_to_float()
        return


class S4ICS(Header):

    sub_system = "S4ICS"

    def __init__(self, dict_header_jsons, log_file):
        self.log_file = log_file
        self.dict_header_jsons = dict_header_jsons
        try:
            json_string = dict_header_jsons[self.sub_system].split("\n")[1]
            dict_header_jsons[self.sub_system] = json_string
            self._load_json(dict_header_jsons)
            self._create_s4ics_kws()
        except Exception as e:
            self._write_log_file(repr(e), "")
        self.kw_dataclass = self._initialize_kw_dataclass()
        self.extract_info()
        self._check_type()
        self._check_allowed_values()
        return

    def _initialize_kw_dataclass(self):
        keywords = [
            "WPANG",
            "WPPOS",
            "WPROMODE",
            "WPSEL",
            "WPSELPO",
            "WPSEMODE",
            "CALW",
            "CALWMODE",
            "CALWANG",
            "ASEL",
            "ANMODE",
            "ANALANG",
            "GMIR",
            "GMIRMODE",
            "GFOC",
            "GFOCMODE",
            "ICSVRSN",
        ]
        idx_in_dict = {
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
        to_float_kws = ["GMIR", "GFOC", "WPANG", "WPSELPO", "CALWANG", "ANALANG"]
        to_int_kws = ["WPPOS"]
        to_bool_with_condition = {
            "WPROMODE": ("SIMULATED", "ACTIVE"),
            "WPSEMODE": ("SIMULATED", "ACTIVE"),
            "ANMODE": ("SIMULATED", "ACTIVE"),
            "CALWMODE": ("SIMULATED", "ACTIVE"),
            "GMIRMODE": ("SIMULATED", "ACTIVE"),
            "GFOCMODE": ("SIMULATED", "ACTIVE"),
            "ASEL": ("OFF", "ON"),
        }
        regex_str = {"ICSVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0")}

        return Keywords_Dataclass(
            keywords=keywords,
            to_float_kws=to_float_kws,
            idx_in_dict=idx_in_dict,
            to_bool_with_condition=to_bool_with_condition,
            regex_str=regex_str,
            to_int_kws=to_int_kws,
        )

    def fix_keywords(self):
        self._convert_to_float()
        self._convert_to_int()
        self._substitute_idx_in_dict()
        self._convert_to_bool_with_condition()
        self._verify_regex()
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

    def _treat_s4ics_json(self):
        try:
            mechanisms_list = self.original_json["MECHANISMS"]
            mechanisms = {}
            for mechanism in mechanisms_list:
                mechanism_st = mechanism["status"]
                mechanism_name = mechanism["name"]
                pos_id = mechanism_st["pos_id"]
                if int(mechanism_st["pos_id"]) == -1 and mechanism_name != "WPROT":
                    self._write_log_file(
                        f"There was an error related to the {mechanism_name} position: {mechanism_st}.",
                        "",
                    )
                    continue
                mechanisms[mechanism_name] = mechanism_st

            return mechanisms
        except Exception as e:
            self._write_log_file(repr(e), "")
            return {}

    def _write_WPPOS(self, wppos):
        try:
            kw = "WPPOS"
            wppos = int(wppos)
            s4gui_json = json.loads(self.dict_header_jsons[S4GUI.sub_system])
            inst_mode = s4gui_json["INSTMODE"]
            if wppos == -1 and inst_mode == "PHOT":
                self.original_json[kw] = 0
            elif 1 <= wppos <= 16 and inst_mode == "POL":
                self.original_json[kw] = wppos
            else:
                self._write_log_file(f"The unexpected value {wppos} was found.", kw)
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return


class TCS(Header):

    sub_system = "TCS"

    def __init__(self, _json, night_dir) -> None:
        super().__init__(_json, night_dir)
        self.new_json["TCSDATE"] = self._write_TCSDATE()

    def _initialize_kw_dataclass(self):
        keywords = ["RA", "DEC", "TCSHA", "INSTROT", "AIRMASS"]
        to_float_kws = ["AIRMASS", "INSTROT"]
        regex_str = {
            "RA": (r"[\+-]?\d{2}:\d{2}:\d{2}(\.\d+)?", "HH:MM:SS.ss"),
            "DEC": (r"[\+-]?\d{2}:\d{2}:\d{2}(\.\d+)?", "HH:MM:SS.ss"),
            "TCSHA": (r"[\+-]?\d{2}:\d{2}:\d{2}(\.\d+)?", "HH:MM:SS.ss"),
            "TCSDATE": (
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}",
                "YYY-MM-DDTHH:MM:SS.sss",
            ),
        }
        comma_kws = ["TCSHA"]

        return Keywords_Dataclass(
            keywords=keywords,
            to_float_kws=to_float_kws,
            comma_kws=comma_kws,
            regex_str=regex_str,
        )

    def fix_keywords(self):
        self._convert_to_float()
        self._write_any_value()
        self._replace_comma()
        self._verify_regex()
        return

    def _write_TCSDATE(self):
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
            return tcsdate
        except Exception as e:
            self._write_log_file(repr(e), "TCSDATE")


class S4GUI(Header):

    sub_system = "S4GUI"

    def _initialize_kw_dataclass(self):
        keywords = [
            "CHANNEL1",
            "CHANNEL2",
            "CHANNEL3",
            "CHANNEL4",
            "OBJECT",
            "OBSERVER",
            "PROJID",
            "TCSMODE",
            "FILTER",
            "GUIVRSN",
            "CTRLINTE",
            "SYNCMODE",
            "INSTMODE",
            "OBSTYPE",
        ]
        to_bool_kw = ["CHANNEL1", "CHANNEL2", "CHANNEL3", "CHANNEL4", "TCSMODE"]
        write_any_val = ["OBJECT", "OBSERVER", "PROJID"]
        write_predefined_value = [
            "FILTER",
            "CTRLINTE",
            "SYNCMODE",
            "OBSTYPE",
            "INSTMODE",
        ]
        regex_str = {"GUIVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0")}

        return Keywords_Dataclass(
            keywords=keywords,
            to_bool_kws=to_bool_kw,
            write_any_val=write_any_val,
            write_predefined_value=write_predefined_value,
            regex_str=regex_str,
        )

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
                self._write_log_file(f"An empty string was found.", kw)
                return
            if kw in self.hdr.keys():
                del self.hdr[kw]

            self.hdr[kw] = self.original_json[kw]
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return

    def fix_keywords(self):
        self._convert_to_boolean()
        self._write_any_value()
        self._write_predefined_value()
        self._verify_regex()
        self._write_COMMENT()
        return


class CCD(Header):

    sub_system = "CCD"
    trigger_modes = {0: "Internal", 6: "External"}
    acq_modes = {1: "Single Scan", 3: "Kinetics"}
    em_modes = ["Electron Multiplying", "Conventional"]
    shutter_modes = ["Auto", "Open", "Closed"]
    vclock_modes = ["Normal", "+1", "+2", "+3", "+4"]
    preamp_modes = ["Gain 1", "Gain 2"]
    vshift_modes = [0.6, 1.13, 2.2, 4.33]

    def _load_json(self, dict_header_jsons):
        super()._load_json(dict_header_jsons)
        self._fix_ccd_parameters()

    def _initialize_kw_dataclass(self):
        keywords = [
            "FRAMEIND",
            "CCDTEMP",
            "TEMPST",
            "CCDSERN",
            "PREAMP",
            "READRATE",
            "EMGAIN",
            "VSHIFT",
            "FRAMETRF",
            "VCLKAMP",
            "ACQMODE",
            "EMMODE",
            "SHUTTER",
            "TRIGGER",
            "VBIN",
            "INITLIN",
            "INITCOL",
            "FINALLIN",
            "FINALCOL",
            "HBIN",
            "EXPTIME",
            "NFRAMES",
            "TGTEMP",
            "COOLER",
            "DATE-OBS",
            "UTTIME",
            "UTDATE",
        ]

        to_bool_kws = ["COOLER", "FRAMETRF"]
        to_float_kws = ["EXPTIME"]
        to_int_kws = [
            "VBIN",
            "HBIN",
            "FINALCOL",
            "FINALLIN",
            "INITCOL",
            "INITLIN",
            "FRAMEIND",
            "CCDSERN",
            "EMGAIN",
            "NFRAMES",
            "CCDTEMP",
            "TGTEMP",
        ]
        write_predefined_value = [
            "TEMPST",
            "TRIGGER",
            "ACQMODE",
            "EMMODE",
            "SHUTTER",
            "VSHIFT",
            "READRATE",
            "PREAMP",
            "VCLKAMP",
        ]
        regex_str = {
            "DATE-OBS": (
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}",
                "YYYY-MM-DDTHH:MM:SS.ssssss",
            ),
            "UTTIME": (r"\d{2}:\d{2}:\d{2}\.\d{6}", "HH:MM:SS.ssssss"),
            "UTDATE": (r"\d{4}-\d{2}-\d{2}", "YYYY-MM-DD"),
        }

        return Keywords_Dataclass(
            keywords=keywords,
            to_bool_kws=to_bool_kws,
            to_float_kws=to_float_kws,
            to_int_kws=to_int_kws,
            write_predefined_value=write_predefined_value,
            regex_str=regex_str,
        )

    def fix_keywords(self):
        self._convert_to_boolean()
        self._convert_to_float()
        self._convert_to_int()
        self._subs_idx_in_list()
        self._substitute_idx_in_dict()
        self._write_predefined_value()
        self._verify_regex()
        self._write_ccd_gain()
        self._write_read_noise()
        self._fix_EXPTIME()

        return

    def _write_read_noise(self):
        try:
            idx = self.find_index_tab()
            self.hdr["RDNOISE"] = read_noise[f"{self.hdr['CCDSERN']}"][idx]
        except Exception as e:
            self._write_log_file(repr(e), "RDNOISE")

    def _write_ccd_gain(self):
        try:
            idx = self.find_index_tab()
            self.hdr["GAIN"] = gains[f"{self.hdr['CCDSERN']}"][idx]
        except Exception as e:
            self._write_log_file(repr(e), "GAIN")

    def find_index_tab(self):
        _json = self.new_json
        index = 0
        if _json["EMMODE"] == "Conventional":
            index += 8
            readout_modes = [1.0, 0.1]
        else:
            readout_modes = [30.0, 20.0, 10.0, 1.0]
        index += 2 * readout_modes.index(_json["READRATE"])
        index += float(_json["PREAMP"][-1]) - 1
        return index

    def _fix_ccd_parameters(self):
        _json = self.original_json
        _json["READRATE"] = self._write_READRATE(_json)
        _json["TRIGGER"] = self.trigger_modes[_json["TRIGGER"]]
        _json["ACQMODE"] = self.acq_modes[_json["ACQMODE"]]
        _json["EMMODE"] = self.em_modes[_json["EMMODE"]]
        _json["SHUTTER"] = self.shutter_modes[_json["SHUTTER"]]
        _json["VCLKAMP"] = self.vclock_modes[_json["VCLKAMP"]]
        _json["PREAMP"] = self.preamp_modes[_json["PREAMP"]]
        _json["VSHIFT"] = self.vshift_modes[_json["VSHIFT"]]
        _json["COOLER"] = _json["COOLER"] == 1
        _json["EXPTIME"] = float(_json["EXPTIME"])
        self.original_json = _json

    @staticmethod
    def _write_READRATE(_json):
        _list = [30.0, 20.0, 10.0, 1.0]
        if _json["EMMODE"] == 1:
            _list = [1.0, 0.1]
        return _list[_json["READRATE"]]

    def _fix_EXPTIME(self):
        if 1e-5 > self.hdr["EXPTIME"] > 9.9999997e-6:
            self.hdr["EXPTIME"] = 10e-6
        return


class General_KWs(Header):

    sub_system = "GENERAL KW"

    def _initialize_kw_dataclass(self):
        keywords = [
            "FILENAME",
            "SEQINDEX",
            "NCYCLES",
            "NSEQ",
            "CYCLIND",
            "ACSVRSN",
            "ACSMODE",
            "CHANNEL",
            "ACQERROR",
        ]

        to_int_kws = [
            "NSEQ",
            "NCYCLES",
            "CHANNEL",
            "SEQINDEX",
            "CYCLIND",
        ]
        regex_str = {
            "ACSVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0"),
            "FILENAME": (
                r"\d{8}_s4c[1-4]_\d{6}(_[a-z0-9]+)?\.fits",
                "YYYYMMDD_s4c1_000000.fits",
            ),
        }

        to_bool_kw = ["ACSMODE", "ACQERROR"]
        replace_empty_kws = {
            "NAXIS": 2,
            "OBSLONG": -45.5825,
            "OBSLAT": -22.534,
            "OBSALT": 1864.0,
            "EQUINOX": 2000.0,
            "INSTRUME": "SPARC4",
            "SIMPLE": True,
            "BITPIX": 16,
        }
        return Keywords_Dataclass(
            keywords=keywords,
            replace_empty_kws=replace_empty_kws,
            to_bool_kws=to_bool_kw,
            to_int_kws=to_int_kws,
            regex_str=regex_str,
        )

    def _load_json(self, dict_header_jsons):
        super()._load_json(dict_header_jsons)
        self._fix_parameters()

    def _fix_parameters(self):
        self.original_json["SEQINDEX"] = self.original_json["SEQINDEX"] + 1
        self.original_json["CYCLIND"] = self.original_json["CYCLIND"] + 1

    def fix_keywords(self):
        self._replace_empty_str()
        self._convert_to_int()
        self._verify_regex()
        self._convert_to_boolean()


@dataclass
class Keywords_Dataclass:
    keywords: list = field(default_factory=list)

    to_float_kws: list = field(default_factory=list)
    to_int_kws: list = field(default_factory=list)
    to_bool_kws: list = field(default_factory=list)
    to_bool_with_condition: dict = field(default_factory=dict)

    comma_kws: list = field(default_factory=list)
    replace_str: dict = field(default_factory=dict)
    delete_str: dict = field(default_factory=dict)
    regex_str: dict = field(default_factory=dict)

    write_any_val: list = field(default_factory=list)
    write_predefined_value: dict = field(default_factory=dict)

    idx_in_dict: dict = field(default_factory=dict)
    idx_in_list: dict = field(default_factory=dict)
    replace_empty_kws: dict = field(default_factory=dict)
