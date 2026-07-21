from .header import Header


class GUI(Header):
    name = "GUI"

    def _write_COMMENT(self) -> None:
        kw = "COMMENT"
        try:
            if self.original_hdr_data is not None:
                comment = self.original_hdr_data[kw]
                if comment == "":
                    return
                if not isinstance(comment, str):
                    self._write_log_file(
                        f'Keyword value "{comment}" is not an instance of {str}.', kw
                    )
                    return
                self.fixed_data[kw] = comment
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return

    def fix_keywords(self) -> None:
        super().fix_keywords()
        self._write_COMMENT()
        return
