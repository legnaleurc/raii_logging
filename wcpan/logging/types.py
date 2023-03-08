from os import PathLike
from typing import Any, Literal, TypeAlias


StrPath: TypeAlias = str | PathLike[str]


BriefLevelName: TypeAlias = Literal["N", "D", "I", "W", "E", "C"]
FullLevelName: TypeAlias = Literal[
    "NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
]
LevelName: TypeAlias = BriefLevelName | FullLevelName


AnyDict: TypeAlias = dict[str, Any]
