import json
import re
from abc import ABC
from datetime import datetime
from pathlib import Path

import astropy.io.fits as fits

from python.header_content import Header_Content
from python.keywords_specs import Keywords_Specifications


class Header(ABC):
    kw_types = {"integer": int, "boolean": bool, "float": float, "string": str}
    sub_system = "HEADER"

    def __init__(
        self,
        dict_header_jsons: dict,
        log_file: str,
        hdr_cnt: Header_Content,
        csv_folder: Path,
    ) -> None:
        self.empty_kws: dict | None = None
        self.new_json = None
        self.how_to_fix_regex = None
        self.regex_expressions = None
        self.log_file = log_file
        self.hdr_cnt = hdr_cnt
        self.json_string = dict_header_jsons[self.sub_system]
        self.csv_folder = csv_folder
        self.filename = json.loads(dict_header_jsons["CCD"])["FILENAME"]

        self.original_json = self._load_json()
        self.kws_specs: Keywords_Specifications = Keywords_Specifications()
        self.kws_specs.load_data(
            csv_folder / "keywords spec" / f"{self.sub_system}.csv"
        )

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

    def extract_info(self) -> None:
        new_json = {}
        for hdr_kw in self.kws_specs.keywords:
            try:
                json_kw = hdr_kw
                expected_name = self.hdr_cnt.expected_kw_names[hdr_kw]
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

    def _check_type(self) -> None:
        for hdr_kw in self.kws_specs.keywords:
            try:
                val = self.new_json[hdr_kw]
                _type = self.hdr_cnt.keyword_types[hdr_kw]
                if not isinstance(val, self.kw_types[_type]):
                    self.new_json[hdr_kw] = ""
                    self._write_log_file(
                        f'Keyword value "{val}" is not an instance of {repr(_type)}.',
                        hdr_kw,
                    )
            except Exception as e:
                self._write_log_file(repr(e), hdr_kw)

    def _check_allowed_values(self) -> None:
        for hdr_kw in self.kws_specs.keywords:
            try:
                _type = self.hdr_cnt.keyword_types[hdr_kw]
                if _type in ["integer", "float"]:
                    self._check_number_in_range(hdr_kw)
                elif _type == "string":
                    self._check_string_in_allowed_values(hdr_kw)
            except Exception as e:
                self._write_log_file(repr(e), hdr_kw)

        return

    def _check_number_in_range(self, hdr_kw) -> None:
        val = self.new_json[hdr_kw]
        a_values = self.hdr_cnt.allowed_kw_values[hdr_kw]
        min, *max = a_values
        if not min <= val <= max[-1]:
            self.new_json[hdr_kw] = ""
            self._write_log_file(
                f'The provided keyword value is out of range {a_values}. "{val}" was found.',
                hdr_kw,
            )
        return

    def _check_string_in_allowed_values(self, hdr_kw) -> None:
        val = self.new_json[hdr_kw]
        a_values = self.hdr_cnt.allowed_kw_values[hdr_kw]
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

    def fix_keywords(self) -> None:
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

    def _write_log_file(self, message, keyword) -> None:
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
        if self.kws_specs.to_float is None:
            return
        for kw in self.kws_specs.to_float:
            try:
                self.new_json[kw] = float(self.new_json[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_int(self) -> None:
        if self.kws_specs.to_int is None:
            return
        for kw in self.kws_specs.to_int:
            try:
                self.new_json[kw] = int(self.new_json[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_boolean(self) -> None:
        if self.kws_specs.to_bool is None:
            return
        for kw in self.kws_specs.to_bool:
            try:
                self.new_json[kw] = bool(self.new_json[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_bool_with_condition(self) -> None:
        if self.kws_specs.to_bool_w_cond is None:
            return
        for kw, (off, on) in self.kws_specs.to_bool_w_cond.items():
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
        if self.kws_specs.replace_comma is None:
            return
        for kw in self.kws_specs.replace_comma:
            try:
                self._search_unwanted_kw(kw, ",")
                self.new_json[kw] = self.new_json[kw].replace(",", ".")
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _verify_regex(self) -> None:
        if self.kws_specs.regex is None:
            return
        for kw in self.kws_specs.regex:
            try:
                kw_value = self.new_json[kw]
                regex_expr, ex_val = self.regex_expressions[kw]
                if re.match(regex_expr, kw_value) is not None:
                    continue
                self._write_log_file(
                    f"The provided value for the keyword {kw} '{kw_value}' does not match the expected format {ex_val}.",
                    kw,
                )
                if self.how_to_fix_regex is None:
                    self._write_log_file(
                        "The method to fix this keyword was not implemented.", kw
                    )
                    self.new_json[kw] = ""
                    continue
                self._write_log_file("Trying to fix...", kw)
                self._fix_regex_keyword(kw)
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _fix_regex_keyword(self, kw) -> None:
        try:
            kw_value = self.new_json[kw]
            regex_expr, _ = self.regex_expressions[kw]
            if kw not in self.how_to_fix_regex.keys():
                self.new_json[kw] = ""
                self._write_log_file(
                    "The method to fix this keyword was not found.", kw
                )
                return
            new_value = self.how_to_fix_regex[kw](kw_value)
            if re.match(regex_expr, new_value) is None:
                self._write_log_file(
                    f"The provided value {kw_value} could not be fixed.", kw
                )
            self.new_json[kw] = new_value
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return

    def _replace_empty_kws(self) -> None:
        if self.empty_kws is None:
            return
        for kw, val in self.empty_kws.items():
            try:
                self.new_json[kw] = val
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _write_any_value(self) -> None:
        if self.kws_specs.write_any_val is None:
            return
        for kw in self.kws_specs.write_any_val:
            try:
                self.new_json[kw] = self.new_json[kw]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _write_predefined_value(self) -> None:
        if self.kws_specs.write_predefined_vals is None:
            return
        for kw in self.kws_specs.write_predefined_vals:
            try:
                _list = self.hdr_cnt.allowed_kw_values[kw]
                val = self.new_json[kw]
                if val not in _list:
                    self._write_log_file(
                        f"The provided value should be in the expected values list {_list}. {val} was found.",
                        kw,
                    )

            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _kw_in_dict(self) -> None:
        if self.kws_specs.kws_in_dict is None:
            return
        for kw in self.kws_specs.kws_in_dict:
            try:
                val = self.new_json[kw]
                self.new_json[kw] = self.dict_w_kws[kw][val]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _search_unwanted_kw(self, kw, _str) -> None:
        if _str in self.new_json[kw]:
            self._write_log_file(
                f"An unexpected string was found in the keyword value: {_str}", kw
            )
