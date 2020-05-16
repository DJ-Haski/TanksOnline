import pika
import uuid
import json
IP = '34.254.177.17'
PORT = 5672
VIRTUAL_HOST = 'dar-tanks'
USERNAME = 'dar-tanks'
PASSWORD = '5orPLExUYnyVYZg48caMpX'

class RpcClient():

    def __init__(self):
        self.credentials = pika.PlainCredentials(USERNAME, password=PASSWORD)
        self.parameters = pika.ConnectionParameters(IP, PORT, VIRTUAL_HOST, self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True, auto_delete=True)
        self.callback_queue = result.method.queue
        self.channel.exchange_declare('X:routing.topic', 'topic', durable=True)

        self.channel.queue_bind(exchange='X:routing.topic', queue=self.callback_queue)
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)
        self.token = None
        self.response = None
        self.corr_id = None
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)
    def call(self, key, msg=''):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange='X:routing.topic',
            routing_key=key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id),
            body=msg
        )
        while self.response is None:
            self.connection.process_data_events()
    def room_register(self, room):
        request = json.dumps({'roomId': room})
        self.call('tank.request.register', request)
        try:
            self.token = self.response['token']
        except:
            pass
        return self.response
    def turn_tank(self, direction):
        request = json.dumps({'token': self.token, 'direction': direction})
        self.call('tank.request.turn', request)
        return self.response
    def fire(self):
        request = json.dumps({'token': self.token})
        self.call('tank.request.fire', request)
        return self.response