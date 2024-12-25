from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email
from wtforms.widgets import SubmitInput


class UserForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired(), Email()])
    submit = SubmitField(widget=SubmitInput())
