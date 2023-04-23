import os

import django

from games.operations import GameProcessForUser

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnt.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from telethon.sync import TelegramClient, events
from telegram.tg_bot.tg_bot import BotLogic, TelegramGame
import authapp
from authapp.models import AuthUser
from questions.operations import SettingRatingToQuestionByUser, UserLevelTooLow, NoUnratedQuestionsForUser
from variables import TG_MENU_START_GAME, TG_MENU_PROFILE, TG_MENU_CREATE_QUESTION, TG_MENU_RATE_QUESTIONS, \
    TG_LEAVE_QUEUE

BOT_TOKEN = os.environ['BOT_TOKEN']
API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']

MENU_BUTTONS = [TG_MENU_START_GAME, TG_MENU_PROFILE,
                TG_MENU_CREATE_QUESTION, TG_MENU_RATE_QUESTIONS]


def work_with_chat(api_id: int, api_hash: str, bot_token: str, session_file='bot') -> None:
    """
    Основная функция-обработчик общения пользователей с ботом
    """

    bot = TelegramClient(os.path.join('sessions', session_file), api_id, api_hash).start(bot_token=bot_token)

    @bot.on(events.NewMessage)
    async def handler(event):
        message = event.message
        telegram_id = message.chat.id

        bot_logic = BotLogic(bot=bot,
                             telegram_id=telegram_id,
                             telegram_username=message.chat.username)

        if message.text == '/start':
            try:
                AuthUser.objects.get(telegram_id=telegram_id)
                # если в БД есть пользователь с таким telegram_id
                await bot_logic.send_welcome_back()

            except authapp.models.AuthUser.DoesNotExist:
                # если в БД нет пользователя с таким telegram_id
                await bot_logic.create_or_merge_account()

        elif message.text == TG_MENU_START_GAME:
            try:
                user = AuthUser.objects.get(telegram_id=telegram_id)
                game_process = GameProcessForUser(user)
                await bot_logic.play_game(game_process)
            except Exception as e:
                print(e, e.__class__.__name__)

        elif message.text == TG_LEAVE_QUEUE:
            await bot_logic.remove_from_regular_queue()

        elif message.text == TG_MENU_RATE_QUESTIONS:
            try:
                user = AuthUser.objects.get(telegram_id=telegram_id)
                rating_process = SettingRatingToQuestionByUser(user)
                await bot_logic.rate_questions(rating_process)

            except UserLevelTooLow:
                await bot.send_message(telegram_id, 'Твоего уровня недостаточно для оценки вопросов')
            except NoUnratedQuestionsForUser:
                await bot.send_message(telegram_id, 'Ты уже оценил все вопросы')

        elif message.text == TG_MENU_PROFILE:
            user = AuthUser.objects.get(telegram_id=telegram_id)
            user_profile = f'__Данные:__\n\n' \
                           f'  Имя пользователя: {user.username}\n' \
                           f'  Никнэйм: **{user.nickname}**\n' \
                           f'  Присоединился: __{str(user.date_joined)[:10]}__\n\n' \
                           f'__Характеристики:__\n\n' \
                           f'  Уровень: **{user.level}**\n' \
                           f'  Опыт текущего уровня: {user.current_experience}\n' \
                           f'  Ранг: {user.rank.split(",")[1].replace(")", "")}\n' \
                           f'  Дивизион: {user.division}'

            await bot.send_message(telegram_id, user_profile)

    bot.start()
    game = TelegramGame(bot=bot)
    bot.loop.create_task(game.matchmaking())
    bot.run_until_disconnected()

if __name__ == "__main__":

    try:
        work_with_chat(API_ID, API_HASH, BOT_TOKEN)
    except Exception as e:
        print(e.__class__.__name__, e)
