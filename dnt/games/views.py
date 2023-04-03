import time
import random
import math
from collections import Counter
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Lobby, Queue, Game
from authapp.models import AuthUser
from questions.models import Question, Answer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from variables import *


# view страницы игрового лобби и очереди и создания игрового лобби
def create_lobby(request):

    # создание лобби и добавление его в объект пользователя в качестве current_lobby
    current_user = request.user
    new_lobby = Lobby.objects.create()
    current_user.current_lobby = new_lobby
    current_user.is_lobby_leader = True
    current_user.save()

    context = {
        'title': 'Игровое лобби',
        'user': current_user,
        'modes': Game.types,
        'max_players': GAME_MAX_PLAYERS,
        'users': '',
        'friends': AuthUser.objects.filter(pk__in=current_user.friends.values_list('pk'))
    }
    return render(request, 'games/lobby.html', context=context)


def join_lobby(request):

    sender = AuthUser.objects.get(pk=int(request.GET.get('sender_id')))
    lobby = Lobby.objects.get(pk=sender.current_lobby.pk)

    if lobby.players_count < GAME_MAX_PLAYERS:
        current_user = request.user
        current_user.current_lobby = lobby
        current_user.is_lobby_leader = False
        current_user.save()
        friends = [x[0] for x in current_user.friends.values_list('pk') if x not in [player.pk for player in lobby.players.all()]]

        last_place = True if current_user.current_lobby.players_count == GAME_MAX_PLAYERS else False
        data = {'action': 'player_join', 'joiner_pk': current_user.pk, 'joiner_nickname': current_user.nickname,
                'last_place': last_place}
        layer = get_channel_layer()
        for user in AuthUser.objects.filter(current_lobby=current_user.current_lobby).exclude(pk=current_user.pk):
            async_to_sync(layer.group_send)(f'user_{user.pk}', {'type': 'send_message', 'message': data})

        context = {
            'title': 'Игровое лобби',
            'user': current_user,
            'modes': Game.types,
            'max_players': GAME_MAX_PLAYERS,
            'users': AuthUser.objects.filter(current_lobby=lobby).exclude(pk=current_user.pk),
            'friends': friends
        }

        return HttpResponse(render_to_string('games/lobby.html', context=context))
    else:
        return HttpResponse('full')


def change_game_mode(request):

    new_type = request.GET.get('mode')
    lobby = Lobby.objects.get(pk=request.user.current_lobby.pk)
    lobby.type = [type_ for type_ in lobby.types if type_[0] == new_type][0]
    lobby.save()

    return JsonResponse({'ok': 'ok'})


# view добавления в очередь и проверки количества игроков в ней
def queue(request):

    max_players = GAME_MAX_PLAYERS
    current_user = request.user
    current_lobby = current_user.current_lobby

    # обработка случая обновления страницы, при котором current_lobby у пользователя убирается, а новое не создаётся
    if current_lobby is None:
        current_lobby = Lobby.objects.create()
        current_user.current_lobby = current_lobby
        current_user.save()

    # получение среднего уровня и проверка наличия существующей очереди для этого уровня
    level = current_lobby.get_average_level // QUEUE_LEVEL_RANGE
    try:
        new_queue = Queue.objects.filter(lowest_level=level, type=current_lobby.type).first()
    except:
        new_queue = False

    # если подходящей очереди нет, или если в очереди нет места для всех членов лобби, создаётся новая очередь
    if not new_queue or new_queue.players_count + current_lobby.players_count > max_players:
        new_queue = Queue.objects.create(lowest_level=level, highest_level=level+QUEUE_LEVEL_RANGE,
                                         type=current_lobby.type)

    # лобби добавляется в очередь
    current_lobby.queue = new_queue
    current_lobby.save()

    if current_lobby.players_count > 1:
        data = {'action': 'queue', 'queue_id': new_queue.pk}
        layer = get_channel_layer()
        for user in AuthUser.objects.filter(current_lobby=current_lobby).exclude(pk=current_user.pk):
            async_to_sync(layer.group_send)(f'user_{user.pk}', {'type': 'send_message', 'message': data})

    # если очередь заполнена, отправляется сигнал на запрос на подтверждение для всех пользователей в очереди
    if new_queue.players_count == max_players:
        return JsonResponse({'result': 'start', 'queue_id': new_queue.pk})

    # если нет, отправляется сигнал ждать
    return JsonResponse({'result': 'wait', 'queue_id': new_queue.pk})


# view создания игры
def create_game(request):

    # получается объект очереди, а также создаётся объект игры
    current_queue = request.user.current_lobby.queue
    current_game = Game.objects.create(lowest_level=current_queue.lowest_level,
                                       highest_level=current_queue.highest_level,
                                       type=current_queue.type)

    # объектам всех пользователей в очереди в поле current_game присваивается созданная игра,
    # объекты очереди и всех лобби удаляются
    for lobby in current_queue.lobbies.all():
        for player in lobby.players.all():
            player.current_game = current_game
            player.save()
            current_game.results[player.pk] = {'score': 0, 'answer_time': []}
        lobby.delete()
    current_queue.delete()
    current_game.save()

    # отправляется ссылка для перехода на страницу игры
    url = 'http://' + request.META['HTTP_HOST'] + '/games/game/'
    return JsonResponse({'url': url})


