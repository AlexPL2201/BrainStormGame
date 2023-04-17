from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
from chat.models import GameMessage, FriendMessage, LobbyMessage
from django.db.models import Q
from authapp.models import AuthUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


def load_messages(request):
    type_ = request.GET.get('type')
    if type_ == 'friend':
        friend_pk = int(request.GET.get('friend_pk'))
        friend = AuthUser.objects.get(pk=friend_pk)
        messages = FriendMessage.objects.filter(Q(sender__in=[request.user, friend])
                                                & Q(receiver__in=[request.user, friend]))
        print(messages)
        return JsonResponse(serializers.serialize('json', messages.order_by('created_at')), safe=False)
    elif type_ == 'lobby':
        pass
    elif type_ == 'game':
        pass

def create_messages(request):
    button_message = request.GET.get('message')
    receiver_pk = int(request.GET.get('receiver'))
    sender_pk = int(request.GET.get('sender'))
    msg = FriendMessage.objects.create(text=button_message, receiver_id=receiver_pk, sender_id=sender_pk)
    # FriendMessage.objects.create(receiver=receiver_pk)
    data = {'action': 'chat_message', 'message': serializers.serialize('json', [msg])}
    layer = get_channel_layer()
    for pk in [sender_pk, receiver_pk]:
        async_to_sync(layer.group_send)(f'user_{pk}', {'type': 'send_message', 'message': data})

    print(msg)
    return JsonResponse({'ok': 'ok'})