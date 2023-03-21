from django.urls import path
import authapp.views as auth

app_name = 'authapp'

urlpatterns = [
    path('login/', auth.login, name='login'),
    path('logout/', auth.logout, name='logout'),
    path('register/', auth.register, name='register'),
    path('edit/', auth.edit, name='edit'),
]


