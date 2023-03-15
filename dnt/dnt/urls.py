from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from main import views as main

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main.index, name="home"), #todo
    # path('index/', main.index, name="home"),
    path('authapp/', include('authapp.urls', namespace='auth')),
    path('custom_admin/', include('custom_admin.urls', namespace='custom_admin')),
    path('games/', include('games.urls', namespace='games')),
    path('questions/', include('questions.urls', namespace='questions')),
    path('telegram/', include('telegram.urls', namespace='telegram')),
    path('user_profile/', include('user_profile.urls', namespace='user_profile')),
]
