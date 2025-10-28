# analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Point the root of 'analytics/' to the new dashboard view
    path('', views.dashboard_view, name='analytics_dashboard'),
]