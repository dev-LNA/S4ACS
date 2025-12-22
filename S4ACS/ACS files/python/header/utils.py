from dataclasses import dataclass
from os.path import dirname, join, realpath

import numpy as np
import pandas as pd


@dataclass
class Header_Parameters:

    def __init__(self, csv_folder: str) -> None:
        self.csv_folder = csv_folder
        self.read_hdr_ctnt_csv()
        self.keywords = [kw for kw in self.hdr_cnt["Keyword"]]
        self.comments = [comment for comment in self.hdr_cnt["Comment"]]
        self.get_gain_values()
        self.get_read_noise_values()
        self.get_expected_kw_names()
        self.get_keyword_types()
        self.get_allowed_kw_vals()

        return

    def read_hdr_ctnt_csv(self) -> None:
        csv_path = join(self.csv_folder, "header_content.csv")
        self.hdr_cnt = pd.read_csv(csv_path, delimiter=";", keep_default_na=False)
        return

    def get_gain_values(self) -> None:
        csv_path = join(self.csv_folder, "preamp_gains.csv")
        self.gain_values = pd.read_csv(csv_path)
        return

    def get_read_noise_values(self) -> None:
        csv_path = join(self.csv_folder, "read_noises.csv")
        self.rd_values = pd.read_csv(csv_path)
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


# base_folder = join(dirname(realpath(__file__)), "..", "csvs")
# csv_folder = join(dirname(realpath(__file__)), "..", "csvs", "sparc4")
# sparc4_hdr_data_class = Header_Parameters(csv_folder)
