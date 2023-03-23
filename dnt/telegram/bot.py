import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnt.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from telethon.sync import TelegramClient, events
from telegram.tg_bot.tg_bot import BotLogic
import authapp
from authapp.models import AuthUser
from questions.operations import SettingRatingToQuestionByUser, UserLevelTooLow, NoUnratedQuestionsForUser
from telethon.tl.custom import Button


BOT_TOKEN = os.environ['BOT_TOKEN']
API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']


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

        # кнопки основного меню (Custom Keyboard), которые выводятся в случае успешной авторизации пользователя
        menu_buttons = [Button.text('Создать вопрос', resize=True),
                        Button.text('Оценить вопросы', resize=True),
                        Button.text('Начать игры', resize=True),
                        Button.text('Профиль', resize=True)]

        if message.text == '/start':
            try:
                AuthUser.objects.get(telegram_id=telegram_id)
                # если в БД есть пользователь с таким telegram_id
                await bot_logic.send_welcome_back(menu_buttons)

            except authapp.models.AuthUser.DoesNotExist:
                # если в БД нет пользователя с таким telegram_id
                await bot_logic.create_or_merge_account(menu_buttons)

        elif message.text == '/rate':
            try:
                user = AuthUser.objects.get(telegram_id=telegram_id)
                rating_process = SettingRatingToQuestionByUser(user)
                await bot_logic.rate_questions(rating_process)

            except UserLevelTooLow:
                await bot.send_message(telegram_id, 'Твоего уровня недостаточно для оценки вопросов')
            except NoUnratedQuestionsForUser:
                await bot.send_message(telegram_id, 'Ты уже оценил все вопросы')

    bot.start()
    bot.run_until_disconnected()


if __name__ == "__main__":

    try:
        work_with_chat(API_ID, API_HASH, BOT_TOKEN)
    except Exception as e:
        print(e.__class__.__name__, e)
