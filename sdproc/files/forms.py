from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, MultipleFileField
from wtforms.validators import DataRequired


class FileUploadForm(FlaskForm):
    files = MultipleFileField(label='Choose File(s)', validators=[DataRequired(), FileAllowed(['mda', 'txt', 'dat'])])
    submit = SubmitField(label='Upload')
