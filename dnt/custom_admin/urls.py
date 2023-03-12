from django.urls import path
import custom_admin.views as admin

app_name = 'custom_admin'

urlpatterns = [
    path('', admin.index, name='index'),
]
