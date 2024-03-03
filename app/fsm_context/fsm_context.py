"""
    Модуль, содержащий класс FSM (Конечный Автомат) и функцию для инициализации экземпляра FSM.

    Класс FSM предоставляет методы для работы с таблицей fsm_context в базе данных,
    представляющей контекст конечного автомата для пользователей.

    Функция fsm_context_init и глобальная переменная _fsm_context используются для инициализации
    единственного экземпляра FSM при старте приложения.

"""

import json

from sqlalchemy import text

from app.db.db_config import Session
from app.db.models import FSMContext


class FSM:
    """
    Класс для управления состояниями конечного автомата (FSM) для пользователей.

    Параметры:
        __list_fsm_contexts (dict[int, FSMContext]):
            Словарь, содержащий FSMContext объекты для каждого пользователя.

    Methods:
        get_list_fsm_contexts(): Получает словарь FSMContext объектов для всех пользователей.
        __update_list_fsm_contexts(): Приватный метод для обновления списка FSMContext объектов из базы данных.
        __get_fsm_context(telegram_id: int) -> FSMContext | None: Приватный метод для получения FSMContext
            объекта для пользователя.
        __set_fsm_context(telegram_id: int, state: str, data: dict) -> None: Приватный метод для
            установки нового FSMContext объекта в базе данных.
        __update_fsm_context(telegram_id: int, state: str, data: dict) -> None: Приватный метод для
            обновления существующего FSMContext объекта в базе данных.
        __delete_fsm_context(telegram_id: int) -> None: Приватный метод для удаления FSMContext
            объекта из базы данных.
        get_state(telegram_id: int) -> str | None: Получает текущее состояние пользователя в FSM.
        update_state(telegram_id: int, state: str) -> None: Обновляет состояние пользователя в FSM.
        get_data(telegram_id: int) -> dict: Получает дополнительные данные пользователя в FSM.
        update_data(telegram_id: int, data: dict) -> dict: Обновляет дополнительные данные пользователя в FSM.
        clear(telegram_id: int) -> None: Очищает FSMContext объект для пользователя.

    """

    def __init__(self):
        """
        Инициализация объекта FSM.

        """
        self.__list_fsm_contexts: dict[int, FSMContext] = dict()
        self.__update_list_fsm_contexts()

    def get_list_fsm_contexts(self) -> dict[int, FSMContext]:
        """
        Получает словарь FSMContext объектов для всех пользователей.

        Возвращает:
            dict[int, FSMContext]: Словарь FSMContext объектов для всех пользователей.

        """
        return self.__list_fsm_contexts

    def __update_list_fsm_contexts(self) -> None:
        """
        Приватный метод для обновления списка FSMContext объектов из базы данных.

        """
        with Session() as session:
            query = text("SELECT * FROM fsm_context")
            fsm_context_list: list[FSMContext] = session.execute(query).all()
        self.__list_fsm_contexts: dict[int, FSMContext] = {x.telegram_id: x for x in fsm_context_list}

    @staticmethod
    def __get_fsm_context(telegram_id: int) -> FSMContext | None:
        """
        Приватный метод для получения FSMContext объекта для пользователя.

        Параметры:
            telegram_id (int): Идентификатор пользователя в Telegram.

        Возвращает:
            FSMContext | None: Объект FSMContext или None, если объект не найден.

        """
        with Session() as session:
            query = text("SELECT * FROM fsm_context WHERE telegram_id=:telegram_id")
            fsm_context: FSMContext | None = session.execute(query, {"telegram_id": telegram_id}).first()
        return fsm_context

    def __set_fsm_context(self, telegram_id: int, state: str, data: dict) -> None:
        """
        Приватный метод для установки нового FSMContext объекта в базе данных.

        Параметры:
            telegram_id (int): Идентификатор пользователя в Telegram.
            state (str): Новое состояние пользователя в FSM.
            data (dict): Новые дополнительные данные пользователя в FSM.

        """
        with Session() as session:
            query = text("INSERT INTO fsm_context VALUES (:telegram_id, :state, :data)")
            session.execute(query, {"telegram_id": telegram_id, "state": state, "data": json.dumps(data)})
            session.commit()
        self.__list_fsm_contexts[telegram_id] = self.__get_fsm_context(telegram_id=telegram_id)

    def __update_fsm_context(self, telegram_id: int, state: str, data: dict) -> None:
        """
        Приватный метод для обновления существующего FSMContext объекта в базе данных.

        Параметры:
            telegram_id (int): Идентификатор пользователя в Telegram.
            state (str): Новое состояние пользователя в FSM.
            data (dict): Новые дополнительные данные пользователя в FSM.

        """
        with Session() as session:
            query = text("UPDATE fsm_context SET state=:state, data=:data WHERE telegram_id=:telegram_id")
            session.execute(query, {"telegram_id": telegram_id, "state": state, "data": json.dumps(data)})
            session.commit()
        self.__list_fsm_contexts[telegram_id] = self.__get_fsm_context(telegram_id=telegram_id)

    def __delete_fsm_context(self, telegram_id: int) -> None:
        """
        Приватный метод для удаления FSMContext объекта из базы данных.

        Параметры:
            telegram_id (int): Идентификатор пользователя в Telegram.

        """
        with Session() as session:
            query = text("DELETE FROM fsm_context WHERE telegram_id=:telegram_id")
            session.execute(query, {"telegram_id": telegram_id})
            session.commit()
        del self.__list_fsm_contexts[telegram_id]

    def get_state(self, telegram_id: int) -> str | None:
        """
        Получает текущее состояние пользователя в FSM.

        Параметры:
            telegram_id (int): Идентификатор пользователя в Telegram.

        Возвращает:
            str | None: Состояние пользователя в FSM или None, если объект не найден.

        """
        if self.__list_fsm_contexts.get(telegram_id):
            return self.__list_fsm_contexts[telegram_id].state

    def update_state(self, telegram_id: int, state: str) -> None:
        """
        Обновляет состояние пользователя в FSM.

        Параметры:
            telegram_id (int): Идентификатор пользователя в Telegram.
            state (str): Новое состояние пользователя в FSM.

        Возвращает:
            None

        """
        fsm_context: FSMContext | None = self.__get_fsm_context(telegram_id=telegram_id)
        if fsm_context:
            self.__update_fsm_context(telegram_id=telegram_id, state=state, data=fsm_context.data)
        else:
            self.__set_fsm_context(telegram_id=telegram_id, state=state, data=dict())

    def get_data(self, telegram_id: int) -> dict:
        """
        Получает дополнительные данные пользователя в FSM.

        Параметры:
            telegram_id (int): Идентификатор пользователя в Telegram.

        Возвращает:
            dict: Дополнительные данные пользователя в FSM или пустой словарь, если объект не найден.

        """
        return self.__list_fsm_contexts[telegram_id].data if self.__list_fsm_contexts.get(telegram_id) else dict()

    def update_data(self, telegram_id: int, data: dict) -> dict:
        """
        Обновляет дополнительные данные пользователя в FSM.

        Параметры:
            telegram_id (int): Идентификатор пользователя в Telegram.
            data (dict): Новые дополнительные данные пользователя в FSM.

        Возвращает:
            dict: Обновленные дополнительные данные пользователя в FSM.

        """
        fsm_context: FSMContext | None = self.__get_fsm_context(telegram_id=telegram_id)
        if fsm_context:
            self.__update_fsm_context(telegram_id=telegram_id, data=data, state=fsm_context.state)
        else:
            self.__set_fsm_context(telegram_id=telegram_id, data=data, state=str())
        return self.get_data(telegram_id=telegram_id)

    def clear(self, telegram_id: int) -> None:
        """
        Очищает FSMContext объект для пользователя.

        Параметры:
            telegram_id (int): Идентификатор пользователя в Telegram.

        Возвращает:
            None

        """
        self.__update_fsm_context(telegram_id=telegram_id, state=str(), data=dict())


_fsm_context: FSM


async def fsm_context_init() -> None:
    """
    Инициализация объекта FSM.

    Производит инициализацию глобального объекта FSM для управления состояниями конечного автомата (FSM) в приложении.

    Возвращает:
        None

    """
    global _fsm_context
    _fsm_context = FSM()


def get_fsm_context() -> FSM:
    """
    Получение объекта FSM.

    Возвращает глобальный объект FSM для управления состояниями конечного автомата (FSM) в приложении.

    Возвращает:
        FSM: Объект FSM.

    """
    return _fsm_context
