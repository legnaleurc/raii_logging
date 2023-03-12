from contextlib import contextmanager
from logging import getLogger
from logging.config import dictConfig
from tempfile import NamedTemporaryFile
from typing import TextIO, cast
from unittest import TestCase

from wcpan.logging import ConfigBuilder


class BasicTestCase(TestCase):
    def test_default_level(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name).add("a").to_dict())
            getLogger("a").debug("test")
            logs = parse_file(fio)
        self.assertEqual(len(logs), 0)

    def test_message(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name).add("a").to_dict())
            getLogger("a").error("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("E", "a", "test"))

    def test_dynamic_name(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name).add("a").to_dict())
            getLogger("a").warning("test")
            getLogger("a.a").warning("test")
            getLogger("a").warning("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("W", "a", "test"))
        self.assertEqual(logs[1], ("W", "a.a", "test"))
        self.assertEqual(logs[2], ("W", "a__", "test"))


class FieldTestCase(TestCase):
    def test_processes(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name, processes=True).add("a").to_dict())
            getLogger("a").warning("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("MainProcess", "W", "a", "test"))

    def test_threads(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name, threads=True).add("a").to_dict())
            getLogger("a").warning("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("MainThread", "W", "a", "test"))

    def test_processes_and_threads(self):
        with tmp() as fio:
            dictConfig(
                ConfigBuilder(path=fio.name, processes=True, threads=True)
                .add("a")
                .to_dict()
            )
            getLogger("a").warning("test")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("MainProcess", "MainThread", "W", "a", "test"))


class PropagationTestCase(TestCase):
    def test_single_level(self):
        with tmp() as fio:
            dictConfig(ConfigBuilder(path=fio.name, level="N").add("a").to_dict())
            getLogger("a").info("z")
            getLogger("a.b").info("y")
            getLogger("a.b.c").info("x")
            logs = parse_file(fio)
        self.assertEqual(logs[0], ("I", "a", "z"))
        self.assertEqual(logs[1], ("I", "a.b", "y"))
        self.assertEqual(logs[2], ("I", "a.b.c", "x"))

    def test_multiple_level(self):
        with tmp() as fio:
            dictConfig(
                ConfigBuilder(path=fio.name)
                .add("a", level="D")
                .add("a.b", level="I")
                .to_dict()
            )
            getLogger("a").debug("z")
            getLogger("a.b").info("y")
            getLogger("a.b").debug("x")
            getLogger("a.b.c").debug("x")
            getLogger("b").debug("w")
            getLogger("b").warning("w")
            logs = parse_file(fio)
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0], ("D", "a", "z"))
        self.assertEqual(logs[1], ("I", "a.b", "y"))
        self.assertEqual(logs[2], ("W", "b__", "w"))


@contextmanager
def tmp():
    with NamedTemporaryFile(mode="w+", encoding="utf-8") as fio:
        yield cast(TextIO, fio)


def parse_file(fio: TextIO) -> list[tuple[str]]:
    fio.flush()
    fio.seek(0)
    return [tuple(line.rstrip().split("|")[1:]) for line in fio]
