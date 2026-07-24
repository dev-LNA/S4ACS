from .header import Header


class General_KWs(Header):
    name = "GENERAL_KWS"

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self.fixed_data["CYCLIND"] = self.fixed_data["CYCLIND"] + 1

    def _get_numeric_kws_predefined_vals(self) -> None:
        super()._get_numeric_kws_predefined_vals()
        self.num_kws_predefined_vals.append("BITPIX")


class General_SPARC4_KWs(General_KWs):
    def fix_keywords(self) -> None:
        super().fix_keywords()
        self.fixed_data["SEQINDEX"] = self.fixed_data["SEQINDEX"] + 1


class General_ECHARPE_KWs(General_KWs):
    pass
