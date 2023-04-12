from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired


class AddReviewForm(FlaskForm):
    code = FileField("Приложи файл с комментариями", validators=[DataRequired()])
    language = SelectField('Язык программирования', choices=[('1', 'C++'), ('2', 'Python')])
    submit = SubmitField('Опубликовать')
