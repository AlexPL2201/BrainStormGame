from django.urls import path
from games import consumers

websocket_urlpatterns = [
    path('ws/user/<int:user_id>', consumers.GamesConsumer.as_asgi()),
    path('ws/queue/<int:queue_id>', consumers.GamesConsumer.as_asgi()),
    path('ws/game/<int:game_id>', consumers.GamesConsumer.as_asgi()),
    #path('ws/chat/', consumers.ChatConsumers.as_asgi()
]
