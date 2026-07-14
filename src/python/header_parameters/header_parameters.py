from pathlib import Path

import numpy as np
import pandas as pd


class Header_Parameters:
    def __init__(self, csv_folder: str) -> None:
        self.csv_folder = Path(csv_folder)
        self.read_hdr_ctnt_csv()
        self.keywords = [kw for kw in self.hdr_cnt["Keyword"]]
        self.comments = [comment for comment in self.hdr_cnt["Comment"]]
        self.get_expected_kw_names()
        self.get_keyword_types()
        self.get_allowed_kw_vals()

        return

    def read_hdr_ctnt_csv(self) -> None:
        self.hdr_cnt = pd.read_csv(
            self.csv_folder / "header_content.csv", delimiter=";", keep_default_na=False
        )
        return

    def get_keyword_types(self) -> None:
        self.keyword_types = {
            k: v for (k, v) in zip(self.hdr_cnt["Keyword"], self.hdr_cnt["Type"])
        }
        return

    def get_expected_kw_names(self) -> None:
        self.expected_kw_names = {
            k: v
            for (k, v) in zip(self.hdr_cnt["Keyword"], self.hdr_cnt["Expected name"])
        }

    def get_allowed_kw_vals(self) -> None:
        allowed_kw_values = {
            k: v
            for (k, v) in zip(self.hdr_cnt["Keyword"], self.hdr_cnt["Allowed values"])
        }
        for kw, values in allowed_kw_values.items():
            if values != "":
                val = allowed_kw_values[kw].split(",")
                if "inf" in val:
                    val[val.index("inf")] = np.inf
                if self.keyword_types[kw] in ["integer", "float"]:
                    val = [float(v) for v in val]
                if self.keyword_types[kw] == "boolean":
                    val = [v == "true" for v in val]
                allowed_kw_values[kw] = val
        self.allowed_kw_values = allowed_kw_values
        return

    @property
    def cards(self) -> list:
        return [
            (kw, "", comment) for (kw, comment) in zip(self.keywords, self.comments)
        ]


def get_gain_values(self) -> None:
    self.gain_values = pd.read_csv(self.csv_folder / "preamp_gains.csv")
    return


def get_read_noise_values(self) -> None:
    self.rd_values = pd.read_csv(self.csv_folder / "read_noises.csv")
    return
