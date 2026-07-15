from .header import Header


class General_KWs(Header):
    name = "GENERAL_KWS"

    def __init__(self, log_file, hdr_cnt, csv_folder) -> None:
        super().__init__(log_file, hdr_cnt, csv_folder)
        # O pandas trata tudo como uma string
        self.empty_kws = {
            "NAXIS": 2,
            "OBSLONG": -45.5825,
            "OBSLAT": -22.534,
            "OBSALT": 1864.0,
            "EQUINOX": 2000.0,
            "SIMPLE": True,
            "BITPIX": 16,
            "BZERO": 1,
            "BSCALE": 32768,
            "SITEID": "OPD",
        }

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self.fixed_data["CYCLIND"] = self.extracted_data["CYCLIND"] + 1


class General_SPARC4_KWs(General_KWs):
    def __init__(self, log_file, hdr_cnt, csv_folder) -> None:
        super().__init__(log_file, hdr_cnt, csv_folder)

        self.empty_kws["INSTRUME"] = "SPARC4"
        self.empty_kws["TELESCOP"] = "PE160"

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self.fixed_data["SEQINDEX"] = self.extracted_data["SEQINDEX"] + 1


class General_ECHARPE_KWs(General_KWs):
    def __init__(self, log_file, hdr_cnt, csv_folder) -> None:
        super().__init__(log_file, hdr_cnt, csv_folder)

        self.empty_kws["TELESCOP"] = "PE160"
        self.empty_kws["INSTRUME"] = "ECHARPE"

        return
