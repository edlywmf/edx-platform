"""
Messenger Models
"""
from django.db import models
from django.contrib.auth.models import User

APP_LABEL = 'messenger'


class Message(models.Model):
    class Meta:
        app_label = APP_LABEL

    message = models.TextField()
    created = models.DateTimeField()
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')

    def __str__(self):
        return "from: {}, to: {}, message: {}".format(
            self.sender.username,
            self.receiver.username,
            self.message[:20]
        )


class Inbox(models.Model):
    class Meta:
        app_label = APP_LABEL

    unread_count = models.IntegerField(default=0)
    last_message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='last_message')
