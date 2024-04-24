from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired, URL


class MessageForm(FlaskForm):
    content = TextAreaField("Содержание", validators=[DataRequired()])
    url = TextAreaField("URL картинки")
    submit = SubmitField('Применить')