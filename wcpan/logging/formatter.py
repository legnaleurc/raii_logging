from logging import Formatter, LogRecord

TIMESTAMP = r"{asctime}"
PROCESSES = r"{{processName:_<{size}.{size}}}"
THREADS = r"{{threadName:_<{size}.{size}}}"
LEVEL = r"{levelname:_<1.1}"
NAME = r"{{name:_<{size}.{size}}}"
MESSAGE = r"{message}"


class DynamicFormatter:
    def __init__(self, *, processes: bool, threads: bool) -> None:
        self._processes = processes
        self._threads = threads
        self._name_size = 0
        self._process_name_size = 0
        self._thread_name_size = 0
        self._formatter = self._create_formatter()

    def format(self, record: LogRecord) -> str:
        changed = [
            self._check_name(record),
            self._check_processes(record),
            self._check_threads(record),
        ]
        if any(changed):
            self._formatter = self._create_formatter()
        return self._formatter.format(record)

    def _create_formatter(self) -> Formatter:
        format_list: list[str] = []
        format_list.append(TIMESTAMP)
        if self._processes:
            format_list.append(PROCESSES.format(size=self._process_name_size))
        if self._threads:
            format_list.append(THREADS.format(size=self._thread_name_size))
        format_list.append(LEVEL)
        format_list.append(NAME.format(size=self._name_size))
        format_list.append(MESSAGE)
        format = "|".join(format_list)
        return Formatter(format, style="{")

    def _check_name(self, record: LogRecord) -> bool:
        if len(record.name) > self._name_size:
            self._name_size = len(record.name)
            return True
        return False

    def _check_processes(self, record: LogRecord) -> bool:
        if (
            self._processes
            and record.processName
            and len(record.processName) > self._process_name_size
        ):
            self._process_name_size = len(record.processName)
            return True
        return False

    def _check_threads(self, record: LogRecord) -> bool:
        if (
            self._threads
            and record.threadName
            and len(record.threadName) > self._thread_name_size
        ):
            self._thread_name_size = len(record.threadName)
            return True
        return False
