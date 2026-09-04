import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.users.selectors import get_user_page


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        have_page = await self.get_user_page()
        if have_page is None:
            await self.close()
            return
        self.group_name =f'notification_{have_page}'
        await self.channel_layer.group_add(self.group_name,self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name,self.channel_name)

    async def receive(self, text_data = None):
        pass

    async def send_notification(self,event):
        try:
            await self.send(text_data=json.dumps(event['data']))  # chuyển data của event thành json
        except RuntimeError:
            pass  # client đã đóng kết nối, bỏ qua
    @database_sync_to_async
    def get_user_page(self):
        return self.user.profile.page.id if self.user.profile.page else None