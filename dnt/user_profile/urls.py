from django.urls import path
import user_profile.views as u_p
from user_profile.views import UserDetailView
app_name = 'user_profile'

urlpatterns = [
    path('', u_p.index, name='index'),
    path('games/', u_p.game_status, name='game_status'),
    path('friends/', u_p.view_friends, name='friends'),
    path('users/<int:pk>/', u_p.UserDetailView.as_view(), name='profile'),
]



