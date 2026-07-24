import json
import unittest

from header_formatter.header import CCD, iXon_Ultra
from header_formatter.setup import Header_Class_Setup


class Test_Camera(unittest.TestCase):
    def setUp(self) -> None:
        self._dict_data = {
            "FILENAME": "00000000_s4c1_000000.fits",
            "READRATE": 1,
            "PREAMP": 1,
            "FRAMEIND": 0,
            "EXPTIME": 9.9999999e-6,
            "VBIN": 1,
            "INITLIN": 1,
            "INITCOL": 1,
            "FINALLIN": 1024,
            "FINALCOL": 1024,
            "HBIN": 1,
            "CCDSERN": 9914,
            "TRIGGER": 0,
            "ACQMODE": 3,
            "SHUTTER": 2,
            "VCLKAMP": 0,
            "NFRAMES": 1,
            "DATE-OBS": "0000-00-00T00:00:00.000000",
            "UTDATE": "0000-00-00",
            "UTTIME": "00:00:00.000000",
            "CCDTEMP": -30,
            "TEMPST": "TEMPERATURE_STABILIZED",
            "TGTEMP": -30,
            "COOLER": True,
            "VSHIFT": 3,
            "EMGAIN": 2,
            "EMMODE": 1,
            "FRAMETRF": True,
        }

        self._hdr_data = dict.fromkeys(
            ["CCD", "GUI", "ICS", "FOCUSER", "WSTATION", "GENERAL KW", "TCS"], "{}"
        )
        self._hdr_data["CCD"] = json.dumps(self._dict_data)
        setup = Header_Class_Setup("sparc4")
        self.hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
            json.dumps(self._hdr_data), "00000000_s4c1_000001.fits"
        )
        kws_specs = setup.create_hdr_specs(CCD.name)
        self.tester = CCD(kws_specs, hdr_cnt, log_file, file_name)
        self.tester.write_header_all_apps(hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        self.tester.fix_keywords()
        self.tester.fix_remainder_keywords()

    def test_idx_tab(self) -> None:
        assert self.tester.idx_tab == 3

    def test_write_read_noise(self) -> None:
        assert self.tester.fixed_data["RDNOISE"] == 65.5

    def test_write_gain(self) -> None:
        assert self.tester.fixed_data["GAIN"] == 4.39

    def test_fix_exp_time(self) -> None:
        assert self.tester.fixed_data["EXPTIME"] == 1e-5

    def test_calc_NAXIS1(self) -> None:
        assert self.tester.fixed_data["NAXIS1"] == 1024

    def test_calc_NAXIS2(self) -> None:
        assert self.tester.fixed_data["NAXIS2"] == 1024

    def test_fix_keywords(self) -> None:
        assert self.tester.fixed_data["SHUTTER"] == "Closed"
        assert self.tester.fixed_data["VCLKAMP"] == "Normal"
        assert self.tester.fixed_data["NFRAMES"] == 1
        assert self.tester.fixed_data["DATE-OBS"] == "0000-00-00T00:00:00.000000"
        assert self.tester.fixed_data["UTDATE"] == "0000-00-00"
        assert self.tester.fixed_data["UTTIME"] == "00:00:00.000000"
        assert self.tester.fixed_data["CCDTEMP"] == -30
        assert self.tester.fixed_data["TEMPST"] == "TEMPERATURE_STABILIZED"
        assert self.tester.fixed_data["TGTEMP"] == -30
        assert self.tester.fixed_data["COOLER"] is True

    def test_fix_remainder_keywords(self) -> None:
        assert self.tester.fixed_data["NAXIS1"] == 1024
        assert self.tester.fixed_data["NAXIS2"] == 1024
        assert self.tester.fixed_data["GAIN"] == 4.39
        assert self.tester.fixed_data["RDNOISE"] == 65.5


class Test_iXon_Ultra(unittest.TestCase):
    def setUp(self) -> None:
        self._dict_data = {
            "FILENAME": "00000000_s4c1_000000.fits",
            "READRATE": 1,
            "PREAMP": 1,
            "FRAMEIND": 0,
            "EXPTIME": 9.9999999e-6,
            "VBIN": 1,
            "INITLIN": 1,
            "INITCOL": 1,
            "FINALLIN": 1024,
            "FINALCOL": 1024,
            "HBIN": 1,
            "CCDSERN": 9914,
            "TRIGGER": 0,
            "ACQMODE": 3,
            "SHUTTER": 2,
            "VCLKAMP": 0,
            "NFRAMES": 1,
            "DATE-OBS": "0000-00-00T00:00:00.000000",
            "UTDATE": "0000-00-00",
            "UTTIME": "00:00:00.000000",
            "CCDTEMP": -30,
            "TEMPST": "TEMPERATURE_STABILIZED",
            "TGTEMP": -30,
            "COOLER": True,
            "EMMODE": 1,
            "VSHIFT": 3,
            "EMGAIN": 2,
            "FRAMETRF": True,
        }

        self._hdr_data = dict.fromkeys(
            ["CCD", "GUI", "ICS", "FOCUSER", "WSTATION", "GENERAL KW", "TCS"], "{}"
        )
        self._hdr_data["CCD"] = json.dumps(self._dict_data)
        setup = Header_Class_Setup("sparc4")
        self.hdr, hdr_data, hdr_cnt, log_file, file_name = setup.create_setup(
            json.dumps(self._hdr_data), "00000000_s4c1_000001.fits"
        )

        kws_specs = setup.create_hdr_specs(iXon_Ultra.name)

        self.tester = iXon_Ultra(kws_specs, hdr_cnt, log_file, file_name)
        self.tester.write_header_all_apps(hdr_data)
        self.tester.get_app_header_data()
        self.tester.fix_original_string()
        self.tester.load_json()
        self.tester.fix_original_hdr_data()
        self.tester.extract_data()
        self.tester.fix_keywords()
        self.tester.fix_remainder_keywords()

    def test_init(self) -> None:
        assert self.tester.kws_specs.dict_w_kws["VSHIFT"] == [0.6, 1.13, 2.2, 4.33]
        assert self.tester.kws_specs.dict_w_kws["PREAMP"] == ["Gain 1", "Gain 2"]
        assert self.tester.kws_specs.dict_w_kws["EMMODE"] == [
            "Electron Multiplying",
            "Conventional",
        ]
        assert self.tester.kws_specs.dict_w_kws["READRATE"] == {
            0: [30.0, 20.0, 10.0, 1.0],
            1: [1.0, 0.1],
        }

    def test_find_idx_tab(self) -> None:
        assert self.tester.idx_tab == 11

    def test_write_readrate(self) -> None:
        assert self.tester.fixed_data["READRATE"] == 0.1

    def test_fill_image_header(self) -> None:
        self.tester.check_kws_types()
        self.tester.check_allowed_values()
        hdr = self.tester.fill_image_header(self.hdr)
        assert hdr["SHUTTER"] == "Closed"
        assert hdr["VCLKAMP"] == "Normal"
        assert hdr["NFRAMES"] == 1
        assert hdr["DATE-OBS"] == "0000-00-00T00:00:00.000000"
        assert hdr["UTDATE"] == "0000-00-00"
        assert hdr["UTTIME"] == "00:00:00.000000"
        assert hdr["CCDTEMP"] == -30
        assert hdr["TEMPST"] == "TEMPERATURE_STABILIZED"
        assert hdr["TGTEMP"] == -30
        assert hdr["COOLER"] is True
        assert hdr["NAXIS1"] == 1024
        assert hdr["NAXIS2"] == 1024
        assert hdr["GAIN"] == 0.8
        assert hdr["RDNOISE"] == 3.47
        assert hdr["VSHIFT"] == 4.33
