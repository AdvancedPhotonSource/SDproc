from datetime import datetime

from flask import Blueprint, url_for, flash, render_template, redirect, session, request
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sdproc.user import clear_cmeta, clear_rowa_wrapper

from db.db_model import db, User, notification
from sdproc.users.forms import RegistrationForm, LoginForm, UpdateProfileForm

users = Blueprint('users', __name__)


@users.route("/", methods=['GET', 'POST'])
def toLogin2():
    return redirect(url_for('users.login2'))


@users.route("/register2", methods=['GET', 'POST'])
def register2():
    if current_user.is_authenticated:
        return redirect(url_for('sdproc.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data,
                    pwhash=hashed_password, fullname=form.full_name.data,
                    institution=form.institution.data, reason=form.reason_for_account.data)
        user.approved = 0
        user.isAdmin = 0
        db.session.add(user)
        notif = notification()
        notif.originUser = user.username
        notif.type = 'Create Account'
        notif.timestamp = datetime.now()
        db.session.add(notif)
        db.session.commit()
        flash('Your account is pending approval from the admin.', 'success')
        return redirect(url_for('user.login'))
    return render_template('new_reg.html', title='Register', form=form)


@users.route("/login2", methods=['GET', 'POST'])
def login2():
    if current_user.is_authenticated:
        return redirect(url_for('sdproc.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.pwhash, form.password.data):
            if user.approved == 1:
                login_user(user)
                clear_cmeta()
                clear_rowa_wrapper()
                current_user.current_session = 'None'
                db.session.commit()
                return redirect(url_for('sdproc.index'))
            elif user.approved == 2:
                flash("Your account has been frozen", 'danger')
                return render_template('new_login.html', form=form, session=session)
            elif user.approved == 0:
                flash("Your account is still pending admin approval.", 'info')
                return render_template('new_login.html', form=form, session=session)
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('new_login.html', title='Login', form=form)


@users.route("/profile2", methods=['GET', 'POST'])
@login_required
def profile2():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.fullName = form.full_name.data
        current_user.institution = form.institution.data
        current_user.commentChar = form.comment_char.data
        # current_user.pwhash = form.password.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.profile2'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.full_name.data = current_user.fullName
        form.institution.data = current_user.institution
        form.comment_char.data = current_user.commentChar
        # form.password.data = current_user.pwhash.decode('utf-8')
    return render_template('new_profile.html', title='Profile', form=form)
