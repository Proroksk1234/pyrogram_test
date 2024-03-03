from sqlalchemy import create_engine, JSON, ARRAY, Integer, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app import config


class Base(DeclarativeBase):
    """
    Базовый класс для моделей SQLAlchemy с типовыми аннотациями и конфигурациями метаданных.

    Этот класс служит основой для определения моделей SQLAlchemy и включает в себя атрибут `type_annotation_map`,
    который отображает аннотации типов Python на соответствующие типы SQLAlchemy. Кроме того,
    предоставляется предварительно настроенный атрибут `metadata` с соглашениями по именованию
    для индексов, уникальных ограничений, проверочных ограничений, внешних ключей и первичных ключей.

    Атрибуты:
        type_annotation_map (dict): Отображение аннотаций типов Python на типы SQLAlchemy.
            Пример:
                {
                    dict[str, any]: JSON,
                    tuple[int]: ARRAY(Integer, as_tuple=True, dimensions=1)
                }

        metadata (MetaData): Экземпляр класса MetaData SQLAlchemy с настройками соглашений по именованию.
            Соглашения по именованию:
                - Индекс: "ix_%(column_0_label)s"
                - Уникальное ограничение: "uq_%(table_name)s_%(column_0_name)s"
                - Проверочное ограничение: "ck_%(table_name)s_`%(constraint_name)s`"
                - Внешний ключ: "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
                - Первичный ключ: "pk_%(table_name)s"

    Использование:
        class MyModel(Base):
            __tablename__ = 'my_table'
            id = Column(Integer, primary_key=True)
            name = Column(String(50), nullable=False)

    Примечание:
        Убедитесь, что ваши классы моделей наследуются от этого класса `Base`,
        чтобы воспользоваться предоставленными типовыми аннотациями и конфигурациями метаданных.

    """
    type_annotation_map = {
        dict[str, any]: JSON,
        tuple[int]: ARRAY(Integer, as_tuple=True, dimensions=1)
    }
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })


engine = create_engine(config.DATABASE_CONNECTION_STRING, pool_size=10, max_overflow=30)
Session = sessionmaker(bind=engine)
