from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
import sqlite3

class LoginForm(FlaskForm):
 username = StringField('username')
 password = PasswordField('password')

