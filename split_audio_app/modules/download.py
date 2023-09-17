import os
import urllib.request

import filetype

from apps.config import path_to_temp_files


class DownloadError(Exception):
    pass


def download_file(url: str, file_name: str) -> os.PathLike:
    """Загружает файл по ссылке и возвращает путь до него."""
    path_to_file, _ = urllib.request.urlretrieve(
        url, path_to_temp_files / file_name
    )
    return _rename_file_with_extension(path_to_file)


def _rename_file_with_extension(path_to_file: str) -> os.PathLike:
    """Определяет расширение файла и добавляет его в его название."""
    file_name = os.path.basename(path_to_file)
    try:
        file_extension = filetype.guess(path_to_file).extension
    except AttributeError as e:
        raise DownloadError(
            "Ошибка определения расширения файла. Проверьте переданную ссылку."
        ) from e
    file_name_with_extension = f"{file_name}.{file_extension}"
    path_to_file_with_extension = path_to_temp_files / file_name_with_extension
    os.rename(path_to_file, path_to_file_with_extension)
    return path_to_file_with_extension
