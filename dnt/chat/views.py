from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
from chat.models import GameMessage, FriendMessage, LobbyMessage
from django.db.models import Q
from authapp.models import AuthUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from games.models import Lobby, Game


def load_messages(request):
    type_ = request.GET.get('type')
    if type_ == 'friend':
        friend_pk = int(request.GET.get('friend_pk'))
        friend = AuthUser.objects.get(pk=friend_pk)
        messages = FriendMessage.objects.filter(Q(sender__in=[request.user, friend])
                                                & Q(receiver__in=[request.user, friend])).order_by('created_at')
        print(messages)
        return JsonResponse({'messages': list(messages.values()), 'friend_name': friend.nickname}, safe=False)
    elif type_ == 'lobby':
        print(request.user)
        print(request.user.current_lobby)
        lobby = request.user.current_lobby
        messages = LobbyMessage.objects.filter(lobby=lobby).order_by('created_at')
        players = lobby.players.all()
        return JsonResponse({'messages': list(messages.values()), 'players': {player.pk: player.nickname for player in players}}, safe=False)
    elif type_ == 'game':
        game = request.user.current_game
        messages = GameMessage.objects.filter(game=game).order_by('created_at')
        players = AuthUser.objects.filter(pk__in=game.players)
        return JsonResponse(
            {'messages': list(messages.values()), 'players': {player.pk: player.nickname for player in players}},
            safe=False)

def create_messages(request):
    type_ = request.GET.get('type')
    if type_ == 'friend':
        button_message = request.GET.get('message')
        receiver_pk = int(request.GET.get('receiver'))
        sender_pk = int(request.GET.get('sender'))
        msg = FriendMessage.objects.create(text=button_message, receiver_id=receiver_pk, sender_id=sender_pk)
        # FriendMessage.objects.create(receiver=receiver_pk)
        data = {'action': 'chat_message', 'message': serializers.serialize('json', [msg]), 'type': 'friend'}
        layer = get_channel_layer()
        for pk in [sender_pk, receiver_pk]:
            async_to_sync(layer.group_send)(f'user_{pk}', {'type': 'send_message', 'message': data})
        print(msg)
    elif type_ == 'lobby':
        button_message = request.GET.get('message')
        lobby = request.user.current_lobby
        msg = LobbyMessage.objects.create(text=button_message, lobby_id=lobby.pk, sender_id=request.user.pk)
        data = {'action': 'chat_message', 'message': serializers.serialize('json', [msg]), 'type': 'lobby'}
        layer = get_channel_layer()
        for player in lobby.players.all():
            async_to_sync(layer.group_send)(f'user_{player.pk}', {'type': 'send_message', 'message': data})
    elif type_ == 'game':
        button_message = request.GET.get('message')
        game = request.user.current_game.pk
        msg = GameMessage.objects.create(text=button_message, game_id=game, sender_id=request.user.pk)
        data = {'action': 'chat_message', 'message': serializers.serialize('json', [msg])}
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(f'game_{request.user.current_game.pk}', {'type': 'send_message', 'message': data})

    return JsonResponse({'ok': 'ok'})