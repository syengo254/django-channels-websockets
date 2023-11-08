import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connect to websockets server succesfully!',
        }))

    def receive(self, text_data=None, bytes_data=None):
        received_data = json.loads(text_data)

        # print('Recieved message of type', received_data['type'])
        # print('Message:', received_data['message'])

        # send received message to group
        async_to_sync(self.channel_layer.group_send)(
           self.room_group_name,
           {
               'type': 'chat_message',
               'message': received_data['message'],
           }
        )

    # read message from group (received method did this) & send to clients
    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
        }))

    def disconnect(self, code):
        # leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def close(self, code=None):
        return super().close(code)
