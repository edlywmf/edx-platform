"""
Views for Messenger v0 API(s)
"""
from importlib import import_module

from django.db.models import Q
from rest_framework import generics
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from openedx.features.wikimedia_features.messenger.models import Inbox, Message
from openedx.features.wikimedia_features.messenger.api.v0.serializers import (
    InboxSerializer, ConversationAccessSerializer, ConversationSerializer
)


class InboxListView(generics.ListAPIView):
    """
    Returns a list of all inbox messages of request.user
    Get /messenger/api/v0/user_inbox/

    ```
    [
        {
            "id": 1,
            "with_user": "honor",
            "last_message": "Sorry, I was busy. J...",
            "unread_count": 1
        },
        {
            "id": 2,
            "with_user": "staff",
            "last_message": "hey, I need your hel...",
            "unread_count": 1
        }
    ]

    ```

    Note that last_message will only contain first 20 chars of full message.
    """
    queryset = Inbox.objects.all()
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = InboxSerializer
    pagination_class = None

    def get_queryset(self):
        return Inbox.objects.filter(
            Q(last_message__sender=self.request.user)  | Q(last_message__receiver=self.request.user)
        )


class ConversationListView(APIView):
    """
    Return conversation between two users -> All messages sent or received between two users.

    POST /messenger/api/v0/conversation/
    POST DATA: {
        chat_user: "username"
    }

    Return -> list of messages sent or received between request.user and user with given username/
    [
        {
            "id": 1,
            "sender": "honor",
            "receiver": "edx",
            "message": "Hi",
            "created": "2021-08-17T15:21:04Z"
        },
        {
            "id": 2,
            "sender": "honor",
            "receiver": "edx",
            "message": "There ?",
            "created": "2021-08-17T15:21:31Z"
        },
        {
            "id": 3,
            "sender": "edx",
            "receiver": "honor",
            "message": "Sorry, I was busy. Just saw your message. Is anything urgent ?",
            "created": "2021-08-17T15:23:21Z"
        }
    ]
    """
    queryset = Inbox.objects.all()
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = None
    serializer_class = ConversationAccessSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.POST)
        if serializer.is_valid(raise_exception=True):
            chat_user = serializer.validated_data.get('chat_user')
            owner = self.request.user

            conversation_messages = Message.objects.filter(
                (Q(sender=owner) & Q(receiver__username=chat_user)) |
                (Q(sender__username=chat_user) & Q(receiver=owner))
            ).order_by('created')

            conversation = ConversationSerializer(conversation_messages, many=True)
            return Response(conversation.data)
