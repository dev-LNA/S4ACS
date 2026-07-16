"""This file has all the functions needed to save the acquired images and to edit the image headers"""

import configparser
import logging
from datetime import datetime, timezone
from pathlib import Path

import astropy.io.fits as fits
import numpy as np

from python.data_types import Log_Level, S4ACS_Cfg_File

SUB_SYSTEMS = [
    "CCD",
    "GUI",
    "ICS",
    "TCS",
    "FOCUSER",
    "WSTATION",
    "GENERAL KW",
]

_log_levels = {
    "0": "STATUS",
    "1": logging.DEBUG,
    "2": logging.INFO,
    "3": logging.WARNING,
    "4": logging.ERROR,
    "5": logging.CRITICAL,
}


def format_string(string: str) -> str:
    string = str(string)[2:-1]
    return string


def write_error_log(message: str, log_file: str) -> None:
    with open(log_file, "a") as file:
        now = str(datetime.now())
        file.write(now + " - " + message + "\n")


def read_config_file(
    instrument: str, file_name: str = "acs_config.cfg"
) -> S4ACS_Cfg_File:

    section_name = "channel configuration"
    cfg_file_folder = Path.home() / instrument.upper() / "ACS"
    cfg_file = cfg_file_folder / file_name
    cfg_file_content = {}
    if not cfg_file.exists():
        raise RuntimeError(f"file {cfg_file} not found")
    config = configparser.ConfigParser()
    config.read(cfg_file)

    cfg_file_content = S4ACS_Cfg_File(
        channel=int(config.get(section_name, "channel")),
        acs_mode=config.get(section_name, "ACS mode") == 1,
        image_path=Path(config.get(section_name, "image path")),
        log_file_path=Path(config.get(section_name, "log file path")),
        log_level=Log_Level(_log_levels[config.get(section_name, "log level")]),
    )
    return cfg_file_content
