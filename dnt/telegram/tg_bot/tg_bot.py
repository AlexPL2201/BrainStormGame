import asyncio
import json
import random

from django.contrib import auth
from typing import List
from telethon.sync import TelegramClient, events
from telethon.tl.custom import Button

from authapp.models import AuthUser
from games.models import TYPES as GAMES_TYPES
from games.operations import GameProcessForUser
from questions.models import Question, Answer
from questions.operations import SettingRatingToQuestionByUser
from variables import TG_MENU_START_GAME, TG_MENU_PROFILE, TG_MENU_CREATE_QUESTION, TG_MENU_RATE_QUESTIONS, \
    GAME_MAX_PLAYERS, GAME_QUESTIONS_COUNT, TG_LEAVE_QUEUE

MENU_LIST = [TG_MENU_START_GAME, TG_MENU_PROFILE,
             TG_MENU_CREATE_QUESTION, TG_MENU_RATE_QUESTIONS]
MAIN_MENU = [Button.text(button, resize=True) for button in MENU_LIST]
regular_queue = []


class BotLogic:
    # кнопки основного меню (Custom Keyboard), которые выводятся в случае успешной авторизации пользователя
    def __init__(self, bot: TelegramClient, telegram_id: int, telegram_username: str):
        self.bot = bot
        self.telegram_id = telegram_id
        self.telegram_username = telegram_username

    @staticmethod
    async def _get_answer_from_conv(conv: TelegramClient.conversation, question: str):
        """
        Функция-обертка над фрагментом диалога
        (отправит пользователю уведомление, если время ожидания ответа истечет)
        """

        timeout_message = 'Время ответа истекло'
        try:
            await conv.send_message(question)
            answer = await conv.get_response()
            return answer.text
        except Exception as e:
            await conv.send_message(timeout_message)

    @staticmethod
    def _press_event(user_id: int) -> events.CallbackQuery:
        """
        Вспомогательная функция для отслеживания кнопки, нажатой в диалоге
        """
        return events.CallbackQuery(func=lambda e: e.sender_id == user_id)

    @staticmethod
    def _authorize(username: str, password: str) -> bool:
        user = auth.authenticate(username=username, password=password)
        if user:
            return True
        return False

    async def _merge_accounts(self, conv: TelegramClient.conversation) -> None:
        """
        Функция связывания аккаунтов:
        - в случае успешной авторизации аккаунту в базе добавляется переданный telegram id
        """
        username = await self._get_answer_from_conv(conv=conv, question='Введи имя пользователя')
        if username:
            password = await self._get_answer_from_conv(conv=conv, question='Введи пароль')
            if password:
                # Авторизация базовым аккаунтом системы
                authorized = self._authorize(username=username, password=password)

                if authorized:
                    # Добавляем аккаунту telegram id
                    current_user = AuthUser.objects.get(username=username)
                    current_user.telegram_id = self.telegram_id
                    current_user.save()
                    await conv.send_message(
                        f'Аккаунты связаны: login {current_user.username}, telegram_id {current_user.telegram_id}',
                        buttons=MAIN_MENU)
                else:
                    await conv.send_message(f'Неверный логин или пароль')

    async def _create_account(self, conv: TelegramClient.conversation) -> None:
        """
        Функция создания аккаунта в системе на основе telegram id
        """

        nickname = await self._get_answer_from_conv(conv=conv, question='Введи свой ник')
        if nickname:
            password = await self._get_answer_from_conv(conv=conv, question='Введи пароль')
            if password:
                new_user = AuthUser(telegram_id=self.telegram_id, username=self.telegram_username, nickname=nickname)
                new_user.set_password(password)
                new_user.save()
                await conv.send_message(
                    f'Создан новый аккаунт: login {new_user.username}, telegram_id {new_user.telegram_id}',
                    buttons=MAIN_MENU)

    async def send_welcome_back(self):
        await self.bot.send_message(self.telegram_id, 'С возвращением!', buttons=MAIN_MENU)

    async def create_or_merge_account(self):
        """
        Функция создания нового аккаунта на базе telegram id
        или связи telegram id с существующим аккаунтом
        """

        async with self.bot.conversation(self.telegram_id) as conv:
            buttons = [Button.inline('Да, связать аккаунты', b'merge'),
                       Button.inline('Нет, создать аккаунт', b'create')]
            await conv.send_message('Аккаунт не найден. Ты уже регистрировался на сайте?', buttons=buttons)

            try:
                press = await conv.wait_event(self._press_event(self.telegram_id))
                if press.data == b'merge':
                    # связывание аккаунтов
                    await self._merge_accounts(conv)
                elif press.data == b'create':
                    # создание аккаунта
                    await self._create_account(conv)
            except Exception as e:
                pass

    async def rate_questions(self, rating_process: SettingRatingToQuestionByUser):

        def get_question_buttons() -> List[Button]:
            """
            Внутренняя функция для получения актуального состава inline-кнопок.
            Их состав меняется в зависимости от наличия замечаний вообще и наличия замечаний текущего пользователя.
            :return:
            """

            # Базовый набор кнопок вопроса
            question_buttons = [Button.inline('👍', b'like'),
                                Button.inline('👎', b'dislike'),
                                Button.inline('🔚', b'cancel')]

            # Если у вопроса есть замечания, добавляем кнопку для их просмотра
            remarks = rating_process.get_remarks_for_current_question()
            if remarks:
                question_buttons.append(Button.inline(f'👀 {len(remarks)}', b'remarks'), )

            # Если пользователь может добавить замечание (еще не добавлял на этот вопрос), добавляем кнопку для этого
            able_to_add_remark = rating_process.ability_to_remark_question()
            if able_to_add_remark:
                question_buttons.append(Button.inline('✏️', b'add_remark'))

            return question_buttons

        while rating_process.current_question:
            # Пока существует вопрос для оценки (не все вопросы оценены пользователем)

            question = rating_process.current_question.question
            answer = rating_process.current_question.answer.answer
            answer_type = rating_process.current_question.answer.subtype.type.name
            answer_subtype = rating_process.current_question.answer.subtype.name

            # Строка с описанием вопроса для вывода
            question_description_string = f'Вопрос: {question}\nОтвет: {answer}\nТип ответа: {answer_type}\nПодтип ответа: {answer_subtype}'

            async with self.bot.conversation(self.telegram_id) as conv:
                await conv.send_message(question_description_string, buttons=get_question_buttons())

                press = await conv.wait_event(self._press_event(self.telegram_id))
                if press.data == b'like':
                    # Если пользователь нажал Like, добавляем очко вопросу и переходим к следующему
                    rating_process.rate_current_question()
                    rating_process.get_next_question()

                elif press.data == b'dislike':
                    # Если пользователь нажал Like, забираем очко вопросу и переходим к следующему
                    rating_process.rate_current_question(bad=True)
                    rating_process.get_next_question()

                elif press.data == b'remarks':
                    # Выдаем пользователю замечания на оценку
                    for remark in rating_process.get_remarks_for_current_question():
                        remark_text = remark.text
                        remark_buttons = [Button.inline('👍', b'like_remark'),
                                          Button.inline('👎', b'dislike_remark'),
                                          Button.inline('🔚', b'cancel_remark')]
                        await conv.send_message(f'Замечание: {remark_text}', buttons=remark_buttons)

                        press = await conv.wait_event(self._press_event(self.telegram_id))
                        if press.data == b'like_remark':
                            # Если пользователь нажал Like, добавляем очко замечанию и переходим к следующему
                            rating_process.rate_remark(remark=remark)
                            await conv.send_message('Like замечания принят')
                            continue
                        elif press.data == b'dislike_remark':
                            # Если пользователь нажал Dislike, забираем очко у замечания и переходим к следующему
                            rating_process.rate_remark(remark=remark, bad=True)
                            await conv.send_message('Dislike замечания принят')
                            continue
                        elif press.data == b'cancel_remark':
                            # Если пользователь закончил смотреть замечания, возвращаемся к вопросу
                            await conv.send_message(question_description_string, buttons=get_question_buttons())
                            break

                    else:
                        # Если замечания закончились, возвращаемся к вопросу
                        pass  # получалось дублирование сообщений, этот шаг лишний, TODO разобраться получше
                        # await conv.send_message(question_description_string, buttons=get_question_buttons())

                elif press.data == b'add_remark':
                    # Если пользователь нажал добавление замечания, берем текст и добавлем замечание
                    remark_text = await self._get_answer_from_conv(conv=conv, question='Введи текст замечания')
                    if remark_text:
                        rating_process.add_remark_to_current_question(text=remark_text)

                elif press.data == b'cancel':
                    # Пользователь закончил оценку вопросов
                    await conv.send_message('Оценка вопросов завершена')
                    await conv.cancel()

    async def _add_to_regular_queue(self):
        # Добавление пользователя в очередь для обычной игры
        global regular_queue
        if self.telegram_id in regular_queue:
            await self.bot.send_message(self.telegram_id, 'Вы уже находитесь в очереди.')
        else:
            regular_queue.append(self.telegram_id)
            await self.bot.send_message(self.telegram_id,
                                        'Вы добавлены в очередь для обычной игры. Подождите, пока найдется противник.')

    async def remove_from_regular_queue(self):
        global regular_queue
        if self.telegram_id in regular_queue:
            regular_queue.remove(self.telegram_id)
            await self.bot.send_message(self.telegram_id, 'Вы удалены из очереди', buttons=MAIN_MENU)
        else:
            await self.bot.send_message(self.telegram_id, 'Вы не состоите в очереди', buttons=MAIN_MENU)

    async def _show_lobby(self):

        game_type_buttons = [[Button.text(game_type[1], resize=True)] for game_type in GAMES_TYPES]
        game_type_buttons.append([Button.text('Назад', resize=True)])

        await self.bot.send_message(self.telegram_id, 'Выберите тип игры:', buttons=game_type_buttons)

        async with self.bot.conversation(self.telegram_id) as conv:
            while True:
                try:
                    message_pattern = '^(' + '|'.join(game_type[1] for game_type in GAMES_TYPES) + ')$'  # TODO
                    response = await conv.wait_event(
                        events.NewMessage(pattern='^(Обычная|Тематическая|Дружеская|Назад)$'))
                    if response.text == 'Обычная':
                        await response.respond('Вы выбрали режим "Обычная".', buttons=Button.text(TG_LEAVE_QUEUE))
                        await self._add_to_regular_queue()
                        # print(f"Добавлен пользователь {event.sender_id} в очередь")
                        break
                    elif response.text == 'Назад':
                        await conv.send_message('Ну как хотите', buttons=MAIN_MENU)
                        break
                    else:
                        await response.respond('К сожалению, этот тип игры пока недоступен.')
                except asyncio.TimeoutError:
                    await conv.send_message('Я не получил ответа, попробуйте снова.')
                    break

    async def play_game(self, game_process: GameProcessForUser):
        await self._show_lobby()


