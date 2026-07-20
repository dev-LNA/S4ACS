import json

from .header import Header


class ICS(Header):
    name = "ICS"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.how_to_fix_regex = {"ICSVRSN": self._fix_ICSVRSN}
        self.inst_mode: str
        return

    @staticmethod
    def _fix_ICSVRSN(kw_value: str) -> str:
        return "v" + kw_value


class S4ICS(ICS):
    def write_header_all_apps(self, header_data: dict) -> None:
        super().write_header_all_apps(header_data)
        self.inst_mode = json.loads(header_data["GUI"])["INSTMODE"]

    def fix_original_hdr_data(self) -> None:
        if self.original_hdr_data is None:
            return
        mechanisms = self._treat_s4ics_json()

        components_list = [
            "WPROMODE",
            "WPSEMODE",
            "CALWMODE",
            "ANMODE",
            "GMIRMODE",
            "GFOCMODE",
        ]
        s4ics_correspondents = ["WPROT", "WPSEL", "CALW", "ASEL", "GMIR", "GFOC"]
        self._write_s4ics_kws_into_json(
            mechanisms, components_list, s4ics_correspondents, "mode"
        )

        components_list = ["WPANG", "WPSELPO", "CALWANG", "ANALANG", "GMIR", "GFOC"]
        self._write_s4ics_kws_into_json(
            mechanisms, components_list, s4ics_correspondents, "position"
        )

        components_list = ["WPSEL", "CALW", "ASEL"]
        self._write_s4ics_kws_into_json(
            mechanisms, components_list, components_list, "pos_name"
        )

        components_list = [
            comp + "STAT" for comp in ["WPRO", "WPSE", "CALW", "AN", "GMIR", "GFOC"]
        ]
        self._write_s4ics_kws_into_json(
            mechanisms, components_list, s4ics_correspondents, "condition"
        )

        try:
            self.fixed_original_hdr_data["ICSVRSN"] = self.original_hdr_data["VERSION"]
        except Exception as e:
            self._write_log_file(repr(e), "ICSVRSN")

        self._write_WPPOS(mechanisms["WPROT"]["pos_id"])

    def _write_s4ics_kws_into_json(
        self, mechanisms, components_list, s4ics_correspondents, st_param
    ) -> None:
        if self.original_hdr_data is None:
            return
        for comp, ics_corresp in zip(components_list, s4ics_correspondents):
            try:
                self.fixed_original_hdr_data[comp] = mechanisms[ics_corresp][st_param]
            except Exception as e:
                self._write_log_file(repr(e), comp)

    def _treat_s4ics_json(self) -> dict:
        if self.original_hdr_data is None:
            return {}
        try:
            mechanisms_list = self.original_hdr_data["MECHANISMS"]
            mechanisms = {}
            for mechanism in mechanisms_list:
                status = mechanism["status"]
                name = mechanism["name"]
                pos_id = int(status["pos_id"])
                if pos_id == -1 and name != "WPROT":
                    self._write_log_file(
                        f"There was an error related to the {name} position: {status}.",
                        "",
                    )
                mechanisms[name] = status

            return mechanisms
        except Exception as e:
            self._write_log_file(repr(e), "")
            return {}

    def _write_WPPOS(self, wppos) -> None:
        if self.fixed_original_hdr_data is None:
            return
        kw: str = "WPPOS"
        try:
            wppos = int(wppos)
            if wppos == -1 and self.inst_mode == "PHOT":
                self.fixed_original_hdr_data[kw] = 0
            elif 1 <= wppos <= 16 and self.inst_mode == "POLAR":
                self.fixed_original_hdr_data[kw] = wppos
            else:
                self._write_log_file(f"The unexpected value {wppos} was found.", kw)
        except Exception as e:
            self._write_log_file(repr(e), kw)
        return


class EICS(ICS):
    pass
