import json

sub_systems = [
    "CCD",
    "S4GUI",
    "S4ICS",
    "TCS",
    "FOCUSER",
    "WSTATION",
    "GENERAL KW",
]


def main(night_dir, file, data, tuple_header_jsons, log_file):
    error_json = {"status": False, "code": 0, "source": ""}
    header_jsons = {k: v for (k, v) in zip(sub_systems, tuple_header_jsons)}

    if night_dir != "C://":
        raise ValueError(f"Wrong night directory value: {night_dir}")
    if file != "20251007_s4c1_000139.fits":
        raise ValueError(f"Wrong file name value: {file}")
    if data[0][0] != 1:
        raise ValueError(f"Wrong data value: {data}")
    for idx, system in enumerate(header_jsons.keys()):
        _json = json.loads(header_jsons[system])
        if _json["code"] != idx + 1:
            raise ValueError(f"Wrong header json value: {header_jsons}")
    if log_file != "E://":
        raise ValueError(f"Wrong log file path value: {log_file}")
    return json.dumps(error_json)
