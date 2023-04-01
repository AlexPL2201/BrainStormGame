from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView
from authapp.models import AuthUser
from django.shortcuts import render, redirect, get_object_or_404
from games.models import Game
from django.http import HttpResponseRedirect
from django.urls import reverse


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
    user = AuthUser.objects.get(nickname=request.user)
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
        context['title'] = AuthUser.objects.get(pk=self.kwargs['pk']).nickname

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
        user.friends.add(friend)
    elif action == 'remove':
        friend = get_object_or_404(user.friends, username=friend_username)
        user.friends.remove(friend)

    context = {
        'user': user,
        'results': results,
    }
    return render(request, 'user_profile/manage_friends.html', context)
