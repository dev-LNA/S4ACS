from pathlib import Path

import pandas as pd


class Keywords_Specifications:
    def __init__(self) -> None:
        self.to_bool: list | None = None
        self.to_int: list | None = None
        self.to_float: list | None = None
        self.replace_comma: list | None = None
        self.write_any_val: list | None = None
        self.write_predefined_vals: list | None = None
        self.kws_in_dict: list | None = None
        self.regex: list | None = None
        self.to_bool_w_cond: dict | None = None
        return

    def load_data(self, csv_file: Path) -> None:
        kws_config = pd.read_csv(csv_file).fillna("")
        self.header_keywords = kws_config["Header Keywords"].values

        if "to bool" in kws_config.keys():
            self.to_bool = [val for val in kws_config["to bool"].values if val != ""]

        if "to int" in kws_config.keys():
            self.to_int = [val for val in kws_config["to int"].values if val != ""]

        if "to float" in kws_config.keys():
            self.to_float = [val for val in kws_config["to float"].values if val != ""]

        if "replace comma" in kws_config.keys():
            self.replace_comma = [
                val for val in kws_config["replace comma"].values if val != ""
            ]

        if "write any val" in kws_config.keys():
            self.write_any_val = [
                val for val in kws_config["write any val"].values if val != ""
            ]
        if "write predefined val" in kws_config.keys():
            self.write_predefined_vals = [
                val for val in kws_config["write predefined val"].values if val != ""
            ]

        if "kws in dict" in kws_config.keys():
            self.kws_in_dict = [
                val for val in kws_config["kws in dict"].values if val != ""
            ]

        if "regex strings" in kws_config.keys():
            self.regex = [
                val for val in kws_config["regex strings"].values if val != ""
            ]
        self.to_bool_w_cond = self._get_bool_w_cond_kws(kws_config)

    @staticmethod
    def _get_bool_w_cond_kws(kws_config: pd.DataFrame) -> dict:
        if "to bool w cond" in kws_config.keys():
            return {
                kw: condition.split(";")
                for (kw, condition) in zip(
                    kws_config["to bool w cond"], kws_config["to bool condition"]
                )
                if kw != ""
            }
        return
