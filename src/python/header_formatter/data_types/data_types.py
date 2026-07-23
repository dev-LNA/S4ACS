import json
import logging
from enum import IntEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Test_Applications(BaseModel):
    TESTER: str

    @classmethod
    def from_dict(cls, _header_data: str) -> Any:
        header_data = json.loads(_header_data)
        return Test_Applications(TESTER=header_data["TESTER"])


class External_Applications(BaseModel):
    GUI: str = Field(min_length=2)
    CCD: str = Field(min_length=2)
    ICS: str
    TCS: str
    FOCUSER: str
    WSTATION: str
    GENERAL_KWS: str

    @classmethod
    def from_dict(cls, _header_data: str) -> Any:
        header_data = json.loads(_header_data)
        return External_Applications(
            GUI=header_data["GUI"],
            CCD=header_data["CCD"],
            ICS=header_data["ICS"],
            TCS=header_data["TCS"],
            FOCUSER=header_data["FOCUSER"],
            WSTATION=header_data["WSTATION"],
            GENERAL_KWS=header_data["GENERAL KW"],
        )


class Log_Level(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class S4ACS_Cfg_File(BaseModel):
    channel: int
    acs_mode: bool
    image_path: Path
    log_file_path: Path
    log_level: Log_Level

    def to_sparc4_format(self) -> "dict[str, Any]":
        new_dict = {key.replace("_", " "): val for key, val in self.dict().items()}
        new_dict["log level"] //= 10
        return new_dict


class Error_Json(BaseModel):
    status: bool = False
    code: int = 0
    source: str = ""

    @classmethod
    def no_error(cls) -> Any:
        return Error_Json(status=False, code=0, source="")
