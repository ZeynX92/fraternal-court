from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired


class AddReviewForm(FlaskForm):
    """Форма добавления записи"""
    code = FileField("Приложи файл с комментариями", validators=[DataRequired()])
    language = SelectField('Язык программирования', choices=[('2', 'C++'), ('1', 'Python'), ("3", "C#"), ("4", "Java")])
    submit = SubmitField('Опубликовать')