# view выхода из игрового лобби
def quit_lobby(request):

    current_user = request.user

    # если пользователь в лобби один, лобби удаляется, если нет - лобби убирается из current_lobby объекта пользователя
    if current_user.current_lobby and current_user.current_lobby.players_count == 1:
        current_user.current_lobby.delete()
    else:
        data = {'action': 'player_quit', 'quitter_pk': current_user.pk, 'quitter_nickname': current_user.nickname,
                'lobby_leader': False, 'u_r_alone': False}
        layer = get_channel_layer()
        users = AuthUser.objects.filter(current_lobby=request.user.current_lobby).exclude(pk=request.user.pk)
        if current_user.is_lobby_leader:
            new_leader = users.first()
            new_leader.is_lobby_leader = True
            new_leader.save()
            data['lobby_leader'] = True
            data['new_leader_pk'] = new_leader.pk
            data['current_mode'] = current_user.current_lobby.type[0]
        if current_user.current_lobby.players_count == 2:
            data['u_r_alone'] = True
        for user in AuthUser.objects.filter(current_lobby=request.user.current_lobby).exclude(pk=request.user.pk):
            async_to_sync(layer.group_send)(f'user_{user.pk}', {'type': 'send_message', 'message': data})
        current_user.current_lobby = None
        current_user.save()

    # ответ заглушка
    return JsonResponse({'ok': 'ok'})


# view выхода из очереди
def cancel_queue(request):

    # убирание очереди из queue объекта лобби
    request.user.current_lobby.queue = None
    request.user.current_lobby.save()

    # отправка сигнала для выхода из очереди всем игрокам в лобби
    if request.user.current_lobby.players_count > 1:
        data = {'action': 'cancel_queue'}
        layer = get_channel_layer()
        for user in AuthUser.objects.filter(current_lobby=request.user.current_lobby).exclude(pk=request.user.pk):
            async_to_sync(layer.group_send)(f'user_{user.pk}', {'type': 'send_message', 'message': data})

    # ответ заглушка
    return JsonResponse({'ok': 'ok'})


# view страницы игры
def game(request):

    context = {
        'title': "Игра",
        # получение объектов всех игроков игры в алфавитном порядке
        'users': AuthUser.objects.filter(current_game=request.user.current_game).order_by('nickname')
    }

    return render(request, 'games/game.html', context)


