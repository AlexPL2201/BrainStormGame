from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.urls import reverse
from authapp.forms import AuthUserRegisterForm, AuthUserLoginForm


def login(request):
    login_form = AuthUserLoginForm(data=request.POST)
    if 'next' in request.GET.keys():
        next_value = request.GET['next']
    else:
        next_value = ''
    if request.method == 'POST' and login_form.is_valid():
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            if 'next' in request.POST.keys():
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect(reverse('home'))
    context = {
        'title': 'Вход',
        'login_form': login_form,
        'next': next_value
    }
    return render(request, 'authapp/login.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('auth:login'))


def register(request):
    if request.method == 'POST':
        register_form = AuthUserRegisterForm(request.POST, request.FILES)

        if register_form.is_valid():
            register_form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        register_form = AuthUserRegisterForm()

    context = {
        'title': 'Регистрация',
        'register_form': register_form,
    }
    return render(request, 'authapp/register.html', context)
