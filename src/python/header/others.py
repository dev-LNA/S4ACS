import json
import re
from datetime import datetime

from astropy.time import Time

from .header import Header


class Focuser(Header):
    sub_system = "FOCUSER"

    def _fix_tfocstat(self) -> None:
        try:
            if self.original_json["INITIALIZED"] is False:
                self.new_json["TFOCSTAT"] = "NONE"
                return
            elif self.original_json["ISMOVING"] is True:
                self.new_json["TFOCSTAT"] = "BUSY"
            elif self.original_json["ISMOVING"] is False:
                self.new_json["TFOCSTAT"] = "READY"
            else:
                self.new_json["TFOCSTAT"] = ""
        except Exception as e:
            self._write_log_file(repr(e), "TFOCSTAT")
        return

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._fix_tfocstat()
        return


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

    def _create_s4ics_kws(self) -> None:
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

        components_list = [
            comp + "STAT" for comp in ["WPRO", "WPSE", "CALW", "AN", "GMIR", "GFOC"]
        ]
        self._write_s4ics_kws_into_json(
            mechanisms, components_list, s4ics_correspondents, "condition"
        )

        try:
            self.original_json["ICSVRSN"] = self.original_json["VERSION"]
        except Exception as e:
            self._write_log_file(repr(e), "ICSVRSN")

        self._write_WPPOS(mechanisms["WPROT"]["pos_id"])

    def _write_s4ics_kws_into_json(
        self, mechanisms, components_list, s4ics_correspondents, st_param
    ) -> None:
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

    def extract_info(self) -> None:
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

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._write_ccd_gain()
        self._write_read_noise()
        self._fix_EXPTIME()
        self.calc_NAXIS1()
        self.calc_NAXIS2()
        self.new_json["FRAMEIND"] += 1

        return

    def _write_read_noise(self) -> None:
        try:
            val = self.hdr_params.rd_values[f"{self.new_json['CCDSERN']}"][self.idx_tab]
            self.new_json["RDNOISE"] = float(val)
        except Exception as e:
            self._write_log_file(repr(e), "RDNOISE")

    def _write_ccd_gain(self) -> None:
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
            self.new_json["EXPTIME"] = 1e-5
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

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._write_READRATE()

    def _write_READRATE(self) -> None:
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
            "SDKVRSN": (r"^\d[.]\d{3}[.]\d{5}[.]\d$", "0.000.00000.0"),
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
            "SITEID": "OPD",
        }

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self.new_json["CYCLIND"] = self.new_json["CYCLIND"] + 1


class General_SPARC4_KWs(General_KWs):
    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder) -> None:
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.regex_expressions["FILENAME"] = (
            r"\d{8}_s4c[1-4]_\d{6}(_[a-z0-9]+)?\.fits",
            "YYYYMMDD_s4c1_000000.fits",
        )
        self.empty_kws["INSTRUME"] = "SPARC4"
        self.empty_kws["TELESCOP"] = "PE160"

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self.new_json["SEQINDEX"] = self.new_json["SEQINDEX"] + 1


class General_ECHARPE_KWs(General_KWs):
    def __init__(self, dict_header_jsons, log_file, hdr_params, csv_folder):
        super().__init__(dict_header_jsons, log_file, hdr_params, csv_folder)
        self.regex_expressions["FILENAME"] = (
            r"\d{8}_ECH_(BLUE|RED)_\d{6}[ozdfts](_[a-z0-9]+)?\.fits",
            "YYYYMMDD_ECH_BLUE_000000o.fits",
        )
        self.empty_kws["TELESCOP"] = "PE160"
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
