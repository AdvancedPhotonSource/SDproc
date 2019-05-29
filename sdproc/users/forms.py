from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import re
from flask_login import current_user

from db.db_model import User


class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    full_name = StringField(label='Full Name', validators=[DataRequired()])
    reason_for_account = StringField(label='Reason for Account Creation')
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired(), EqualTo('password')])
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    institution = StringField(label='Institution')
    submit = SubmitField('Sign Up')

    @staticmethod
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    @staticmethod
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please choose a different one.')

    @staticmethod
    def validate_password(self, password):
        password = password.data
        if re.search(r"\d", password) is None:
            raise ValidationError('Your password must have at least one digit.')
        elif re.search(r"[A-Z]", password) is None:
            raise ValidationError('Your password must have at least one uppercase letter.')
        elif re.search(r"[a-z]", password) is None:
            raise ValidationError('Your password must have at least one lowercase letter.')
        elif re.search(r"\W", password) is None:
            raise ValidationError('Your password must have at least one symbol.')


class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField('Login')
