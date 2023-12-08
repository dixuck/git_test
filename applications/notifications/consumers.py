from channels.generic.websocket import AsyncJsonWebsocketConsumer


class DoctorConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.doctor_id = self.scope['url_route']['kwargs']['doctor_id']
        await self.channel_layer.group_add(
            f"{self.doctor_id}",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"{self.doctor_id}",
            self.channel_name
        )

    async def receive(self, text_data):
        pass
         

    async def new_booking(self, event):
        await self.send_json(event)
