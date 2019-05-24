from sdproc.files.forms import FileUploadForm
from flask import Blueprint, render_template, url_for
from flask_login import login_required


files = Blueprint('files', __name__)


@files.route('/upload_files', methods=['GET', 'POST'])
@login_required
def upload_files():
    file_types = ['mda', 'dat', 'txt']
    form = FileUploadForm()
    form.file_type.choices = file_types
    if form.validate_on_submit():
        files = form.files.data
        for file in files:
            print file
    return render_template('new_upload.html',title='New Upload',form=form)
