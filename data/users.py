import datetime

import requests
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase
import urllib, hashlib


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    """Класс модели пользователя"""
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    reviews = orm.relationship("Review", back_populates='author_user')

    def get_avatar(self, size):
        """Функция генерации аватарки"""
        digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        gravatar_url = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
        return requests.get(gravatar_url).content

    def __repr__(self):
        return f"<User> {self.id} {self.nickname}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
