import os
from typing import Optional

import boto3
from flask import current_app as app

from apps.config import config


class S3UploadError(Exception):
    pass


AWS_SERVER_PUBLIC_KEY = "id"
AWS_SERVER_SECRET_KEY = "key"

session = boto3.Session(
    aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
    aws_secret_access_key=AWS_SERVER_SECRET_KEY,
    region_name="ru-central1"
)
s3 = session.client(
    service_name='s3',
    endpoint_url=config.get("s3.endpoint"),
)


def upload_file_to_s3(
    path_to_file: os.PathLike, bucket: str, object_name: Optional[str] = None
) -> None:
    """
    Загружает файл в s3 bucket.
    Возвращает True если файл был загружен, иначе False.
    """
    if object_name is None:
        object_name = os.path.basename(path_to_file)
    try:
        s3.upload_file(path_to_file, bucket, object_name)
    except Exception as e:
        app.logger.error(f"Ошибка при загрузке файла в s3: {e}")
        raise S3UploadError from e
    finally:
        os.remove(path_to_file)
