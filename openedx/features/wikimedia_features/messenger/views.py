"""
Views for Messenger
"""
from django.contrib.auth.decorators import login_required

from common.djangoapps.edxmako.shortcuts import render_to_response


@login_required
def render_messenger_home(request):
    return render_to_response('wikimedia/messenger.html', {'uses_bootstrap': True,})
