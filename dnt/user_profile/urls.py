from django.urls import path
import user_profile.views as user_profile

app_name = 'user_profile'

urlpatterns = [
    path('', user_profile.index, name='index'),
]