# view запуска игры и игрового процесса
def start_game(request):

    current_game = request.user.current_game

    # процесс запуска игры происходит только у одного игрока (возможно стоит переделать)
    if current_game.players[0] == str(request.user.pk):

        # получается количество вопросов и даётся время перед началом игры
        questions_count = GAME_QUESTIONS_COUNT
        time.sleep(GAME_TIME_BEFORE_START)

        # цикл обработки одного вопроса
        for _ in range(questions_count):

            # получение случайного вопроса, которого не было в игре, и добавление его в объект игры в current_question
            question = Question.objects.exclude(pk__in=current_game.asked_questions.values_list('pk')).order_by('?').first()
            current_game = Game.objects.get(pk=request.user.current_game.pk)
            current_game.current_question = question
            current_game.save()

            # определение количества нерправильных ответов относящихся к тому же типу, но не подтипу, что и верный
            type_answers_count = GAME_ANSWERS_COUNT - GAME_SUBTYPE_ANSWERS_COUNT - 1

            # попытка получить нужное количество неправильных ответов того же подтипа, что и верный
            first_answers = Answer.objects.filter(
                Q(subtype=question.answer.subtype) & ~Q(pk=question.answer.pk)
            ).order_by('?')[:GAME_SUBTYPE_ANSWERS_COUNT]

            # компенсация возможного недостатка неправильных ответов того же подтипа неправильными ответами того же типа
            if len(first_answers) != GAME_SUBTYPE_ANSWERS_COUNT:
                type_answers_count += GAME_SUBTYPE_ANSWERS_COUNT - len(first_answers)

            # получение необходимого количества неправильных ответов того же типа
            type_answers = Answer.objects.exclude(subtype=question.answer.subtype).order_by('?')[:type_answers_count]

            # преобразование всех нужных ответов в список словарей и перемешивание их
            answers = first_answers | Answer.objects.filter(pk=question.answer.pk) | type_answers
            answers = list(answers.values())
            random.shuffle(answers)

            # отправка вопроса и ответов пользователям
            data = {'action': 'get_question', 'question': question.question, 'answers': answers}
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(f'game_{current_game.pk}', {'type': 'send_message', 'message': data})

            # даётся время на ответ
            time.sleep(GAME_TIME_TO_ANSWER)

            # добавление вопроса в задаваемые. объект игры достаётся из базы каждый раз заново, потому что его данные
            # меняются и используются в других view и их надо обновлять
            current_game = Game.objects.get(pk=request.user.current_game.pk)
            current_game.asked_questions.add(question)

            # определение самого быстрого правильного ответа и начисление баллов за него
            for player, result in current_game.results.items():
                if len(result['answer_time']) < len(current_game.asked_questions.all()):
                    result['answer_time'].append((False, str(datetime.now())))
            data = {player: datetime.strptime(result['answer_time'][-1][1][:-7], '%Y-%m-%d %H:%M:%S') for player, result
                    in current_game.results.items() if result['answer_time'][-1][0]}
            if data:
                fastest = list(data.keys())[list(data.values()).index(min(data.values()))]
                current_game.results[fastest]['score'] += GAME_POINTS_FOR_FASTEST
            current_game.save()

            # отправка правильного ответа и баллов пользователям
            data = {'action': 'get_answer', 'correct_answer': model_to_dict(question.answer),
                    'score': {player: result['score'] for player, result in current_game.results.items()}}
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(f'game_{current_game.pk}', {'type': 'send_message', 'message': data})

            # даётся время на просмотр верного ответа
            time.sleep(GAME_TIME_SHOW_ANSWER)

        # закрытие игры
        current_game = Game.objects.get(pk=request.user.current_game.pk)
        current_game.is_finished = True

        # функция получения среднего времени правильных ответов
        def average_time(lst):
            return datetime.strftime(datetime.fromtimestamp(sum(map(
                lambda x: datetime.timestamp(datetime.strptime(x[:-7], '%Y-%m-%d %H:%M:%S')), lst)) / len(lst)),
                                     '%Y-%m-%d %H:%M:%S')

        # определение мест
        standings = sorted([(pk, result['score']) for pk, result in current_game.results.items()],
                           key=lambda x: x[1], reverse=True)

        # определение мест при ничьих по очкам на основе времени правильных ответов
        scores = [x[1] for x in standings]
        scores_counter = Counter(scores)
        for score, count in scores_counter.items():
            if count > 1:
                index = scores.index(score)
                standings = standings[:index] + \
                            sorted(standings[index:index + count],
                                   key=lambda x: average_time([x[1] for x in current_game.results[x[0]]['answer_time'] if x[0]])) + \
                            standings[index + count:]

        # занесение мест в результаты игры
        for i, standing in enumerate(standings):
            current_game.results[standing[0]]['place'] = i + 1
        current_game.save()

        # начисление опыта за игру
        for pk, result in current_game.results.items():
            user = AuthUser.objects.get(pk=pk)
            xp = XP_PER_GAME / result['place']
            xp += XP_FIRST_PLACE_BONUS if result['place'] == 1 else 0

            # калибровка опыта в зависимости от уровня игрока относительно уровня игры
            xp_ratio = 1
            if current_game.lowest_level > user.level:
                xp_ratio += XP_OUT_OF_LEVEL_BONUS_RATIO \
                            * math.ceil((current_game.lowest_level - user.level) / QUEUE_LEVEL_RANGE)
            elif current_game.highest_level < user.level:
                xp_ratio -= XP_OUT_OF_LEVEL_BONUS_RATIO \
                            * math.ceil((user.level - current_game.highest_level) / QUEUE_LEVEL_RANGE)
            xp *= xp_ratio

            # добавление опыта пользователю
            user.current_experience += int(xp / max(int(user.level * 0.5), 1))

            # проверка перехода на новый уровень и его реализация
            if user.current_experience >= XP_PER_LEVEL:
                ratio = user.current_experience // XP_PER_LEVEL
                user.current_experience -= XP_PER_LEVEL * ratio
                user.level += ratio

            # убирание объекта игры из current_game всех игроков
            user.current_game = None
            user.save()

        # отправка ссылки для перехода на страницу результатов
        data = {'action': 'show_results',
                'url': f'http://{request.META["HTTP_HOST"]}/games/results/{current_game.pk}/'}
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(f'game_{current_game.pk}', {'type': 'send_message', 'message': data})

    # ответ заглушка
    return JsonResponse({'ok': 'ok'})


# view проверки правильности ответа пользователя
def check_answer(request):

    # определение времени ответа и его получение
    answer_time = datetime.now()
    user = request.user
    current_game = Game.objects.get(pk=user.current_game.pk)
    answer = int(request.GET.get('answer'))
    result = False

    # проверка правильности ответа, начисление баллов и добавление в results времени и правильности ответа
    if current_game.current_question.answer.id == answer:
        current_game.results[str(user.pk)]['score'] += GAME_POINTS_FOR_CORRECT
        result = True
    current_game.results[str(user.pk)]['answer_time'].append((result, str(answer_time)))
    current_game.save()

    # ответ заглушка
    return JsonResponse({'ok': 'ok'})


# view страницы результатов игры
def results(request, game_id):

    # получение объекта нужной игры и всех её игроков
    current_game = Game.objects.get(pk=game_id)
    players = AuthUser.objects.filter(pk__in=current_game.players)

    # создание списка кортежей игрок-место-баллы
    game_results = []

    for player in players:
        game_results.append((player, int(current_game.results[str(player.pk)]['place']), current_game.results[str(player.pk)]['score']))

    context = {
        'title': 'Результаты игры',
        # сортировка спика кортежей по месту
        'results': sorted(game_results, key=lambda x: x[1])
    }

    return render(request, 'games/results.html', context)

