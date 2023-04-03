from django.urls import path
import user_profile.views as u_p
from user_profile.views import UserDetailView

app_name = 'user_profile'

urlpatterns = [
    path('', u_p.index, name='index'),
    path('friends/', u_p.view_friends, name='friends'),
    path('users/<int:pk>/', u_p.UserDetailView.as_view(), name='profile'),
    path('users_list/', u_p.user_list, name='user_list'),
    path('friends_list/', u_p.manage_friends, name='manage_friends'),
    path('users/<int:pk>/', u_p.my_games, name='profile')
]
