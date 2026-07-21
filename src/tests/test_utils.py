import unittest
from pathlib import Path

from python.utils import format_string, read_config_file


def test_parameters() -> None:
    cfg_file = read_config_file("sparc4")
    assert cfg_file.acs_mode is False
    assert cfg_file.channel == 1
    assert cfg_file.image_path == Path.home() / "images" / "today"
    assert cfg_file.log_file_path == Path.home() / "sparc4" / "log" / "s4acs1"
    assert cfg_file.log_level == 20


def test_format_str() -> None:
    assert format_string("12345") == "34"
