
from pathlib import Path
from uuid import uuid4
from unittest import TestCase
from tempfile import mkdtemp
from shutil import copy, rmtree
from zipfile import ZipFile

from archiver.archiver import ArchiveError, ArchiveManager

from tests.utils import UtilsMixin


class ArchiverTest(UtilsMixin, TestCase):

    def setUp(self):
        self.tmp_dir = None

    def tearDown(self):
        if self.tmp_dir:
            rmtree(self.tmp_dir)

    def test_initialization(self):

        # test with invalid directory
        with self.assertRaises(ArchiveError):
            ArchiveManager(self.BASE_DIR.joinpath('fake_folder'))

        # test with valid directory specified
        manager = ArchiveManager(self.MEDIA_DIR)
        self.assertEqual(self.MEDIA_DIR, manager.root_path)

        # test with no directory specified
        manager = ArchiveManager()
        self.assertEqual(manager.root_path, Path.cwd().resolve())

    def test_commands(self):
        manager = ArchiveManager()

        # check that all commands are as expected
        commands = manager.commands
        self.assertEqual(
            manager.commands.get('create', None),
            "7z a -y -bso0 -bsp0 {path_args}"
        )
        self.assertEqual(
            commands.get('list', None),
            "7z l -slt -ba {path_args}"
        )
        self.assertEqual(
            commands.get('rename', None),
            "7z rn -bso0 -bsp0 {path_args}"
        )
        self.assertEqual(
            commands.get('encrypt', None),
            "7z a -mem=AES256 -p{key} -y -bso0 -bsp0 {path_args}"
        )

        # test `get_commands` method
        command = manager.get_command('create', path_args='some_nonsense_args')
        self.assertEqual(
            command, "7z a -y -bso0 -bsp0 some_nonsense_args"
        )

    def test_resolve_path(self):
        manager = ArchiveManager(self.MEDIA_DIR)

        path = manager.resolve_path('./test_files')
        self.assertEqual(path, self.FILE_DIR.resolve())

    def test_clean_filename(self):
        manager = ArchiveManager(self.FILE_DIR)

        # with non existent file
        with self.assertRaises(ArchiveError):
            manager.clean_filename('non_existent_file.txt')

        self.assertEqual(
            manager.clean_filename('first_test_file.txt'),
            self.FILE_DIR.joinpath('first_test_file.txt')
        )

    def test_create_archive(self):
        manager = ArchiveManager(self.FILE_DIR)

        self.tmp_dir = mkdtemp(dir=self.TMP_DIR)
        archive_dir = Path(self.tmp_dir).joinpath('test_archive.zip')
        self.assertFalse(archive_dir.exists())

        files_to_archive = self.get_text_files()

        manager.create_archive(archive_dir, files_to_archive)

        self.assertTrue(archive_dir.is_file())

        with ZipFile(archive_dir) as zip_file:
            self.assertEqual(
                sorted(f.name for f in files_to_archive),
                sorted(zip_file.namelist())
            )

            for filename in zip_file.namelist():
                self.assertEqual(
                   self.FILE_DIR.joinpath(filename).read_bytes(),
                   zip_file.read(filename)
                )

    def test_rename_archive_files(self):
        manager = ArchiveManager()

        self.tmp_dir = mkdtemp(dir=self.TMP_DIR)
        archive_path = Path(self.tmp_dir).joinpath('test_archive.zip')

        copy(self.get_file_path('archive.zip'), archive_path)

        file_mapping = {
            f.name: uuid4().hex for f in self.get_text_files()
        }
        manager.rename_archive_files(archive_path, file_mapping)

        with ZipFile(archive_path) as zip_file:
            self.assertEqual(
                sorted(file_mapping.values()),
                sorted(zip_file.namelist())
            )

            # make sure that correct files have been renamed
            for old_name, new_name in file_mapping.items():
                self.assertEqual(
                    self.get_file_path(old_name).read_bytes(),
                    zip_file.read(new_name)
                )

    def test_encrypt_file(self):
        manager = ArchiveManager()

        self.tmp_dir = mkdtemp(dir=self.TMP_DIR)
        archive_path = Path(self.tmp_dir).joinpath('encrypted_archive.zip')
        self.assertFalse(archive_path.exists())

        file_to_encrypt = self.get_file_path('first_test_file.txt')

        manager.encrypt_file(
            archive_path,
            file_to_encrypt,
            key='password'
        )

        self.assertTrue(archive_path.is_file())

        with ZipFile(archive_path) as zip_file:

            # Check that zip file contains only one file
            self.assertEqual(len(zip_file.filelist), 1)

            encrypted_file = zip_file.filelist[0]

            self.assertEqual(encrypted_file.filename, file_to_encrypt.name)
            self.assertTrue(encrypted_file.flag_bits & 0x1)
