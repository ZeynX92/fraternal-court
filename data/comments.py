import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    review_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("reviews.id"))
    comment_text = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    author_user = orm.relationship("User")
    review_obj = orm.relationship("Review")
