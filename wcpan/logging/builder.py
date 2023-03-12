from typing import Self

from .const import LEVEL_TABLE
from .types import AnyDict, LevelName, StrPath


FORMATTER_ID = "wcpan.logging.formatter"
HANDLER_ID = "wcpan.logging.handler"


class ConfigBuilder:
    def __init__(
        self,
        *,
        level: LevelName | None = None,
        path: StrPath | None = None,
        rotate: bool = False,
        processes: bool = False,
        threads: bool = False
    ) -> None:
        self._level: LevelName | None = level
        self._path = path
        self._rotate = rotate
        self._processes = processes
        self._threads = threads
        self._loggers: dict[str, LevelName | None] = {}

    def add(self, *names: str, level: LevelName | None = None) -> Self:
        for name in names:
            self._loggers[name] = level
        return self

    def to_dict(self) -> AnyDict:
        handler = create_handler(path=self._path, rotate=self._rotate)
        handler["formatter"] = FORMATTER_ID
        root = create_root(level=self._level)
        root["handlers"] = [HANDLER_ID]
        return {
            "version": 1,
            "formatters": {
                FORMATTER_ID: {
                    "()": "wcpan.logging.formatter.DynamicFormatter",
                    "processes": self._processes,
                    "threads": self._threads,
                },
            },
            "handlers": {
                HANDLER_ID: handler,
            },
            "root": root,
            "loggers": create_loggers(self._loggers),
        }


def create_root(*, level: LevelName | None) -> AnyDict:
    root: AnyDict = {}
    if level:
        root["level"] = LEVEL_TABLE[level]
    return root


def create_handler(*, path: StrPath | None, rotate: bool) -> AnyDict:
    if not path:
        return {
            "class": "logging.StreamHandler",
        }
    elif rotate:
        return {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(path),
            "when": "w6",
        }
    else:
        return {
            "class": "logging.FileHandler",
            "filename": str(path),
        }


def create_loggers(loggers: dict[str, LevelName | None]) -> AnyDict:
    rv: AnyDict = {}
    for name, level in loggers.items():
        logger: AnyDict = {}
        if level:
            logger["level"] = LEVEL_TABLE[level]
        rv[name] = logger
    return rv
