from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

Base = declarative_base(metadata=MetaData())

"""
This module defines the base model for SQLAlchemy ORM.

The `Base` object is an instance of `declarative_base` class from SQLAlchemy.
It is used as the base class for all models in the application.

The `metadata` argument is set to an instance of `MetaData` class, which allows
defining naming conventions for database objects.

Example usage:
    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String)

Note: This module should be imported before defining any models in the application.
"""


class BaseTable(Base):
    """
    Base class for database tables.

    This class serves as a base for all database table models in the application.
    It provides common functionality and attributes that are shared among all tables.

    Attributes:
        __abstract__ (bool): Indicates if this class is an abstract base class.
    """

    __abstract__ = True

    def __repr__(self):
        columns = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        return f'<{self.__tablename__}: {", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'
