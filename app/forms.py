from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired
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
    file = FileField('Choose file',
                     validators=[FileAllowed(['geojson'], 'Тільки geojson')])
    submit = SubmitField('Upload',
                         render_kw={"class": "btn btn-primary"})
