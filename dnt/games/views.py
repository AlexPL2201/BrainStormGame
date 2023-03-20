import time
import random
from django.shortcuts import render
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.db.models import Q
from .models import Lobby, Queue, Game
from questions.models import Question, Answer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def create_lobby(request):
    current_user = request.user
    new_lobby = Lobby.objects.create()
    current_user.current_lobby = new_lobby
    current_user.save()
    context = {
        'title': 'Home',
        'user': current_user,

    }
    return render(request, 'games/lobby.html', context=context)


def queue(request):
    max_players = 2
    current_user = request.user
    current_lobby = current_user.current_lobby

    if current_lobby is None:
        current_lobby = Lobby.objects.create()
        current_user.current_lobby = current_lobby
        current_user.save()

    level = current_lobby.get_average_level // 5
    try:
        new_queue = Queue.objects.filter(lowest_level=level).first()
    except:
        new_queue = False

    if not new_queue or new_queue.players_count + current_lobby.players_count > max_players:
        new_queue = Queue.objects.create(lowest_level=level, highest_level=level+5)
    current_lobby.queue = new_queue
    current_lobby.save()

    if new_queue.players_count == max_players:

        return JsonResponse({'result': 'start', 'queue_id': new_queue.pk, 'max_players': max_players})

    return JsonResponse({'result': 'wait', 'queue_id': new_queue.pk, 'max_players': max_players})


def create_game(request):
    queue = request.user.current_lobby.queue
    game = Game.objects.create()

    for lobby in queue.lobbies.all():
        for player in lobby.players.all():
            player.current_game = game
            player.save()
            game.results[player.pk] = 0
        lobby.delete()
    queue.delete()
    game.save()

    url = 'http://' + request.META['HTTP_HOST'] + '/games/game/'
    return JsonResponse({'url': url})


def quit_lobby(request):
    user = request.user
    if user.current_lobby and user.current_lobby.players_count == 1:
        user.current_lobby.delete()
    else:
        user.current_lobby = None
        user.save()
    return JsonResponse({'ok': 'ok'})


def cancel_queue(request):
    request.user.current_lobby.queue = None
    request.user.current_lobby.save()
    return JsonResponse({'ok': 'ok'})


def game(request):

    context = {
        'title': "Игра",
        'game': request.user.current_game,
    }

    return render(request, 'games/game.html', context)


def start_game(request):

    game = request.user.current_game

    if game.players[0] == str(request.user.pk):

        layer = get_channel_layer()
        questions_count = 3
        for _ in range(questions_count):
            time.sleep(5)
            type_answers_count = 0
            question = Question.objects.exclude(pk__in=game.asked_questions.values_list('pk')).order_by('?').first()
            first_answers = Answer.objects.filter(
                Q(subtype=question.answer.subtype) & ~Q(pk=question.answer.pk)
            ).order_by('?')[:2]
            if len(first_answers) != 2:
                type_answers_count += 2 - len(first_answers)
            fourth_answer = Answer.objects.filter(
                Q(subtype__type=question.answer.subtype.type) & ~Q(subtype=question.answer.subtype)
            ).order_by('?')[:1]
            if not fourth_answer:
                type_answers_count += 1
            type_answers = Answer.objects.exclude(subtype=question.answer.subtype).order_by('?')[:type_answers_count]

            answers = first_answers | Answer.objects.filter(pk=question.answer.pk) | fourth_answer | type_answers
            answers = list(answers.values())
            random.shuffle(answers)

            data = {'action': 'get_question', 'question': question.question, 'answers': answers}
            async_to_sync(layer.group_send)(f'game_{game.pk}', {'type': 'send_message', 'message': data})
            time.sleep(10)
            data = {'action': 'get_answer', 'correct_answer': model_to_dict(question.answer)}
            async_to_sync(layer.group_send)(f'game_{game.pk}', {'type': 'send_message', 'message': data})

    return JsonResponse({'ok': 'ok'})
