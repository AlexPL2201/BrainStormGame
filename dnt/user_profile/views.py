from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from authapp.models import AuthUser
from games.models import Game


def index(request):
    pass


@login_required
def user_list(request):
    users = AuthUser.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'user_profile/user_list.html', context)


@login_required
def view_friends(request):
    user = AuthUser.objects.get(username=request.user)
    friends = user.friends.all()
    context = {
        'friends': friends,
    }
    return render(request, 'user_profile/friends.html', context)


class UserDetailView(DetailView):
    model = AuthUser
    template_name = 'user_profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = AuthUser.objects.get(pk=self.kwargs['pk'])

        return context


@login_required
def manage_friends(request):
    user = request.user
    query = request.GET.get('q')
    action = request.POST.get('action')
    friend_username = request.POST.get('friend_username')

    if query:
        results = AuthUser.objects.filter(username__icontains=query)
    else:
        results = None

    if action == 'add':
        friend = get_object_or_404(AuthUser, username=friend_username)
        if friend == request.user:
            messages.error(request, "Вы не можете добавить себя в друзья")
        else:
            user.friends.add(friend)
    elif action == 'remove':
        friend = get_object_or_404(user.friends, username=friend_username)
        user.friends.remove(friend)

    context = {
        'user': user,
        'results': results,
    }
    return render(request, 'user_profile/manage_friends.html', context)


# @login_required
# def my_games(request):
#     user = request.user
#     objs = Game.objects.filter(players=user).order_by('-started')  # all() == filter(players=user).order_by('-started')
#     games = [x for x in objs if str(user.pk) in x.players]
#     context = {
#         'user': user,
#         'games': games,
#     }
#     return render(request, 'user_profile/profile.html', context)


def leaderboard(request):
    players = AuthUser.objects.order_by('-current_experience')[:5]
    return render(request, 'user_profile/leaderboard.html', {'players': players})


@login_required
def my_games(request):
    user = request.user
    obj = Game.objects.all()
    games = [x for x in obj if str(user.pk) in x.players]
    context = {
        'user': user,
        'games': games,
    }
    return render(request, 'user_profile/games_list.html', context)
