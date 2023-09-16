import os
from typing import NamedTuple
import uuid

from apps.config import config
from modules.download import download_file
from modules.split_audio import split_audio
from modules.s3_storage_utils import upload_file_to_s3


class MonoAudioLinks(NamedTuple):
    left_channel_link: os.PathLike
    right_channel_link: os.PathLike


class UnsupportedExtensionError(Exception):
    pass


def get_mono_audio_links(link: str) -> MonoAudioLinks:
    """
    Разбивает переданный по ссылке стерео
    аудиофайл на 2 по каналам и загружает в s3 хранилище.
    Возвращает ссылки на скачивание полученных файлов.
    """
    file_name = str(uuid.uuid4())
    path_to_file = download_file(link, file_name)
    if ((extension := str(path_to_file).split(".")[-1])
            not in config.get("audio.supported_extensions")):
        os.remove(path_to_file)
        raise UnsupportedExtensionError(
            f"Расширение файла `{extension}` не поддерживается."
        )
    paths_to_files = split_audio(path_to_file)
    try:
        upload_file_to_s3(
            paths_to_files.left_channel, config.get("s3.bucket")
        )
        upload_file_to_s3(
            paths_to_files.right_channel, config.get("s3.bucket")
        )
    finally:
        os.remove(paths_to_files.left_channel)
        os.remove(paths_to_files.right_channel)
    left_channel_link = (f"{config.get('s3.endpoint')}"
                         f"/{config.get('s3.bucket')}/"
                         f"{os.path.basename(paths_to_files.left_channel)}")
    right_channel_link = (f"{config.get('s3.endpoint')}"
                          f"/{config.get('s3.bucket')}/"
                          f"{os.path.basename(paths_to_files.right_channel)}")
    return MonoAudioLinks(
        left_channel_link=left_channel_link,
        right_channel_link=right_channel_link
    )
