from contextlib import contextmanager
from logging import basicConfig, getLogger, getLoggerClass
from logging.config import dictConfig
from tempfile import NamedTemporaryFile
from typing import TextIO, cast
from unittest import TestCase

from wcpan.logging import ConfigBuilder


class BasicTestCase(TestCase):
    def setUp(self) -> None:
        basicConfig(force=True)
        getLoggerClass().manager.loggerDict.clear()

    def test_default_level(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name).to_dict())
            getLogger("a").debug("test")
            getLogger("a").info("test")
            getLogger("a").warning("test")
            getLogger("a").error("test")
            getLogger("a").critical("test")
            logs = parse_file(fio)
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0], ("W", "a", "test"))
        self.assertEqual(logs[1], ("E", "a", "test"))
        self.assertEqual(logs[2], ("C", "a", "test"))

    def test_module_level(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name).add("a", level="I").to_dict())
            # should not log debug from a
            getLogger("a").debug("test")
            # should log info from a
            getLogger("a").info("test")
            # should not log info from b
            getLogger("b").info("test")
            # should log warning from b
            getLogger("b").warning("test")
            logs = parse_file(fio)
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0], ("I", "a", "test"))
        self.assertEqual(logs[1], ("W", "b", "test"))

    def test_dynamic_name(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name).to_dict())
            getLogger("a").warning("test")
            getLogger("a.a").warning("test")
            getLogger("a").warning("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("W", "a", "test"))
        self.assertEqual(logs[1], ("W", "a.a", "test"))
        self.assertEqual(logs[2], ("W", "a__", "test"))

    def test_rotation(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name, rotate=True).to_dict())
            getLogger("a").warning("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("W", "a", "test"))


class FieldTestCase(TestCase):
    def setUp(self) -> None:
        basicConfig(force=True)
        getLoggerClass().manager.loggerDict.clear()

    def test_processes(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name, processes=True).to_dict())
            getLogger("a").warning("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("MainProcess", "W", "a", "test"))

    def test_threads(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name, threads=True).to_dict())
            getLogger("a").warning("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("MainThread", "W", "a", "test"))

    def test_processes_and_threads(self):
        with tmp() as fio:
            dictConfig(
                ConfigBuilder(path=fio.name, processes=True, threads=True).to_dict()
            )
            getLogger("a").warning("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("MainProcess", "MainThread", "W", "a", "test"))


class PropagationTestCase(TestCase):
    def setUp(self) -> None:
        basicConfig(force=True)
        getLoggerClass().manager.loggerDict.clear()

    def test_one_level_down(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name).add("a", level="I").to_dict())
            # should not log debug from a
            getLogger("a").debug("test")
            # should log info from a
            getLogger("a").info("test")
            # should not log debug from a.b
            getLogger("a.b").debug("test")
            # should log info from a.b
            getLogger("a.b").info("test")
            logs = parse_file(fio)
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0], ("I", "a", "test"))
        self.assertEqual(logs[1], ("I", "a.b", "test"))

    def test_skip_level(self):
        with tmp() as fio:
            dictConfig(
                ConfigBuilder(path=fio.name)
                .add("a", level="I")
                .add("a.b.c", level="D")
                .to_dict()
            )
            # should not log debug from a
            getLogger("a").debug("test")
            # should log info from a
            getLogger("a").info("test")
            # should not log debug from a.b
            getLogger("a.b").debug("test")
            # should log info from a.b
            getLogger("a.b").info("test")
            # should log debug from a.b.c
            getLogger("a.b.c").debug("test")
            # should log debug from a.b.c.d
            getLogger("a.b.c.d").debug("test")
            logs = parse_file(fio)
        self.assertEqual(len(logs), 4)
        self.assertEqual(logs[0], ("I", "a", "test"))
        self.assertEqual(logs[1], ("I", "a.b", "test"))
        self.assertEqual(logs[2], ("D", "a.b.c", "test"))
        self.assertEqual(logs[3], ("D", "a.b.c.d", "test"))


@contextmanager
def tmp():
    with NamedTemporaryFile(mode="w+", encoding="utf-8") as fio:
        yield cast(TextIO, fio)


def parse_file(fio: TextIO) -> list[tuple[str]]:
    fio.flush()
    fio.seek(0)
    return [tuple(line.rstrip().split("|")[1:]) for line in fio]
