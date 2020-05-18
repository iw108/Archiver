
from unittest import TestCase

from archiver.utils import get_sha256_checksum

from tests.utils import UtilsMixin


class GetSHA256ChecksumFunctionTest(UtilsMixin, TestCase):

    def test_get_sha256_checksum_valid(self):
        filename = 'first_test_file.txt'
        file_path = self.FILE_DIR.joinpath(filename)

        self.assertEqual(
            get_sha256_checksum(file_path),
            self.get_checksum(filename)
        )
