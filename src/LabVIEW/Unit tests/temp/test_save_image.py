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
    return json.dumps(error_json)
