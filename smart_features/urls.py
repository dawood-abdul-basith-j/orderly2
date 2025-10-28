# smart_features/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Page that displays the chatbot interface
    path('chat/', views.chatbot_page_view, name='chatbot_page'),
    # API endpoint for sending/receiving messages
    path('chatbot/', views.chatbot_api, name='chatbot_api'),
]