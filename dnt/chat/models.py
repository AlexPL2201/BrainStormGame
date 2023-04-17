from django.db import models
from authapp.models import AuthUser
from games.models import Game, Lobby

class FriendMessage(models.Model):

    sender = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='receiver')
    text = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now=True)

class LobbyMessage(models.Model):

    sender = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    text = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now=True)

class GameMessage(models.Model):

    sender = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    text = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now=True)

