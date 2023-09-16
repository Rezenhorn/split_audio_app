import json
import threading

import pika
from flask.app import Flask

from apps.config import config
from modules.main_logic import get_mono_audio_links


class ThreadedConsumerBase(threading.Thread):
    """Базовый класс для получения и обработки сообщений из RMQ."""

    def __init__(self, app: Flask):
        threading.Thread.__init__(self)
        self.app = app
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(config.RABBITMQ_SERVER)
            )
            self.channel = self.connection.channel()
        except pika.exceptions.AMQPConnectionError as error:
            self.app.logger.error(f"Ошибка присоединения к RabbitMQ: {error}")
            raise pika.exceptions.AMQPConnectionError from error

    def handle_messages(self, data):
        """Обрабатывает сообщение из очереди RabbitMQ."""
        ...

    def callback(self, channel, method, properties, body):
        """Обрабатывает каждое полученное сообщение."""
        try:
            data = json.loads(body)
            self.handle_messages(data)
        except Exception as e:
            self.app.logger.error(f"Ошибка в консьюмере: {e}")
        finally:
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def stop(self):
        """Останавливает чтение сообщений консьюмером."""
        self.channel.stop_consuming()
        self.connection.close()
        self.app.logger.debug("Поток остановлен.")

    def run(self):
        """Прослушивание очереди."""
        with self.app.app_context():
            try:
                self.channel.start_consuming()
            except KeyboardInterrupt:
                self.stop()


class ThreadedConsumer(ThreadedConsumerBase):
    """
    Поток, читающий сообщения из очереди `tasks`.
    Для каждого сообщения вызывается функцию обработки.
    """

    def __init__(self, app: Flask):
        super().__init__(app)
        self.channel.queue_declare(
            queue=config.get("queues.tasks"), durable=True
        )
        self.channel.queue_declare(
            queue=config.get("queues.results"), durable=True
        )
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=config.get("queues.tasks"),
            on_message_callback=self.callback
        )

    def handle_messages(self, data: dict) -> None:
        """Обрабатывает сообщение из очереди RabbitMQ."""
        link = data.get("link")
        if link:
            mono_files_links = get_mono_audio_links(link)
            message = {
                "status": "success",
                "result": {
                    "left_mono": mono_files_links.left_channel_link,
                    "right_mono": mono_files_links.right_channel_link
                }
            }
            self.channel.basic_publish(
                exchange='',
                routing_key=config.get("queues.results"),
                body=json.dumps(message, ensure_ascii=False)
            )
