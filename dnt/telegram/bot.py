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

# BOT_TOKEN = os.environ['BOT_TOKEN']
# API_ID = os.environ['API_ID']
# API_HASH = os.environ['API_HASH']
BOT_TOKEN='1208251813:AAHDznm1Rugi6Uu5sgSJ_Olc6_3gkMWhsts'
API_ID = 1819249
API_HASH = '9da3041ebb4fe58a85263a92d8c15f72'


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
