from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, MultipleFileField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, Length


class FileUploadForm(FlaskForm):
    files = MultipleFileField(label='Choose File(s)', validators=[DataRequired(), FileAllowed(['mda', 'txt', 'dat'])])
    comment_character = StringField(label='Character used to comment', validators=[DataRequired(), Length(min=1,max=1)])
    file_type = SelectField(label='File Type', choices=[(1,'mda'), (2,'txt')], validators=[DataRequired()])
    submit = SubmitField(label='Upload')