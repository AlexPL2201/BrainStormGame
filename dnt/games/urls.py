from django.urls import path
import games.views as games

app_name = 'games'

urlpatterns = [
    path('', games.index, name='index'),
]
