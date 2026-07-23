import re
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from header_formatter.setup import Header_Class_Setup


class Test_Setup(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        instrument = "tester"
        cls.csv_folder = Path().resolve().parent / "csv" / instrument
        cls.image_path = Path(Path(__file__).resolve().anchor) / "images" / "today"
        cls.log_file_path = (
            Path(Path(__file__).resolve().anchor) / instrument / "log" / "s4acs1"
        )
        cls.setup = Header_Class_Setup(instrument)
        now = datetime.now(tz=timezone.utc)
        if now.hour < 12:
            now -= timedelta(1)
        cls.today_str = now.strftime("%Y%m%d")
        return super().setUpClass()

    def test_init(self) -> None:
        setup = Header_Class_Setup("tester")
        assert setup.instrument == "tester"
        assert setup.acs_config.acs_mode == 0
        assert setup.acs_config.channel == 1
        assert setup.acs_config.image_path == self.image_path
        assert setup.acs_config.log_file_path == self.log_file_path
        assert setup.acs_config.log_level == 10
        assert setup._csv_folder.resolve() == self.csv_folder.resolve()
        now = datetime.now(tz=timezone.utc)
        if now.hour < 12:
            now -= timedelta(1)
        assert setup.today_str == self.today_str

    def test_verify_file_exists(self) -> None:
        file_path = self.image_path / "00000000_s4c1_000000.fits"
        assert (
            re.match(
                r"^00000000_h\d{2}m\d{2}s\d{2}ms\d{6}_s4c1_000000.fits$",
                self.setup.verify_file_exists(file_path).name,
            )
            is not None
        )

        file_path = self.image_path / "00000000_s4cs1_000001.fits"
        assert self.setup.verify_file_exists(file_path).name == file_path.name

    def test_create_today_str(self) -> None:
        now = datetime.now(tz=timezone.utc)
        if now.hour < 12:
            now -= timedelta(1)
        assert self.setup._create_today_str() == self.today_str

    def test_log_file(self) -> None:
        log_file = self.log_file_path / f"{self.today_str}_keywords.log"
        assert self.setup.log_file == log_file
