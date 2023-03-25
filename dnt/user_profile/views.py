from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from authapp.models import AuthUser
from games.models import Game
from django.urls import reverse


def index(request):
    pass


def game_status(request):
    games = Game.objects.filter(authuser=request.user)
    game_info = ""
    for game in games:
        game_info += f"Type: {game.type} Старт: {game.started} Финиш: {game.is_finished} Результат: {game.results}<br>"
    return HttpResponse(game_info)


@login_required
def profile_view(request):
    user = AuthUser.objects.get(username=request.user)
    context = {
        'user': user
    }
    return render(request, 'user_profile/profile.html', context)
