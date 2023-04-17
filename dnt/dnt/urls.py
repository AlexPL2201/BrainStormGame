from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from main import views as main
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', main.index, name='home'),  # todo
                  # path('index/', main.index, name="home"),
                  path('authapp/', include('authapp.urls', namespace='auth')),
                  path('chat/', include('chat.urls', namespace='chat')),
                  path('custom_admin/', include('custom_admin.urls', namespace='custom_admin')),
                  path('games/', include('games.urls', namespace='games')),
                  path('quest/', include('questions.urls', namespace='quest')),
                  path('telegram/', include('telegram.urls', namespace='telegram')),
                  path('user_profile/', include('user_profile.urls', namespace='user_profile')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
