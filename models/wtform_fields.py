from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import ImputRequired, Lenght, EqualTo

class RegistrationForm(FlaskForm):
    """Registration Form"""

    username = StringField('username_label')
    password = PasswordField('password_label')
    confirm_pswd = PasswordField('confirm_pswd_label')

    