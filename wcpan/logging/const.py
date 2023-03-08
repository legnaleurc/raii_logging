from .types import FullLevelName, LevelName


LEVEL_TABLE: dict[LevelName, FullLevelName] = {
    "N": "NOTSET",
    "NOTSET": "NOTSET",
    "D": "DEBUG",
    "DEBUG": "DEBUG",
    "I": "INFO",
    "INFO": "INFO",
    "W": "WARNING",
    "WARNING": "WARNING",
    "E": "ERROR",
    "ERROR": "ERROR",
    "C": "CRITICAL",
    "CRITICAL": "CRITICAL",
}
