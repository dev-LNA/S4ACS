import logging
from enum import IntEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# class Tester(BaseModel):
#     TESTER: str

#     @classmethod
#     def from_tuple(cls, header_data: tuple) -> Applications:
#         return Applications()


class External_Applications(BaseModel):
    CCD: str = Field(min_length=2)
    GUI: str = Field(min_length=2)
    ICS: str
    TCS: str
    FOCUSER: str
    WSTATION: str
    GENERAL_KWS: str

    @classmethod
    def from_tuple(cls, header_data: tuple) -> External_Applications:
        return External_Applications(
            GUI=header_data[0],
            CCD=header_data[1],
            ICS=header_data[2],
            TCS=header_data[3],
            FOCUSER=header_data[4],
            WSTATION=header_data[5],
            GENERAL_KWS=header_data[6],
        )


class S4ACS_Cfg_File(BaseModel):
    channel: int
    acs_mode: int
    image_path: Path
    log_file_path: Path
    log_level: Log_Level

    def to_sparc4_format(self) -> dict[str, Any]:
        new_dict = {
            key.replace("_", " "): val for key, val in self.model_dump().items()
        }
        new_dict["log level"] //= 10
        return new_dict


class Log_Level(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Error_Json(BaseModel):
    status: bool = False
    code: int = 0
    source: str = ""

    @classmethod
    def no_error(cls) -> Error_Json:
        return Error_Json(status=False, code=0, source="")
