import logging
import os
from importlib import import_module

from concurrent_log_handler import ConcurrentRotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


if not os.path.exists("logs"):
    os.mkdir("logs")

# Заменяет файл после достижения 10MB, хранит 20 старых копий.
rotateHandler = ConcurrentRotatingFileHandler(
    "logs/system.log", "a", 10 * 1024 * 1024, 20, encoding="utf-8"
)
rotateHandler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    )
)
rotateHandler.setLevel(logging.DEBUG)

gunicorn_error_handlers = logging.getLogger("gunicorn.error").handlers


db = SQLAlchemy()


def register_extensions(app, config):
    """Регистрация расширений."""
    db.init_app(app)

    from modules.consumer import ThreadedConsumer
    for thread in range(config.get("common.consumer_threads")):
        app.logger.info(f"Запуск RabbitMQ consumer thread {thread}")
        td = ThreadedConsumer(app)
        td.start()


def register_blueprints(app):
    """Регистрация модулей приложения."""
    for module_name in ("api", "errors"):
        module = import_module(f"apps.{module_name}.routes")
        app.register_blueprint(module.blueprint)


def configure_database(app):
    """Конфигурация БД."""

    with app.app_context():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()
        if exception and db.session.is_active:
            db.session.rollback()


def create_app(config):
    """Создание приложения."""
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app, config)
    register_blueprints(app)
    configure_database(app)
    app.logger.addHandler(rotateHandler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info("========== System START ==========")
    return app
