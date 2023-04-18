from django.urls import path
import games.views as games

app_name = 'games'

urlpatterns = [
    path('lobby/', games.create_lobby, name='lobby'),
    path('join_lobby/', games.join_lobby, name='join_lobby'),
    path('join_lobby_ajax/', games.join_lobby_ajax, name='join_lobby_ajax'),
    path('change_game_mode/', games.change_game_mode, name='change_game_mode'),
    path('queue/', games.queue, name='queue'),
    path('quit_lobby/', games.quit_lobby, name='quit_lobby'),
    path('cancel_queue/', games.cancel_queue, name='cancel_queue'),
    path('create_game/', games.create_game, name='create_game'),
    path('game/', games.game, name='game'),
    path('start_game/', games.start_game, name='start_game'),
    path('check_answer/', games.check_answer, name='check_answer'),
    path('results/<int:game_id>/', games.results, name='results'),
]
