from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView
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


@login_required
def get_friends(user_id):
    user = AuthUser.objects.get(id=user_id)
    friends = user.profile.friends.all()
    return friends


class UserDetailView(DetailView):
    model = AuthUser
    template_name = 'user_profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = AuthUser.objects.get(pk=self.kwargs['pk']).nickname

        return context
