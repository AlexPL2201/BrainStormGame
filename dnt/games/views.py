from django.shortcuts import render
from authapp.models import AuthUser
from .models import Lobby, Queue, Game
from django.shortcuts import get_object_or_404


def create_lobby(request):
    current_user = request.user
    new_lobby = Lobby.objects.create()
    current_user.current_lobby = new_lobby
    current_user.save()

    context = {
        'title': 'Home',
        'user': current_user,

    }
    return render(request, 'games/lobby.html', context=context)


def queue(request):
    max_players = 1
    current_user = request.user
    current_lobby = current_user.current_lobby

    level = current_lobby.get_average_level // 5
    try:
        new_queue = Queue.objects.get(lowest_level=level)
    except:
        new_queue = False


    if not new_queue or new_queue.players_count + current_lobby.players_count > max_players:
        new_queue = Queue.objects.create(lowest_level=level, highest_level=level+5)
    current_lobby.queue = new_queue
    current_lobby.save()

    if new_queue.players_count == max_players: #  Создаем игру
        game = Game.objects.create()

    while new_queue.players_count != max_players:
        pass

    for lobby in new_queue.lobbies.all():

        for player in lobby.players.all():
            player.current_game = game
            player.save()
        lobby.delete()

    new_queue.delete()

    context = {
        'title': "Игра",
        'game': game,
    }

    return render(request, 'games/game.html', context)


