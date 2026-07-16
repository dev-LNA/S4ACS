import logging
from enum import IntEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class SPARC4_Applications(BaseModel):
    CCD: str = Field(min_length=2)
    GUI: str = Field(min_length=2)
    ICS: str
    TCS: str
    FOCUSER: str
    WSTATION: str
    GENERAL_KWS: str

    @classmethod
    def from_tuple(cls, _header_jsons: tuple) -> SPARC4_Applications:
        return SPARC4_Applications(
            GUI=_header_jsons[0],
            CCD=_header_jsons[1],
            ICS=_header_jsons[2],
            TCS=_header_jsons[3],
            FOCUSER=_header_jsons[4],
            WSTATION=_header_jsons[5],
            GENERAL_KWS=_header_jsons[6],
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
