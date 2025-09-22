import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message, UserStatus

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.current_user = self.scope['user']
        
        if self.current_user.is_anonymous:
            await self.close()
            return
        
        # Create room name
        user_ids = sorted([self.current_user.id, int(self.user_id)])
        self.room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        self.room_group_name = f"chat_{self.room_name}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Set user online
        await self.set_user_online(True)
        
        # Notify other user about online status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.current_user.id,
                'username': self.current_user.username,
                'is_online': True
            }
        )
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Set user offline
        await self.set_user_online(False)
        
        # Notify other user about offline status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.current_user.id,
                'username': self.current_user.username,
                'is_online': False
            }
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        if message.strip():
            # Save message to database
            saved_message = await self.save_message(message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': self.current_user.username,
                    'user_id': self.current_user.id,
                    'timestamp': saved_message.timestamp.isoformat()
                }
            )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp']
        }))
    
    async def user_status(self, event):
        # Send user status to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_online': event['is_online']
        }))
    
    @database_sync_to_async
    def save_message(self, message):
        other_user = User.objects.get(id=self.user_id)
        room, created = ChatRoom.objects.get_or_create(
            user1=min(self.current_user, other_user, key=lambda u: u.id),
            user2=max(self.current_user, other_user, key=lambda u: u.id)
        )
        return Message.objects.create(
            room=room,
            sender=self.current_user,
            content=message
        )
    
    @database_sync_to_async
    def set_user_online(self, is_online):
        status, created = UserStatus.objects.get_or_create(user=self.current_user)
        status.is_online = is_online
        status.save()
