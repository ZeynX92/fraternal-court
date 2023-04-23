import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Language(SqlAlchemyBase, SerializerMixin):
    """Класс модели языка программирования"""
    __tablename__ = 'languages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    language = sqlalchemy.Column(sqlalchemy.String)

    review = orm.relationship("Review", back_populates='language_obj')
