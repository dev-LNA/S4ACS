import json
from pathlib import Path

import pandas as pd


class Keywords_Specifications:
    def __init__(self, csv_folder: Path, app_name: str) -> None:
        self.to_bool: list | None = None
        self.to_int: list | None = None
        self.to_float: list | None = None
        self.replace_comma: list | None = None
        self.any_val: list | None = None
        self.predefined_vals: list | None = None

        self.kws_in_dict: list | None = None
        self.dict_w_kws: dict[str, dict]

        self.empty_kws: list | None = None
        self.empty_kws_vals: dict[str, str | int | float]

        self.regex: list | None = None
        self.regex_expressions: dict[str, tuple[str, str]]

        self.to_bool_w_cond: dict | None = None
        self._csv_folder = csv_folder
        self.app_name = app_name
        self.kws_specs = pd.read_csv(
            self._csv_folder / "keywords spec" / f"{self.app_name}.csv"
        ).fillna("")
        return

    @property
    def csv_folder(self) -> Path:
        return self._csv_folder

    def load_data(self) -> None:

        self.keywords = self.kws_specs["Header Keywords"].values

        if "to bool" in self.kws_specs.keys():
            self.to_bool = [
                val for val in self.kws_specs["to bool"].values if val != ""
            ]

        if "to int" in self.kws_specs.keys():
            self.to_int = [val for val in self.kws_specs["to int"].values if val != ""]

        if "to float" in self.kws_specs.keys():
            self.to_float = [
                val for val in self.kws_specs["to float"].values if val != ""
            ]

        if "replace comma" in self.kws_specs.keys():
            self.replace_comma = [
                val for val in self.kws_specs["replace comma"].values if val != ""
            ]

        if "any val" in self.kws_specs.keys():
            self.any_val = [
                val for val in self.kws_specs["any val"].values if val != ""
            ]
        if "predefined val" in self.kws_specs.keys():
            self.predefined_vals = [
                val for val in self.kws_specs["predefined val"].values if val != ""
            ]

        self._get_bool_w_cond_kws()
        self._get_regex_keywords()
        self._get_keywords_in_dict()
        self._get_empty_keywords()

    def _get_bool_w_cond_kws(self) -> dict | None:
        if "to bool w cond" in self.kws_specs.keys():
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
        if "regex" in self.kws_specs.keys():
            self.regex = [val for val in self.kws_specs["regex"].values if val != ""]
            df = pd.read_csv(
                self._csv_folder / "regex expressions" / f"{self.app_name}.csv"
            )
            self.regex_expressions = (
                df
                .set_index("keyword")[["expression", "example"]]
                .apply(tuple, axis=1)
                .to_dict()
            )  # type: ignore

    def _get_keywords_in_dict(self) -> None:
        if "kws in dict" in self.kws_specs.keys():
            self.kws_in_dict = [
                val for val in self.kws_specs["kws in dict"].values if val != ""
            ]
            df = pd.read_csv(
                self._csv_folder / "keywords in dict" / f"{self.app_name}.csv", sep=";"
            )
            df["dict_parsed"] = df["dict"].apply(json.loads)
            self.dict_w_kws = dict(zip(df["keywords"], df["dict_parsed"]))

    def _get_empty_keywords(self) -> None:
        if "empty keywords" in self.kws_specs.keys():
            self.kws_in_dict = [
                val for val in self.kws_specs["empty keywords"].values if val != ""
            ]
            df = pd.read_csv(
                self._csv_folder / "empty keywords" / f"{self.app_name}.csv"
            )
            df["values_parsed"] = df["values"].apply(json.loads)
            self.empty_kws_vals = dict(zip(df["keywords"], df["values_parsed"]))
