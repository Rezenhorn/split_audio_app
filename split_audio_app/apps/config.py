import os
import urllib.parse
from pathlib import Path
from threading import Lock

import yaml


class ConfigClass(object):
    """Класс ConfigClass служит для чтения config.yaml файла."""

    def __init__(self, filename):
        self._lock = Lock()
        self.filename = filename
        self.load = "abc"
        with open(self.filename, "r") as stream:
            try:
                self.load = yaml.safe_load(stream)
                for i in self.load:
                    setattr(self, i, self.load[i])
            except yaml.YAMLError as exc:
                print("Ошибка чтения конфиг файла", exc)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __getitem__(self, item):
        with self._lock:
            namespace = item.split(".")
            data = self.load
            for name in namespace:
                data = data[name]
            return data


class Config(ConfigClass):
    """
    Класс Config служит для установки переменных окружения данного модуля.
    """

    def __init__(self, filename):
        ConfigClass.__init__(self, filename)

        # Конфигурация PostgreSQL
        # Прочитать логин и пароль, содержащие спец символы
        sql_db_user = urllib.parse.quote_plus(self.get("db.user"))
        sql_db_pass = urllib.parse.quote_plus(self.get("db.pass"))
        self.SQLALCHEMY_DATABASE_URI = f"{self.get('db.engine')}://{sql_db_user}:{sql_db_pass}@{self.get('db.host')}:{self.get('db.port')}/{self.get('db.name')}"

        # Конфигурация RabbitMQ
        # Прочитать логин и пароль, содержащие спец символы
        rmq_db_user = urllib.parse.quote_plus(self.get("rmq.user"))
        rmq_db_pass = urllib.parse.quote_plus(self.get("rmq.pass"))
        self.RABBITMQ_SERVER = f"amqp://{rmq_db_user}:{rmq_db_pass}@{self.get('rmq.host')}:{self.get('rmq.port')}/{self.get('rmq.vhost')}"

        self.SQLALCHEMY_TRACK_MODIFICATIONS = True
        # Настройка для корректного отображения ответов
        self.JSON_AS_ASCII = False


current_file = os.path.realpath(__file__)
current_directory = os.path.dirname(current_file)
root_directory = Path(current_directory).parents[0]
path_to_temp_files = root_directory / "temp"

# Загрузка всех конфигураций
config = Config("./config.yaml")
