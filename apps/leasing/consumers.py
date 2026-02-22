"""WebSocket consumer для чата."""
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import LeaseRequest, MaintenanceRequest


class MaintenanceChatConsumer(AsyncWebsocketConsumer):
    """WebSocket для чата по заявке на ТО."""
    async def connect(self):
        self.maint_id = self.scope['url_route']['kwargs']['maint_id']
        self.room_group_name = f'maint_chat_{self.maint_id}'
        if not await self._can_access():
            await self.close()
            return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def _can_access(self):
        from apps.accounts.models import Account
        session = self.scope.get('session') or {}
        account_id = session.get('account_id')
        if not account_id:
            return False
        try:
            account = Account.objects.filter(id=account_id, is_active=True).select_related('role').first()
            if not account:
                return False
            maint = MaintenanceRequest.objects.get(pk=self.maint_id)
            if maint.company.account_id == account.id:
                return True
            if account.role and account.role.name in ('manager', 'admin'):
                return True
        except (MaintenanceRequest.DoesNotExist, ValueError):
            pass
        return False


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.request_id = self.scope['url_route']['kwargs']['request_id']
        self.room_group_name = f'chat_{self.request_id}'
        # Проверка доступа
        if not await self._can_access():
            await self.close()
            return
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        pass  # Сообщения отправляются через HTTP POST, не через WebSocket

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def _can_access(self):
        from apps.accounts.models import Account
        session = self.scope.get('session') or {}
        account_id = session.get('account_id')
        if not account_id:
            return False
        try:
            account = Account.objects.filter(id=account_id, is_active=True).select_related('role').first()
            if not account:
                return False
            lease_req = LeaseRequest.objects.get(pk=self.request_id)
            if lease_req.account_id == account.id:
                return True
            if account.role and account.role.name in ('manager', 'admin'):
                return True
        except (LeaseRequest.DoesNotExist, ValueError):
            pass
        return False
