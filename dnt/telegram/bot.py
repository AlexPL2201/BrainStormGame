import os

import django
from django.contrib import auth

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnt.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from telethon.sync import TelegramClient, events
from telethon.tl.custom import Button
import authapp
from authapp.models import AuthUser
from dnt.settings import BOT_TOKEN, API_ID, API_HASH


class BotLogic:

    def __init__(self, bot: TelegramClient, telegram_id: int, telegram_username: str):
        self.bot = bot
        self.telegram_id = telegram_id
        self.telegram_username = telegram_username

    @staticmethod
    async def _get_answer_from_conv(conv: TelegramClient.conversation, question: str):
        """
        Функция-обертка над фрагментом диалога
        (отправит пользователю уведомление, есил время ожилания ответа истечет)
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
                        f'Аккаунты связаны: login {current_user.username}, telegram_id {current_user.telegram_id}')
                else:
                    await conv.send_message(f'Неверный логин или пароль')

    async def _create_account(self, conv: TelegramClient.conversation) -> None:
        """
        Функция создания аккаунта в системе на основе telegram id
        """

        new_user = AuthUser(telegram_id=self.telegram_id, username=self.telegram_username)
        new_user.save()
        await conv.send_message(f'Создан новый аккаунт: login {new_user.username}, telegram_id {new_user.telegram_id}')

    async def send_welcome_back(self):
        await self.bot.send_message(self.telegram_id, 'С возвращением!')

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

    bot.start()
    bot.run_until_disconnected()


if __name__ == "__main__":

    try:
        work_with_chat(API_ID, API_HASH, BOT_TOKEN)
    except Exception as e:
        print(e.__class__.__name__, e)