class TelegramGame:

    def __init__(self, bot: TelegramClient):
        self.bot = bot

    async def _answering_to_questions(self, player):
        questions = Question.objects.all()
        answers = Answer.objects.all()
        player_score = 0

        questions_to_ask = []
        while len(questions_to_ask) < GAME_QUESTIONS_COUNT:
            buf = random.choice(questions)
            if buf in questions_to_ask:
                pass
            else:
                questions_to_ask.append(buf)

        async with self.bot.conversation(player) as conv:
            for i in range(GAME_QUESTIONS_COUNT):
                question = questions_to_ask[i]

                answer_buttons = [[Button.text(str(question.answer))]]
                for random_answer in random.sample(list(answers), 3):
                    answer_buttons.append([Button.text(random_answer.answer)])

                random.shuffle(answer_buttons)
                await conv.send_message(str(question.question), buttons=answer_buttons)
                response = await conv.wait_event(events.NewMessage(incoming=True, from_users=player))
                # Получаем текст ответа
                text = response.message.text
                if text == str(question.answer):
                    await conv.send_message('Верно!')
                    player_score += 1
                else:
                    await conv.send_message(f"Увы, \n правильный ответ: \n{question.answer} ")

            return player_score

    async def _start_regular_game(self, players: list):

        # Получаем имена игроков
        player_objs = []
        for player in players:
            player_obj = {'telegram_id': player, 'nickname': AuthUser.objects.get(telegram_id=player).nickname}
            player_objs.append(player_obj)

        scores = []

        for player_obj in player_objs:
            others_list = [player_obj_['nickname'] for player_obj_ in player_objs if
                           player_obj_['telegram_id'] != player_obj['telegram_id']]
            await self.bot.send_message(player_obj['telegram_id'],
                                        f"Игра начинается! Вы играете против {', '.join(others_list)}.")

            player_obj['task'] = asyncio.create_task(self._answering_to_questions(player_obj['telegram_id']))

        for player_obj in player_objs:
            player_score = await player_obj['task']
            player_obj['score'] = player_score

        winner = player_objs[0]
        for player_obj in player_objs[1:]:
            if player_obj['score'] > winner['score']:
                winner = player_obj

        await self.bot.send_message(winner['telegram_id'],
                                    f'Игра окончена: ПОБЕДА! (правильных ответов: {winner["score"]})',
                                    buttons=MAIN_MENU)
        for player_obj in player_objs:
            if player_obj != winner:
                await self.bot.send_message(player_obj['telegram_id'],
                                            f'Игра окончена: ПОРАЖЕНИЕ. (правильных ответов: {player_obj["score"]})',
                                            buttons=MAIN_MENU)

        # Тут нужно победителю начислитиь опыт.

    async def matchmaking(self):
        tasks = []
        while True:
            if len(regular_queue) >= GAME_MAX_PLAYERS:
                players = []
                while len(players) < GAME_MAX_PLAYERS:
                    players.append(regular_queue.pop(0))
                task = asyncio.create_task(self._start_regular_game(players=players))
                tasks.append(task)
                await asyncio.gather(*tasks)
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    tasks.remove(task)
            else:
                await asyncio.sleep(1)
