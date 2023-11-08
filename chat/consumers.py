import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import ChatHistory


def get_history(room_name):
    return ChatHistory.objects.filter(room_name=room_name).all()[:5]


def add_to_history(**kwargs):
    ChatHistory.objects.create(**kwargs)


@database_sync_to_async
def async_get_history(room_name):
    return get_history(room_name)


@database_sync_to_async
def async_add_to_history(**kwargs):
    return add_to_history(**kwargs)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'test'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # fetch last 5 messages in ChatHistory
        history = await async_get_history(self.room_group_name)

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connect to websockets server succesfully!',
            'history': [row.message async for row in history]
        }))

    async def receive(self, text_data=None, bytes_data=None):
        received_data = json.loads(text_data)

        # print('Recieved message of type', received_data['type'])
        # print('Message:', received_data['message'])

        # add to history
        await async_add_to_history(
            room_name=self.room_group_name,
            message=received_data['message']
        )

        # send received message to group
        await self.channel_layer.group_send(
           self.room_group_name,
           {
               'type': 'chat_message',
               'message': received_data['message'],
           }
        )

    # read message from group (received method did this) & send to clients
    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
        }))

    async def disconnect(self, code):
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def close(self, code=None):
        return await super().close(code)
