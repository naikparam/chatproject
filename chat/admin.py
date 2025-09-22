from django.contrib import admin
from .models import ChatRoom, Message, UserStatus

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user1__username', 'user2__username']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'content', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read']
    search_fields = ['sender__username', 'content']

@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_online', 'last_seen']
    list_filter = ['is_online', 'last_seen']