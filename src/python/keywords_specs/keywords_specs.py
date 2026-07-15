from pathlib import Path

import pandas as pd


class Keywords_Specifications:
    def __init__(self) -> None:
        self.to_bool: list | None = None
        self.to_int: list | None = None
        self.to_float: list | None = None
        self.replace_comma: list | None = None
        self.any_val: list | None = None
        self.predefined_vals: list | None = None
        self.kws_in_dict: list | None = None
        self.regex: list | None = None
        self.to_bool_w_cond: dict | None = None
        return

    def load_data(self, csv_file: Path) -> None:
        kws_specs = pd.read_csv(csv_file).fillna("")
        self.keywords = kws_specs["Header Keywords"].values

        if "to bool" in kws_specs.keys():
            self.to_bool = [val for val in kws_specs["to bool"].values if val != ""]

        if "to int" in kws_specs.keys():
            self.to_int = [val for val in kws_specs["to int"].values if val != ""]

        if "to float" in kws_specs.keys():
            self.to_float = [val for val in kws_specs["to float"].values if val != ""]

        if "replace comma" in kws_specs.keys():
            self.replace_comma = [
                val for val in kws_specs["replace comma"].values if val != ""
            ]

        if "any val" in kws_specs.keys():
            self.any_val = [val for val in kws_specs["any val"].values if val != ""]
        if "predefined val" in kws_specs.keys():
            self.predefined_vals = [
                val for val in kws_specs["predefined val"].values if val != ""
            ]

        if "kws in dict" in kws_specs.keys():
            self.kws_in_dict = [
                val for val in kws_specs["kws in dict"].values if val != ""
            ]

        if "regex" in kws_specs.keys():
            self.regex = [val for val in kws_specs["regex"].values if val != ""]
        self.to_bool_w_cond = self._get_bool_w_cond_kws(kws_specs)

    @staticmethod
    def _get_bool_w_cond_kws(kws_specs: pd.DataFrame) -> dict | None:
        if "to bool w cond" in kws_specs.keys():
            return {
                kw: condition.split(";")
                for (kw, condition) in zip(
                    kws_specs["to bool w cond"], kws_specs["to bool condition"]
                )
                if kw != ""
            }
        return
