"""
Urls for Admin Dashboard
"""
from django.conf.urls import include, url

from openedx.features.wikimedia_features.admin_dashboard.course_reports import generate_report

urlpatterns = [
    url(r'', generate_report, name='generate_report'),
]
