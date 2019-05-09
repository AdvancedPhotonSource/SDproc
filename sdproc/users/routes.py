from flask import Blueprint, url_for, flash, render_template, redirect
from flask_login import current_user
from sdproc import bcrypt

from db.db_model import db, User
from sdproc.users.forms import RegistrationForm

users = Blueprint('users', __name__)


@users.route("/register2", methods=['GET', 'POST'])
def register2():
    if current_user.is_authenticated:
        return redirect(url_for('sdproc.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #user = User(username=form.username.data, email=form.email.data, pwhash=hashed_password, fullname=form.full_name.data, institution=form.institution.data, reason=form.reason_for_account.data)
        # db.session.add(user)
        # db.session.commit()
        flash('Your account is pending approval from the admin.', 'success')
        return redirect(url_for('user.login'))
    return render_template('new_reg.html', title='Register', form=form)
