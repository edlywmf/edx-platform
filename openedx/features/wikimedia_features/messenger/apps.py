"""
Messenger App Config
"""
from django.apps import AppConfig
from edx_django_utils.plugins import PluginURLs
from openedx.core.djangoapps.plugins.constants import ProjectType


class MessengerConfig(AppConfig):
    name = 'openedx.features.wikimedia_features.messenger'

    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: 'messenger',
                PluginURLs.REGEX: '^messenger/',
                PluginURLs.RELATIVE_PATH: 'urls',
            }
        }
    }
