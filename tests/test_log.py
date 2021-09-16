from contextlib import redirect_stderr
from tempfile import NamedTemporaryFile
from unittest import TestCase

from wcpan.logger import setup, INFO


class LogTestCase(TestCase):

    def test_log(self):
        with NamedTemporaryFile() as fio:
            setup([
                'short',
                'long.long',
            ], fio.name)

            INFO('short') << 'test'
            INFO('long.long') << 'test'
            INFO('long.long.long') << 'test'
            INFO('short') << 'test'

            fio.seek(0)
            line = fio.readline()
            pos = line.find(b'|short____|')
            self.assertGreaterEqual(pos, 0)
            line = fio.readline()
            pos = line.find(b'|long.long|')
            self.assertGreaterEqual(pos, 0)
            line = fio.readline()
            pos = line.find(b'|long.long.long|')
            self.assertGreaterEqual(pos, 0)
            line = fio.readline()
            pos = line.find(b'|short_________|')
            self.assertGreaterEqual(pos, 0)
