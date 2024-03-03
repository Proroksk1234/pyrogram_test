import asyncio

from pyrogram import types

from app.bot_init.bot_init import client_bot
from app.fsm_context.fsm_context import get_fsm_context


class TelegramUtils:
    """
        Утилита для взаимодействия с Telegram API, отправки сообщений и удаления сообщений.

        Параметры:
        - message: types.Message | types.CallbackQuery: Объект сообщения или коллбэк-запроса в Telegram.
        - text: str: Текст сообщения.
        - chat_ids: list[int] | None: Список ID чатов, в которые нужно отправить сообщение (по умолчанию None).
        - reply_markup: types.ReplyKeyboardMarkup | types.InlineKeyboardMarkup | None: Объект разметки клавиатуры
          (по умолчанию None).
        - resize_keyboard: bool: Флаг изменения размеров клавиатуры (по умолчанию True).

        Методы:
        - send_messages(): Асинхронно отправляет сообщение в указанные чаты с учетом разметки клавиатуры.
        - delete_message(delete_last_messages: bool = False, message_delete_ids: list[int] = None): Асинхронно удаляет
          сообщения из указанных чатов. Может использоваться для удаления текущего сообщения или предыдущих.

        Возвращает:
        - None
    """
    def __init__(
            self, message: types.Message | types.CallbackQuery, text: str, chat_ids: list[int] | None = None,
            reply_markup: types.ReplyKeyboardMarkup | types.InlineKeyboardMarkup | None = None,
            resize_keyboard: bool = True):

        self.message = message
        self.text = text
        self.chat_ids = chat_ids if chat_ids else [message.from_user.id]
        self.reply_markup = reply_markup
        if isinstance(reply_markup, types.ReplyKeyboardMarkup):
            reply_markup.resize_keyboard = resize_keyboard
        asyncio.run(self.delete_message())

    async def send_messages(self) -> None:
        """
            Асинхронно отправляет сообщение(я) в указанные чаты с учетом разметки клавиатуры.

            Возвращает:
            - None
        """
        data = get_fsm_context().get_data(telegram_id=self.message.from_user.id)
        for count, chat_id in enumerate(self.chat_ids):
            message = await client_bot.send_message(reply_markup=self.reply_markup, chat_id=chat_id, text=self.text)
            if isinstance(self.reply_markup, types.InlineKeyboardMarkup):
                if not data.get('list_messages_delete_ids'):
                    data["list_messages_delete_ids"] = list()
                data["list_messages_delete_ids"].append(message.id)
        get_fsm_context().update_data(telegram_id=self.message.from_user.id, data=data)

    async def delete_message(self, delete_last_messages: bool = False, message_delete_ids: list[int] = None) -> None:
        """
            Асинхронно удаляет сообщения из указанных чатов. Может использоваться для удаления текущего сообщения
            или предыдущих.

            Параметры:
            - delete_last_messages: bool: Флаг удаления предыдущих сообщений (по умолчанию False).
            - message_delete_ids: list[int] | None: Список ID сообщений для удаления (по умолчанию None).

            Возвращает:
            - None
        """
        data = get_fsm_context().get_data(telegram_id=self.message.from_user.id)
        if not self.chat_ids:
            return
        if not message_delete_ids and not delete_last_messages:
            message_delete_ids = [self.message.id] if isinstance(self.message, types.Message) else list()
        if data.get('list_messages_delete_ids'):
            message_delete_ids += data.get('list_messages_delete_ids')
            del data["list_messages_delete_ids"]
            get_fsm_context().update_data(telegram_id=self.message.from_user.id, data=data)
        for count, chat_id in enumerate(self.chat_ids):
            await client_bot.delete_messages(chat_id=chat_id, message_ids=message_delete_ids)
