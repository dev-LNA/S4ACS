import json


def main(file, data, dict_header_jsons) -> str:
    error_json = {"status": False, "code": 0, "source": ""}
    header_jsons = json.loads(dict_header_jsons)

    if file != "20251007_s4c1_000139.fits":
        raise ValueError(f"Wrong file name value: {file}")
    if data[0][0] != 1:
        raise ValueError(f"Wrong data value: {data}")
    for idx, system in enumerate(header_jsons.keys()):
        _json = json.loads(header_jsons[system])
        if _json["code"] != idx + 1:
            raise ValueError(f"Wrong header json value: {header_jsons}")
    return json.dumps(error_json)
