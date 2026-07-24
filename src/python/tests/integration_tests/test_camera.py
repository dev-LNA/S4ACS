import json
import unittest

from header_formatter.header import (
    GUI,
    S4ICS,
    TCS,
    Focuser,
    General_SPARC4_KWs,
    Weather_Station,
    iXon_Ultra,
)
from header_formatter.setup import Header_Class_Setup
from header_formatter.utils import (
    WS_json,
    ccd_kw,
    focuser_json,
    ics_kw,
    s4gui_json,
    tcs_json,
)


class Test_Everything(unittest.TestCase):
    def setUp(self) -> None:

        self._hdr_data = dict.fromkeys(
            ["CCD", "GUI", "ICS", "FOCUSER", "WSTATION", "GENERAL KW", "TCS"], "{}"
        )
        self._hdr_data["CCD"] = json.dumps(ccd_kw)
        self._hdr_data["GUI"] = json.dumps(s4gui_json)
        self._hdr_data["WSTATION"] = json.dumps(WS_json)
        self._hdr_data["FOCUSER"] = json.dumps(focuser_json)
        self._hdr_data["ICS"] = json.dumps(ics_kw)
        self._hdr_data["TCS"] = json.dumps(tcs_json)

        setup = Header_Class_Setup("sparc4")
        self.hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
            json.dumps(self._hdr_data), "00000000_s4c1_000001.fits"
        )

        for obj in [
            Focuser,
            S4ICS,
            GUI,
            TCS,
            Weather_Station,
            General_SPARC4_KWs,
            iXon_Ultra,
        ]:
            kws_specs = setup.create_hdr_specs(obj.name)
            obj = obj(kws_specs, hdr_cnt, log_file, file_name)
            obj.write_header_all_apps(hdr_data)
            obj.get_app_header_data()
            obj.fix_original_string()
            obj.load_json()
            obj.fix_original_hdr_data()
            obj.extract_data()
            obj.fix_keywords()
            obj.fix_remainder_keywords()
            obj.check_kws_types()
            obj.check_allowed_values()
            self.hdr = obj.fill_image_header(self.hdr)

    def test_fill_image_header(self) -> None:
        assert self.hdr["SHUTTER"] == "Closed"
        assert self.hdr["VCLKAMP"] == "Normal"
        assert self.hdr["NFRAMES"] == 1
        assert self.hdr["DATE-OBS"] == "2026-07-23T18:47:59.719488"
        assert self.hdr["UTDATE"] == "2026-07-23"
        assert self.hdr["UTTIME"] == "18:47:59.719488"
        assert self.hdr["CCDTEMP"] == 0
        assert self.hdr["TEMPST"] == "TEMPERATURE_OFF"
        assert self.hdr["TGTEMP"] == 0
        assert self.hdr["COOLER"] is False
        assert self.hdr["NAXIS1"] == 1024
        assert self.hdr["NAXIS2"] == 1024
        assert self.hdr["GAIN"] == 3.37
        assert self.hdr["RDNOISE"] == 6.66
