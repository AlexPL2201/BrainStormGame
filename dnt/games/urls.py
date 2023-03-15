from django.urls import path
import games.views as games

app_name = 'games'

urlpatterns = [
    path('lobby/', games.create_lobby, name='lobby'),
    path('game/', games.queue, name='game'),
]
