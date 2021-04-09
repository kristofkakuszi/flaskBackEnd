from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import sqlite3

class LoginForm(FlaskForm):
 username = StringField('username')
 password = PasswordField('password')
 submit = SubmitField('Login')
