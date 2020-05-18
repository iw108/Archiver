
import logging
from os import remove as os_remove, sep as os_sep
from pathlib import Path
from re import match as re_match, sub as re_sub
from shlex import split as shlex_split
from subprocess import PIPE, Popen  # nosec
from threading import Timer


ARCHIVE_TIMEOUT = 15


logger = logging.getLogger(__name__)


class ArchiveError(Exception):
    pass


def execute_subprocess(command):

    command = shlex_split(command)
    process = Popen(command, stdout=PIPE, stderr=PIPE, shell=False)
    timer = Timer(ARCHIVE_TIMEOUT, process.kill)

    try:
        timer.start()
        out, error = process.communicate()
        exit_code = process.returncode
    except Exception as e:
        logger.error(f'Something went wrong: {e}')
        raise ArchiveError
    finally:
        timer.cancel()

    if exit_code != 0:
        raise ArchiveError(error.decode())

    return out.decode()


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    regex_expr = '[^-\w.]'
    return re_sub(regex_expr, "", s)


def clean_file_name(filename):
    if filename and filename == get_valid_filename(filename):
        return filename
    raise ArchiveError


def format_path_args(*args):
    return ' '.join(f"'{arg}'" for arg in args)


class ArchiveManager(object):

    permitted_extension = ['.7z', '.zip']

    default_extension = '.zip'

    commands = {
        'create': "7z a -y -bso0 -bsp0 {path_args}",
        'list': "7z l -slt -ba {path_args}",
        'rename': "7z rn -bso0 -bsp0 {path_args}",
        'encrypt': "7z a -mem=AES256 -p{key} -y -bso0 -bsp0 {path_args}"
    }

    def __init__(self, path=None):
        path = Path(path).resolve() if path else Path.cwd()
        if not path.is_dir():
            raise ArchiveError('only directories allowed')
        self._root = path

    @property
    def root_path(self):
        return self._root

    def is_extension_permitted(self, extension):
        return extension in self.permitted_extension

    def get_command(self, command_name, **kwargs):
        command = self.commands[command_name]
        return command.format(**kwargs)

    def resolve_path(self, path):
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj.resolve()
        return self.root_path.joinpath(path).resolve()

    def clean_archive_name(self, archive_name):
        archive_path = self.resolve_path(archive_name)
        if not archive_path.parent.is_dir():
            raise ArchiveError

        cleaned_name = archive_path.name
        if not archive_name:
            raise ArchiveError

        if cleaned_name != get_valid_filename(cleaned_name):
            raise ArchiveError

        archive_extension = archive_path.suffix
        if archive_extension:
            if not self.is_extension_permitted(archive_extension):
                raise ArchiveError
        else:
            cleaned_name += self.default_extension

        archive_path = archive_path.parent.joinpath(cleaned_name)
        if archive_path.exists():
            return ArchiveError
        return archive_path

    def clean_filename(self, file_name):
        file_path = self.resolve_path(file_name)
        if not file_path.is_file():
            raise ArchiveError(f'{file_name} is not a file')
        return file_path

    def clean_dirname(self, dir_name):
        path = self.resolve_path(dir_name)
        if not path.is_dir():
            raise ArchiveError
        return str(path) + os_sep

    def create_archive(self, archive_name, file_names=None, dir_names=None):
        archive_path = self.clean_archive_name(archive_name)

        paths = [archive_path]
        if file_names:
            paths.extend(self.clean_filename(f) for f in file_names)
        if dir_names:
            paths.extend(self.clean_dirname(d) for d in dir_names)
        path_args = format_path_args(*paths)

        command = self.get_command('create', path_args=path_args)
        try:
            execute_subprocess(command)
        except ArchiveError as e:
            if archive_path.exists():
                os_remove(archive_path)
            raise ArchiveError(e)

    def list_archive(self, archive_name):
        """
        function calls << 7z l -slt -ba {container_path}>> function, the
        output of which looks something like ...
            Path = first_file.py
            Size = 123

            Path = second_file.py
            Size = 123
        extract the key and the value from the output
        """

        # Parse input
        container_path = self.clean_filename(archive_name)

        path_args = format_path_args(container_path)
        command = self.get_command('list', path_args=path_args)
        output = execute_subprocess(command)

        file_list = [{}]
        for line in output.strip().splitlines():
            if not line:
                file_list.append({})
                continue
            file_item = file_list[-1]

            key = re_match(r'^\w+', line)[0].lower()
            value = re_sub(r'^\w+\s=\s', "", line)
            file_item.update({key: value})

        return [f for f in file_list if f]

    def rename_archive_files(self, archive_name, file_mapping):
        container_path = self.clean_filename(archive_name)

        archive_file_names = [
            file['path'] for file in self.list_archive(container_path)
        ]

        invalid_files = [
            old_name for old_name in file_mapping
            if old_name not in archive_file_names
        ]
        if invalid_files:
            raise ArchiveError(
                f'The following files are not in the archive: {invalid_files}'
            )

        invalid_new_names = []
        for file in file_mapping.keys():
            try:
                clean_file_name(file)
            except ArchiveError:
                invalid_new_names.append(file)
        if invalid_new_names:
            raise ArchiveError(
                f'The following file names are not valid: {invalid_files}'
            )

        mapping = (item for items in file_mapping.items() for item in items)
        path_args = format_path_args(container_path, *mapping)
        command = self.get_command('rename', path_args=path_args)
        execute_subprocess(command)

    def encrypt_file(self, archive_name, file_name, key):
        archive_path = self.clean_archive_name(archive_name)

        file_path = self.clean_filename(file_name)

        path_args = format_path_args(archive_path, file_path)
        command = self.get_command('encrypt', path_args=path_args, key=key)
        try:
            execute_subprocess(command)
        except ArchiveError as error:
            if archive_path.exists():
                os_remove(archive_path)
            raise ArchiveError(error)


class LockedDownArchiveManager(ArchiveManager):

    def resolve_path(self, path):
        output_path = super().resolve_path(path)

        try:
            self.root_path.relative_to(output_path)
        except ValueError as error:
            ArchiveError(error)

        return output_path
