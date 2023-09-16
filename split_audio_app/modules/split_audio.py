import os
from typing import NamedTuple

from pydub import AudioSegment

from apps.config import path_to_temp_files


class MonoAudioFiles(NamedTuple):
    left_channel: os.PathLike
    right_channel: os.PathLike


def split_audio(path_to_file: os.PathLike) -> MonoAudioFiles:
    """
    Разбивает стерео аудио-файл на 2 файла по каналам.
    Возвращает пути к полученным файлам и удаляет исходный файл.
    """
    stereo_audio = AudioSegment.from_file(path_to_file)
    file_name = os.path.basename(path_to_file)
    mono_audios = stereo_audio.split_to_mono()
    path_to_left_channel = path_to_temp_files / f"mono_left_{file_name}"
    path_to_right_channel = path_to_temp_files / f"mono_right_{file_name}"
    mono_audios[0].export(path_to_left_channel)
    mono_audios[1].export(path_to_right_channel)
    os.remove(path_to_file)
    return MonoAudioFiles(
        left_channel=path_to_left_channel, right_channel=path_to_right_channel
    )
