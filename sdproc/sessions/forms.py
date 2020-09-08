from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from db.db_model import SessionFiles
from sqlalchemy import and_


class SessionForm(FlaskForm):
    session_name = StringField(label='Session Name', validators=[DataRequired(), Length(min=2, max=20)])
    comments = StringField(label='Comments')
    submit = SubmitField('Save Session')

    @staticmethod
    def validate_session_name(self, session_name):
        name = SessionFiles.query.filter(and_(SessionFiles.name == session_name.data,
                                              SessionFiles.user_id == current_user.id)).first()
        if name:
            raise ValidationError('That session name is taken. Please choose a different one.')
