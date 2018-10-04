import pickle
import threading


from config import queue
from masonite.contracts import QueueContract
from masonite.drivers import BaseDriver
from masonite.exceptions import DriverLibraryNotFound

if 'amqp' in queue.DRIVERS:
    listening_channel = queue.DRIVERS['amqp']['channel']
else:
    listening_channel = 'default'


class QueueAmqpDriver(QueueContract, BaseDriver):

    def __init__(self, Container):
        """Queue Async Driver
        Arguments:
            Container {masonite.app.App} -- The application container.
        """
        try:
            import pika
            self.pika = pika
        except ImportError:
            raise DriverLibraryNotFound(
                "Could not find the 'pika' library. Run pip install pika to fix this.")

        connection = self.pika.BlockingConnection(
            self.pika.ConnectionParameters('localhost')
        )

        self.channel = connection.channel()

        self.channel.queue_declare(queue=listening_channel, durable=True)

    def push(self, *objects):
        """Push objects onto the amqp stack.

        Arguments:
            objects {*args of objects} - This can be several objects as parameters into this method.
        """

        for obj in objects:
            self.channel.basic_publish(exchange='',
                                  routing_key=listening_channel,
                                  body=pickle.dumps(obj),
                                  properties=self.pika.BasicProperties(
                                      delivery_mode=2,  # make message persistent
                                  ))
