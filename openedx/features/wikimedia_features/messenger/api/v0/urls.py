"""
Urls for Messenger v0 API(s)
"""
from django.conf.urls import include, url

from  openedx.features.wikimedia_features.messenger.api.v0.views import InboxListView, ConversationListView

app_name = 'messenger_api_v0'


urlpatterns = [
    url(
        r'^user_inbox/$',
        InboxListView.as_view(),
        name="user_inbox"
    ),
    url(
        r'^conversation/$',
        ConversationListView.as_view(),
        name="conversation"
    ),


]
