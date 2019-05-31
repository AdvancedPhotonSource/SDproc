from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required, current_user
from db.db_model import db, sessionFiles, dataFile, User, HRM, notification
from utilities.file_utility import FileUtility

admin = Blueprint('admin', __name__)


@admin.route('/admin2', methods=['GET', 'POST'])
@login_required
def admin2():
    users = User.query.filter(User.id != current_user.id).all()
    hrms = HRM.query.order_by('id').all()
    return render_template('new_admin.html', title="Admin", users=users, hrms=hrms)
