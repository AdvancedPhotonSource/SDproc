from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Email


class UserInfoForm(FlaskForm):
    full_name = StringField(label='Full Name', validators=[DataRequired()])
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    institution = StringField(label='Institution', validators=[DataRequired()])
    reason = StringField(label="Reason")
