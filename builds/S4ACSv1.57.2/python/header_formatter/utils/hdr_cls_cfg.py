regex_expressions = {
    "TCS": {
        "RA": (r"[\+-]?\d{2}:\d{2}:\d{2}\.\d{2}", "HH:MM:SS.ss"),
        "DEC": (r"[\+-]?\d{2}:\d{2}:\d{2}\.\d{2}", "HH:MM:SS.ss"),
        "TCSHA": (r"[\+-]?\d{2}:\d{2}:\d{2}\.\d{2}", "HH:MM:SS.ss"),
    },
    "TESTER": {"GUIVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0")},
    "CCD": {
        "DATE-OBS": (
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}",
            "YYYY-MM-DDTHH:MM:SS.ssssss",
        ),
        "UTTIME": (r"\d{2}:\d{2}:\d{2}\.\d{6}", "HH:MM:SS.ssssss"),
        "UTDATE": (r"\d{4}-\d{2}-\d{2}", "YYYY-MM-DD"),
    },
    "S4_GENERAL_KWS": {
        "ACSVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0"),
        "SDKVRSN": (r"^\d[.]\d{3}[.]\d{5}[.]\d$", "0.000.00000.0"),
        "FILENAME": (
            r"\d{8}_s4c[1-4]_\d{6}(_[a-z0-9]+)?\.fits",
            "YYYYMMDD_s4c1_000000.fits",
        ),
    },
    "ECH_GENERAL_KWS": {
        "ACSVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0"),
        "SDKVRSN": (r"^\d[.]\d{3}[.]\d{5}[.]\d$", "0.000.00000.0"),
        "FILENAME": (
            r"\d{8}_ECH_(BLUE|RED)_\d{6}[ozdfts](_[a-z0-9]+)?\.fits",
            "YYYYMMDD_ECH_BLUE_000000o.fits",
        ),
    },
    "S4GUI": {
        "GUIVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0"),
    },
    "ICS": {"ICSVRSN": (r"v\d+\.\d+\.\d+", "v0.0.0")},
}


keywords_in_dict = {
    "TESTER": {"VSHIFT": [0.6, 1.13, 2.2, 4.33]},
    "IXON": {
        "TRIGGER": {0: "Internal", 6: "External"},
        "ACQMODE": {1: "Single Scan", 3: "Kinetics"},
        "SHUTTER": ["Auto", "Open", "Closed"],
        "VCLKAMP": ["Normal", "+1", "+2", "+3", "+4"],
        "VSHIFT": [0.6, 1.13, 2.2, 4.33],
        "EMMODE": ["Electron Multiplying", "Conventional"],
        "PREAMP": ["Gain 1", "Gain 2"],
        "READRATE": {
            0: [30.0, 20.0, 10.0, 1.0],
            1: [1.0, 0.1],
        },
    },
    "IKON": {
        "TRIGGER": {0: "Internal", 6: "External"},
        "ACQMODE": {1: "Single Scan", 3: "Kinetics"},
        "SHUTTER": ["Auto", "Open", "Closed"],
        "VCLKAMP": ["Normal", "+1", "+2", "+3", "+4"],
        "VSHIFT": [38.55, 76.95],
        "PREAMP": ["Gain 1", "Gain 2", "Gain 4"],
        "READRATE": [0.05, 1.0, 3.0, 5.0],
    },
    "S4ICS": {
        "WPSEL": {"OFF": "None", "L/2": "L2", "L/4": "L4"},
        "CALW": {
            "POLARIZER": "POLARIZER",
            "DEPOLARIZER": "DEPOLARIZER",
            "CLEAR": "CLEAR",
            "OFF": "CLEAR",
            "PINHOLE": "SPARE",
            "SPARE": "SPARE",
            "SHUTTER": "CLOSED",
            "CLOSED": "CLOSED",
        },
    },
}


empty_keywords = {
    "S4_GENERAL_KWS": {
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
        "INSTRUME": "SPARC4",
        "TELESCOP": "PE160",
    },
    "ECH_GENERAL_KWS": {
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
        "INSTRUME": "ECHARPE",
        "TELESCOP": "PE160",
    },
    "TESTER": {"BITPIX": 16},
}
