"""
Модуль для создания динамических фильтров Pyrogram.

Этот модуль содержит код для создания динамических фильтров Pyrogram,
основанных на состоянии конечного автомата (FSM) пользователей.

Параметры:
    _filters (Filters): Статический объект Filters для управления динамическими фильтрами.

"""

from pyrogram import filters, types
from pyrogram.filters import Filter

from app.fsm_context.fsm_context import get_fsm_context


class Filters:
    """
    Класс для создания динамических фильтров Pyrogram на основе состояния конечного автомата (FSM) пользователей.

    Параметры:
        __instance (Filters): Единственный экземпляр Filters.

    Methods:
        __new__(*args, **kwargs): Создает и возвращает единственный экземпляр класса Filters.
        __init__(): Инициализация объекта Filters.
        __message_dynamic_filter(state: str, is_regex: bool = False) -> Filter: Приватный метод для
            создания фильтра на основе состояния FSM.

    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        Создает и возвращает единственный экземпляр класса Filters.

        Возвращает:
            Filters: Единственный экземпляр класса Filters.

        """
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        """
        Инициализация объекта Filters.

        """
        self.message_filter = self.__message_dynamic_filter

    @staticmethod
    def __message_dynamic_filter(state: str, is_regex: bool = False) -> Filter:
        """
        Приватный метод для создания динамического фильтра Pyrogram на основе состояния FSM.

        Параметры:
            state (str): Состояние конечного автомата (FSM).
            is_regex (bool): Флаг, указывающий, является ли состояние регулярным выражением.

        Возвращает:
            Filter: Динамический фильтр Pyrogram.

        """

        async def __func(flt: filters, __, message: types.Message | types.CallbackQuery) -> bool:
            user_fsm_state_object = get_fsm_context().get_list_fsm_contexts().get(message.from_user.id)
            user_state = str() if not user_fsm_state_object else user_fsm_state_object.state
            if is_regex:
                return flt.state in user_state
            return flt.state == user_state

        return filters.create(__func, state=state, is_regex=is_regex)


_filters: Filters = Filters()


def get_filters() -> Filters:
    """
    Получение объекта Filters.

    Возвращает:
        Filters: Объект Filters.

    """
    return _filters
