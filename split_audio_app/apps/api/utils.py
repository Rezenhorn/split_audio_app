from apps import db
from apps.api.models import AppRequest


def add_apprequest_to_db(link: str, is_done: bool = True) -> None:
    """Добавляет запись об использовании сервиса в БД."""
    app_request = AppRequest(link=link, is_done=is_done)
    db.session.add(app_request)
    db.session.commit()
