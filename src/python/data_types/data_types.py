from pydantic import BaseModel


class SPARC4_Applications(BaseModel):
    CCD: str
    GUI: str
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
