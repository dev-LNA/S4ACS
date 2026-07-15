from .header import Header


class S4GUI(Header):
    name = "GUI"

    def _write_COMMENT(self) -> None:
        kw = "COMMENT"
        try:
            val = self.extracted_data[kw]
            if not isinstance(val, str):
                self._write_log_file(
                    f'Keyword value "{val}" is not an instance of {str}.', kw
                )
                return
            if self.extracted_data[kw] == "":
                return
            self.fixed_data[kw] = val
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._write_COMMENT()
        return
