import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnt.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
import games.routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            games.routing.websocket_urlpatterns
        )
    )
})
