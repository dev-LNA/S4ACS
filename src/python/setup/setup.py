from datetime import datetime, timedelta, timezone
from pathlib import Path

import astropy.io.fits as fits

from python.data_types import SPARC4_Applications
from python.header import (
    EICS,
    GUI,
    S4ICS,
    TCS,
    Focuser,
    General_SPARC4_KWs,
    Header,
    Weather_Station,
    iXon_Ultra,
)
from python.header.camera import iKon_L
from python.header.general_kws import General_ECHARPE_KWs
from python.header_content import Header_Content
from python.keywords_specs import Keywords_Specifications
from python.utils import read_config_file


class Header_Class_Setup:
    def __init__(self, instrument: str) -> None:
        self.instrument = instrument
        self._hdr_cnt: Header_Content
        self._hdr_data: SPARC4_Applications
        self._hdr: fits.Header
        self._file_name: Path
        self.acs_config = read_config_file(instrument)
        self.today_str = self._create_today_str()
        self._csv_folder = Path().cwd() / "csv" / self.instrument

    def create_setup(self, hdr_data: tuple, file_name: str) -> None:
        """Create the instances needed by the Header class.

        Args:
            hdr_data (tuple): header data
            file_name (str): image file name
        """
        self._hdr_cnt = Header_Content(self._csv_folder)
        self._hdr_data = SPARC4_Applications.from_tuple(hdr_data)
        self._hdr = fits.Header(self._hdr_cnt.cards)
        self._file_name = self.verify_file_exists(
            self.acs_config.image_path / file_name
        )
        return

    def create_hdr_specs(self, hdr_name: str) -> Keywords_Specifications:
        """Instanciate the class responsible for the header specifications.

        Args:
            hdr_name (str): header class name

        Returns:
            Keywords_Specifications: keywords specifications
        """
        kws_specs = Keywords_Specifications(self._csv_folder, hdr_name)
        kws_specs.load_data()
        return kws_specs

    @staticmethod
    def verify_file_exists(file_path: Path) -> Path:
        if file_path.exists:
            now = datetime.now(timezone.utc)
            now = now.strftime("h%Hm%Ms%Sms%f")
            date, chnl, idx = file_path.name.split("_")
            return file_path.parent / f"{date}_{now}_{chnl}_{idx}"
        return file_path

    @staticmethod
    def _create_today_str() -> str:
        now = datetime.now(timezone.utc)
        if now.hour < 12:
            now -= timedelta(1)
        return now.strftime("%Y%m%d")

    @property
    def hdr_data(self) -> dict:
        return self._hdr_data.model_dump()

    @property
    def hdr_cnt(self) -> Header_Content:
        return self._hdr_cnt

    @property
    def hdr(self) -> fits.Header:
        return self._hdr

    @property
    def file_name(self) -> Path:
        return self._file_name

    @property
    def log_file(self) -> Path:
        return self.acs_config.log_file_path / (self.today_str + "_keywords.log")

    @property
    def csv_folder(self) -> Path:
        return self._csv_folder

    @property
    def header_classes_list(self) -> list[Header]:
        _list: list[type[Header]]
        parameters = (self.hdr_cnt, self.log_file, self.file_name)
        if self.instrument == "sparc4":
            _list = [
                Focuser,
                S4ICS,
                GUI,
                TCS,
                Weather_Station,
                General_SPARC4_KWs,
                iXon_Ultra,
            ]
        elif self.instrument == "echarpe":
            _list = [
                Focuser,
                EICS,
                GUI,
                TCS,
                Weather_Station,
                General_ECHARPE_KWs,
                iKon_L,
            ]
        else:
            raise ValueError(f"Unkown instrument: {self.instrument}")

        return [_cls(self.create_hdr_specs(_cls.name), *parameters) for _cls in _list]
