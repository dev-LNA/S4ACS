import json
import re
from datetime import datetime

from astropy.time import Time

from .header import Header


class Focuser(Header):
    name = "FOCUSER"

    def _fix_tfocstat(self) -> None:
        if self.original_hdr_data is None:
            return
        try:
            if self.original_hdr_data["INITIALIZED"] is False:
                self.fixed_data["TFOCSTAT"] = "NONE"
                return
            elif self.original_hdr_data["ISMOVING"] is True:
                self.fixed_data["TFOCSTAT"] = "BUSY"
            elif self.original_hdr_data["ISMOVING"] is False:
                self.fixed_data["TFOCSTAT"] = "READY"
            else:
                self.fixed_data["TFOCSTAT"] = ""
        except Exception as e:
            self._write_log_file(repr(e), "TFOCSTAT")
        return

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._fix_tfocstat()
        return


class Weather_Station(Header):
    name = "WSTATION"

    def fix_header_data(self) -> None:
        if self.original_string is None:
            return
        if "Weather" in self.original_string[:7]:
            self.original_string = self.original_string.replace("Weather", "")


class TCS(Header):
    name = "TCS"

    def __init__(self, log_file, hdr_cnt, csv_folder) -> None:
        super().__init__(log_file, hdr_cnt, csv_folder)
        self.how_to_fix_regex = {
            k: self._fix_coordinates for k in ["RA", "DEC", "TCSHA"]
        }
        self.obstype: str

    def write_header_all_apps(self, header_data: dict) -> None:
        super().write_header_all_apps(header_data)
        self.obstype = json.loads(header_data["GUI"])["OBSTYPE"]

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._write_TCSDATE()
        self.fix_RA_DEC()
        return

    def _write_TCSDATE(self) -> None:
        if self.original_hdr_data is None:
            return
        try:
            for kw in ["DATE", "TIME"]:
                if not isinstance(self.original_hdr_data[kw], str):
                    self._write_log_file(
                        f'Keyword value "{self.original_hdr_data[kw]}" is not an instance of {repr(str)}.',
                        kw,
                    )
                    return
            date, time = self.original_hdr_data["DATE"], self.original_hdr_data["TIME"]
            date = date.split("/")[::-1]
            time = time.split(":")
            tmp = [int(val) for val in date + time]
            tmp[0] += 2000
            tcsdate = Time(datetime(*tmp)).isot  # type: ignore
            self.fixed_data["TCSDATE"] = tcsdate
        except Exception as e:
            self._write_log_file(repr(e), "TCSDATE")

    @staticmethod
    def _fix_coordinates(
        kw_value: str,
    ) -> str:  # está gerando log de erro. tratar melhor
        new_value = kw_value.strip()
        new_value = re.sub(r"^([+-]?\d{1,2})$", r"\1:00:00", new_value)
        new_value = re.sub(r"^([+-]?\d{1,2}):(\d{1,2})$", r"\1:\2:00", new_value)
        h, m, s = new_value.split(":")
        h, m, s = abs(int(h)), abs(int(m)), abs(float(s))
        new_value = f"{h:02}:{m:02}:{s:05.2f}"

        if "-" in kw_value:
            new_value = "-" + new_value
        return new_value

    def fix_RA_DEC(self) -> None:
        for kw in ["RA", "DEC"]:
            try:
                kw_value = self.extracted_data[kw]
                if kw_value == "" and self.obstype in ["ZERO", "FLAT", "DARK"]:
                    new_value = "00:00:00.00"
                    self._write_log_file(
                        f"An empty string was found for the keyword {kw}. As OBSTYPE={self.obstype}, the keyword value was changed to {new_value}",
                        kw,
                    )
                    self.fixed_data[kw] = new_value
            except Exception as e:
                self._write_log_file(repr(e), kw)


class Header_Tester(Header):
    name = "TESTER"

    def __init__(self, log_file, hdr_cnt, csv_folder) -> None:
        super().__init__(log_file, hdr_cnt, csv_folder)
        self.how_to_fix_regex = {"GUIVRSN": self._fix_soft_version}

    @staticmethod
    def _fix_soft_version(kw_value: str) -> str:
        return "v" + kw_value
