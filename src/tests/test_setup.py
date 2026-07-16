import re
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from python.setup import Header_Class_Setup


class Test_Setup(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.csv_folder = Path.cwd() / "csv" / "sparc4"
        cls.image_path = Path.home() / "images" / "today"
        cls.log_file_path = Path.home() / "sparc4" / "log" / "s4acs1"
        cls.setup = Header_Class_Setup("sparc4")
        return super().setUpClass()

    def test_init(self) -> None:
        setup = Header_Class_Setup("sparc4")
        assert setup.instrument == "sparc4"
        assert setup.acs_config.acs_mode == 0
        assert setup.acs_config.channel == 1
        assert setup.acs_config.image_path == self.image_path
        assert setup.acs_config.log_file_path == self.log_file_path
        assert setup.acs_config.log_level == 20
        assert setup._csv_folder == self.csv_folder
        now = datetime.now(tz=timezone.utc)
        if now.hour < 12:
            now -= timedelta(1)
        assert setup.today_str == now.strftime("%Y%m%d")

    def test_verify_file_exists(self) -> None:
        file_path = self.image_path / "00000000_s4acs1_000000.fits"
        assert (
            re.match(
                r"^00000000_h\d{2}m\d{2}s\d{2}ms\d{6}_s4acs1_000000.fits$",
                self.setup.verify_file_exists(file_path).name,
            )
            is not None
        )
