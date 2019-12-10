import datetime

from flask import Blueprint, url_for, flash, render_template, redirect, session, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sdproc.sessions.routes import clear_cmeta, clear_rowa_wrapper
from db.db_model import db, User, Notification
from sdproc.users.forms import RegistrationForm, LoginForm, UpdateProfileForm, UpdatePasswordForm

users = Blueprint('users', __name__)


@users.route("/", methods=['GET', 'POST'])
def toLogin2():
    return redirect(url_for('users.login2'))


@users.route("/register2", methods=['GET', 'POST'])
def register2():
    if current_user.is_authenticated:
        if current_user.badge_number is None:
            flash('Please update your badge number in order to continue', 'info')
            return redirect(url_for('users.profile2'))
        else:
            return redirect(url_for('sessions.index2'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data,
                    pwhash=hashed_password, fullName=form.full_name.data,
                    institution=form.institution.data, reason=form.reason_for_account.data,
                    badge_number=form.badge_number.data)
        user.approved = 0
        user.isAdmin = 0
        db.session.add(user)
        notif = Notification()
        notif.originUser = user.username
        notif.type = 'Create Account'
        notif.timestamp = datetime.date.today()
        db.session.add(notif)
        db.session.commit()
        flash('Your account is pending approval from the admin.', 'success')
        return redirect(url_for('users.login2'))
    return render_template('new_reg.html', title='Register', form=form)


@users.route("/login2", methods=['GET', 'POST'])
def login2():
    if current_user.is_authenticated:
        return redirect(url_for('sessions.index2'))
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
                if current_user.badge_number is None:
                    flash('Please update your badge number in order to continue', 'info')
                    return redirect(url_for('users.profile2'))
                else:
                    return redirect(url_for('sessions.index2'))
            elif user.approved == 2:
                flash("Your account has been frozen", 'danger')
                return render_template('new_login.html', form=form, session=session)
            elif user.approved == 0:
                flash("Your account is still pending admin approval.", 'info')
                return render_template('new_login.html', form=form, session=session)
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('new_login.html', title='Login', form=form)


@users.route("/logout2")
@login_required
def logout2():
    session.clear()
    clear_rowa_wrapper()
    clear_cmeta()
    logout_user()
    return redirect(url_for('users.login2'))


@users.route("/profile2", methods=['GET', 'POST'])
@login_required
def profile2():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.fullName = form.full_name.data
        current_user.badge_number = form.badge_number.data
        current_user.institution = form.institution.data
        current_user.commentChar = form.comment_char.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.profile2'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.full_name.data = current_user.fullName
        form.badge_number.data = current_user.badge_number
        form.institution.data = current_user.institution
        form.comment_char.data = current_user.commentChar
    return render_template('new_profile.html', title='Profile', form=form)


@users.route("/update_password", methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        current_user.pwhash = hashed_password
        db.session.commit()
        flash('Your password has been updated', 'success')
        return redirect(url_for('users.profile2'))
    return render_template('update_password.html', title='Update Password', form=form)
