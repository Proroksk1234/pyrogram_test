"""
Модуль для обработки событий и команд бота.

Этот модуль содержит код для обработки различных событий и команд, таких как старт, удаление аккаунта и др.


"""

from pyrogram import filters, Client, types

from app.auth_manager import auth_controller
from app.bot_init.bot_init import client_bot
from app.fsm_context.fsm_context import get_fsm_context
from app.root.controller import send_message_start
from app.root.filters import get_filters
from app.tasks_manager import tasks_controller
from app.utils import TelegramUtils


@client_bot.on_callback_query(filters.regex("main_menu"))
@client_bot.on_message(filters.text & (filters.regex("В главное меню") | filters.command("start")))
async def handler_start(_: Client, message: types.Message | types.CallbackQuery, owner_telegram_id: int = None) -> None:
    """
    Обработчик команды /start и нажатия на кнопку "В главное меню".

    Параметры:
        _: Экземпляр клиента Pyrogram (не используется).
        message: Объект сообщения или запроса обратного вызова.
        owner_telegram_id (int, optional): Идентификатор владельца аккаунта (необязательно).

    Возвращает:
        None

    """
    await send_message_start(_=_, message=message, owner_telegram_id=owner_telegram_id)


@client_bot.on_message(filters.text & filters.regex("Удалить аккаунт"))
async def confirm_delete_account_user(_: Client, message: types.Message) -> None:
    """
    Подтверждение удаления аккаунта пользователя.

    Параметры:
        _: Экземпляр клиента Pyrogram.
        message: Объект сообщения.

    Возвращает:
        None

    """
    data = get_fsm_context().get_data(telegram_id=message.from_user.id)
    reply_markup = None
    if not data.get('owner_telegram_id') or not auth_controller.check_user_is_owner(
            user_telegram_id=message.from_user.id, owner_telegram_id=data.get('owner_telegram_id')):
        text_message = "Вы не имеете доступ к данному функционалу"
    else:
        text_message = (
            "Вы точно уверены, что хотите удалить аккаунт?"
        )
        inline_keyboard = list()
        inline_keyboard.append([types.InlineKeyboardButton(
            text="Удалить аккаунт", callback_data=f"delete_account:{data.get('owner_telegram_id')}")])
        inline_keyboard.append([types.InlineKeyboardButton(
            text="Вернуться в главное меню", callback_data=f"main_menu:{data.get('owner_telegram_id')}")])
        reply_markup = types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    get_fsm_context().update_state(telegram_id=message.from_user.id, state="main_menu")
    telegram_utils = TelegramUtils(text=text_message, reply_markup=reply_markup, message=message)
    await telegram_utils.send_messages()
    if not reply_markup:
        await send_message_start(_=_, message=message)


@client_bot.on_callback_query(filters.regex("delete_account:") & (
        get_filters().message_filter(state="registration_authorization")
        | get_filters().message_filter(state="main_menu")))
async def delete_account_user(client: Client, message: types.CallbackQuery) -> None:
    """
    Удаление аккаунта пользователя.

    Параметры:
        client: Экземпляр клиента Pyrogram.
        message: Объект запроса обратного вызова.

    Возвращает:
        None

    """
    owner_telegram_id = int(message.data.split(":")[-1])
    if auth_controller.check_user_is_owner(user_telegram_id=message.from_user.id, owner_telegram_id=owner_telegram_id):
        auth_controller.delete_user(owner_telegram_id=owner_telegram_id)
        tasks_controller.delete_task(owner_telegram_id=owner_telegram_id)
        text_message = (
            "Привязанный аккаунт был успешно удален"
        )
        data = dict()
        data["list_messages_delete_ids"] = get_fsm_context().get_data(
            telegram_id=message.from_user.id).get('list_messages_delete_ids')
        get_fsm_context().clear(telegram_id=message.from_user.id)
        get_fsm_context().update_data(telegram_id=message.from_user.id, data=data)
    else:
        text_message = (
            "Вы не имеете доступ к данному действию"
        )
    telegram_utils = TelegramUtils(text=text_message, message=message)
    await telegram_utils.send_messages()
    return await handler_start(_=client, message=message)