from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError, NumberRange
from db.db_model import User


class UserInfoForm(FlaskForm):
    full_name = StringField(label='Full Name', validators=[DataRequired()])
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    institution = StringField(label='Institution', validators=[DataRequired()])
    reason = StringField(label="Reason")


class UpdateUserInfoForm(FlaskForm):
    full_name = StringField(label='Full Name', validators=[DataRequired()])
    badge_number = IntegerField(label='Badge Number', validators=[DataRequired(), NumberRange(min=0, max=999999)])
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    institution = StringField(label='Institution')
    comment_char = StringField(label='Comment Char')
    submit = SubmitField('Update Profile')

    @staticmethod
    def validate_username(self, username):
        if 'admin_username' in session:
            currUsername = session['admin_username']
            if username.data != currUsername:
                user = User.query.filter_by(username=username.data).first()
                if user:
                    raise ValidationError('That username is taken. Please choose a different one.')

    @staticmethod
    def validate_badge_number(self, badge_number):
        if 'admin_badge_number' in session:
            currBadgeNumber = session['admin_badge_number']
            if badge_number.data != currBadgeNumber:
                user = User.query.filter_by(badge_number=badge_number.data).first()
                if user:
                    raise ValidationError('Please enter correct badge number.')

    @staticmethod
    def validate_email(self,  email):
        if 'admin_email' in session:
            currEmail = session['admin_email']
            if email.data != currEmail:
                user = User.query.filter_by(username=email.data).first()
                if user:
                    raise ValidationError('That email is taken. Please choose a different one.')
