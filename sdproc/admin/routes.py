from flask import Blueprint, redirect, render_template, url_for, request, flash, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from db.db_model import db, DataFile, User, HRM, Notification as n, SessionFiles
from sdproc.admin.forms import UpdateUserInfoForm
from sdproc.users.forms import UpdatePasswordForm
from forms import UserInfoForm

a = Blueprint('admin', __name__)


@a.route('/admin', methods=['GET', 'POST'])
@login_required
def admin2():
    if current_user.badge_number is None:
        flash('Please update your badge number in order to continue', 'info')
        return redirect(url_for('users.profile2'))
    form = UserInfoForm()
    users = User.query.filter(User.id != current_user.id).all()
    hrms = HRM.query.order_by('id').all()
    notifications = n.query.order_by('id').all()
    new_users = []
    for x in notifications:
        for i in users:
            if x.originUser == i.username:
                new_users.append(i)

    return render_template('new_admin.html', title="Admin", users=users, hrms=hrms, notifications=notifications,
                           form=form, new_users=new_users)


@a.route('/profile/<string:username>', methods=['GET', 'POST'])
@login_required
def update_user_profile(username):
    user = User.query.filter_by(username=username).first()
    session['admin_username'] = user.username
    session['admin_email'] = user.email
    session['admin_badge_number'] = user.badge_number
    form = UpdateUserInfoForm()
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.badge_number = form.badge_number.data
        user.fullName = form.full_name.data
        user.institution = form.institution.data
        user.commentChar = form.comment_char.data
        db.session.commit()
        session.pop('admin_username', None)
        session.pop('admin_email', None)
        session.pop('admin_badge_number', None)
        flash('The user information has been updated!', 'success')
        return redirect(url_for('admin.update_user_profile', username=user.username))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.full_name.data = user.fullName
        form.badge_number.data = user.badge_number
        form.institution.data = user.institution
        form.comment_char.data = user.commentChar
    return render_template('view_user.html', title='View User Profile', form=form, user=user)


@a.route('/profile/password/<string:username>', methods=['GET', 'POST'])
@login_required
def update_user_password(username):
    user = User.query.filter_by(username=username).first()
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.pwhash = hashed_password
        db.session.commit()
        flash(user.username + '"s password has been updated', 'success')
        return redirect(url_for('admin.update_user_profile', username=user.username))
    return render_template('update_password.html', title='Update Password', form=form, user=user)


@a.route('/decline_user/<int:id_value>', methods=['GET', 'POST'])
@login_required
def decline_user(id_value):
    notification = n.query.filter_by(id=id_value).first()
    user = User.query.filter_by(username=notification.originUser).first()
    db.session.delete(user)
    db.session.delete(notification)
    db.session.commit()
    return redirect(url_for('admin.admin2'))


@a.route('/approve_user/<int:id_value>', methods=['GET', 'POST'])
@login_required
def approve_user(id_value):
    notification = n.query.filter_by(id=id_value).first()
    user = User.query.filter_by(username=notification.originUser).first()
    user.approved = 1
    db.session.delete(notification)
    root = DataFile(name='/' + user.username + '/', authed=str(user.id), comChar='#', parentID=0, treeType="Root")
    db.session.add(root)
    db.session.commit()
    return redirect(url_for('admin.admin2'))


@a.route('/delete_user/<string:username>', methods=['GET', 'POST'])
@login_required
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    files = DataFile.query.filter_by(authed=str(user.id)).all()
    for f in files:
        db.session.delete(f)
    sessions = SessionFiles.query.filter_by(user_id=user.id).all()
    if sessions:
        db.session.delete(sessions)
    db.session.delete(user)
    db.session.commit()
    flash(user.username + ' has been deleted.', 'info')
    return redirect(url_for('admin.admin2'))


@a.route('/freeze_user/<string:username>', methods=['GET', 'POST'])
@login_required
def freeze_user(username):
    user = User.query.filter_by(username=username).first()
    if user.approved == 1:
        user.approved = 2
        db.session.commit()
        flash(user.username + "'s account has been frozen. They are currently unable to login.", 'info')
        return redirect(url_for('admin.update_user_profile', username=user.username))
    else:
        user.approved = 1
        db.session.commit()
        flash(user.username + "'s account has been unfrozen. They can now login.", 'info')
        return redirect(url_for('admin.update_user_profile', username=user.username))
