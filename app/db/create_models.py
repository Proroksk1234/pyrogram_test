"""
Создание таблиц в базе данных.

Этот скрипт проверяет существование таблиц в базе данных и, если они отсутствуют, создает их.
Также инициализируется функция `uuid_generate_v4()` в PostgreSQL для использования уникальных идентификаторов.

Параметры:
    - engine: SQLAlchemy engine, используемый для взаимодействия с базой данных.

Действия:
    - Скрипт использует SQL-запросы для создания таблиц users, fsm_context и user_tasks.
    - При создании таблицы user_tasks, заданы внешние ключи и каскадное удаление, связывающее ее с таблицей users.
    - Если таблица в базе данных уже создана, данное действие в этом файле пропускается
"""

from sqlalchemy import text
from sqlalchemy.ext.automap import automap_base

from app.db.db_config import engine

Base = automap_base()
Base.prepare(engine, reflect=True)

# Get the table names
table_names: list[str] = [x for x in Base.metadata.tables.keys()]

with engine.connect() as con:
    ##########################################################
    #   Инициализация функции uuid_generate_v4() в Postgres  #
    ##########################################################
    con.execute(
        text(
            'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
        )
    )
    ######################################################################
    #                      Создание таблицы users                        #
    #  user_uuid: Автоматическо-генерируемый индентификатор пользователя #
    #  owner_telegram_id: id телеграмма владельца аккаунта               #
    #  login_name: уникальный логин для аутентификации пользователя      #
    #  username: имя пользователя, используемого в боте                  #
    #  password: пароль для аутентификации пользователя в боте           #
    #  is_login: индентификатор, в сети ли данный пользователь или нет   #
    #  registration_date: время регистрации пользователя в боте          #
    ######################################################################
    if "users" not in table_names:
        con.execute(
            text(
                'CREATE TABLE users (\
                user_uuid UUID DEFAULT uuid_generate_v4() NOT NULL PRIMARY KEY, \
                owner_telegram_id BIGINT UNIQUE NOT NULL, \
                login_name VARCHAR UNIQUE NOT NULL, \
                username VARCHAR NOT NULL, \
                password VARCHAR NOT NULL, \
                is_login bool NOT NULL DEFAULT false, \
                registration_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP);'
            )
        )

    ############################################################################################
    #                                Создание таблицы fsm_context                              #
    #   telegram_id: id телеграмма пользователя (не обязательно зарегистрированного в системе) #
    #   state: данное состояние пользователя в боте                                            #
    #   data: сохраненные временные данные пользователя в fsm. имеет тип данных dict           #
    ############################################################################################
    if "fsm_context" not in table_names:
        con.execute(
            text(
                'CREATE TABLE fsm_context (\
                telegram_id BIGINT NOT NULL PRIMARY KEY, \
                state VARCHAR DEFAULT NULL, \
                data JSON DEFAULT \'{}\');'
            )
        )
    ######################################################################################################
    #                                    Создание таблицы user_tasks                                     #
    #   task_uuid: уникальный автогенерируемый индентификатор задачи                                     #
    #   id_task: уникальный автогенерируемый числовой индентификатор задачи                              #
    #   owner_telegram_id: foreign key поле связи с таблицей users через телеграмм id владельца аккаунта #
    #   task_name: название задачи                                                                       #
    #   description: описание задачи                                                                     #
    #   start_time: время старта задачи                                                                  #
    #   end_time: время окончания задачи                                                                 #
    #   completion_time: время завершения задачи                                                         #
    #   status: индентификатор, завершена ли задача, или нет                                             #
    ######################################################################################################
    if "user_tasks" not in table_names:
        con.execute(
            text(
                'CREATE TABLE user_tasks (\
                task_uuid UUID DEFAULT uuid_generate_v4() NOT NULL PRIMARY KEY, \
                id_task serial UNIQUE NOT NULL, \
                owner_telegram_id bigint NOT NULL, \
                task_name VARCHAR NOT NULL, \
                description VARCHAR NOT NULL, \
                start_time TIMESTAMPTZ NOT NULL, \
                end_time TIMESTAMPTZ NOT NULL, \
                completion_time TIMESTAMPTZ DEFAULT NULL, \
                status BOOLEAN NOT NULL DEFAULT FALSE, \
                FOREIGN KEY (owner_telegram_id) REFERENCES users (owner_telegram_id) ON DELETE CASCADE);'
            )
        )

    con.commit()
