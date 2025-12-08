import math
import os

import numpy as np
import pandas as pd

cwd = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.join(cwd, "..")
csv_path = os.path.join(base_path, "csvs", "header_content.csv")
ss = pd.read_csv(csv_path, delimiter=";", keep_default_na=False)
cards = [
    (keyword, "", comment) for keyword, comment in zip(ss["Keyword"], ss["Comment"])
]

keyword_types = {k: v for (k, v) in zip(ss["Keyword"], ss["Type"])}
expected_kw_names = {k: v for (k, v) in zip(ss["Keyword"], ss["Expected name"])}
gains = pd.read_csv(os.path.join(base_path, "csvs", "preamp_gains.csv"))
read_noise = pd.read_csv(os.path.join(base_path, "csvs", "read_noises.csv"))

allowed_kw_values = {k: v for (k, v) in zip(ss["Keyword"], ss["Allowed values"])}
for kw, values in allowed_kw_values.items():
    if values != "":
        val = allowed_kw_values[kw].split(",")
        if "inf" in val:
            val[val.index("inf")] = np.inf
        if keyword_types[kw] in ["integer", "float"]:
            val = [float(v) for v in val]
        if keyword_types[kw] == "boolean":
            val = [v == "true" for v in val]
        allowed_kw_values[kw] = val
