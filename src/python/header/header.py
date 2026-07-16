import json
import re
from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Any

import astropy.io.fits as fits

from python.setup import Header_Class_Setup


class Header(ABC):
    kw_types = {"integer": int, "boolean": bool, "float": float, "string": str}
    name = "HEADER"

    def __init__(self, setup: Header_Class_Setup) -> None:

        self.kws_specs = setup.create_hdr_specs(self.name)
        self.hdr_cnt = setup.hdr_cnt
        self.log_file = setup.log_file
        self.file_name = setup.file_name

        self.how_to_fix_regex: dict

        self.header_all_apps: dict
        self.original_string: str | None = None
        self.original_hdr_data: dict | None = None
        self.extracted_data: dict = {}
        self.fixed_data: dict = {k: "" for k in self.kws_specs.keywords}
        self.checked_data: dict = {k: "" for k in self.kws_specs.keywords}

        return

    def write_header_all_apps(self, header_data: dict) -> None:
        self.header_all_apps = header_data

    def get_app_header_data(self) -> None:
        header_data = self.header_all_apps[self.name]
        if header_data == "":
            self._write_log_file("The header data is empty.")
            return
        self.original_string = header_data

    def fix_header_data(self) -> None:
        pass

    def load_json(self) -> None:
        if self.original_string is None:
            return
        try:
            _json: dict[str, Any] = json.loads(self.original_string)
            self.original_hdr_data = {k.upper(): v for k, v in _json.items()}
        except Exception as e:
            self._write_log_file(
                f"There was an error when loading the JSON data --> {self.original_string}."
                + repr(e)
            )

    def extract_data(self) -> None:
        if self.original_hdr_data is None:
            return

        for hdr_kw in self.kws_specs.keywords:
            try:
                kw = hdr_kw
                expected_name = self.hdr_cnt.expected_kw_names[hdr_kw]
                if expected_name != "":
                    kw = expected_name
                self.extracted_data[hdr_kw] = self.original_hdr_data[kw]
            except Exception as e:
                self._write_log_file(repr(e), hdr_kw)

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

    def _write_log_file(self, message: str, keyword: str | None = None) -> None:
        now = str(datetime.now())
        _str = now + " - " + f"FILENAME= {self.file_name}, " + f"SUB-SYTEM={self.name}"
        if keyword is not None:
            _str += ", KEYWORD={keyword}"
        _str += " - " + message + "\n"
        with open(self.log_file, "a") as file:
            file.write(_str)

    # ========================= Convertions =========================

    def _convert_to_float(self) -> None:
        if self.kws_specs.to_float is None:
            return
        for kw in self.kws_specs.to_float:
            try:
                self.fixed_data[kw] = float(self.extracted_data[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_int(self) -> None:
        if self.kws_specs.to_int is None:
            return
        for kw in self.kws_specs.to_int:
            try:
                self.fixed_data[kw] = int(self.extracted_data[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_boolean(self) -> None:
        if self.kws_specs.to_bool is None:
            return
        for kw in self.kws_specs.to_bool:
            try:
                self.fixed_data[kw] = bool(self.extracted_data[kw])
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _convert_to_bool_with_condition(self) -> None:
        if self.kws_specs.to_bool_w_cond is None:
            return
        for kw, (off, on) in self.kws_specs.to_bool_w_cond.items():
            try:
                val = self.extracted_data[kw]
                if val == off:
                    self.fixed_data[kw] = False
                elif val == on:
                    self.fixed_data[kw] = True
                else:
                    self._write_log_file(f"Invalid keyword value: {val}", kw)
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _replace_comma(self) -> None:
        if self.kws_specs.replace_comma is None:
            return
        for kw in self.kws_specs.replace_comma:
            try:
                self._search_unwanted_kw(kw, ",")
                self.fixed_data[kw] = self.extracted_data[kw].replace(",", ".")
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _verify_regex(self) -> None:
        if self.kws_specs.regex is None:
            return
        for kw in self.kws_specs.regex:
            try:
                kw_value = self.extracted_data[kw]
                regex_expr, ex_val = self.kws_specs.regex_expressions[kw]
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
                    continue
                self._write_log_file("Trying to fix...", kw)
                self._fix_regex_keyword(kw)
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _fix_regex_keyword(self, kw) -> None:
        try:
            kw_value = self.extracted_data[kw]
            regex_expr, _ = self.kws_specs.regex_expressions[kw]
            if kw not in self.how_to_fix_regex.keys():
                self._write_log_file(
                    "The method to fix this keyword was not found.", kw
                )
                return
            new_value = self.how_to_fix_regex[kw](kw_value)
            if re.match(regex_expr, new_value) is None:
                self._write_log_file(
                    f"The provided value {kw_value} could not be fixed.", kw
                )
                return
            self.fixed_data[kw] = new_value
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return

    def _replace_empty_kws(self) -> None:
        if self.kws_specs.empty_kws is None:
            return
        for kw, val in self.kws_specs.empty_kws_vals.items():
            try:
                self.fixed_data[kw] = val
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _write_any_value(self) -> None:
        if self.kws_specs.any_val is None:
            return
        for kw in self.kws_specs.any_val:
            try:
                self.fixed_data[kw] = self.extracted_data[kw]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _write_predefined_value(self) -> None:
        if self.kws_specs.predefined_vals is None:
            return
        for kw in self.kws_specs.predefined_vals:
            try:
                _list = self.hdr_cnt.allowed_kw_values[kw]
                val = self.extracted_data[kw]
                if val not in _list:
                    self._write_log_file(
                        f"The provided value should be in the expected values list {_list}. {val} was found.",
                        kw,
                    )
                    return
                self.fixed_data[kw] = self.extracted_data[kw]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _kw_in_dict(self) -> None:
        if self.kws_specs.kws_in_dict is None:
            return
        for kw, val in self.kws_specs.dict_w_kws.items():
            try:
                data = self.extracted_data[kw]
                self.fixed_data[kw] = val[data]
            except Exception as e:
                self._write_log_file(repr(e), kw)

    def _search_unwanted_kw(self, kw, _str) -> None:
        if _str in self.extracted_data[kw]:
            self._write_log_file(
                f"An unexpected string was found in the keyword value: {_str}", kw
            )

    # ===================== Validation ===================================

    def validate_info(self) -> None:
        self._check_type()
        self._check_allowed_values()
        return

    def _check_type(self) -> None:
        for hdr_kw in self.kws_specs.keywords:
            try:
                val = self.fixed_data[hdr_kw]
                _type = self.hdr_cnt.keyword_types[hdr_kw]
                if not isinstance(val, self.kw_types[_type]):
                    self._write_log_file(
                        f'Keyword value "{val}" is not an instance of {repr(_type)}.',
                        hdr_kw,
                    )
                    return
                self.checked_data[hdr_kw] = val
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
        val = self.fixed_data[hdr_kw]
        a_values = self.hdr_cnt.allowed_kw_values[hdr_kw]
        min, *max = a_values
        if not min <= val <= max[-1]:
            self._write_log_file(
                f'The provided keyword value is out of range {a_values}. "{val}" was found.',
                hdr_kw,
            )
            return
        self.checked_data[hdr_kw] = val
        return

    def _check_string_in_allowed_values(self, hdr_kw) -> None:
        val = self.fixed_data[hdr_kw]
        a_values = self.hdr_cnt.allowed_kw_values[hdr_kw]
        if val not in a_values and a_values != "":
            self._write_log_file(
                f'The expected values for this keyword are {a_values}. "{val}" was found.',
                hdr_kw,
            )
            return
        self.checked_data[hdr_kw] = val
        return

    def fill_image_header(self, hdr: fits.Header) -> fits.Header:
        for kw, val in self.checked_data.items():
            try:
                hdr[kw] = val
            except Exception as e:
                self._write_log_file(repr(e), kw)
        return hdr
