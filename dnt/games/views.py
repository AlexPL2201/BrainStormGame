from django.shortcuts import render
from authapp.models import AuthUser
from .models import Lobby


def index(request):
    pass


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
