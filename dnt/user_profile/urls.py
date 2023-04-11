from django.urls import path
import user_profile.views as u_p

app_name = 'user_profile'

urlpatterns = [
    path('', u_p.index, name='index'),
    path('friends/', u_p.view_friends, name='friends'),
    path('users/<int:pk>/', u_p.UserDetailView.as_view(), name='profile'),
    path('games_list/', u_p.my_games, name='games_list'),
    path('search_friends/', u_p.manage_friends, name='search_friends'),
    path('leaderboard/', u_p.leaderboard, name='leaderboard'),
]
