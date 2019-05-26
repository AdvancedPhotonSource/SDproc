from flask_wtf import FlaskForm
from wtforms import SubmitField, MultipleFileField
from wtforms.validators import DataRequired, ValidationError


class FileUploadForm(FlaskForm):
    files = MultipleFileField(label='Choose File(s)', validators=[DataRequired()])
    submit = SubmitField(label='Upload')

    @staticmethod
    def validate_files(self, files):
        for file in files.data:
            print file.filename
            f_ext = file.filename[-3:]
            print f_ext
            if f_ext != 'mda' and f_ext != "dat" and f_ext != "txt":
                raise ValidationError('One or more of your files does not have an approved extension: mda, txt, dat')
