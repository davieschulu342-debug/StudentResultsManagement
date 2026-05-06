import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the connection
        await self.accept()
        # Optionally join a group
        await self.channel_layer.group_add("dashboard", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard", self.channel_name)

    # Receive message from server to send to client
    async def send_update(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))
