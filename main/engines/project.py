import os
import zipfile
from typing import IO, Any, Dict, List

from main.engines.exceptions import NoValidImportFileException
from main.enums import FileReferenceType, FileType, ProjectImportServiceFileName


def unzip_import_file(zip_file_buffer: IO[bytes]) -> List[Dict[str, Any]]:
    zipfile_object = zipfile.ZipFile(zip_file_buffer)
    # Get the directory inside the zip if it exists
    try:
        zipfile_dir = [
            name for name in zipfile_object.namelist() if name.endswith('/')
        ][0]
    except IndexError:
        zipfile_dir = ''

    actual_file_names = [
        item.split('/')[-1]
        for item in zipfile_object.namelist()
        if not item.split('/')[-1].startswith('.') and not item.endswith('/')
    ]
    expected_file_names = ProjectImportServiceFileName.get_list()

    valid_file_names = [
        name for name in actual_file_names if name in expected_file_names
    ]
    if not valid_file_names:
        raise NoValidImportFileException(
            message=f'No valid import file found in uploaded zip. Valid files are {expected_file_names}'
        )

    unzipped_files = [
        {'name': file_name, 'content': zipfile_object.read(zipfile_dir + file_name)}
        for file_name in valid_file_names
    ]
    return unzipped_files


def generate_export_file_path(project_id: int, file_name: str):
    return os.path.join(
        FileReferenceType.PROJECT, str(project_id), FileType.EXPORT, file_name
    )


def generate_import_file_path(project_id: int, file_name: str):
    return os.path.join(
        FileReferenceType.PROJECT, str(project_id), FileType.IMPORT, file_name
    )
