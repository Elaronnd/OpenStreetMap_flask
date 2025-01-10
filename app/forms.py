from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileField, FileAllowed


class UserRegForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])


class UserLoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])


class ChangePasswordForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])


class NewPasswordForm(FlaskForm):
    new_password = PasswordField(validators=[DataRequired()])

class UploadForm(FlaskForm):
    file = FileField('Choose file', validators=[FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Тільки geojson')])
    submit = SubmitField('Upload')
