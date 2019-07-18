from flask import Blueprint, redirect, render_template, url_for, request, flash
from flask_login import login_required, current_user
from db.db_model import db, sessionFiles, dataFile, User, HRM, notification as n
from utilities.file_utility import FileUtility
from forms import UserInfoForm
from sqlalchemy import or_

admin = Blueprint('admin', __name__)


@admin.route('/admin2', methods=['GET', 'POST'])
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


@admin.route('/decline_user', methods=['GET', 'POST'])
@login_required
def decline_user():
    notification_id = request.form.get("notification_id")
    notification = n.query.filter_by(id=notification_id).first()
    user = User.query.filter_by(username=notification.originUser).first()
    db.session.delete(user)
    db.session.delete(notification)
    db.session.commit()
    return "deleted"


@admin.route('/approve_user', methods=['GET', 'POST'])
@login_required
def approve_user():
    notification_id = request.form.get("notification_id")
    notification = n.query.filter_by(id=notification_id).first()
    user = User.query.filter_by(username=notification.originUser).first()
    user.approved = 1
    db.session.delete(notification)
    db.session.commit()
    return "approved"



