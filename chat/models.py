# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChatRoom(models.Model):
    user1 = models.ForeignKey(User, related_name='chatroom_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='chatroom_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user1', 'user2')
    
    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"
    
    @property
    def room_name(self):
        return f"chat_{min(self.user1.id, self.user2.id)}_{max(self.user1.id, self.user2.id)}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"
