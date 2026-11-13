import json
from ast import literal_eval
from pathlib import Path
from typing import Any, Union

import pandas as pd


class Keywords_Specifications:
    def __init__(self, csv_folder: Path, app_name: str) -> None:
        self.to_bool: Union[list, None] = None
        self.to_int: Union[list, None] = None
        self.to_float: Union[list, None] = None
        self.replace_comma: Union[list, None] = None
        self.any_val: Union[list, None] = None
        self.predefined_vals: Union[list, None] = None
        self.to_bool_w_cond: Union[dict, None] = None
        self.deducted_keywords: Union[list, None] = None

        self.kws_in_dict: Union[list, None] = None
        self.empty_kws: Union[list, None] = None
        self.regex: Union[list, None] = None

        self.dict_w_kws: dict[str, dict]
        self.empty_kws_vals: dict[str, Union[str, int, float]]
        self.regex_expressions: dict[str, tuple[str, str]]

        self._csv_folder = csv_folder
        self.app_name = app_name
        self.kws_specs = pd.read_csv(
            self._csv_folder / "keywords spec" / f"{self.app_name}.csv"
        ).fillna("")

    @property
    def csv_folder(self) -> Path:
        return self._csv_folder

    @property
    def all_keywords(self) -> list:
        _list = self.keywords.copy()
        if self.deducted_keywords is not None:
            _list += self.deducted_keywords.copy()
        if self.empty_kws is not None:
            _list += self.empty_kws.copy()
        return _list

    def load_data(self) -> None:

        self.keywords = [
            val for val in self.kws_specs["Header Keywords"].values if val != ""
        ]

        if "to bool" in self.kws_specs:
            self.to_bool = [
                val for val in self.kws_specs["to bool"].values if val != ""
            ]

        if "to int" in self.kws_specs:
            self.to_int = [val for val in self.kws_specs["to int"].values if val != ""]

        if "to float" in self.kws_specs:
            self.to_float = [
                val for val in self.kws_specs["to float"].values if val != ""
            ]

        if "replace comma" in self.kws_specs:
            self.replace_comma = [
                val for val in self.kws_specs["replace comma"].values if val != ""
            ]

        if "any val" in self.kws_specs:
            self.any_val = [
                val for val in self.kws_specs["any val"].values if val != ""
            ]
        if "predefined val" in self.kws_specs:
            self.predefined_vals = [
                val for val in self.kws_specs["predefined val"].values if val != ""
            ]

        if "deducted kws" in self.kws_specs:
            self.deducted_keywords = [
                val for val in self.kws_specs["deducted kws"].values if val != ""
            ]

        self._get_bool_w_cond_kws()
        self._get_regex_keywords()
        self._get_keywords_in_dict()
        self._get_empty_keywords()

    def _get_bool_w_cond_kws(self) -> Union[dict, None]:
        if "to bool w cond" in self.kws_specs:
            self.to_bool_w_cond = {
                kw: condition.split(";")
                for (kw, condition) in zip(
                    self.kws_specs["to bool w cond"],
                    self.kws_specs["to bool condition"],
                )
                if kw != ""
            }
        return

    def _get_regex_keywords(self) -> None:
        if "regex" in self.kws_specs:
            self.regex = [val for val in self.kws_specs["regex"].values if val != ""]
            df = pd.read_csv(
                self._csv_folder / "regex expressions" / f"{self.app_name}.csv", sep=";"
            )
            self.regex_expressions = (
                df
                .set_index("keyword")[["expression", "example"]]
                .apply(tuple, axis=1)
                .to_dict()
            )  # type: ignore

    def _get_keywords_in_dict(self) -> None:
        if "kws in dict" in self.kws_specs:
            self.kws_in_dict = [
                val for val in self.kws_specs["kws in dict"].values if val != ""
            ]
            df = pd.read_csv(
                self._csv_folder / "keywords in dict" / f"{self.app_name}.csv", sep=";"
            )
            df["dict_parsed"] = df["dict"].apply(
                json.loads, object_hook=self.convert_keys_int
            )
            self.dict_w_kws = dict(zip(df["keyword"], df["dict_parsed"]))

    def _get_empty_keywords(self) -> None:
        if "empty keywords" in self.kws_specs:
            self.empty_kws = [
                val for val in self.kws_specs["empty keywords"].values if val != ""
            ]
            df = pd.read_csv(
                self._csv_folder / "empty keywords" / f"{self.app_name}.csv"
            )
            df["values"] = df["values"].apply(self.loads)
            self.empty_kws_vals = dict(zip(df["keyword"], df["values"]))

    @staticmethod
    def convert_keys_int(d) -> "dict[Union[int, Any], Any]":
        return {int(k) if k.isdigit() else k: v for k, v in d.items()}

    @staticmethod
    def converte_type(value) -> Union[Any, str]:
        try:
            return literal_eval(value)
        except SyntaxError:
            return value
        except ValueError:
            return value

    @staticmethod
    def loads(valor) -> Any:
        try:
            return json.loads(valor)
        except json.JSONDecodeError:
            return valor
        except TypeError:
            return valor

    def validate_specifications(self) -> None:
        if self.deducted_keywords is None:
            return
        for kw in self.deducted_keywords:
            if kw in self.keywords:
                raise ValueError(
                    f"Keyword {kw} should not be in the main keywords list."
                )
