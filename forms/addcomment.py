from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired


class AddCommentForm(FlaskForm):
    comment_text = TextAreaField("Введите свой комментарий с использованием md", validators=[DataRequired()])
    submit = SubmitField('Опубликовать')
