import json
from channels.generic.websocket import AsyncWebsocketConsumer


class GamesConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            name = f"queue_{self.scope['url_route']['kwargs']['queue_id']}"
        except:
            try:
                name = f"game_{self.scope['url_route']['kwargs']['game_id']}"
            except:
                pass

        self.group_name = name

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, code):

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        event = {
            'type': 'send_message',
            'message': message
        }

        await self.channel_layer.group_send(self.group_name, event)

    async def send_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({'message': message}))
