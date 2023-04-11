from main import app
from flask_wtf import Form
from wtforms import StringField, PasswordField, validators


class LoginValidation(Form):
    user_name_pid = StringField('', [validators.DataRequired()],
                                render_kw={'autofocus': True, 'placeholder': 'Enter User'})

    user_pid_Password = PasswordField('', [validators.DataRequired()],
                                      render_kw={'autofocus': True, 'placeholder': 'Enter your login Password'})