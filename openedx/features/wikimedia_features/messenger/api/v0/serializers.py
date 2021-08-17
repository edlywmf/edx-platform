"""
Serializers for Messenger v0 API(s)
"""
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from rest_framework import serializers

from openedx.features.wikimedia_features.messenger.models import Inbox, Message


class InboxSerializer(serializers.ModelSerializer):
    with_user = serializers.SerializerMethodField()

    class Meta:
        model = Inbox
        fields = ('id', 'with_user', 'last_message', 'unread_count')

    def get_with_user(self, obj):
        request = self.context.get('request')
        if request:
            if obj.last_message.sender != request.user:
                return obj.last_message.sender.username
            return obj.last_message.receiver.username
        raise serializers.ValidationError(
            _('Invalid request - request object not found.')
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)

        # if message length is greater then 20 -> we just want to show first 20 chars with `...`
        if len(instance.last_message.message) > 20:
            response['last_message'] = "{}...".format(instance.last_message.message[:20])
        else:
            response['last_message'] = "{}.format"(instance.last_message.message)
        return response


class ConversationAccessSerializer(serializers.Serializer):
    chat_user = serializers.CharField(max_length=250, write_only=True)
    class Meta:
        fields = ('chat_user',)

    def validate_chat_user(self, chat_user):
        try:
            User.objects.get(username=chat_user)
            return chat_user
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist - invalid username')


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'sender', 'receiver', 'message', 'created')
        read_only_fields = ('id',)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sender'] = instance.sender.username
        response['receiver'] = instance.receiver.username
        return response
