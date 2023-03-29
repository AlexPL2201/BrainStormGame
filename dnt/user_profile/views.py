from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from authapp.models import AuthUser
from django.shortcuts import render, redirect
from games.models import Game


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
    user = AuthUser.objects.get(nickname=request.user)
    context = {
        'user': user
    }
    return render(request, 'user_profile/profile.html', context)


@login_required
def user_games(request):
    game = Game.objects.filter(authuser=request.user).all()
    context = {
        'game': game,
    }
    return render(request, 'user_profile/profile.html', context)


@login_required
def view_friends(request):
    user = AuthUser.objects.get(nickname=request.user)
    friends = user.friends.all()
    context = {
        'friends': friends,
    }
    return render(request, 'user_profile/friends.html', context)



