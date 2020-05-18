
from pathlib import Path
from unittest import TestCase


class UtilsMixin(TestCase):

    BASE_DIR = Path(__file__).parent

    MEDIA_DIR = BASE_DIR.joinpath('media')

    FILE_DIR = MEDIA_DIR.joinpath('test_files')

    TMP_DIR = MEDIA_DIR.joinpath('tmp')

    CHECKSUMS = {
        'first_test_file.txt': (
            '260871b53e7d8420eb2cf11ed00badf863'
            '406f00a6741a5e19857b2df69a26c7'
        ),
        'second_test_file.txt': (
            '7ebb39d81431558fa63fbf2035f25e4'
            'edfe38c6ca3e5566bf9bf2fbc20421951'
        ),
        'archive.zip': (
            'ffdf6f781ad8833dfdbc0bef23a4f0bc31c904'
            '6b8edb075569ffe659ea298687'
        )
    }

    def _get_path(self, filename):
        return self.FILE_DIR.joinpath(filename)

    def get_file_path(self, filename):
        if filename not in self.CHECKSUMS:
            raise ValueError
        return self._get_path(filename)

    @property
    def file_list(self):
        return [self._get_path(f) for f in self.CHECKSUMS]

    def get_text_files(self):
        return [f for f in self.file_list if f.suffix == '.txt']

    def get_checksum(self, filename):
        return self.CHECKSUMS[filename]
