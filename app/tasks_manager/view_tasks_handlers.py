from pyrogram import filters, Client, types

from app.bot_init.bot_init import client_bot
from app.db.models import UserTasks
from app.fsm_context.fsm_context import get_fsm_context
from app.root.filters import get_filters
from app.tasks_manager import tasks_controller
from app.tasks_manager.handlers import get_back_buttons
from app.utils import TelegramUtils


@client_bot.on_callback_query(filters.regex("tasks:view_tasks:") & get_filters().message_filter(state="tasks"))
async def view_tasks(_: Client, message: types.CallbackQuery) -> None:
    """
        Обрабатывает запрос пользователя на просмотр задач в зависимости от выбранной опции.

        Параметры:
        - _: Client: Объект клиента Pyrogram (не используется в функции).
        - message: types.CallbackQuery: Объект сообщения типа CallbackQuery в Telegram.

        Действия:
        - Извлекает ID пользователя из callback_data.
        - Формирует текстовое сообщение с доступными опциями просмотра задач.
        - Создает инлайн-клавиатуру с опциями просмотра задач и кнопкой "Назад".
        - Отправляет сообщение с клавиатурой пользователю.
        - Обновляет состояние конечного автомата на "tasks:view".

        Возвращает:
        - None
    """
    owner_telegram_id = int(message.data.split(":")[-1])
    text_message = (
        "В данном меню вы можете:\n\n"
        "1) Просмотреть все действующие задачи\n"
        "2) Просмотреть все выполненные задачи\n"
        "3) Просмотреть все просроченные задачи\n"
        "4) Просмотреть все задачи\n"
    )
    inline_keyboard = list()
    inline_keyboard.append([types.InlineKeyboardButton(
        text="Просмотреть все действующие задачи",
        callback_data=f"tasks:view_current_tasks:{owner_telegram_id}")])
    inline_keyboard.append([types.InlineKeyboardButton(
        text="Просмотреть все выполненные задачи",
        callback_data=f"tasks:view_completed_tasks:{owner_telegram_id}")])
    inline_keyboard.append([types.InlineKeyboardButton(
        text="Просмотреть все просроченные задачи",
        callback_data=f"tasks:view_overdue_tasks:{owner_telegram_id}")])
    inline_keyboard.append([types.InlineKeyboardButton(
        text="Просмотреть все задачи",
        callback_data=f"tasks:view_all_tasks:{owner_telegram_id}")])
    inline_keyboard += (get_back_buttons(owner_telegram_id=owner_telegram_id)).inline_keyboard
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    telegram_utils = TelegramUtils(text=text_message, reply_markup=reply_markup, message=message)
    await telegram_utils.send_messages()
    get_fsm_context().update_state(telegram_id=message.from_user.id, state="tasks:view")


@client_bot.on_callback_query(
    filters.regex("tasks:view_current_tasks:") & get_filters().message_filter(state="tasks:view"))
async def get_all_current_tasks(_: Client, message: types.CallbackQuery) -> None:
    """
        Обрабатывает запрос пользователя на просмотр всех текущих задач.

        Параметры:
        - _: Client: Объект клиента Pyrogram (не используется в функции).
        - message: types.CallbackQuery: Объект сообщения типа CallbackQuery в Telegram.

        Действия:
        - Получает список текущих задач пользователя.
        - Отправляет сообщение с информацией о текущих задачах.
        - Вызывает функцию view_tasks для возврата к меню просмотра задач.

        Возвращает:
        - None
    """
    list_user_tasks: list[UserTasks] = tasks_controller.get_all_tasks(
        owner_telegram_id=int(message.data.split(":")[-1]), current_tasks=True)
    await tasks_controller.send_messages_get_all_tasks(list_tasks=list_user_tasks, message=message)
    await view_tasks(_=_, message=message)


@client_bot.on_callback_query(
    filters.regex("tasks:view_completed_tasks:") & get_filters().message_filter(state="tasks:view"))
async def get_all_completed_tasks(_: Client, message: types.CallbackQuery) -> None:
    """
        Обрабатывает запрос пользователя на просмотр всех выполненных задач.

        Параметры:
        - _: Client: Объект клиента Pyrogram (не используется в функции).
        - message: types.CallbackQuery: Объект сообщения типа CallbackQuery в Telegram.

        Действия:
        - Получает список выполненных задач пользователя.
        - Отправляет сообщение с информацией о выполненных задачах.
        - Вызывает функцию view_tasks для возврата к меню просмотра задач.

        Возвращает:
        - None
    """
    list_user_tasks: list[UserTasks] = tasks_controller.get_all_tasks(
        owner_telegram_id=int(message.data.split(":")[-1]), completed_tasks=True)
    await tasks_controller.send_messages_get_all_tasks(list_tasks=list_user_tasks, message=message)
    await view_tasks(_=_, message=message)


@client_bot.on_callback_query(
    filters.regex("tasks:view_overdue_tasks:") & get_filters().message_filter(state="tasks:view"))
async def get_all_overdue_tasks(_: Client, message: types.CallbackQuery) -> None:
    """
        Обрабатывает запрос пользователя на просмотр всех просроченных задач.

        Параметры:
        - _: Client: Объект клиента Pyrogram (не используется в функции).
        - message: types.CallbackQuery: Объект сообщения типа CallbackQuery в Telegram.

        Действия:
        - Получает список просроченных задач пользователя.
        - Отправляет сообщение с информацией о просроченных задачах.
        - Вызывает функцию view_tasks для возврата к меню просмотра задач.

        Возвращает:
        - None
    """
    list_user_tasks: list[UserTasks] = tasks_controller.get_all_tasks(
        owner_telegram_id=int(message.data.split(":")[-1]), overdue_tasks=True)
    await tasks_controller.send_messages_get_all_tasks(list_tasks=list_user_tasks, message=message)
    await view_tasks(_=_, message=message)


@client_bot.on_callback_query(filters.regex("tasks:view_all_tasks:") & get_filters().message_filter(state="tasks:view"))
async def get_all_tasks(_: Client, message: types.CallbackQuery) -> None:
    """
        Обрабатывает запрос пользователя на просмотр всех задач.

        Параметры:
        - _: Client: Объект клиента Pyrogram (не используется в функции).
        - message: types.CallbackQuery: Объект сообщения типа CallbackQuery в Telegram.

        Действия:
        - Получает список всех задач пользователя.
        - Отправляет сообщение с информацией о всех задачах.
        - Вызывает функцию view_tasks для возврата к меню просмотра задач.

        Возвращает:
        - None
    """
    list_user_tasks: list[UserTasks] = tasks_controller.get_all_tasks(
        owner_telegram_id=int(message.data.split(":")[-1]))
    await tasks_controller.send_messages_get_all_tasks(list_tasks=list_user_tasks, message=message)
    await view_tasks(_=_, message=message)
