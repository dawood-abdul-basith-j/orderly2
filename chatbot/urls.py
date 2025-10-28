# chatbot/urls.py
from django.urls import path
from . import views

# This sets a 'namespace' for your chatbot URLs
app_name = 'chatbot'

urlpatterns = [
    # API endpoint for sending/receiving chat messages
    path('api/message/', views.chatbot_api, name='chat_api'),

    # URL for the HTML page that shows the chat interface
    path('', views.chatbot_page_view, name='chatbot_page'),
    
    # Note: We removed the other API endpoints (place_order, get_menu) 
    # because our new chatbot_api view handles those intents internally.
]