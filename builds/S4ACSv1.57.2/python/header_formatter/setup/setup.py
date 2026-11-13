from datetime import datetime, timedelta, timezone
from pathlib import Path

from astropy.io import fits
from header_formatter.data_types import External_Applications, Test_Applications
from header_formatter.header_content import Header_Content
from header_formatter.keywords_specs import Keywords_Specifications
from header_formatter.utils import read_config_file


class Header_Class_Setup:
    ext_app_classes = {
        "sparc4": External_Applications,
        "echarpe": External_Applications,
        "tester": Test_Applications,
    }

    def __init__(self, instrument: str) -> None:
        if instrument not in self.ext_app_classes:
            raise ValueError(f"Unknown instrument: {instrument}")
        self.instrument = instrument
        self.acs_config = read_config_file(instrument)
        self.today_str = self._create_today_str()
        self._csv_folder = (
            Path(__file__).resolve().parent
            / ".."
            / ".."
            / ".."
            / "csv"
            / self.instrument
        )

    def create_setup(
        self, _hdr_data: str, _file_name: str
    ) -> "tuple[fits.Header, dict[str, str], Header_Content, Path, Path]":
        """Create the instances needed by the Header class.

        Args:
            hdr_data (tuple): header data
            file_name (str): image file name
        """
        hdr_cnt = Header_Content(self._csv_folder)
        hdr_data = self.ext_app_classes[self.instrument].from_dict(_hdr_data)
        hdr = fits.Header(hdr_cnt.cards)
        file_name = self.verify_file_exists(self.acs_config.image_path / _file_name)
        return (
            hdr,
            hdr_data.dict(),
            hdr_cnt,
            self.log_file,
            file_name,
        )

    def create_hdr_specs(self, hdr_name: str) -> Keywords_Specifications:
        """Instanciate the class responsible for the header specifications.

        Args:
            hdr_name (str): header class name

        Returns:
            Keywords_Specifications: keywords specifications
        """
        kws_specs = Keywords_Specifications(self._csv_folder, hdr_name)
        kws_specs.load_data()
        kws_specs.validate_specifications()
        return kws_specs

    def verify_file_exists(self, file_path: Path) -> Path:
        if file_path.exists():
            now = datetime.now(timezone.utc)
            now = now.strftime("%Hh%Mm%Ss%f")[:-3] + "ms"
            if self.instrument in ["sparc4", "tester"]:
                reformatted_name = self._reformat_sparc4_file_name(file_path.name, now)
            elif self.instrument == "echarpe":
                reformatted_name = self._reformat_echarpe_file_name(file_path.name, now)
            else:
                raise ValueError(f"Unknown instrument: {self.instrument}")
            return file_path.parent / reformatted_name
        return file_path

    @staticmethod
    def _reformat_sparc4_file_name(file_name: str, now: str) -> str:
        date, chnl, *idx = file_name.split("_")
        return f"{date}_{now}_{chnl}_{idx[0]}"

    @staticmethod
    def _reformat_echarpe_file_name(file_name: str, now: str) -> str:
        return file_name[:8] + "_" + now + "_" + file_name[8:]

    @staticmethod
    def _create_today_str() -> str:
        now = datetime.now(timezone.utc)
        if now.hour < 12:
            now -= timedelta(1)
        return now.strftime("%Y%m%d")

    @property
    def log_file(self) -> Path:
        return self.acs_config.log_file_path / (self.today_str + "_keywords.log")

    @property
    def csv_folder(self) -> Path:
        return self._csv_folder
