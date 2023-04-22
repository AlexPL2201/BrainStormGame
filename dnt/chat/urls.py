from django.urls import path
import chat.views as chat

app_name = 'chat'

urlpatterns = [
    path('load_messages/', chat.load_messages, name='load_messages'),
    path('create_messages/', chat.create_messages, name='create_messages'),
]
